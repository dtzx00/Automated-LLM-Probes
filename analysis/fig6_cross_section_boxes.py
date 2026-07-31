"""Cross-sectional comparison, two groups only: all humans vs all LLM responses.

  results/fig6_box_within_person.png   within-person divergence (DAT)
  results/fig7_box_between_person.png  between-person uniqueness (human-only reference)

Reads the response-level scores written by build_overtime_data.py, so the measures can never
drift from the over-time figures. Env: FIG_TITLE=0 drops the in-figure title (decks set their
own headline); FIG_OUT overrides the output directory.
"""
import os, sys, csv
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/verify"
DATA = os.environ.get("FIG_DATA", f"{ROOT}/analysis/data")
OUT  = os.environ.get("FIG_OUT",  f"{ROOT}/results")
SHOW_TITLE = os.environ.get("FIG_TITLE", "1") == "1"
# One shared y range on both panels so the two measures are read on the same scale
# (set by Dawei 2026-07-31). The human DAT tail runs below 50, so any series whose range
# falls outside the window gets its true bound labelled at the axis rather than hidden.
BOX_YLIM = tuple(float(x) for x in os.environ.get("FIG_BOX_YLIM", "60,100").split(","))
BOX_YSTEP = float(os.environ.get("FIG_BOX_YSTEP", "5"))

HUMAN, MACHINE = "#5E348B", "#3CB7B0"        # human purple / machine teal
INK, MUTED, GRID = "#1a1420", "#6b6470", "#cccccc"

def col(path, field, where=None):
    out = []
    with open(path, newline='') as fh:
        for r in csv.DictReader(fh):
            if where and not where(r): continue
            v = r[field]
            if v != "": out.append(float(v))
    return np.array(out)

H = f"{DATA}/response_scores_human.csv"
M = f"{DATA}/response_scores_machine.csv"
n_models = len({r['model_name'] for r in csv.DictReader(open(M))})

def stats(v):
    q1, med, q3 = np.percentile(v, [25, 50, 75])
    p5, p95 = np.percentile(v, [5, 95])
    return dict(n=len(v), mean=v.mean(), sd=v.std(ddof=1), med=med, q1=q1, q3=q3,
                p5=p5, p95=p95, lo=v.min(), hi=v.max())

def box(ax, x, s, color, W=0.40):
    ylo, yhi = ax.get_ylim()
    lo, hi = max(s['lo'], ylo), min(s['hi'], yhi)
    ax.plot([x, x], [lo, hi], color=color, lw=1.7, alpha=0.32, zorder=2)
    for y, true_v, out in ((lo, s['lo'], s['lo'] < ylo), (hi, s['hi'], s['hi'] > yhi)):
        if out:      # range continues past the axis: caret plus the true bound
            ax.scatter([x], [y], marker='v' if true_v == s['lo'] else '^', s=95, color=color,
                       alpha=0.55, zorder=3, clip_on=False)
            ax.annotate(f"min {true_v:.1f}" if true_v == s['lo'] else f"max {true_v:.1f}",
                        xy=(x + 0.085, y), ha='left', va='center', fontsize=16.5,
                        color=color, alpha=0.85, zorder=7)
        else:
            ax.plot([x - 0.055, x + 0.055], [y, y], color=color, lw=1.7, alpha=0.32, zorder=2)
    ax.plot([x, x], [s['p5'], s['q1']], color=color, lw=2.7, zorder=3)
    ax.plot([x, x], [s['q3'], s['p95']], color=color, lw=2.7, zorder=3)
    for y in (s['p5'], s['p95']):
        ax.plot([x - 0.125, x + 0.125], [y, y], color=color, lw=2.7, zorder=3)
    ax.add_patch(Rectangle((x - W/2, s['q1']), W, s['q3'] - s['q1'], facecolor=color, alpha=0.20,
                           edgecolor=color, lw=2.7, zorder=4))
    ax.plot([x - W/2, x + W/2], [s['med']] * 2, color=color, lw=4.0, zorder=5)
    ax.scatter([x], [s['mean']], marker='D', s=170, facecolors='white', edgecolors=color,
               linewidths=2.7, zorder=6)

ROWS = [("responses", lambda s: f"{s['n']:,}"),
        ("mean",      lambda s: f"{s['mean']:.2f}"),
        ("SD",        lambda s: f"{s['sd']:.2f}"),
        ("median",    lambda s: f"{s['med']:.2f}"),
        ("IQR",       lambda s: f"{s['q1']:.1f}\u2013{s['q3']:.1f}"),
        ("5\u201395%",   lambda s: f"{s['p5']:.1f}\u2013{s['p95']:.1f}"),
        ("full range",lambda s: f"{s['lo']:.1f}\u2013{s['hi']:.1f}")]

