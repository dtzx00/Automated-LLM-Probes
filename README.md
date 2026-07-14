# Creativity Networks

## Key design decisions (locked 2026-07-14)
1. **Analysis uses temperature == 0.5 only.** The temperature sweep is not a variable in
   this paper (that is the NHB paper's territory). Old 9 models' `baseline` == temp 0.5;
   GPT-5 family == 0.5; new sweep models keep their 0.5 slice.
2. **Sample-size standardization = collection, not trimming.** Target n=1000 per model at
   temp 0.5, achieved by generating top-ups — never by downsampling good data.
3. **Models (current 20, all @ temp 0.5):**
   - Old (2024, n=750): GPT-3.5-Turbo, GPT-4.0-Turbo, GPT-4o, Claude-3-Haiku, Claude-3-Opus, Claude-3.5-Sonnet, Ernie-4.0-8k, Llama-2-70b, DeepSeek-R1
   - New (2025, n=478-515): Claude-Opus-4.1, Claude-Sonnet-4, Deepseek-Chat, Kimi-k2, Llama4-Scout, Llama4-Maverick, Qwen-Max, Qwen-Turbo, Grok-Code-Fast
   - GPT-5 family (n=550/500): GPT-5, GPT-5-Mini
   - _Even-newer models to add (each +1000): PENDING Dawei's list (no Google model present yet)._

## Layout
- `data/raw/` — untouched source files (machine raw x2; add human sources here).
- `data/processed/` — pipeline outputs (source-tagged).
- `data/data_collection.py` — data collection (n=1000 top-up); `data/01_build_temp05_dataset.py` — rebuild processed set; `data/collection_spec.md` — spec.

## Machine data at temp 0.5 (current)
20 models, 12,397 rows. Old 9 @ 750, GPT-5/Mini @ 550/500, new sweep 9 @ ~478–515.
See `data/processed/machine_temp05_summary.csv` and `data/collection_spec.md`.

## Not yet incorporated (human side)
Lucas BTB (~800), Olson 2026 Sci Reports (~100k), Zunyi convergent (~800). See `data/collection_spec.md`.
