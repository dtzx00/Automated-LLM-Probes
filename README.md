# Automated-LLM-Probes

Minimal package that calls LLM APIs and saves the responses.
It contains **no probe logic** (no prompts, no item sampling, no answer parsing).
All probe definitions live in [Automated-Intelligence-Tests](https://github.com/dtzx00/Automated-Intelligence-Tests) and are imported as three functions:

- `sample(i)` → parameters for repetition *i*
- `build_prompt(**kwargs)` → the instruction text
- `parse(raw, **kwargs)` → structured fields from a response

## Layout

```
api/                    # one file per provider family
  openai.py
  claude.py
  openrouter.py
  spacexai.py
  deepseek.py
  qwen.py
  hunyuan.py
  moonshot.py
  doubao.py
data/                   # responses land here (gitignored contents)
models.csv              # calling registry (name, vendor, api, model_id, ...)
automated-llm-probes.py # collect() + parse_and_merge()
requirements.txt        # openai, anthropic
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
python automated-llm-probes.py collect DAT 250

# collect specific models such as Llama-4 Maverick
python automated_llm_probes.py collect DAT 250 "Llama-4 Maverick"

# restrict to a subset by editing the call or filtering models.csv
python automated-llm-probes.py collect DAT 50

# merge / parse the pickles into a CSV
python automated-llm-probes.py parse DAT
```

Responses are stored as pickles under `data/<task>/<model>/<temp>/`. <br>
Data are then merged into `data/<task>.csv`. Data folder is gitignored.

## models.csv

One row per model + lane. Columns:

| column      | meaning |
|-------------|---------|
| name        | unique label |
| vendor      | who built the model |
| api         | which `api/*.py` file to use |
| model_id    | exact string sent to the API |
| base_url    | optional override |
| temperature | blank = omit, otherwise the value to send |

Edit this file (or filter the loaded list in code) to choose which models are probed.

## Design notes

- Python 3.9+
- Only two external packages: `openai` and `anthropic`
- All other providers are OpenAI-compatible and reuse the same client with a different base URL
- Pure and minimal — no over-engineering
