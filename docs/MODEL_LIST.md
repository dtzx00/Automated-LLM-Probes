# creativity_networks — model list (59 models)

Canonical source: `machine_data/processed/machine_analysis_canonical.csv` (33,481 responses). Both scores are computed on identical rows per model (midpoint condition), so DAT and between-person are never based on different samples.

Human baselines: DAT **78.45** (n=11,597), between-person **80.11** (n=11,531).

**Shift** = between-person relative to DAT, the direction of the arrow in figure 2. **Precision** *approx* means the release month is sourced but the exact day is not.


| # | Model | Provider | Class | API model id | Release date | Precision | API-verified | n | DAT | Between | Shift |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | GPT-3.5-Turbo | openai | All-rounder | `gpt-3.5-turbo` | 2023-02-28 | exact | yes | 770 | 76.73 | 75.69 | down 1.04 |
| 2 | Llama-2-70b | meta | All-rounder | — | 2023-07-18 | exact | — | 750 | 77.89 | 76.11 | down 1.77 |
| 3 | Ernie-4.0-8k | baidu | All-rounder | `ernie-4.0-8k` | 2023-10-17 | exact | — | 750 | 76.12 | 76.65 | up 0.53 |
| 4 | GPT-4.0-Turbo | openai | All-rounder | — | 2023-11-06 | exact | — | 770 | 81.77 | 79.03 | down 2.74 |
| 5 | Moonshot-v1-8k | moonshot | Efficient | `moonshot-v1-8k` | 2024-02-01 | exact | — | 500 | 74.44 | 75.42 | up 0.98 |
| 6 | Moonshot-v1-128k | moonshot | Efficient | `moonshot-v1-128k` | 2024-02-01 | exact | — | 500 | 74.45 | 75.41 | up 0.96 |
| 7 | Claude-3-Opus | anthropic | All-rounder | — | 2024-03-04 | exact | — | 750 | 76.80 | 76.87 | up 0.08 |
| 8 | Claude-3-Haiku | anthropic | Efficient | — | 2024-03-13 | exact | — | 750 | 79.06 | 77.59 | down 1.47 |
| 9 | DeepSeek-Chat | deepseek | All-rounder | — | 2024-05-06 | exact | — | 515 | 75.89 | 76.26 | up 0.38 |
| 10 | Claude-3.5-Sonnet | anthropic | All-rounder | `claude-3.5-sonnet` | 2024-06-20 | exact | — | 750 | 80.01 | 77.12 | down 2.89 |
| 11 | GPT-4o | openai | All-rounder | `gpt-4o-2024-08-06` | 2024-08-04 | exact | yes | 770 | 76.20 | 75.03 | down 1.17 |
| 12 | DeepSeek-R1 | deepseek | Reasoning | `deepseek-r1` | 2025-01-20 | exact | — | 766 | 76.49 | 76.13 | down 0.36 |
| 13 | Qwen-Turbo | qwen | Efficient | `qwen-turbo` | 2025-02-01 | exact | — | 535 | 71.31 | 74.04 | up 2.72 |
| 14 | Llama4-Scout | meta | Efficient | — | 2025-04-05 | exact | — | 515 | 81.81 | 77.66 | down 4.15 |
| 15 | Llama4-Maverick | meta | All-rounder | — | 2025-04-05 | exact | — | 514 | 84.84 | 80.37 | down 4.47 |
| 16 | o4-mini | openai | Reasoning | `o4-mini-2025-04-16` | 2025-04-08 | exact | yes | 500 | 76.14 | 75.23 | down 0.91 |
| 17 | GPT-4.1 | openai | All-rounder | `gpt-4.1-2025-04-14` | 2025-04-10 | exact | yes | 500 | 77.20 | 75.45 | down 1.75 |
| 18 | GPT-4.1-mini | openai | Efficient | `gpt-4.1-mini-2025-04-14` | 2025-04-10 | exact | yes | 500 | 76.77 | 75.15 | down 1.62 |
| 19 | GPT-4.1-nano | openai | Efficient | `gpt-4.1-nano-2025-04-14` | 2025-04-10 | exact | yes | 496 | 78.65 | 77.31 | down 1.34 |
| 20 | Claude-Sonnet-4 | anthropic | Hybrid | — | 2025-05-22 | exact | — | 515 | 77.90 | 76.28 | down 1.62 |
| 21 | Kimi-K2 | moonshot | All-rounder | `moonshot-v1-32k` | 2025-07-11 | exact | — | 515 | 80.91 | 79.05 | down 1.86 |
| 22 | Qwen3-235B-Instruct | qwen | All-rounder | `qwen3-235b-a22b-instruct-2507` | 2025-07-21 | exact | — | 530 | 75.13 | 75.33 | up 0.20 |
| 23 | GPT-5 | openai | Hybrid | `gpt-5-2025-08-07` | 2025-08-01 | exact | yes | 1,054 | 78.84 | 77.48 | down 1.35 |
| 24 | GPT-5-mini | openai | Efficient | `gpt-5-mini-2025-08-07` | 2025-08-05 | exact | yes | 1,020 | 75.74 | 75.32 | down 0.42 |
| 25 | Claude-Opus-4.1 | anthropic | Hybrid | `claude-opus-4-1-20250805` | 2025-08-05 | exact | yes | 535 | 84.76 | 79.92 | down 4.84 |
| 26 | Grok-Code-Fast | xai | Reasoning | `grok-code-fast` | 2025-08-28 | exact | — | 478 | 74.46 | 74.94 | up 0.48 |
| 27 | Qwen-Max | qwen | Hybrid | `qwen-max` | 2025-09-13 | **approx** | — | 535 | 75.15 | 74.30 | down 0.84 |
| 28 | Qwen-Plus | qwen | Hybrid | `qwen-plus` | 2025-09-22 | **approx** | — | 500 | 77.89 | 76.21 | down 1.67 |
| 29 | Claude-Sonnet-4.5 | anthropic | Hybrid | `claude-sonnet-4-5-20250929` | 2025-09-29 | exact | yes | 520 | 80.92 | 78.26 | down 2.66 |
| 30 | MiniMax-M2.5 | minimax | Reasoning | `minimax-m2.5` | 2025-10-11 | **approx** | — | 500 | 75.59 | 75.78 | up 0.19 |
| 31 | Claude-Haiku-4.5 | anthropic | Efficient | `claude-haiku-4-5-20251001` | 2025-10-15 | exact | yes | 500 | 80.96 | 79.10 | down 1.85 |
| 32 | GPT-5.1 | openai | Hybrid | `gpt-5.1-2025-11-13` | 2025-11-10 | exact | yes | 500 | 80.84 | 78.11 | down 2.72 |
| 33 | Claude-Opus-4.5 | anthropic | Hybrid | `claude-opus-4-5-20251101` | 2025-11-24 | exact | yes | 500 | 79.69 | 78.09 | down 1.60 |
| 34 | DeepSeek-V3.2 | deepseek | Hybrid | `deepseek-v3.2` | 2025-12-01 | exact | — | 547 | 79.40 | 79.22 | down 0.18 |
| 35 | MiniMax-M2.7 | minimax | Reasoning | `minimax-m2.7` | 2025-12-04 | **approx** | — | 500 | 77.86 | 77.55 | down 0.31 |
| 36 | Qwen3.7-Max | qwen | Hybrid | `qwen3.7-max` | 2025-12-04 | **approx** | — | 520 | 77.51 | 78.07 | up 0.56 |
| 37 | GPT-5.2 | openai | Hybrid | `gpt-5.2-2025-12-11` | 2025-12-09 | exact | yes | 500 | 79.51 | 77.24 | down 2.27 |
| 38 | Kimi-K2.5 | moonshot | All-rounder | `kimi-k2.5` | 2025-12-16 | **approx** | — | 519 | 79.43 | 78.69 | down 0.74 |
| 39 | MiniMax-M3 | minimax | Reasoning | `minimax-m3` | 2025-12-16 | **approx** | — | 500 | 78.48 | 77.57 | down 0.91 |
| 40 | Hunyuan-Hy3 | tencent | Hybrid | `hy3` | 2026-01-23 | **approx** | — | 542 | 77.52 | 74.93 | down 2.59 |
| 41 | Qwen3.5-Plus | qwen | Hybrid | `qwen3.5-plus` | 2026-01-23 | **approx** | — | 500 | 72.83 | 75.57 | up 2.74 |
| 42 | DeepSeek-V4-Pro | deepseek | Reasoning | `deepseek-v4-pro` | 2026-02-10 | **approx** | — | 536 | 77.34 | 77.22 | down 0.12 |
| 43 | DeepSeek-V4-Flash-TH | deepseek | Efficient | `deepseek-v4-flash` | 2026-02-10 | **approx** | — | 500 | 73.59 | 75.38 | up 1.79 |
| 44 | Kimi-K2.6 | moonshot | Reasoning | `kimi-k2.6` | 2026-02-11 | **approx** | — | 502 | 78.55 | 78.27 | down 0.29 |
| 45 | Claude-Sonnet-4.6 | anthropic | Hybrid | `claude-sonnet-4-6` | 2026-02-17 | exact | yes | 500 | 79.97 | 79.82 | down 0.15 |
| 46 | DeepSeek-V4-Flash | deepseek | Efficient | `deepseek-v4-flash` | 2026-02-18 | **approx** | — | 500 | 73.95 | 75.59 | up 1.64 |
| 47 | GPT-5.4 | openai | Hybrid | `gpt-5.4-2026-03-05` | 2026-03-04 | exact | yes | 500 | 76.79 | 76.67 | down 0.12 |
| 48 | Grok-4.20-nonreason | xai | All-rounder | `grok-4.20-0309-non-reasoning` | 2026-03-09 | exact | yes | 500 | 73.98 | 75.92 | up 1.94 |
| 49 | Grok-4.20-reason | xai | Reasoning | `grok-4.20-0309-reasoning` | 2026-03-09 | exact | yes | 500 | 75.92 | 76.35 | up 0.43 |
| 50 | Qwen4-Max | qwen | Hybrid | `qwen3-max-2026-01-23` | 2026-03-23 | **approx** | — | 532 | 76.45 | 75.72 | down 0.73 |
| 51 | Claude-Opus-4.7 | anthropic | Hybrid | `claude-opus-4-7` | 2026-04-14 | exact | yes | 520 | 85.89 | 80.35 | down 5.54 |
| 52 | Grok-4.3 | xai | Hybrid | `grok-4.3` | 2026-04-17 | exact | yes | 520 | 76.55 | 76.65 | up 0.10 |
| 53 | GPT-5.5 | openai | Hybrid | `gpt-5.5-2026-04-23` | 2026-04-22 | exact | yes | 500 | 78.12 | 76.41 | down 1.71 |
| 54 | Claude-Fable-5 | anthropic | Hybrid | `claude-fable-5` | 2026-06-07 | exact | yes | 537 | 83.49 | 79.49 | down 4.00 |
| 55 | GPT-5.6-Sol | openai | Hybrid | `gpt-5.6-sol` | 2026-06-23 | exact | yes | 514 | 80.42 | 78.04 | down 2.37 |
| 56 | Claude-Sonnet-5 | anthropic | Hybrid | `claude-sonnet-5` | 2026-06-29 | exact | yes | 533 | 81.16 | 79.76 | down 1.41 |
| 57 | Grok-4.5 | xai | Hybrid | `grok-4.5` | 2026-06-29 | exact | yes | 540 | 75.93 | 75.54 | down 0.39 |
| 58 | Kimi-K3 | moonshot | Reasoning | `kimi-k3` | 2026-07-16 | exact | — | 508 | 77.56 | 77.10 | down 0.45 |
| 59 | Claude-Opus-5 | anthropic | Hybrid | `claude-opus-5` | 2026-07-24 | exact | yes | 508 | 84.30 | 81.44 | down 2.86 |

