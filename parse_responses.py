from __future__ import annotations
import re, pandas as pd
import glove_word_embeddings as gwe
from automated_llm_probes import parse_and_merge

def parse_dat(raw):
    nouns = [n for n in (gwe.pre.clean_word(t) for t in str(raw or "").split(",")) if n][:10]
    return nouns + [""] * (10 - len(nouns))

def parse_aut(raw):
    uses = []
    for line in re.split(r"[\n\r]+", str(raw or "")):
        line = re.sub(r"^\s*[\d\.\)\-]+\s*", "", line)
        if toks := [t for t in (gwe.pre.clean_word(t) for t in line.split()) if t]:
            uses.append(" ".join(toks))
    return ", ".join(uses)

def parse_wrt(raw):
    text = re.sub(r"^#+\s*.*$", "", str(raw or ""), flags=re.M)
    text = re.sub(r"^\s*Title:.*$", "", text, flags=re.M | re.I)
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def load_task(task: str) -> pd.DataFrame:
    task = task.lower()
    df = pd.DataFrame.from_dict(parse_and_merge(task),orient='index')
    if task == "dat":
        parsed = df["raw"].map(parse_dat)
        df[[f"noun_{i}" for i in range(10)]] = pd.DataFrame(parsed.tolist())
        df["response_clean"] = parsed.map(lambda x: ", ".join(n for n in x if n))
        extra = [f"noun_{i}" for i in range(10)]
    elif task == "aut":
        df["object"] = df["prompt"].str.extract(r"object: (.+?)\?", expand=False).str.strip()
        df["response_clean"] = df["raw"].map(parse_aut)
        extra = ["object"]
    elif task == "wrt":
        cues = df["prompt"].str.extract(r"words: (.+?)\.", expand=False).str.strip().str.split(r",\s*")
        df[["cue_0", "cue_1", "cue_2"]] = pd.DataFrame(cues.tolist()).iloc[:, :3]
        df["response_clean"] = df["raw"].map(parse_wrt)
        extra = ["cue_0", "cue_1", "cue_2"]
    else:
        raise ValueError(f"Unknown task: {task}")
    cols = ["task", "model_name", "model_id", "provider", "rep", "temperature_std"] + extra + ["prompt", "response_clean", "ts_utc", "hash"]
    return df[[c for c in cols if c in df.columns]].sort_values(["model_name", "rep"]).reset_index(drop=True)

def load_tasks():
    for task in ("dat", "aut", "wrt"):
        print(f"Parsing {task.upper()}...")
        df = load_task(task)
        print(df.shape)
        df.to_csv(f"./data/{task}.csv", index=False)