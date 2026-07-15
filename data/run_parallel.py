"""run_parallel.py — 7-lane parallel DAT collection.

One thread per PROVIDER lane (independent API keys, independent rate-limit buckets).
Within a lane: a small worker pool (--concurrency) shares a 0.5s LAUNCH GATE, so no two
requests on the same lane start less than --min-gap seconds apart (default 0.5s), even
under concurrency. Resumable: skips models already at target n in raw/topup_<provider>.csv.
Thread-safe incremental CSV writes (durable per row). Reuses data_collection.call_once.

Usage:
  python data/run_parallel.py --n 500 --batch collect_2026_n500 --concurrency 3
  python data/run_parallel.py --n 500 --only openai,anthropic   # subset of lanes
"""
import argparse, csv, os, sys, time, threading, queue
from pathlib import Path
import data_collection as dc

HERE = Path(__file__).parent

def existing_count(out_csv, model_name):
    if not out_csv.exists(): return 0
    with open(out_csv) as f:
        return sum(1 for r in csv.DictReader(f) if r["model_name"] == model_name)

_write_locks = {}
_wl_guard = threading.Lock()
def write_lock(path):
    with _wl_guard:
        if path not in _write_locks: _write_locks[path] = threading.Lock()
        return _write_locks[path]

def load_live(models_csv, only=None):
    lanes = {}
    for r in csv.DictReader(open(models_csv)):
        if (r.get("status") or "").strip().lower() != "live": continue
        prov = r["provider"]
        if only and prov not in only: continue
        lanes.setdefault(prov, []).append(r)
    return lanes

class LaunchGate:
    """Enforce a minimum wall-clock gap between successive request launches on a lane."""
    def __init__(self, min_gap):
        self.min_gap = min_gap; self.lock = threading.Lock(); self.last = 0.0
    def wait(self):
        with self.lock:
            now = time.time(); delta = now - self.last
            if delta < self.min_gap:
                time.sleep(self.min_gap - delta)
            self.last = time.time()

def collect_one(model_row, n, out_csv, batch, gate, key, stop):
    """Collect up to n rows for one model, respecting the shared launch gate."""
    prov = model_row["provider"]; name = model_row["model"]; api = model_row["api_model_id"]
    meta = {"region": model_row.get("region",""), "reasoning": model_row.get("reasoning",""), "year": model_row.get("year","")}
    have = existing_count(out_csv, name)
    made = have
    target_temp = dc.provider_midpoint(prov)
    lk = write_lock(str(out_csv))
    while made < n and not stop.is_set():
        seed = 1000 + made
        gate.wait()                          # <-- 0.5s min gap between launches on this lane
        req_ts = dc._now(); t0 = time.time()
        try:
            payload, temp_used = dc.call_once(prov, key, api, target_temp, seed)
        except Exception as e:
            msg = str(e)
            if "429" in msg:
                time.sleep(2.0); continue     # simple backoff; gate already paces us
            print(f"FAIL {name} ({prov}): {msg[:80]}", flush=True)
            return name, made-have, f"error:{msg[:60]}"
        resp_ts = dc._now(); latency = int((time.time()-t0)*1000)
        nouns = dc.parse_nouns(payload["text"]); status = "ok" if nouns else "failed"
        row = {
            "record_id":"","model_name":name,"api_model_requested":api,
            "api_model_returned":payload.get("api_model_returned",""),"provider":prov,
            "endpoint_base":payload.get("endpoint_base",""),"batch":batch,
            "region":meta["region"],"reasoning":meta["reasoning"],"model_year":meta["year"],
            "temperature_requested":target_temp,"temperature_effective":temp_used,
            "temp_range_used":dc.temp_range_str(prov),"seed":seed if dc.PROVIDERS[prov][2] else "",
            "request_timestamp_utc":req_ts,"response_timestamp_utc":resp_ts,"latency_ms":latency,
            "api_request_id":payload.get("api_request_id",""),"response_id":payload.get("response_id",""),
            "system_fingerprint":payload.get("system_fingerprint",""),"finish_reason":payload.get("finish_reason",""),
            "prompt_tokens":payload.get("prompt_tokens",""),"completion_tokens":payload.get("completion_tokens",""),
            "total_tokens":payload.get("total_tokens",""),"prompt_sha256":dc.PROMPT_SHA256,
            "raw_response_text":payload["text"],"parse_status":status,
            "n_nouns_parsed":len(nouns) if nouns else 0,
            **{c:(nouns[i] if nouns else "") for i,c in enumerate(dc.NOUN_COLS)},
            "dat_score":"","collector_version":dc.COLLECTOR_VERSION,
        }
        with lk:
            dc.write_rows(out_csv, [row])
        made += 1
    return name, made-have, "done"

def run_lane(prov, models, n, out_dir, batch, concurrency, min_gap, stop):
    key = os.environ.get(dc.PROVIDERS[prov][1])
    if not key:
        print(f"LANE {prov}: MISSING KEY {dc.PROVIDERS[prov][1]} — skipped", flush=True); return
    out_csv = Path(out_dir)/f"topup_{prov}.csv"
    gate = LaunchGate(min_gap)
    todo = [m for m in models if existing_count(out_csv, m["model"]) < n]
    print(f"LANE {prov}: {len(todo)}/{len(models)} models need work (concurrency={concurrency})", flush=True)
    q = queue.Queue()
    for m in todo: q.put(m)
    def worker():
        while not stop.is_set():
            try: m = q.get_nowait()
            except queue.Empty: return
            try:
                name, got, st = collect_one(m, n, out_csv, batch, gate, key, stop)
                print(f"  [{prov}] {name}: +{got} ({st})", flush=True)
            finally:
                q.task_done()
    ts = [threading.Thread(target=worker, daemon=True) for _ in range(max(1,concurrency))]
    for t in ts: t.start()
    for t in ts: t.join()
    print(f"LANE DONE: {prov}", flush=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default=str(HERE/"models.csv"))
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--out-dir", default=str(HERE/"raw"))
    ap.add_argument("--batch", default="collect_2026_n500")
    ap.add_argument("--concurrency", type=int, default=3, help="in-flight workers per lane")
    ap.add_argument("--min-gap", type=float, default=0.5, help="min seconds between launches per lane")
    ap.add_argument("--only", help="comma-separated provider subset")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    lanes = load_live(a.models, only)
    if not lanes: sys.exit("no live lanes matched")
    Path(a.out_dir).mkdir(parents=True, exist_ok=True)
    stop = threading.Event()
    print(f"START {len(lanes)} lanes @ n={a.n}, concurrency={a.concurrency}, min-gap={a.min_gap}s, batch={a.batch}", flush=True)
    threads=[]
    for prov, models in lanes.items():
        t = threading.Thread(target=run_lane, args=(prov, models, a.n, a.out_dir, a.batch, a.concurrency, a.min_gap, stop), daemon=True)
        t.start(); threads.append(t)
    try:
        for t in threads: t.join()
    except KeyboardInterrupt:
        stop.set(); print("STOPPING (data already flushed per-row)", flush=True)
    print("ALL LANES COMPLETE", flush=True)

if __name__ == "__main__":
    main()
