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
