import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib as mpl
mpl.rcParams.update({'font.size':16,'axes.titlesize':18,'axes.labelsize':18,'xtick.labelsize':15,'ytick.labelsize':15})
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch

# --- same expanding x-transform as the other over-time figures ---
X0=2022.9; GAMMA=2.0
def tx(x):
    return np.sign(x-X0)*(abs(x-X0)**GAMMA)

PROV_COLOR={'openai':'#10a37f','anthropic':'#d97757','qwen':'#9b30d0','deepseek':'#4d6bfe','moonshot':'#00b3a4','xai':'#333333','baidu':'#2932e1','meta':'#0866ff','minimax':'#e8590c','tencent':'#00a4a6'}
PROV_LABEL={'openai':'OpenAI','anthropic':'Anthropic','qwen':'Qwen','deepseek':'DeepSeek','moonshot':'Moonshot','xai':'xAI','baidu':'Baidu','meta':'Meta','minimax':'MiniMax','tencent':'Tencent'}
HUMAN_PURPLE='#5E348B'
MARK={'efficient':'v','all-rounder':'o','hybrid':'D','reasoning':'*'}; SIZE={'efficient':170,'all-rounder':190,'hybrid':150,'reasoning':320}

def load(fn):
    d=json.load(open(fn)); return {r[6]:r for r in d["recs"]}, {int(k):v for k,v in d["human_year"].items()}
dat,dat_hy=load("data/permonth_data.json")
btw,btw_hy=load("data/between_data.json")
models=[m for m in dat if m in btw]   # same model set as the other two figures
allx=[dat[m][0] for m in models]; xmin=min(allx)-3/12; xmax=max(allx)+0.2/12

fig,ax=plt.subplots(figsize=(16,9))

# original DAT score as a transparent reference point (within-person convention: filled)
for m in models:
    x=dat[m][0]; p=dat[m][4]; intel=dat[m][5]; col=PROV_COLOR.get(p,'#888')
    ax.scatter(tx(x),dat[m][7],marker=MARK[intel],s=SIZE[intel],color=col,alpha=0.50,
               zorder=5,edgecolors='white',linewidths=1.1)

# arrow from the DAT score to the between-person score: direction = shifted up or down
for m in models:
    x=dat[m][0]; p=dat[m][4]; col=PROV_COLOR.get(p,'#888')
    yd=dat[m][7]; yb=btw[m][7]
    ax.add_patch(FancyArrowPatch((tx(x),yd),(tx(x),yb),arrowstyle='-|>',
                 mutation_scale=17,color=col,alpha=0.50,lw=2.4,
                 shrinkA=9,shrinkB=9,zorder=4,joinstyle='miter'))

# markers: BETWEEN-UNIT convention = open, thick provider-coloured border, alpha 1.0 (the emphasis)
for m in models:
    x=dat[m][0]; p=dat[m][4]; intel=dat[m][5]; col=PROV_COLOR.get(p,'#888')
    ax.scatter(tx(x),btw[m][7],marker=MARK[intel],s=SIZE[intel]*0.855,
               facecolors='white',edgecolors=col,linewidths=3.6,alpha=1.0,zorder=6)

# human between-person baseline: BETWEEN-UNIT convention = dotted, alpha 1.0
_havg=json.load(open("data/human_avg.json"))
HUMAN_BTW_AVG=_havg["human_between_mean"]
_xL,_xR=tx(xmin),tx(xmax)
HUMAN_DAT_AVG=_havg["human_dat_mean"]
ax.plot([_xL,_xR],[HUMAN_DAT_AVG,HUMAN_DAT_AVG],'-',color=HUMAN_PURPLE,lw=2.4,alpha=0.50,zorder=5)
ax.plot([_xL,_xR],[HUMAN_BTW_AVG,HUMAN_BTW_AVG],':',color=HUMAN_PURPLE,lw=2.4,alpha=1.0,zorder=5)
ax.fill_between([_xL,_xR],[HUMAN_DAT_AVG]*2,[HUMAN_BTW_AVG]*2,color=HUMAN_PURPLE,alpha=0.10,zorder=2,linewidth=0)
ax.annotate(f"Human DAT (avg {HUMAN_DAT_AVG:.1f})",(tx(2024.3),HUMAN_DAT_AVG),textcoords="offset points",xytext=(0,-14),ha='center',fontsize=12,weight='bold',color=HUMAN_PURPLE)
ax.annotate(f"Human between-person (avg {HUMAN_BTW_AVG:.1f})",(tx(2024.3),HUMAN_BTW_AVG),
            textcoords="offset points",xytext=(0,6),ha='center',fontsize=12,weight='bold',color=HUMAN_PURPLE)