## Ranked by DAT (within-person)

| Rank | Model | DAT | vs human |
|---|---|---|---|
| 1 | Claude-Opus-4.7 | 85.89 | above 7.44 |
| 2 | Llama4-Maverick | 84.84 | above 6.38 |
| 3 | Claude-Opus-4.1 | 84.76 | above 6.31 |
| 4 | Claude-Opus-5 | 84.30 | above 5.85 |
| 5 | Claude-Fable-5 | 83.49 | above 5.03 |
| 6 | Llama4-Scout | 81.81 | above 3.36 |
| 7 | GPT-4.0-Turbo | 81.77 | above 3.31 |
| 8 | Claude-Sonnet-5 | 81.16 | above 2.71 |
| 9 | Claude-Haiku-4.5 | 80.96 | above 2.50 |
| 10 | Claude-Sonnet-4.5 | 80.92 | above 2.47 |
| 11 | Kimi-K2 | 80.91 | above 2.46 |
| 12 | GPT-5.1 | 80.84 | above 2.38 |
| 13 | GPT-5.6-Sol | 80.42 | above 1.96 |
| 14 | Claude-3.5-Sonnet | 80.01 | above 1.56 |
| 15 | Claude-Sonnet-4.6 | 79.97 | above 1.51 |
| 16 | Claude-Opus-4.5 | 79.69 | above 1.23 |
| 17 | GPT-5.2 | 79.51 | above 1.06 |
| 18 | Kimi-K2.5 | 79.43 | above 0.98 |
| 19 | DeepSeek-V3.2 | 79.40 | above 0.95 |
| 20 | Claude-3-Haiku | 79.06 | above 0.61 |
| 21 | GPT-5 | 78.84 | above 0.38 |
| 22 | GPT-4.1-nano | 78.65 | above 0.19 |
| 23 | Kimi-K2.6 | 78.55 | above 0.10 |
| 24 | MiniMax-M3 | 78.48 | above 0.03 |
| 25 | GPT-5.5 | 78.12 | below 0.33 |
| 26 | Claude-Sonnet-4 | 77.90 | below 0.55 |
| 27 | Llama-2-70b | 77.89 | below 0.57 |
| 28 | Qwen-Plus | 77.89 | below 0.57 |
| 29 | MiniMax-M2.7 | 77.86 | below 0.60 |
| 30 | Kimi-K3 | 77.56 | below 0.90 |
| 31 | Hunyuan-Hy3 | 77.52 | below 0.93 |
| 32 | Qwen3.7-Max | 77.51 | below 0.95 |
| 33 | DeepSeek-V4-Pro | 77.34 | below 1.11 |
| 34 | GPT-4.1 | 77.20 | below 1.25 |
| 35 | Claude-3-Opus | 76.80 | below 1.66 |
| 36 | GPT-5.4 | 76.79 | below 1.66 |
| 37 | GPT-4.1-mini | 76.77 | below 1.69 |
| 38 | GPT-3.5-Turbo | 76.73 | below 1.72 |
| 39 | Grok-4.3 | 76.55 | below 1.90 |
| 40 | DeepSeek-R1 | 76.49 | below 1.96 |
| 41 | Qwen4-Max | 76.45 | below 2.01 |
| 42 | GPT-4o | 76.20 | below 2.26 |
| 43 | o4-mini | 76.14 | below 2.32 |
| 44 | Ernie-4.0-8k | 76.12 | below 2.33 |
| 45 | Grok-4.5 | 75.93 | below 2.52 |
| 46 | Grok-4.20-reason | 75.92 | below 2.54 |
| 47 | DeepSeek-Chat | 75.89 | below 2.57 |
| 48 | GPT-5-mini | 75.74 | below 2.71 |
| 49 | MiniMax-M2.5 | 75.59 | below 2.87 |
| 50 | Qwen-Max | 75.15 | below 3.31 |
| 51 | Qwen3-235B-Instruct | 75.13 | below 3.32 |
| 52 | Grok-Code-Fast | 74.46 | below 3.99 |
| 53 | Moonshot-v1-128k | 74.45 | below 4.00 |
| 54 | Moonshot-v1-8k | 74.44 | below 4.01 |
| 55 | Grok-4.20-nonreason | 73.98 | below 4.47 |
| 56 | DeepSeek-V4-Flash | 73.95 | below 4.50 |
| 57 | DeepSeek-V4-Flash-TH | 73.59 | below 4.86 |
| 58 | Qwen3.5-Plus | 72.83 | below 5.62 |
| 59 | Qwen-Turbo | 71.31 | below 7.14 |

