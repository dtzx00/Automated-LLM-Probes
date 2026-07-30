"""Shared styling + data loading for the three over-time figures.

One module so the three figures cannot drift apart. Conventions:
  within-person (DAT)  -> solid lines, FILLED provider-coloured markers
  between-person       -> dotted lines, OPEN thick provider-edged markers
Both figures share identical x and y limits so they are directly comparable.
"""
import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib as mpl
mpl.rcParams.update({'font.size':16,'axes.titlesize':18,'axes.labelsize':18,
                     'xtick.labelsize':15,'ytick.labelsize':15})
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch

# ---- x transform: expanding, so the crowded recent years get more room ----
X0=2022.9; GAMMA=2.0
def tx(x): return np.sign(np.asarray(x,dtype=float)-X0)*(abs(np.asarray(x,dtype=float)-X0)**GAMMA)

PROV_COLOR={'openai':'#10a37f','anthropic':'#d97757','qwen':'#9b30d0','deepseek':'#4d6bfe',
            'moonshot':'#00b3a4','xai':'#333333','baidu':'#2932e1','meta':'#0866ff',
            'minimax':'#e8590c','tencent':'#00a4a6'}
PROV_LABEL={'openai':'OpenAI','anthropic':'Anthropic','qwen':'Qwen','deepseek':'DeepSeek',
            'moonshot':'Moonshot','xai':'xAI','baidu':'Baidu','meta':'Meta',
            'minimax':'MiniMax','tencent':'Tencent'}
HUMAN_PURPLE='#5E348B'
BTW_LABEL='Human uniqueness'   # set by the figure script if a different measure is plotted
MARK={'efficient':'v','all-rounder':'o','hybrid':'D','reasoning':'*'}
SIZE={'efficient':170,'all-rounder':190,'hybrid':150,'reasoning':320}
INTEL_LABEL={'efficient':'Efficient','all-rounder':'All-rounder','hybrid':'Hybrid','reasoning':'Reasoning'}
LINEAGES=[("claude",PROV_COLOR['anthropic']),("gpt",PROV_COLOR['openai'])]  # OpenAI + Claude ONLY

DATA_DIR="data"
def _l(fn):
    j=json.load(open(f"{DATA_DIR}/{fn}")); return {r[6]:r for r in j["recs"]}

def load_all():
    """Legacy loader: DAT + the balanced half-machine per-rank between-person measure."""
    dat=_l("permonth_data.json"); btw=_l("between_data.json")
    hav=json.load(open(f"{DATA_DIR}/human_avg.json"))
    models=[m for m in dat if m in btw]
    models.sort(key=lambda m: dat[m][0])
    return dat,btw,hav["human_dat_mean"],hav["human_between_mean"],models

CHURN_YLIM=(55.5,87.0)   # churn spans 56.5-72.3 and must also show the DAT range 71.3-85.9
def load_uniq():
    """PRIMARY loader: DAT + uniqueness against a position-agnostic, HUMAN-ONLY reference.

    Design set 2026-07-29. The reference pool contains only human words and is pooled across
    word positions, so the measure is invariant to which models are in the dataset and means
    one thing: how unlike the human population a response is.
    """
    dat=_l("permonth_data.json"); uniq=_l("uniqueness_data.json")
    hav=json.load(open(f"{DATA_DIR}/human_avg.json"))
    models=[m for m in dat if m in uniq]
    models.sort(key=lambda m: dat[m][0])
    return dat,uniq,hav["human_dat_mean"],hav["human_uniq_mean"],models


def load_churn():
    """DAT + repetition/churn: rarity of a response's words within its OWN population.

    Each group is scored against itself (humans vs the human corpus, machines vs the pooled
    machine corpus), then put on the DAT scale by matching the human mean and sd. This is the
    only way a per-response score can see self-repetition.
    """
    dat=_l("permonth_data.json"); ch=_l("churn_data.json")
    hav=json.load(open(f"{DATA_DIR}/human_avg.json"))
    models=[m for m in dat if m in ch]
    models.sort(key=lambda m: dat[m][0])
    return dat,ch,hav["human_dat_mean"],hav["human_churn_mean"],models

# ---- SHARED AXES: identical on all three figures ----
def limits(dat,models):
    ax_=[dat[m][0] for m in models]
    return min(ax_)-2.6/12, max(ax_)+0.6/12
YLIM=(70.6,86.3)          # covers DAT 71.3-85.9 and uniqueness 77.0-83.4, plus both human baselines
FIGSIZE=(16,9); DPI=200   # saved WITHOUT tight bbox -> exactly 3200x1800 = true 16:9

def new_fig():
    fig,ax=plt.subplots(figsize=FIGSIZE)
    fig.subplots_adjust(left=0.055,right=0.987,top=0.902,bottom=0.185)
    return fig,ax

def frame(ax,xmin,xmax,title,ylim=None,ystep=2):
    ax.set_xlim(tx(xmin),tx(xmax)); ax.set_ylim(*(ylim or YLIM))
    yr=[2023,2024,2025,2026]
    ax.set_xticks([tx(y) for y in yr]); ax.set_xticklabels([str(y) for y in yr])
    months=[y+mn/12 for y in range(2023,2028) for mn in range(12)]
    ax.set_xticks([tx(m) for m in months if xmin<=m<=xmax],minor=True)
    lo,hi=(ylim or YLIM)
    ax.set_yticks(np.arange(int(np.ceil(lo/ystep))*ystep,hi,ystep))
    ax.grid(which='major',color='#dcdcdc',lw=1.0,zorder=0)
    ax.grid(which='minor',axis='x',color='#f2f2f2',lw=0.6,zorder=0)
    ax.set_axisbelow(True); ax.spines[['top','right']].set_visible(False)
    ax.set_xlabel("Model API release date (year, by month and day) / human collection year",fontsize=17)
    ax.set_ylabel("Divergence score",fontsize=17)
    ax.set_title(title,fontsize=15,weight='bold')

