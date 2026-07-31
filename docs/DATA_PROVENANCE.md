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

One baseline, in `machine_data/human_avg_baselines.json`: DAT 78.42 (n=11,529), between-unit 80.11 (n=11,531), from 12,147 respondents across 5 sources (olson_pnas2021, btb, zunyi, zunyi2024, hsbc2025).

A second, conflicting figure of 78.69 previously circulated. That was the legacy `word_dat_score` column, which used a different vocabulary filter. It has been superseded. Use 78.45 for anything where humans and machines are compared, because only that value is produced by the same scorer as the machine numbers.

Collection-year assignment for the year-wise baseline: olson_pnas2021 → 2022, zunyi and zunyi2024 → 2024, btb and hsbc2025 → 2025. The zunyi and btb assignments were inferred rather than read from the source files. **Reviewed and accepted as the project convention on 2026-07-29; treat them as settled, not as an open question.** They set only the x-position of the year-wise human baseline markers and enter no score: the headline human baselines (DAT 78.42, between-person 80.11; see the 2026-07-31 entry) are pooled across all sources and are unaffected by year assignment.

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

## Single model registry (2026-07-29)

`machine_data/models.csv` is now the only source of model metadata and release dates,
and `analysis/build_overtime_data.py` reads it directly. Previously dates lived in three
places: a hardcoded DATE_FIX dict inside the build script, the model_year/model_month/
model_day columns of the master CSV, and model_release_dates.csv — which was never read
by anything and served only as documentation. That file has been deleted.

### 13 release dates corrected against primary sources
Re-checking the 14 dates previously marked approximate showed they were not merely
day-imprecise: most were wrong by months, nearly all too early.

| Model | Was | Now | Shift | Evidence |
|---|---|---|---|---|
| MiniMax-M3 | 2025-12-16 | 2026-06-01 | +167d | MiniMax platform release notes |
| Hunyuan-Hy3 | 2026-01-23 | 2026-07-06 | +164d | Tencent GA announcement (preview was 2026-04-23) |
| Qwen3.7-Max | 2025-12-04 | 2026-05-17 | +164d | earliest pinned DashScope snapshot |
| MiniMax-M2.5 | 2025-10-11 | 2026-02-12 | +124d | MiniMax blog |
| MiniMax-M2.7 | 2025-12-04 | 2026-03-18 | +104d | MiniMax news + release notes |
| DeepSeek-V4-Pro | 2026-02-10 | 2026-04-24 | +73d | DeepSeek API changelog |
| DeepSeek-V4-Flash-TH | 2026-02-10 | 2026-04-24 | +73d | DeepSeek API changelog |
| Qwen-Plus | 2025-09-22 | 2025-12-01 | +70d | latest pinned snapshot at collection |
| Kimi-K2.6 | 2026-02-11 | 2026-04-21 | +69d | Moonshot forum announcement |
| DeepSeek-V4-Flash | 2026-02-18 | 2026-04-24 | +65d | DeepSeek API changelog |
| Kimi-K2.5 | 2025-12-16 | 2026-01-27 | +42d | ZDNET + Baidu Baike |
| Qwen3.5-Plus | 2026-01-23 | 2026-02-15 | +23d | earliest pinned DashScope snapshot |
| Qwen4-Max | 2026-03-23 | 2026-01-23 | −59d | date encoded in the api id actually called |

Scores are unaffected: re-running the build reproduces every per-model DAT and
between-person value bit-identically (max difference 0.00e+00). Only x-positions move.

### Two provider APIs re-tested and still unusable for dates
DashScope (Qwen) returns a listing timestamp — `qwen-max` reported the date of the query
itself. Moonshot returns the query date for all twelve models. Neither is a release date.
However DashScope exposes **pinned dated snapshot ids**, and the earliest snapshot in a
family is solid release evidence; that is how the two Qwen dates were fixed.

### Rolling aliases: three models cannot be dated
Qwen-Max, Qwen-Plus and Qwen-Turbo were collected through bare aliases whose target
changes silently, so no release date describes what actually answered. They are marked
`alias_unresolved` rather than given false precision. 32 of 59 models were called by
alias; for OpenAI, Anthropic and xAI the provider API still dates the alias, so only
these three are unresolved.

### Two flagged identity mismatches — unresolved, need a decision
- **Qwen4-Max** was collected via `qwen3-max-2026-01-23`, a Qwen3-Max snapshot. The name
  says Qwen4; the endpoint says Qwen3. The date now follows the endpoint.
