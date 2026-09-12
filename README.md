# Automated-LLM-Probes

Minimal package that calls LLM APIs and saves the responses. It contains **no probe logic** (no prompts, no item sampling, no answer parsing). All probe definitions live in [Automated-Intelligence-Tests](https://github.com/dtzx00/Automated-Intelligence-Tests) and are imported as:

- `ait.instruct(...)` → stimulus + instruction text
- `ait.parse(...)`    → parsing is always enforced
- `ait.evaluate(...)` → scoring is set by default 

Successful `collect()` calls `ait.parse` then `ait.evaluate` and writes `parsed` + `score` on every pickle (`scoring=True` by default). Pass `scoring=False` or `--no-scoring` to skip evaluate; `parsed` is still written. Existing pickles are backfilled.

## Layout

```
api/                     # one file per provider family
  openai.py
  claude.py
  openrouter.py
  spacexai.py
  deepseek.py
  qwen.py
  hunyuan.py
  moonshot.py
  doubao.py
data/                    # responses land here (gitignored contents)
models.csv               # calling registry (name, vendor, api, model_id, ...)
automated_llm_probes.py  # collect() + parse_and_merge()
requirements.txt         # openai, anthropic
```

## Setup

Make sure Automated-Intelligence-Tests is installed to your environment. If not, simply install it using `pip3 install automated-intelligence-tests`. After installing, all probe functions can be imported.

```bash
git pull origin main
pip install -r requirements.txt
source /Users/daweiwang/.config/llm_api_keys.sh   # or your own key file
```

## Usage

Responses are stored as pickles under `data/<task>/<model>/<temp>/`. Data are then merged into `data/<task>.csv`. Data folder is gitignored.

```bash
# collect responses using all models that have keys
python automated_llm_probes.py collect DAT 250

# collect specific models (quote names that contain spaces)
python automated_llm_probes.py collect DAT 250 "Llama-4 Maverick"

# collect with a pinned cue
python automated_llm_probes.py collect AUT 260 --cue brick
python automated_llm_probes.py collect CWT 100 --cue stamp,letter,send
python automated_llm_probes.py collect CAT 50 --cue television,lake --single-item
python automated_llm_probes.py collect CAT 50 --cue television:lake --single-item

# still random if --cue is omitted
python automated_llm_probes.py collect AUT 250

# load valid pickles for a task (does not write CSV)
python automated_llm_probes.py parse DAT

# models that have keys and are not marked dead
python automated_llm_probes.py list_models
```

`collect()` defaults to `n_to_topup=True`: `n_per_model` is how many **new** samples to add, even if the folder is already full. Pass `n_to_topup=False` to only fill the shortfall. The CLI has no flag for this, so CLI collect always tops up.

```python
from automated_llm_probes import collect

collect("DAT", n_per_model=50)                       # add 50 new per model
collect("DAT", n_per_model=250, n_to_topup=False)    # fill until 250 exist
collect("DAT", n_per_model=50, scoring=False)        # parsed only, score=None
```

## Output

Each successful `collect` call writes one pickle under `data/<task>/<model-slug>/<temp>/<hash>.pickle`:

- `<task>` — lowercased test name (`dat`, `aut`, `cat`, `cwt`)
- `<model-slug>` — `name` from `models.csv`, lowercased, non-word characters turned into `-`
- `<temp>` — the model's temperature, or `default` if blank
- `<hash>` — first 16 hex chars of SHA-256 over `test`, model `name`, `model_id`, rep index, UTC timestamp, and the first 40 characters of the prompt

Failed calls are printed and skipped. They are not written.

| key | type | meaning |
| --- | --- | --- |
| `task` | str | uppercased test name (`AUT`, `DAT`, …) |
| `model_name` | str | `name` from `models.csv` |
| `model_id` | str | string sent to the API |
| `provider` | str | `api` column (which `api/*.py` file was used) |
| `rep` | int | repetition index, 0-based |
| `temperature` | str or None | temperature from `models.csv`, or `None` if blank |
| `kwargs` | dict | full return value of `ait.instruct()` |
| `prompt` | str | `kwargs["instructions"]` — the exact text sent to the model |
| `ts_utc` | str | UTC ISO-8601 timestamp |
| `hash` | str | same 16-char hash as the filename |
| `raw` | str | model text (stripped). Not a dict. |
| `error` | str | empty string on success |
| `parsed` | list / dict / None | `ait.parse(test, raw, stim=kwargs)` output. |
| `score`  | float / None       | `ait.evaluate(...)["score"]` when worked. |

`parse_and_merge()` also copies `kwargs["cue"]` onto each row as `cue`.

`kwargs` always includes at least:

```python
{"test": "aut",            # cat / dat / aut / cwt
 "cue": "brick",           # str for AUT/DAT; list[str] for CWT; list[tuple] for CAT
 "n_words": None,
 "instructions": "...",    # same string as prompt
 "response_format": {...}}
```

## Models

```bash
# check what models are available in the package
python automated_llm_probes.py list_models
```

Models all put under models.csv. One row per model + lane. Model naming conventions: lowercase, family-tier-version, hyphens between words (kebab-case), dots kept inside version numbers. Model list column conventions:

| column      | meaning |
|-------------|---------| 
| name        | unique label |
| vendor      | who built the model |
| api         | which `api/*.py` file to use |
| model_id    | exact string sent to the API |
| release_date | date model was released to public |
| temperature | blank = omit, otherwise the value to send |
| speed_per_call | speed to return "ok" |
| status | status ok or not |
| reply | reply when asked about "ok" |
| errors | errors message if any |

Edit this file (or filter the loaded list in code) to choose which models are probed.

## Requirements

- Python 3.9+ and required package: [Automated-Intelligence-Tests](https://github.com/dtzx00/Automated-Intelligence-Tests)
- Only two external packages for model API: `openai` and `anthropic`
- All other providers are OpenAI-compatible and reuse the same client with a different base URL
