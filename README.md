# Creativity Networks

## Key design decisions (locked 2026-07-14)
1. **Analysis uses temperature == 0.5 only.** The temperature sweep is not a variable in
   this paper (that is the NHB paper's territory). Old 9 models' `baseline` == temp 0.5;
   GPT-5 family == 0.5; new sweep models keep their 0.5 slice.
2. **Sample-size standardization = collection, not trimming.** Target n=1000 per model at
   temp 0.5, achieved by generating top-ups — never by downsampling good data.
3. **Models (40 total, 2022–2026; full inventory in `machine_data/models.csv`):**
   - **Collected (20, temp 0.5, n=12,397):** GPT-3.5-Turbo, Llama-2-70b, GPT-4.0-Turbo, Claude-3-Haiku, Claude-3-Opus, Claude-3.5-Sonnet, GPT-4o, Ernie-4.0-8k, DeepSeek-R1, Claude-Opus-4.1, Claude-Sonnet-4, Deepseek-Chat, Kimi-k2, Llama4-Scout, Llama4-Maverick, Qwen-Max, Qwen-Turbo, Grok-Code-Fast, GPT-5, GPT-5-Mini
   - **To collect — 2025 (10):** o3, Claude Opus 4.7, Grok 4, DeepSeek R2, Qwen3.7 Max, Hunyuan T1, GPT-5.4, Doubao Seed 2.0 Pro, Claude Sonnet 4, Grok 3
   - **To collect — 2026 (10):** GPT-5.6 Sol, GPT-5.5, Claude Fable 5, Claude Sonnet 5, Claude Opus 4.8, Grok 4.5, DeepSeek V4 Pro, Qwen4 Max, Kimi K2.6, Hunyuan Hy3
   - Region: 26 Western / 14 Eastern (origin, not prompt language — all prompts English). Reasoning: 19 yes / 21 no. Target: n=1000 per model @ temp 0.5.

## Layout
- `machine_data/` — machine (LLM) DAT collection. See `machine_data/README.md` for the full spec, the
  locked 55-model grid (`machine_data/models.csv`), and how to run.
  - `machine_data/raw/` — per-provider raw output (`topup_<provider>.csv`), one row per generation.
  - `machine_data/processed/` — consolidated outputs (`machine_all.csv`, `machine_temp05.csv`).
  - `machine_data/data_collection.py` — the one collection script (single / `--all` / `--parallel`).
  - `machine_data/data_cleaning.py` — the one cleaning/build script (temp-0.5 dataset).
  - `machine_data/legacy/` — archived reference/older data (not in the active analysis set).
- `human_data/` — human DAT sources, consolidated to the machine-side schema.

## Machine data (current)
Locked grid: **55 models** (38 live-collectable + 17 legacy/retired). Selection rules, provider lanes,
and the full model list are documented in `machine_data/README.md`. Collection uses per-provider
midpoint temperature; the temp-0.5 legacy set (12,397 rows) is preserved for reference.

## Not yet incorporated (human side)
Lucas BTB (~800), Olson 2026 Sci Reports (~100k), Zunyi convergent (~800). See `machine_data/README.md`.

## Model-DAT-by-release figure (added 2026-07-18)
- Figure: `results/fig_model_dat_by_release.png` — per-model mean DAT vs release date, colored by provider (developer brand), shaped by intelligence class (efficient / all-rounder / hybrid / reasoning), with per-provider flagship evolution lines and the human baseline.
- Reproduce: `python analysis/model_dat_by_release.py` (needs `GLOVE_PICKLE` → validated GloVe model, kept out of git).
- Data columns added to `machine_data/processed/machine_all_merged.csv`: `model_month`, `model_day`, `date_precision` (exact|approx), `intelligence`; `provider` corrected to developer brand (not API endpoint).
- Verification of every model's release date, provider, and intelligence class: `machine_data/model_release_dates_verified.md`.

## Cleanup (2026-07-18)
Removed transient `logs/` and superseded intermediate collection snapshots (`machine_all_n50…n500`, `raw_n100…n500_catchup`); canonical data is `machine_data/processed/machine_all_merged.csv`. Logs and large `*.pickle` embeddings are now gitignored.