## Ranked by between-person (uniqueness)

| Rank | Model | Between | vs human |
|---|---|---|---|
| 1 | Claude-Opus-5 | 81.44 | above 1.33 |
| 2 | Llama4-Maverick | 80.37 | above 0.26 |
| 3 | Claude-Opus-4.7 | 80.35 | above 0.24 |
| 4 | Claude-Opus-4.1 | 79.92 | below 0.19 |
| 5 | Claude-Sonnet-4.6 | 79.82 | below 0.29 |
| 6 | Claude-Sonnet-5 | 79.76 | below 0.35 |
| 7 | Claude-Fable-5 | 79.49 | below 0.62 |
| 8 | DeepSeek-V3.2 | 79.22 | below 0.89 |
| 9 | Claude-Haiku-4.5 | 79.10 | below 1.00 |
| 10 | Kimi-K2 | 79.05 | below 1.05 |
| 11 | GPT-4.0-Turbo | 79.03 | below 1.08 |
| 12 | Kimi-K2.5 | 78.69 | below 1.42 |
| 13 | Kimi-K2.6 | 78.27 | below 1.84 |
| 14 | Claude-Sonnet-4.5 | 78.26 | below 1.85 |
| 15 | GPT-5.1 | 78.11 | below 2.00 |
| 16 | Claude-Opus-4.5 | 78.09 | below 2.02 |
| 17 | Qwen3.7-Max | 78.07 | below 2.04 |
| 18 | GPT-5.6-Sol | 78.04 | below 2.06 |
| 19 | Llama4-Scout | 77.66 | below 2.45 |
| 20 | Claude-3-Haiku | 77.59 | below 2.52 |
| 21 | MiniMax-M3 | 77.57 | below 2.54 |
| 22 | MiniMax-M2.7 | 77.55 | below 2.56 |
| 23 | GPT-5 | 77.48 | below 2.63 |
| 24 | GPT-4.1-nano | 77.31 | below 2.80 |
| 25 | GPT-5.2 | 77.24 | below 2.87 |
| 26 | DeepSeek-V4-Pro | 77.22 | below 2.89 |
| 27 | Claude-3.5-Sonnet | 77.12 | below 2.99 |
| 28 | Kimi-K3 | 77.10 | below 3.01 |
| 29 | Claude-3-Opus | 76.87 | below 3.23 |
| 30 | GPT-5.4 | 76.67 | below 3.43 |
| 31 | Ernie-4.0-8k | 76.65 | below 3.46 |
| 32 | Grok-4.3 | 76.65 | below 3.46 |
| 33 | GPT-5.5 | 76.41 | below 3.70 |
| 34 | Grok-4.20-reason | 76.35 | below 3.76 |
| 35 | Claude-Sonnet-4 | 76.28 | below 3.83 |
| 36 | DeepSeek-Chat | 76.26 | below 3.85 |
| 37 | Qwen-Plus | 76.21 | below 3.90 |
| 38 | DeepSeek-R1 | 76.13 | below 3.98 |
| 39 | Llama-2-70b | 76.11 | below 3.99 |
| 40 | Grok-4.20-nonreason | 75.92 | below 4.19 |
| 41 | MiniMax-M2.5 | 75.78 | below 4.33 |
| 42 | Qwen4-Max | 75.72 | below 4.39 |
| 43 | GPT-3.5-Turbo | 75.69 | below 4.42 |
| 44 | DeepSeek-V4-Flash | 75.59 | below 4.52 |
| 45 | Qwen3.5-Plus | 75.57 | below 4.53 |
| 46 | Grok-4.5 | 75.54 | below 4.57 |
| 47 | GPT-4.1 | 75.45 | below 4.66 |
| 48 | Moonshot-v1-8k | 75.42 | below 4.68 |
| 49 | Moonshot-v1-128k | 75.41 | below 4.70 |
| 50 | DeepSeek-V4-Flash-TH | 75.38 | below 4.73 |
| 51 | Qwen3-235B-Instruct | 75.33 | below 4.78 |
| 52 | GPT-5-mini | 75.32 | below 4.79 |
| 53 | o4-mini | 75.23 | below 4.88 |
| 54 | GPT-4.1-mini | 75.15 | below 4.96 |
| 55 | GPT-4o | 75.03 | below 5.08 |
| 56 | Grok-Code-Fast | 74.94 | below 5.17 |
| 57 | Hunyuan-Hy3 | 74.93 | below 5.18 |
| 58 | Qwen-Max | 74.30 | below 5.81 |
| 59 | Qwen-Turbo | 74.04 | below 6.07 |

