"""Cross-sectional comparison, two groups only: all humans vs all LLM responses.

  results/fig6_box_within_person.png   within-person divergence (DAT)
  results/fig7_box_between_person.png  between-person uniqueness

Styling is imported from overtime_style, not copied, so these cannot drift from the three
over-time figures: same 16:9 canvas, same margins, same grid, same spines, same title and
label sizes, same human-baseline colour and label treatment. Per the measure convention the
human baseline is a SOLID line on the within-person figure and DOTTED on the between-person one.

Reads the response-level scores written by build_overtime_data.py.
Env: FIG_BOX_YLIM (default "65,100"), FIG_BOX_YSTEP, FIG_NOTITLE / FIG_TITLE=0, FIG_OUT.
"""
import os, sys, csv
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overtime_style import HUMAN_PURPLE, LBL_BOX, new_fig, save, plt, NOTITLE
from matplotlib.patches import Rectangle

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/verify"
DATA = os.environ.get("FIG_DATA", f"{ROOT}/analysis/data")
SHOW_TITLE = (not NOTITLE) and os.environ.get("FIG_TITLE", "1") == "1"
YLIM  = tuple(float(x) for x in os.environ.get("FIG_BOX_YLIM", "65,100").split(","))
YSTEP = float(os.environ.get("FIG_BOX_YSTEP", "5"))

MACHINE = "#3CB7B0"          # machine teal, as in every human-vs-machine figure
INK, MUTED = "#1a1420", "#6b6470"

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

def box(ax, x, s, color, W=0.30):
    ylo, yhi = ax.get_ylim()
    lo, hi = max(s['lo'], ylo), min(s['hi'], yhi)
    ax.plot([x, x], [lo, hi], color=color, lw=1.8, alpha=0.32, zorder=2)
    for y, true_v in ((lo, s['lo']), (hi, s['hi'])):
        outside = true_v < ylo or true_v > yhi
        if outside:
            ax.scatter([x], [y], marker='v' if true_v < ylo else '^', s=95, color=color,
                       alpha=0.55, zorder=3, clip_on=False)
            ax.annotate(("min " if true_v < ylo else "max ") + f"{true_v:.1f}", xy=(x, y),
                        textcoords="offset points", xytext=(11, 13 if true_v < ylo else -13),
                        ha='left', va='bottom' if true_v < ylo else 'top', fontsize=13,
                        color=color, alpha=0.9, bbox=LBL_BOX, zorder=9)
        else:
            ax.plot([x - 0.042, x + 0.042], [y, y], color=color, lw=1.8, alpha=0.32, zorder=2)
    ax.plot([x, x], [s['p5'], s['q1']], color=color, lw=2.8, zorder=3)
    ax.plot([x, x], [s['q3'], s['p95']], color=color, lw=2.8, zorder=3)
    for y in (s['p5'], s['p95']):
        ax.plot([x - 0.095, x + 0.095], [y, y], color=color, lw=2.8, zorder=3)
    ax.add_patch(Rectangle((x - W/2, s['q1']), W, s['q3'] - s['q1'], facecolor=color, alpha=0.20,
                           edgecolor=color, lw=2.8, zorder=4))
    ax.plot([x - W/2, x + W/2], [s['med']] * 2, color=color, lw=4.0, zorder=5)
    ax.scatter([x], [s['mean']], marker='D', s=175, facecolors='white', edgecolors=color,
               linewidths=2.8, zorder=6)

def line(label, s, color):
    return (f"{label}    n = {s['n']:,}     mean {s['mean']:.2f}     SD {s['sd']:.2f}     "
            f"median {s['med']:.2f}     IQR {s['q1']:.1f}\u2013{s['q3']:.1f}     "
            f"5\u201395% {s['p5']:.1f}\u2013{s['p95']:.1f}     "
            f"full range {s['lo']:.1f}\u2013{s['hi']:.1f}"), color

def render(hv, mv, ylab, head, sub, within, fname):
    hs, ms = stats(hv), stats(mv)
    d = (ms['mean'] - hs['mean']) / np.sqrt(((hs['n']-1)*hs['sd']**2 + (ms['n']-1)*ms['sd']**2)
                                            / (hs['n']+ms['n']-2))
    fig, ax = new_fig()
    ax.set_xlim(0.30, 2.70); ax.set_ylim(*YLIM)
    ax.set_yticks(np.arange(YLIM[0], YLIM[1] + 0.01, YSTEP))
    ax.grid(which='major', axis='y', color='#dcdcdc', lw=1.0, zorder=0)
    ax.set_axisbelow(True); ax.spines[['top', 'right']].set_visible(False)

    # human mean: solid for the within-person measure, dotted for between-person
    ax.plot([0.30, 2.70], [hs['mean']] * 2, '-' if within else ':', color=HUMAN_PURPLE,
            lw=2.4, zorder=5)
    ax.annotate(f"Human average {hs['mean']:.2f}", (2.62, hs['mean']), textcoords="offset points",
                xytext=(0, 11), ha='right', fontsize=12, weight='bold', color=HUMAN_PURPLE,
                bbox=LBL_BOX, zorder=9)

    box(ax, 1.0, hs, HUMAN_PURPLE)
    box(ax, 2.0, ms, MACHINE)
    ax.set_xticks([1.0, 2.0])
    ax.set_xticklabels(["Humans", f"LLMs ({N_MODELS} models)"], fontsize=17)
    ax.set_ylabel(ylab, fontsize=17)
    if SHOW_TITLE: ax.set_title(f"{head}\n{sub}", fontsize=15, weight='bold')

    for i, (txt, c) in enumerate([line("Humans", hs, HUMAN_PURPLE), line("LLMs  ", ms, MACHINE)]):
        fig.text(0.055, 0.115 - i * 0.048, txt, fontsize=13, color=c, ha='left', va='center')
    fig.text(0.055, 0.019, f"Difference    \u0394 mean {ms['mean']-hs['mean']:+.2f}     d {d:+.2f}"
             f"     SD ratio {ms['sd']/hs['sd']:.2f}", fontsize=13, color=INK, ha='left', va='center')
    save(fig, fname)
    print(f"{fname}: human {hs['mean']:.2f}/{hs['sd']:.2f} n={hs['n']}  "
          f"machine {ms['mean']:.2f}/{ms['sd']:.2f} n={ms['n']}  d {d:+.3f}  ratio {ms['sd']/hs['sd']:.3f}")

BOXNOTE = ("Box = IQR; line = median; diamond = mean; whiskers = 5th/95th percentile; "
           "thin line = full range")

render(col(H, 'dat_score', MATCHED), col(M, 'dat_score'),
       "Divergence score", "Within-Person Divergence: Humans vs LLMs", BOXNOTE,
       True, "fig6_box_within_person.png")

render(col(H, 'uniqueness_human_agnostic', MATCHED), col(M, 'uniqueness_human_agnostic'),
       "Uniqueness score", "Between-Person Uniqueness: Humans vs LLMs", BOXNOTE,
       False, "fig7_box_between_person.png")
