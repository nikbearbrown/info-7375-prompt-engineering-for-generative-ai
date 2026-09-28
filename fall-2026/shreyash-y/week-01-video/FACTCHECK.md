# FACTCHECK.md — every claim in the narration, and what backs it

Reel: `yadav-shreyash-week01-softmax-max-subtraction`
Checked: 2026-09-21
Course source: `nikbearbrown/info-7375-prompt-engineering-for-generative-ai` @ `a0d8a1e`
Evidence file: `evidence/evidence.json` (written by `evidence/run_evidence.py`)

Rule applied: no figure is typed into a scene by hand. `scenes.py` reads
`evidence/evidence.json`; if a number in this table changed, the frame would
change with it. Nothing on screen is a constructed illustration — there are no
invented distributions in this reel, and no Claude transcript is shown.

| # | Beat | Claim | Backing | Verified |
|---|------|-------|---------|----------|
| 1 | B00 | `main.py` subtracts the largest logit before exponentiating | `peak = max(logits)` then `math.exp((x - peak) / temperature)` — lines 14–15 of the course `main.py`, unmodified | quoted verbatim in B02 |
| 2 | B02 | The code shown is the course reference implementation, unedited | `lessons/01-randomness-and-first-prompts/code/main.py` @ `a0d8a1e`; the beat shows lines 9, 14–17 with the two guard clauses elided as `...` | diff against the clone |
| 3 | B03 | `exp(1)`, `exp(2)`, `exp(3)` = 2.71828, 7.38906, 20.08554 | `evidence.json → naive.weights` | ✅ |
| 4 | B03 | Shifted weights = 0.13534, 0.36788, 1.00000 | `evidence.json → shifted.weights` | ✅ |
| 5 | B03 | Sums are 30.19287 and 1.50321 | `evidence.json → naive.sum`, `shifted.sum` | ✅ |
| 6 | B03 | Every row differs by the **same** factor, 20.085537 | `evidence.json → ratios` = three identical values; `e_to_the_peak` = 20.085536923187668 | ✅ |
| 7 | B04 | Both columns normalise to 0.09003, 0.24473, 0.66524 (5 dp) | `evidence.json → naive.probs`, `shifted.probs` | ✅ |
| 8 | B04 | `main.py`'s own output equals the shifted path exactly | `run_evidence.py` asserts `main.probabilities(LOGITS) == shifted_probs`; the run fails loudly if not | ✅ assertion |
| 9 | B04 | The shift is an exact identity, not an approximation | exp(x−m)/Σexp(x−m) = e^−m·exp(x) / e^−m·Σexp(x); the common factor cancels | algebra, shown on screen |
| 10 | B05 | `math.exp(1000)` raises `OverflowError: math range error` | `evidence.json → overflow_demo.naive_exp_1000` | ✅ |
| 11 | B05 | float64 "runs out just past e^709" | `sys.float_info.max` = 1.7976931348623157e308; `log(max)` = 709.782712893384; `exp(709)` = 8.218e307 finite, `exp(710)` raises | ✅ checked 2026-09-21 |
| 12 | B05 | `probabilities([1000, 1000])` returns `[0.5, 0.5]` | `evidence.json → overflow_demo.shifted_probabilities_1000_1000` | ✅ |
| 13 | B05 | With the shift the largest exponent is always e^0 = 1 | `x - max(logits)` is 0 for the maximal element by construction | ✅ by inspection |
| 14 | B06 | The two paths are **not** bit-identical in float64 | `evidence.json → identical_bitwise` = `false` | ✅ |
| 15 | B06 | They differ by one unit in the last place, in two of three entries | `evidence.json → ulp_difference` = `[1, 0, -1]` on the primary interpreter | ✅ |
| 16 | B06 | Unshifted probabilities sum to exactly 1.0; shifted sum to just under | `evidence.json → prob_sums` = `{naive: 1.0, shifted: 0.9999999999999999}` | ✅ |
| 17 | B07 | The same script under two Pythons reports the gap differently | Python 3.14.6 → `[1, 0, -1]`; Python 3.11.15 → `[0, -1, -1]`. Both in `evidence.json` (`ulp_difference`, `crosscheck.ulp_difference`) — the cross-run is performed by the script itself | ✅ |
| 18 | B07 | Cause: CPython changed `sum()` to compensated summation in 3.12 | Behavioural probe, not a citation: `sum([1e100, 1.0, -1e100, 1.0])` returns **2.0** on 3.14.6 and **1.0** on 3.11.15 and 3.9.6. `evidence.json → neumaier_probe` | ✅ probed |
| 19 | B07 | `exp()` itself is identical across the interpreters | all three interpreters return bit-identical `math.exp(1/2/3)`; only the `sum()` of them differs | ✅ checked |
| 20 | B07 | What IS stable across both: not bit-identical, and shifted Σp = 0.9999999999999999 | both runs agree on `identical_bitwise` and `prob_sums` | ✅ |
| 21 | BVDT | Says nothing about which token is correct | scope claim, not an empirical one: softmax is a normalisation of scores; no step in it consults ground truth. Matches the lesson's own "temperature changes the distribution, not the truth of the answer" | ✅ by scope |

## Claims deliberately NOT made

- **Not claimed:** that the shift is "numerically stable" in general. It removes
  the overflow at the top end. It does not address underflow of small terms, and
  this reel does not test that.
- **Not claimed:** that the ±1 ULP gap is a defect. It is the expected
  consequence of reordering float operations.
- **Not claimed:** that 630 vs 665.24 (the sampling counts in `main.py`) means
  anything is wrong. That is a different concept and is not in this reel.
- **Not shown:** any Claude chat transcript. None was used as evidence, so none
  is displayed. Beats B00 and BHTF render the Claude *composer* — the toolkit's
  standard chassis — but they are labelled **RECONSTRUCTED INTERFACE** on
  screen, the model and effort chips are blanked so no model is implied, and
  the lines beneath the card state in view that they are quoted from `main.py`,
  **not a model reply**. No Claude output, real or invented, appears anywhere
  in the reel, and no date/model is asserted for one.

## Constructed illustrations

**No constructed data.** Every figure is a rendering of a value in
`evidence/evidence.json`. No distribution, count or probability anywhere in the
reel was invented to illustrate a point.

Two non-data constructions, both labelled on screen:

1. **The Claude composer (B00, BHTF)** — a reconstructed interface, not a
   screenshot and not a transcript. Labelled `RECONSTRUCTED INTERFACE` in the
   eyebrow of both beats; model/effort chips blanked; the text below the card
   says on screen that it is quoted from the file rather than a model reply.
2. **The algebraic identity (B04)** — a statement of algebra, drawn. Not a data
   illustration; its correctness is checkable by inspection.
