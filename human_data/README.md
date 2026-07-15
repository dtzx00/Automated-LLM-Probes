# Human Data

Human DAT sources for the Creativity Networks project, consolidated to match the
machine-side schema (`../machine_data/processed/machine_temp05.csv` / `machine_all.csv`).

## Layout
- `raw/` — one row per human response, source-tagged, nothing trimmed. Keep-flags carried so any threshold is reproducible.
- `processed/` — slim analysis view mirroring `machine_temp05.csv` (source, batch, dat_score, noun_0..9) for analysis-ready rows.

## Sources (in-repo, from anthony240624/DAT-Creativity-Networks-Project)
| Source | Rows | Stage | Tag |
|---|---|---|---|
| average_human_raw.csv | 9,297 | raw (Olson 2021 + Bao 2024 + HKU) | olson_human_raw |
| 04_human_dat_review.csv | 5,517 | reviewed + keep-flags | olson_human_reviewed |
| project_1.csv (Human) | 5,000 | final analysis set | human_study1a |
| project_2 HCI (Human arm) | 605 | BTB solo-human | btb_human |

The first three are ONE lineage at three cleaning stages (raw 9,297 -> reviewed 5,517 -> final 5,000), not independent datasets.

## Deferred (not in this repo yet)
- Olson 2026 Sci Reports (~100k) — external release; confirm scope before adding.
- Zunyi convergent (~800) — a CONVERGENT task (CAT project), not DAT. Confirm before mixing.

_Status: folder scaffolded 2026-07-15. Consolidation build pending Dawei's scope decisions (see thread)._
