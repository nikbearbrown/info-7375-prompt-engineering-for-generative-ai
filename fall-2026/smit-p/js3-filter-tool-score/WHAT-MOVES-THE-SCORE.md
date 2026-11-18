# What moves the score

> **Authorship.** Claude drafted this report, wrote both prompts, and chose the
> configurations. The labels it measures against are Smit's (`audit/hand-verdicts.json`).
> Every Claude reply below was actually received on 2026-11-14 US Eastern time (timestamps
> 2026-11-15 00:26–00:29 UTC in `experiments/results/*.jsonl`). Recompute:
> `python3 src/measure_filter.py --run-id live-20261114` and `python3 experiments/run_claude.py --score`.

## Executive summary

This agent has numbers in it: thresholds, weights, word lists, a Claude prompt. This report
says where each one came from. It then changes **one object at a time** and measures the
effect on postings Smit labeled but nothing was tuned on (the 33 held-out postings).

- **The filter file** mattered most. One wrong definition, how to read "5+ years …
  including 3+ years", caused 3 of the filter's 6 keeps to be wrong.
- **The prompt:** one added sentence telling Claude to abstain when years or level are not
  stated removed Claude's one wrong "keep", at the price of abstaining on a job Smit
  judged relevant.
- **The context:** giving Claude the tool's summary instead of the posting text made it answer
  "cannot_tell" on 6 of 33 postings instead of 0.
- **The setting:** switching from Sonnet to Haiku changed almost nothing on these 33.
- **Persistence:** the same configuration run twice gave a different answer on 1 posting
  in 33. Nothing here is trained, so neither a change nor a non-change across sessions is
  evidence of learning.

## Where every number came from

| Object | Number or setting | Value | Origin |
|---|---|---|---|
| filter | skill threshold (R6) | 2 → **1** in v1.1 | **inherited** from Job-Search Agent 1, where Smit hand-set it; changed to 1 by Smit after measuring on the dev labels (FILTER.md change C) |
| filter | years cut-off (R5) | 4 | **hand-set** by Smit, from his labeling rule ("up to 3–4 years") |
| filter | which years number counts | smallest → **largest** in v1.1 | **defined by Claude** in v1.0 (an untested guess), replaced after measuring (change A) |
| filter | role words, seniority words | lists in FILTER.md | **hand-set**: Smit chose the families; Claude wrote the exact lists |
| filter | intern / internship / PhD as level words | added in v1.1 | **chosen on dev labels** by Smit (change B) |
| filter | US markers, "Remote"-only rule, sentence windows | FILTER.md R4, R5 | **defined by Claude**, never measured on their own |
| score | points per skill / title bonus | 1 / 2 | **hand-set** by Smit (chosen option); never measured, because the shortlist has 3 postings |
| audit | seed, sample size, split | 7375 / 30 / 50% | seed and split **chosen by Claude**; 30 is the assignment's minimum |
| audit | interval | exact 95% Clopper–Pearson | convention |
| Claude judge | model | `claude-sonnet-5-5` | **chosen by Claude**, inherited from Job-Search Agent 1 |
| Claude judge | prompt | `prompts/judge-baseline.md` | **written by Claude** from FILTER.md, before any call (`18474fdc`) |
| Claude judge | reply rules | one JSON object; quotes must appear verbatim in the context | **set by Claude**; 0 of 165 replies were rejected |

**Fitted on labels:** nothing was fitted numerically. Three filter changes were *selected* by
Smit after seeing dev results; that is the closest thing to fitting here.

## One change at a time

### The filter file (dev chosen, held-out reported). Full table in FILTER.md

| Change from v1.0 | Dev errors (38) | Held-out errors (33) |
|---|---|---|
| none (v1.0) | 7 | 3 |
| A: largest years number | 4 | 3 |
| B: interns are a level | 6 | 3 |
| C: 1 skill is enough | 6 | 4 |
| D: allow "Manager, Software Engineering" | 7 | 3 |
| v1.1 = A + B + C | 2 | 3 |

