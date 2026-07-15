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
