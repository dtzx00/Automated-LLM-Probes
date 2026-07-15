# Human Word-Generation Trajectory (Brian's process analysis)

**Question:** not *how creative is the final set* (DAT score), but *how do people build the 10 words* —
does the sequence have structure, or is it order-random?

**Data:** `human_data/processed/human_dat_all.csv`, all cleaned individual-word responses with 7 valid
unique words. **N = 10,384** (PNAS + BTB + Zunyi pooled).

**Method (matches the machine-side panels):** three semantic-distance metrics along each response's
word sequence, each compared to a **per-response order-shuffled permutation null** (200 shuffles of
that response's own 7 words; 95% CI). Distances are cosine on the project GloVe embedding.
- **A — Diffusion:** anchor (word 1) → word j. Labels 1→2 … 1→7.
- **B — Adjacent:** word k → word k+1. Labels 1→2 … 6→7.
- **C — Stepwise:** word k → centroid of all prior words. Steps 2 … 7. (Null declines mechanically —
  each added word grows the prior-set centroid.)

Figure: `results/human_trajectory_3panel.png`.

## The human finding — a warm-up-then-diverge path, NOT a flat cloud
With the full pooled sample (vs the earlier n=302 machine bars), the human sequence shows real,
significant order structure:

- **Early words sit BELOW null.** The first few words a person writes are *closer together* than
  shuffling their own words predicts (diffusion 1→2 = 0.756 vs null 0.787; adjacent 1→2, 2→3, 3→4 all
  below). People **start local** — an initial associatively-linked cluster.
- **Later words rise to and ABOVE null.** By the end of the list they place words *farther* than
  random ordering would (diffusion 1→7 = 0.790 > null; adjacent 6→7 = 0.791 > null; stepwise steps
  5, 6, 7 all above their declining null). People **push outward** as they go, adding genuinely new
  directions late.

So the human process is a **trajectory**: begin near the anchor, then diverge — semantic distance
*grows* across the sequence relative to the order-random baseline. This revises the earlier
small-sample read ("humans ≈ null = order-irrelevant cloud"): at full N the human order is clearly
non-random, with a consistent early-tight / late-wide shape across all three metrics.

## A — Diffusion (anchor → word j)
| step | observed | null | 95% CI | vs null |
|---|---|---|---|---|
| 1→2 | 0.7558 | 0.7870 | [0.7852, 0.7888] | **below** |
| 1→3 | 0.7766 | 0.7869 | [0.7850, 0.7888] | **below** |
| 1→4 | 0.7806 | 0.7871 | [0.7854, 0.7891] | **below** |
| 1→5 | 0.7857 | 0.7870 | [0.7849, 0.7892] | inside |
| 1→6 | 0.7884 | 0.7871 | [0.7850, 0.7890] | inside |
| 1→7 | 0.7901 | 0.7870 | [0.7850, 0.7889] | **above** |

## B — Adjacent (word k → k+1)
| step | observed | null | 95% CI | vs null |
|---|---|---|---|---|
| 1→2 | 0.7558 | 0.7870 | [0.7852, 0.7888] | **below** |
| 2→3 | 0.7770 | 0.7870 | [0.7854, 0.7890] | **below** |
| 3→4 | 0.7766 | 0.7870 | [0.7851, 0.7891] | **below** |
| 4→5 | 0.7846 | 0.7871 | [0.7851, 0.7891] | **below** |
| 5→6 | 0.7828 | 0.7871 | [0.7847, 0.7888] | **below** |
| 6→7 | 0.7913 | 0.7871 | [0.7854, 0.7892] | **above** |

## C — Stepwise (word k → centroid of prior words)
| step | observed | null | 95% CI | vs null |
|---|---|---|---|---|
| 2 | 0.7558 | 0.7870 | [0.7852, 0.7888] | **below** |
| 3 | 0.7193 | 0.7287 | [0.7271, 0.7305] | **below** |
| 4 | 0.6894 | 0.6944 | [0.6927, 0.6960] | **below** |
| 5 | 0.6758 | 0.6711 | [0.6694, 0.6729] | **above** |
| 6 | 0.6622 | 0.6541 | [0.6526, 0.6558] | **above** |
| 7 | 0.6556 | 0.6411 | [0.6396, 0.6425] | **above** |

## Notes / caveats
- This is the **human** panel only. The machine panels (n=302 in the earlier cut) plug into the same
  three metrics + null for the human-vs-LLM contrast. On current numbers the stories differ: humans
  *widen* late (above null at the end); the earlier LLM cut *decayed below null* late (circling back).
  Worth re-running the machine side at the larger n now being collected before locking the contrast.
- Effect magnitudes are small in absolute cosine terms but the CIs are tight at this N, so the
  below→above crossover is robust, not noise.
- Distances use the first 7 valid unique words per response (same words the DAT score uses), so score
  and trajectory are on the same footing.
