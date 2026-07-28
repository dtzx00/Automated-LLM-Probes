import csv, os, json, pickle, datetime, re, itertools, sys
import numpy as np, scipy.spatial.distance as ssd
from collections import defaultdict
csv.field_size_limit(10**9)
ROOT="/home/user/cn"
BASE=f"{ROOT}/machine_data/processed/machine_final_baseline_midpoint.csv"   # committed dat_score per row
MERGED=f"{ROOT}/machine_data/processed/machine_all_merged.csv"               # committed between_unit_posaware + metadata
HUMAN=f"{ROOT}/human_data/processed/human_dat_all.csv"
K3=f"{ROOT}/machine_data/raw_reasoning/topup_moonshot_k3.csv"
REFDIR=f"{ROOT}/machine_data/between_unit_references"
V=pickle.load(open("/home/user/repro/models/glove_olson.pickle","rb"))

# ---- Olson DAT ----
def validate(word):
    clean=re.sub(r"[^a-zA-Z- ]+","",word).strip().lower()
    if len(clean)<=1: return None
    cands=[re.sub(r" +","-",clean),re.sub(r" +","",clean)] if " " in clean else [clean]+([re.sub(r"-+","",clean)] if "-" in clean else [])
    for c in cands:
        if c in V: return c
    return None
def dat(words,minimum=7):
    u=[]
    for w in words:
        v=validate(w)
        if v and v not in u: u.append(v)
    if len(u)<minimum: return None
    sub=u[:minimum]
    return sum(ssd.cosine(V[a],V[b]) for a,b in itertools.combinations(sub,2))/(minimum*(minimum-1)/2)*100

# ---- between-unit posaware ----
_norm={}
def nvec(w):
    v=_norm.get(w)
    if v is None:
        raw=V.get(w)
        if raw is None: return None
        v=np.asarray(raw,float); v=v/(np.linalg.norm(v)+1e-12); _norm[w]=v
    return v
def cln(w):
    c=re.sub(r'[^a-zA-Z- ]+','',str(w)).strip().lower()
    return c if (c and len(c.split(' '))==1 and c in V) else None
refm=[np.vstack([nvec(w) for w in (x.strip() for x in open(f"{REFDIR}/rank{k}_ref.txt")) if w and nvec(w) is not None]) for k in range(1,8)]
fc=[dict() for _ in range(7)]
def fs(c,k):
    s=fc[k].get(c)
    if s is None: s=float(np.mean(1-(refm[k]@nvec(c))))*100; fc[k][c]=s
    return s
def bpa(cells):
    seq=[]
    for w in cells:
        c=cln(w)
        if c: seq.append(c)
        if len(seq)==7: break
    if len(seq)<7: return None
    return float(np.mean([fs(c,k) for k,c in enumerate(seq)]))

def frac_year(y,m,d):
    doy=datetime.date(y,m,d).timetuple().tm_yday
    nd=366 if (y%4==0 and (y%100!=0 or y%400==0)) else 365
    return y+(doy-0.5)/nd

# ---- metadata from merged (year/mo/day/provider/intelligence/precision) ----
info={}
for row in csv.DictReader(open(MERGED,encoding='utf-8-sig',errors='replace')):
    m=row['model_name']
    if m not in info:
        info[m]=(int(row['model_year']),int(row['model_month']),int(row['model_day']),row['provider'],row['intelligence'],row.get('date_precision','exact'))

# ---- DAT recs: committed dat_score per model (baseline-midpoint) ----
dat_by=defaultdict(list)
for row in csv.DictReader(open(BASE)):
    c=row.get("dat_score","")
    if c not in ("","None"): dat_by[row["model"]].append(float(c))
# ---- between recs: committed between_unit_posaware per model (merged) ----
btw_by=defaultdict(list)
for row in csv.DictReader(open(MERGED,encoding='utf-8-sig',errors='replace')):
    v=row.get("between_unit_posaware","")
    if v!="":
        try: btw_by[row['model_name']].append(float(v))
        except ValueError: pass

# ---- Kimi-K3 scored identically ----
NC=[f"noun_{i}" for i in range(10)]
k3d=[];k3b=[]
for row in csv.DictReader(open(K3)):
    if row['model_name']!='Kimi-K3': continue
    nouns=[row.get(c,"") for c in NC]
    ds=dat(nouns); bs=bpa(nouns)
    if ds is not None: k3d.append(ds)
    if bs is not None: k3b.append(bs)
dat_by['Kimi-K3']=k3d; btw_by['Kimi-K3']=k3b
info['Kimi-K3']=(2026,7,16,'moonshot','reasoning','exact')
print(f"K3 DAT n={len(k3d)} mean={np.mean(k3d):.2f} | between n={len(k3b)} mean={np.mean(k3b):.2f}")

def recs(by):
    out=[]
    for m,sc in by.items():
        if not sc or m not in info: continue
        y,mo,d,p,intel,prec=info[m]
        out.append([frac_year(y,mo,d),y,mo,d,p,intel,m,float(np.mean(sc)),prec])
    return out
dat_recs=recs(dat_by); btw_recs=recs(btw_by)

# ---- human baselines (Olson DAT + between) ----
SRC_YEAR={'olson_pnas2021':2022,'zunyi2024':2024,'hsbc2025':2025,'zunyi':2024,'btb':2025}
Hc=[f"word_{i}" for i in range(1,11)]
hyd=defaultdict(list); hyb=defaultdict(list); alld=[]; allb=[]
for row in csv.DictReader(open(HUMAN,encoding='utf-8-sig',errors='replace')):
    cells=[row.get(c,"") for c in Hc]
    ds=dat(cells); bs=bpa(cells)
    if ds is not None: alld.append(ds)
    if bs is not None: allb.append(bs)
    yy=SRC_YEAR.get(row.get('source',''))
    if yy:
        if ds is not None: hyd[yy].append(ds)
        if bs is not None: hyb[yy].append(bs)
hyd={y:float(np.mean(v)) for y,v in hyd.items()}; hyb={y:float(np.mean(v)) for y,v in hyb.items()}
print("human DAT year:",{k:round(v,2) for k,v in sorted(hyd.items())})
print("human grand DAT:",round(np.mean(alld),2),"between:",round(np.mean(allb),2))

json.dump({"recs":dat_recs,"human_year":hyd},open("/home/user/permonth_data.json","w"))
json.dump({"recs":btw_recs,"human_year":hyb},open("/home/user/between_data.json","w"))
json.dump({"human_dat_mean":float(np.mean(alld)),"human_between_mean":float(np.mean(allb))},open("/home/user/human_avg.json","w"))
print(f"dat_recs={len(dat_recs)} btw_recs={len(btw_recs)}")
