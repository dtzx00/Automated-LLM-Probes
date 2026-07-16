# Average DAT Score by Model (Olson GloVe scorer)

Computed on `machine_final_baseline_midpoint.csv` (baseline prompt, midpoint temperature).
DAT = mean pairwise cosine distance among the first 7 in-vocabulary words ×100 (Olson 2021). **All 57 models re-scored with the same scorer** so they are directly comparable.
Rows needing ≥7 in-vocab words; 504 of 31,959 skipped for too few valid words.

| Model | Mean DAT | n scored | source(s) |
|---|--:|--:|---|
| Claude-Opus-4.7 | 85.89 | 520 | 2026_latest |
| Llama4-Maverick | 84.84 | 514 | newer_2025 |
| Claude-Opus-4.1 | 84.76 | 535 | 2026_latest,newer_2025 |
| Claude-Fable-5 | 83.49 | 537 | 2026_latest |
| Llama4-Scout | 81.81 | 515 | newer_2025 |
| GPT-4.0-Turbo | 81.77 | 770 | 2026_latest,NHB_2024 |
| Claude-Sonnet-5 | 81.16 | 533 | 2026_latest |
| Claude-Haiku-4.5 | 80.96 | 500 | 2026_latest |
| Claude-Sonnet-4.5 | 80.92 | 520 | 2026_latest |
| Kimi-k2 | 80.91 | 515 | newer_2025 |
| GPT-5.1 | 80.84 | 500 | 2026_latest |
| Claude-3.5-Sonnet | 80.01 | 750 | NHB_2024 |
| Claude-Sonnet-4.6 | 79.97 | 500 | 2026_latest |
| Claude-Opus-4.5 | 79.69 | 500 | 2026_latest |
| GPT-5.2 | 79.51 | 500 | 2026_latest |
| Kimi-K2.5 | 79.42 | 519 | 2026_latest |
| DeepSeek-V3.2 | 79.40 | 547 | 2026_latest |
| Claude-3-Haiku | 79.06 | 750 | NHB_2024 |
| GPT-5 | 78.84 | 1054 | 2026_latest,newer_2025 |
| GPT-4.1-nano | 78.64 | 496 | 2026_latest |
| Kimi-K2.6 | 78.55 | 502 | 2026_latest |
| GPT-5.5 | 78.12 | 500 | 2026_latest |
| Claude-Sonnet-4 | 77.90 | 515 | newer_2025 |
| Llama-2-70b | 77.89 | 750 | NHB_2024 |
| Qwen-Plus | 77.89 | 500 | 2026_latest |
| MiniMax-M2.7 | 77.86 | 500 | 2026_latest |
| Hunyuan-Hy3 | 77.52 | 542 | 2026_latest |
| Qwen3.7-Max | 77.51 | 520 | 2026_latest |
| DeepSeek-V4-Pro | 77.34 | 536 | 2026_latest |
| GPT-4.1 | 77.20 | 500 | 2026_latest |
| Claude-3-Opus | 76.80 | 750 | NHB_2024 |
| GPT-5.4 | 76.79 | 500 | 2026_latest |
| GPT-4.1-mini | 76.77 | 500 | 2026_latest |
| GPT-3.5-Turbo | 76.73 | 770 | 2026_latest,NHB_2024 |
| Grok-4.3 | 76.55 | 520 | 2026_latest |
| DeepSeek-R1 | 76.49 | 766 | 2026_latest,NHB_2024 |
| Qwen4-Max | 76.45 | 532 | 2026_latest |
| GPT-4o | 76.20 | 770 | 2026_latest,NHB_2024 |
| o4-mini | 76.14 | 500 | 2026_latest |
| Ernie-4.0-8k | 76.12 | 750 | NHB_2024 |
| MiniMax-M3 | 75.95 | 4 | 2026_latest |
| Grok-4.5 | 75.93 | 540 | 2026_latest |
| Grok-4.20-reason | 75.92 | 500 | 2026_latest |
| Deepseek-Chat | 75.89 | 515 | newer_2025 |
| GPT-5-Mini | 75.77 | 500 | newer_2025 |
| GPT-5-mini | 75.71 | 520 | 2026_latest |
| MiniMax-M2.5 | 75.59 | 500 | 2026_latest |
| Qwen-Max | 75.15 | 535 | 2026_latest,newer_2025 |
| Qwen3-235B-Instruct | 75.13 | 530 | 2026_latest |
| Grok-Code-Fast | 74.46 | 478 | newer_2025 |
| Moonshot-v1-128k | 74.45 | 500 | 2026_latest |
| Moonshot-v1-8k | 74.44 | 500 | 2026_latest |
| Grok-4.20-nonreason | 73.98 | 500 | 2026_latest |
| DeepSeek-V4-Flash | 73.95 | 500 | 2026_latest |
| DeepSeek-V4-Flash-TH | 73.59 | 500 | 2026_latest |
| Qwen3.5-Plus | 72.83 | 500 | 2026_latest |
| Qwen-Turbo | 71.31 | 535 | 2026_latest,newer_2025 |

Grid: highest Claude-Opus-4.7 (85.89) → lowest Qwen-Turbo (71.31).