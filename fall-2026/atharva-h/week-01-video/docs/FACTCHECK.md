# FACTCHECK — claude-liam-only-the-gaps

DOUBLE-CHECK LAW: every claim that reaches the screen or the voice is listed here
with a verdict. Nothing was taken on trust. Every numeric claim traces to a named
check in `verify/verify_claims.py`, which passes 14/14 on two interpreters
(Python 3.14.7 and 3.12.14) and writes a JSON record of each run.

**Source text:** Chapter 1 — *Randomness and first prompts*, INFO 7375.
**Reference implementation:** the chapter's own printed listing (lines 170–182 and
228–241). The course book repo was not on this machine, so the printed listing is
the source — and claim C1 cross-checks our output against the chapter's own
recorded tables to ten decimal places. See FRICTIONAL.md.

**No Claude transcript appears anywhere in this reel.** Nothing was fabricated to
make a cleaner story, and there was no transcript to fabricate.

| # | Claim | Where | Check | Verdict | Basis / scope |
|---|---|---|---|---|---|
| 1 | Scores `[1, 2, 3]` are constructed, not measured | B01, B04 | — | ✅ | Chapter line 134 says so of its own: "I have chosen them; no model produced them." Marked **CONSTRUCTED** on screen for the whole reel. |
| 2 | `[1,2,3]` at T=1.0 → `0.0900305732 / 0.2447284711 / 0.6652409558` | B01 | C1 | ✅ | Matches the chapter's recorded T=1.0 row (line 209) to 10 dp. |
| 3 | Softmax output is unchanged by adding a constant to every score | B03 | C3 | ✅ | Tested for shifts 1e0…1e15. Exact list equality, not `isclose`. |
| 4 | Sliding is a real property of *this* function, not a static animation | B04 | C4 | ✅ | Negative control: `x²` and `|x|` normalisation both change under the identical +100 shift; softmax does not. |
| 5 | Lunch labels (pizza / salad / dirt) are the narrator's invention | B04 | — | ✅ | Marked **CONSTRUCTED** on screen. The numbers beneath them are the verified `[1,2,3]` distribution; only the labels are invented. |
| 6 | Halving the temperature is the same operation as doubling the gaps | B05 | C12 | ✅ | `[1,2,3]` at T=0.5 == `[1,3,5]` at T=1.0, bit-for-bit. Verified for gap scaling ×2, ×3, ×0.5. |
| 7 | 2⁵³ = 9,007,199,254,740,992 is the float64 integer limit | B07 | C6 | ✅ | `sys.float_info.mant_dig == 53`. Above 2⁵³, consecutive integers are no longer all representable. |
| 8 | Shift-invariance holds at 2⁵³−3 and breaks at 2⁵³−2 | B07 | C6 | ✅ | Found by explicit nine-integer scan, not by search — see claim 12. |
| 9 | At shift 1e16 the output equals the chapter's T=0.5 row exactly | B07 | C7 | ✅ | Rounding widens the gaps 1→2; a ×2 stretch *is* T=0.5 (claim 6), so this is C12 **predicting** C7. Stated on screen before it is computed. |
| 10 | At shift 1e17 all three scores collapse and the output is exactly uniform | B08 | C8 | ✅ | All three round to `1e17`; gaps become 0; output `0.3333333333` ×3. |
| 11 | Both broken outputs pass a sum-to-one check | B08 | C9 | ✅ | Both sum to exactly `1.0`; `math.isclose(sum, 1.0)` is `True` for both. Compare chapter line 373 (Assignment 10), which asks the reader to *construct* such a case. |
| 12 | The threshold was first sought with an invalid method | B09 | C10 | ✅ | Binary search requires a monotonic predicate. The region around 2⁵³ alternates between uniform and skewed, so the search was invalid and its answer untrustworthy. Recorded, not hidden. |
| 13 | A float64 holds about sixteen digits, so just past 2⁵³ three consecutive integers cannot all be stored: `…740993 · …740994 · …740995` become `…740992 · …740994 · …740996` | B06 | C14 | ✅ | `int(float(9007199254740993))` is `…992`; the wanted gaps `[1,1]` are stored as `[2,2]`. `sys.float_info.dig` is 15; 2⁵³ has 16 digits. |
| 14 | Squashing the gaps by half reproduces the recorded T=2.0 row | B05 | C12 | ✅ | `[1, 1.5, 2]` at T=1.0 equals the chapter's T=2.0 row exactly; asserted at render time in `scenes.py`. |

## Scope limits stated on screen

| Limit | Where said | Why it matters |
|---|---|---|
| **This does not show that real language models break this way.** Raw next-token logits sit around −10…+10; nobody shifts by 1e16. | B07, spoken | The honest claim is narrower than "numerically stable": exact below 2⁵³, silently wrong above it. This is the reel's falsifiability beat. |
| The *shape* of the distribution still carries information — flat differs from spiky, and entropy measures that. What is destroyed is the overall **level**. | not in runtime; README | Cut for the one-concept rule. Prevents the over-reading that softmax carries no uncertainty information at all. |
| C2's portability result is two interpreter versions, not "all versions". | not in runtime; README | Chapter line 245 makes the same distinction about its own recorded run. |

## Verified but deliberately NOT in the reel

| Finding | Check | Why cut |
|---|---|---|
| The naive form also fails *downward*: at `[-800, -801]` every weight underflows to 0 and normalisation divides by zero. Chapter line 164 justifies max-subtraction only by *overflow* and never mentions this. | C13 | Real finding, and it catches a genuine gap in the chapter — but it is about the exponential's range, not about gaps. On-topic for the chapter, off-concept for this reel. |
| `exp` is *forced* by requiring that only differences matter; it is not merely "a way to get positive numbers" as line 138 implies (`x²` and `\|x\|` are positive too). | C4, C5 | A second concept. Cutting it is what keeps this reel about one thing. |
| Ratio identity `p_i/p_k = exp(z_i − z_k)`. | C5 | The mechanism behind Act I; Act I shows the consequence visually instead. |
| Seeded sample counts reproduce the chapter's recorded run on both interpreters. | C2 | Real finding, wrong reel. |
| Without max-subtraction, `exp()` overflows outright at `[1000, 1001, 1002]`. | C11 | Interesting, not load-bearing here. |

## Reproduce every number in this reel

```bash
python3 verify/verify_claims.py --json out.json
```

`scenes.py` does not carry copies of these figures — it imports the chapter's
function and **computes** each one at render time, then asserts the results match
the chapter's recorded tables. An earlier draft hardcoded one value by hand and
got it wrong (`softmax([1, 3.4, 3])`); the assertions exist so that cannot recur.
See FRICTIONAL.md, entry 4.
