# Final Machine CSV — Baseline Prompt, Midpoint Temperature

File: `machine_data/processed/machine_final_baseline_midpoint.csv`

- **31,959 rows**, **57 models**, index unique across all rows (0 collisions).
- **Filter:** midpoint temperature + `baseline_prompt_1` only. No temperature sweeps, no alt prompts.
- **index** = native unique ID: `.pickle` ID (NHB_2024 / newer_2025) or `api_request_id`/`response_id` (2026_latest, hash fallback).
- **collected_at** = source timestamp (`start_time`→ISO for NHB_2024; `request_timestamp_utc` for 2026_latest; blank for newer_2025 which has no timestamp).
- **temperature** = `midpoint` on every row. **dat_score** left blank.
- Columns: `index, provider, model, data_source, model_year, collected_at, temperature, word_1…word_10, dat_score`.

| data_source | rows | index source | collected_at |
|---|--:|---|---|
| NHB_2024 | 6,750 | .pickle ID | start_time→ISO |
| newer_2025 | 5,647 | .pickle ID | (none in source) |
| 2026_latest | 19,562 | api_request_id/response_id | request_timestamp_utc |

## Sample size by model

| Model | NHB_2024 | newer_2025 | 2026_latest | Total |
|---|--:|--:|--:|--:|
| GPT-5 | 0 | 550 | 504 | 1054 |
| DeepSeek-R1 | 750 | 0 | 20 | 770 |
| GPT-3.5-Turbo | 750 | 0 | 20 | 770 |
| GPT-4.0-Turbo | 750 | 0 | 20 | 770 |
| GPT-4o | 750 | 0 | 20 | 770 |
| Claude-3-Haiku | 750 | 0 | 0 | 750 |
| Claude-3-Opus | 750 | 0 | 0 | 750 |
| Claude-3.5-Sonnet | 750 | 0 | 0 | 750 |
| Ernie-4.0-8k | 750 | 0 | 0 | 750 |
| Llama-2-70b | 750 | 0 | 0 | 750 |
| DeepSeek-V3.2 | 0 | 0 | 547 | 547 |
| Hunyuan-Hy3 | 0 | 0 | 542 | 542 |
| Grok-4.5 | 0 | 0 | 540 | 540 |
| Claude-Fable-5 | 0 | 0 | 537 | 537 |
| DeepSeek-V4-Pro | 0 | 0 | 536 | 536 |
| Claude-Opus-4.1 | 0 | 515 | 20 | 535 |
| Qwen-Max | 0 | 515 | 20 | 535 |
| Qwen-Turbo | 0 | 515 | 20 | 535 |
| Claude-Sonnet-5 | 0 | 0 | 533 | 533 |
| Qwen4-Max | 0 | 0 | 532 | 532 |
| Qwen3-235B-Instruct | 0 | 0 | 530 | 530 |
| Claude-Opus-4.7 | 0 | 0 | 520 | 520 |
| Claude-Sonnet-4.5 | 0 | 0 | 520 | 520 |
| GPT-5-mini | 0 | 0 | 520 | 520 |
| Grok-4.3 | 0 | 0 | 520 | 520 |
| Qwen3.7-Max | 0 | 0 | 520 | 520 |
| Kimi-K2.5 | 0 | 0 | 519 | 519 |
| Claude-Sonnet-4 | 0 | 515 | 0 | 515 |
| Deepseek-Chat | 0 | 515 | 0 | 515 |
| Kimi-k2 | 0 | 515 | 0 | 515 |
| Llama4-Scout | 0 | 515 | 0 | 515 |
| Llama4-Maverick | 0 | 514 | 0 | 514 |
| Kimi-K2.6 | 0 | 0 | 502 | 502 |
| Claude-Haiku-4.5 | 0 | 0 | 500 | 500 |
| Claude-Opus-4.5 | 0 | 0 | 500 | 500 |
| Claude-Sonnet-4.6 | 0 | 0 | 500 | 500 |
| DeepSeek-V4-Flash | 0 | 0 | 500 | 500 |
| DeepSeek-V4-Flash-TH | 0 | 0 | 500 | 500 |
| GPT-4.1 | 0 | 0 | 500 | 500 |
| GPT-4.1-mini | 0 | 0 | 500 | 500 |
| GPT-4.1-nano | 0 | 0 | 500 | 500 |
| GPT-5-Mini | 0 | 500 | 0 | 500 |
| GPT-5.1 | 0 | 0 | 500 | 500 |
| GPT-5.2 | 0 | 0 | 500 | 500 |
| GPT-5.4 | 0 | 0 | 500 | 500 |
| GPT-5.5 | 0 | 0 | 500 | 500 |
| Grok-4.20-nonreason | 0 | 0 | 500 | 500 |
| Grok-4.20-reason | 0 | 0 | 500 | 500 |
| MiniMax-M2.5 | 0 | 0 | 500 | 500 |
| MiniMax-M2.7 | 0 | 0 | 500 | 500 |
| MiniMax-M3 | 0 | 0 | 500 | 500 |
| Moonshot-v1-128k | 0 | 0 | 500 | 500 |
| Moonshot-v1-8k | 0 | 0 | 500 | 500 |
| Qwen-Plus | 0 | 0 | 500 | 500 |
| Qwen3.5-Plus | 0 | 0 | 500 | 500 |
| o4-mini | 0 | 0 | 500 | 500 |
| Grok-Code-Fast | 0 | 478 | 0 | 478 |
| **TOTAL** | **6,750** | **5,647** | **19,562** | **31,959** |