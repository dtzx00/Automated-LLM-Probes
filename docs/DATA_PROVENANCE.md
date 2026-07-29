# Data provenance and known limitations

Covers what is and is not verifiable about the machine and human DAT data. Written 2026-07-28.

## Canonical analysis file

`machine_data/processed/machine_analysis_canonical.csv` — 33,481 scored responses, 59 models. One row per response, carrying both scores plus model metadata and release date. This is the single source for the over-time figures. Build it with `analysis/build_overtime_data.py`.

Both measures are computed on **identical rows**. Earlier versions computed DAT on the baseline-midpoint slice while computing between-unit divergence over the full corpus, which for 20 models pooled up to 12 temperature settings. Those two markers per model were therefore not the same sample. Restricting both to the midpoint condition moved between-unit by at most 0.46 points (Claude-Opus-4.1) and left the 35 single-temperature models unchanged to within 0.003.

## Scoring

- DAT: Olson et al. 2021 procedure. GloVe 840B/300d filtered to the Olson word list. Non-alphabetic characters stripped, duplicates removed, first 7 vocabulary-valid words retained, mean pairwise cosine distance × 100.
- Between-unit divergence, position-aware: each word L2-normalised and compared to a fixed per-rank reference list (`machine_data/between_unit_references/rank1–7_ref.txt`, 2,500 human + 2,500 machine words per rank), mean cosine distance × 100 across the 7 slots.
- Humans and machines are scored with the same scorer and the same 7-valid-word rule. Re-scoring reproduces the previously committed per-row `dat_score` to a mean absolute difference of 0.0005.
- Responses that cannot yield 7 vocabulary-valid words are dropped. Currently 8 rows: DeepSeek-R1 4, GPT-4.1-nano 4.

## Human baseline

One baseline, in `machine_data/human_avg_baselines.json`: DAT 78.45 (n=11,597), between-unit 80.11 (n=11,531), from 12,147 respondents across 5 sources (olson_pnas2021, btb, zunyi, zunyi2024, hsbc2025).

A second, conflicting figure of 78.69 previously circulated. That was the legacy `word_dat_score` column, which used a different vocabulary filter. It has been superseded. Use 78.45 for anything where humans and machines are compared, because only that value is produced by the same scorer as the machine numbers.

Collection-year assignment for the year-wise baseline: olson_pnas2021 → 2022, zunyi and zunyi2024 → 2024, btb and hsbc2025 → 2025. The zunyi and btb assignments are inferred, not documented in the source files, and remain unconfirmed.

## Release dates

`machine_data/model_release_dates.csv` records every model's date, the exact `api_model_id` called, the source, and whether the date is API-verified.

26 of 59 dates are verified against the provider's own API metadata (`created_at` for Anthropic, `created` for OpenAI and xAI) for the exact model ID used. This corrected 16 dates, several materially: Grok-4.5 by 132 days, Grok-4.3 by 126, Claude-Fable-5 by 108, Claude-Opus-4.7 by 100, GPT-4o by 83 (the dataset had used the May 4o launch date while calling the August snapshot).

The remaining 33 dates come from published announcements and cannot be API-verified. Moonshot and Alibaba/Qwen return a listing or last-modified timestamp rather than a release date, so their `created` fields are unusable — do not treat them as release dates. Models absent from current provider listings (Claude 3 family, Grok-Code-Fast, Llama, Ernie, Moonshot v1) are deprecated and retain published dates.

Where only a month is known, the day is hash-spread deterministically within that month; those rows carry `date_precision = approx`.

## Legacy corpus limitations

`machine_data/processed/machine_all_merged.csv` holds the full 90,293-response corpus. 70,731 of those rows (78%) predate the locked collector and carry `parse_status = unknown` with blank `region` and `reasoning` fields. For those rows there is no record of the exact prompt, temperature handling, or parse validation. They are retained for the temperature-sweep analyses but the canonical analysis file draws only on the baseline-midpoint condition.

