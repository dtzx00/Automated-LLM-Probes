"""Canonical rebuild of the creativity_networks analysis dataset.
Fixes P1 (MiniMax-M3 reparse), P2 (name casing), P3 (new models merged),
P4 (DAT + between-unit on the SAME rows), P5 (single human baseline),
P6 (provider-authoritative release dates), P7 (explicit parse-failure drops)."""
import csv, os, json, pickle, re, itertools, sys
import numpy as np, scipy.spatial.distance as ssd
from collections import defaultdict, Counter, Counter
csv.field_size_limit(10**9)
ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/cn"
MID   = f"{ROOT}/machine_data/processed/machine_final_baseline_midpoint.csv"
MAST  = f"{ROOT}/machine_data/processed/machine_all_merged.csv"
HUMAN = f"{ROOT}/human_data/processed/human_dat_all.csv"
REFD  = f"{ROOT}/machine_data/between_unit_references"
NEWF  = {"Kimi-K3":"topup_moonshot_k3","Claude-Opus-5":"topup_anthropic_opus5","GPT-5.6-Sol":"topup_openai_gpt56sol"}
# ---------------- scorers: single source of truth in analysis/scoring.py ----------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scoring import (init as _scoring_init, validate, dat, cln, seq7, bpa, uniq,
                     churn_scorer, make_resampled_uniq)
V = _scoring_init(ROOT)

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

# ---------------- reference population for uniqueness (no fixed pool) ----------------
# Every uniqueness score is measured against a FRESH random draw of 500 human responses,
# redrawn for each response and never including the response itself. Nothing is cached across
# responses, so no arbitrary pool is frozen into the measure and no response is excluded for
# having helped build one. Machines are scored against the same human population: uniqueness
# means "unlike the people", so the reference stays human-only and cannot move when the model
# line-up changes.
HROWS=rd(HUMAN)
HQ=[seq7([r[f'word_{i}'] for i in range(1,11)]) for r in HROWS]
REF_SEQS=[q for q in HQ if q is not None]
REF_POS={}                      # csv row index -> row in the reference matrix
for ri,q in enumerate(HQ):
    if q is not None: REF_POS[ri]=len(REF_POS)
N_REF=500
uniq_rs,_R=make_resampled_uniq(REF_SEQS,n_ref=N_REF,seed=20260731)
print(f"[uniqueness] reference population {len(REF_SEQS)} human responses; "
      f"{N_REF} redrawn at random for every score (seed 20260731)")

# ---------------- P4/P7: score DAT + between-unit on the SAME rows ----------------
out=[]; drops=Counter()
per=open("/home/user/fix/canonical_responses.csv","w",newline='')
slim=open("/home/user/fix/response_scores_machine.csv","w",newline='')
swtr=csv.writer(slim); swtr.writerow(["model_name","provider","intelligence","dat_score","between_unit_posaware","uniqueness_human_agnostic","uniqueness_fixed_pool_legacy"])
wtr=csv.writer(per); wtr.writerow(["model_name","provider","intelligence","region","reasoning",
  "release_date","date_precision"]+[f"noun_{i}" for i in range(10)]+["dat_score","between_unit_posaware","uniqueness_human_agnostic"])
for n,rows in resp.items():
    m=meta[n]; ds=f"{m['y']:04d}-{m['mo']:02d}-{m['d']:02d}"
    dv=[]; bv=[]; uv=[]; cv=[]
    for nouns in rows:
        a=dat(nouns); b=bpa(nouns); q=seq7(nouns); u=uniq_rs(q); uf=uniq(nouns)
        if a is None or b is None or u is None or q is None:
            drops[n]+=1; continue          # P7: explicit, symmetric drop
        dv.append(a); bv.append(b); uv.append(u); cv.append(q)
        wtr.writerow([n,m['prov'],m['intel'],m['reg'],m['reas'],ds,m['prec']]+list(nouns)+[f"{a:.6f}",f"{b:.6f}",f"{u:.6f}"])
        swtr.writerow([n,m['prov'],m['intel'],f"{a:.6f}",f"{b:.6f}",f"{u:.6f}",f"{uf:.6f}"])
    out.append(dict(model=n,prov=m['prov'],intel=m['intel'],y=m['y'],mo=m['mo'],d=m['d'],prec=m['prec'],
                    n=len(dv),dat=float(np.mean(dv)),btw=float(np.mean(bv)),uniq=float(np.mean(uv)),
                    dat_sd=float(np.std(dv,ddof=1)),btw_sd=float(np.std(bv,ddof=1)),uniq_sd=float(np.std(uv,ddof=1)),
                    _seqs=cv))
