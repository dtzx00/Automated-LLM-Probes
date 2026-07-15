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
| Source | Description | Respondents | DAT Score |
|---|---|---|---|
| Olson et al., 2021 (S2) | The published open DAT sample, 98 countries | 8,571 | 78 |
| Beat The Bot Platform | https://beat-the-bot.com -- individual and augmented-pair exercises | 1,641 | 78 |
| Zunyi Medical College | Field study, DAT arm, translated to English | 904 | 78 |
