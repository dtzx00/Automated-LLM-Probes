# Creativity Networks

## Key design decisions (locked 2026-07-14)
1. **Analysis uses temperature == 0.5 only.** The temperature sweep is not a variable in
   this paper (that is the NHB paper's territory). Old 9 models' `baseline` == temp 0.5;
   GPT-5 family == 0.5; new sweep models keep their 0.5 slice.
2. **Sample-size standardization = collection, not trimming.** Target n=1000 per model at
   temp 0.5, achieved by generating top-ups — never by downsampling good data.
3. Models:



## Layout
- `data/raw/` — untouched source files (machine raw x2; add human sources here).
- `data/processed/` — pipeline outputs (source-tagged).
- `data/data_collection.py` - scripts to run data collection. 

## Machine data at temp 0.5 (current)
20 models, 12,397 rows. Old 9 @ 750, GPT-5/Mini @ 550/500, new sweep 9 @ ~478–515.
See `data/processed/machine_temp05_summary.csv` and `docs/collection_spec.md`.

## Not yet incorporated (human side)
Lucas BTB (~800), Olson 2026 Sci Reports (~100k), Zunyi convergent (~800). See `docs/`.