per.close(); slim.close()
print(f"[P4] DAT and between-unit now computed on identical rows for all {len(out)} models")
print(f"[P7] rows dropped for failing the 7-valid-noun rule: {sum(drops.values())} -> {dict(drops)}")

# ---------------- P5: one human baseline, same scorer ----------------
hd=[];hb=[];hu=[];hseq=[];hy=defaultdict(list);huy=defaultdict(list)
YR={'olson_pnas2021':2022,'zunyi':2024,'zunyi2024':2024,'btb':2025,'hsbc2025':2025}
hslim=open("/home/user/fix/response_scores_human.csv","w",newline='')
hwtr=csv.writer(hslim); hwtr.writerow(["row_index","source","year","dat_score","between_unit_posaware",
                                       "uniqueness_human_agnostic","uniqueness_fixed_pool_legacy",
                                       "in_reference_pool","matched"])
# ONE MATCHED HUMAN SAMPLE (2026-07-31). A response counts only if every measure can be
# computed on it, so the within-person and between-person figures compare exactly the same
# people. Two things changed here:
#  1. Pool-building rows are no longer excluded from the uniqueness baseline. The pool acts
#     only through its centroid of 5,000 word tokens, so a response contributes 7 tokens
#     (0.14%) to the yardstick it is measured against. Measured bias: the pool-building half
#     scores 80.567 against 80.620 for the held-out half, and scoring everyone moves the mean
#     by 0.026. Discarding half the human sample to avoid that was not a good trade.
#  2. All measures now use the same rows, so n is identical across figures.
for ri,r in enumerate(HROWS):
    nouns=[r[f'word_{i}'] for i in range(1,11)]
    a=dat(nouns); b=bpa(nouns); q=HQ[ri]
    u=uniq_rs(q,self_idx=REF_POS[ri]) if q is not None else None
    uf=uniq(nouns)
    keep = None not in (a,b,u,q)
    if keep:
        hd.append(a); hy[YR[r['source']]].append(a)
        hb.append(b)
        hu.append(u); huy[YR[r['source']]].append(u)
        hseq.append(q)
    hwtr.writerow([ri,r['source'],YR[r['source']],
                   "" if a is None else f"{a:.6f}", "" if b is None else f"{b:.6f}",
                   "" if u is None else f"{u:.6f}", "" if uf is None else f"{uf:.6f}",
                   int(ri in UREF_ROWS), int(keep)])
hslim.close()
human=dict(human_dat_mean=float(np.mean(hd)),human_between_mean=float(np.mean(hb)),
           human_uniq_mean=float(np.mean(hu)),n_dat=len(hd),n_btw=len(hb),n_uniq=len(hu),
           human_year={str(k):float(np.mean(v)) for k,v in sorted(hy.items())},
           human_uniq_year={str(k):float(np.mean(v)) for k,v in sorted(huy.items())})
print(f"[uniqueness] human-only position-agnostic baseline {human['human_uniq_mean']:.2f} "
      f"(n={len(hu)}, one matched human sample across all measures)")

# ---- churn: each population scored against ITSELF, then put on the DAT scale ----
h_churn_f=churn_scorer(hseq)
h_churn=np.array([v for v in (h_churn_f(q) for q in hseq) if v is not None])
m_seqs=[q for r in out for q in r['_seqs']]
m_churn_f=churn_scorer(m_seqs)
HC_M,HC_S=float(h_churn.mean()),float(h_churn.std(ddof=1))
DAT_M,DAT_S=float(np.mean(hd)),float(np.std(hd,ddof=1))
def to_dat_scale(v):        # match the HUMAN mean and sd to the human DAT distribution
    return DAT_M+((v-HC_M)/HC_S)*DAT_S
