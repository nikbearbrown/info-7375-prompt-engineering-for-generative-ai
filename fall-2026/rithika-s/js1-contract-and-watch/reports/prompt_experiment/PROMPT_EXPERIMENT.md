# Prompt experiment (Chapter 2) — Job-Search Agent 1

**Date of runs:** 2026-10-31. **Interface:** Claude Code CLI `claude -p`, one fresh call
per posting per prompt (timestamps and raw replies in `results_*.jsonl`).

## Order of work (each step committed before the next)
1. **Labeling rule** written before labeling: `LABELING_RULE.md`, plus a dated
   amendment adding a US-location condition before any label was saved.
2. **Label sheet v1** (commit a40d97b): 20 random postings. Before labeling, I saw
   almost none could be relevant (base-rate problem), so I discarded it.
3. **Label sheet v2** (065d568): stratified, 10 "plausible" titles plus 10 others,
   with the 10 dev / 10 held-out split fixed by seed 7375 before any labels.
4. **Hand labels** (2b7d3ce), then **corrected** (cb39cee) before any prompt ran.
   Claude pointed out labels that contradicted my own written rule (e.g. a
   TS/SCI-required posting labeled relevant). I re-opened each posting and
   re-labeled it myself. An earlier free-form labeling attempt was discarded for
   the same reason, and I switched to a condition-by-condition tool (`tools/label_v2.py`).
5. **Prompts** committed before any trial (9e5f8b1).
6. **Dev runs** (a8d460e), then **held-out runs last** (ed39877).

## The prompts and the one change
- **Baseline** (`prompts/baseline.txt`): the persona's target roles, shipped skills,
  education/experience, the clearance exclusion, the posting, and a fixed JSON
  output contract.
- **Revision** (`prompts/revision.txt`): identical, except for **one added section**,
  "Hard constraints": US-only, needs sponsorship, at most 2 years of required
  experience, and engineering/data roles only.
- Question: does stating the persona's hard constraints make Claude agree more
  with my hand labels?

## Results as pre-registered (labels as committed)

| prompt | dev (10) | held-out (10) |
|---|---|---|
| baseline | 9/10 | 10/10 |
| revision | 9/10 | 8/10 |
| comparison: always answer "not_relevant" | 9/10 | 8/10 |

All 40 replies passed the validator (0 rejected). On held-out, the revision said
not_relevant to both postings I had labeled relevant, so it scored no better than
always answering "not_relevant".

## Post-hoc label audit (after all runs — not part of the pre-registered result)
Claude's reasons disagreed with three of my "relevant" labels. I did not take
Claude's word for it; I extracted the relevant sentences from the saved raw
response (`label_audit_evidence.txt`) and judged each one myself:

| posting | what the posting says | my decision |
|---|---|---|
| 4730836005 New Grad (dev) | "Requirements: A graduation date in Fall 2026 or Spring 2027…" | **Rule gap.** My rule has no graduation condition; the persona graduated in 2025-12, so she is not eligible. Truly not relevant. |
| 4720573005 Frontier Agents Engineer, Applied AI (held-out) | "Required Qualifications: 4+ years…" | **My labeling error.** My note said "0–1 yrs"; under my condition 4 it is not relevant. |
| 4722512005 Software Engineer – AI Enablement (held-out) | "Ideal Experience: 3+ years…" | **Label stands.** "Ideal" is preferred, not required, so it passes condition 4. |

Rescored with the two corrections (post-hoc, for interpretation only):

| prompt | dev | held-out |
|---|---|---|
| baseline | 10/10 | 9/10 |
| revision | 10/10 | 9/10 |
| always "not_relevant" | 10/10 | 9/10 |

## What this shows, and how little
- **As pre-registered,** the baseline did better on held-out (10/10 vs 8/10). After the
  audit, the two prompts **tie**, and neither beats always answering "not_relevant".
  Most of the apparent difference came from my labeling errors, not from the prompts.
- **The one real behavioral difference:** the revision's "at most 2 years of required
  experience" led Claude to treat "Ideal Experience: 3+ years" as a requirement.
  The baseline read it as preferred, as I did.
- **Ten cases show very little.** The held-out set has 2 relevant postings as
  labeled, 1 after the audit. A one-posting swing moves a score by 10 points. With
  this base rate, a lazy prompt scores 80–100%. I cannot claim the change helped
  or hurt in general.
- **Other limits:** one board (Scale AI), one fictional persona, one labeler (me),
  one call per posting per prompt, all on one day. Location and graduation windows
  are not in the agent's own rule (`CONTRACT.md`) either.
- **The most useful result was about evaluation, not prompting.** Claude's reasons
  exposed one error in my labels and one gap in my rule, and I could verify both
  in the raw posting text. The score was only as good as my labels.

## Not run (ideas for the next layer, clearly not results)
- A revision distinguishing required from preferred experience.
- Adding a graduation-window condition to the labeling rule and the prompt.
- More held-out cases with more relevant postings, and repeated runs per prompt.