On held-out, the adopted changes neither helped nor hurt: 3 errors before and after. The
three errors that remain are titles outside the role words, and an Android job with no
résumé skills. The gains are on dev, where they were chosen. That is weaker evidence.

### Claude as a judge: prompt, context, setting (held-out only, 33 postings each)

| Config | One object changed | Right | Wrong keep | Wrong reject | cannot_tell | Reply rejected |
|---|---|---|---|---|---|---|
| baseline | — | 30 | 1 | 2 | 0 | 0 |
| prompt | **prompt**: one sentence added (`prompts/judge-cannot-tell.md`) | 29 | **0** | 2 | 2 | 0 |
| context | **context**: the `score_posting` tool's output instead of the posting text | 26 | 0 | 1 | **6** | 0 |
| setting | **setting**: model Haiku 5.5 instead of Sonnet 5.5 | 29 | 1 | 2 | 1 | 0 |
| baseline-repeat | nothing (same config, second session) | 29 | 1 | 2 | 1 | 0 |

Cost of all 165 calls: $1.46 (`cost_usd` in each record).

**Which postings moved** (`experiments/results/*.jsonl`):

| Posting (Smit's verdict) | baseline | repeat | prompt | context | setting |
|---|---|---|---|---|---|
| Figma · Software Engineer - Full Stack (relevant) | keep | **cannot_tell** | cannot_tell | cannot_tell | cannot_tell |
| Figma · Support Engineer, AI Infrastructure (not relevant) | **keep** | keep | **cannot_tell** | cannot_tell | keep |
| Figma · Forward Deployed Engineer (relevant) | reject | reject | reject | cannot_tell | reject |
| Figma · Field / Data & Integration / AI Engineer (3 postings, not relevant) | reject | reject | reject | **cannot_tell** | reject |
| Figma · Manager, Software Engineering - Design Systems (relevant) | reject | reject | reject | reject | reject |

What each change shows:

- **Prompt.** The added sentence did what it says. The one wrong keep (a 3+ year Support
  Engineer role with no stated level) became "cannot_tell". So did the Full Stack job
  Smit wanted, which states neither level nor years. The prompt moved errors into
  abstentions. It did not make Claude more right.
- **Context.** Given only the filter's evidence (title, location and quotes, without the
  description), Claude abstained on near-miss titles, because the tool output for a title
  reject holds no description. Less context made it more cautious, not more wrong. It also
  stopped being an independent check, since it saw only what the filter chose to show.
- **Setting.** Haiku agreed with Sonnet on 32 of 33. Haiku's 33 calls cost $0.03; Sonnet's
  cost $0.52 in the baseline and $0.15 in the identical repeat (prompt caching lowers repeat
  runs, so cost is not a property of the model alone). On this evidence, the cheaper model
  would do for this task.
- **Not done: the tool list.** Giving Claude the `score_posting` tool as an extra object was
  run only as a demonstration (`TOOL-SERVER.md`), not measured on held-out labels.

## What persistence is not proof of

The baseline configuration was run twice in separate, fresh sessions: same prompt, same
context, same model, no memory, `--no-session-persistence`. It answered differently on 1
posting of 33 (Figma Full Stack: "keep", then "cannot_tell", with different reasons). So:

- A changed answer across sessions here came from sampling, not from anything learned. No
  weights were updated, no memory was kept, and no file Claude could see changed between
  the two runs.
- An answer that *persists* after the prompt changes (the Design Systems manager role is
  "reject" in all five) shows that this model, given this text, keeps reaching the same
  answer. It does **not** show the model was trained on anything here. Nothing in this
  project trains a model.
- The filter did not "learn" either. Version 1.1 is a file Smit chose to edit after
  measuring, and `git log -- FILTER.md src/filter.py` shows each edit.

## Limits

- 33 held-out postings, 4 of them labeled relevant: one posting changing is a 3-point swing.
- The prompt revision was written after seeing the shortlist analysis (Full Stack: no years,
  level decided later) but before seeing any Claude results. It still targets a pattern
  that also appears in the held-out set.
- One run per configuration, apart from the baseline. The repeat shows a run can differ by
  at least one posting, so a 1-posting difference between configurations is within noise.
