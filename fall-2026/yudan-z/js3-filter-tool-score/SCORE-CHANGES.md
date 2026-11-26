# SCORE-CHANGES — what moves the score, one change at a time

## Executive summary

Every number in the filter was **set by hand** or **inherited** from JS1/JS2. None was fitted.

The filter changed in eight steps, one at a time. Each step was measured on my hand labels:
- **dev**: the 45 rows used while designing changes;
- **held-out**: the 16 rows reserved for measuring.

Four steps moved the held-out result. One step was rejected after measuring. Three steps changed what the whole dataset shows Mira, but my labels cannot measure them, and this file says so.

## 1. Where every number comes from

| Number | Value (v4) | Origin |
|---|---|---|
| role word | +4 | **hand-set** (v1). Larger than the 4-point topic cap, so a role word can outweigh all the topic words together |
| topic word | +1 each, at most +4 | **hand-set** (v1) |
| senior title | −3 → **−5** (v2g) | **hand-set**. Changed after the threshold dropped (below) |
| stated 3+ years | −3 | **hand-set**. The year patterns are **inherited** from JS1 `agent/rule.py` (`YEARS`) |
| not in the US | −5 | **hand-set**. The US test is **inherited** from JS1 R3 with the JS2 full-state-name fix |
| citizenship / clearance / no sponsorship | −5 | **hand-set**. Phrase lists `CITIZEN` and `NO_SPONSOR` are **inherited** from JS1 R5/R6; clearance and four phrases were added in v2b/v2c |
| PhD in the title | −5 | **hand-set** (v2d) |
| threshold | 5 → **0** (v2a) | **hand-set** |
| minimum description length (abstain) | 200 characters | **hand-set** (`agent/filter.py` `MIN_TEXT`) |
| random seed for the sample | 20261125 | **hand-set** (today's date) |

**Fitted: none.** No number was chosen by searching for the value that scores best on the labels. With 61 labels, a fitted weight would mainly fit these 61 postings.

## 2. One change at a time

**Reaches Mira** means the decision is `keep` or `cannot tell`; both are shown to her, labelled. Each row in the table below changes one thing from the row above. Source: `runs/measure.txt`, produced by `python -m audit.measure filter/*.json`.

| Step | One change | Held-out (16): Y found / N shown | Dev (45): Y found / N shown | All 1,595: reach Mira | Kept? |
|---|---|---|---|---|---|
| v1 | starting point | 0 of 5 / 0 of 11 | 1 of 16 / 0 of 29 | 1 | — |
| v2a | threshold 5 → 0 | **5 of 5** / 3 of 11 | 14 of 16 / 4 of 29 | 211 | yes |
| v2b | + clearance phrases | 5 / **2** | 14 / 3 | 201 | yes |
| v2c | + four no-sponsorship phrases | 5 / **1** | 14 / 3 | 198 | yes |
| v2d | + PhD in the title | 5 / 1 | 14 / **2** | 193 | yes, on the dev rows only |
| v2e | 3+ years penalty → 0 | 5 / 1 | **16** / **4** | **387** | **no** |
| v2f | `Excel` only when capitalised | 5 / 1 | 14 / 2 | 145 | yes, decided by me; **not measurable** |
| v2g | senior −3 → −5, add `Sr` | 5 / 1 | 14 / 2 | 138 | yes, decided by me; **not measurable** |
| v4 | strict sponsorship evidence | 5 / 1 | 14 / 2 | 138 (0 keep, 138 cannot tell) | yes: it enforces FILTER.md §2 |

v3 is v2 plus v2f and v2g.

**Why v2e was rejected.** It found two more dev Y rows (rows 2 and 30, which have 3+ year minimums). It also showed two more N rows (27, 39), did nothing on the held-out rows, and doubled what reaches Mira. The gain was on the rows I designed with, not on the ones I held out.

**Why v2f and v2g are labelled "not measurable".** Neither changes a single labelled row. Each removes postings from the 1,595 (48 and 7) that nobody labelled. I adopted them because the evidence they remove is wrong ("excel" the verb) or contradicts my own labels (senior titles). That is a judgement, not a measurement.

**The one held-out N still shown (row 46)** fails on a graduation year ("Must be planning on graduating in 2028"). No rule reads graduation dates (AUDIT.md §5).

## 3. Limits of this measurement

- **16 held-out rows hold only 5 Y.** Going from 0 of 5 to 5 of 5 is a large change. But a difference of one row between two versions is within noise.
- **The held-out labels were not hidden from the designer.** While choosing steps v2b–v2d, Claude printed a table of all 61 rows, held-out included. The steps were motivated by dev rows (23, 49, 58 for clearance; 40 for PhD) and the film check (two phrases), but the held-out rows 25 and 41 were on screen. The held-out set is therefore **not blind**, and the gain on it is weaker evidence than a truly untouched set would give.
- **One labeller.** My Y rule is broader than the persona's target roles (AUDIT.md §2), and it was written down only after the labels.

## 4. Persistence is not training

The filter "remembers" each change because each version is a JSON file in `filter/`, and `agent/filter.py` reads whichever file it is given. Nothing learns:
- re-running v1 today gives v1's result;
- no weight moved because of data;
- in the Claude session, the model read tool outputs within one conversation and kept nothing afterwards.

A score that improves across versions here improved because **I wrote a different file**, not because a model was trained on my labels.
