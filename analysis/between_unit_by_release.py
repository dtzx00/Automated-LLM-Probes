"""
Figure: Between-unit (between-person) divergence per model, by release date.
  x = model release date (year + day-of-year/365; human points at collection year)
  y = mean DAT (Olson 2021 GloVe scorer) per model
  color = model provider (developer brand)
  shape = intelligence class (efficient / all-rounder / hybrid / reasoning)
  thin lines = per-provider flagship evolution (date-ordered); purple = human baseline.

Inputs (repo-relative):
  machine_data/processed/machine_all_merged.csv   # nouns + model_year/month/day, provider, intelligence, date_precision
  human_data/processed/human_dat_all.csv          # word_dat_score + source

Requires a GloVe-backed DAT scorer. Set GLOVE_PICKLE to the validated GloVe model
(same one used across this repo; kept out of git as a large asset).
Run:  python analysis/model_dat_by_release.py
Out:  results/fig_model_dat_by_release.png
"""
import csv, os, sys, json, pickle, datetime
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict

csv.field_size_limit(10**9)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERGED = os.path.join(ROOT, "machine_data/processed/machine_all_merged.csv")
HUMAN  = os.path.join(ROOT, "human_data/processed/human_dat_all.csv")
OUT    = os.path.join(ROOT, "results/fig_between_unit_by_release.png")
GLOVE_PICKLE = os.environ.get("GLOVE_PICKLE", os.path.join(ROOT, "models/glove_validated.pickle"))

# ---- DAT scorer (Olson 2021): mean pairwise cosine distance of first 7 in-vocab words x100 ----
if not os.path.exists(GLOVE_PICKLE):
    sys.exit(f"GloVe model not found at {GLOVE_PICKLE}. Set GLOVE_PICKLE env var to the validated GloVe pickle.")
GLOVE = pickle.load(open(GLOVE_PICKLE, "rb"))
def _vec(w):
    return GLOVE.get(w.strip().lower()) if w else None
def dat_score(words, minimum=7):
    vs = []
    for w in words:
        v = _vec(w)
        if v is not None:
            vs.append(np.asarray(v, float))
        if len(vs) == minimum:
            break
    if len(vs) < minimum:
        return None
    d = []
    for i in range(len(vs)):
        for j in range(i+1, len(vs)):
            a, b = vs[i], vs[j]
            cos = float(np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b)))
            d.append(1.0 - cos)
    return float(np.mean(d))*100.0

def frac_year(y, m, d):
    doy = datetime.date(y, m, d).timetuple().tm_yday
    ndays = 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365
    return y + (doy - 0.5)/ndays

# ---- load machine, score per model ----
by = defaultdict(list); info = {}
with open(MERGED, newline='', encoding='utf-8-sig', errors='replace') as f:
    for row in csv.DictReader(f):
        m = row['model_name']
        v = row.get('between_unit_posaware', '')
        if v != '':
            by[m].append(float(v))
        info[m] = (int(row['model_year']), int(row['model_month']), int(row['model_day']),
                   row['provider'], row['intelligence'], row['date_precision'])
recs = []
for m, sc in by.items():
    if not sc:
        continue
    y, mo, d, p, intel, prec = info[m]
    recs.append((frac_year(y, mo, d), y, mo, d, p, intel, m, float(np.mean(sc)), prec))

# ---- human yearly baseline (same position-aware metric, per-rank refs) ----
import re
REFDIR = os.path.join(ROOT, "machine_data/between_unit_references")
_norm = {}
def _get(w):
    return _norm.get(w)
# build normalized vectors lazily from GLOVE for reference words + human words
def _clean(w):
    c = re.sub(r'[^a-zA-Z- ]+', '', str(w)).strip().lower()
    return c if (c and len(c.split(' '))==1 and c in GLOVE) else None
def _nvec(w):
    v = _norm.get(w)
    if v is None:
        raw = GLOVE.get(w)
        if raw is None: return None
        v = np.asarray(raw, float); v = v/(np.linalg.norm(v)+1e-12); _norm[w]=v
    return v
K = 7
ref_mats = []
for k in range(1, K+1):
    words = [x.strip() for x in open(os.path.join(REFDIR, f"rank{k}_ref.txt")) if x.strip()]
    ref_mats.append(np.vstack([_nvec(w) for w in words]))
_fc = [dict() for _ in range(K)]
def _fscore(c, k):
    s = _fc[k].get(c)
    if s is None:
        s = float(np.mean(1.0 - (ref_mats[k] @ _nvec(c))))*100.0; _fc[k][c]=s
    return s
def _rscore(cells):
    seq = []
    for w in cells:
        c = _clean(w)
        if c: seq.append(c)
        if len(seq)==7: break
    if len(seq)<7: return None
    return float(np.mean([_fscore(c,k) for k,c in enumerate(seq)]))
SRC_YEAR = {'olson_pnas2021':2022, 'zunyi2024':2024, 'hsbc2025':2025, 'zunyi':2024, 'btb':2025}
Hcols = [f"word_{i}" for i in range(1,11)]
hy = defaultdict(list)
with open(HUMAN, newline='', encoding='utf-8-sig', errors='replace') as f:
    for row in csv.DictReader(f):
        yy = SRC_YEAR.get(row.get('source',''))
        if not yy: continue
        s = _rscore([row.get(c,"") for c in Hcols])
        if s is not None: hy[yy].append(s)
hy = {y: float(np.mean(v)) for y, v in hy.items()}

# ---- plot ----
mpl.rcParams.update({'font.size':16,'axes.titlesize':20,'axes.labelsize':18,
                     'xtick.labelsize':15,'ytick.labelsize':15,'legend.fontsize':13,'legend.title_fontsize':14})
