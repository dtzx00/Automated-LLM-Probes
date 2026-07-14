# Machine data collection spec — standardize to n=1000 @ temp 0.5

**Goal:** every model reaches n=1000 responses at temperature 0.5, using the same baseline
prompt and the same DAT scorer (`dat_new`) as existing temp-0.5 rows, so all rows are comparable.

## Top-up for the 20 existing models (total = 7,603 generations)
| Group | Models | Current @0.5 | Top-up each |
|---|---|---:|---:|
| Old 9 | GPT-3.5-Turbo, GPT-4.0-Turbo, GPT-4o, Claude-3-Haiku, Claude-3-Opus, Claude-3.5-Sonnet, Ernie-4.0-8k, Llama-2-70b, DeepSeek-R1 | 750 | +250 |
| New sweep 9 | Claude-Opus-4.1, Claude-Sonnet-4, Deepseek-Chat, Kimi-k2, Llama4-Scout, Llama4-Maverick, Qwen-Max, Qwen-Turbo, Grok-Code-Fast | 478–515 | +485 to +522 |
| GPT-5 family | GPT-5 (550), GPT-5-Mini (500) | — | +450 / +500 |

Exact per-model counts: `data/processed/machine_temp05_summary.csv` (`need_to_1000`).

## Even-newer models to add (each +1000) — PENDING Dawei's list
Candidate gaps vs current set: Gemini 2.5 Pro/Flash (no Google model present), Claude Haiku 4,
Mistral Large, Qwen3, others. Dawei to confirm the final list; each adds 1,000 @ temp 0.5.

## Parity requirements (must match existing rows)
- **Prompt:** same baseline DAT prompt (`baseline_prompt_1`).
- **Temperature:** 0.5.
- **Scoring:** same DAT scorer -> `dat_new`.
- **Output schema:** model_name, batch, temperature=0.5, source_file, dat_score, noun_0..noun_9.

## Run ownership
Dawei will trigger the run; Lumen scripts + executes against the model APIs, writing straight
into `data/raw/` then re-running `scripts/01_build_temp05_dataset.py`.

## Baseline prompt (LOCKED — verbatim from NHB OSF a9v2t, studies_prompts.ipynb, baseline_prompt_1)
Stored at `data/baseline_prompt.txt`. Study 1a/1b baseline; matches the existing 12,397 temp-0.5 rows.

```
Generate 10 nouns that are as different from each other as possible using the instructions below:
1. Generate only single-word nouns in English.
2. Generate only nouns such as things, objects and concepts.
3. Do not use proper nouns such as people or places.
4. Do not use specialised vocabulary or technical terms.
5. Generate your final response as a string with each noun separated by commas: "noun_1, noun_2, noun_3, noun_4, noun_5, noun_6, noun_7, noun_8, noun_9, noun_10".
6. Do not return anything else other than the comma-separated string of nouns.
```
Source: https://osf.io/a9v2t/files/y4rhs (public). Do not paraphrase.

## Temperature parity rule (LOCKED 2026-07-14)
- The existing NHB baseline data (12,397 rows) was collected on a **0–1 sampling scale**; the analysis
  slice is literal API `temperature = 0.5` (verified: the sweep range is 1e-05 → 1.0, analysis == 0.5).
- **New collection passes the same literal value 0.5 to every provider** for parity. Do NOT rescale to a
  provider's own max (e.g. OpenAI supports 0–2, but the anchor is the collected value 0.5, not the midpoint).
- **Exception handling:** if a model rejects 0.5 (some newer models only allow temperature = 1, e.g. Kimi
  K2.5/K2.6), the collector falls back to the model's allowed default and records the ACTUAL temperature in
  the row's `temperature` column. Such rows are a documented parity exception, not silently mixed in.
- Every row therefore carries its true temperature; downstream analysis can filter to temperature == 0.5
  for the strict-parity set and treat exceptions separately.
