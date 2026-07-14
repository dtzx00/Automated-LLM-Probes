# Legacy machine data (temperature = 0.5, all providers)

The original NHB-baseline machine rows collected at literal API temperature 0.5 for ALL providers.
Superseded 2026-07-14 by the per-provider MIDPOINT collection (option 1): every model is now
re-collected at the middle of its own temperature range (0-2 providers -> 1.0; 0-1 providers -> 0.5),
so models are comparable at their scale midpoints. These files are kept for reference/reproducibility
only; the analysis set is the new midpoint collection under data/raw/ + data/processed/.
