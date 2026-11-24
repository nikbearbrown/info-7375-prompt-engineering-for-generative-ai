# EVAL-PLAN — Readback (PLANNED, 2026-11-23)

**Status: PLANNED. Nothing in this file has been run.** As of 2026-11-23 the repo holds no judge outputs, no human labels and no agreement results. Every number below is a plan setting, not a result.

Items marked **(decided)** were proposed by Claude Code and approved by Aravind on 2026-11-23. This file is committed **before** any judge or labelling run, so the git history shows the plan came first.

## What gets judged

- **Feature under test:** the 10 real recaps in `../../case-study/outputs/feature-run/*.json` (`claude-opus-5-5`, 2026-10-14), one per AMI meeting.
- **Rubric:** `../../case-study/constructed/rubric-v0.md` (CONSTRUCTED). Five pass/fail clauses, C1–C5.
  - **C1 (decisions complete) is the anchored clause.** Its reference is each meeting's human-written DECISIONS list in `../../case-study/data/sample/<meeting>/summary.txt`, 86 decisions across the 10 meetings (`selection.csv`).

## Judges (3)

| Judge | Access | Status on 2026-11-23 |
|---|---|---|
| Claude | `claude -p` on Aravind's subscription (or API credits) | CLI verified installed (2.1.323) |
| A second provider's model | Aravind's second-provider access | confirmed by Aravind; not configured on this machine |
| A local open-weight model | Ollama (free, local) | **installed 2026-11-23 (0.40.17); no model pulled; not yet wired as a judge** |

Each judge scores every recap on every clause, pass or fail. For C1 it also marks each of that meeting's AMI decisions as covered or missing.

## Human labels (anchored clause only) (decided: proposal A)

- **Proposal A:** Aravind marks each of the 86 AMI decisions as covered or missing in the matching recap, then commits the labels before any judge runs.
  - C1's human pass/fail per recap follows from the marks: pass only if all of that meeting's decisions are covered.
- **Alternative B:** derive coverage automatically from AMI's summary-to-transcript links (`extractive/*.summlink.xml`). A decision counts as covered if a recap item cites a timestamp inside AMI's linked span. This needs no hand labelling, but it's approximate.

## Agreement measures

- **Judge vs judge:** on every clause, pairwise percent agreement and Cohen's kappa across the 10 recaps.
- **Judge vs human:** on C1, Cohen's kappa per judge, over the 86 decision items (covered or missing).

## Check 1 — planted ambiguity

- **Method:** copy the rubric and make exactly one clause deliberately vague. The seeded clause is recorded in this file before the run.
  - **(decided)** Run one variant per clause: five variants, C1–C5.
- **Pass:** Readback attributes the disagreement to the seeded clause, in every variant.
- **Fail:** it attributes the disagreement to a different clause, or the disagreement isn't concentrated on any clause (noise).

## Check 2 — anchored-clause agreement

- **Statistic:** Cohen's kappa, judge vs human labels, on C1's 86 decision items.
- **Pass:** κ ≥ 0.6 for a judge. **(decided)** Threshold proposed by Claude Code, approved by Aravind 2026-11-23, fixed before any run.
- **Fail:** κ < 0.6. That judge isn't trusted on C1.
- **Result:** — (will be measured).

## Check 3 — before and after

- **Method:**
  1. Fix and commit a held-out split of the 10 meetings before any revision. **(decided)** The split is fixed before revision; its size will be set here, before any revision, and isn't shown in the film.
  2. Readback flags a clause and asks the PM a question.
  3. The PM revises that clause from their answer.
  4. Re-measure judge–judge agreement on that clause on the held-out recaps.
- **Pass:** agreement on the revised clause rises on the held-out recaps.
- **Fail:** it stays the same or drops. Readback didn't help, and that is reported.
- **Result:** — (will be measured).

## Reporting

Every check is reported, including failures, with its date, the models used and the commit that ran it. Until a check runs, its scorecard cell stays empty: "—", will be measured.
