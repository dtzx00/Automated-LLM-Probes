"""
data_collection.py — generate machine DAT responses to standardize every model to n=1000 @ temp 0.5.

BASELINE PROMPT is the verbatim `baseline_prompt_1` from the NHB divergent-creativity OSF
(osf.io/a9v2t -> studies_prompts.ipynb, Study 1a/1b). Do NOT paraphrase — it must match the
existing 12,397 rows exactly. Loaded from data/baseline_prompt.txt.

Parity contract (must match existing temp-0.5 rows):
  - prompt      : baseline_prompt.txt (verbatim NHB baseline_prompt_1)
  - temperature : 0.5
  - scoring     : same DAT scorer -> dat_new
  - output cols : model_name, batch, temperature, source_file, dat_score, noun_0..noun_9
Writes new rows into data/raw/, then re-run 01_build_temp05_dataset.py to rebuild processed/.

Run ownership: Dawei triggers; Lumen executes against model APIs.
Per-model top-up counts: processed/machine_temp05_summary.csv; full grid: model_inventory.csv.
API keys read from env at runtime; never hard-coded.
"""
from pathlib import Path

BASELINE_PROMPT = Path(__file__).with_name("baseline_prompt.txt").read_text().strip()
TEMPERATURE = 0.5
TARGET_N_PER_MODEL = 1000

# TODO(Lumen, pending Dawei): finalize API access, then implement the per-model generation loop
# (call model API with BASELINE_PROMPT @ TEMPERATURE, parse comma-separated nouns, score dat_new,
#  append to data/raw/<batch>_topup.csv). Loop over models needing top-up from model_inventory.csv.
if __name__ == "__main__":
    raise SystemExit("data_collection.py: prompt + parity locked; generation loop pending API access.")
