"""Canonical rebuild of the creativity_networks analysis dataset.
Fixes P1 (MiniMax-M3 reparse), P2 (name casing), P3 (new models merged),
P4 (DAT + between-unit on the SAME rows), P5 (single human baseline),
P6 (provider-authoritative release dates), P7 (explicit parse-failure drops)."""
import csv, os, json, pickle, re, itertools, sys
import numpy as np, scipy.spatial.distance as ssd
from collections import defaultdict, Counter
csv.field_size_limit(10**9)
ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/cn"
MID   = f"{ROOT}/machine_data/processed/machine_final_baseline_midpoint.csv"
MAST  = f"{ROOT}/machine_data/processed/machine_all_merged.csv"
HUMAN = f"{ROOT}/human_data/processed/human_dat_all.csv"
REFD  = f"{ROOT}/machine_data/between_unit_references"
NEWF  = {"Kimi-K3":"topup_moonshot_k3","Claude-Opus-5":"topup_anthropic_opus5","GPT-5.6-Sol":"topup_openai_gpt56sol"}
V = pickle.load(open("/home/user/repro/models/glove_olson.pickle","rb"))

# ---------------- scorers (Olson 2021 exact) ----------------
def validate(w):
    c=re.sub(r"[^a-zA-Z- ]+","",str(w)).strip().lower()
    if len(c)<=1: return None
    cands=[re.sub(r" +","-",c),re.sub(r" +","",c)] if " " in c else [c]+([re.sub(r"-+","",c)] if "-" in c else [])
    for x in cands:
        if x in V: return x
    return None
def dat(words,minimum=7):
    u=[]
    for w in words:
        v=validate(w)
        if v and v not in u: u.append(v)
    if len(u)<minimum: return None
    s=u[:minimum]
    return sum(ssd.cosine(V[a],V[b]) for a,b in itertools.combinations(s,2))/(minimum*(minimum-1)/2)*100
_n={}
def nvec(w):
    v=_n.get(w)
    if v is None:
        r=V.get(w)
        if r is None: return None
        v=np.asarray(r,float); v/= (np.linalg.norm(v)+1e-12); _n[w]=v
    return v
def cln(w):
    c=re.sub(r'[^a-zA-Z- ]+','',str(w)).strip().lower()
    return c if (c and len(c.split(' '))==1 and c in V) else None
refm=[np.vstack([nvec(w) for w in (x.strip() for x in open(f"{REFD}/rank{k}_ref.txt")) if w and nvec(w) is not None]) for k in range(1,8)]
_fc=[dict() for _ in range(7)]
def fs(c,k):
    s=_fc[k].get(c)
    if s is None: s=float(np.mean(1-(refm[k]@nvec(c))))*100; _fc[k][c]=s
    return s
def bpa(cells):
    seq=[]
    for w in cells:
        c=cln(w)
        if c: seq.append(c)
        if len(seq)==7: break
    return float(np.mean([fs(c,k) for k,c in enumerate(seq)])) if len(seq)==7 else None

# ---- PRIMARY uniqueness measure: position-agnostic, HUMAN-ONLY reference ----
# Design decision (2026-07-29): the reference contains only human words and is pooled across
# positions. This makes the measure invariant to which models are in the dataset and gives it
# one clean meaning - how unlike the human population a response is. The balanced half-machine
# per-rank pools are retained as `bpa` for comparison only.
UPOOL=f"{ROOT}/machine_data/between_unit_references/human_agnostic_5000words.txt"
_uc=np.mean(np.vstack([nvec(w) for w in (x.strip() for x in open(UPOOL)) if w and nvec(w) is not None]),axis=0)
_ucache={}
def _us(c):
    s=_ucache.get(c)
    if s is None: s=100*(1-float(_uc@nvec(c))); _ucache[c]=s
    return s
def uniq(cells):
    seq=[]
    for w in cells:
        c=cln(w)
        if c: seq.append(c)
        if len(seq)==7: break
    return float(np.mean([_us(c) for c in seq])) if len(seq)==7 else None

