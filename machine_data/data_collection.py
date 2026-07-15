"""
data_collection.py — generate machine DAT responses with FULL open-science provenance.

BASELINE PROMPT: verbatim `baseline_prompt_1` from the NHB divergent-creativity OSF
(osf.io/a9v2t -> studies_prompts.ipynb, Study 1a/1b). Loaded from data/baseline_prompt.txt.
Do NOT paraphrase.

TEMPERATURE: per-provider MIDPOINT (locked 2026-07-14). 0-2 scale providers -> 1.0;
0-1 scale providers -> 0.5. Recorded per row (requested + effective + range). If a model
forces its own temperature, the row records what was actually used.

Each generation writes ONE raw row with full provenance (timestamps, api request/response ids,
system fingerprint, finish reason, token usage, prompt sha256, raw response text, parsed nouns).
DAT scoring is a SEPARATE later pass; dat_score stays blank here.

Keys read from env at runtime; never hard-coded, never written to disk.

Usage:
  python data_collection.py --model "GPT-4o" --api-model gpt-4o-2024-08-06 --provider openai --n 5 [--dry-run]
  python data_collection.py --from-inventory machine_data/models.csv --n 500   # full run
"""
import argparse, csv, hashlib, json, os, subprocess, sys, time, threading, queue, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
BASELINE_PROMPT = (
    "Generate 10 nouns that are as different from each other as possible using the instructions below:\n"
    "1. Generate only single-word nouns in English.\n"
    "2. Generate only nouns such as things, objects and concepts.\n"
    "3. Do not use proper nouns such as people or places.\n"
    "4. Do not use specialised vocabulary or technical terms.\n"
    "5. Generate your final response as a string with each noun separated by commas: \"noun_1, noun_2, noun_3, noun_4, noun_5, noun_6, noun_7, noun_8, noun_9, noun_10\".\n"
    "6. Do not return anything else other than the comma-separated string of nouns."
)
PROMPT_SHA256 = hashlib.sha256(BASELINE_PROMPT.encode()).hexdigest()

PROVIDER_TEMP_RANGE = {
    "openai": (0, 2), "xai": (0, 2), "deepseek": (0, 2), "qwen": (0, 2), "hunyuan": (0, 2),
    "anthropic": (0, 1), "moonshot": (0, 1), "openrouter": (0, 2),
}
def provider_midpoint(provider):
    lo, hi = PROVIDER_TEMP_RANGE.get(provider, (0, 2))
    return (lo + hi) / 2
def temp_range_str(provider):
    lo, hi = PROVIDER_TEMP_RANGE.get(provider, (0, 2))
    return f"{lo}-{hi}"

TARGET_N_PER_MODEL = 500
NOUN_COLS = [f"noun_{i}" for i in range(10)]

FIELDS = ["record_id","model_name","api_model_requested","api_model_returned","provider",
          "endpoint_base","batch","region","reasoning","model_year",
          "temperature_requested","temperature_effective","temp_range_used","seed",
          "request_timestamp_utc","response_timestamp_utc","latency_ms",
          "api_request_id","response_id","system_fingerprint","finish_reason",
          "prompt_tokens","completion_tokens","total_tokens","prompt_sha256",
          "raw_response_text","parse_status","n_nouns_parsed"] + NOUN_COLS + ["dat_score","collector_version"]

def _collector_version():
    try:
        return "git:" + subprocess.check_output(["git","-C",str(HERE),"rev-parse","--short","HEAD"],text=True).strip()
    except Exception:
        return "git:unknown"
COLLECTOR_VERSION = _collector_version()

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

# ---- low-level POST that returns (parsed_json, response_headers) --------------------------
def _post_full(url, headers, body, timeout=300):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        return json.loads(raw), dict(r.headers)

