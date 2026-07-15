# Machine data collection (n=500 @ midpoint temperature)

**Goal:** every model reaches n=500 responses at midpoint temperature, using the same baseline prompt as existing temp rows, so all rows are comparable.

| Group | Models | Current @0.5 | Top-up each |
|---|---|---:|---:|
| Old 9 | GPT-3.5-Turbo, GPT-4.0-Turbo, GPT-4o, Claude-3-Haiku, Claude-3-Opus, Claude-3.5-Sonnet, Ernie-4.0-8k, Llama-2-70b, DeepSeek-R1 | 750 | +250 |
| New sweep 9 | Claude-Opus-4.1, Claude-Sonnet-4, Deepseek-Chat, Kimi-k2, Llama4-Scout, Llama4-Maverick, Qwen-Max, Qwen-Turbo, Grok-Code-Fast | 478–515 | +485 to +522 |
| GPT-5 family | GPT-5 (550), GPT-5-Mini (500) | — | +450 / +500 |

Exact per-model counts: `data/processed/machine_temp05_summary.csv` (`need_to_1000`).

## Even-newer models to add (each +500)
Candidate gaps vs current set: Gemini 2.5 Pro/Flash (no Google model present), Claude Haiku 4,
Mistral Large, Qwen3, others. Dawei to confirm the final list; each adds 1,000 @ temp 0.5.

## Parity requirements (must match existing rows)
- **Prompt:** same baseline DAT prompt (`baseline_prompt_1`).
- **Temperature:** baseline midpoint temperature
- **Scoring:** same DAT scorer as Olson et al., 2021 (https://github.com/jayolson/divergent-association-task)
- **Output schema:** model_name, batch, temperature, source_file, dat_score, noun_0..noun_9.

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
- **New collection passes the same literal value 0.5 to every provider** for parity. Do NOT rescale to a
  provider's own max (e.g. OpenAI supports 0–2, but the anchor is the collected value 0.5, not the midpoint).
- **Exception handling:** if a model rejects 0.5 (some newer models only allow temperature = 1, e.g. Kimi
  K2.5/K2.6), the collector falls back to the model's allowed default and records the ACTUAL temperature in
  the row's `temperature` column. Such rows are a documented parity exception, not silently mixed in.
- Every row therefore carries its true temperature; downstream analysis can filter to temperature == 0.5
  for the strict-parity set and treat exceptions separately.