- **Kimi-K2** was collected via `moonshot-v1-32k`, not a `kimi-k2` endpoint. Its label and
  its 2025-07-11 date both describe Kimi K2, which is probably not what answered.
Both are recorded in the `identity_flag` column. Neither name has been changed, because
renaming alters what the datapoint means.

### Latent double-count bug fixed
The build appended Kimi-K3, Claude-Opus-5 and GPT-5.6-Sol from `raw_reasoning/` while a
later commit had also merged them into the midpoint file, so a fresh run counted every
response twice (n 508 to 1016). Means were unaffected because the duplicates are
identical, which is why it went unnoticed. The build now skips the raw_reasoning append
when the midpoint file already carries the model. Total scored responses: 33,481.

### Reasoning flag
`Grok-Code-Fast` was recorded as reasoning=No while classified in the always-on CoT
`reasoning` intelligence class. Set to Yes for consistency with its class.

## GPT-4.0-Turbo date corrected (14th correction, 2026-07-29)

`machine_data/processed/machine_all.csv` retains full api provenance for an early collection
batch, and it shows GPT-4.0-Turbo was called as **`gpt-4-turbo-2024-04-09`** — a pinned GA
snapshot. The registry had dated it 2023-11-06, which is the GPT-4 Turbo *preview*
announcement, not the snapshot we called. OpenAI `/v1/models` reports `created` =
**2024-04-08** for that id, so the date moves 154 days later and is now api-verified.

This is the same class of error as the earlier GPT-4o correction, where the dataset used the
May launch date while the collector called the August snapshot. The lesson holds: date the
exact api id, never the family announcement.

Cross-checking every registry `api_model_id` against the ids actually recorded in the
collected data found this as the **only** discrepancy across the 48 models that carry
observable ids, which is good evidence the rest of the registry is faithful.

Seven models still have no recorded api id (Llama-2-70b, Claude-3-Opus, Claude-3-Haiku,
DeepSeek-Chat, Llama4-Scout, Llama4-Maverick, Claude-Sonnet-4). Their collection predates
provenance capture and the ids are not recoverable from data held here.

## Repository cleanup (2026-07-29)

Removed as superseded, duplicated, or actively misleading:
- `machine_data/processed/machine_temp05.csv` and its summary — byte-identical duplicates of
  the copies already in `legacy/` (md5 verified before deletion).
- `machine_data/models_n100.csv`, `models_n200.csv`, `models_n500.csv` — collection-planning
  snapshots on the retired schema, referenced by nothing.
- `machine_data/model_release_dates_verified.md` — superseded by the registry, and it carried
  the pre-correction dates, so keeping it would mislead.
- `machine_data/processed/*_summary.md` (three files) — stale, unreferenced, superseded by
  `docs/MODEL_LIST.md`.
- `analysis/between_unit_label.py`, `analysis/between_unit_posaware_label.py` — one-off
  labelling scripts, unreferenced, superseded by `analysis/build_overtime_data.py`.

Moved:
- `machine_data/data_cleaning.py` → `machine_data/legacy/data_cleaning_temp05.py`. It builds
  the retired temperature-0.5 dataset, so it belongs with that data rather than looking like
  part of the live pipeline.
- `analysis/figure1_composite.png`, `analysis/panelD_trial_dendrogram.png` → `results/`.

Kept deliberately: `machine_data/processed/machine_all.csv` shares no rows with the merged
file and is the only source of api ids, timestamps, token counts and latency for its 45
models — it is what made the GPT-4.0-Turbo correction possible.

Both READMEs were rewritten. They had described a 40-model, temperature-0.5-only design and
listed models as "to collect" that were already collected and analysed.

## Two identity mismatches resolved (2026-07-29)

Both flags are cleared. The evidence pointed in opposite directions, and in one case the
flag was aimed at the wrong field.

### Qwen4-Max → renamed Qwen3-Max (the label was wrong)
`api_model_requested` is recorded as **`qwen3-max-2026-01-23`** in both
`machine_data/processed/machine_all.csv` and `machine_data/raw/topup_qwen.csv` (82 rows
each). That is observed collection provenance, not a planning value, so a Qwen3-Max pinned
snapshot answered these prompts and the name "Qwen4-Max" described a model that was never
called. Renamed to **Qwen3-Max** across the registry, canonical, midpoint, merged,
machine_all and raw Qwen files — 1,760 rows in total. The release date 2026-01-23 was
already correct because it came from the snapshot id.

### Kimi-K2 → label kept, api id cleared (the api id was wrong)
The opposite conclusion. Two independent lines of evidence:

1. **No observed api id exists.** Kimi-K2's 6,175 merged rows all carry
   `data_generation=legacy` and originate from
   `legacy/prior_raw_inputs/new_machine_baseline.csv`, inherited data with no provenance
   columns. The `moonshot-v1-32k` value came from the old planning spreadsheet and was never
   an observed fact.
2. **The scores rule it out.** Moonshot-v1-8k and Moonshot-v1-128k score DAT 74.44 and
   74.45 — a 0.01 gap, as expected for one base model at two context lengths. If Kimi-K2
   were `moonshot-v1-32k` it should land near 74.4. It scores **80.91**, 6.5 points higher.
   Meanwhile it fits the Kimi lineage cleanly as its earliest and highest member
   (K2 80.91 → K2.5 79.43 → K2.6 78.55 → K3 77.56).

So the label is right and the api id was the error. `api_model_id` is now blank with
`api_id_type=none`, consistent with the seven other legacy models whose ids were never
recorded. The 2025-07-11 Kimi K2 release date stands.

**Lesson worth keeping:** a planning-sheet field can masquerade as collection provenance.
Distinguish observed values (`api_model_requested` in the response rows) from intended ones
(the planning registry) before concluding which field is wrong. Scores of known sibling
models are a useful independent check on identity.

## Uniqueness redesigned: position-agnostic, human-only reference (2026-07-29)

The primary between-person measure is now `uniqueness_human_agnostic`: mean distance from each
of a response's first 7 valid nouns to a **single** reference pool of 5,000 **human** word
tokens, frequency-weighted, pooled across word positions.

Committed artefacts:
- `machine_data/between_unit_references/human_agnostic_5000words.txt` — the pool, 5,000 tokens,
  1,774 distinct, sampled with frequency weighting to match the existing pool convention.
- `human_data/processed/uniqueness_reference_rows.txt` — the 5,765 human rows used to build the
  pool. The human baseline is computed on the complementary 5,766 rows, so no response is ever
  scored against a pool containing its own words.

Human baseline **80.62**. Machine overall 79.64. Per-model range 77.02 to 83.41. **16 of 59
models exceed the human baseline**, against 3 under the retired measure.

### Why the previous measure was retired

The old `between_unit_posaware` used seven position-specific pools, each half human and half
machine words. Two problems:

1. **It was not invariant to our own dataset.** Because the score depends only on the pool
   centroid, and half the pool was machine words, adding differently-behaved models moved every
   existing model's score. Holding the design fixed and drawing the machine half from the ten
   highest-DAT models instead of all 59 changed the count of models beating humans from 4 to 0,
   with no model changing behaviour.
2. **It penalised machines by self-reference.** Machines cluster on a small vocabulary, so
   machine words sat close to the machine half of their own yardstick. Solving for the effective
   machine share of the committed pools by projecting their centroids onto the human-to-machine
   axis gave 0.497 — a genuine 50/50. Sweeping that share from 0 to 1 moved the effect from
   d = −0.37 to −1.83, so the headline depended on an unargued design choice.

The retired measure is preserved as the `between_unit_posaware` column and the `bpa` function
for comparison.

### Position-agnostic rather than position-specific

The two variants agreed closely (response-level r = 0.966, model-level Spearman 0.947), and the
entire difference sat at word position 1, where opening words are stereotyped. Position-specific
scoring inflated the machine deficit at that position (machines 5.00 below humans at position 1,
against 2.3 to 3.1 from position 4 onward). Pooling positions removes a nuisance parameter and
costs nothing. The position-1 effect is a substantive finding in its own right — models share a
small set of openers — and belongs in the results, not in the measure.

### Figures

`results/fig2_uniqueness_with_dat.png` shows uniqueness with the DAT reference (transparent
filled DAT markers, open uniqueness markers, an arrow per model showing the direction of the
shift, and gap shading for the OpenAI and Claude lineages).
`results/fig3_uniqueness_only.png` shows uniqueness alone.
Both keep the shared y range 70.6 to 86.3 so they stay directly comparable with figure 1.

## Second uniqueness measure: repetition within one's own population (2026-07-29)

Added because the reference-based measure cannot detect repetition, which is the thing we most
want to claim about models.

### The defect it fixes

`uniqueness_human_agnostic` is mean distance to the centroid of a human reference pool. Distance
to a fixed point is **blind to how often a word is used**. Worked examples from our own data:

| Word | Share of machine tokens | Share of human tokens | Reference-based uniqueness |
|---|---|---|---|
| freedom | 3.41% | 0.05% | 82.31 (above the human mean of 80.59) |
| mountain | 5.81% | 0.50% | 76.58 |
| chair | 5.01% | 0.82% | 78.31 |
| ocean | 3.53% | 0.47% | 76.55 |