# ---- drawing primitives ----
def dat_markers(ax,dat,models,alpha):
    for m in models:
        i=dat[m][5]; c=PROV_COLOR.get(dat[m][4],'#888')
        ax.scatter(tx(dat[m][0]),dat[m][7],marker=MARK[i],s=SIZE[i],color=c,alpha=alpha,
                   edgecolors='white',linewidths=1.1,zorder=6)

def between_markers(ax,dat,btw,models):
    for m in models:
        i=dat[m][5]; c=PROV_COLOR.get(dat[m][4],'#888')
        ax.scatter(tx(dat[m][0]),btw[m][7],marker=MARK[i],s=SIZE[i]*0.855,facecolors='white',
                   edgecolors=c,linewidths=3.6,alpha=1.0,zorder=7)

def shift_arrows(ax,dat,btw,models):
    for m in models:
        c=PROV_COLOR.get(dat[m][4],'#888')
        ax.add_patch(FancyArrowPatch((tx(dat[m][0]),dat[m][7]),(tx(dat[m][0]),btw[m][7]),
                     arrowstyle='-|>',mutation_scale=17,color=c,alpha=0.50,lw=2.4,
                     shrinkA=9,shrinkB=9,zorder=4))

LBL_BOX=dict(facecolor='white',alpha=0.78,edgecolor='none',boxstyle='round,pad=0.25')
def human_lines(ax,xmin,xmax,h_dat,h_btw,show_dat,show_btw,dat_alpha=1.0,band=False,
                dat_label_x=2024.75,btw_label_x=2023.02,dat_label=None):
    xL,xR=tx(xmin),tx(xmax)
    if show_dat:
        ax.plot([xL,xR],[h_dat]*2,'-',color=HUMAN_PURPLE,lw=2.4,alpha=dat_alpha,zorder=5)
    if show_btw:
        ax.plot([xL,xR],[h_btw]*2,':',color=HUMAN_PURPLE,lw=2.4,alpha=1.0,zorder=5)
    if band and show_dat and show_btw:
        ax.fill_between([xL,xR],[h_dat]*2,[h_btw]*2,color=HUMAN_PURPLE,alpha=0.10,zorder=2,linewidth=0)
    if show_dat:
        ax.annotate(dat_label or f"Human DAT (avg {h_dat:.1f})",(tx(dat_label_x),h_dat),textcoords="offset points",
                    xytext=(0,-17),ha='center',fontsize=12,weight='bold',color=HUMAN_PURPLE,
                    bbox=LBL_BOX,zorder=9)
    if show_btw:
        ax.annotate(f"{BTW_LABEL} (avg {h_btw:.1f})",(tx(btw_label_x),h_btw),textcoords="offset points",
                    xytext=(2,9),ha='left',fontsize=12,weight='bold',color=HUMAN_PURPLE,
                    bbox=LBL_BOX,zorder=9)

def lineages(ax,dat,btw,models,mode):
    """mode: 'dat' | 'between' | 'both' (both adds the 10% gap shading)"""
    for prefix,color in LINEAGES:
        ms=[m for m in models if m.lower().startswith(prefix)]
        if len(ms)<2: continue
        xs=[tx(dat[m][0]) for m in ms]
        yd=[dat[m][7] for m in ms]; yb=[btw[m][7] for m in ms]
        if mode in ('dat','both'):
            ax.plot(xs,yd,'-',color=color,lw=2.2,alpha=0.50 if mode=='both' else 1.0,zorder=3)
        if mode in ('between','both'):
            ax.plot(xs,yb,':',color=color,lw=2.2,alpha=1.0,zorder=3)
        if mode=='both':
            ax.fill_between(xs,yd,yb,color=color,alpha=0.10,zorder=2,linewidth=0)

def legend(ax,dat,models,extra,open_style=False):
    provs=sorted({dat[m][4] for m in models})
    if open_style:
        ph=[Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor=PROV_COLOR.get(p,'#888'),
                   markeredgewidth=2.6,ms=12,label=PROV_LABEL.get(p,p)) for p in provs]
        ih=[Line2D([0],[0],marker=MARK[t],ls='none',markerfacecolor='white',markeredgecolor='#555',
                   markeredgewidth=2.2,ms=13,label=INTEL_LABEL[t]) for t in MARK]
    else:
        ph=[Line2D([0],[0],marker='o',ls='none',color=PROV_COLOR.get(p,'#888'),ms=12,
                   label=PROV_LABEL.get(p,p)) for p in provs]
        ih=[Line2D([0],[0],marker=MARK[t],ls='none',color='#555',ms=13,label=INTEL_LABEL[t]) for t in MARK]
    ax.legend(handles=ph+ih+extra,loc='upper center',bbox_to_anchor=(0.5,-0.125),ncol=10,
              fontsize=10,framealpha=0.95,handletextpad=0.5,columnspacing=1.2,borderpad=0.8)

def save(fig,path):
    fig.savefig(path,dpi=DPI)   # no bbox_inches -> canvas stays exactly 16:9
    plt.close(fig)
    from PIL import Image
    w,h=Image.open(path).size
    print(f"{path}  {w}x{h}  aspect {w/h:.4f}")
