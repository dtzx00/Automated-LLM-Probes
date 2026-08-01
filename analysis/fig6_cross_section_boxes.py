"""Cross-sectional comparison, one figure with two panels: all humans vs all LLM responses.

  results/fig6_cross_section_boxes.png
    left  - within-person divergence (DAT)
    right - between-person uniqueness

Styling is imported from overtime_style, not copied, so this cannot drift from the three
over-time figures: same 16:9 canvas, same outer margins, same grid, same spines, same title and
axis-label sizes. Reads the response-level scores written by build_overtime_data.py.

Env: FIG_BOX_YLIM (default "65,100"), FIG_BOX_YSTEP, FIG_NOTITLE / FIG_TITLE=0, FIG_OUT.
"""
import os, sys, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overtime_style import HUMAN_PURPLE, LBL_BOX, FIGSIZE, save, plt, NOTITLE, vmargins
from matplotlib.patches import Rectangle

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/verify"
DATA = os.environ.get("FIG_DATA", f"{ROOT}/analysis/data")
SHOW_TITLE = (not NOTITLE) and os.environ.get("FIG_TITLE", "1") == "1"
YLIM  = tuple(float(x) for x in os.environ.get("FIG_BOX_YLIM", "65,100").split(","))
YSTEP = float(os.environ.get("FIG_BOX_YSTEP", "5"))

MACHINE = "#3CB7B0"          # machine teal, as in every human-vs-machine figure

H = f"{DATA}/response_scores_human.csv"
M = f"{DATA}/response_scores_machine.csv"
N_MODELS = len({r['model_name'] for r in csv.DictReader(open(M))})
MATCHED = lambda r: r['matched'] == '1'

def col(path, field, where=None):
    out = []
    for r in csv.DictReader(open(path, newline='')):
        if where and not where(r): continue
        if r[field] != "": out.append(float(r[field]))
    return np.array(out)

def stats(v):
    q1, med, q3 = np.percentile(v, [25, 50, 75])
    p5, p95 = np.percentile(v, [5, 95])
    return dict(n=len(v), mean=v.mean(), sd=v.std(ddof=1), med=med, q1=q1, q3=q3,
                p5=p5, p95=p95, lo=v.min(), hi=v.max())

def box(ax, x, s, color, W=0.34):
    ylo, yhi = ax.get_ylim()
    lo, hi = max(s['lo'], ylo), min(s['hi'], yhi)
    ax.plot([x, x], [lo, hi], color=color, lw=1.8, alpha=0.32, zorder=2)
    for y, true_v in ((lo, s['lo']), (hi, s['hi'])):
        if true_v < ylo or true_v > yhi:      # range continues past the axis
            ax.scatter([x], [y], marker='v' if true_v < ylo else '^', s=95, color=color,
                       alpha=0.55, zorder=3, clip_on=False)
            ax.annotate(("min " if true_v < ylo else "max ") + f"{true_v:.1f}", xy=(x, y),
                        textcoords="offset points", xytext=(11, 13 if true_v < ylo else -13),
                        ha='left', va='bottom' if true_v < ylo else 'top', fontsize=13,
                        color=color, alpha=0.9, bbox=LBL_BOX, zorder=9)
        else:
            ax.plot([x - 0.048, x + 0.048], [y, y], color=color, lw=1.8, alpha=0.32, zorder=2)
    ax.plot([x, x], [s['p5'], s['q1']], color=color, lw=2.8, zorder=3)
    ax.plot([x, x], [s['q3'], s['p95']], color=color, lw=2.8, zorder=3)
    for y in (s['p5'], s['p95']):
        ax.plot([x - 0.105, x + 0.105], [y, y], color=color, lw=2.8, zorder=3)
    ax.add_patch(Rectangle((x - W/2, s['q1']), W, s['q3'] - s['q1'], facecolor=color, alpha=0.20,
                           edgecolor=color, lw=2.8, zorder=4))
    ax.plot([x - W/2, x + W/2], [s['med']] * 2, color=color, lw=4.0, zorder=5)
    ax.scatter([x], [s['mean']], marker='D', s=175, facecolors='white', edgecolors=color,
               linewidths=2.8, zorder=6)

def panel(ax, hv, mv, ylab, label):
    hs, ms = stats(hv), stats(mv)
    ax.set_xlim(0.35, 2.65); ax.set_ylim(*YLIM)
    ax.set_yticks(np.arange(YLIM[0], YLIM[1] + 0.01, YSTEP))
    ax.grid(which='major', axis='y', color='#dcdcdc', lw=1.0, zorder=0)
    ax.set_axisbelow(True); ax.spines[['top', 'right']].set_visible(False)
    box(ax, 1.0, hs, HUMAN_PURPLE)
    box(ax, 2.0, ms, MACHINE)
    ax.set_xticks([1.0, 2.0])
    ax.set_xticklabels([f"Humans\n(n = {hs['n']:,})",
                        f"LLMs, {N_MODELS} models\n(n = {ms['n']:,})"], fontsize=16)
    ax.set_ylabel(ylab, fontsize=17)
    ax.set_title(label, fontsize=15, weight='bold')   # panel label always shown
    d = (ms['mean'] - hs['mean']) / np.sqrt(((hs['n']-1)*hs['sd']**2 + (ms['n']-1)*ms['sd']**2)
                                            / (hs['n']+ms['n']-2))
    print(f"  {label:26} human {hs['mean']:.2f}/{hs['sd']:.2f} n={hs['n']}   "
          f"machine {ms['mean']:.2f}/{ms['sd']:.2f} n={ms['n']}   d {d:+.3f}   "
          f"sd ratio {ms['sd']/hs['sd']:.3f}")

fig, axes = plt.subplots(1, 2, figsize=FIGSIZE)
_V = vmargins(top_in=1.305 if SHOW_TITLE else 0.585, bot_in=1.035)  # inches, so 16:7 crops the plot
fig.subplots_adjust(left=0.055, right=0.987, top=_V["top"], bottom=_V["bottom"], wspace=0.155)
if SHOW_TITLE:
    fig.suptitle("Divergence and Uniqueness: Humans vs LLMs\nBox = IQR; line = median; "
                 "diamond = mean; whiskers = 5th/95th percentile; thin line = full range",
                 fontsize=15, weight='bold', y=1-0.315/FIGSIZE[1])
panel(axes[0], col(H, 'dat_score', MATCHED), col(M, 'dat_score'),
      "Divergence score", "Within a response")
panel(axes[1], col(H, 'uniqueness_human_agnostic', MATCHED), col(M, 'uniqueness_human_agnostic'),
      "Uniqueness score", "Against the population")
save(fig, "fig6_cross_section_boxes.png")