# version-evolution lines: Claude + GPT only, BETWEEN-UNIT convention = dotted, alpha 1.0
def _lineage_connectors(prefix, color):
    ms=[m for m in dat if m.lower().startswith(prefix) and m in btw]
    ms.sort(key=lambda m: dat[m][0])
    if len(ms)<2: return
    _xs=[tx(dat[m][0]) for m in ms]
    _yd=[dat[m][7] for m in ms]; _yb=[btw[m][7] for m in ms]
    ax.plot(_xs,_yd,'-',color=color,lw=2.2,alpha=0.50,zorder=4)   # within = solid, transparent
    ax.plot(_xs,_yb,':',color=color,lw=2.2,alpha=1.0,zorder=4)    # between = dotted, opaque
    ax.fill_between(_xs,_yd,_yb,color=color,alpha=0.10,zorder=2,linewidth=0)  # gap shading
_lineage_connectors("claude", PROV_COLOR['anthropic'])
_lineage_connectors("gpt",    PROV_COLOR['openai'])

ax.set_xlim(tx(xmin),tx(xmax))
ax.set_ylim(70.6,86.3)   # shared with fig_within_dat_only: both measures now appear here
_yr=[2023,2024,2025,2026]
ax.set_xticks([tx(y) for y in _yr]); ax.set_xticklabels([str(y) for y in _yr])
ax.set_xlabel("API release date (year, by day) / human collection year",fontsize=17)
ax.set_ylabel("Divergence score",fontsize=17)
ax.set_title("Between-Person Divergence per Model\nOpen markers = between-person; transparent filled = original DAT; arrow = shift",fontsize=15,weight='bold')
_months=[y+mn/12 for y in range(2023,2027) for mn in range(12)]
_months=[m for m in _months if xmin<=m<=xmax]
ax.set_xticks([tx(m) for m in _months],minor=True)
ax.grid(which='major',color='#dcdcdc',lw=1.0,zorder=0)
ax.grid(which='minor',axis='x',color='#f2f2f2',lw=0.6,zorder=0)
ax.set_axisbelow(True); ax.spines[['top','right']].set_visible(False)

# legend: providers shown as open markers to match the plotted convention
provs=sorted({dat[m][4] for m in models})
prov_h=[Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor=PROV_COLOR.get(p,'#888'),
               markeredgewidth=2.6,ms=12,label=PROV_LABEL.get(p,p)) for p in provs]
INTEL_LABEL={'efficient':'Efficient','all-rounder':'All-rounder','hybrid':'Hybrid','reasoning':'Reasoning'}
intel_h=[Line2D([0],[0],marker=MARK[t],ls='none',markerfacecolor='white',markeredgecolor='#555',
                markeredgewidth=2.2,ms=13,label=INTEL_LABEL[t]) for t in ['efficient','all-rounder','hybrid','reasoning']]
metric_h=[Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor='#555',markeredgewidth=2.6,ms=12,label='Between-person = open'),
          Line2D([0],[0],marker='o',ls='none',color='#555',alpha=0.50,ms=12,label='Original DAT = filled'),
          Line2D([0],[0],color='#555',lw=2.4,alpha=0.50,label='Arrow = DAT to between'),
          Patch(facecolor='#555',alpha=0.10,label='Gap of scores'),
          Line2D([0],[0],color=HUMAN_PURPLE,lw=3,ls=':',marker='o',ms=12,label='Human')]
handles=prov_h+intel_h+metric_h
ax.legend(handles=handles,loc='upper center',bbox_to_anchor=(0.5,-0.13),ncol=9,fontsize=10,framealpha=0.95,handletextpad=0.5,columnspacing=1.2,borderpad=0.8)
fig.tight_layout(rect=[0,0.02,1,1])
fig.savefig("/home/user/fig_between_only.png",dpi=300,bbox_inches='tight'); plt.close(fig)
print("done models",len(models))
