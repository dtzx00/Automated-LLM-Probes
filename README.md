# Creativity Networks

Clean rebuild of the Human-vs-LLM DAT creativity-networks analysis (target: PNAS).
Leader: Dawei Wang. Senior: Brian Uzzi. Supersedes `anthony240624/DAT-Creativity-Networks-Project`.

## Why this repo exists
Anthony's repo mixed cleaning + analysis in single notebooks, imported the old models
**baseline-only**, and carried a temperature sweep it never used — which made per-model
sample sizes look wildly inconsistent. This repo fixes that with a pipeline that keeps
`source`, `batch`, and `temperature` tags on every row from raw to analysis.

## Key design decisions (locked 2026-07-14)
1. **Analysis uses temperature == 0.5 only.** The temperature sweep is not a variable in
   this paper (that is the NHB paper's territory). Old 9 models' `baseline` == temp 0.5;
   GPT-5 family == 0.5; new sweep models keep their 0.5 slice.
2. **Provenance is preserved.** Every row carries model_name, batch (old_2024 / new_2025),
   temperature, source_file, dat_score, and the 10 nouns.
3. **Sample-size standardization = collection, not trimming.** Target n=1000 per model at
   temp 0.5, achieved by generating top-ups — never by downsampling good data.

## Layout
- `data/raw/` — untouched source files (machine raw x2; add human sources here).
- `data/processed/` — pipeline outputs (source-tagged).
- `scripts/` — ordered, runnable steps (01_build_temp05_dataset.py, ...).
- `pipeline/` — analysis notebooks (added incrementally).
- `docs/` — data tabulation, collection spec, decisions.
- `results/` — figures, tables, CSVs.

## Machine data at temp 0.5 (current)
20 models, 12,397 rows. Old 9 @ 750, GPT-5/Mini @ 550/500, new sweep 9 @ ~478–515.
See `data/processed/machine_temp05_summary.csv` and `docs/collection_spec.md`.

## Not yet incorporated (human side)
Lucas BTB (~800), Olson 2026 Sci Reports (~100k), Zunyi convergent (~800). See `docs/`.
