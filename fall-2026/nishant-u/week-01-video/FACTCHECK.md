# FACTCHECK — week-01-softmax-max-subtraction

Status: **Agent-checked 2026-09-27 (Claude Code). Reviewed and signed off by Nishant U on 2026-09-27: I read every row against maxsub_runs.stdout.txt and re-ran maxsub_runs.py myself; the output matched.**
Every on-screen number was compared character-by-character against `maxsub_runs.stdout.txt`
(the saved stdout of `maxsub_runs.py`, sha256 `e0fd1eca…150c`, Python 3.12.10), or recomputed /
worked out as stated in its row. "PASS" below means only what the Source column says was done —
nothing here was checked against an external reference.

**Source types**
- **PRINTED** — appears in maxsub_runs.py stdout. Blocks `[1, 2, 3]` and `[1000, 1000]` were first
  printed 2026-09-26 and reprinted identically 2026-09-27; blocks `[1000, 1001]`, `[0, 1]` and
  `[0, -1000]` were first printed 2026-09-27.
- **COMPUTED** — arithmetic on printed values (not itself printed). Recomputed in Python 2026-09-27.
- **BY HAND** — worked from the formula; not printed. Arithmetic checked 2026-09-27.
- **ALGEBRA** — a symbolic identity; checked by derivation, not by running code.

## On-screen numbers

| # | Beat | Claim (as shown) | Verdict | Source / derivation | Fix |
|---|---|---|---|---|---|
| 1 | B01 | `naive (no max-subtraction): OverflowError: math range error` | PASS | PRINTED, verbatim, `[1000, 1000]` block (2026-09-26; same line again in `[1000, 1001]` block 2026-09-27) | — |
| 2 | B02 | z = [1, 2, 3] | PASS | Input to the script (`logits = [1, 2, 3]`), 2026-09-26 | — |
| 3 | B02 | p = [0.090, 0.245, 0.665] | PASS | PRINTED `probs from raw` [0.09003057317038045, 0.24472847105479764, 0.6652409557748219], 2026-09-26; rounded to 3 decimals (rounding not labelled on screen in this beat) | — |
| 4 | B03 | e^1, e^2, e^3 = 2.718, 7.389, 20.086 | PASS | PRINTED `raw exp(x)` [2.718281828459045, 7.38905609893065, 20.085536923187668], 2026-09-26; rounded to 3 decimals | — |
| 5 | B03 | total = 30.193 | PASS | COMPUTED: sum of printed raw exp values = 30.192874850577365 → 30.193 (on-screen label "Totals computed from printed values.") | — |
| 6 | B03 | 2.718/30.193, 7.389/30.193, 20.086/30.193 = 0.090, 0.245, 0.665 | PASS | Fractions assembled from rows 4–5 (COMPUTED); results = PRINTED `probs from raw`, 2026-09-26 | — |
| 7 | B04 | [1, 2, 3] − 3 = [−2, −1, 0] | PASS | BY HAND (max = 3; the script prints only the exponentials, not the shifted scores). Not labelled "by hand" on screen | — |
| 8 | B04 | e^z raw: 2.718, 7.389, 20.086 | PASS | Same as row 4 | — |
| 9 | B04 | e^z shifted: 0.135, 0.368, 1.000 | PASS | PRINTED `shifted exp(x - max)` [0.1353352832366127, 0.36787944117144233, 1.0], 2026-09-26; rounded | — |
| 10 | B04 | totals 30.193 and 1.503 | PASS | COMPUTED: 30.192874850577365; 1.5032147244080551 → 1.503 (labelled "Totals computed from printed values.") | — |
| 11 | B04 | p raw 0.090, 0.245, 0.665 · p shifted 0.090, 0.245, 0.665 | PASS | PRINTED `probs from raw` [0.09003057317038045, 0.24472847105479764, 0.6652409557748219] and `probs from shifted` [0.09003057317038046, 0.24472847105479764, 0.6652409557748218], 2026-09-26; rounded | — |
| 12 | B05 | e^{z_i−m}/Σ_j e^{z_j−m} = e^{−m}e^{z_i}/(e^{−m}Σ_j e^{z_j}) = e^{z_i}/Σ_j e^{z_j} | PASS | ALGEBRA: e^{a−m} = e^{−m}e^{a}; e^{−m} does not depend on j so it factors out of the sum; e^{−m} > 0 for every real m so the cancellation is valid | — |
| 13 | B05 | "m is any constant; the code uses m = max score" | PASS | ALGEBRA (row 12) + lesson `main.py`: `peak = max(logits)`, `math.exp((x - peak) / temperature)` | — |
| 14 | B06 | z = [1000, 1000] | PASS | Script input, 2026-09-26 | — |
| 15 | B06 | e^{1000} → OverflowError: math range error | PASS | PRINTED, `[1000, 1000]` block, 2026-09-26 (labelled Source) | — |
| 16 | B06 | [0, 0] → [1, 1] | PASS | BY HAND: 1000 − 1000 = 0; e^0 = 1 (labelled "Worked by hand from the formula.") | — |
| 17 | B06 | → [0.5, 0.5] | PASS | PRINTED `main.probabilities(): [0.5, 0.5]`, 2026-09-26 (labelled Source) | — |
| 18 | B06B | z = [1000, 1001] | PASS | Script input, 2026-09-27 | — |
| 19 | B06B | z − 1001 = [−1, 0] | PASS | BY HAND (labelled "Worked by hand from the formula.") | — |
| 20 | B06B | [1000, 1001] → p = [0.269, 0.731] | PASS | PRINTED `main.probabilities(): [0.2689414213699951, 0.7310585786300049]`, 2026-09-27; rounded (labelled "Rounded to 3 decimals.") | — |
| 21 | B06B | [0, 1] → p = [0.269, 0.731] | PASS | PRINTED `main.probabilities([0, 1]): [0.2689414213699951, 0.7310585786300049]`, 2026-09-27; rounded (labelled) | — |
| 22 | B07 | 0.09003057317038045 (raw) vs 0.09003057317038046 (shifted) | PASS | PRINTED, verbatim, first entries of `probs from raw` / `probs from shifted`, 2026-09-26 | — |
| 23 | B08 | z = [0, −1000] | PASS | Script input, 2026-09-27 | — |
| 24 | B08 | math.exp(-1000) = 0.0 | PASS | PRINTED `math.exp(-1000):      0.0`, 2026-09-27 | — |
| 25 | B08 | p = [1.0, 0.0] | PASS | PRINTED `main.probabilities(): [1.0, 0.0]`, 2026-09-27 | — |
| 26 | B08 | e^{−1000}/(1 + e^{−1000}) > 0 | PASS | ALGEBRA: e^x > 0 for all real x, so numerator and denominator are both positive. No numeric value computed or shown (labelled "From the formula, not printed output.") | — |

