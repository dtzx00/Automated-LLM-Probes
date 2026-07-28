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

def rd(f):
    with open(f,newline='',encoding='utf-8',errors='replace') as fh: return list(csv.DictReader(fh))

# ---------------- P6: provider-authoritative release dates ----------------
DATE_FIX = {  # api-verified created_at for the exact api_model_id we called
 "Claude-Sonnet-4.6":"2026-02-17","Claude-Opus-4.7":"2026-04-14","Claude-Sonnet-5":"2026-06-29",
 "Claude-Fable-5":"2026-06-07","Claude-Opus-5":"2026-07-24",
 "Grok-4.20-nonreason":"2026-03-09","Grok-4.20-reason":"2026-03-09","Grok-4.3":"2026-04-17","Grok-4.5":"2026-06-29",
 "GPT-3.5-Turbo":"2023-02-28","GPT-4o":"2024-08-04","GPT-4.1":"2025-04-10","GPT-4.1-mini":"2025-04-10",
 "GPT-4.1-nano":"2025-04-10","o4-mini":"2025-04-08","GPT-5":"2025-08-01","GPT-5-mini":"2025-08-05",
 "GPT-5.1":"2025-11-10","GPT-5.2":"2025-12-09","GPT-5.4":"2026-03-04","GPT-5.5":"2026-04-22",
 "GPT-5.6-Sol":"2026-06-23","Kimi-K3":"2026-07-16",
}
NEW_META = {"Kimi-K3":("moonshot","reasoning","Eastern","Yes"),
            "Claude-Opus-5":("anthropic","hybrid","Western","Yes"),
            "GPT-5.6-Sol":("openai","hybrid","Western","Yes")}

# ---------------- metadata + canonical names from master ----------------
MAST_ROWS = rd(MAST)
canon={}; meta={}
for r in MAST_ROWS:
    n=r['model_name']; canon[n.lower()]=n
    meta.setdefault(n,dict(prov=r['provider'],intel=r['intelligence'],reg=r['region'],reas=r['reasoning'],
                           y=int(r['model_year']),mo=int(r['model_month']),d=int(r['model_day']),prec=r['date_precision']))
for n,(p,i,rg,rs) in NEW_META.items():
    canon[n.lower()]=n
    meta[n]=dict(prov=p,intel=i,reg=rg,reas=rs,y=0,mo=0,d=0,prec="exact")
for n,ds in DATE_FIX.items():
    y,mo,d=[int(x) for x in ds.split("-")]
    meta[n].update(y=y,mo=mo,d=d,prec="exact")

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
for n,f in NEWF.items():
    for r in rd(f"{ROOT}/machine_data/raw_reasoning/{f}.csv"):
        if r['model_name']==n: resp[n].append([r[f'noun_{i}'] for i in range(10)])
print(f"[P2/P3] models assembled: {len(resp)}  (name-casing merged, 3 new models included)")

# ---------------- P4/P7: score DAT + between-unit on the SAME rows ----------------
out=[]; drops=Counter()
per=open("/home/user/fix/canonical_responses.csv","w",newline='')
wtr=csv.writer(per); wtr.writerow(["model_name","provider","intelligence","region","reasoning",
  "release_date","date_precision"]+[f"noun_{i}" for i in range(10)]+["dat_score","between_unit_posaware"])
for n,rows in resp.items():
    m=meta[n]; ds=f"{m['y']:04d}-{m['mo']:02d}-{m['d']:02d}"
    dv=[]; bv=[]
    for nouns in rows:
        a=dat(nouns); b=bpa(nouns)
        if a is None or b is None:
            drops[n]+=1; continue          # P7: explicit, symmetric drop
        dv.append(a); bv.append(b)
        wtr.writerow([n,m['prov'],m['intel'],m['reg'],m['reas'],ds,m['prec']]+list(nouns)+[f"{a:.6f}",f"{b:.6f}"])
    out.append(dict(model=n,prov=m['prov'],intel=m['intel'],y=m['y'],mo=m['mo'],d=m['d'],prec=m['prec'],
                    n=len(dv),dat=float(np.mean(dv)),btw=float(np.mean(bv)),
                    dat_sd=float(np.std(dv,ddof=1)),btw_sd=float(np.std(bv,ddof=1))))
per.close()
print(f"[P4] DAT and between-unit now computed on identical rows for all {len(out)} models")
print(f"[P7] rows dropped for failing the 7-valid-noun rule: {sum(drops.values())} -> {dict(drops)}")

# ---------------- P5: one human baseline, same scorer ----------------
hd=[];hb=[];hy=defaultdict(list)
YR={'olson_pnas2021':2022,'zunyi':2024,'zunyi2024':2024,'btb':2025,'hsbc2025':2025}
for r in rd(HUMAN):
    nouns=[r[f'word_{i}'] for i in range(1,11)]
    a=dat(nouns); b=bpa(nouns)
    if a is not None: hd.append(a); hy[YR[r['source']]].append(a)
    if b is not None: hb.append(b)
human=dict(human_dat_mean=float(np.mean(hd)),human_between_mean=float(np.mean(hb)),
           n_dat=len(hd),n_btw=len(hb),
           human_year={str(k):float(np.mean(v)) for k,v in sorted(hy.items())})
print(f"[P5] single human baseline: DAT {human['human_dat_mean']:.2f} (n={len(hd)}), between {human['human_between_mean']:.2f} (n={len(hb)})")

# ---------------- emit figure inputs ----------------
def frac(y,mo,d): return y+((mo-1)*30.44+d)/365.0
recs_d=[[frac(r['y'],r['mo'],r['d']),r['y'],r['mo'],r['d'],r['prov'],r['intel'],r['model'],r['dat'],r['prec']] for r in out]
recs_b=[[frac(r['y'],r['mo'],r['d']),r['y'],r['mo'],r['d'],r['prov'],r['intel'],r['model'],r['btw'],r['prec']] for r in out]
hyr={str(k):v for k,v in human['human_year'].items()}
json.dump({"recs":recs_d,"human_year":hyr},open("/home/user/fix/permonth_data.json","w"))
json.dump({"recs":recs_b,"human_year":hyr},open("/home/user/fix/between_data.json","w"))
json.dump({"human_dat_mean":human['human_dat_mean'],"human_between_mean":human['human_between_mean']},
          open("/home/user/fix/human_avg.json","w"))
json.dump(human,open("/home/user/fix/human_baselines_canonical.json","w"),indent=1)
json.dump(sorted(out,key=lambda r:-r['dat']),open("/home/user/fix/model_summary.json","w"),indent=1)
print(f"\nmodels={len(out)}  total scored responses={sum(r['n'] for r in out)}")
print(f"{'model':22}{'n':>6}{'DAT':>8}{'BTW':>8}  released")
for r in sorted(out,key=lambda r:-r['dat']):
    print(f"{r['model'][:21]:22}{r['n']:>6}{r['dat']:>8.2f}{r['btw']:>8.2f}  {r['y']}-{r['mo']:02d}-{r['d']:02d}")
