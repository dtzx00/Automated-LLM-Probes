# Model release dates - web verification (checked 2026-07-18)

**Short answer to "do we have exact year-month-day?":** For the real, historically-released models - yes, verified to the day below. For the future/non-standard names in the dataset - no, they have no verifiable public release date; marked WARN.

## Confidence key
- OK  = verified exact date (web source)
- MON = verified month; day approximate / announce-vs-GA ambiguity
- WARN = no verifiable public release (future-dated vs today 2026-07-18, or non-standard name); date is a placeholder

## OpenAI
| Model | Verified date | Conf | Note / correction |
|---|---|---|---|
| GPT-3.5-Turbo | 2023-03-01 | OK | Correction: dataset had 2022-11. The gpt-3.5-turbo API model shipped Mar 2023 (ChatGPT launched Nov 2022 on GPT-3.5, but the turbo API model is Mar 2023). |
| GPT-4.0-Turbo | 2023-11-06 | OK | DevDay |
| GPT-4o | 2024-05-13 | OK | |
| GPT-4.1 / mini / nano | 2025-04-14 | OK | all three same day |
| o4-mini | 2025-04-16 | OK | API/paid; free tier 04-24 |
| GPT-5 / GPT-5-mini | 2025-08-07 | OK | |
| GPT-5.1 | 2025-11-12 | OK | |
| GPT-5.2 | placeholder | WARN | no public release; placeholder 2025-12 |
| GPT-5.4 | placeholder | WARN | future-dated; placeholder 2026-02 |
| GPT-5.5 | placeholder | WARN | future-dated; placeholder 2026-04 |

## Anthropic
| Model | Verified date | Conf | Note |
|---|---|---|---|
| Claude-3-Opus | 2024-03-04 | OK | Opus+Sonnet GA on announce day |
| Claude-3-Haiku | 2024-03-13 | OK | |
| Claude-3.5-Sonnet | 2024-06-20 | OK | |
| Claude-Sonnet-4 | 2025-05-22 | OK | |
| Claude-Opus-4.1 | 2025-08-05 | OK | |
| Claude-Sonnet-4.5 | 2025-09-29 | OK | |
| Claude-Haiku-4.5 | 2025-10-15 | OK | |
| Claude-Opus-4.5 | 2025-11-24 | OK | dataset had 2025-11, day now known |
| Claude-Opus-4.7 | placeholder | WARN | no public release; placeholder 2026-01 |
| Claude-Sonnet-4.6 | placeholder | WARN | no public release; placeholder 2026-01 |
| Claude-Fable-5 | placeholder | WARN | non-standard name; no release |
| Claude-Sonnet-5 | placeholder | WARN | no public release; placeholder 2026-03 |

## DeepSeek
| Model | Verified date | Conf | Note |
|---|---|---|---|
| DeepSeek-Chat | 2024-05-06 | OK | V2-era chat |
| DeepSeek-R1 | 2025-01-20 | OK | model release (chatbot 01-10) |
| DeepSeek-V3.2 | 2025-12-01 | OK | |
| DeepSeek-V4-Pro | placeholder | WARN | no public release; placeholder 2026-02 |
| DeepSeek-V4-Flash | placeholder | WARN | no public release |
| DeepSeek-V4-Flash-TH | placeholder | WARN | no public release |

## Qwen (Alibaba)
| Model | Verified date | Conf | Note |
|---|---|---|---|
| Qwen3-235B-Instruct | 2025-07-21 | OK | -2507 instruct (base Qwen3 2025-04-28) |
| Qwen-Turbo | 2025-02-01 | MON | Qwen2.5-based; dataset had 2025-09 (wrong) |
| Qwen-Max | ambiguous | MON | Max line muddled; dataset 2025-09 not reliable - which snapshot did you use? |
| Qwen-Plus | ambiguous | MON | same ambiguity as Max |
| Qwen3.7-Max | placeholder | WARN | future-dated |
| Qwen4-Max | placeholder | WARN | future-dated |
| Qwen3.5-Plus | placeholder | WARN | future-dated; mis-tagged provider=hunyuan |