## Spoken claims

| # | Beat | Claim (as spoken) | Verdict | Source / derivation | Fix |
|---|---|---|---|---|---|
| 27 | B01 | "Ask Python for the probability of an option with a score of 1000, and it crashes." | PASS | PRINTED OverflowError for the naive path on [1000, 1000] and [1000, 1001]. A single-option run was not printed; the crash is `math.exp(1000)` in either case. "Crashes" refers to the naive path, not `main.probabilities()` | — |
| 28 | B02 | "nine, twenty-four and a half, and sixty-six and a half percent" | PASS | PRINTED probs 0.0900…, 0.2447…, 0.6652… → 9.0%, 24.5%, 66.5% (rounded) | — |
| 29 | B03 | "2.7, 7.4 and 20.1" | PASS | PRINTED raw exp values, rounded to 1 decimal | — |
| 30 | B04 | "the largest is always exactly one" | PASS | ALGEBRA: max − max = 0 and e^0 = 1; PRINTED 1.0 for this case | — |
| 31 | B04 | "the final probabilities are identical" | PASS | PRINTED: identical at 3 decimals (shown). At full precision p₁ and p₃ differ in the last digit, which B07 discloses | — |
| 32 | B05 | "Softmax only cares about the gaps between scores, not their size." | PASS | ALGEBRA (row 12): softmax is unchanged by adding the same constant to every score | — |
| 33 | B06 | "e to the thousand overflows" / "fifty-fifty" | PASS | Rows 15, 17 | — |
| 34 | B06B | "The result matches what scores zero and one give." | PASS | Rows 20–21: printed values identical to all 16 digits | — |
| 35 | B07 | "for two of the three probabilities, the methods differ in the last digit" | CORRECTED | PRINTED 2026-09-26: p₁ …045 vs …046 (shown on screen) and p₃ …219 vs …218 differ in the last digit; p₂ is identical on both paths (0.24472847105479764). Earlier wording "the two methods differ in the last digit" implied every value differed | Narration reworded 2026-09-27; B07 audio regenerated |
| 36 | B07 | "That's ordinary floating-point rounding." | EXEMPT | Explanation, not measured. Consistent with IEEE-754 doubles (~16–17 significant digits), but no rounding-error analysis was run | — |
| 37 | B08 | "the smaller option's probability comes out as exactly zero" | PASS | PRINTED [1.0, 0.0], 2026-09-27 | — |
| 38 | B08 | "Its true value is tiny, but not zero." | PASS | ALGEBRA (row 26). "Tiny" is qualitative; no value computed | — |
| 39 | B08 | "The subtraction prevents overflow, not rounding." | PASS | [1000, 1000] / [1000, 1001] avoid overflow (PRINTED); [0, −1000] still underflows to 0.0 after subtraction (PRINTED) | — |
| 40 | B08 | "one passing test covers one case…doesn't prove the code is stable for every input…doesn't change what the model prefers or whether its answer is right" | EXEMPT | Scope and limits statements; nothing to test | — |
| 41 | B00 | Title "Why subtracting the max changes nothing that matters" | EXEMPT | Framing line; supported by rows 12 and 31, qualified by rows 35 and 39 | — |

## Not verified
- The lesson file `main.py` was read (sha256 `df9940ca…43e5d`) but not tested beyond the calls in the script.