# ---- provider adapters: return a normalized dict of everything we log ---------------------
def _openai_like(base, key, api_model, temperature, seed=None, extra_headers=None):
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if extra_headers: headers.update(extra_headers)
    body = {"model": api_model, "messages": [{"role":"user","content":BASELINE_PROMPT}], "temperature": temperature}
    if seed is not None: body["seed"] = seed
    d, h = _post_full(f"{base}/chat/completions", headers, body)
    ch = (d.get("choices") or [{}])[0]
    usage = d.get("usage") or {}
    return {
        "text": (ch.get("message") or {}).get("content","").strip(),
        "api_model_returned": d.get("model",""),
        "response_id": d.get("id",""),
        "system_fingerprint": d.get("system_fingerprint",""),
        "finish_reason": ch.get("finish_reason",""),
        "prompt_tokens": usage.get("prompt_tokens",""),
        "completion_tokens": usage.get("completion_tokens",""),
        "total_tokens": usage.get("total_tokens",""),
        "api_request_id": h.get("x-request-id") or h.get("x-amzn-requestid") or h.get("request-id",""),
        "endpoint_base": base,
    }

def _anthropic(base, key, api_model, temperature, seed=None):
    headers = {"x-api-key": key, "anthropic-version":"2023-06-01", "Content-Type":"application/json"}
    body = {"model": api_model, "max_tokens":200, "temperature":temperature,
            "messages":[{"role":"user","content":BASELINE_PROMPT}]}
    d, h = _post_full(f"{base}/messages", headers, body)
    usage = d.get("usage") or {}
    return {
        "text": "".join(b.get("text","") for b in d.get("content",[])).strip(),
        "api_model_returned": d.get("model",""),
        "response_id": d.get("id",""),
        "system_fingerprint": "",
        "finish_reason": d.get("stop_reason",""),
        "prompt_tokens": usage.get("input_tokens",""),
        "completion_tokens": usage.get("output_tokens",""),
        "total_tokens": (usage.get("input_tokens",0) or 0)+(usage.get("output_tokens",0) or 0),
        "api_request_id": h.get("request-id",""),
        "endpoint_base": base,
    }

# provider -> (callable(base,key,api_model,temperature,seed), base_url, env_key, supports_seed)
PROVIDERS = {
    "openai":    (lambda k,m,t,s: _openai_like("https://api.openai.com/v1", k, m, t, s), "OPENAI_API_KEY", True),
    "anthropic": (lambda k,m,t,s: _anthropic("https://api.anthropic.com/v1", k, m, t, s), "ANTHROPIC_API_KEY", False),
    "xai":       (lambda k,m,t,s: _openai_like("https://api.x.ai/v1", k, m, t, None), "XAI_API_KEY", False),
    "deepseek":  (lambda k,m,t,s: _openai_like("https://api.deepseek.com/v1", k, m, t, s), "DEEPSEEK_API_KEY", True),
    "qwen":      (lambda k,m,t,s: _openai_like("https://dashscope.aliyuncs.com/compatible-mode/v1", k, m, t, s), "QWEN_API_KEY", True),
    "hunyuan":   (lambda k,m,t,s: _openai_like("https://tokenhub.tencentmaas.com/v1", k, m, t, None), "HUNYUAN_API_KEY", False),
    "moonshot":  (lambda k,m,t,s: _openai_like("https://api.moonshot.ai/v1", k, m, t, None), "MOONSHOT_API_KEY", False),
}

def parse_nouns(text):
    t = text.replace("\n", ",")
    parts = [p.strip().strip('".').strip() for p in t.split(",")]
    parts = [p for p in parts if p and not p[0].isdigit()]
    parts = [p.lower() for p in parts]  # case-normalize parsed nouns (raw_response_text stays verbatim)
    return parts[:10] if len(parts) >= 10 else None

def call_once(provider, key, api_model, target_temp, seed):
    """Call at target_temp; on a temperature-rejection 400, retry with no seed at temp 1.0
    (some models only allow their own default). Returns (payload_dict, temp_used)."""
    fn = PROVIDERS[provider][0]
    try:
        return fn(key, api_model, target_temp, seed if PROVIDERS[provider][2] else None), target_temp
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode()
        except Exception: pass
        if e.code == 400 and "temperature" in body.lower():
            return fn(key, api_model, 1.0, None), 1.0
        raise RuntimeError(f"HTTP {e.code}: {body[:200]}")

