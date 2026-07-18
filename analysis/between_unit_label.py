import csv, sys, pickle, re, numpy as np
csv.field_size_limit(10**9)
GLOVE="/home/user/repro/models/glove_validated.pickle"
MACHINE="/home/user/machine_all_merged_relabeled.csv"
HUMAN="/home/user/human_data_scored.csv"
SEED=42; NREF=2500  # per side

print("loading glove...", flush=True)
raw=pickle.load(open(GLOVE,"rb"))
PAT=re.compile(r'^[a-z][a-z-]*[a-z]$')
NORM={w:(np.asarray(v,'float32')/(np.linalg.norm(v)+1e-12)) for w,v in raw.items() if PAT.match(w)}
print(f"glove vocab {len(NORM):,}", flush=True)

def clean(w):
    c=re.sub(r'[^a-zA-Z- ]+','',str(w)).strip().lower()
    return c if (c and len(c.split(' '))==1 and c in NORM) else None

def human_words():
    out=[]
    with open(HUMAN,newline='',encoding='utf-8-sig',errors='replace') as f:
        for row in csv.DictReader(f):
            for i in range(1,11):
                c=clean(row.get(f"word_{i}",""))
                if c: out.append(c)
    return out
def machine_words():
    out=[]
    with open(MACHINE,newline='',encoding='utf-8-sig',errors='replace') as f:
        for row in csv.DictReader(f):
            for i in range(10):
                c=clean(row.get(f"noun_{i}",""))
                if c: out.append(c)
    return out

print("collecting bags...", flush=True)
H=human_words(); M=machine_words()
print(f"human valid tokens {len(H):,} | machine valid tokens {len(M):,}", flush=True)
rng=np.random.default_rng(SEED)
ref_words=list(rng.choice(H,size=NREF,replace=False))+list(rng.choice(M,size=NREF,replace=False))
ref_mat=np.vstack([NORM[w] for w in ref_words])   # (5000, dim), normalized
print(f"reference set: {ref_mat.shape[0]} words (2500 human + 2500 machine), NO exclusion", flush=True)
np.save("/home/user/ref_mat.npy",ref_mat)
with open("/home/user/ref_words.txt","w") as f: f.write("\n".join(ref_words))

_cache={}
def focal_score(word):
    c=clean(word)
    if c is None: return None
    s=_cache.get(c)
    if s is None:
        cos=ref_mat @ NORM[c]           # cosine sim to all 5000
        s=float(np.mean(1.0-cos))*100.0 # mean cosine distance, full fixed reference
        _cache[c]=s
    return s

def response_score(words):
    vals=[]
    for w in words:
        s=focal_score(w)
        if s is not None: vals.append(s)
        if len(vals)==7: break
    return float(np.mean(vals)) if len(vals)==7 else None

print("scoring machine rows...", flush=True)
rows=[]; n=0; scored=0
with open(MACHINE,newline='',encoding='utf-8-sig',errors='replace') as f:
    r=csv.DictReader(f); cols=list(r.fieldnames)
    if 'between_unit_score' not in cols: cols.append('between_unit_score')
    for row in r:
        s=response_score([row.get(f"noun_{i}","") for i in range(10)])
        row['between_unit_score']= '' if s is None else f"{s:.4f}"
        if s is not None: scored+=1
        rows.append(row); n+=1
        if n%20000==0: print(f"  {n} rows...", flush=True)
with open(MACHINE,'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
print(f"DONE machine: {n} rows, {scored} scored, {len(_cache)} unique focal words", flush=True)
