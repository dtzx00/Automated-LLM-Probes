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
