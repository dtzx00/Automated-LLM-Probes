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

```bash
git pull origin main
pip install -r requirements.txt
source /Users/daweiwang/.config/llm_api_keys.sh   # or your own key file
```

Make sure Automated-Intelligence-Tests is installed to your environment.<br>
If not, simply install it using `pip3 install automated-intelligence-tests`.<br>
After installing, all probe functions can be imported.

## Usage

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

Responses are stored as pickles under `data/<task>/<model>/<temp>/`. <br>
Data are then merged into `data/<task>.csv`. Data folder is gitignored.

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
