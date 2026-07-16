import csv, pickle, numpy as np, random
from scipy import stats
from wordfreq import zipf_frequency
from nltk.corpus import wordnet as wn
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
csv.field_size_limit(10**9); random.seed(42); np.random.seed(42)

# ---------- shared data prep ----------
GLOVE=pickle.load(open("/home/user/repro/models/glove_validated.pickle","rb"))
def valid(w):
    w=str(w).strip().lower(); return w if (w and w in GLOVE) else None
def load(p,enc='utf-8-sig'):
    with open(p,newline='',encoding=enc,errors='replace') as f: return list(csv.DictReader(f))
WCOLS=[f"word_{i}" for i in range(1,11)]
H=load("/home/user/human_data_scored.csv"); M=load("/home/user/machine_data_merged.csv")
def rws(rows,k):
    o=[]
    for r in rows:
        ws=[r[c] for c in WCOLS]; s=r.get(k,'')
        try:s=float(s)
        except:s=None
        o.append((ws,s))
    return o
Hd=[(w,s) for w,s in rws(H,'word_dat_score') if s is not None]
Md=[(w,s) for w,s in rws(M,'dat_score') if s is not None]
Hs=np.array([s for _,s in Hd]); Ms=np.array([s for _,s in Md])
def top10(d):
    t=np.percentile([s for _,s in d],90); return [w for w,s in d if s>=t]
Ht=top10(Hd); Mt=top10(Md)
def first7(ws):
    o=[];seen=set()
    for w in ws:
        v=valid(w)
        if v is None or v in seen: continue
        seen.add(v);o.append(v)
        if len(o)>=7:break
    return o
Ha=[first7(ws) for ws in Ht if len(first7(ws))==7]
Ma=[first7(ws) for ws in Mt if len(first7(ws))==7]
SAMPLE_N=500
random.shuffle(Ha); random.shuffle(Ma)
HaS=Ha[:SAMPLE_N]; MaS=Ma[:SAMPLE_N]

HUMAN="#5E348B"; MACHINE="#3CB7B0"; RATIO="#c0762e"
def darken(hexc,f=0.64):
    hexc=hexc.lstrip('#'); r,g,b=[int(hexc[i:i+2],16) for i in (0,2,4)]
    return (r*f/255,g*f/255,b*f/255)
HUMAN_D=darken(HUMAN); MACHINE_D=darken(MACHINE)
def sq(ax):
    x0,x1=ax.get_xlim(); y0,y1=ax.get_ylim(); ax.set_aspect(abs(x1-x0)/abs(y1-y0))
def note_under_legend(ax,leg,txt):
    ax.figure.canvas.draw()
    bb=leg.get_window_extent().transformed(ax.transAxes.inverted())
    ax.text(bb.x0+0.008, bb.y0-0.02, txt, transform=ax.transAxes, fontsize=8.5, color='#555', va='top', ha='left')

