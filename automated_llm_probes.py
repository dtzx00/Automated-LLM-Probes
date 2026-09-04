from __future__ import annotations
import automated_intelligence_tests as ait
import csv,hashlib,importlib,os,pickle,re,time,sys
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm

TEMPERATURE_STD = 0.5
MAX_RETRIES = 3
MAX_CONSECUTIVE_FAILURES = 3
SLEEP_BETWEEN_CALLS = 0.2
REQUEST_TIMEOUT = 60
DATA_ROOT = Path("data")
DEAD_PREFIXES = ("RETIRED", "DEAD", "BAD-ID", "DUPLICATE", "UPSTREAM-ALIAS", "ALIASES")

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
    return [m for m in models
            if os.environ.get(KEY_ENV.get(m["api"], ""), "").strip()
            and not m.get("status", "").upper().startswith(DEAD_PREFIXES)]

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

def collect(test_name, models=None, n_per_model=250, cue=None, seed=None, **instruct_kwargs):
    """Collect model responses for a test.
    cue, seed, and any other kwargs are forwarded to ait.instruct().
    cue=None keeps the current randomized-stimulus behavior.
    The same cue/seed is used for every rep in this run.
    """
    models = models or ready_models()

    for m in models:

        mdir = _model_dir(test_name, m["name"], m.get("temperature") or None)
        mdir.mkdir(parents=True, exist_ok=True)
        have = sum(1 for p in mdir.glob("*.pickle") if p.is_file())
        if have >= n_per_model:
            print(f"  {m['name']}: {have}/{n_per_model} done — skip")
            continue
        need = n_per_model - have
        print(f"  {m['name']}: {have} collected, {need} to collect")

        fails = 0
        for k in tqdm(range(need), desc=test_name):

            i = have + k
            stim = ait.instruct(
                test_name.lower(),
                cue=cue,
                seed=seed,
                **instruct_kwargs,
            )
            instructions = stim["instructions"]

            ts = _now()
            h = _hash(test_name, m["name"], m["model_id"], i, ts, instructions[:40])
            row = {
                "task": test_name.strip().upper(),
                "model_name": m["name"],
                "model_id": m["model_id"],
                "provider": m["api"],
                "rep": i,
                "temperature_std": m.get("temperature") or None,
                "kwargs": stim,
                "prompt": instructions,
                "ts_utc": ts,
                "hash": h}

            try:
                raw = call_model(m, [{"role": "user", "content": instructions}])
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

def _parse_cli_cue(test_name, cue_args):
    """Turn --cue values into the object ait.instruct() expects."""
    if not cue_args:
        return None
    test_name = test_name.strip().lower()
    if len(cue_args) == 1:
        raw = cue_args[0].strip()
        if raw.startswith("[") or raw.startswith("{"):
            import json
            return json.loads(raw)
    if test_name in ("aut", "dat"):
        if len(cue_args) != 1:
            sys.exit("AUT/DAT accept a single --cue value")
        return cue_args[0].strip()
    if test_name == "cwt":
        words = []
        for v in cue_args:
            words.extend(w.strip() for w in v.split(",") if w.strip())
        return words
    if test_name == "cat":
        pairs = []
        for v in cue_args:
            for chunk in re.split(r"[;|]", v):
                chunk = chunk.strip()
                if not chunk:
                    continue
                if ":" in chunk and "," not in chunk:
                    a, b = chunk.split(":", 1)
                else:
                    parts = [p.strip() for p in chunk.split(",") if p.strip()]
                    if len(parts) != 2:
                        sys.exit(
                            f"CAT --cue must be word1,word2 or word1:word2 (got {chunk!r})"
                        )
                    a, b = parts
                pairs.append((a.strip(), b.strip()))
        return pairs
    return cue_args[0]


def _split_collect_args(argv):
    cue_args, seed, n_words, single_item, positional = [], None, None, False, []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--cue":
            i += 1
            if i >= len(argv):
                sys.exit("--cue needs a value")
            cue_args.append(argv[i])
        elif a.startswith("--cue="):
            cue_args.append(a.split("=", 1)[1])
        elif a == "--seed":
            i += 1
            seed = int(argv[i])
        elif a.startswith("--seed="):
            seed = int(a.split("=", 1)[1])
        elif a == "--n-words":
            i += 1
            n_words = int(argv[i])
        elif a.startswith("--n-words="):
            n_words = int(a.split("=", 1)[1])
        elif a in ("--single-item", "--single_item"):
            single_item = True
        elif a.startswith("-"):
            sys.exit(f"Unknown flag: {a}")
        else:
            positional.append(a)
        i += 1
    return positional, cue_args, seed, n_words, single_item


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(
            "Usage:\n"
            "  python automated_llm_probes.py collect <test> [n] [model ...] "
            "[--cue ...] [--seed N] [--n-words N] [--single-item]\n"
            "  python automated_llm_probes.py parse <test>\n"
            "  python automated_llm_probes.py list_models"
        )
        sys.exit(0 if len(sys.argv) > 1 else 1)

    cmd = sys.argv[1].lower()

    if cmd == "list_models":
        for m in ready_models():
            print(f"{m['name']:25s} {m['vendor']:12s} {m['api']:10s} {m['model_id']}")
        sys.exit(0)

    if cmd == "parse":
        if len(sys.argv) < 3:
            sys.exit("Usage: python automated_llm_probes.py parse <test>")
        rows = parse_and_merge(sys.argv[2])
        print(f"{sys.argv[2]}: {len(rows)} rows")
        sys.exit(0)

    if cmd != "collect":
        sys.exit(f"Unknown command {cmd!r}. Use collect, parse, or list_models.")

    positional, cue_args, seed, n_words, single_item = _split_collect_args(sys.argv[2:])
    if not positional:
        sys.exit("Usage: python automated_llm_probes.py collect <test> [n] [model ...]")

    test = positional[0]
    n_per_model = next((int(a) for a in positional[1:] if a.isdigit()), 250)
    names = [a for a in positional[1:] if not a.isdigit()]
    models = [m for m in ready_models() if m["name"] in names] if names else None

    instruct_kwargs = {}
    if n_words is not None:
        instruct_kwargs["n_words"] = n_words
    if single_item:
        instruct_kwargs["single_item"] = True

    collect(
        test,
        models=models,
        n_per_model=n_per_model,
        cue=_parse_cli_cue(test, cue_args),
        seed=seed,
        **instruct_kwargs,)