"freedom" is 68 times over-represented in machine output and still scores above the human
average, because it happens to sit far from the average human word. The measure rewards being
atypical, not being rare.

More generally: **any per-response score against a fixed external reference is mathematically
incapable of seeing self-repetition.** Two identical responses receive identical scores whether
one model or ten thousand produced them. Repetition is a property of the population, not of a
response in isolation.

### The measure

`uniqueness_own_population` = mean over the 7 nouns of −log10(share of that population's
responses containing the word), then placed on the DAT scale by matching the human mean and
standard deviation to the human DAT distribution.

Each group is scored against itself — humans against the human corpus, machines against the
pooled 59-model corpus — so the design is symmetric and does not reintroduce the contaminated
reference problem, where machines were scored against a pool whose machine half depended on
which models we happened to collect.

The calibration means human uniqueness equals human DAT (78.45) by construction, so any machine
value is read directly as a departure from the human relationship between the two measures.

### Result

| Measure, on the DAT scale | Human | Machine | Difference | d |
|---|---|---|---|---|
| Within-person DAT | 78.45 | 78.01 | 0.32 lower | −0.058 |
| Uniqueness vs human reference | 78.45 | 76.26 | 2.07 lower | −0.364 |
| **Uniqueness within own population** | **78.45** | **62.96** | **15.5 lower** | **−2.646** |

**All 59 models fall below the human level**, range 56.53 to 72.41. Most repetitive:
GPT-4.1-mini 56.5, Grok-4.20-nonreason 58.4, Hunyuan-Hy3 58.5. Least: DeepSeek-V3.2 72.4,
Qwen3.7-Max 69.9, Claude-Opus-5 69.6.

Not a sample-size artefact: subsampling the machine corpus to the human n of 11,529 five times
gave 62.86 to 62.92 against 62.96 for the full corpus.

### Honest caveat

This is closely related to the vocabulary result — humans use 8,418 distinct words across all
responses against 1,118 for machines — and should be presented as the per-response expression of
that fact, not as independent evidence. It also depends on defining the machine population as the
pooled corpus. A within-model variant, scoring each model's 500 responses against only itself,
answers a different question (does a single model repeat itself) and has not been computed.

### Figures

- `results/fig4_repetition_with_dat.png` — DAT and this measure together, with a drop arrow per
  model. The human baselines coincide by construction, so one line is drawn.
- `results/fig5_repetition_only.png` — this measure alone.
Both use y range 55.5 to 87.0, which must cover the churn range and the DAT range together.

## Unit of analysis: a model is not a person (settled 2026-07-29)

Each human contributed one response, so 11,529 humans are 11,529 independent sources. A model's
~500 responses are 500 draws from one generator, not one individual answering repeatedly.
Treating a model as a person is not a compatible comparison, so the machine population is the
**pooled 59-model corpus** and the unit of analysis is the response. A within-model repetition
variant was considered and deliberately not built.

### Pre-empting the obvious objection: "you only had 59 generators"

Vocabulary diversity grows with the number of independent sources, so part of the machine
narrowness could in principle be source count rather than narrowness per source. It is not.
Holding total responses constant at 2,000 and varying only how many models supply them:

| Sources | Distinct words |
|---|---|
| 1 model | 141 |
| 2 models | 157 |
| 5 models | 341 |
| 10 models | 379 |
| 20 models | 422 |
| 40 models | 478 |
| 59 models | 484 |
| 2,000 humans | 3,351 |

Machine vocabulary **saturates**: five models already deliver 70% of what all 59 deliver, and
going from 40 to 59 adds 1%. Twelve times more generators buys 43% more vocabulary. All 59
models together reach 14% of what 2,000 people produce. Adding models would not close the gap,
which is the strong form of the collective-narrowness claim and is now measured rather than
asserted.

### A nuance that should shape the wording

Mean pairwise Jaccard overlap between two models' vocabularies is **0.225**. The same statistic
for 59 equal-sized groups of humans is **0.217** — effectively identical. No word is used by all
59 models.

So "models churn out the same words as each other" is too strong. Relative to how much each one
says, models are no more redundant with each other than human subgroups are. The difference is
scale: mean per-model vocabulary is 129 distinct words, and the union across all 59 models is
1,131 against 8,418 for humans.

The accurate claim is therefore: **each generator draws from a small vocabulary, and pooling
generators does not recover the human range.** Not: models are copies of one another.

---

