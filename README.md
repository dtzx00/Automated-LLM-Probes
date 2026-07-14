# Creativity Networks

## Key design decisions (locked 2026-07-14)
1. **Analysis uses temperature == 0.5 only.** The temperature sweep is not a variable in
   this paper (that is the NHB paper's territory). Old 9 models' `baseline` == temp 0.5;
   GPT-5 family == 0.5; new sweep models keep their 0.5 slice.
2. **Sample-size standardization = collection, not trimming.** Target n=1000 per model at
   temp 0.5, achieved by generating top-ups — never by downsampling good data.
3. **Models (40 total, 2022–2026; full inventory in `data/model_inventory.csv`):**
   - **Collected (20, temp 0.5, n=12,397):** GPT-3.5-Turbo, Llama-2-70b, GPT-4.0-Turbo, Claude-3-Haiku, Claude-3-Opus, Claude-3.5-Sonnet, GPT-4o, Ernie-4.0-8k, DeepSeek-R1, Claude-Opus-4.1, Claude-Sonnet-4, Deepseek-Chat, Kimi-k2, Llama4-Scout, Llama4-Maverick, Qwen-Max, Qwen-Turbo, Grok-Code-Fast, GPT-5, GPT-5-Mini
   - **To collect — 2025 (10):** o3, Claude Opus 4.7, Grok 4, DeepSeek R2, Qwen3.7 Max, Hunyuan T1, GPT-5.4, Doubao Seed 2.0 Pro, Claude Sonnet 4, Grok 3
   - **To collect — 2026 (10):** GPT-5.6 Sol, GPT-5.5, Claude Fable 5, Claude Sonnet 5, Claude Opus 4.8, Grok 4.5, DeepSeek V4 Pro, Qwen4 Max, Kimi K2.6, Hunyuan Hy3
   - Region: 26 Western / 14 Eastern (origin, not prompt language — all prompts English). Reasoning: 19 yes / 21 no. Target: n=1000 per model @ temp 0.5.

## Layout
- `data/raw/` — untouched source files (machine raw x2; add human sources here).
- `data/processed/` — pipeline outputs (source-tagged).
- `data/data_collection.py` — data collection (n=1000 top-up); `data/01_build_temp05_dataset.py` — rebuild processed set; `data/collection_spec.md` — spec.

## Machine data at temp 0.5 (current)
20 models, 12,397 rows. Old 9 @ 750, GPT-5/Mini @ 550/500, new sweep 9 @ ~478–515.
See `data/processed/machine_temp05_summary.csv` and `data/collection_spec.md`.

## Not yet incorporated (human side)
Lucas BTB (~800), Olson 2026 Sci Reports (~100k), Zunyi convergent (~800). See `data/collection_spec.md`.