def generate(model_name, api_model, provider, n, out_csv, meta, dry_run=False, seed_base=1000, pace=0.1, max_retries=5, batch="collect_2026_midpoint"):
    env_key = PROVIDERS[provider][1]
    key = os.environ.get(env_key)
    if not key: sys.exit(f"Missing env key {env_key} for provider {provider}")
    target_temp = provider_midpoint(provider)
    rows, made, attempts = [], 0, 0
    while made < n:
        seed = seed_base + made
        req_ts = _now(); t0 = time.time()
        try:
            payload, temp_used = call_once(provider, key, api_model, target_temp, seed)
        except RuntimeError as e:
            attempts += 1
            if "429" in str(e) and attempts <= max_retries:
                time.sleep(min(2**attempts, 30)); continue
            # skip-and-flag: do not kill the run; stop this model and report it
            print(f"SKIP {model_name} ({provider}): {str(e)[:120]}", flush=True)
            return rows
        resp_ts = _now(); latency = int((time.time()-t0)*1000)
        nouns = parse_nouns(payload["text"])
        status = "ok" if nouns else "failed"
        row = {
            "record_id": "", "model_name": model_name, "api_model_requested": api_model,
            "api_model_returned": payload.get("api_model_returned",""), "provider": provider,
            "endpoint_base": payload.get("endpoint_base",""), "batch": batch,
            "region": meta.get("region",""), "reasoning": meta.get("reasoning",""),
            "model_year": meta.get("year",""),
            "temperature_requested": target_temp, "temperature_effective": temp_used,
            "temp_range_used": temp_range_str(provider), "seed": seed if PROVIDERS[provider][2] else "",
            "request_timestamp_utc": req_ts, "response_timestamp_utc": resp_ts, "latency_ms": latency,
            "api_request_id": payload.get("api_request_id",""), "response_id": payload.get("response_id",""),
            "system_fingerprint": payload.get("system_fingerprint",""), "finish_reason": payload.get("finish_reason",""),
            "prompt_tokens": payload.get("prompt_tokens",""), "completion_tokens": payload.get("completion_tokens",""),
            "total_tokens": payload.get("total_tokens",""), "prompt_sha256": PROMPT_SHA256,
            "raw_response_text": payload["text"], "parse_status": status,
            "n_nouns_parsed": len(nouns) if nouns else 0,
            **{c:(nouns[i] if nouns else "") for i,c in enumerate(NOUN_COLS)},
            "dat_score": "", "collector_version": COLLECTOR_VERSION,
        }
        made += 1
        rows.append(row)
        if not dry_run:
            write_rows(out_csv, [row])   # incremental flush: durable per-row
        if dry_run:
            print(json.dumps({k:row[k] for k in ("model_name","provider","temperature_effective","parse_status","api_request_id","response_id","system_fingerprint","total_tokens","latency_ms",*NOUN_COLS)}, ensure_ascii=False))
            return rows
        time.sleep(pace)
    print(f"[{provider}/{api_model}] wrote {len(rows)} rows -> {out_csv}")
    return rows