# rows used to BUILD the pool -> excluded from the human baseline (no self-inclusion)
UREF_ROWS=set(int(x) for x in open(f"{ROOT}/human_data/processed/uniqueness_reference_rows.txt")
              if x.strip() and not x.startswith("#"))

def rd(f):
    with open(f,newline='',encoding='utf-8',errors='replace') as fh: return list(csv.DictReader(fh))

# ---------------- single model registry is the ONLY source of dates + metadata ----------------
REG = f"{ROOT}/machine_data/models.csv"

MAST_ROWS = rd(MAST)
canon={}
for r in MAST_ROWS: canon[r['model_name'].lower()]=r['model_name']

meta={}
for r in rd(REG):
    n=r['model']; canon[n.lower()]=n
    y,mo,d=[int(x) for x in r['release_date'].split("-")]
    meta[n]=dict(prov=r['provider'],intel=r['intelligence'],reg=r['region'],reas=r['reasoning'],
                 y=y,mo=mo,d=d,prec=r['date_precision'])
print(f"[registry] {len(meta)} models loaded from machine_data/models.csv (dates + metadata)")

# ---------------- P1: rebuild MiniMax-M3 responses from raw text ----------------
m3=[]
for r in MAST_ROWS:
    if r['model_name']!='MiniMax-M3': continue
    t=r['raw_response_text']
    tail=t.split('</think>')[-1] if '</think>' in t else t
    w=[x.strip().lower() for x in re.split(r'[,\n]',tail) if x.strip()]
    w=[x for x in w if re.fullmatch(r'[a-z][a-z-]*[a-z]',x)]
    if w: m3.append(w[:10])
print(f"[P1] MiniMax-M3 re-parsed from raw_response_text: {len(m3)}/500 responses recovered")

# ---------------- assemble per-model response sets ----------------
resp=defaultdict(list)   # canonical name -> list of noun lists
for r in rd(MID):
    n=canon.get(r['model'].lower())
    if n is None: raise SystemExit(f"unmapped midpoint model {r['model']}")
    if n=='MiniMax-M3': continue                      # replaced by re-parse
    resp[n].append([r[f'word_{i}'] for i in range(1,11)])
resp['MiniMax-M3']=m3
# The three newest models were later merged INTO the midpoint file. Only pull them
# from raw_reasoning/ if the midpoint file does not already carry them, otherwise
# every response is counted twice (n doubles; means unchanged, counts wrong).
for n,f in NEWF.items():
    if resp.get(n):
        print(f"[P3] {n}: already in midpoint file ({len(resp[n])} responses) - skipping raw_reasoning to avoid double count")
        continue
    for r in rd(f"{ROOT}/machine_data/raw_reasoning/{f}.csv"):
        if r['model_name']==n: resp[n].append([r[f'noun_{i}'] for i in range(10)])
print(f"[P2/P3] models assembled: {len(resp)}  (name-casing merged, 3 new models included)")

# ---------------- P4/P7: score DAT + between-unit on the SAME rows ----------------
out=[]; drops=Counter()
per=open("/home/user/fix/canonical_responses.csv","w",newline='')
wtr=csv.writer(per); wtr.writerow(["model_name","provider","intelligence","region","reasoning",
  "release_date","date_precision"]+[f"noun_{i}" for i in range(10)]+["dat_score","between_unit_posaware","uniqueness_human_agnostic"])
for n,rows in resp.items():
    m=meta[n]; ds=f"{m['y']:04d}-{m['mo']:02d}-{m['d']:02d}"
    dv=[]; bv=[]; uv=[]
    for nouns in rows:
        a=dat(nouns); b=bpa(nouns); u=uniq(nouns)
        if a is None or b is None or u is None:
            drops[n]+=1; continue          # P7: explicit, symmetric drop
        dv.append(a); bv.append(b); uv.append(u)
        wtr.writerow([n,m['prov'],m['intel'],m['reg'],m['reas'],ds,m['prec']]+list(nouns)+[f"{a:.6f}",f"{b:.6f}",f"{u:.6f}"])
    out.append(dict(model=n,prov=m['prov'],intel=m['intel'],y=m['y'],mo=m['mo'],d=m['d'],prec=m['prec'],
                    n=len(dv),dat=float(np.mean(dv)),btw=float(np.mean(bv)),uniq=float(np.mean(uv)),
                    dat_sd=float(np.std(dv,ddof=1)),btw_sd=float(np.std(bv,ddof=1)),uniq_sd=float(np.std(uv,ddof=1))))
