# Sampling report (Chapter 1)

**What ran (2026-10-31, 23:50:23–23:50:40 UTC, from `called_at` in the results file):** 5 real Databricks postings (#1–#5 of my 20 hand-labeled postings,
the first five of the development set), each sent to Claude **4 times**, every call a fresh conversation
(`claude -p`, model `claude-sonnet-5-5`, no tools, no MCP, no settings, no saved session, run from an empty
temp directory). The prompt is `experiments/prompts/v1_baseline.md`. Every reply, including session ids and
the raw text, is in `experiments/results/sampling_v1.jsonl`. The table is recomputed by
`python3 -m experiments.summarize`.

| # | title | my hand label | Claude, 4 fresh calls | agree with me |
|---|---|---|---|---|
| 1 | Manager, Field Engineering France - Specialist Solutions Architects | not_relevant | not, not, not, not | 4/4 |
| 2 | Sr. Software Engineer - Storage I/O (Amsterdam) | not_relevant | not, not, not, not | 4/4 |
| 3 | Solutions Engineer (New York City) | **relevant** | relevant, relevant, **not**, **REJECTED** | 2/4 |
| 4 | Software Engineer - New Grad, Distributed Data Systems (2027 Start) | **relevant** | not, not, not, not | **0/4** |
| 5 | Data+AI Workforce Transformation Practitioner | not_relevant | not, not, not, not | 4/4 |

## How much did it vary?

- **4 of 5 postings: no variation.** Same verdict on all 4 calls.
- **Posting #3 varied.** Two calls said relevant (citing Python and SQL, the Databricks Genie agent, the MS degree).
  One said not relevant, citing "2+ years of customer-facing solutions engineering" against an 8-month internal co-op.
  The fourth reply said `relevant`, but the validator **rejected** it because its justification was longer than
  600 characters. The prompt asks for "at most 2 sentences" but never states the 600-character limit the
  validator enforces. That mismatch is mine, not Claude's (see FRICTIONAL.md).
- **Overall:** 19 of 20 calls gave a valid verdict and 1 was rejected. 14 of 20 agreed with my label.
- **The reasons varied less than the verdicts.** All four #3 replies cited the same résumé fields (`skills.languages`,
  `skills.data_bi`, `experience`, `education`) and **all four named the same gap**, "2+ years customer-facing". They differed only in
  how they weighed it: "only partly met … a reasonable fit" (call 1), "a stretch, but … a reasonable fit" (call 2), "the experience
  gap makes it a poor fit" (call 3), "a gap … but a soft preference" (call 4). So the cited fields don't determine the verdict, and a
  validator that checks only which fields are cited can't tell these replies apart.

## What I can conclude

- **Repeatable is not correct.** Posting #4 is the clearest case. Claude was perfectly consistent (4/4 not relevant)
  and **disagreed with my label every time**. When I checked, Claude was right and my label was wrong. The posting is for people who
  "will graduate in Fall 2026 or Spring 2027", and Arya's résumé says `education.end_date: 2025-12`. It also asks
  for Java or C++, and Arya lists Python and SQL. I labeled from a summary that showed "new grad, Java or C++" but not
  the graduation window. My label stays `relevant` in `labels/hand_labels.csv` because it was committed (c665200)
  before any Claude call, and changing it after seeing Claude's answer would contaminate the experiment.
- **Consistency on easy cases means little.** #1, #2 and #5 are obvious no's (a manager role in Paris, a senior role in
  Amsterdam, and a non-technical role). Any judge gets them right, so 4/4 there shows the format holds, not that the
  judgment is good.
- **On a borderline posting (#3), a single call is not a verdict.** A one-call agent would have reported #3 as
  relevant or not depending on the draw.

## What I cannot conclude

- Whether Claude is "accurate" in general: 5 postings × 4 calls is 20 calls on one board, one persona and one model.
- Anything about temperature or seeds. `claude -p` doesn't expose them, so the variation reflects whatever the CLI
  defaults are on 2026-10-31.
- That 4 calls is enough to see all the variation. #3 might split differently over 20 calls.
