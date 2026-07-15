# Human Data

This folder holds the human Divergent Association Task (DAT) data for the Creativity Networks
project, consolidated from three independent studies into a single analysis-ready dataset that
mirrors the machine-side schema in `../data/`.

The goal is one clean human table I can line up directly against the machine data for the
human-vs-model comparison: one row per unique respondent, the same DAT word slots across every
source, and DAT scores computed with one scorer so human and machine numbers are comparable.

## Layout
- `raw/` — one file per source, lightly processed. Each keeps its own respondents, its DAT words,
  and whatever demographics that study collected. Nothing is trimmed here.
- `processed/` — the unified master, `human_dat_all.csv`: all three sources joined, one row per
  individual, DAT-scored and cleaned. This is the file to analyze.

## Sources
| Source | What it is | Respondents (with DAT words) |
|---|---|---|
| Olson PNAS 2021 (Study 2) | The published open DAT sample, 98 countries | 8,571 |
| BTB | Our platform: solo (individual) and human+AI (augmented-pair) DAT exercises | 1,641 |
| Zunyi | Field study, DAT arm, translated to English | 904 |

## Scope notes
- The DAT word lists are the only human word-level data available across these studies. Two large
  Olson score sets (a 100k and a 750k human sample) exist but were released as scores only, with no
  underlying words, so they cannot be re-scored or joined at the word level and are excluded here.
- The Zunyi study ran a multi-task battery; only its DAT arm is included. Its non-DAT measures are
  out of scope for this dataset.

See `raw/README.md` and `processed/README.md` for exact columns, counts, and scoring details.
