# human_data/processed/

## human_dat_all.csv
Unified human DAT master — all three word-level sources joined, one row per human DAT response, with a `source` column.

**Rows: 12,189 | Columns: 36**
| source | subset | rows |
|---|---|---|
| olson_pnas2021 | study2 | 8,572 |
| btb | individual | 1,454 |
| btb | augmented_pair | 1,259 |
| zunyi | dat | 904 |

**Schema (in order):**
- `response_id`, `source`, `subset`, `dat_score` (blank — re-scored jointly with machine data later)
- `dat_word_1 .. dat_word_10` — the human's 10 DAT words
- `machine_word_1 .. machine_word_10` — the AI cue words shown in the augmented-pair exercise (populated for btb/augmented_pair only; blank for pure-human rows)
- `machine_model_name` — the AI model involved (augmented_pair: the paired model; btb/individual: the model the human competed against; blank for PNAS/Zunyi pure-human)
- Demographics: `age, gender, country, region, ethnicity, education, major, english_comfort, program_type, multilingual`
- `extra_json` — source-specific extras (BTB exercise_id/duration/ai_score/original score; Zunyi college/admission_batch/candidate_type/foreign_language)

**Machine columns coverage:** 1,259 rows (btb augmented_pair) have machine cue words + model; btb individual (1,454) has model name only (competitor), no cue words; PNAS + Zunyi are pure human (both blank).

**Demographics** are filled per source wherever collected: BTB richest; PNAS = age/gender/country/multilingual; Zunyi = gender/country/province(region)/ethnicity/major.

_dat_score blank on purpose — joint human+machine re-score on one embedding after machine consolidation. Zunyi words are Chinese-native, translated to English. Built 2026-07-15 by Lumen._
