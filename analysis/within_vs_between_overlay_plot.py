import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib as mpl
mpl.rcParams.update({'font.size':16,'axes.titlesize':18,'axes.labelsize':18,'xtick.labelsize':15,'ytick.labelsize':15})
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.collections import LineCollection

# --- expanding x-transform: earlier years compact, later years broader ---
X0=2022.9  # anchor near earliest so compression bites
GAMMA=2.0  # >1 => later spans get more width
def tx(x): 
    import numpy as _np
    return _np.sign(x-X0)*(abs(x-X0)**GAMMA)

PROV_COLOR={'openai':'#10a37f','anthropic':'#d97757','qwen':'#9b30d0','deepseek':'#4d6bfe','moonshot':'#00b3a4','xai':'#333333','baidu':'#2932e1','meta':'#0866ff','minimax':'#e8590c','tencent':'#00a4a6'}
HUMAN_PURPLE='#5E348B'
MARK={'efficient':'v','all-rounder':'o','hybrid':'D','reasoning':'*'}; SIZE={'efficient':170,'all-rounder':190,'hybrid':150,'reasoning':320}

def load(fn):
    d=json.load(open(fn)); return {r[6]:r for r in d["recs"]}, {int(k):v for k,v in d["human_year"].items()}
dat,dat_hy=load("permonth_data.json")
btw,btw_hy=load("between_data.json")
models=[m for m in dat if m in btw]
allx=[dat[m][0] for m in models]; xmin=min(allx)-1/12; xmax=max(allx)+1/12

def grad_segments(x,y0,y1,c0,c1,n=40,a0=0.12,a1=0.75):
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

fig,ax=plt.subplots(figsize=(14,9))
GRAD_TO='#bcbcbc'  # fade toward grey at the between end
for m in models:
    x=dat[m][0]; p=dat[m][4]; intel=dat[m][5]
    yd=dat[m][7]; yb=btw[m][7]; col=PROV_COLOR.get(p,'#888')
    segs,cols=grad_segments(tx(x),yd,yb,col,GRAD_TO)
    ax.add_collection(LineCollection(segs,colors=cols,linewidths=4.2,zorder=3))
# markers on top: filled = DAT, open thick = between
for m in models:
    x=dat[m][0]; p=dat[m][4]; intel=dat[m][5]; col=PROV_COLOR.get(p,'#888')
    ax.scatter(tx(x),dat[m][7],marker=MARK[intel],s=SIZE[intel],color=col,alpha=0.65,zorder=6,edgecolors='white',linewidths=1.1)
    ax.scatter(tx(x),btw[m][7],marker=MARK[intel],s=SIZE[intel]*0.9,facecolors='white',edgecolors=col,linewidths=2.6,zorder=6)
# human baselines: DAT filled dashed, between open dashed
def human_line(hy,style,fillopen,line_alpha):
    hx=sorted(hy)
    ax.plot([tx(hx[0]),tx(hx[1])],[hy[hx[0]],hy[hx[1]]],':',color=HUMAN_PURPLE,lw=2.4,zorder=5,alpha=line_alpha)
    ax.plot([tx(2024),tx(2025)],[hy[2024],hy[2025]],'-',color=HUMAN_PURPLE,lw=2.4,zorder=5,alpha=line_alpha)
    ax.plot([tx(2025),tx(xmax)],[hy[2025],hy[2025]],'--',color=HUMAN_PURPLE,lw=2.4,zorder=5,alpha=line_alpha)
    for y in hx:
        if fillopen=='fill': ax.scatter(tx(y),hy[y],marker='o',s=210,color=HUMAN_PURPLE,alpha=0.65,zorder=7,edgecolors='white',linewidths=1.2)
        else: ax.scatter(tx(y),hy[y],marker='o',s=210,facecolors='white',edgecolors=HUMAN_PURPLE,linewidths=3,zorder=7)
human_line(dat_hy,'-','fill',0.65)   # DAT baseline: 35% transparent, matches its dots
human_line(btw_hy,'--','open',0.90)  # between-unit baseline: strong, matches white-fill dots
# --- Claude lineage connectors: link consecutive Claude models' existing points (no new numbers) ---
_claude=[m for m in dat if m.lower().startswith("claude") and m in btw]
_claude.sort(key=lambda m: dat[m][0])   # by release date
_ccol=PROV_COLOR['anthropic']
if len(_claude)>=2:
    _xs=[tx(dat[m][0]) for m in _claude]
    _yd=[dat[m][7] for m in _claude]     # DAT points
    _yb=[btw[m][7] for m in _claude]     # between-unit points
    ax.plot(_xs,_yd,'-',color=_ccol,lw=2.2,alpha=0.65,zorder=4)   # DAT lineage: 35% transparent (like human DAT)
    ax.plot(_xs,_yb,'-',color=_ccol,lw=2.2,alpha=0.90,zorder=4)   # between lineage: strong (like human between)
# human connectors: same gradient pattern as models (faded at DAT end -> strong at between end)
for _y in sorted(set(dat_hy)&set(btw_hy)):
    _segs,_cols=grad_segments(tx(_y),dat_hy[_y],btw_hy[_y],HUMAN_PURPLE,GRAD_TO)
    ax.add_collection(LineCollection(_segs,colors=_cols,linewidths=4.2,zorder=4))
ax.annotate("Human DAT",(tx(2025),dat_hy[2025]),textcoords="offset points",xytext=(8,-20),fontsize=13,weight='bold',color=HUMAN_PURPLE)
ax.annotate("Human between-unit",(tx(2025),btw_hy[2025]),textcoords="offset points",xytext=(8,10),fontsize=13,weight='bold',color=HUMAN_PURPLE)

ax.set_xlim(tx(xmin),tx(xmax))
_yr=[2023,2024,2025,2026]
ax.set_xticks([tx(y) for y in _yr]); ax.set_xticklabels([str(y) for y in _yr])
ax.set_xlabel("Release date (year, by day) / human collection year",fontsize=17)
ax.set_ylabel("Divergence score",fontsize=17)
ax.set_title("Within-person (filled) vs between-unit (open) divergence per model\ngradient links each model's two scores; purple = human baselines",fontsize=15,weight='bold')
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
prov_h=[Line2D([0],[0],marker='o',ls='none',color=PROV_COLOR.get(p,'#888'),ms=12,label=p) for p in provs]
intel_h=[Line2D([0],[0],marker=MARK[t],ls='none',color='#555',ms=13,label=t) for t in ['efficient','all-rounder','hybrid','reasoning']]
metric_h=[Line2D([0],[0],marker='o',ls='none',color='#555',ms=12,label='Within (DAT) = filled'),
          Line2D([0],[0],marker='o',ls='none',markerfacecolor='white',markeredgecolor='#555',markeredgewidth=2.4,ms=12,label='Between-unit = white fill'),
          Line2D([0],[0],color=HUMAN_PURPLE,lw=3,marker='o',ms=12,label='Human')]
handles=prov_h+intel_h+metric_h
ax.legend(handles=handles,loc='upper center',bbox_to_anchor=(0.5,-0.13),ncol=9,fontsize=10,framealpha=0.95,handletextpad=0.5,columnspacing=1.2,borderpad=0.8)
fig.tight_layout(rect=[0,0.02,1,1])
fig.savefig("/home/user/fig_overlay.png",dpi=220,bbox_inches='tight'); plt.close(fig)
print("done models",len(models))
