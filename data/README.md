# Machine DAT Data Collection — `data/`

| File | What it is |
|---|---|
| **`models.csv`** | **The single source of truth for the model grid.** One row per model: `#, model, year, region, reasoning, provider, api_model_id, type, existing_samples_legacy, status`. Replaces the old `model_id_mapping.csv` / `model_inventory.csv` / `model_inventory_final.csv` / `model_summary.csv`. |
| `data_collection.py` | **The collection script.** Single model (`--model ... --provider ...`) or full batch (`--all`). One raw row per generation, full provenance, incremental flush, resumable (skips models already at target n). Baseline prompt embedded in-code, verified against the SHA below. |
| `run_parallel.py` | **The parallel run driver.** 7 lanes (one thread per provider key) run at once; within each lane a small worker pool (`--concurrency`, default 3) shares a **0.5 s launch gate** so no two requests on the same key start less than `--min-gap` seconds apart, even under concurrency. Thread-safe incremental writes, resumable. Reuses `data_collection`. |
| `data_cleaning.py` | **The cleaning/build script.** Builds the canonical temperature-0.5 dataset from the archived source machine files, tagging source + temperature, and writes `processed/machine_temp05.csv` (+ summary). |
| `raw/` | The one raw output folder — per-provider `topup_<provider>.csv` files written during collection. |
| `processed/` | Consolidated outputs: `machine_all.csv` (one row per generation, stable `record_id`s) and `machine_temp05.csv` (cleaned temp-0.5 analysis set). |
| `legacy/` | Archived material, not part of active collection: the flat temp-0.5 reference data, and `prior_raw_inputs/` (Anthony's original `average_machine_raw.csv` / `new_machine_baseline.csv` source files, consumed by `data_cleaning.py`). |

---

## Locked design (2026-07-15)

### Baseline prompt (verbatim — do NOT paraphrase)
Source: https://osf.io/a9v2t/files/y4rhs (`studies_prompts.ipynb`, `baseline_prompt_1`, Study 1a/1b).
SHA-256: `d03218e72a815ec8...` (asserted at collection time). Matches the existing 12,397 legacy rows.

```
Generate 10 nouns that are as different from each other as possible using the instructions below:
1. Generate only single-word nouns in English.
2. Generate only nouns such as things, objects and concepts.
3. Do not use proper nouns such as people or places.
4. Do not use specialised vocabulary or technical terms.
5. Generate your final response as a string with each noun separated by commas: "noun_1, noun_2, noun_3, noun_4, noun_5, noun_6, noun_7, noun_8, noun_9, noun_10".
6. Do not return anything else other than the comma-separated string of nouns.
```

> The exact prompt is embedded in `data_collection.py`; there is no separate `baseline_prompt.txt`.

### Temperature — per-provider midpoint (LOCKED 2026-07-14)
- The collector requests each provider's **scale midpoint**: providers on a **0–2** scale
  (OpenAI, xAI, DeepSeek, Qwen, Hunyuan, Moonshot) get **temperature = 1.0**; providers on a **0–1**
  scale (Anthropic) get **temperature = 0.5**. This is the locked design, chosen so every model runs at
  the neutral centre of its own supported range rather than at one arbitrary absolute value.
- Every row records `temperature_requested`, `temperature_effective` (what was actually used), and
  `temp_range_used` (the provider's scale), so the choice is fully auditable per row.
- **Exception handling:** if a model rejects the midpoint (some newer models only accept temperature = 1),
  the collector falls back to the model's allowed default and records the TRUE value. Those rows are a
  documented exception, not silently mixed in.
- The legacy temp-0.5 reference data in `legacy/` was collected under the earlier flat-0.5 setting and is
  kept separate; it is a comparison input, not part of the midpoint collection.

### Other locked choices
- **Target n:** 500 per model.
- **Region label:** `Western` / `Eastern` = model origin; all prompts are in English.
- **Noun parsing:** parsed nouns are lowercase-normalized; `raw_response_text` is kept verbatim.
- **DAT scoring:** deferred to data cleaning (`dat_score` stays blank during collection).
- **DAT scorer:** use Olson et al. 2021 (github.com/jayolson/divergent-association-task).
- **Slow models:** Gemini and GLM are dropped entirely — both exceed the ~1 min/call budget (GLM ran 30–55 s/call), which at n=500 would push the run past ~8 h. Excluded from the grid, not merely deprioritized.

---

## The model grid (`models.csv`)

55 rows total: **38 live/collectable models** + 17 retired/legacy rows whose existing data stands. Columns:

`#, model, year, region, reasoning, provider, api_model_id, type, existing_samples_legacy, status`

**Grid revision 2026-07-15 (55 models).** Balanced against: ≤1 min/call (GLM dropped entirely, like
Gemini); lanes roughly even with Western keys heaviest (OpenAI 10, Anthropic 7, Hunyuan/TokenHub 6, Qwen 5,
xAI 4, Moonshot 4, DeepSeek native 2); a mix of **fast / all-rounder / reasoning** types (12 / 23 / 20);
**Eastern + Western** (23 / 32); and an era spread across **2022–2026**. All 7 distinct Eastern reasoning
models are preserved (DeepSeek-V4-Pro, DeepSeek-R1, DeepSeek-V3.2, Qwen3.7-Max, MiniMax-M3, MiniMax-M2.7,
Kimi-K2.6). 38 models are collected live at n=500; the other 17 are legacy/retired rows whose existing data
stands (source of the 2022–2024 depth).

**DeepSeek naming convention:** the display name matches the actual API version (`DeepSeek-V4-Pro`,
`DeepSeek-R1`, `DeepSeek-V3.2`, ...). When the same version is collected on a second key (e.g. TokenHub as
well as DashScope), the second row carries a lane suffix (`-TH`) so rows stay distinct and honest about
which endpoint produced them. `type` = fast / allrounder / reasoning.

---

## Provider configuration

| Provider | Env key | Base URL |
|---|---|---|
| openai | `OPENAI_API_KEY` | default |
| anthropic | `ANTHROPIC_API_KEY` | default |
| xai | `XAI_API_KEY` | default |
| qwen (DashScope) | `QWEN_API_KEY` | dashscope.aliyuncs.com/compatible-mode/v1 |
| deepseek | `DEEPSEEK_API_KEY` | api.deepseek.com/v1 |
| hunyuan (TokenHub) | `HUNYUAN_API_KEY` | tokenhub.tencentmaas.com/v1 |
| moonshot | `MOONSHOT_API_KEY` | api.moonshot.ai |

Keys are read from env at runtime — never hard-coded, never written to disk.
Known-benign metadata gaps: Anthropic/Qwen/Hunyuan return no `system_fingerprint`;
DeepSeek/Hunyuan return no `api_request_id`.

---

## How to run

```bash
# one model, quick sanity check (prints one row, writes nothing)
python data/data_collection.py --model "GPT-4.1" --api-model gpt-4.1 --provider openai --n 1 --dry-run

# FULL RUN (recommended): 7 lanes in parallel, 3 runners per lane, 0.5s launch gate per lane
python data/run_parallel.py --n 500 --concurrency 3 --min-gap 0.5 --batch collect_2026_n500
#   - one lane per API key (7 keys -> 7 parallel lanes); rate limits are per key, so lanes never
#     collide with each other. --concurrency = runners WITHIN each lane; --min-gap = min seconds
#     between request launches on a single lane (held >=0.5s under any concurrency).
#   - --only openai,anthropic  restricts to a subset of lanes.
#   - resumable: skips models already at n; safe to re-run after an interruption.

# serial fallback (no threads): one provider, or all providers serially
python data/data_collection.py --all --n 500 --provider openai
python data/data_collection.py --all --n 500

# build the cleaned temperature-0.5 analysis dataset
python data/data_cleaning.py
```

Each row carries: identity + provenance (timestamps, api request/response ids, system fingerprint,
finish reason, token usage, prompt SHA-256), the verbatim `raw_response_text`, `parse_status`, and
`noun_0..noun_9`. `dat_score` is filled in the separate scoring pass.