## By provider

| Provider | Models | Mean DAT | Mean between | Dates API-verified |
|---|---|---|---|---|
| meta | 3 | 81.51 | 78.05 | 0 of 3 |
| anthropic | 13 | 81.15 | 78.78 | 9 of 13 |
| openai | 14 | 78.12 | 76.58 | 13 of 14 |
| moonshot | 6 | 77.56 | 77.32 | 0 of 6 |
| tencent | 1 | 77.52 | 74.93 | 0 of 1 |
| minimax | 3 | 77.31 | 76.97 | 0 of 3 |
| baidu | 1 | 76.12 | 76.65 | 0 of 1 |
| deepseek | 6 | 76.11 | 76.63 | 0 of 6 |
| xai | 5 | 75.37 | 75.88 | 4 of 5 |
| qwen | 7 | 75.18 | 75.61 | 0 of 7 |

## Date quality

- **Exact dates:** 45 of 59. **Approximate (month only):** 14 of 59.
- **API-verified against the exact model id we called:** 26 of 59. Only OpenAI, Anthropic and xAI return a real creation timestamp. Moonshot and Qwen/DashScope return a listing timestamp, which is not a release date and is not used.
- **All 13 Claude and all 13 GPT models have exact dates** (9 and 12 API-verified), so both version-evolution lines in the figures rest entirely on exact dates.
- **Missing `api_model_id`:** 8 legacy models — Llama-2-70b, GPT-4.0-Turbo, Claude-3-Opus, Claude-3-Haiku, DeepSeek-Chat, Llama4-Scout, Llama4-Maverick, Claude-Sonnet-4. Collected before the locked collector recorded the requested id; not recoverable from the data we hold.