for r in out:
    vals=[m_churn_f(q) for q in r['_seqs']]
    vals=[v for v in vals if v is not None]
    r['churn_raw']=float(np.mean(vals)); r['churn']=to_dat_scale(r['churn_raw'])
    del r['_seqs']
m_churn=np.array([v for v in (m_churn_f(q) for q in m_seqs) if v is not None])
human['human_churn_raw']=HC_M
human['human_churn']=to_dat_scale(HC_M)
human['churn_calibration']={'human_raw_mean':HC_M,'human_raw_sd':HC_S,'dat_mean':DAT_M,'dat_sd':DAT_S}
print(f"[churn] own-population rarity, on the DAT scale: human {human['human_churn']:.2f} "
      f"(raw {HC_M:.4f}), machine {to_dat_scale(float(m_churn.mean())):.2f} (raw {m_churn.mean():.4f})")
print(f"[churn] distinct words used: human {len(set(w for q in hseq for w in q))}, "
      f"machine {len(set(w for q in m_seqs for w in q))}")
print(f"[P5] single human baseline: DAT {human['human_dat_mean']:.2f} (n={len(hd)}), between {human['human_between_mean']:.2f} (n={len(hb)})")

# ---------------- emit figure inputs ----------------
def frac(y,mo,d): return y+((mo-1)*30.44+d)/365.0
recs_d=[[frac(r['y'],r['mo'],r['d']),r['y'],r['mo'],r['d'],r['prov'],r['intel'],r['model'],r['dat'],r['prec']] for r in out]
recs_b=[[frac(r['y'],r['mo'],r['d']),r['y'],r['mo'],r['d'],r['prov'],r['intel'],r['model'],r['btw'],r['prec']] for r in out]
recs_u=[[frac(r['y'],r['mo'],r['d']),r['y'],r['mo'],r['d'],r['prov'],r['intel'],r['model'],r['uniq'],r['prec']] for r in out]
recs_c=[[frac(r['y'],r['mo'],r['d']),r['y'],r['mo'],r['d'],r['prov'],r['intel'],r['model'],r['churn'],r['prec']] for r in out]
hyr={str(k):v for k,v in human['human_year'].items()}
json.dump({"recs":recs_d,"human_year":hyr},open("/home/user/fix/permonth_data.json","w"))
json.dump({"recs":recs_b,"human_year":hyr},open("/home/user/fix/between_data.json","w"))
json.dump({"recs":recs_u,"human_year":{str(k):v for k,v in human['human_uniq_year'].items()}},
          open("/home/user/fix/uniqueness_data.json","w"))
json.dump({"recs":recs_c,"human_year":{}},open("/home/user/fix/churn_data.json","w"))
json.dump({"human_dat_mean":human['human_dat_mean'],"human_between_mean":human['human_between_mean'],
           "human_uniq_mean":human['human_uniq_mean'],"human_churn_mean":human['human_churn'],
           "churn_calibration":human['churn_calibration']},
          open("/home/user/fix/human_avg.json","w"))
json.dump(human,open("/home/user/fix/human_baselines_canonical.json","w"),indent=1)
json.dump(sorted(out,key=lambda r:-r['dat']),open("/home/user/fix/model_summary.json","w"),indent=1)
print(f"\nmodels={len(out)}  total scored responses={sum(r['n'] for r in out)}")
print(f"{'model':22}{'n':>6}{'DAT':>8}{'BTW':>8}  released")
for r in sorted(out,key=lambda r:-r['dat']):
    print(f"{r['model'][:21]:22}{r['n']:>6}{r['dat']:>8.2f}{r['btw']:>8.2f}  {r['y']}-{r['mo']:02d}-{r['d']:02d}")
