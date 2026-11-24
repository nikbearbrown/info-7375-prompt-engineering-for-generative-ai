# One change at a time

DRAFT (Claude, Nov 24, 2026), to be checked and rewritten by me. Every number has a row in `score/origins.md`.

## The baseline: FILTER.md v1.0 rules

The rules were written before any code (`0041401`) and implemented in `agent/filter.py` (`342075a`). They were run on all 400 postings and kept 22 (`evidence/filter-v1.0/`).

## The one change: v1.2, R2 scores N ≥ 3 years at −0.40

- **Before:** in v1.0, a posting asking for exactly 3 years got 0 points from R2. A posting with a role phrase and one skill then reached 0.60 and was kept.
- **Why I changed it:** there were two signals, and both were read before the change.
  - **Dev labels:** v1.0 had 6 false positives, and all 6 ask for exactly 3 years.
  - **The v1.0 audit:** of the 11 kept postings I judged wrong, 7 ask for exactly 3 years. None of the 11 I judged right do.
- **What else changed:** nothing. The threshold, the other rules and the gates are the same.

| | dev (45; 6 keep) | held-out (45; 5 keep) | all 400 |
|---|---|---|---|
| v1.0 | tp 6, fp 6, fn 0, tn 33 | tp 5, fp 5, fn 0, tn 35 | kept 22 |
| v1.2 | tp 6, **fp 0**, fn 0, tn 39 | tp 5, **fp 4**, fn 0, tn 36 | kept 15 |
| difference | −6 false positives | −1 false positive | 7 postings flipped, all keep → reject, all at N = 3 |

## How to read it

- **The change fit dev far better than held-out.** It fixed 6 false positives on dev and 1 on held-out. Most of held-out's errors are a different kind, so the dev result overstates what the change does.
- **Recall did not drop.** Recall was 6/6 on dev and 5/5 on held-out before and after. No posting I would keep was lost.
- **Held-out is small.** It has 5 true keeps, and the difference is 1 posting, so it cannot show that v1.2 is better in general. It shows only that v1.2 did no harm on these 45.
- **Held-out was not fully untouched.** The kept audit sheet lists every kept posting, and some are held-out rows, so I had seen their filter decisions before choosing the rule. The rule rests on dev alone, but the held-out number is not a clean test of it.
- **Held-out has been used.** It was run once (Nov 24, 05:54 UTC), for v1.0 and v1.2 together. Any further rule change would be measured on dev and reported against this run, not tuned on held-out again.

## What one more change would target (not made)

The 4 false positives left on held-out are kept by both versions:

| Posting | Why I reject it | Why the years rule cannot reach it |
|---|---|---|
| `robinhood:7263592`, `robinhood:8258305`, `robinhood:8385931` (backend) | mid-level: "track record", "proven ability" | they ask for 2+ years |
| `wealthfront:eccc8bc6…` (iOS) | mobile specialty, not Sam's stack | it asks for 2–6 years, so N = 2 |

- **Mobile roles:** a change here would be a decision about the persona, namely whether iOS and Android count as Sam's target. It is not a parsing fix.
- **The three backend roles:** these would need a rule that reads wording, such as "track record". The shortlist claim check already flags all four (`shortlist/CASES.md`), but its cue was chosen after reading these postings, so it is not a measurement either.