def table(fig, hs, ms, d):
    ax = fig.add_axes([0.605, 0.135, 0.375, 0.735]); ax.axis('off')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    xl, xh, xm = 0.0, 0.55, 0.90
    ax.text(xh, 0.985, "Humans", ha='right', va='top', fontsize=21, color=HUMAN, weight='bold')
    ax.text(xm, 0.985, "LLMs",   ha='right', va='top', fontsize=21, color=MACHINE, weight='bold')
    ax.plot([xl, xm], [0.935, 0.935], color='#d5d0d8', lw=1.4)
    for i, (lab, f) in enumerate(ROWS):
        y = 0.855 - i * 0.108
        ax.text(xl, y, lab, ha='left', va='center', fontsize=19, color=MUTED)
        ax.text(xh, y, f(hs), ha='right', va='center', fontsize=21, color=HUMAN)
        ax.text(xm, y, f(ms), ha='right', va='center', fontsize=21, color=MACHINE)
    ax.plot([xl, xm], [0.055, 0.055], color='#d5d0d8', lw=1.4)
    ax.text(xl, -0.035, f"\u0394 mean {ms['mean']-hs['mean']:+.2f}     d {d:+.2f}     "
                        f"SD ratio {ms['sd']/hs['sd']:.2f}",
            ha='left', va='center', fontsize=20, color=INK)

def render(hv, mv, ylab, title, sub, fname):
    hs, ms = stats(hv), stats(mv)
    d = (ms['mean'] - hs['mean']) / np.sqrt(((hs['n']-1)*hs['sd']**2 + (ms['n']-1)*ms['sd']**2) / (hs['n']+ms['n']-2))
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_axes([0.088, 0.135, 0.45, 0.735])
    ax.set_ylim(*BOX_YLIM); ax.set_xlim(0.40, 2.60)
    ax.set_yticks(np.arange(BOX_YLIM[0], BOX_YLIM[1] + 0.01, BOX_YSTEP))
    ax.grid(axis='y', color=GRID, lw=0.7, alpha=0.8, zorder=0); ax.set_axisbelow(True)
    ax.axhline(hs['mean'], color=HUMAN, lw=1.6, ls=':', alpha=0.55, zorder=1)
    box(ax, 1.0, hs, HUMAN, W=0.50)
    box(ax, 2.0, ms, MACHINE, W=0.50)
    ax.set_xticks([1.0, 2.0]); ax.set_xticklabels(["Humans", "LLMs"], fontsize=25, color=INK)
    ax.tick_params(axis='x', length=0, pad=14)
    ax.tick_params(axis='y', labelsize=21, colors=MUTED)
    ax.set_ylabel(ylab, fontsize=24, color=INK, labelpad=17)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'): ax.spines[sp].set_color('#bbbbbb')
    table(fig, hs, ms, d)
    if SHOW_TITLE:
        fig.text(0.088, 0.945, title, fontsize=27, color=INK, ha='left', va='bottom')
        fig.text(0.088, 0.915, sub, fontsize=16, color=MUTED, ha='left', va='bottom')
    else:
        fig.text(0.088, 0.925, sub, fontsize=16, color=MUTED, ha='left', va='bottom')
    fig.savefig(f"{OUT}/{fname}", dpi=200, facecolor='white')
    plt.close(fig)
    print(f"{fname}: human mean {hs['mean']:.2f} sd {hs['sd']:.2f} range {hs['lo']:.1f}-{hs['hi']:.1f} | "
          f"machine mean {ms['mean']:.2f} sd {ms['sd']:.2f} range {ms['lo']:.1f}-{ms['hi']:.1f} | "
          f"d {d:+.3f} sd ratio {ms['sd']/hs['sd']:.3f}")

BOXNOTE = ("box = IQR  \u00b7  line = median  \u00b7  diamond = mean  \u00b7  "
           "whisker caps = 5th/95th percentile  \u00b7  thin line = full range")
MATCHED = lambda r: r['matched'] == '1'
render(col(H, 'dat_score', MATCHED), col(M, 'dat_score'), "Divergence score",
       "Within-person divergence", BOXNOTE, "fig6_box_within_person.png")
# both panels use the identical matched human sample
render(col(H, 'uniqueness_human_agnostic', MATCHED),
       col(M, 'uniqueness_human_agnostic'), "Uniqueness score",
       "Between-person uniqueness", BOXNOTE, "fig7_box_between_person.png")
