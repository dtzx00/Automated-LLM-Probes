# Legacy machine data (temperature = 0.5, all providers)

The original NHB-baseline machine rows collected at literal API temperature 0.5 for ALL providers.
Superseded 2026-07-14 by the per-provider MIDPOINT collection (option 1): every model is now
re-collected at the middle of its own temperature range (0-2 providers -> 1.0; 0-1 providers -> 0.5),
so models are comparable at their scale midpoints. These files are kept for reference/reproducibility
only; the analysis set is the midpoint collection, consolidated into
`machine_data/processed/machine_analysis_canonical.csv`.

## Contents
| File | What it is |
|---|---|
| `machine_temp05_legacy_0p5.csv` | The temperature-0.5 dataset, 12,397 rows across 20 models. |
| `machine_temp05_summary_legacy.csv` | Per-model counts for the above. |
| `data_cleaning_temp05.py` | The script that built the two files above, moved here 2026-07-29 so it is not mistaken for part of the live pipeline. |
| `prior_raw_inputs/` | The original source files this project inherited (`average_machine_raw.csv`, `new_machine_baseline.csv`). |
| `pre_lock_nonfinal/` | Rows collected before the collector was locked; not analysis-grade. |
