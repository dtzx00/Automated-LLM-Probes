"""
data_collection.py — generate machine DAT responses to standardize every model to n=1000 @ temp 0.5.

Parity contract (must match existing temp-0.5 rows so top-ups are comparable):
  - prompt      : baseline DAT prompt (baseline_prompt_1)
  - temperature : 0.5
  - scoring     : same DAT scorer -> dat_new
  - output cols : model_name, batch, temperature, source_file, dat_score, noun_0..noun_9
Writes new rows into data/raw/, then re-run 01_build_temp05_dataset.py to rebuild processed/.

Run ownership: Dawei triggers; Lumen executes against model APIs.
Model list + per-model top-up counts: processed/machine_temp05_summary.csv (need_to_1000).
API keys are read from env at runtime; never hard-coded here.
"""
# TODO(Lumen, pending Dawei): finalize model list (incl. even-newer models) + API access, then implement generation loop.
raise SystemExit("data_collection.py is a stub — awaiting final model list + API access before implementation.")
