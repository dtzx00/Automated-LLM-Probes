# human_data/processed/

## human_dat_all.csv
Unified human DAT master — one row per unique individual, all three sources joined, `source`-tagged.

**Rows: 11,117 unique individuals | Columns: 46**
| source | subset | rows |
|---|---|---|
| olson_pnas2021 | study2 | 8,572 |
| btb | both | 1,072 |
| btb | individual only | 382 |
| btb | augmented_pair only | 187 |
| zunyi | dat | 904 |

**Six column sets (in order):**
1. `index` — unique per row (source-prefixed). `source`, `subset` are tags; `dat_score` blank (joint re-score later).
2. `word_1 .. word_10` — individual (solo) human DAT words. All sources fill this.
3. `cue_model_name` — the AI model in the augmented-pair exercise (BTB augpair only). No model for individual/PNAS/Zunyi.
4. `cue_1 .. cue_10` — augpair MACHINE (AI cue) words (BTB augpair only).
5. `augment_1 .. augment_10` — augpair FINAL submitted words (BTB augpair only).
6. `demo_*` — demographics: demo_age, demo_gender, demo_country, demo_region, demo_ethnicity, demo_education, demo_major, demo_english_comfort, demo_program_type, demo_multilingual.

Plus `extra_json` — exercise ids + original platform scores (BTB) / college+admission fields (Zunyi).

A BTB user who did both exercises carries 30 words: word_* (individual) + cue_* (machine) + augment_* (augpair final).

**Notes:** dat_score blank on purpose (re-score with machine data on one embedding). Zunyi words are Chinese-native, translated to English. Lucas's machine words had leaked list-brackets — stripped on ingest, verified clean.

_Built 2026-07-15 by Lumen._
