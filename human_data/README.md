# Human Data

This folder holds the human Divergent Association Task (DAT) data for the Creativity Networks
project, consolidated from five sources into a single analysis-ready dataset that mirrors the
machine-side schema in `../machine_data/`.

The goal is one clean human table I can line up directly against the machine data for the
human-vs-model comparison: one row per respondent, the same DAT word slots across every source, and
DAT scores computed with one scorer so human and machine numbers are comparable.

## Layout
- `raw/` — one file per originally-separate source, lightly processed. Each keeps its own
  respondents, its DAT words, and whatever demographics that source collected. Nothing is trimmed.
- `processed/` — the unified master, `human_dat_all.csv`: all sources joined, one row per
  respondent, DAT-scored and cleaned. This is the file to analyze.

## Sources
| Source | Description | Respondents | Mean DAT |
|---|---|---|---|
| Olson et al. (2021) | Published open DAT sample, 98 countries | 8,571 | 78.47 |
| Beat the Bot Platform (2025) | https://beat-the-bot.com — individual and augmented-pair exercises | 1,641 | 80.27 |
| Zunyi Medical University (2025) | Field study, DAT arm, translated to English | 904 | 79.02 |
| Zunyi Medical University (2024) | Field study cohort, DAT arm, translated to English | 827 | 78.44 |
| HSBC AI Ambassador (2025) | Corporate AI-ambassador programme cohort, DAT | 203 | 79.02 |

**Master total: 12,147 respondents.**

Mean DAT above is the individual-word mean over scored responses. Beat the Bot's figure is its solo
(individual) arm; its AI-augmented arm is analyzed separately.

## Provenance notes
- Zunyi Medical University (2024) and HSBC AI Ambassador (2025) arrived in a later consolidated
  collection file and were merged in de-duplicated against the existing master (rows already present
  from other cohorts were skipped, not double-counted).
- Zunyi Medical University (2025) is the copy already in the project database; it was not re-imported
  from the later collection file.

See `raw/README.md` and `processed/README.md` for exact columns, counts, scoring, and cleaning.
