# processed/

## human_dat_all.csv
The unified human DAT dataset: all sources joined, **one row per respondent**, DAT-scored and
cleaned. This is the file to analyze.

**12,147 respondents | 51 columns**

| source code | display name | subset | rows |
|---|---|---|---|
| olson_pnas2021 | Olson et al. (2021) | study2 | 8,572 |
| btb | Beat the Bot Platform (2025) | both (individual + augmented-pair) | 1,072 |
| btb | Beat the Bot Platform (2025) | individual only | 382 |
| btb | Beat the Bot Platform (2025) | augmented-pair only | 187 |
| zunyi | Zunyi Medical University (2025) | dat | 904 |
| zunyi2024 | Zunyi Medical University (2024) | dat | 827 |
| hsbc2025 | HSBC AI Ambassador (2025) | dat | 203 |

The `source` column in the CSV holds the short code; the display name is for write-ups.

## Column groups
1. **Identifier** — `index` (unique per row), `source`, `subset`.
2. **Individual words** — `word_1..word_10`: the respondent's solo DAT words. Every source fills this.
3. **Cue model** — `cue_model_name`: the AI model in the augmented-pair exercise (Beat the Bot
   augmented-pair only; the solo exercise uses no AI).
4. **Cue words** — `cue_1..cue_10`: the AI's suggested words shown in the augmented-pair exercise
   (Beat the Bot augmented-pair only).
5. **Augmented words** — `augment_1..augment_10`: the final submitted words in the augmented-pair
   exercise, i.e. the human's choices after seeing the AI suggestions (Beat the Bot augmented-pair only).
6. **Demographics** — `demo_age, demo_gender, demo_country, demo_region, demo_ethnicity,
   demo_education, demo_major, demo_english_comfort, demo_program_type, demo_multilingual`. Filled
   per source wherever that source collected it.

Plus DAT scores and cleaning flags for each word set (below) and `extra_json` for source-specific
extras (exercise ids and original platform scores; field-study college/admission fields; GPA,
college-entrance score, and other cohort fields from the 2024/HSBC collection).

A respondent who did both Beat the Bot exercises carries 30 words on one row: 10 individual +
10 cue + 10 augmented.

## DAT scoring
Scored with Olson's official scorer (mean pairwise cosine distance of the first 7 valid unique
words, ×100; a response needs at least 7 valid words). The embedding is the validated 100k-word,
300-dimension GloVe subset used across this project. Validated exact against the scorer's published
reference examples.

Three score columns, each beside its word set:
- `word_dat_score` — individual words (all sources)
- `cue_dat_score` — augmented-pair AI cue words (Beat the Bot)
- `augment_dat_score` — augmented-pair final words (Beat the Bot)

A blank score means fewer than 7 valid words, or a response removed by cleaning (below) — blank,
never zero. **Individual-word scored: 11,399. Overall mean DAT: 78.69.**

## Cleaning
Before scoring, a response is removed if it shows a low-effort / list-the-category pattern rather
than genuine divergent choices. A word set is dropped when it contains either:
- a run of **three or more consecutive words from one closed category** — numbers, colors, animals,
  or everyday/household objects (e.g. cup, plate, fork, spoon, knife); or
- **three or more counting words or function-word fillers** anywhere in the response.

Applied independently to each word set. A removed response is flagged `word_dropped` /
`cue_dropped` / `augment_dropped` = 1 and its score is left blank; kept responses are flagged 0.
The original words are always retained.

Individual-word responses removed by cleaning: **184** (Olson 151, Beat the Bot 10,
Zunyi 2025 9, Zunyi 2024 14). Cue: 0. Augmented: 0.

## Notes
- Field-study words (Zunyi 2024/2025) are English translations of Chinese responses.
- Zunyi Medical University (2025) `demo_age` is set to 18 for all rows: this cohort are all university freshmen, so age was not collected per-person but is known by cohort.

- Respondents who submitted no words (empty response) are not in the master — dropped as
  non-completion, not as a cleaning flag.
- Two large Olson human samples (100k and 750k) are score-only with no words released, so they
  can't be re-scored or joined at the word level and are excluded.
