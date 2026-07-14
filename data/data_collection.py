"""
data_collection.py — generate machine DAT responses to standardize every model to n=1000 @ temp 0.5.

BASELINE PROMPT: verbatim `baseline_prompt_1` from the NHB divergent-creativity OSF
(osf.io/a9v2t -> studies_prompts.ipynb, Study 1a/1b). Loaded from data/baseline_prompt.txt.
Do NOT paraphrase — it must match the existing 12,397 rows exactly.

Parity contract (must match existing temp-0.5 rows):
  - prompt      : baseline_prompt.txt (verbatim)
  - temperature : 0.5
  - output cols : model_name, batch, temperature, source_file, dat_score, noun_0..noun_9
Appends new rows to data/raw/topup_<provider>.csv, then re-run 01_build_temp05_dataset.py.

Providers are pluggable. Each returns the raw text completion for BASELINE_PROMPT @ temp 0.5.
API keys are read from env at runtime (never hard-coded, never logged).

Usage:
  python data_collection.py --model gpt-4o --provider openai --n 10 [--dry-run]
  python data_collection.py --from-inventory model_inventory.csv   # top-up every model to TARGET_N
"""
import argparse, csv, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).parent
BASELINE_PROMPT = (HERE / "baseline_prompt.txt").read_text().strip()
TEMPERATURE = 0.5
TARGET_N_PER_MODEL = 1000
NOUN_COLS = [f"noun_{i}" for i in range(10)]