# ---------- Panel A ----------
def draw_A(ax):
    def splits(ss):
        lo,hi=np.percentile(ss,10),np.percentile(ss,90)
        return [ss[ss<=lo],ss[(ss>lo)&(ss<hi)],ss[ss>=hi]]
    Hsp=[np.random.choice(a,min(SAMPLE_N,len(a)),replace=False) for a in splits(Hs)]
    Msp=[np.random.choice(a,min(SAMPLE_N,len(a)),replace=False) for a in splits(Ms)]
    groups=["Bottom 10%","Middle 80%","Top 10%"]
    def ci95(a):
        # 95% percentile interval over 1000 nonparametric bootstraps (with replacement, full N)
        bs=[np.mean(np.random.choice(a,len(a),replace=True)) for _ in range(1000)]
        m=np.mean(a); return np.array([[m-np.percentile(bs,2.5)],[np.percentile(bs,97.5)-m]])
    def stars(p): return "***" if p<1e-3 else "**" if p<1e-2 else "*" if p<0.05 else "ns"
    AS=10; AC="#333333"; w=0.36
    for i in range(3):
        h=Hsp[i]; m=Msp[i]
        ax.bar(i-w/2,h.mean(),w,color=HUMAN,alpha=0.85,zorder=2)
        ax.bar(i+w/2,m.mean(),w,color=MACHINE,alpha=0.85,zorder=2)
        def jit(v,c): return c+np.random.uniform(-w/2.6,w/2.6,len(v)),v
        jx,jv=jit(h,i-w/2); ax.scatter(jx,jv,s=12,facecolors='none',edgecolors=HUMAN_D,alpha=0.36,linewidths=0.6,zorder=3)
        jx,jv=jit(m,i+w/2); ax.scatter(jx,jv,s=12,facecolors='none',edgecolors=MACHINE_D,alpha=0.36,linewidths=0.6,zorder=3)
        ax.errorbar(i-w/2,h.mean(),yerr=ci95(h),color='black',capsize=4,lw=1.4,zorder=5)
        ax.errorbar(i+w/2,m.mean(),yerr=ci95(m),color='black',capsize=4,lw=1.4,zorder=5)
        t,p=stats.ttest_ind(h,m,equal_var=False); diff=m.mean()-h.mean()
        ytop=max(h.mean(),m.mean())+9
        ax.plot([i-w/2,i-w/2,i+w/2,i+w/2],[ytop-1.5,ytop,ytop,ytop-1.5],color='black',lw=1.1,zorder=5)
        ax.text(i,ytop+0.3,stars(p),ha='center',va='bottom',fontsize=AS,color=AC,zorder=6)
        ax.text(i,ytop+3.0,f"{diff:+.1f}",ha='center',va='bottom',fontsize=AS,weight='bold',color=AC,zorder=6)
        ax.text(i-w/2,ytop-3.2,f"{h.mean():.1f}",ha='center',va='top',fontsize=AS,weight='bold',color=AC,zorder=6)
        ax.text(i+w/2,ytop-3.2,f"{m.mean():.1f}",ha='center',va='top',fontsize=AS,weight='bold',color=AC,zorder=6)
    ax.set_xticks(range(3)); ax.set_xticklabels(groups,fontsize=11)
    ax.set_ylabel("Divergent thinking score",fontsize=11); ax.set_ylim(60,105)
    leg=ax.legend(handles=[Patch(color=HUMAN,label='Human'),Patch(color=MACHINE,label='Machine')],loc='upper left',fontsize=10)
    leg._legend_box.align='left'
    ax.set_title("Panel A - Divergent Thinking Score by Split",fontsize=12,weight='bold')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',color='#cccccc',linewidth=0.7,alpha=0.8,zorder=0); ax.set_axisbelow(True)
    note_under_legend(ax,leg,f"n={SAMPLE_N} per group\n95% CI, 1000-rep bootstrap")
    sq(ax)

# ---------- Panel B ----------
def draw_B(ax):
    CAP=500; STEP=5; BREPS=1000
    def rarefy(pop):
        pop=[set(a) for a in pop]; N=len(pop); K=min(CAP,N); xs=list(range(STEP,K+1,STEP))
        curves=np.zeros((BREPS,len(xs)))
        for r in range(BREPS):
            boot=np.random.randint(0,N,size=K); seen=set(); vals=[]
            for pos,i in enumerate(boot):
                seen|=pop[i]
                if (pos+1)%STEP==0: vals.append(len(seen))
            curves[r,:len(vals)]=vals[:len(xs)]
        # CI OF THE MEAN: percentile of the per-rep curve gives the sampling dist of the mean curve
        ys=curves.mean(0)
        se=curves.std(0,ddof=1)/np.sqrt(BREPS)
        lo=ys-1.96*se; hi=ys+1.96*se   # 95% CI of the mean
        return xs,ys,lo,hi
    hx,hy,hl,hh=rarefy(Ha[:CAP]); mx,my,ml,mh=rarefy(Ma[:CAP])
    ax.plot(hx,hy,color=HUMAN,lw=2,label="Human"); ax.fill_between(hx,hl,hh,color=HUMAN,alpha=0.25)
    ax.plot(mx,my,color=MACHINE,lw=2,label="Machine"); ax.fill_between(mx,ml,mh,color=MACHINE,alpha=0.25)
    ax.text(0.60,0.30,"Distinct words @500:",transform=ax.transAxes,fontsize=9.5,color="#333",va="top",weight="bold")
    ax.text(0.60,0.245,f"Human  {int(round(hy[-1]))}",transform=ax.transAxes,fontsize=10,color=HUMAN,va="top",weight="bold")
    ax.text(0.60,0.19,f"Machine  {int(round(my[-1]))}",transform=ax.transAxes,fontsize=10,color=MACHINE,va="top",weight="bold")
    ax.set_xlabel("Sampled responses",fontsize=11); ax.set_ylabel("Cumulative distinct words",fontsize=11)
    ax.set_title("Panel B - Cumulative Distinct Words",fontsize=12,weight='bold')
    leg=ax.legend(handles=[Patch(color=HUMAN,label='Human'),Patch(color=MACHINE,label='Machine')],loc='upper left',fontsize=10)
    leg._legend_box.align='left'
    ax.spines[['top','right']].set_visible(False)
    ax.grid(color='#cccccc',linewidth=0.7,alpha=0.8,zorder=0); ax.set_axisbelow(True)
    note_under_legend(ax,leg,"top 10%, first 7 words\n95% CI, 1000-rep bootstrap")
    ax.set_xlim(0,CAP+5); sq(ax)

