# Machine data

LLM responses to the DAT prompt: 10 single-word English nouns, no proper nouns, no
technical terms, comma-separated. Baseline prompt, each provider's midpoint temperature,
default thinking effort (never overridden), n≈500 per model, no seed.

## Files

| Path | What it is |
|---|---|
| `models.csv` | **The registry.** One row per model in the analysis (59). Metadata, api id and id type, release date with precision/verification/source, per-model scores, and any identity flag. Read directly by `analysis/build_overtime_data.py`. |
| `data_collection.py` | The collection script. Single model, serial `--all`, or 7-lane `--parallel` (one thread per provider key). One raw row per generation with full provenance, incremental flush, resumable. |
| `raw/` | Per-provider collection output, `topup_<provider>.csv`. |
| `raw_reasoning/` | Collection under the reasoning-capture protocol, which also stores `reasoning_text`. |
| `processed/machine_analysis_canonical.csv` | **The analysis file.** 33,481 responses, 59 models, DAT and between-person on identical rows. |
| `processed/machine_final_baseline_midpoint.csv` | Midpoint-temperature slice the canonical file is built from. |
| `processed/machine_all_merged.csv` | Full merge across all collection eras, including the temperature sweep. Superset; not the analysis set. |
| `processed/machine_all.csv` | Early collection batch, 45 models, retained because it is the only file carrying full api provenance (requested/returned ids, timestamps, tokens, latency) for those rows. |
| `between_unit_references/` | Rank-matched reference pools for the between-person measure: `rank1_ref.txt` … `rank7_ref.txt`, each 2,500 human + 2,500 machine words, plus a position-agnostic 5,000-word pool. |
| `human_avg_baselines.json` | Human grand means, same scorer as the machine numbers. |
| `legacy/` | Archived, not in the active analysis: the retired temperature-0.5 dataset and the script that built it (`data_cleaning_temp05.py`), plus `prior_raw_inputs/` (the original source files this project inherited). |

## Reasoning capture

Every response row has a `reasoning_text` column. The collector reads whatever the API
exposes — `reasoning_content` on OpenAI-compatible endpoints, `thinking` blocks on
Anthropic, inline `<think>` tags otherwise — and never sends a reasoning-effort or
thinking-budget override, so every model runs at its shipped default. Reasoning tokens are
billed whether or not the text is stored, so capturing costs nothing extra. In practice
Anthropic returns encrypted blocks and OpenAI does not expose reasoning on the completions
endpoint, so usable traces exist only for the open models.

## Release dates

Trust a date only when it is tied to the exact api id that was called. OpenAI, Anthropic
and xAI return a real creation timestamp. DashScope and Moonshot return the timestamp of
the *query*, so they are never used as release dates — but DashScope does expose pinned
dated snapshot ids, and the earliest snapshot in a family is good evidence. Rolling aliases
cannot be dated at all and are marked `alias_unresolved`. Details and the full correction
history are in `docs/DATA_PROVENANCE.md`.
