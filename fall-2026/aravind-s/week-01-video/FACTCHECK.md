# FACTCHECK: Three Scores Are Not Yet Three Chances

Every claim the video makes, on screen or in narration, with its evidence.
Numbers come from `evidence/softmax_steps_output.txt` and
`evidence/main_py_output.txt` (Python 3.12.14, course repo commit 24f4af3,
run 2026-09-26). Values are rounded to 4 decimal places on screen.

| Beat | Claim | Verdict | Evidence |
|---|---|---|---|
| B00 | The scores [1, 2, 3] were chosen by hand; no model produced them. | True by construction | The lesson's demo input; the chapter says the same of its own example. |
| B00 | A language model ends each prediction step with one score per possible next token. | Supported | Lesson 1 docs: "A language model assigns scores to possible continuations." |
| B01 | Scores rank outcomes; they are not yet chances (chances must be nonnegative and sum to 1). | Supported | [1, 2, 3] sums to 6, and scores may be negative. |
| B02 | [1, 2, 3] / 6 = [0.1667, 0.3333, 0.5000]. | Verified | softmax_steps_output.txt, divide-by-sum block |
| B02 | [-1, 2, 3] / 4 gives -0.2500, a "chance" below zero. | Verified | same |
| B02 | [-1, 0, 1] has sum 0, so dividing raises ZeroDivisionError. | Verified | same |
| B02 | Divide-by-sum is not the lesson's rule. | True | main.py never divides raw scores by their sum. Labelled on screen. |
| B03 | probabilities() subtracts the max, exponentiates, and divides by the total. | Verified | main.py lines 14-17. Lines 10-13 (input checks) are elided and labelled. |
| B03 | Temperature is 1.0 in every example in the video. | True | All calls use the default temperature=1.0. |
| B04 | [1, 2, 3] minus peak 3 = [-2, -1, 0]. | Verified | softmax_steps_output.txt |
| B04 | Weights = [0.1353, 0.3679, 1.0000]; total = 1.5032. | Verified | same |
| B04 | Chances = [0.0900, 0.2447, 0.6652]; they sum to 1.0000. | Verified | same, and main_py_output.txt (full precision) |
| B05 | A 1-point score gap multiplies the weight by e = 2.7183. | Verified (math + run) | exp(z + 1) / exp(z) = e; neighbour ratios printed as [2.7183, 2.7183]. |
| B05 | Dividing every weight by the same total keeps the ratios, so neighbouring chances also differ by x 2.7183. | Verified | same printout |
| B05 | Divide-by-six gives a neighbour ratio of 1.5000 instead. | Verified | 0.5000 / 0.3333 printout |
| B06 | probabilities([-1, 2, 3]): weights [0.0183, 0.3679, 1.0000], chances [0.0132, 0.2654, 0.7214], sum 1.0000, order kept. | Verified | softmax_steps_output.txt |
| B06 | A 3-point gap multiplies by e cubed = 20.0855 ("about twenty"). | Verified | neighbour ratio 20.0855 printed |
| B07 | These are chances of being sampled from hand-picked scores, not chances of being right. | Supported | Lesson 1 Computational Skepticism note: softmax probabilities describe which toy token is sampled; they are not calibrated probabilities that a claim is true. |
| B07 | In exact arithmetic the transformation gives positive numbers that sum to 1 and keep the order (for positive temperature). | Supported | Chapter 1, "Three scores are not yet three chances". |
| B07 | It says nothing about whether the scores are sensible or outcome 2 is true. | Supported | Same section: "not a statement that the inputs were sensible or the outcome labels were true." |
| B08 | The result keeps the order and every ratio. | Verified | B04 and B05 evidence |

## Corrections applied while fact-checking

- B07 originally said the transformation "guarantees positive numbers that
  sum to one". In floating point a weight can underflow to exactly 0.0 (for
  example `math.exp(-800)` is `0.0`), and a sum can differ from 1 in the last
  bits. The narration now says "In exact arithmetic", matching the chapter,
  and the on-screen heading reads "Guaranteed (exact math)".

## What the video does not claim

- It does not claim the probabilities are calibrated or that any outcome is correct.
- It does not show or quote any Claude response.
- It does not model temperature, sampling counts, or seeds (other concepts).
