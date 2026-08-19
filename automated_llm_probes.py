from __future__ import annotations
import csv,hashlib,importlib,os,pickle,re,time
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm

TEMPERATURE_STD = 0.5
MAX_RETRIES = 3
MAX_CONSECUTIVE_FAILURES = 3
SLEEP_BETWEEN_CALLS = 0.2
REQUEST_TIMEOUT = 60
DATA_ROOT = Path("data")

KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "spacexai": "XAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "qwen": "QWEN_API_KEY",
    "hunyuan": "HUNYUAN_API_KEY",
    "moonshot": "MOONSHOT_API_KEY",
    "doubao": "DOUBAO_API_KEY",
}

def load_models(path="models.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def ready_models(models=None):
    models = models or load_models()
    return [m for m in models if os.environ.get(KEY_ENV.get(m["api"], ""), "").strip()]

def get_api_module(api_name):
    return importlib.import_module(f"api.{api_name}")

def call_model(model_row, messages):
    mod = get_api_module(model_row["api"])
    key = os.environ[KEY_ENV[model_row["api"]]]
    temp = model_row.get("temperature")
    temp = float(temp) if temp not in (None, "") else None
    base = model_row.get("base_url") or None
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return mod.call(key, model_row["model_id"], messages,
                            base_url=base, temperature=temp, timeout=REQUEST_TIMEOUT)
        except Exception as e:
            last_err = e
            time.sleep(min(2 ** attempt, 20))
    raise RuntimeError(f"{model_row['name']} failed after {MAX_RETRIES} tries: {last_err}")

def _model_dir(task, name, temp):
    slug = re.sub(r"[^\w\-.]+", "-", name.strip()).strip("-").lower()
    t = str(temp).rstrip("0").rstrip(".") if temp is not None else "default"
    return DATA_ROOT / task.lower() / slug / t

def _hash(*parts, n=16):
    return hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:n]

def _now():
    return datetime.now(timezone.utc).isoformat()

def get_probe(test_name):
    try:
        from automated_intelligence_tests import get_probe as _gp
        return _gp(test_name)
    except ImportError:
        raise ImportError(
            "AIT is required for probe definitions. "
            "Install Automated-Intelligence-Tests or place it on PYTHONPATH.")

def collect(test_name, models=None, n_per_model=250):
    models = models or ready_models()
    probe = get_probe(test_name)
    for m in models:
        mdir = _model_dir(test_name, m["name"], m.get("temperature") or TEMPERATURE_STD)
        mdir.mkdir(parents=True, exist_ok=True)
        have = sum(1 for p in mdir.glob("*.pickle") if p.is_file())
        if have >= n_per_model:
            print(f"  {m['name']}: {have}/{n_per_model} done — skip")
            continue
        need = n_per_model - have
        print(f"  {m['name']}: {have} have, {need} to collect")
        fails = 0
        for k in range(need):
            i = have + k
            kw = probe.sample(i)
            messages = probe.build_prompt(**kw)
            if isinstance(messages, str):
                messages = [{"role": "user", "content": messages}]
            prompt = messages[0]["content"] if messages else ""
            ts = _now()
            h = _hash(test_name, m["name"], m["model_id"], i, ts, prompt[:80])
            row = {
                "task": test_name.strip().upper(),
                "model_name": m["name"],
                "model_id": m["model_id"],
                "provider": m["api"],
                "rep": i,
                "temperature_std": m.get("temperature") or TEMPERATURE_STD,
                "kwargs": kw,
                "prompt": prompt,
                "ts_utc": ts,
                "hash": h,
            }
            try:
                raw = call_model(m, messages)
                row.update(raw=raw, error="")
                fails = 0
                with open(mdir / f"{h}.pickle", "wb") as f:
                    pickle.dump(row, f, protocol=pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                row.update(raw="", error=str(e))
                fails += 1
                print(f"  SKIP {m['name']} rep={i}: {e}")
                if fails >= MAX_CONSECUTIVE_FAILURES:
                    print(f"  >> {m['name']}: {fails} consecutive fails — skip rest")
                    break
            time.sleep(SLEEP_BETWEEN_CALLS)
    print(f"DONE {test_name}")

def parse_and_merge(test_name: str) -> dict:
    """
    Load valid pickle rows for a task.
    Returns dict {hash: row} containing metadata + raw
    """
    task_dir = DATA_ROOT / test_name.lower()
    if not task_dir.is_dir():
        raise FileNotFoundError(task_dir)

    files = list(task_dir.rglob("*.pickle"))
    rows = {}

    for p in tqdm(files, desc=test_name):
        try:
            with p.open("rb") as f:
                row = pickle.load(f)

            if row.get("error") or not row.get("raw"):
                continue

            h = row.pop("hash", None)
            if h is not None:
                rows[h] = row

        except Exception:
            continue

    if not rows: print("No valid rows")
    return rows

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python automated-llm-probes.py collect|parse <test_name> [n]")
        sys.exit(1)
    cmd = sys.argv[1]
    test = sys.argv[2] if len(sys.argv) > 2 else "DAT"
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 250
    if cmd == "collect":
        collect(test, n_per_model=n)
    elif cmd == "parse":
        parse_and_merge(test)
    else:
        print("Unknown command")
