import csv, sys, pickle, re, numpy as np, os
csv.field_size_limit(10**9)
GLOVE="/home/user/repro/models/glove_validated.pickle"
MACHINE="/home/user/machine_all_merged_relabeled.csv"
HUMAN="/home/user/human_data_scored.csv"
SEED=42; NREF=2500; K=7

print("loading glove...", flush=True)
raw=pickle.load(open(GLOVE,"rb"))
PAT=re.compile(r'^[a-z][a-z-]*[a-z]$')
NORM={w:(np.asarray(v,'float32')/(np.linalg.norm(v)+1e-12)) for w,v in raw.items() if PAT.match(w)}
def clean(w):
    c=re.sub(r'[^a-zA-Z- ]+','',str(w)).strip().lower()
    return c if (c and len(c.split(' '))==1 and c in NORM) else None

def valid_seq(cells):
    """first 7 VALID words in order -> their clean forms (valid-rank positions 0..6)."""
    out=[]
    for w in cells:
        c=clean(w)
        if c: out.append(c)
        if len(out)==7: break
    return out

# per-VALID-RANK bags (position = rank among valid words, matching DAT 'first 7 valid')
def pos_words(path, cols_fn):
    pos=[[] for _ in range(K)]
    with open(path,newline='',encoding='utf-8-sig',errors='replace') as f:
        for row in csv.DictReader(f):
            seq=valid_seq([row.get(c,"") for c in cols_fn])
            for k,c in enumerate(seq):
                pos[k].append(c)
    return pos

print("collecting per-valid-rank bags...", flush=True)
Hcols=[f"word_{i}" for i in range(1,11)]; Mcols=[f"noun_{i}" for i in range(10)]
Hp=pos_words(HUMAN,Hcols); Mp=pos_words(MACHINE,Mcols)
for k in range(K): print(f"  rank {k+1}: human {len(Hp[k]):,} | machine {len(Mp[k]):,}", flush=True)
rng=np.random.default_rng(SEED)
ref_mats=[]; ref_lists=[]
for k in range(K):
    words=list(rng.choice(Hp[k],size=NREF,replace=False))+list(rng.choice(Mp[k],size=NREF,replace=False))
    ref_mats.append(np.vstack([NORM[w] for w in words])); ref_lists.append(words)
os.makedirs("/home/user/posref",exist_ok=True)
for k in range(K):
    open(f"/home/user/posref/rank{k+1}_ref.txt","w").write("\n".join(ref_lists[k]))
print("per-rank references built (5000 each: 2500 human + 2500 machine)", flush=True)

_cache=[dict() for _ in range(K)]
def fscore(c,k):
    s=_cache[k].get(c)
    if s is None:
        s=float(np.mean(1.0-(ref_mats[k]@NORM[c])))*100.0; _cache[k][c]=s
    return s
def response_score(cells):
    seq=valid_seq(cells)
    if len(seq)<7: return None
    return float(np.mean([fscore(c,k) for k,c in enumerate(seq)]))

print("scoring machine rows (position-aware)...", flush=True)
rows=[]; n=0; scored=0
with open(MACHINE,newline='',encoding='utf-8-sig',errors='replace') as f:
    r=csv.DictReader(f); cols=list(r.fieldnames)
    if 'between_unit_posaware' not in cols: cols.append('between_unit_posaware')
    for row in r:
        s=response_score([row.get(c,"") for c in Mcols])
        row['between_unit_posaware']='' if s is None else f"{s:.4f}"
        if s is not None: scored+=1
        rows.append(row); n+=1
        if n%20000==0: print(f"  {n} rows...",flush=True)
with open(MACHINE,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
print(f"DONE: {n} rows, {scored} scored", flush=True)
# quick compare to position-agnostic
import numpy as np
pa=[float(r['between_unit_posaware']) for r in rows if r['between_unit_posaware']!='']
ag=[float(r['between_unit_score']) for r in rows if r.get('between_unit_score','')!='']
print(f"pos-AWARE mean {np.mean(pa):.2f} sd {np.std(pa):.2f} | pos-AGNOSTIC mean {np.mean(ag):.2f} sd {np.std(ag):.2f}")