MiniMax-M3 was previously unusable: a parser fault split the model's chain-of-thought prose on commas into the noun columns, leaving `noun_0 = "<think>"` in all 500 rows and only 4 scoreable. Because stripping non-alphabetic characters turns `<think>` into `think`, which is a valid GloVe entry, the fault survived the vocabulary filter. All 500 responses were recovered from `raw_response_text` after the `</think>` marker. The model's DAT moved from a meaningless 75.95 to 78.48.

## Reasoning traces

Trace capture was added to the collector on 2026-07-27. Everything collected before that discarded reasoning tokens that were nonetheless billed.

No model currently has usable traces. Of the three collected since capture was added:

- Claude-Opus-5 returns a `thinking` block containing only a cryptographic `signature` and an empty text field. Anthropic encrypts the trace; it cannot be read.
- GPT-5.6-Sol produces reasoning tokens but chat/completions does not expose them. Only the Responses API returns a summary, and switching endpoints for a single model would break comparability with the other OpenAI models.
- Kimi-K3 was collected before the Anthropic and OpenAI capture paths were exercised.

Providers that expose verbatim chain-of-thought on OpenAI-compatible endpoints (DeepSeek, Moonshot, Qwen, MiniMax) would need to be re-collected if traces are required as evidence. Capture costs nothing extra — the tokens are billed either way — but the effort is only worthwhile if traces are actually used in the analysis.

## Collection protocol

10 nouns, single words, English, no proper nouns, no technical terms, comma-separated. 500 responses per model, no seed reuse within a model, each model left at its shipped default thinking effort. Temperature requested at the provider midpoint; several models reject it and fall back to 1.0 (Kimi-K3, Claude-Opus-4.7, Claude-Opus-5), which is recorded per row in the raw files.

## Model registry: `machine_data/models.csv` (rebuilt 2026-07-29)

One row per model in the analysis, 59 rows. Invariant: the row set equals the model
set in `analysis/data/permonth_data.json` and `between_data.json`, and `n_analysis`
sums to the row count of `machine_analysis_canonical.csv` (33,481). Assert both when
changing the data.

Why it was rebuilt: the registry had drifted to a collection-era snapshot of 55 rows.
It was missing five models that were being plotted (Claude-Opus-5, Claude-Sonnet-4,
DeepSeek-Chat, GPT-5.6-Sol, Kimi-K3), carried a `Kimi-k2-legacy` row that is not in
the analysis, used a superseded three-way `type` taxonomy (fast / allrounder /
reasoning) rather than the four-class `intelligence` used by the figures, and its
`year` column predated the release-date corrections (GPT-3.5-Turbo was recorded as
2022 against an actual release of 2023-02-28).

Field precedence, so metadata is never silently invented:
1. Majority value across that model's rows in the canonical CSV.
2. Else the value curated in the previous registry.
3. Else derived — region from provider, reasoning from intelligence class.
Any field reaching step 3 is named in the `derived_fields` column. Currently two
models rely on derivation: DeepSeek-Chat and Claude-Sonnet-4, which are absent from
the old registry and have blank region/reasoning in the legacy corpus.

`api_model_id` is blank for eight legacy models (Llama-2-70b, GPT-4.0-Turbo,
Claude-3-Opus, Claude-3-Haiku, DeepSeek-Chat, Llama4-Scout, Llama4-Maverick,
Claude-Sonnet-4). They were collected before the collector recorded the requested id
and it is not recoverable from the data held. Claude-Opus-5, Kimi-K3 and GPT-5.6-Sol
were backfilled from `machine_data/raw_reasoning/`, where requested and returned ids
are both recorded.

Known redundancy: `models.csv` and `model_release_dates.csv` now overlap on date
fields. `model_release_dates.csv` remains the input the build script reads; the
registry is generated to match it. Do not edit date fields in the registry alone.