per.close()
print(f"[P4] DAT and between-unit now computed on identical rows for all {len(out)} models")
print(f"[P7] rows dropped for failing the 7-valid-noun rule: {sum(drops.values())} -> {dict(drops)}")

# ---------------- P5: one human baseline, same scorer ----------------
hd=[];hb=[];hu=[];hy=defaultdict(list);huy=defaultdict(list)
YR={'olson_pnas2021':2022,'zunyi':2024,'zunyi2024':2024,'btb':2025,'hsbc2025':2025}
for ri,r in enumerate(rd(HUMAN)):
    nouns=[r[f'word_{i}'] for i in range(1,11)]
    a=dat(nouns); b=bpa(nouns)
    if a is not None: hd.append(a); hy[YR[r['source']]].append(a)
    if b is not None: hb.append(b)
    if ri not in UREF_ROWS:                     # exclude pool-building rows
        u=uniq(nouns)
        if u is not None: hu.append(u); huy[YR[r['source']]].append(u)
human=dict(human_dat_mean=float(np.mean(hd)),human_between_mean=float(np.mean(hb)),
           human_uniq_mean=float(np.mean(hu)),n_dat=len(hd),n_btw=len(hb),n_uniq=len(hu),
           human_year={str(k):float(np.mean(v)) for k,v in sorted(hy.items())},
           human_uniq_year={str(k):float(np.mean(v)) for k,v in sorted(huy.items())})
print(f"[uniqueness] human-only position-agnostic baseline {human['human_uniq_mean']:.2f} "
      f"(n={len(hu)}, pool-building rows excluded)")
print(f"[P5] single human baseline: DAT {human['human_dat_mean']:.2f} (n={len(hd)}), between {human['human_between_mean']:.2f} (n={len(hb)})")

# ---------------- emit figure inputs ----------------
def frac(y,mo,d): return y+((mo-1)*30.44+d)/365.0
recs_d=[[frac(r['y'],r['mo'],r['d']),r['y'],r['mo'],r['d'],r['prov'],r['intel'],r['model'],r['dat'],r['prec']] for r in out]
recs_b=[[frac(r['y'],r['mo'],r['d']),r['y'],r['mo'],r['d'],r['prov'],r['intel'],r['model'],r['btw'],r['prec']] for r in out]
recs_u=[[frac(r['y'],r['mo'],r['d']),r['y'],r['mo'],r['d'],r['prov'],r['intel'],r['model'],r['uniq'],r['prec']] for r in out]
hyr={str(k):v for k,v in human['human_year'].items()}
json.dump({"recs":recs_d,"human_year":hyr},open("/home/user/fix/permonth_data.json","w"))
json.dump({"recs":recs_b,"human_year":hyr},open("/home/user/fix/between_data.json","w"))
json.dump({"recs":recs_u,"human_year":{str(k):v for k,v in human['human_uniq_year'].items()}},
          open("/home/user/fix/uniqueness_data.json","w"))
json.dump({"human_dat_mean":human['human_dat_mean'],"human_between_mean":human['human_between_mean'],
           "human_uniq_mean":human['human_uniq_mean']},
          open("/home/user/fix/human_avg.json","w"))
json.dump(human,open("/home/user/fix/human_baselines_canonical.json","w"),indent=1)
json.dump(sorted(out,key=lambda r:-r['dat']),open("/home/user/fix/model_summary.json","w"),indent=1)
print(f"\nmodels={len(out)}  total scored responses={sum(r['n'] for r in out)}")
print(f"{'model':22}{'n':>6}{'DAT':>8}{'BTW':>8}  released")
for r in sorted(out,key=lambda r:-r['dat']):
    print(f"{r['model'][:21]:22}{r['n']:>6}{r['dat']:>8.2f}{r['btw']:>8.2f}  {r['y']}-{r['mo']:02d}-{r['d']:02d}")
