# human_data/processed/

## human_dat_all.csv
Unified human DAT master — all three word-level sources joined into one long table, one row per human DAT response, with a `source` column.

**Rows: 12,189**
| source | subset | rows |
|---|---|---|
| olson_pnas2021 | study2 | 8,572 |
| btb | individual | 1,454 |
| btb | augmented_pair | 1,259 |
| zunyi | dat | 904 |

BTB contributes two rows per relevant user (individual arm + augmented-pair arm are separate DAT responses).

**Schema:**
- `response_id` — unique, prefixed by source (pnas_*, btb_*_indiv, btb_*_augpair, zunyi_*)
- `source` — olson_pnas2021 | btb | zunyi
- `subset` — study2 | individual | augmented_pair | dat
- `dat_score` — intentionally BLANK; all sources will be re-scored together with the machine data on one embedding.
- `noun_0..noun_9` — the 10 DAT words (English; Zunyi words are translations)
- Demographics (unified, filled where the source carries them): age, gender, country, region, ethnicity, education, major, english_comfort, program_type, multilingual, ai_model
- `extra_json` — source-specific extras (BTB exercise_id/duration/machine_words/ai_score; Zunyi college/admission_batch/candidate_type/foreign_language)

**Demographic coverage** differs by source (each source only has what it collected):
- BTB: richest (gender, age, ethnicity, education, major, english_comfort, region, program_type, ai_model)
- PNAS 2021: age, gender, country, multilingual
- Zunyi: gender, country(China), province(region), ethnicity, major + extras in extra_json

**Note on scoring:** dat_score left blank on purpose — the joint human+machine re-score happens after machine data consolidation, on a single scorer/embedding. Zunyi words are Chinese-native translated to English; cross-lingual scoring is a re-score-time decision.

_Built 2026-07-15 by Lumen._