def write_rows(out_csv, rows):
    if not rows: return
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    exists = out_csv.exists()
    with open(out_csv, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists: w.writeheader()
        w.writerows(rows)

def _rows_at(out_dir, provider, model_name):
    from pathlib import Path as _P
    f=_P(out_dir)/f"topup_{provider}.csv"
    if not f.exists(): return 0
    import csv as _csv
    return sum(1 for r in _csv.DictReader(open(f)) if r["model_name"]==model_name)

def run_batch(models_csv, n, out_dir, batch, provider=None):
    """Resumable batch over all live models in models_csv; skips models already at n."""
    import csv as _csv
    from pathlib import Path as _P
    targets=[r for r in _csv.DictReader(open(models_csv)) if (r.get("status") or "").lower().startswith("live")]
    if provider: targets=[t for t in targets if t["provider"]==provider]
    for t in targets:
        prov=t["provider"]; name=t["model"]; api=t["api_model_id"]
        have=_rows_at(out_dir, prov, name); need=n-have
        if need<=0:
            print(f"SKIP {name} ({prov}) already {have}", flush=True); continue
        print(f"RUN  {name} ({prov}) have={have} need={need}", flush=True)
        out=_P(out_dir)/f"topup_{prov}.csv"
        meta={"region":t.get("region",""),"reasoning":t.get("reasoning",""),"year":t.get("year","")}
        try:
            generate(name, api or name, prov, need, out, meta, batch=batch)
        except Exception as e:
            print(f"FAIL {name} ({prov}): {e}", flush=True)
    print(f"BATCH DONE: {provider or 'all'}", flush=True)

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
    target_temp = provider_midpoint(prov)
    lk = write_lock(str(out_csv))
    while made < n and not stop.is_set():
        seed = 1000 + made
        gate.wait()                          # <-- 0.5s min gap between launches on this lane
        req_ts = _now(); t0 = time.time()
        try:
            payload, temp_used = call_once(prov, key, api, target_temp, seed)
        except Exception as e:
            msg = str(e)
            transient = ("429" in msg or "timed out" in msg.lower() or "timeout" in msg.lower()
                         or "temporarily" in msg.lower() or "connection" in msg.lower()
                         or "reset" in msg.lower() or " 500" in msg or " 502" in msg or " 503" in msg or " 504" in msg)
            if transient:
                consec_transient = locals().get("consec_transient", 0) + 1
                if consec_transient <= 8:
                    time.sleep(min(2.0*consec_transient, 15)); continue   # retry, do NOT skip
            # real error (e.g. HTTP 400/404) or too many transient failures -> skip-and-flag
            print(f"FAIL {name} ({prov}): {msg[:80]}", flush=True)
            return name, made-have, f"error:{msg[:60]}"
        consec_transient = 0
        resp_ts = _now(); latency = int((time.time()-t0)*1000)
        nouns = parse_nouns(payload["text"]); status = "ok" if nouns else "failed"
        row = {
            "record_id":"","model_name":name,"api_model_requested":api,
            "api_model_returned":payload.get("api_model_returned",""),"provider":prov,
            "endpoint_base":payload.get("endpoint_base",""),"batch":batch,
            "region":meta["region"],"reasoning":meta["reasoning"],"model_year":meta["year"],
            "temperature_requested":target_temp,"temperature_effective":temp_used,
            "temp_range_used":temp_range_str(prov),"seed":seed if PROVIDERS[prov][2] else "",
            "request_timestamp_utc":req_ts,"response_timestamp_utc":resp_ts,"latency_ms":latency,
            "api_request_id":payload.get("api_request_id",""),"response_id":payload.get("response_id",""),
            "system_fingerprint":payload.get("system_fingerprint",""),"finish_reason":payload.get("finish_reason",""),
            "prompt_tokens":payload.get("prompt_tokens",""),"completion_tokens":payload.get("completion_tokens",""),
            "total_tokens":payload.get("total_tokens",""),"prompt_sha256":PROMPT_SHA256,
            "raw_response_text":payload["text"],"parse_status":status,
            "n_nouns_parsed":len(nouns) if nouns else 0,
            **{c:(nouns[i] if nouns else "") for i,c in enumerate(NOUN_COLS)},
            "dat_score":"","collector_version":COLLECTOR_VERSION,
        }
        with lk:
            write_rows(out_csv, [row])
        made += 1
    return name, made-have, "done"

def run_lane(prov, models, n, out_dir, batch, concurrency, min_gap, stop, lane_results=None):
    key = os.environ.get(PROVIDERS[prov][1])
    if not key:
        print(f"LANE {prov}: MISSING KEY {PROVIDERS[prov][1]} — skipped", flush=True); return
    out_csv = Path(out_dir)/f"topup_{prov}.csv"
    gate = LaunchGate(min_gap)
    todo = [m for m in models if existing_count(out_csv, m["model"]) < n]
    print(f"LANE {prov}: {len(todo)}/{len(models)} models need work (concurrency={concurrency})", flush=True)
    q = queue.Queue()
    for m in todo: q.put(m)
    results = []
    def worker():
        while not stop.is_set():
            try: m = q.get_nowait()
            except queue.Empty: return
            try:
                name, got, st = collect_one(m, n, out_csv, batch, gate, key, stop)
                results.append((name, got, st))
                print(f"  [{prov}] {name}: +{got} ({st})", flush=True)
            finally:
                q.task_done()
    ts = [threading.Thread(target=worker, daemon=True) for _ in range(max(1,concurrency))]
    for t in ts: t.start()
    for t in ts: t.join()
    if lane_results is not None: lane_results.extend(results)
    print(f"LANE DONE: {prov}", flush=True)


def run_parallel(models_csv, n, out_dir, batch, concurrency, min_gap, only=None):
    lanes = load_live(models_csv, only)
    if not lanes: sys.exit("no live lanes matched")
    from pathlib import Path as _P
    _P(out_dir).mkdir(parents=True, exist_ok=True)
    stop = threading.Event()
    print(f"START {len(lanes)} lanes @ n={n}, concurrency={concurrency}, min-gap={min_gap}s, batch={batch}", flush=True)
    results = []
    threads=[]
    for prov, models in lanes.items():
        t = threading.Thread(target=run_lane, args=(prov, models, n, out_dir, batch, concurrency, min_gap, stop, results), daemon=True)
        t.start(); threads.append(t)
    try:
        for t in threads: t.join()
    except KeyboardInterrupt:
        stop.set(); print("STOPPING (data already flushed per-row)", flush=True)
    # skip-and-flag summary: surface any model that errored so it is never silently swapped
    skipped = [(name, st) for (name, got, st) in results if st.startswith("error")]
    print("ALL LANES COMPLETE", flush=True)
    if skipped:
        print("\n=== SKIPPED (errored — NOT collected, NOT swapped) ===", flush=True)
        for name, st in skipped: print(f"  {name}: {st}", flush=True)
    else:
        print("No models skipped — all attempted models collected cleanly.", flush=True)
    return results

def main():
    ap = argparse.ArgumentParser(description="Collect machine DAT responses. Single-model or --all batch.")
    ap.add_argument("--model"); ap.add_argument("--api-model"); ap.add_argument("--provider", choices=list(PROVIDERS))
    ap.add_argument("--n", type=int, default=5); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--region", default=""); ap.add_argument("--reasoning", default=""); ap.add_argument("--year", default="")
    ap.add_argument("--batch", default="collect_2026_midpoint"); ap.add_argument("--out-dir", default=str(HERE/"raw"))
    ap.add_argument("--all", action="store_true", help="serial batch over all live models in --models (resumable)")
    ap.add_argument("--parallel", action="store_true", help="7-lane parallel run: one thread per provider key")
    ap.add_argument("--concurrency", type=int, default=3, help="runners within each lane (parallel mode)")
    ap.add_argument("--min-gap", type=float, default=0.5, help="min seconds between launches per lane (parallel mode)")
    ap.add_argument("--only", help="comma-separated provider subset (parallel mode)")
    ap.add_argument("--models", default=str(HERE/"models.csv"), help="model grid for --all/--parallel modes")
    a = ap.parse_args()
    if a.parallel:
        run_parallel(a.models, a.n, a.out_dir, a.batch, a.concurrency, a.min_gap,
                     only=set(a.only.split(",")) if a.only else None); return
    if a.all:
        run_batch(a.models, a.n, a.out_dir, a.batch, provider=a.provider); return
    if not (a.model and a.provider): sys.exit("need --model and --provider (or --all)")
    from pathlib import Path as _P
    out = _P(a.out_dir) / f"topup_{a.provider}.csv"
    meta = {"region": a.region, "reasoning": a.reasoning, "year": a.year}
    generate(a.model, a.api_model or a.model, a.provider, a.n, out, meta, dry_run=a.dry_run, batch=a.batch)

if __name__ == "__main__":
    main()
