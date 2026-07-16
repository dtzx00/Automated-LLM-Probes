# Machine Data — Full Merge Sample Size by Model

Merged all machine data: **legacy (old 2024 + new 2025 + temp-sweep experiments, temp≈0.5)** + **new temp-locked batches (n50→n500)**.

- **Distinct models:** 57
- **Total responses:** 90,293  (new temp-locked 19,562 + legacy 70,731)
- Merged file: `machine_data/processed/machine_all_merged.csv` (schema-unified, `data_generation` column tags each row `new_temp_locked` vs `legacy`).
- **No pooling of temperatures**: legacy is mostly temp≈0.5 + temperature sweeps; new is temp-midpoint-locked. Keep separate for analysis; the merged file preserves the tag so you can filter.

| Model | New (temp-locked) | Legacy | Total |
|---|--:|--:|--:|
| Claude-Opus-4.1 | 20 | 6180 | 6200 |
| Qwen-Max | 20 | 6165 | 6185 |
| Qwen-Turbo | 20 | 6165 | 6185 |
| Claude-Sonnet-4 | 0 | 6180 | 6180 |
| Deepseek-Chat | 0 | 6180 | 6180 |
| Llama4-Scout | 0 | 6180 | 6180 |
| Kimi-k2 | 0 | 6175 | 6175 |
| Llama4-Maverick | 0 | 6155 | 6155 |
| Grok-Code-Fast | 0 | 5751 | 5751 |
| GPT-5 | 504 | 1100 | 1604 |
| DeepSeek-R1 | 20 | 1500 | 1520 |
| GPT-3.5-Turbo | 20 | 1500 | 1520 |
| GPT-4.0-Turbo | 20 | 1500 | 1520 |
| GPT-4o | 20 | 1500 | 1520 |
| Claude-3-Haiku | 0 | 1500 | 1500 |
| Claude-3-Opus | 0 | 1500 | 1500 |
| Claude-3.5-Sonnet | 0 | 1500 | 1500 |
| Ernie-4.0-8k | 0 | 1500 | 1500 |
| Llama-2-70b | 0 | 1500 | 1500 |
| GPT-5-Mini | 0 | 1000 | 1000 |
| DeepSeek-V3.2 | 547 | 0 | 547 |
| Hunyuan-Hy3 | 542 | 0 | 542 |
| Grok-4.5 | 540 | 0 | 540 |
| Claude-Fable-5 | 537 | 0 | 537 |
| DeepSeek-V4-Pro | 536 | 0 | 536 |
| Claude-Sonnet-5 | 533 | 0 | 533 |
| Qwen4-Max | 532 | 0 | 532 |
| Qwen3-235B-Instruct | 530 | 0 | 530 |
| Claude-Opus-4.7 | 520 | 0 | 520 |
| Claude-Sonnet-4.5 | 520 | 0 | 520 |
| GPT-5-mini | 520 | 0 | 520 |
| Grok-4.3 | 520 | 0 | 520 |
| Qwen3.7-Max | 520 | 0 | 520 |
| Kimi-K2.5 | 519 | 0 | 519 |
| Kimi-K2.6 | 502 | 0 | 502 |
| Claude-Haiku-4.5 | 500 | 0 | 500 |
| Claude-Opus-4.5 | 500 | 0 | 500 |
| Claude-Sonnet-4.6 | 500 | 0 | 500 |
| DeepSeek-V4-Flash | 500 | 0 | 500 |
| DeepSeek-V4-Flash-TH | 500 | 0 | 500 |
| GPT-4.1 | 500 | 0 | 500 |
| GPT-4.1-mini | 500 | 0 | 500 |
| GPT-4.1-nano | 500 | 0 | 500 |
| GPT-5.1 | 500 | 0 | 500 |
| GPT-5.2 | 500 | 0 | 500 |
| GPT-5.4 | 500 | 0 | 500 |
| GPT-5.5 | 500 | 0 | 500 |
| Grok-4.20-nonreason | 500 | 0 | 500 |
| Grok-4.20-reason | 500 | 0 | 500 |
| MiniMax-M2.5 | 500 | 0 | 500 |
| MiniMax-M2.7 | 500 | 0 | 500 |
| MiniMax-M3 | 500 | 0 | 500 |
| Moonshot-v1-128k | 500 | 0 | 500 |
| Moonshot-v1-8k | 500 | 0 | 500 |
| Qwen-Plus | 500 | 0 | 500 |
| Qwen3.5-Plus | 500 | 0 | 500 |
| o4-mini | 500 | 0 | 500 |
| **TOTAL** | **19,562** | **70,731** | **90,293** |

## Notes
- Models with counts in **both** columns (e.g. GPT-4o, Qwen-Max, DeepSeek-R1, GPT-5) have legacy volume plus a small new-batch presence (~20-row probes or the current locked run). They are the same model name across generations; the row-level `data_generation` tag disambiguates.
- Excluded from the merge: the legacy aggregate summary file (not row-level) and `pre_lock_nonfinal/` (archived non-finalized preview rows).