# One change at a time

Every figure below maps to a reproducible command in `score/origins.md`.

## Baseline: `FILTER.md` v1.0 rules

The filter rules were committed before any implementation code existed (`0041401`) and implemented in `agent/filter.py` (`342075a`). Running the v1.0 baseline across all 400 collected postings kept 22 and rejected 378 (`evidence/filter-v1.0/`).

## The single rule change: `FILTER.md` v1.2 (`R2` scores `N ≥ 3` years at `−0.40`)

- **Before (`v1.0`):** Postings asking for `3` years received `0` points from `R2`, allowing any posting with a matching role phrase (`+0.50`) and one skill hit (`+0.10`) to reach `0.60` and pass the `0.50` threshold.
- **Why I changed it:** Two pre-change signals pointed directly to the `3`-year boundary:
  - **Dev labels:** All `6` false positives on `dev` asked for `3` years.
  - **The v1.0 audit:** Of the `11` kept postings I judged wrong, `7` asked for `3` years, whereas `0` of the `11` postings I judged right asked for `3` years.
- **What stayed unchanged:** The `0.50` threshold, the three hard gates (`G1`–`G3`), and all other scoring weights remained identical.

| Version | `dev` (45; 6 keep) | `heldout` (45; 5 keep) | All 400 postings |
| :--- | :--- | :--- | :--- |
| **`v1.0`** | `tp = 6`, `fp = 6`, `fn = 0`, `tn = 33` | `tp = 5`, `fp = 5`, `fn = 0`, `tn = 35` | `kept = 22` |
| **`v1.2`** | `tp = 6`, `fp = 0`, `fn = 0`, `tn = 39` | `tp = 5`, `fp = 4`, `fn = 0`, `tn = 36` | `kept = 15` |
| **Difference** | `−6` false positives | `−1` false positive | `7` postings flipped `keep → reject` (all at `N = 3`) |

## How to interpret these numbers

- **`dev` improved far more than `heldout`:** Penalizing `N ≥ 3` removed all `6` false positives on `dev` but only `1` of `5` on `heldout`, because most held-out false positives stem from a different failure mode (`2+ years` mid-level roles and mobile stack mismatches). The `dev` jump therefore overstates how much the rule change fixes out of sample.
- **Recall held steady at 100%:** Recall stayed at `6/6` on `dev` and `5/5` on `heldout` before and after the change—no genuine fit was lost.
- **The `heldout` split is too small for broad claims:** With only `5` true keeps and a `1`-posting difference, `heldout` cannot establish that `v1.2` generalizes broadly; it shows only that tightening `R2` caused no harm on these 45 rows.
- **`heldout` was not strictly untouched:** Because `audit/filter-v1.0/kept.csv` included all `22` kept postings from the full dataset—some of which belong to `heldout`—I had already seen their v1.0 filter outcomes before selecting the `N ≥ 3` rule. The rule itself was chosen from `dev` and the audit, but the `heldout` score is not an uncontaminated out-of-sample test.
- **`heldout` has now been spent:** `agent/evaluate.py` was run once on Nov 24 at `05:54 UTC` for `v1.0` and `v1.2` together. Any further rule changes would be evaluated on `dev` and reported against that single run rather than tuned on `heldout`.

## What one further change would target (not implemented)

The `4` remaining false positives on `heldout` pass both `v1.0` and `v1.2`:

| Posting | Why I rejected it | Why the years rule cannot catch it |
| :--- | :--- | :--- |
| `robinhood:7263592`, `robinhood:8258305`, `robinhood:8385931` (backend) | Mid-level scope (`"track record"`, `"proven ability"`) | Each states `2+ years` (`N = 2`) |
| `wealthfront:eccc8bc6…` (iOS) | Native iOS specialty outside Sam's stack | States `2–6 years`, so `N = 2` |

- **Mobile roles:** Excluding iOS/Android roles would require changing Sam's persona scope rather than fixing a parsing bug.
- **Mid-level `2+ years` backend roles:** Filtering those out would require lexical rules targeting scope phrases like `"track record"`. While the shortlist claim check flags all four entries (`shortlist/CASES.md`), its contradiction cue was written after inspecting those postings in the audit and does not count as an independent measurement.
