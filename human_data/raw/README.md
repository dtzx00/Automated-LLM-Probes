# raw/

One file per source. Each is the source's own respondents with DAT words and native demographics,
lightly processed and not trimmed. These feed the unified master in `../processed/`.

## olson_pnas2021_study2_dat.csv — 8,571 rows
Olson et al. 2021 PNAS, Study 2 — the published open DAT sample (OSF `kbeq6`, `study2.tsv`).
This is the shared human backbone: the same sample appears in our published divergent-creativity
work and in Olson's 2026 follow-up (verified byte-for-byte against that follow-up's human anchor —
identical n, mean, and SD). It is the full published sample; nothing was excluded.

- Kept: `id, age, gender, country, multilingual, dat, word.1..word.10`.
- Dropped: the paper's other creativity measures (Alternative Uses, problem-solving), which are
  not part of this consolidation.

## btb_individual_augpair.csv — 1,641 rows
Our platform's human DAT (from the BTB analysis repo, `master_user_sessions.csv`).
Superset of respondents who completed the individual exercise OR the augmented-pair exercise
(not required to have done both): 1,454 have individual words, 1,259 have augmented-pair words,
1,072 have both.

- Kept: demographics + the individual arm (words, score, duration) + the augmented-pair arm
  (final submitted words, the AI cue words, model, score).
- Dropped: team and augmented-team arms.
- Note: the individual exercise involves no AI, so it has no model name.

## zunyi_dat.csv — 904 rows
Field-study DAT arm, translated to English from the source study.

- Kept: DAT words (`dat_1_en..dat_10_en`) + demographics (sex, ethnicity, province, major, college)
  and three admission background fields.
- Dropped: all non-DAT measures and personal names.
- Note: responses were originally given in Chinese; these are English translations. Cross-language
  scoring is handled at the consolidation step.

## Zunyi Medical University (2024) and HSBC AI Ambassador (2025)
These two sources arrived together in a later consolidated collection file (a multi-cohort export)
rather than as standalone raw files, so they are not stored as separate CSVs in `raw/`. They were
mapped into the master schema and merged directly:

- **Zunyi Medical University (2024)** — field-study cohort, DAT arm, English-translated. 827
  respondents kept (rows with no words were dropped as non-completion). Extra cohort fields (GPA,
  college-entrance score, and similar) are preserved in `extra_json`.
- **HSBC AI Ambassador (2025)** — corporate AI-ambassador programme cohort, DAT. 203 respondents.

Both were de-duplicated against the existing master before merging; rows already present from other
cohorts in the same export were skipped. Zunyi Medical University (2025) was **not** re-imported from
this file — the existing `zunyi` copy is authoritative.
