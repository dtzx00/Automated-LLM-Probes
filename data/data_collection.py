"""
data_collection.py — generate machine DAT responses with FULL open-science provenance.

BASELINE PROMPT: verbatim `baseline_prompt_1` from the NHB divergent-creativity OSF
(osf.io/a9v2t -> studies_prompts.ipynb, Study 1a/1b). Loaded from data/baseline_prompt.txt.
Do NOT paraphrase.

TEMPERATURE: per-provider MIDPOINT (option 1, locked 2026-07-14). 0-2 providers -> 1.0;
0-1 providers -> 0.5. Recorded per row (requested + effective + range). If a model forces
its own temperature, the row records what was actually used.

Each generation writes ONE raw row with full provenance (timestamps, api request/response ids,
system fingerprint, finish reason, token usage, prompt sha256, raw response text, parsed nouns).
DAT scoring is a SEPARATE later pass; dat_score stays blank here.

Keys read from env at runtime; never hard-coded, never written to disk.

Usage:
  python data_collection.py --model "GPT-4o" --api-model gpt-4o-2024-08-06 --provider openai --n 5 [--dry-run]
  python data_collection.py --from-inventory data/model_id_mapping.csv --n 500   # full run
"""
import argparse, csv, hashlib, json, os, subprocess, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
BASELINE_PROMPT = (HERE / "baseline_prompt.txt").read_text().strip()
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
def _post_full(url, headers, body, timeout=180):
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

def generate(model_name, api_model, provider, n, out_csv, meta, dry_run=False, seed_base=1000, pace=0.25, max_retries=5):
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
            sys.exit(f"[{provider}/{api_model}] {e}")
        resp_ts = _now(); latency = int((time.time()-t0)*1000)
        nouns = parse_nouns(payload["text"])
        status = "ok" if nouns else "failed"
        row = {
            "record_id": "", "model_name": model_name, "api_model_requested": api_model,
            "api_model_returned": payload.get("api_model_returned",""), "provider": provider,
            "endpoint_base": payload.get("endpoint_base",""), "batch": "collect_2026_midpoint",
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--api-model"); ap.add_argument("--provider", choices=list(PROVIDERS))
    ap.add_argument("--n", type=int, default=5); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--region", default=""); ap.add_argument("--reasoning", default=""); ap.add_argument("--year", default="")
    a = ap.parse_args()
    if not (a.model and a.provider): sys.exit("need --model and --provider")
    out = HERE / "raw" / f"topup_{a.provider}.csv"
    meta = {"region": a.region, "reasoning": a.reasoning, "year": a.year}
    generate(a.model, a.api_model or a.model, a.provider, a.n, out, meta, dry_run=a.dry_run)

if __name__ == "__main__":
    main()
