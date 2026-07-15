"""run_collection.py — drive the full n=500 collection from model_id_mapping.csv.
Runs each collectable model (status starts with 'live'); groups by provider so we can parallelize
by launching one run_collection process per provider. Resumable: skips models already at target N
in data/raw/topup_<provider>.csv.
"""
import argparse, csv, subprocess, sys, collections
from pathlib import Path
HERE=Path(__file__).parent
def load_targets(mapping):
    rows=list(csv.DictReader(open(mapping)))
    out=[]
    for r in rows:
        st=(r.get("status") or "").lower()
        if st.startswith("live"):
            out.append(r)
    return out
def already(provider, model_name, out_dir):
    from pathlib import Path as _P
    f=_P(out_dir)/f"topup_{provider}.csv"
    if not f.exists(): return 0
    return sum(1 for r in csv.DictReader(open(f)) if r["model_name"]==model_name)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mapping",default=str(HERE/"models.csv"))
    ap.add_argument("--n",type=int,default=500)
    ap.add_argument("--provider",help="run only this provider (for parallelism)")
    ap.add_argument("--batch",default="collect_2026_midpoint")
    ap.add_argument("--out-dir",default=str(HERE/"raw"))
    a=ap.parse_args()
    targets=load_targets(a.mapping)
    if a.provider: targets=[t for t in targets if t["provider"]==a.provider]
    for t in targets:
        prov=t["provider"]; name=t["model"]; api=t["api_model_id"]
        have=already(prov,name,a.out_dir)
        need=a.n-have
        if need<=0:
            print(f"SKIP {name} ({prov}) already {have}"); continue
        print(f"RUN  {name} ({prov}) have={have} need={need}",flush=True)
        r=subprocess.run([sys.executable,str(HERE/"data_collection.py"),
            "--model",name,"--api-model",api,"--provider",prov,"--n",str(need),
            "--region",t.get("region",""),"--reasoning",t.get("reasoning",""),"--year",t.get("year",""),
            "--batch",a.batch,"--out-dir",a.out_dir])
        if r.returncode!=0: print(f"FAIL {name} ({prov}) rc={r.returncode}",flush=True)
    print(f"PROVIDER DONE: {a.provider or 'all'}",flush=True)
if __name__=="__main__": main()
