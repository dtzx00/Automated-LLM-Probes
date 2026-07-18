import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib as mpl
mpl.rcParams.update({'font.size':16,'axes.titlesize':18,'axes.labelsize':18,'xtick.labelsize':15,'ytick.labelsize':15})
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.collections import LineCollection

# --- expanding x-transform: earlier years compact, later years broader ---
X0=2022.9  # anchor near earliest so compression bites
GAMMA=2.0  # >1 => later spans get more width
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
models=[m for m in dat if m in btw]
allx=[dat[m][0] for m in models]; xmin=min(allx)-3/12; xmax=max(allx)+0.2/12

def grad_segments(x,y0,y1,c0,c1,n=40,a0=0.50,a1=0.50):
    # y0 = DAT end (alpha a0=0.70, matches 30%-transparent DAT circle); y1 = between end (alpha a1, faded)
    ys=np.linspace(y0,y1,n+1); xs=np.full(n+1,x)
    pts=np.array([xs,ys]).T.reshape(-1,1,2)
    segs=np.concatenate([pts[:-1],pts[1:]],axis=1)
    c0=np.array(mpl.colors.to_rgb(c0)); c1=np.array(mpl.colors.to_rgb(c1))
    cols=[]
    for t in np.linspace(0,1,n):
        rgb=(1-t)*c0+t*c1
        a=(1-t)*a0+t*a1
        cols.append((rgb[0],rgb[1],rgb[2],a))
    return segs,cols

fig,ax=plt.subplots(figsize=(16,9))
GRAD_TO='#bcbcbc'  # fade toward grey at the between end
for m in models:
    x=dat[m][0]; p=dat[m][4]; intel=dat[m][5]
    yd=dat[m][7]; yb=btw[m][7]; col=PROV_COLOR.get(p,'#888')
    segs,cols=grad_segments(tx(x),yd,yb,col,GRAD_TO)
    ax.add_collection(LineCollection(segs,colors=cols,linewidths=4.2,zorder=3))
# markers on top: filled = DAT, open thick = between
for m in models:
    x=dat[m][0]; p=dat[m][4]; intel=dat[m][5]; col=PROV_COLOR.get(p,'#888')
    ax.scatter(tx(x),dat[m][7],marker=MARK[intel],s=SIZE[intel],color=col,alpha=0.50,zorder=6,edgecolors='white',linewidths=1.1)
    ax.scatter(tx(x),btw[m][7],marker=MARK[intel],s=SIZE[intel]*0.855,facecolors='white',edgecolors=col,linewidths=3.6,alpha=1.0,zorder=6)
# human baselines: two FLAT dotted horizontal lines at the pooled grand-mean scores
import json as _json
_havg=_json.load(open("human_avg.json"))
HUMAN_DAT_AVG=_havg["human_dat_mean"]        # pooled mean human DAT
HUMAN_BTW_AVG=_havg["human_between_mean"]     # pooled mean human between-unit
_xL,_xR=tx(xmin),tx(xmax)
ax.plot([_xL,_xR],[HUMAN_DAT_AVG,HUMAN_DAT_AVG],':',color=HUMAN_PURPLE,lw=2.4,alpha=0.50,zorder=5)
ax.plot([_xL,_xR],[HUMAN_BTW_AVG,HUMAN_BTW_AVG],':',color=HUMAN_PURPLE,lw=2.4,alpha=0.50,zorder=5)
ax.fill_between([_xL,_xR],[HUMAN_DAT_AVG]*2,[HUMAN_BTW_AVG]*2,color=HUMAN_PURPLE,alpha=0.10,zorder=2,linewidth=0)
ax.annotate(f"Human DAT (avg {HUMAN_DAT_AVG:.1f})",(tx(2025-0.5/12),HUMAN_DAT_AVG),textcoords="offset points",xytext=(0,-14),ha='center',fontsize=12,weight='bold',color=HUMAN_PURPLE)
ax.annotate(f"Human between-unit (avg {HUMAN_BTW_AVG:.1f})",(tx(2025-0.5/12),HUMAN_BTW_AVG),textcoords="offset points",xytext=(0,6),ha='center',fontsize=12,weight='bold',color=HUMAN_PURPLE)
# --- lineage horizontal connectors linking existing points (no new numbers) ---
def _lineage_connectors(prefix, color, shade=True):
    ms=[m for m in dat if m.lower().startswith(prefix) and m in btw]
    ms.sort(key=lambda m: dat[m][0])
    if len(ms)<2: return
    _xs=[tx(dat[m][0]) for m in ms]
    _yd=[dat[m][7] for m in ms]
    _yb=[btw[m][7] for m in ms]
    ax.plot(_xs,_yd,'-',color=color,lw=2.2,alpha=0.50,zorder=4)
    ax.plot(_xs,_yb,'-',color=color,lw=2.2,alpha=0.50,zorder=4)
    if shade:
        ax.fill_between(_xs,_yd,_yb,color=color,alpha=0.10,zorder=2,linewidth=0)
