# What moves the score (JS3 step 2, item 4)

Written by Claude Code on 2026-11-22. Every number below recomputes from the files named.

## The four parts of this step

1. **Where every number comes from:** [`ORIGINS.md`](ORIGINS.md). Every weight and threshold was hand-set by Aravind,
   most of them in his draft 2; the status phrases were inherited from contract v0.2; a few word lists were hand-set by
   Claude Code; Jane's facts come from her profile. Nothing was fitted on labels, and the score has no Claude prompt.
2. **One change to one object at a time:** [`CHANGES-TO-MEASURE.md`](CHANGES-TO-MEASURE.md) lists six changes and an
   identical repeat, with a prediction for each, committed before the held-out answers were opened (`1c9a37e`). The
   tool that measures them was committed before it ran (`bd831c0`); the two switches it needs are absent in v1.0
   (`b8e3a25`).
3. **Measured once, on labels held out:** [`EXPERIMENTS.md`](EXPERIMENTS.md), against Aravind's 30 frozen held-out
   verdicts (`1e2b1e1`), on 2026-11-22 at 08:36 UTC (`cb1b50c`). Every run is kept in `runs/`.
4. **What persistence is not proof of:** the last section of `EXPERIMENTS.md`.

## What the measurement showed

- **v1.0's keep or reject agreed with Aravind on all 27 held-out cards he judged:** 12 of 12 kept, 15 of 15 rejected.
  The exact one-sided 95% bound on the disagreements is 10.5% for this sample.
- **The repeat run was identical, card for card.** The filter has no randomness and calls no model, so there is no
  run-to-run noise to measure, and every run costs $0 at API prices.
- **None of the six changes moved a keep or a reject.** The splitter and company-word fixes (X1, X2) changed nothing
  here; dropping "build systems" (X3) moved 7 scores on the whole run and none here; an export-control penalty (X4)
  lowered three held-out scores, the three cards Aravind marked "?" over export-control lines.
- **The cutoff is what moves the recommendation.** At 60 the run recommends 7 postings and disagrees with Aravind on
  5, all of them postings he kept that scored 50 or 55. At 55 it recommends 9 (24 of 27 agree). At 50 every kept
  posting qualifies: 12 recommended, 27 of 27 agree.
- **The audit said the same before the held-out set was opened:** he kept every kept posting he judged, at 50, 55 and
  60 alike (`ORIGINS.md`).

## What it does not show

A rate for all postings; anything about boards the agent does not watch or about live postings; whether a cutoff of 50
would still agree with him on another day's postings. Two predictions held only in part, and are reported as such.

## What it leads to (FILTER.md v1.1)

- Claude Code's implementation changes X1 (the splitter) and X2 (the company words): adopt. They fix what the audit
  found and changed nothing that was measured.
- Aravind's calls: the cutoff (60, 55 or 50), the export-control line (a caution, or 10 points off) and "build systems"
  (keep or drop).
- A call made from these results turns the held-out set into development data from then on (held-out `CHANGES.md`); a
  later claim about a change would need a new held-out set.

## FILTER.md v1.1 on the whole run

Aravind made the three calls on 2026-11-22 (cutoff 50, an export-control line costs 10 points, "build systems"
dropped), and FILTER.md v1.1 adds them with Claude Code's two implementation changes (`5dff01f`). The filter run
`js3/filter-run/2026-11-22T084738Z/` applies v1.1 to the same 1,509 saved postings. This is development data, not a
new measurement: no labels are involved.

- **No fate changes:** 99 kept, 1,409 rejected and 1 "I cannot tell", the same postings as v1.0.
- **15 kept scores changed:** 9 export-control postings lost 10 points, and 6 postings lost the 5 points "build systems"
  gave them.
- **91 of the 99 kept postings reach the cutoff of 50** (v1.0: 50 reached 60). The 8 that do not are all export-control
  postings.
- **The top 10 lost the two postings behind Aravind's calls:** EDA Cloud & Developer Infrastructure Engineer (its
  export-control line, 70 to 60) and Software Engineer, Ads Integrity ("build systems", 65 to 60). Full Stack Software
  Engineer, Codex and Full Stack Software Engineer, ChatGPT ImageGen took their places.