### The 14 approximate dates

| Model | Provider | Date used |
|---|---|---|
| Qwen-Max | qwen | 2025-09-13 |
| Qwen-Plus | qwen | 2025-09-22 |
| MiniMax-M2.5 | minimax | 2025-10-11 |
| MiniMax-M2.7 | minimax | 2025-12-04 |
| Qwen3.7-Max | qwen | 2025-12-04 |
| Kimi-K2.5 | moonshot | 2025-12-16 |
| MiniMax-M3 | minimax | 2025-12-16 |
| Hunyuan-Hy3 | tencent | 2026-01-23 |
| Qwen3.5-Plus | qwen | 2026-01-23 |
| DeepSeek-V4-Pro | deepseek | 2026-02-10 |
| DeepSeek-V4-Flash-TH | deepseek | 2026-02-10 |
| Kimi-K2.6 | moonshot | 2026-02-11 |
| DeepSeek-V4-Flash | deepseek | 2026-02-18 |
| Qwen4-Max | qwen | 2026-03-23 |

### Dates shared by more than one model

| Date | Models | Precision | Is the same-day launch real? |
|---|---|---|---|
| 2024-02-01 | Moonshot-v1-8k, Moonshot-v1-128k | exact | yes, genuine same-day launch |
| 2025-04-05 | Llama4-Scout, Llama4-Maverick | exact | yes, genuine same-day launch |
| 2025-04-10 | GPT-4.1, GPT-4.1-mini, GPT-4.1-nano | exact | yes, genuine same-day launch |
| 2025-08-05 | GPT-5-mini, Claude-Opus-4.1 | exact | yes, genuine same-day launch |
| 2025-12-04 | MiniMax-M2.7, Qwen3.7-Max | approx | unknown, both dates are month-only |
| 2025-12-16 | Kimi-K2.5, MiniMax-M3 | approx | unknown, both dates are month-only |
| 2026-01-23 | Hunyuan-Hy3, Qwen3.5-Plus | approx | unknown, both dates are month-only |
| 2026-02-10 | DeepSeek-V4-Pro, DeepSeek-V4-Flash-TH | approx | unknown, both dates are month-only |
| 2026-03-09 | Grok-4.20-nonreason, Grok-4.20-reason | exact | yes, genuine same-day launch |
| 2026-06-29 | Claude-Sonnet-5, Grok-4.5 | exact | yes, genuine same-day launch |

### Markers that overlap in the figures

| Pair | DAT gap | Between gap | Effect |
|---|---|---|---|
| Moonshot-v1-8k / Moonshot-v1-128k | 0.01 | 0.01 | one marker fully hides the other in both figures |
| GPT-4.1 / GPT-4.1-mini | 0.43 | 0.30 | markers touch, both readable |
| MiniMax-M2.7 / Qwen3.7-Max | 0.35 | 0.52 | markers touch, different colours so readable |
| Grok-4.20-nonreason / Grok-4.20-reason | 1.94 | 0.43 | clear in DAT, touching in between |
