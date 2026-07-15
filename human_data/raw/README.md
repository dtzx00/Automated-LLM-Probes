# human_data/raw/

## btb_individual_augpair.csv
BTB human DAT data from `lucas23wong/btb-data-analysis` (`data/clean/master_user_sessions.csv`).

**Filter:** superset (m:m) — users with individual words OR augmented-pair words (not required to have both).
- Master users: 1,861
- Have individual words: 1,454
- Have augpair words: 1,259
- **Superset (individual OR augpair): 1,641 -> this file (both=1,072; individual-only=382; augpair-only=187)

**Columns kept (58):**
- Demographics/meta: user_id, class_session, gender, race_ethnicity, age, english_comfort, education, consent, major, newsletter, language, email, region, program_type
- Individual arm: individual_exercise_id, individual_score, individual_completed_at, individual_ai_model, individual_duration, individual_word_1..10, individual_uniqueness
- Augmented-pair arm: augmented_pair_exercise_id, augmented_pair_score, augmented_pair_completed_at, augmented_pair_ai_model, augmented_pair_duration, augmented_pair_word_1..10 (human), augmented_pair_machine_word_1..10 (AI), augmented_pair_ai_score, augmented_pair_uniqueness, augmented_pair_machine_uniqueness

**Dropped:** all team_* and augmented_team_* columns.

_Built 2026-07-15 by Lumen. Source commit: lucas23wong/btb-data-analysis main._

## zunyi_dat.csv
Zunyi field-study human DAT from `jingoystat/convergent-creativity` (`study4_cat_dat_gaokao`), TRANSLATED to English (source: Dawei's `2025_Zunyi_0929_translated_dat.csv`, built from the study's translation cache).

**Kept:** DAT + demographics only.
- DAT words: dat_1_en .. dat_10_en (English translations; originally administered/scored in Chinese)
- Demographics: sex_en, ethnicity_en, province_en, major_en, college_en
- CEE background attributes (kept as demographics, per Dawei): admission_batch_en, candidate_type_en, foreign_language_en

**Dropped:** all CAT, CCAR, LRT, and Gaokao *score/outcome* measures; student name (PII); dat_score (will re-score all sources together with the machine data later).

**Rows:** 904 (dropped 2 fully-empty DAT rows; one row has 9 words, kept pending re-score).

_Note: Zunyi DAT responses are Chinese-native; these are English translations. Cross-source scoring on a shared embedding is a re-score-time decision._
_Built 2026-07-15 by Lumen._

## olson_pnas2021_study2_dat.csv
Olson et al. 2021 PNAS Study 2 human DAT (OSF kbeq6, `study2.tsv`). The shared human spine across PNAS 2021, Dawei's NHB study, and Olson's Sci Reports 2026 (verified: Sci Reports `Human (8k)` tier is byte-identical — same n=8,572, mean=78.1930, sd=6.7731).

**Kept (DAT + demographics, matching BTB/Zunyi):** id, age, gender, country, multilingual, dat, word.1..10.
**Dropped:** aut.originality*, problems.* (Alternative Uses + problem-solving tasks — not part of this DAT consolidation).

**Rows:** 8,572 (full published sample, 98 countries; all 10 words present, all scored, no duplicate IDs — nothing trimmed).

_Verified against PNAS 2021 (N=8,572 exact) and Sci Reports 2026 human anchor. Built 2026-07-15 by Lumen._
