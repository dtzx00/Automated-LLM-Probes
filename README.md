# Creativity Networks

Human and LLM divergent thinking measured on the Divergent Association Task (DAT), across
59 models released 2023–2026 and 11,597 human respondents.

Two measures are computed on every response:

- **Within-person divergence (DAT)** — mean pairwise semantic distance among the first 7
  valid nouns of a single response. How varied one response is internally.
- **Uniqueness** (`uniqueness_human_agnostic`) — mean distance from each noun to a single
  reference pool of 5,000 human words, pooled across word positions. How unlike the human
  population a response is. This is the primary between-person measure as of 2026-07-29; see
  `docs/DATA_PROVENANCE.md` for why the earlier balanced, position-specific pool was retired.

Scoring follows Olson et al. (2021): GloVe 840B/300d filtered to the Olson vocabulary,
first 7 unique in-vocabulary nouns, mean pairwise cosine distance ×100.

## Headline result

| | Human mean | Models beating the human mean |
|---|---|---|
| Within-person (DAT) | 78.45 | 24 of 59 |
| Uniqueness | 80.62 | 16 of 59 |

Models match humans on average but not in the tail. On within-person divergence they equal
the human mean (d = −0.06) while compressing the distribution: better than humans in the
bottom decile, worse in the top. On uniqueness the same shape appears — level with humans at
the 10th percentile and progressively behind toward the 99th. The mechanism is vocabulary:
674 distinct words against 5,559 for humans on matched samples.

## Canonical data

`machine_data/processed/machine_analysis_canonical.csv` — **33,481 responses, 59 models**,
one row per response, with DAT and between-person computed on *identical* rows. This is the
only file the analysis reads for machine scores. Human side:
`human_data/processed/human_dat_all.csv` (12,147 rows, 11,597 scoreable).

All responses use the baseline prompt at each provider's midpoint temperature, default
thinking effort, n≈500 per model.

## Model registry

`machine_data/models.csv` is the **single source of truth** for model metadata and release
dates — provider, region, intelligence class, reasoning flag, api model id and whether it
was a pinned snapshot or a rolling alias, release date with its precision and verification
status, and the per-model scores. `analysis/build_overtime_data.py` reads it directly, so
the figures cannot disagree with it. Readable version: `docs/MODEL_LIST.md`.

Release dates are only trustworthy when tied to the exact api id that was called. OpenAI,
Anthropic and xAI return a real creation timestamp; DashScope and Moonshot return the date
of the query, so they are never used as release dates. Three models called through bare
rolling aliases are marked `alias_unresolved` rather than given false precision. Two models
carry an `identity_flag` where the label and the endpoint disagree. See
`docs/DATA_PROVENANCE.md`.

## Figures

All figures render from the shared style module `analysis/overtime_style.py` at true 16:9
(3200×1800) on one shared y range of 56 to 86, so any two are directly comparable.

| Figure | Script | Output |
|---|---|---|
| Within-person DAT alone | `analysis/fig1_dat_by_release.py` | `results/fig1_dat_by_release.png` |
| Uniqueness with the DAT reference and shift arrows | `analysis/fig2_uniqueness_with_dat.py` | `results/fig2_uniqueness_with_dat.png` |
| Uniqueness alone | `analysis/fig3_uniqueness_only.py` | `results/fig3_uniqueness_only.png` |

Conventions: within-person is drawn solid with filled markers, uniqueness dotted with open
markers. Marker shape encodes intelligence class (efficient ▽, all-rounder ○, hybrid
◇, reasoning ★), colour encodes provider, purple is the human baseline. Version-evolution
lines are drawn for the OpenAI and Claude lineages only.

## Layout

```
analysis/          build script, shared figure style, three figure scripts, figure inputs in data/
docs/              MODEL_LIST.md (readable registry), DATA_PROVENANCE.md (sourcing + known issues)
machine_data/      models.csv registry, collection script, raw + processed responses, reference pools
human_data/        raw human sources and the consolidated scored file
results/           committed figures
```

## Reproducing

```bash
python3 analysis/build_overtime_data.py <repo_root>   # rescores everything, writes analysis/data/*.json
python3 analysis/fig1_dat_by_release.py               # run from analysis/
python3 analysis/fig2_dat_to_uniqueness_by_release.py
python3 analysis/fig3_uniqueness_by_release.py
```

The build needs a local GloVe pickle (not in git — see `docs/DATA_PROVENANCE.md`). It prints
the model count, the rows dropped for failing the 7-valid-noun rule, and the human
baselines, and asserts that DAT and between-person are scored on identical rows.

## Known limitations

- 78% of machine rows predate the locked collector, so their `parse_status` is unverifiable.
- No usable reasoning traces: Anthropic returns encrypted thinking blocks, OpenAI does not
  expose reasoning on the completions endpoint.
- Human collection-year assignments (zunyi→2024, btb→2025) were inferred rather than read from the
  source files. Reviewed 2026-07-29 and accepted as the project convention; they affect only the
  x-position of the year-wise human baseline markers, not any score.
- Two unresolved model identity mismatches, flagged in the registry.
