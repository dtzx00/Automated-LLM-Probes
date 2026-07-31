"""Shared scorers for the creativity_networks analysis (Olson 2021 exact).

Single source of truth. build_overtime_data.py and the cross-section figures both import
from here, so a change to a measure cannot silently apply to one and not the other.

Call init(ROOT) once before using any scorer.
"""
import re, itertools, pickle
import numpy as np, scipy.spatial.distance as ssd
from collections import Counter

V = None; refm = None; _uc = None
_n = {}; _fc = None; _ucache = {}
GLOVE = "/home/user/repro/models/glove_olson.pickle"

def nvec(w):
    v = _n.get(w)
    if v is None:
        r = V.get(w)
        if r is None: return None
        v = np.asarray(r, float); v /= (np.linalg.norm(v) + 1e-12); _n[w] = v
    return v

def init(ROOT, glove=None):
    """Load GloVe and the reference pools. Returns the vector dict."""
    global V, refm, _uc, _fc
    V = pickle.load(open(glove or GLOVE, "rb"))
    REFD = f"{ROOT}/machine_data/between_unit_references"
    refm = [np.vstack([nvec(w) for w in (x.strip() for x in open(f"{REFD}/rank{k}_ref.txt"))
                       if w and nvec(w) is not None]) for k in range(1, 8)]
    _fc = [dict() for _ in range(7)]
    UPOOL = f"{REFD}/human_agnostic_5000words.txt"
    _uc = np.mean(np.vstack([nvec(w) for w in (x.strip() for x in open(UPOOL))
                             if w and nvec(w) is not None]), axis=0)
    return V

def validate(w):
    c = re.sub(r"[^a-zA-Z- ]+", "", str(w)).strip().lower()
    if len(c) <= 1: return None
    cands = [re.sub(r" +", "-", c), re.sub(r" +", "", c)] if " " in c else [c] + ([re.sub(r"-+", "", c)] if "-" in c else [])
    for x in cands:
        if x in V: return x
    return None

def dat(words, minimum=7):
    """WITHIN-person divergence: mean pairwise cosine distance among the first 7 valid unique words."""
    u = []
    for w in words:
        v = validate(w)
        if v and v not in u: u.append(v)
    if len(u) < minimum: return None
    s = u[:minimum]
    return sum(ssd.cosine(V[a], V[b]) for a, b in itertools.combinations(s, 2)) / (minimum * (minimum - 1) / 2) * 100

def cln(w):
    c = re.sub(r'[^a-zA-Z- ]+', '', str(w)).strip().lower()
    return c if (c and len(c.split(' ')) == 1 and c in V) else None

def seq7(cells):
    seq = []
    for w in cells:
        c = cln(w)
        if c: seq.append(c)
        if len(seq) == 7: break
    return seq if len(seq) == 7 else None

def _fs(c, k):
    s = _fc[k].get(c)
    if s is None: s = float(np.mean(1 - (refm[k] @ nvec(c)))) * 100; _fc[k][c] = s
    return s

def bpa(cells):
    """RETIRED between-person measure: 7 position-specific pools, each ~50% machine words.
    Kept for comparison only - it is not invariant to which models are in the dataset."""
    seq = seq7(cells)
    return float(np.mean([_fs(c, k) for k, c in enumerate(seq)])) if seq else None

def _us(c):
    s = _ucache.get(c)
    if s is None: s = 100 * (1 - float(_uc @ nvec(c))); _ucache[c] = s
    return s

def uniq(cells):
    """PRIMARY between-person measure: distance to ONE pool of 5,000 human-only word tokens,
    pooled across word positions. Human-only and position-agnostic by design (2026-07-29)."""
    seq = seq7(cells)
    return float(np.mean([_us(c) for c in seq])) if seq else None

def churn_scorer(word_sets):
    """Own-population rarity: -log10(share of own-population responses using the word)."""
    df = Counter()
    for ws in word_sets: df.update(set(ws))
    n = len(word_sets)
    def f(seq):
        return float(np.mean([-np.log10(max(df.get(c, 0), 0.5) / n) for c in seq])) if len(seq) == 7 else None
    return f