# ---- provider adapters: model_name -> raw completion text ----------------------------------
def _post(url, headers, body, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def openai_chat(api_model, key, temperature=TEMPERATURE):
    d = _post("https://api.openai.com/v1/chat/completions",
              {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
              {"model": api_model, "messages": [{"role": "user", "content": BASELINE_PROMPT}],
               "temperature": temperature})
    return d["choices"][0]["message"]["content"].strip()

def anthropic_chat(api_model, key, temperature=TEMPERATURE):
    d = _post("https://api.anthropic.com/v1/messages",
              {"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
              {"model": api_model, "max_tokens": 200, "temperature": temperature,
               "messages": [{"role": "user", "content": BASELINE_PROMPT}]})
    return "".join(b.get("text", "") for b in d["content"]).strip()

def xai_chat(api_model, key, temperature=TEMPERATURE):
    d = _post("https://api.x.ai/v1/chat/completions",
              {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
              {"model": api_model, "messages": [{"role": "user", "content": BASELINE_PROMPT}],
               "temperature": temperature})
    return d["choices"][0]["message"]["content"].strip()

# OpenAI-compatible endpoints (DeepSeek, Qwen/DashScope, Moonshot/Kimi, etc.)
def openai_compatible(base_url, env_key):
    def _fn(api_model, key, temperature=TEMPERATURE):
        d = _post(f"{base_url}/chat/completions",
                  {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                  {"model": api_model, "messages": [{"role": "user", "content": BASELINE_PROMPT}],
                   "temperature": temperature})
        return d["choices"][0]["message"]["content"].strip()
    _fn.env_key = env_key
    return _fn

PROVIDERS = {
    "openai":    {"fn": openai_chat,    "env": "OPENAI_API_KEY"},
    "anthropic": {"fn": anthropic_chat, "env": "ANTHROPIC_API_KEY"},
    "xai":       {"fn": xai_chat,       "env": "XAI_API_KEY"},
    "deepseek":  {"fn": openai_compatible("https://api.deepseek.com/v1", "DEEPSEEK_API_KEY"), "env": "DEEPSEEK_API_KEY"},
    "qwen":      {"fn": openai_compatible("https://dashscope.aliyuncs.com/compatible-mode/v1", "QWEN_API_KEY"), "env": "QWEN_API_KEY"},
    "moonshot":  {"fn": openai_compatible("https://api.moonshot.ai/v1", "MOONSHOT_API_KEY"), "env": "MOONSHOT_API_KEY"},
    "openrouter":{"fn": openai_compatible("https://openrouter.ai/api/v1", "QWEN_API_KEY"), "env": "QWEN_API_KEY"},
    "hunyuan":   {"fn": openai_compatible("https://tokenhub.tencentmaas.com/v1", "HUNYUAN_API_KEY"), "env": "HUNYUAN_API_KEY"},
    "doubao":    {"fn": openai_compatible("https://ark.cn-beijing.volces.com/api/v3", "DOUBAO_API_KEY"), "env": "DOUBAO_API_KEY"},
}

def parse_nouns(text):
    """Parse the comma-separated response into exactly 10 nouns; return None if not parseable."""
    t = text.replace("\n", ",")
    parts = [p.strip().strip('".').strip() for p in t.split(",")]
    parts = [p for p in parts if p and not p[0].isdigit()]
    return parts[:10] if len(parts) >= 10 else None

def score_dat(nouns):
    """DAT score = mean pairwise semantic distance (GloVe). Deferred to the scoring step to keep
    this collector dependency-free; store nouns now, score in 01_build/scoring pass."""
    return ""  # dat_score filled by the scoring pass, matching NHB dat_new


def call_with_temp(fn, api_model, key):
    """Try temp 0.5 for parity. If the model rejects it (some models only allow temp 1),
    fall back to temp 1.0 and record the actual temperature used, so provenance is honest."""
    try:
        return fn(api_model, key, TEMPERATURE), TEMPERATURE
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
        except Exception:
            body = getattr(e, "_body", "") or ""
        if e.code == 400 and "temperature" in body.lower():
            return fn(api_model, key, 1.0), 1.0
        # re-raise as a plain error carrying the body so upstream handling is stable
        raise RuntimeError(f"HTTP {e.code}: {body[:200]}")

def generate(model_name, api_model, provider, n, out_csv, dry_run=False, sleep=0.3, max_retries=4):
    prov = PROVIDERS[provider]
    key = os.environ.get(prov["env"])
    if not key:
        sys.exit(f"Missing env key {prov['env']} for provider {provider}")
    fn = prov["fn"]
    rows, attempts = [], 0
    while len(rows) < n:
        try:
            raw, temp_used = call_with_temp(fn, api_model, key)
        except urllib.error.HTTPError as e:
            attempts += 1
            msg = e.read().decode()[:200]
            if e.code == 429 and attempts <= max_retries:
                time.sleep(min(2 ** attempts, 30)); continue
            sys.exit(f"[{provider}/{api_model}] HTTP {e.code}: {msg}")
        except RuntimeError as e:
            attempts += 1
            if '429' in str(e) and attempts <= max_retries:
                time.sleep(min(2 ** attempts, 30)); continue
            sys.exit(f"[{provider}/{api_model}] {e}")
        nouns = parse_nouns(raw)
        if not nouns:
            attempts += 1
            if attempts > n + max_retries:
                sys.exit(f"[{provider}/{api_model}] too many unparseable responses")
            continue
        rows.append({"model_name": model_name, "batch": "collect_2026", "temperature": temp_used,
                     "source_file": out_csv.name, "dat_score": score_dat(nouns),
                     **{c: nouns[i] for i, c in enumerate(NOUN_COLS)}})
        if dry_run:
            print(json.dumps(rows[-1], ensure_ascii=False)); return rows
        time.sleep(sleep)
    write_rows(out_csv, rows)
    print(f"[{provider}/{api_model}] wrote {len(rows)} rows -> {out_csv}")
    return rows

def write_rows(out_csv, rows):
    if not rows: return
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    exists = out_csv.exists()
    with open(out_csv, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["model_name","batch","temperature","source_file","dat_score"]+NOUN_COLS)
        if not exists: w.writeheader()
        w.writerows(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="canonical model_name (as in model_inventory.csv)")
    ap.add_argument("--api-model", help="provider's API model id (defaults to --model)")
    ap.add_argument("--provider", choices=list(PROVIDERS))
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--dry-run", action="store_true", help="one call, print, don't write")
    args = ap.parse_args()
    if not (args.model and args.provider):
        sys.exit("need --model and --provider (or extend for --from-inventory batch mode)")
    out = HERE / "raw" / f"topup_{args.provider}.csv"
    generate(args.model, args.api_model or args.model, args.provider, args.n, out, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
