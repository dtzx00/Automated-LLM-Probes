# Human Analysis: Does AI Augmentation Help or Hurt?

**Data:** `human_data/processed/human_dat_all.csv` (cleaned, Olson-scored). Analysis restricted to
BTB respondents who completed **both** a solo DAT and an AI-augmented-pair DAT, so each person is
their own control. **Paired n = 879.**

## Headline
AI augmentation **raises the DAT score but lowers word uniqueness** — the same trade-off seen in the
earlier platform sample, now confirmed on the consolidated, cleaned human data with a within-person
design.

## 1. DAT score goes UP with augmentation
| | Solo | Augmented | Δ |
|---|---|---|---|
| Mean DAT | 80.57 | 82.92 | **+2.35** |

Paired t(878) = **10.33**, Cohen's dz = **0.35**. Highly significant; small-to-moderate effect.
Working with the AI produces higher semantic-distance word sets.

## 2. Word uniqueness goes DOWN with augmentation
Per-response word rarity (mean 1/frequency of a response's words within its own pool — higher = rarer,
more unique words):

| | Solo | Augmented | Δ |
|---|---|---|---|
| Mean rarity | 0.362 | 0.303 | **-0.059** |

Paired t(878) = **-8.07**, dz = **-0.27**. Augmented responses lean on **more common** words.

Two supporting views:
- **Corpus type/token ratio:** solo 3,180 distinct / 8,789 = 0.362 vs augmented 2,663 distinct /
  8,788 = 0.303. Fewer distinct words in the augmented pool for the same volume — answers converge.
- **Word sourcing:** on average **55%** of a respondent's final augmented words are copied directly
  from the AI's suggested cue words. The lift is real, but it comes with heavy reliance on the AI's
  vocabulary.
- **Top words shift toward safe choices:** solo top-10 = apple, tree, dog, car, water, computer,
  book, ocean, moon, love. Augmented top-10 = happiness, mountain, chair, book, ocean, music, apple,
  love, freedom, hammer — more abstract/common convergence.

## Interpretation
AI augmentation is a **score amplifier and a diversity suppressor**. Individuals score higher because
the AI pushes semantically distant words, but the population's answers homogenize — everyone drifts
toward the same AI-favored vocabulary, so collective uniqueness drops. This is the human-side result
for the human-vs-machine comparison; the machine arm plugs into the same scorer for the joint step.

## Reproduce
Restrict to `source==btb` rows with both `word_dat_score` and `augment_dat_score` present; paired
t-tests on (a) score and (b) per-response mean word rarity (augmented − solo).