rbm = {r[6]: r for r in recs}
PROV_COLOR = {'openai':'#10a37f','anthropic':'#d97757','qwen':'#9b30d0','deepseek':'#4d6bfe',
              'moonshot':'#00b3a4','xai':'#333333','baidu':'#2932e1','meta':'#0866ff',
              'minimax':'#e8590c','tencent':'#00a4a6'}
HUMAN_PURPLE = '#5E348B'
MARK = {'efficient':'v','all-rounder':'o','hybrid':'D','reasoning':'*'}
SIZE = {'efficient':170,'all-rounder':190,'hybrid':150,'reasoning':320}
LINEAGES = [
 ['GPT-3.5-Turbo','GPT-4.0-Turbo','GPT-4o','GPT-4.1','GPT-5','GPT-5.1','GPT-5.2','GPT-5.4','GPT-5.5'],
 ['Claude-3-Opus','Claude-3.5-Sonnet','Claude-Sonnet-4','Claude-Opus-4.1','Claude-Sonnet-4.5','Claude-Opus-4.5','Claude-Opus-4.7','Claude-Sonnet-4.6','Claude-Fable-5','Claude-Sonnet-5'],
 ['DeepSeek-Chat','DeepSeek-R1','DeepSeek-V3.2','DeepSeek-V4-Pro'],
 ['Qwen-Turbo','Qwen3-235B-Instruct','Qwen-Max','Qwen3.7-Max','Qwen3.5-Plus','Qwen4-Max'],
 ['Kimi-K2','Kimi-K2.5','Kimi-K2.6'],
 ['Llama-2-70b','Llama4-Maverick'],
 ['Grok-Code-Fast','Grok-4.3','Grok-4.20-reason','Grok-4.5'],
 ['MiniMax-M2.5','MiniMax-M2.7','MiniMax-M3'],
]
fig, ax = plt.subplots(figsize=(13, 8.2))
for chain in LINEAGES:
    pts = sorted([(rbm[m][0], rbm[m][7], rbm[m][4]) for m in chain if m in rbm], key=lambda z: z[0])
    if len(pts) >= 2:
        col = PROV_COLOR.get(pts[0][2], '#888')
        ax.plot([a for a,_,_ in pts], [b for _,b,_ in pts], '-', color=col, lw=2.4, alpha=0.33, zorder=3)
for fx, y, mo, dd, p, intel, m, mean, prec in recs:
    ax.scatter(fx, mean, marker=MARK[intel], s=SIZE[intel], color=PROV_COLOR.get(p, '#888'),
               alpha=0.95, zorder=5, edgecolors='white', linewidths=1.1)
hx = sorted(hy)
ax.plot([hx[0], hx[1]], [hy[hx[0]], hy[hx[1]]], ':', color=HUMAN_PURPLE, lw=4.5, zorder=6)
ax.plot([2024, 2025], [hy[2024], hy[2025]], '-', color=HUMAN_PURPLE, lw=4.5, zorder=6)
xmax = max(r[0] for r in recs) + 1/12
xmin = min(r[0] for r in recs) - 1/12
ax.plot([2025, xmax], [hy[2025], hy[2025]], '--', color=HUMAN_PURPLE, lw=4.5, zorder=6)
ax.plot(hx, [hy[y] for y in hx], 'o', color=HUMAN_PURPLE, ms=16, zorder=7, markeredgecolor='white', markeredgewidth=1)
for y in hx:
    ax.annotate(f"Human {hy[y]:.1f}", (y, hy[y]), textcoords="offset points", xytext=(0, -22),
                ha='center', fontsize=15, weight='bold', color=HUMAN_PURPLE)
ax.set_xticks([2023, 2024, 2025, 2026])
ax.set_xlabel("Release date (year, by day) / human collection year", fontsize=18)
ax.set_ylabel("Between-unit divergence (position-aware)", fontsize=18)
ax.set_title("Between-unit divergence per model by release date - provider (color) x intelligence (shape)\n"
             "lines join evolving families; purple = human baseline (plateau)", fontsize=13, weight='bold')
ax.grid(color='#ebebeb', lw=0.8, zorder=0); ax.set_axisbelow(True)
ax.spines[['top','right']].set_visible(False)
provs = sorted({r[4] for r in recs})
prov_h = [Line2D([0],[0], marker='o', ls='none', color=PROV_COLOR.get(p,'#888'), ms=14, label=p) for p in provs]
intel_h = [Line2D([0],[0], marker=MARK[t], ls='none', color='#555', ms=15, label=t)
           for t in ['efficient','all-rounder','hybrid','reasoning']]
base_h = [Line2D([0],[0], color=HUMAN_PURPLE, lw=3, marker='o', ms=14, label='Human')]
def blank(): return Line2D([0],[0], ls='none', marker='', label=' ')
hdr_p = Line2D([0],[0], ls='none', marker='', label=r'$\bf{Provider}$')
hdr_t = Line2D([0],[0], ls='none', marker='', label=r'$\bf{Intelligence}$')
col1 = [hdr_p] + prov_h[:5]; col2 = [blank()] + prov_h[5:]; col3 = [hdr_t] + intel_h + base_h
nrows = max(len(col1), len(col2), len(col3))
for c in (col1, col2, col3):
    while len(c) < nrows: c.append(blank())
ax.legend(handles=col1+col2+col3, loc='upper left', fontsize=12, framealpha=0.95,
          ncol=3, handletextpad=0.6, columnspacing=1.4, borderpad=0.8)
ax.set_xlim(xmin, xmax)
fig.tight_layout(); fig.savefig(OUT, dpi=300, bbox_inches='tight'); plt.close(fig)
print("wrote", OUT)