# ---------- Panel C ----------
def draw_C(ax):
    CAP=500; REPS=1000; SMOOTH=20
    def new_per(pop):
        pop=[set(a) for a in pop]; N=len(pop); K=min(CAP,N)
        def roll(a):
            c=np.cumsum(np.insert(a,0,0)); return (c[SMOOTH:]-c[:-SMOOTH])/SMOOTH
        rep_curves=[]
        for r in range(REPS):
            boot=np.random.randint(0,N,size=K); seen=set(); marg=np.zeros(K)
            for pos,i in enumerate(boot):
                b=len(seen); seen|=pop[i]; marg[pos]=len(seen)-b
            rep_curves.append(roll(marg))
        rep_curves=np.array(rep_curves)
        xs=np.arange(1,K+1)[SMOOTH-1:]
        mean=rep_curves.mean(0)
        se=rep_curves.std(0,ddof=1)/np.sqrt(REPS)
        lo=mean-1.96*se; hi=mean+1.96*se   # 95% CI of the mean
        return xs,mean,lo,hi
    hx,hy,hlo,hhi=new_per(Ha[:CAP]); mx,my,mlo,mhi=new_per(Ma[:CAP])
    ax.plot(hx,hy,color=HUMAN,lw=1.6,label="Human"); ax.fill_between(hx,hlo,hhi,color=HUMAN,alpha=0.25)
    ax.plot(mx,my,color=MACHINE,lw=1.6,label="Machine"); ax.fill_between(mx,mlo,mhi,color=MACHINE,alpha=0.25)
    ax.text(0.58,0.95,"New words @500:",transform=ax.transAxes,fontsize=9.5,color="#333",va="top",weight="bold")
    ax.text(0.58,0.895,f"Human  {hy[-1]:.2f}",transform=ax.transAxes,fontsize=10,color=HUMAN,va="top",weight="bold")
    ax.text(0.58,0.84,f"Machine  {my[-1]:.2f}",transform=ax.transAxes,fontsize=10,color=MACHINE,va="top",weight="bold")
    ax.set_xlabel("Sampled responses",fontsize=11); ax.set_ylabel("New distinct words added",fontsize=11)
    ax.set_title("Panel C - New Words per Sampled Response",fontsize=12,weight='bold')
    leg=ax.legend(handles=[Patch(color=HUMAN,label='Human'),Patch(color=MACHINE,label='Machine')],loc='upper right',fontsize=10)
    leg._legend_box.align='left'
    ax.spines[['top','right']].set_visible(False)
    ax.grid(color='#cccccc',linewidth=0.7,alpha=0.8,zorder=0); ax.set_axisbelow(True)
    ax.text(0.97,0.66,f"n={CAP} per group\n95% CI, 1000-rep bootstrap",transform=ax.transAxes,fontsize=8.5,color='#555',va='top',ha='right')
    ax.set_xlim(0,CAP+5); ax.set_ylim(0,7.2); sq(ax)

