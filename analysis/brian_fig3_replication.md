# Does Brian's Figure 3 (sequential trajectory) replicate on the new data?

**Method — Brian's exact spec** (from the null-model verdict + main-figure audit), applied to freshly
collected data:
- **Sample:** top 10% by DAT score (dat ≥ p90), same as all Fig-3 analyses. Human p90 = 86.58,
  LLM p90 computed on the new machine batch.
- **Panels:** A diffusion (anchor→word j), B adjacent (k→k+1), C stepwise (k→centroid of prior words).
- **Window:** first 7 valid unique nouns → 6 points per panel.
- **Null:** per-response order-shuffle (permutation), **without replacement**, 300 draws, 95% CI.
- **Stats:** Δ = mean(observed) − mean(null) per point + two-sided Monte Carlo p; null slope test.
- **Data:** human = consolidated `human_dat_all.csv` (n top-10% = 1,033); LLM = new machine batch
  **n100** (3,700 responses, scored here with the Olson pickle; n top-10% = 361).

## Validity checks (Brian's Q1 / Q2) — both pass
- **A[0] = B[0] = C[0]** identical for the actual data (human 0.8695; LLM 0.8244). Brian's Q1 (the
  0→1 bar must match across panels for real data) is satisfied — no plotting bug.
- **Null slopes flat** for A and B (slope CIs include 0). C's null declines mechanically (expected —
  the prior-word centroid grows). Brian's Q2 (a proper null must be flat) is satisfied — the earlier
  upward-sloping null was the with-replacement artifact, now gone.

## Verdict: the STRUCTURE replicates; the human line is anchoring-then-diffusion, as in the audit
### Humans (n=1,033)
- **Start well below null, then rise to/above it.** Diffusion 1→2 = 0.870 vs null 0.889 (Δ=-0.019,
  p=.003); by adjacent 5→6 / 6→7 the observed line sits *above* null (Δ=+0.006, p≈.06-.09); stepwise
  step 6 above null (p=.003). This is exactly the **"humans start anchored and diffuse away faster
  than random"** reading flagged in the main-figure audit (C7) — not the older "humans strictly
  exceed random everywhere" sentence.
- Interpretation: top humans open with a locally-linked pair, then sustain outward exploration —
  distance grows across the sequence relative to order-random.

### LLMs (n=361, n100 batch)
- **Systematic non-random structure, opposite shape.** After an initial dip (1→2 below null), the
  adjacent line jumps **far above null and stays there** across every later step (Δ ≈ +0.03 to +0.04,
  all p=.003). Diffusion oscillates hard (1→3 spike above, then repeatedly below). Stepwise ends
  **below null** (step 7 Δ=-0.017, p=.003) — later words land closer to the running centroid than
  random, i.e. converging.
- Interpretation: LLMs place consecutive words unusually far apart (the "local step then jump"
  oscillation) but the *set* converges by the end — front-load then circle back. Consistent with the
  paper's "top LLMs front-load then converge" claim and with autoregressive w1-conditioning.

## Bottom line
Brian's Figure-3 finding **replicates in structure on the new data**: humans and LLMs both deviate
systematically from an order-random null, in opposite directions — humans widen (anchor→diffuse),
LLMs oscillate locally while the overall set converges. The replication also confirms the two
technical fixes Brian demanded (matching 0→1 bars; flat nulls).

## Caveats
- LLM side is the **n100** batch, scored here for this analysis. The **n150** collection is still in
  progress (10 models pending, xAI blocked on credits). Re-run on the finalized n150 before locking
  magnitudes — the LLM n=361 is solid on direction, softer on exact dip sizes.
- Only the permutation null is shown here (Brian's, and the one the small-sample figure used). The
  frequency-weighted / within-bin nulls from the audit can be layered on the same harness if we want
  the stricter comparison in the paper.

Figure: `results/brian_fig3_replication.png`.
