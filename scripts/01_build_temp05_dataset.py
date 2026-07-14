"""
Build the canonical temp-0.5 machine dataset for all 20 models, with source + temperature
tags preserved through every step. Reads Anthony's two raw machine files (staged in data/raw/)
and emits data/processed/machine_temp05.csv.

Design rules (locked 2026-07-14 with Dawei):
- Analysis uses temperature == 0.5 ONLY. Old 9 models: 'baseline' == 0.5. GPT-5 family: 0.5.
  New sweep models: keep only the 0.5 slice.
- Every row carries: model_name, batch, temperature, source_file, dat score, 10 nouns.
- No collapsing/rebalancing here. Standardization to n=1000 is a SEPARATE collection step.
"""
import pandas as pd
from pathlib import Path

RAW = Path("data/raw")
OUT = Path("data/processed"); OUT.mkdir(parents=True, exist_ok=True)

NOUNS = [f"noun_{i}" for i in range(10)]

def load_old(p):
    df = pd.read_csv(p, low_memory=False)
    df = df.rename(columns={"temperature": "temperature_raw"})
    df["batch"] = "old_2024"
    df["temperature"] = 0.5          # 'baseline' == temp 0.5 per Dawei
    df["source_file"] = p.name
    df["dat_score"] = df["dat"]
    return df[["model_name", "batch", "temperature", "source_file", "dat_score"] + NOUNS]

def load_new(p):
    df = pd.read_csv(p, low_memory=False)
    df = df[df["temperature"] == 0.5].copy()   # temp-0.5 slice only
    df["batch"] = "new_2025"
    df["source_file"] = p.name
    # prefer rescored dat_new; fall back to dat
    df["dat_score"] = df["dat_new"] if "dat_new" in df.columns else df["dat"]
    df["temperature"] = 0.5
    return df[["model_name", "batch", "temperature", "source_file", "dat_score"] + NOUNS]

old = load_old(RAW / "average_machine_raw.csv")
new = load_new(RAW / "new_machine_baseline.csv")
allm = pd.concat([old, new], ignore_index=True)

allm.to_csv(OUT / "machine_temp05.csv", index=False)

summary = (allm.groupby(["batch", "model_name"]).size()
           .rename("n_at_temp_0.5").reset_index().sort_values(["batch", "n_at_temp_0.5"]))
summary["need_to_1000"] = (1000 - summary["n_at_temp_0.5"]).clip(lower=0)
summary.to_csv(OUT / "machine_temp05_summary.csv", index=False)

print(f"models: {allm['model_name'].nunique()}  rows: {len(allm)}")
print(summary.to_string(index=False))
print(f"\nTOTAL @0.5: {len(allm)}  | top-up to reach 1000/model: {int(summary['need_to_1000'].sum())}")
