# human_data/processed/

## human_dat_all.csv
Unified human DAT master — **one row per unique individual**, all three sources joined, `source`-tagged.

**Rows: 11,117 unique individuals | Columns: 46**
| source | subset | rows |
|---|---|---|
| olson_pnas2021 | study2 | 8,572 |
| btb | both (individual + augpair) | 1,072 |
| btb | individual only | 382 |
| btb | augmented_pair only | 187 |
| zunyi | dat | 904 |

BTB = 1,641 unique users total (1,454 have individual words, 1,259 have augpair words, 1,072 have both).

**Schema (46 cols):**
- `response_id` (source-prefixed, unique), `source`, `subset`, `dat_score` (blank — joint re-score later)
- `dat_word_1..10` — primary SOLO human DAT (PNAS study2 / BTB individual / Zunyi)
- `augpair_dat_word_1..10` — BTB only: the pair's FINAL submitted augmented-pair words (human+AI collaborative output)
- `augpair_machine_word_1..10` — BTB only: the AI cue words shown in the pairing (brackets stripped)
- `augpair_ai_model` — BTB augpair only: the paired model. **Individual exercise has NO model** (no AI involvement) — left blank by design.
- Demographics: age, gender, country, region, ethnicity, education, major, english_comfort, program_type, multilingual
- `extra_json` — exercise ids + original platform scores (individual + augpair), plus Zunyi college/admission fields

A BTB user who did both exercises carries 30 words on one row: 10 individual + 10 augpair-final + 10 machine-cue.

**Notes:**
- dat_score blank on purpose — re-score all sources + machine data on one embedding later.
- Zunyi words are Chinese-native, translated to English.
- Fix applied: Lucas's `augmented_pair_machine_word_*` leaked list-brackets ([word / word]); stripped on ingest, all cells verified clean.

_Built 2026-07-15 by Lumen._
