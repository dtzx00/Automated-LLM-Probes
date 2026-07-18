import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib as mpl
mpl.rcParams.update({'font.size':16,'axes.titlesize':18,'axes.labelsize':18,'xtick.labelsize':15,'ytick.labelsize':15})
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# --- same expanding x-transform ---
X0=2022.9; GAMMA=2.0
def tx(x):
    import numpy as _np
    return _np.sign(x-X0)*(abs(x-X0)**GAMMA)

PROV_COLOR={'openai':'#10a37f','anthropic':'#d97757','qwen':'#9b30d0','deepseek':'#4d6bfe','moonshot':'#00b3a4','xai':'#333333','baidu':'#2932e1','meta':'#0866ff','minimax':'#e8590c','tencent':'#00a4a6'}
PROV_LABEL={'openai':'OpenAI','anthropic':'Anthropic','qwen':'Qwen','deepseek':'DeepSeek','moonshot':'Moonshot','xai':'xAI','baidu':'Baidu','meta':'Meta','minimax':'MiniMax','tencent':'Tencent'}
HUMAN_PURPLE='#5E348B'
MARK={'efficient':'v','all-rounder':'o','hybrid':'D','reasoning':'*'}; SIZE={'efficient':170,'all-rounder':190,'hybrid':150,'reasoning':320}

def load(fn):
    d=json.load(open(fn)); return {r[6]:r for r in d["recs"]}, {int(k):v for k,v in d["human_year"].items()}
dat,dat_hy=load("permonth_data.json")
btw,btw_hy=load("between_data.json")
models=[m for m in dat if m in btw]   # same model set as combined fig
allx=[dat[m][0] for m in models]; xmin=min(allx)-3/12; xmax=max(allx)+0.2/12

fig,ax=plt.subplots(figsize=(16,9))
# markers: filled = DAT only
for m in models:
    x=dat[m][0]; p=dat[m][4]; intel=dat[m][5]; col=PROV_COLOR.get(p,'#888')
    ax.scatter(tx(x),dat[m][7],marker=MARK[intel],s=SIZE[intel],color=col,alpha=1.0,zorder=6,edgecolors='white',linewidths=1.1)

# human DAT baseline: single solid flat line (same as combined)
_havg=json.load(open("human_avg.json"))
HUMAN_DAT_AVG=_havg["human_dat_mean"]
_xL,_xR=tx(xmin),tx(xmax)
ax.plot([_xL,_xR],[HUMAN_DAT_AVG,HUMAN_DAT_AVG],'-',color=HUMAN_PURPLE,lw=2.4,alpha=1.0,zorder=5)
ax.annotate(f"Human DAT (avg {HUMAN_DAT_AVG:.1f})",(tx(2025-0.5/12),HUMAN_DAT_AVG),textcoords="offset points",xytext=(0,-14),ha='center',fontsize=12,weight='bold',color=HUMAN_PURPLE)

# lineage connectors: DAT solid @0.50 only (no between-unit, no shaded gap)
def _lineage_connectors(prefix, color):
    ms=[m for m in dat if m.lower().startswith(prefix) and m in btw]
    ms.sort(key=lambda m: dat[m][0])
    if len(ms)<2: return
    _xs=[tx(dat[m][0]) for m in ms]; _yd=[dat[m][7] for m in ms]
    ax.plot(_xs,_yd,'-',color=color,lw=2.2,alpha=1.0,zorder=4)
_lineage_connectors("claude", PROV_COLOR['anthropic'])
_lineage_connectors("gpt",    PROV_COLOR['openai'])

ax.set_xlim(tx(xmin),tx(xmax))
ax.set_ylim(70.6,86.3)   # pinned to match combined-figure autoscale (DAT min/max drive both)
_yr=[2023,2024,2025,2026]
ax.set_xticks([tx(y) for y in _yr]); ax.set_xticklabels([str(y) for y in _yr])
ax.set_xlabel("API release date (year, by day) / human collection year",fontsize=17)
ax.set_ylabel("Divergence score",fontsize=17)
ax.set_title("Within-Person (DAT) Divergence per Model\nFilled markers = model DAT; purple = human baseline",fontsize=15,weight='bold')
import numpy as _np
_months=[y+mn/12 for y in range(2023,2027) for mn in range(12)]
_months=[m for m in _months if xmin<=m<=xmax]
ax.set_xticks([tx(m) for m in _months],minor=True)
ax.grid(which='major',color='#dcdcdc',lw=1.0,zorder=0)
ax.grid(which='minor',axis='x',color='#f2f2f2',lw=0.6,zorder=0)
ax.set_axisbelow(True); ax.spines[['top','right']].set_visible(False)

# legend: providers + intelligence + human (no between-unit / gap entries)
provs=sorted({dat[m][4] for m in models})
prov_h=[Line2D([0],[0],marker='o',ls='none',color=PROV_COLOR.get(p,'#888'),ms=12,label=PROV_LABEL.get(p,p)) for p in provs]
INTEL_LABEL={'efficient':'Efficient','all-rounder':'All-rounder','hybrid':'Hybrid','reasoning':'Reasoning'}
intel_h=[Line2D([0],[0],marker=MARK[t],ls='none',color='#555',ms=13,label=INTEL_LABEL[t]) for t in ['efficient','all-rounder','hybrid','reasoning']]
metric_h=[Line2D([0],[0],marker='o',ls='none',color='#555',ms=12,label='Within (DAT) = filled'),
          Line2D([0],[0],color=HUMAN_PURPLE,lw=3,marker='o',ms=12,label='Human')]
handles=prov_h+intel_h+metric_h
ax.legend(handles=handles,loc='upper center',bbox_to_anchor=(0.5,-0.13),ncol=9,fontsize=10,framealpha=0.95,handletextpad=0.5,columnspacing=1.2,borderpad=0.8)
fig.tight_layout(rect=[0,0.02,1,1])
fig.savefig("/home/user/fig_dat_only.png",dpi=300,bbox_inches='tight'); plt.close(fig)
print("done models",len(models))