## Meta / Moonshot / Baidu
| Model | Verified date | Conf | Note |
|---|---|---|---|
| Llama-2-70b | 2023-07-18 | OK | |
| Llama4-Scout / Maverick | 2025-04-05 | OK | both same day |
| Moonshot-v1-8k / 128k | approx | MON | Kimi platform Oct 2023; exact v1 API GA day undocumented; dataset 2024-02 approximate |
| Kimi-K2 | 2025-07 | MON | July 2025; exact day not pinned |
| Kimi-K2.5 | placeholder | WARN | no public release |
| Kimi-K2.6 | placeholder | WARN | no public release |
| Ernie-4.0-8k | 2023-10-17 | MON | Baidu World 2023; API-tier day approximate |

## xAI (Grok)
| Model | Verified date | Conf | Note |
|---|---|---|---|
| Grok-Code-Fast | 2025-08-28 | OK | Grok Code Fast 1 |
| Grok-4.3 | placeholder | WARN | no public release (Grok 4 = 2025-07-09; 4.3 not real) |
| Grok-4.5 | placeholder | WARN | no public release |
| Grok-4.20-reason / nonreason | placeholder | WARN | non-standard names; no release |

## MiniMax / Tencent Hunyuan
| Model | Verified date | Conf | Note |
|---|---|---|---|
| MiniMax-M2.5 / M2.7 / M3 | placeholder | WARN | no verifiable release for these version numbers; provider mis-tagged hunyuan |
| Hunyuan-Hy3 | placeholder | WARN | non-standard name; no release |

## Two separate data-quality issues surfaced
1. Provider mislabeling (endpoint vs brand): DeepSeek-R1 / DeepSeek-V3.2 tagged qwen; MiniMax-* / Qwen3.5-Plus / DeepSeek-V4-Flash-TH tagged hunyuan. Endpoint artifacts, not developer brand. Unresolved.
2. Days: exact days exist for all OK rows. No days for MON/WARN rows. Plot uses month only (day = mid-month), so adding days won't move points visibly unless you want day-level precision.

---

# UPDATE 2026-07-18 — provider (developer brand) + intelligence class verified & applied

Three axes now locked in `machine_all_merged_relabeled.csv` (columns: `model_year`, `model_month`, `provider`, `intelligence`). Plot reads these directly (no more name-keyword heuristic).