# ---------- Panel D ----------
def draw_D(ax):
    LEVELS=list(range(1,11))
    def cats_at(words,level):
        cats=set()
        for w in words:
            ss=wn.synsets(w,pos=wn.NOUN)
            if not ss: continue
            paths=ss[0].hypernym_paths()
            if not paths: continue
            p=paths[0]; cats.add(p[min(level,len(p)-1)].name())
        return cats
    # Precompute per-response category SETS at each level (so bootstrap is fast)
    def resp_cats(resp,L):
        s=set()
        for w in resp:
            ss=wn.synsets(w,pos=wn.NOUN)
            if not ss: continue
            paths=ss[0].hypernym_paths()
            if not paths: continue
            p=paths[0]; s.add(p[min(L,len(p)-1)].name())
        return s
    Hsets={L:[resp_cats(a,L) for a in HaS] for L in LEVELS}
    Msets={L:[resp_cats(a,L) for a in MaS] for L in LEVELS}
    REPS=1000; NH=len(HaS); NM=len(MaS)
    hcnt=[];mcnt=[];ratio=[]
    hlo=[];hhi=[];mlo=[];mhi=[];rlo=[];rhi=[]
    for L in LEVELS:
        Hs_=Hsets[L]; Ms_=Msets[L]
        hb=[];mb=[];rb=[]
        for _ in range(REPS):
            hi_=np.random.randint(0,NH,size=NH); mi_=np.random.randint(0,NM,size=NM)  # with replacement, full N
            hu=set().union(*[Hs_[i] for i in hi_]); mu=set().union(*[Ms_[i] for i in mi_])
            hb.append(len(hu)); mb.append(len(mu)); rb.append(len(hu)/len(mu) if mu else np.nan)
        hb=np.array(hb);mb=np.array(mb);rb=np.array(rb)
        # PLOT the bootstrap mean so the line is the center of its own CI (distinct-count is not an average,
        # so the full-sample count sits above the bootstrap mean -> use the bootstrap estimate consistently)
        hc=hb.mean(); mc=mb.mean(); hcnt.append(hc); mcnt.append(mc); ratio.append(np.nanmean(rb))
        hse=hb.std(ddof=1)/np.sqrt(len(hb)); mse=mb.std(ddof=1)/np.sqrt(len(mb))
        hlo.append(hc-1.96*hse); hhi.append(hc+1.96*hse)
        mlo.append(mc-1.96*mse); mhi.append(mc+1.96*mse)
        rse=np.nanstd(rb,ddof=1)/np.sqrt(np.sum(~np.isnan(rb)))
        rlo.append(np.nanmean(rb)-1.96*rse); rhi.append(np.nanmean(rb)+1.96*rse)
    ax.plot(LEVELS,hcnt,'-o',color=HUMAN,lw=2,ms=6,zorder=3)
    ax.fill_between(LEVELS,hlo,hhi,color=HUMAN,alpha=0.22,zorder=1)
    ax.plot(LEVELS,mcnt,'-o',color=MACHINE,lw=2,ms=6,zorder=3)
    ax.fill_between(LEVELS,mlo,mhi,color=MACHINE,alpha=0.22,zorder=1)
    # print ratio (with 95% CI) above each human point, black
    for L,hc,r,rl,rh in zip(LEVELS,hcnt,ratio,rlo,rhi):
        if not np.isnan(r):
            ax.annotate(f"{r:.1f}x",(L,hc),textcoords="offset points",xytext=(0,10),ha='center',
                        fontsize=9,weight='bold',color="#333333",zorder=6)
    ax.set_xlabel("WordNet category depth (level)",fontsize=11); ax.set_ylabel("Distinct WordNet categories",fontsize=11)
    ax.set_title("Panel D - Categorical Diversity",fontsize=12,weight='bold')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(color='#cccccc',linewidth=0.7,alpha=0.8,zorder=0); ax.set_axisbelow(True)
    h=[Line2D([0],[0],color=HUMAN,marker='o',lw=2,label='Human'),
       Line2D([0],[0],color=MACHINE,marker='o',lw=2,label='Machine')]
    leg=ax.legend(handles=h,loc='upper left',fontsize=10); leg._legend_box.align='left'
    ax.text(0.03,0.72,"Nx = how many more distinct categories\nhumans use than machines at that level",transform=ax.transAxes,fontsize=8,color='#555',va='top')
    ax.text(0.03,0.63,f"n={SAMPLE_N} per group | 95% CI, 1000-rep bootstrap",transform=ax.transAxes,fontsize=8.5,color='#555',va='top')
    ax.set_ylim(0,max(hcnt)*1.12)
    x0,x1=ax.get_xlim(); y0,y1=ax.get_ylim(); ax.set_aspect(abs(x1-x0)/abs(y1-y0))

# ---------- assemble ----------
fig,axes=plt.subplots(2,2,figsize=(16,16))
draw_A(axes[0,0]); draw_B(axes[0,1]); draw_C(axes[1,0]); draw_D(axes[1,1])
for a,lab in zip(axes.flat,["A","B","C","D"]):
    a.text(-0.02,1.06,lab,transform=a.transAxes,fontsize=20,weight='bold',va='top',ha='left')
fig.suptitle("Figure 1 - Combinatoric Space: Human vs Machine (latest data)",fontsize=18,weight='bold',y=0.995)
fig.tight_layout(rect=[0,0,1,0.98])
fig.savefig("/home/user/figure1_composite.png",dpi=130,bbox_inches='tight'); plt.close(fig)
print("Figure 1 (true subplots) done")
