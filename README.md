# Automated-LLM-Probes

Minimal package that calls LLM APIs and saves the responses.
It contains **no probe logic** (no prompts, no item sampling, no answer parsing).
All probe definitions live in [Automated-Intelligence-Tests](https://github.com/dtzx00/Automated-Intelligence-Tests) and are imported as:

- `ait.instruct(test, cue=None, seed=None, **kwargs)` → stimulus + instruction text
- `ait.evaluate(test, responses, **kwargs)` → score (used outside this repo)

This package only calls `instruct()`. It stores the raw model response.

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
automated-llm-probes.py  # collect() + parse_and_merge()
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

## Output

Each successful `collect` call writes one pickle and dumped to data folder as output:

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
| `temperature_std` | str or None | temperature from `models.csv`, or `None` if blank |
| `kwargs` | dict | full return value of `ait.instruct()` |
| `prompt` | str | `kwargs["instructions"]` — the exact text sent to the model |
| `ts_utc` | str | UTC ISO-8601 timestamp |
| `hash` | str | same 16-char hash as the filename |
| `raw` | str | model text (stripped). Not a dict. |
| `error` | str | empty string on success |

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

Models all put under models.csv. One row per model + lane. Columns:

| column      | meaning |
|-------------|---------|
| name        | unique label |
| vendor      | who built the model |
| api         | which `api/*.py` file to use |
| model_id    | exact string sent to the API |
| base_url    | optional override |
| temperature | blank = omit, otherwise the value to send |

Edit this file (or filter the loaded list in code) to choose which models are probed.

## Requirements

- Python 3.9+ and required package: [Automated-Intelligence-Tests](https://github.com/dtzx00/Automated-Intelligence-Tests)
- Only two external packages for model API: `openai` and `anthropic`
- All other providers are OpenAI-compatible and reuse the same client with a different base URL