## Provider corrections (was API endpoint → now developer brand)
- DeepSeek-R1, DeepSeek-V3.2: `qwen` → **deepseek** (routed via qwen endpoint, brand is DeepSeek).
- DeepSeek-V4-Flash-TH: `hunyuan` → **deepseek**.
- MiniMax-M2.5 / M2.7 / M3: `hunyuan` → **minimax** (independent Shanghai co.; Tencent/Alibaba are investors, NOT the developer).
- Qwen3.5-Plus: `hunyuan` → **qwen**.
- Hunyuan-Hy3: `hunyuan` → **tencent** (Hunyuan is Tencent's brand).

## Intelligence class (efficient / all-rounder / reasoning-heavyweight), web-verified
- **Reasoning** (chain-of-thought first): DeepSeek-R1, DeepSeek-V3.2, DeepSeek-V4-Pro, o4-mini, GPT-5, GPT-5.1/5.2/5.4/5.5, Grok-Code-Fast, Grok-4.3/4.5/4.20-reason, MiniMax-M2.5/M2.7/M3, Kimi-K2.6, Claude-Fable-5.
- **Efficient** (mini/nano/haiku/flash/turbo/scout/8k/128k): GPT-4.1-mini/nano, GPT-5-mini, Claude-3-Haiku, Claude-Haiku-4.5, DeepSeek-V4-Flash/-TH, Qwen-Turbo, Llama4-Scout, Moonshot-v1-8k/128k.
- **All-rounder** (flagship general, non-reasoning-first): GPT-3.5/4-Turbo, GPT-4o, GPT-4.1, all Claude Opus/Sonnet (non-Fable), DeepSeek-Chat, Qwen-Max/Plus/3-235B-Instruct/3.7-Max/4-Max/3.5-Plus, Kimi-K2/K2.5, Llama-2-70b/Llama4-Maverick, Ernie-4.0, Hunyuan-Hy3, Grok-4.20-nonreason.

## Judgment calls to confirm
- **GPT-5 as reasoning**: GPT-5 unifies a fast + a reasoning model behind a router. I classed it reasoning (its headline mode). Say if you'd rather call the default GPT-5 all-rounder.
- **Kimi-K2 vs K2.6**: K2/K2.5 = all-rounder, K2.6 = reasoning (thinking variant). Confirm if K2.6 in your runs was the thinking model.
- **Grok-Code-Fast**: xAI calls it a "fast reasoning model" → reasoning. It's also efficiency-oriented; flag if you'd rather it be efficient.
- **Claude-Fable-5 / Opus-4.7 etc.**: future/non-standard names — class assigned by analogy to the tier the name implies; no authoritative source.

---

# UPDATE 2 (2026-07-18) — 4-class intelligence: added HYBRID

Per Dawei: some models combine all-rounder + reasoning (single model, fast<->thinking toggle/router). Added a 4th class **hybrid**. Re-verified every model against the web.

## Definitions (web-verified)
- **hybrid** — one model that switches between a fast/general mode and a thinking mode via router or toggle. Evidence: GPT-5 = real-time router (fast Main <-> GPT-5 Thinking); Claude 3.7+ / Sonnet-4.5 / Opus-4.5 = extended-thinking toggle (Anthropic's "first hybrid reasoning model" = 3.7); Qwen3 = /think + /no_think soft switch; DeepSeek V3.1+ = hybrid chat-template toggle; Grok 4.x = reasoning-first with modes.
- **reasoning** — always-on chain-of-thought, no fast mode: DeepSeek-R1, o4-mini, Grok-Code-Fast, Grok-4.20-reason, MiniMax-M2 family (interleaved thinking is core), Kimi-K2.6 (K2-Thinking), DeepSeek-V4-Pro.
- **all-rounder** — capable general model, NO thinking mode: GPT-3.5/4-Turbo, GPT-4o, GPT-4.1, Claude 3/3.5, DeepSeek-Chat (V2), Qwen3-235B-Instruct (non-thinking), Kimi-K2/K2.5 (base), Llama-2/Llama4-Maverick, Ernie-4.0, Grok-4.20-nonreason.
- **efficient** — small/fast variants: *-mini, *-nano, *-haiku, *-flash, *-turbo, Llama4-Scout, Moonshot-v1-8k/128k.

## Final 4-class assignment
- **hybrid (13):** GPT-5, GPT-5.1/5.2/5.4/5.5, Claude-Sonnet-4, Claude-Opus-4.1, Claude-Sonnet-4.5, Claude-Opus-4.5/4.7, Claude-Sonnet-4.6, Claude-Fable-5, Claude-Sonnet-5, DeepSeek-V3.2, Qwen-Max, Qwen-Plus, Qwen3.5-Plus, Qwen3.7-Max, Qwen4-Max, Grok-4.3, Grok-4.5, Hunyuan-Hy3.
- **reasoning (8):** o4-mini, DeepSeek-R1, DeepSeek-V4-Pro, Grok-Code-Fast, Grok-4.20-reason, MiniMax-M2.5/M2.7/M3, Kimi-K2.6.
- **all-rounder:** GPT-3.5-Turbo, GPT-4.0-Turbo, GPT-4o, GPT-4.1, Claude-3-Opus, Claude-3.5-Sonnet, DeepSeek-Chat, Qwen3-235B-Instruct, Kimi-K2, Kimi-K2.5, Llama-2-70b, Llama4-Maverick, Ernie-4.0-8k, Grok-4.20-nonreason.
- **efficient:** GPT-4.1-mini/nano, GPT-5-mini, Claude-3-Haiku, Claude-Haiku-4.5, DeepSeek-V4-Flash/-TH, Qwen-Turbo, Llama4-Scout, Moonshot-v1-8k/128k.

## Calls worth a second look
- **Qwen-Max / Qwen-Plus classed hybrid** — the current Qwen "Max/Plus" line is Qwen3-based (think/no_think). If your runs called an OLDER Qwen2.5-based Max/Plus (no thinking mode), they'd be all-rounder. Confirm which snapshot.
- **DeepSeek-Chat = V2 all-rounder** (pre-hybrid). Only V3.1+ became hybrid; you have V3.2 (hybrid) and V4-Pro (reasoning).
- **Grok-4.20-reason vs -nonreason** kept as reasoning vs all-rounder respectively (explicit split in the name).
- Future/non-standard names (GPT-5.2+, Claude-Fable-5, DeepSeek-V4-*, Grok-4.x, Kimi-K2.6, MiniMax-M*, Hunyuan-Hy3): class assigned by analogy to the product line; no authoritative source since they aren't publicly released as of 2026-07-18.

---

# UPDATE 3 (2026-07-18) — day-level granularity + honesty flags

Plot now uses **day** granularity: fractional year = year + (day-of-year − 0.5)/365. Columns added: `model_day`, `date_precision` (exact | approx).

## Marker edge convention
- **White edge = exact verified release date** (day known from web).
- **Dark edge = approximate** — month known but day not (Moonshot-v1, Ernie), OR the model is a placeholder/undated future name (day assigned deterministically by name-hash, spread 3–25, purely to avoid stacking; NOT a real date).

## On the "too many same-day releases" concern
Real same-day releases remain overlapping because they ARE the same day:
- GPT-4.1 + GPT-4.1-mini + GPT-4.1-nano — all 2025-04-14.
- Llama4-Scout + Llama4-Maverick — both 2025-04-05.
- GPT-5 + GPT-5-mini — both 2025-08-07.
These are genuine simultaneous releases, not artifacts. Everything else is now separated by its true day.

## Axis
- x-min = 1 month before earliest model. Earliest is now GPT-3.5-Turbo **2023-03-01** (was mis-dated 2022-11), so axis starts ~2023-02.
- x-max = **1 month after latest model** (GPT-5.5 2026-04 → axis ends ~2026-05). Previously the axis stopped at the latest model's date with no margin.

## Still approximate (no exact day available)
Moonshot-v1-8k/128k (month only), Ernie-4.0-8k (Baidu World week), Kimi-K2 (2025-07-11 used), and ALL future/non-standard names. If you have exact dates for any, send them and I'll flip precision to exact.

---

# UPDATE 4 (2026-07-18) — removed black borders, redrawn lineages

- **Black borders removed.** They were my exact-vs-approx-date flag; read as noise. All markers now have a uniform white edge. Date precision stays documented here (exact vs approx) rather than shown on the marker.
- **Lineage lines redrawn.** Each provider now has ONE flagship evolutionary chain, date-ordered, drawn as directional arrows (arrowhead = newer model). Efficient/mini spurs are omitted from the line so the main trajectory reads cleanly. Chains:
  - openai: 3.5-Turbo -> 4-Turbo -> 4o -> 4.1 -> GPT-5 -> 5.1 -> 5.2 -> 5.4 -> 5.5
  - anthropic: Claude-3-Opus -> 3.5-Sonnet -> Sonnet-4 -> Opus-4.1 -> Sonnet-4.5 -> Opus-4.5 -> Opus-4.7 -> Sonnet-4.6 -> Fable-5 -> Sonnet-5
  - deepseek: Chat -> R1 -> V3.2 -> V4-Pro
  - qwen: Turbo -> 3-235B -> Max -> 3.7-Max -> 3.5-Plus -> 4-Max
  - moonshot: v1 -> Kimi-K2 -> K2.5 -> K2.6
  - meta: Llama-2-70b -> Llama4-Maverick
  - xai: Grok-Code-Fast -> 4.3 -> 4.20-reason -> 4.5
  - minimax: M2.5 -> M2.7 -> M3
- The big salmon (anthropic) zig-zags are real DAT-score bounce between Claude versions, not drawing errors.
