# Prompt experiment (Chapter 2)

*Drafted by Claude Code from the committed evidence. Reviewed by Atharva C.,
2026-10-31: I ran `diff prompts/baseline.txt prompts/revision.txt` (one
changed line, 20c20) and checked the held-out scores in
`results/experiment_*_held-out.json` (baseline 9/10, revision 10/10).
Numbers come from `results/experiment_*.json` and `logs/experiment_*.jsonl`
(commits 1e11045 and f82287b).*

## Setup, in the order it happened

1. **Labeling rule written first:** `LABELING_RULE.md`, commit e70631f, before
   I looked at any of the 20 postings. One clarification was added *during*
   labeling: mixed US + Canada locations must be purely US. It's dated in
   the file, and it changed one label (7557899).
2. **20 real postings:** drawn from the committed baseline response with seed
   7375 by `tools/select_labels.py`, from the 180 postings whose title
   contains "engineer" or "developer". Split 10 dev / 10 held-out by the same
   seed.
3. **Hand labels:** committed as ff49997, before any Claude call on these
   postings. Result: **1 of 20 relevant** (7776179, dev). Held-out has
   **0 relevant**.
4. **Baseline prompt** (`prompts/baseline.txt`) run on dev.
5. **One change:** after reading the dev outputs, I chose to list the valid
   résumé field names in the prompt (`prompts/revision.txt`). That one line
   is the only difference between the prompts (`diff prompts/baseline.txt
   prompts/revision.txt`).
6. **Revision** run on dev.
7. **Held-out**, both prompts, once, with `--final`. No prompt changes
   afterwards.

All calls ran on 2026-10-30 on `claude-sonnet-5-5`, one fresh tool-less
`claude -p` session per posting.

## Results

| | dev (1 relevant, 9 not) | held-out (0 relevant, 10 not) |
|---|---|---|
| baseline | 9/10 | 9/10 |
| revision | 9/10 | 10/10 |
| always "not relevant" (no model) | 9/10 | 10/10 |
| baseline invalid outputs | 1 | 1 |
| revision invalid outputs | 0 | 0 |
| cites `resume.experience` (baseline → revision) | 3/10 → 10/10 | — |

- Both baseline rejections were invented fields: `resume.experience_years`
  (dev, 7776179) and `resume.experience.years` (held-out, 8155381).
- The one dev failure for the revision is 7776179: Claude said "not
  relevant", stating the posting requires 8+ years. I labeled it relevant.
  **Update 2026-10-31:** looking back, I judge Claude was right and my label
  was wrong. My labeling rule ignored required years. Against my
  *corrected* judgment, every valid verdict from both prompts matched. The
  baseline's 2 invalid outputs gave no verdict at all. That still says
  little, because all 20 are now "not relevant". The committed labels and
  pass rates above are left as they were.

## What the change did

It fixed the problem it targeted. Invalid outputs went from 2 in 20 to 0 in
20, and the citations now match the reasons: every reason talked about
experience, and every revision answer cites `resume.experience`. The drop in
invalid outputs was seen on dev and again on held-out.

It did not change what Claude decides. Every valid verdict from both prompts
on all 20 postings was "not relevant".

## Honest limits

- **The pass rates show almost nothing.** A judge that always answers "not
  relevant" without reading the posting scores exactly what both prompts
  scored. My labeled set has one relevant posting, so it can't tell a good
  prompt from a lazy one.
- **Held-out could only catch false positives.** With 0 relevant postings
  there, it can't test whether Claude finds jobs worth applying to.
- **10 cases per set:** one posting moves the rate by 10 points.
- **0 invalid in 20 isn't "never".** It's 20 calls on one model on one day.
- **The set is imbalanced because of how I drew it.** Most Stripe
  engineering roles on 2026-10-30 were senior or outside the US. I decided to
  keep the set and report this, rather than draw more postings after seeing
  the imbalance.
- **The judge prompt for the agent was picked after held-out.** I switched
  `watch --claude` to the revision prompt after seeing held-out (commit
  6a9b31d). Held-out therefore doesn't count as an independent test of that
  choice.
