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


## DAT scoring (2026-07-15)
Scored with Olson's official scorer (github.com/jayolson/divergent-association-task) — mean pairwise cosine distance of the first 7 valid unique words x100, `minimum=7`.
Embedding: the lab's validated **100k-vocab 300d GloVe** subset (`olson_glove.pickle`, words.txt n glove.840B.300d). Validated against Olson's published examples: low=50.31, avg=77.90, high=95.22, cat-dog=19.83, cat-thimble=87.87 — exact.

Three score columns, each next to its word set:
- `word_dat_score` (after word_10) — individual/solo DAT (all sources)
- `cue_dat_score` (after cue_10) — augpair machine cue words (BTB augpair)
- `augment_dat_score` (after augment_10) — augpair final submitted words (BTB augpair)

**Coverage:** word=10,544 (PNAS 8,549 + BTB 1,097 + Zunyi 898); cue=989; augment=987. Blank = fewer than 7 valid unique words (Olson's minimum). Means: PNAS 78.28, BTB 80.18, Zunyi 78.96 (PNAS matches Olson's published ~78).

Note: on ~81 PNAS rows where respondents entered sentences/opposites/function words, this subset scores slightly differently from Olson's published `dat` (max ~14; mean abs diff 0.04 overall) because the 100k subset omits some function words the full GloVe includes. Per Dawei, the subset is the scorer of record for cross-source consistency.


## Word cleaning (Brian's rule, 2026-07-15)
Before scoring, a response is DROPPED (whole response, that word set only) if it shows low-effort/gaming patterns, per Brian's judgment:
- a **consecutive run of >=3 adjacent words** from one closed category: numbers, colors, animals, or environmental/household objects (e.g. cup, plate, fork, spoon, knife); OR
- **>=3 counting words / function-word fillers** anywhere in the response.

Applied independently to word_/cue_/augment_ sets. Dropped responses get `*_dropped=1` and a blank `*_dat_score` (invalid, not zero). `*_dropped=0` = kept & scored.

**Result:** word dropped=170 (scored 10,384); cue dropped=0 (989); augment dropped=0 (987). Means after cleaning: PNAS 78.47, BTB 80.27, Zunyi 79.02.
