# EXPERIMENT-PLAN.md — sampling report and prompt experiment

Written 2026-10-26, before any sampling or experiment run.
Claude (chat) suggested these choices; I (Swathi) reviewed and approved them.
Judge: Claude via Claude Code `claude -p`, model pinned to claude-opus-5-5,
one fresh conversation per call, as in JUDGE-CONTRACT.md.
My labels: labels/LABELS.csv (commit 778614a), made before any of these runs.

## 1. Sampling report (baseline prompt only)
5 hard postings from the DEVELOPMENT set, each judged 4 times in 4 fresh
conversations (20 calls):
- 8546367002 — AI role, but "not intended for new graduate or entry-level"
- 8760167002 — requires US citizenship and secret clearance
- 8735590002 — no years of experience stated
- 8199399002 — "Analyst" title, legal ops role
- 8692962002 — data engineering role, asks 6+ years
Every verdict, quote and rejected reply is recorded. For each posting I report
how many of the 4 verdicts agree with my label, and whether the quotes changed
between calls.

## 2. Prompt experiment
Baseline: prompts/judge-baseline.txt (as committed, prompt_sha256 2a8cc6eb...).
Revision (ONE change): add this sentence to the baseline, nothing else:
"The standard export-control 'Compliance' paragraph is not a citizenship,
clearance, or sponsorship requirement; do not quote it as authorization_found."
Why: in the first 3 live calls, Claude quoted that paragraph as
authorization_found in 2 of 3 replies.

Measures (fixed now):
A. Verdict agreement: number of postings where Claude's verdict matches my label.
B. Authorization quote correct: authorization_found is "none stated" for every
   posting except 8760167002, where it must quote the real citizenship /
   clearance sentence, not the Compliance paragraph.
A rejected (invalid) reply counts as wrong on both measures.

Order:
1. Run baseline and revision once per posting on the 10 DEVELOPMENT postings.
2. Pick the prompt to keep from the development results (B decides if A ties).
3. Then run both prompts once per posting on the 10 HELD-OUT postings, one
   time only, and report the numbers as they come. No prompt changes after
   seeing held-out results.

## Limits (stated before running)
- All 20 of my labels are "not relevant", so a judge that always says
  not_relevant scores 10/10 on measure A. The experiment cannot show whether a
  prompt finds relevant jobs.
- Ten postings per set, one call per posting per prompt: a difference of one
  or two postings may just be sampling variation (see the sampling report).
- Only one posting (8760167002) has a real citizenship requirement, so
  measure B mostly tests whether Claude avoids a false one.