## 2026-07-31 — one matched human sample across every measure

**Problem.** The human n differed by measure. DAT used all 11,597 scoreable responses, while the
uniqueness baseline used only the 5,766 responses that did *not* help build the 5,000-token
reference pool. A within-person figure and a between-person figure therefore described different
halves of the human sample, which is not a defensible pairing.

**Why the exclusion existed, and why it was not worth its cost.** The concern was self-inclusion:
a response being scored against a pool it contributed to. Measured, that concern is negligible.
The pool acts only through its centroid, so one response contributes 7 word tokens out of 5,000,
about 0.14% of the yardstick. Empirically:

| | n | mean |
|---|---|---|
| held-out half (the old baseline) | 5,766 | 80.620 |
| pool-building half, scored against its own pool | 5,765 | 80.567 |
| every human response | 11,531 | 80.594 |

A 0.026 shift in the mean was being bought with a 50% loss of the human sample.

**Change.** A human response is now included only if *every* measure can be computed on it, and all
measures use that one set. The pool itself is unchanged — it is still built from the rows listed in
`human_data/processed/uniqueness_reference_rows.txt`, which are now also scored.
`analysis/data/response_scores_human.csv` carries a `matched` column so the sample is inspectable.
Machine responses were already all-or-nothing on the same rows (33,481).

**Effect on the baselines.**

| baseline | before | after |
|---|---|---|
| human DAT | 78.45 (n=11,597) | **78.42** (n=11,529) |
| human uniqueness | 80.62 (n=5,766) | **80.59** (n=11,529) |
| human between-person (retired measure) | 80.11 (n=11,531) | **80.11** (n=11,529) |

**Effect on results.** Model scores are untouched; only the human line moves. Models above the human
DAT average stay at 24 of 59. Models above the human uniqueness average go from 16 to **17 of 59**:
Kimi-K2.5 scores 80.599 and now clears the 80.593 line, by 0.006. That model is on a knife edge and
no argument should rest on it.

---

## 2026-07-31 (second change) — uniqueness is scored against a fresh random draw, not a fixed pool

**Change.** No reference pool is kept. Every uniqueness score is now measured against **500
reference responses drawn at random for that score**, and a response is never included in its own
reference. Both humans and machines are scored this way. The reference population stays the human
sample (11,531 responses with seven valid words): uniqueness means "unlike the people", so a
reference containing machine words would move whenever the model line-up changed.

`machine_data/between_unit_references/human_agnostic_5000words.txt` and
`human_data/processed/uniqueness_reference_rows.txt` are retained for provenance but are **no
longer used for scoring**. The legacy fixed-pool score is kept alongside the new one as
`uniqueness_fixed_pool_legacy` in `analysis/data/response_scores_*.csv`.

**Implementation.** All vectors are unit-norm and every response contributes exactly seven of them,
so the centroid of a draw of responses equals the mean of those responses' own mean-vectors, and

    score(i) = 100 * (1 - centroid(draw) . mean_vector(i))

A redraw is therefore a 500-row gather and a dot product rather than rebuilding a word pool 45,010
times. Seed 20260731, so the run is reproducible.

**Is it biased? No. Is it noisy? Barely.** Measured on the human sample:

| | mean | sd |
|---|---|---|
| full-population centroid (the estimand) | 80.5643 | 2.8945 |
| 500 redrawn per response | 80.5646 | 2.8971 |

Rescoring 400 responses 25 times with independent draws: per-response sd across redraws **0.150**,
against a between-response sd of **2.88**. The group mean moves by sd **0.008** across redraws. So
the draw adds about 5% of the signal sd as noise to an individual score and essentially nothing to
any aggregate. Model means, over roughly 500 responses each, are stable to about 0.007.

**Effect on the numbers.** The human line moves from 80.593 to **80.566**, and every score shifts
slightly because the reference is now the whole human population rather than a 5,000-token
subsample of it.

| | fixed 5,000-token pool | resampled 500 responses |
|---|---|---|
| human uniqueness | 80.593 | **80.566** |
| machine mean | 79.70 | **79.64** |
| model range | 77.02–83.41 | **76.96–83.39** |
| models above the human line | 17 of 59 | **15 of 59** |

**Read the count as soft.** Models cluster at the line: the two nearest sit 0.02 and 0.03 away, and
five are within 0.13. Across the three defensible reference constructions we have used, the count
has been 15, 16 and 17. What does not move is the contrast — 24 of 59 clear the human line on
within-person divergence, roughly 15 on uniqueness — and the 6.4-point band containing all 59
models. Do not build an argument on the exact count.

