# Pre-lock non-finalized preview rows

Rows collected during the 2026-07-15 preview batches (`collect_2026_midpoint`,
`collect_2026_thread2_n10`) for models that are **not** in the locked 55-model grid
(`data/models.csv`). Archived here for provenance, excluded from the analysis set.

Reasons a model is here:
- **GLM** family — dropped from the grid entirely (too slow, >1 min/call).
- **Preview-only models** not carried into the locked list (e.g. `gpt-5.6-sol`, `o3`,
  `deepseek-v3.1`, `deepseek-v3`, `claude-opus-4-8`).

These are NOT part of the finalized dataset. Do not merge back without re-locking the grid.
