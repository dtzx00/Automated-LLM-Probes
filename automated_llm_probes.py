from __future__ import annotations
import automated_intelligence_tests as ait
import csv,hashlib,importlib,os,pickle,re,time,sys
from datetime import datetime, timezone
from pathlib import Path
from tqdm import tqdm

MAX_RETRIES = 3
MAX_CONSECUTIVE_FAILURES = 3
SLEEP_BETWEEN_CALLS = 0.2
REQUEST_TIMEOUT = 60
DATA_ROOT = Path("data")
DEAD_PREFIXES = ("RETIRED", "DEAD", "BAD-ID", "ID",
                 "DUPLICATE", "UPSTREAM-ALIAS", 
                 "ALIASES", "NAME", "unverified","unverified;")

KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "spacexai": "XAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "qwen": "QWEN_API_KEY",
    "hunyuan": "HUNYUAN_API_KEY",
    "moonshot": "MOONSHOT_API_KEY",
    "doubao": "DOUBAO_API_KEY",}

def load_models(path="models.csv"):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def ready_models(models=None):
    models = models or load_models()
    return [m for m in models
            if os.environ.get(KEY_ENV.get(m["api"], ""), "").strip()
            and not m.get(
                "status","").upper().strip().startswith(DEAD_PREFIXES)]

def get_api_module(api_name):
    return importlib.import_module(f"api.{api_name}")

def call_model(model_row, messages):
    mod = get_api_module(model_row["api"])
    key = os.environ[KEY_ENV[model_row["api"]]]
    t = (model_row.get("temperature") or "").strip()
    temp = None if t.lower() == "default" or t == "" else float(t)
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

def _parse_and_score(test_name, raw, stim, scoring=True):
    """Always parse by default. Score only when scoring=True and parse worked.
    Never raises. parse/evaluate failure → parsed and/or score stay None.
    """
    parsed, score = None, None
    try:
        parsed = ait.parse(str(test_name).strip().lower(), raw, stim=stim)
    except Exception:
        parsed = None
    if scoring and parsed is not None:
        try:
            out = ait.evaluate(str(test_name).strip().lower(), parsed)
            score = None if not isinstance(out, dict) else out.get("score")
            if score is not None:
                score = float(score)
        except Exception:
            score = None
    return parsed, score

def collect(test_name, models=None, n_per_model=250, cue=None,
            seed=None, n_to_topup=True, scoring=True, **instruct_kwargs):
    """Collect model responses for using an automated intelligence test. 
    Cue, seed, and any other kwargs are forwarded to ait.instruct().
    
    Always attempts parsing after collection, but only scores if scoring=True.
    When set True, scores with ait.evaluate. Parsed and score are always written
    (score is None when scoring=False or parse/evaluate fails).
    
    For cue behaviors: cue=None keeps the current randomized-stimulus.
    The same cue/seed is used for every rep in this run.
    
    n_to_topup=True always collects n_per_model new samples.
    n_to_topup=False only fills the shortfall (n_per_model - have).
    """
    models = models or ready_models()

    for m in models:

        mdir = _model_dir(test_name, m["name"], m.get("temperature") or None)
        mdir.mkdir(parents=True, exist_ok=True)
        have = sum(1 for p in mdir.glob("*.pickle") if p.is_file())
        need = n_per_model if n_to_topup else n_per_model - have
        if need <= 0:
            print(f"  {m['name']}: {have}/{n_per_model} done — skip")
            continue
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
                "temperature": m.get("temperature") or None,
                "kwargs": stim,
                "prompt": instructions,
                "ts_utc": ts,
                "hash": h}

            try:
                raw = call_model(m, [{"role": "user", "content": instructions}])
                parsed, score = _parse_and_score(test_name, raw, stim, scoring)
                row.update(raw=raw, error="", parsed=parsed, score=score)
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

            
def load_pickles(test_name: str) -> dict:
    """Load task pickles into {hash: row}. Skips empty raw."""
    task_dir = DATA_ROOT / test_name.lower()
    if not task_dir.is_dir():
        raise FileNotFoundError(task_dir)
    rows = {}
    for p in tqdm(list(task_dir.rglob("*.pickle")), desc=test_name):
        try:
            with p.open("rb") as f:
                row = pickle.load(f)
        except Exception as e:
            print(f"SKIP {p}: {e}")
            continue
        if row.get("error") or not row.get("raw"):
            continue
        row["cue"] = (row.get("kwargs") or {}).get("cue")
        rows[row.get("hash") or p.stem] = row
    if not rows:
        print("No valid rows")
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
    cue_args, seed, n_words, single_item, scoring, positional = [], None, None, False, True, []
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
        elif a in ("--no-scoring", "--no_scoring"):
            scoring = False
        elif a.startswith("-"):
            sys.exit(f"Unknown flag: {a}")
        else:
            positional.append(a)
        i += 1
    return positional, cue_args, seed, n_words, single_item, scoring


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("Usage:\n"
              "  python automated_llm_probes.py collect <test> [n] [model ...] "
              "[--cue ...] [--seed N] [--n-words N] [--single-item] [--no-scoring]\n"
              "  python automated_llm_probes.py load <test>\n"
              "  python automated_llm_probes.py list_models\n")
        sys.exit(0 if len(sys.argv) > 1 else 1)

    cmd = sys.argv[1].lower()

    if cmd == "list_models":
        for m in ready_models():
            print(f"{m['name']:25s} {m['vendor']:12s} {m['api']:10s} {m['model_id']}")
        sys.exit(0)

    if cmd in ("load", "parse"):
        if len(sys.argv) < 3:
            sys.exit("Usage: python automated_llm_probes.py load <test>")
        rows = load_pickles(sys.argv[2])
        print(f"{sys.argv[2]}: {len(rows)} rows")
        sys.exit(0)

    if cmd != "collect":
        sys.exit(f"Unknown command {cmd!r}. Use collect, load, or list_models.")

    positional, cue_args, seed, n_words, single_item, scoring = _split_collect_args(sys.argv[2:])
    
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
        scoring=scoring,
        **instruct_kwargs,)