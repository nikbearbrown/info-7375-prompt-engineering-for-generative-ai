# One change at a time, measured once on the held-out set

Measured by `tools/heldout_experiments.py` at 2026-11-22T083619Z (UTC), after the changes and predictions were committed in `js3/score/CHANGES-TO-MEASURE.md` (`1c9a37e`). Against Aravind's 30 frozen held-out verdicts (`1e2b1e1`: 12 Keep, 15 Reject, 3 "?"). Every run is in `js3/score/runs/2026-11-22T083619Z/`. No model is called, so every run costs $0 at API prices.

## Results

| Run | Change | Fate agreement, kept pool | Fate agreement, rejected pool | Disagreements, 95% bound | Cutoff | Recommended | Cutoff agreement | Held-out cards that change | Whole run: fates / scores that change | Prediction |
|---|---|---|---|---|---:|---:|---|---|---|---|
| R0 | v1.0 as committed | 12 of 12 | 15 of 15 | 0 of 27, at most 10.5% | 60 | 7 | 22 of 27 | 0 (0 fates) | 0 / 0 |  |
| R0b | identical to R0, card for card | 12 of 12 | 15 of 15 | 0 of 27, at most 10.5% | 60 | 7 | 22 of 27 | 0 (0 fates) | 0 / 0 | held |
| X1 | no fate changes | 12 of 12 | 15 of 15 | 0 of 27, at most 10.5% | 60 | 7 | 22 of 27 | 0 (0 fates) | 0 / 0 | held |
| X2 | no fate changes | 12 of 12 | 15 of 15 | 0 of 27, at most 10.5% | 60 | 7 | 22 of 27 | 0 (0 fates) | 0 / 0 | held |
| X3 | no fate changes; a few scores fall by 5 | 12 of 12 | 15 of 15 | 0 of 27, at most 10.5% | 60 | 7 | 22 of 27 | 0 (0 fates) | 0 / 7 | partly: no fate changed, the rest did not happen here |
| X4 | no fate changes; fewer recommended | 12 of 12 | 15 of 15 | 0 of 27, at most 10.5% | 60 | 7 | 22 of 27 | 3 (0 fates) | 0 / 9 | partly: no fate changed, the rest did not happen here |
| X5 | no fate changes; cutoff agreement rises | 12 of 12 | 15 of 15 | 0 of 27, at most 10.5% | 55 | 9 | 24 of 27 | 0 (0 fates) | 0 / 0 | held |
| X6 | no fate changes; cutoff agreement rises further | 12 of 12 | 15 of 15 | 0 of 27, at most 10.5% | 50 | 12 | 27 of 27 | 0 (0 fates) | 0 / 0 | held |

"Prediction" checks each run against what `CHANGES-TO-MEASURE.md` predicted before the answers were opened. The bound is the exact one-sided 95% upper bound on the share of disagreements, for the 27 cards he judged; it says what this sample allows, not a rate for all postings.

## Every run, card by card, where it differs from v1.0

**R0b:** no card changes.

**X1:** no card changes.

**X2:** no card changes.

**X3:** no card changes.

**X4:** 
- card 10 (Software Engineer, AI accelerator Runtime; his verdict ?): kept 50 -> kept 40
- card 22 (Product Reliability Engineer; his verdict ?): kept 50 -> kept 40
- card 29 (Software Engineer, Model Runtime; his verdict ?): kept 55 -> kept 45

**X5:** 
- card 19 (Software Engineer, Foundations Search; his verdict Keep): score 55, now recommended at cutoff 55
- card 28 (Software Engineer, Developer Productivity - Inference Runtime; his verdict Keep): score 55, now recommended at cutoff 55
- card 29 (Software Engineer, Model Runtime; his verdict ?): score 55, now recommended at cutoff 55

**X6:** 
- card 08 (Software Engineer, Security Observability; his verdict Keep): score 50, now recommended at cutoff 50
- card 10 (Software Engineer, AI accelerator Runtime; his verdict ?): score 50, now recommended at cutoff 50
- card 17 (Software Engineer, Mobile Web — Dots; his verdict Keep): score 50, now recommended at cutoff 50
- card 19 (Software Engineer, Foundations Search; his verdict Keep): score 55, now recommended at cutoff 50
- card 22 (Product Reliability Engineer; his verdict ?): score 50, now recommended at cutoff 50
- card 27 (Software Engineer, Research Developer Productivity; his verdict Keep): score 50, now recommended at cutoff 50
- card 28 (Software Engineer, Developer Productivity - Inference Runtime; his verdict Keep): score 55, now recommended at cutoff 50
- card 29 (Software Engineer, Model Runtime; his verdict ?): score 55, now recommended at cutoff 50

## What persistence is not proof of

A behavior that stays the same across runs or sessions does not mean anything was trained. R0 and R0b agree card for card because the filter is a fixed program reading a fixed file over saved text, with no randomness and no model call; nothing in it learns from Aravind's labels. A change persists here only because it is written in FILTER.md and read by the program; training is identified by its mechanism (chapter 9), and there is none.