_lineage_connectors("claude", PROV_COLOR['anthropic'], shade=True)
_lineage_connectors("gpt",    PROV_COLOR['openai'], shade=True)

ax.set_xlim(tx(xmin),tx(xmax))
_yr=[2023,2024,2025,2026]
ax.set_xticks([tx(y) for y in _yr]); ax.set_xticklabels([str(y) for y in _yr])
ax.set_xlabel("API release date (year, by day) / human collection year",fontsize=17)
ax.set_ylabel("Divergence score",fontsize=17)
ax.set_title("Within-Person (Filled) vs Between-Unit (Open) Divergence per Model\nGradient links each model's two scores; purple = human baselines",fontsize=15,weight='bold')
# major year grid + light monthly minor grid (transformed positions)
import numpy as _np
_months=[y+mn/12 for y in range(2023,2027) for mn in range(12)]
_months=[m for m in _months if xmin<=m<=xmax]
ax.set_xticks([tx(m) for m in _months],minor=True)
ax.grid(which='major',color='#dcdcdc',lw=1.0,zorder=0)
ax.grid(which='minor',axis='x',color='#f2f2f2',lw=0.6,zorder=0)
ax.set_axisbelow(True); ax.spines[['top','right']].set_visible(False)

# legend: providers + intelligence + metric fill convention, OUTSIDE bottom, 6 columns
provs=sorted({dat[m][4] for m in models})
prov_h=[Line2D([0],[0],marker='o',ls='none',color=PROV_COLOR.get(p,'#888'),ms=12,label=PROV_LABEL.get(p,p)) for p in provs]
INTEL_LABEL={'efficient':'Efficient','all-rounder':'All-rounder','hybrid':'Hybrid','reasoning':'Reasoning'}
intel_h=[Line2D([0],[0],marker=MARK[t],ls='none',color='#555',ms=13,label=INTEL_LABEL[t]) for t in ['efficient','all-rounder','hybrid','reasoning']]
metric_h=[Line2D([0],[0],marker='o',ls='none',color='#555',ms=12,label='Within (DAT) = filled'),
          Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor='#555',markeredgewidth=2.4,ms=12,label='Between-unit = white fill'),
          Line2D([0],[0],color=HUMAN_PURPLE,lw=3,marker='o',ms=12,label='Human'),
          Patch(facecolor='#9a9a9a',alpha=0.20,edgecolor='none',label='Gap of scores')]
handles=prov_h+intel_h+metric_h
ax.legend(handles=handles,loc='upper center',bbox_to_anchor=(0.5,-0.13),ncol=9,fontsize=10,framealpha=0.95,handletextpad=0.5,columnspacing=1.2,borderpad=0.8)
fig.tight_layout(rect=[0,0.02,1,1])
fig.savefig("/home/user/fig_overlay.png",dpi=300,bbox_inches='tight'); plt.close(fig)
print("done models",len(models))
