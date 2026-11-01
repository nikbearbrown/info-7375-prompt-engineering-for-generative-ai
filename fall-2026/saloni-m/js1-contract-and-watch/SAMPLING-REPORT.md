# Sampling report (Chapter 1)

**What ran (2026-11-01, 19:30–19:31 UTC):** the first 5 development postings × 4 calls each = 20
calls. Each call was a fresh `claude -p` conversation (20 distinct session ids, in
`results/sampling/calls.jsonl`) with no tools, run from an empty temp directory, using the v1
prompt contract (`prompts/v1_baseline.md`) and `--model claude-sonnet-5-5` (the CLI also logs a
`claude-haiku-4-5` helper call in its usage metadata). The four repeats of a posting ran in
parallel, a few seconds apart. Recompute the table with `python3 scripts/score.py sampling`.

| id | title | hand label | rule | Claude, 4 fresh calls | modal share | modal = hand? |
|---|---|---|---|---|---|---|
| 5442680008 | Staff Research Engineer, Multi-Agent Scaling | N | N | N N N N | 4/4 | yes |
| 5157847008 | Staff+ Software Engineer, Platform | N | N | N N N N | 4/4 | yes |
| 5432575008 | Applied AI Engineer, Startups | R | R | N N N N | 4/4 | no |
| 5423737008 | IT Operations Engineer, Asset Management | R | N | N N N N | 4/4 | no |
| 5467083008 | Senior Engineer, Bioinformatics | N | N | N N N N | 4/4 | yes |

R = relevant, N = not_relevant. All 20 outputs passed the validator (0 rejected).

## Spread

- **Verdicts: no spread.** 20/20 calls gave the modal verdict; every posting was 4/4.
- **Citations: real spread.** The verdict never moved, but the résumé fields cited to support it
  did. Across the 4 calls the number of distinct `resume_fields` sets per posting was 2, 3, 4, 2
  and 2. On "Applied AI Engineer, Startups", all four calls cited a different set. Two of them
  cited `search.exclude_title_terms` even though that title has no seniority term. `posting_fields`
  were the same within each posting.

## What I can conclude

- On these 5 postings, under this prompt and model, on this day, the verdict was **repeatable**.
- The justification is **less stable than the verdict**. A justification that changes between
  runs while the verdict stays the same is a reason not to treat a single justification as *the*
  reason.

## What I cannot conclude

- **Repeatable is not correct.** Claude's verdict matched my hand label on 3 of 5 postings, and
  two of those three are the easy "Staff"/"Senior" titles the plain rule also gets right. On
  "Applied AI Engineer, Startups", Claude was unanimous, and unanimously different from my label.
  It cited the posting's 4+ years and customer-facing/pre-sales requirements.
- **Four samples is small.** With 4/4 agreement, a posting whose true flip rate is 10% would still
  show 4/4 about 66% of the time (0.9⁴). This rules out large instability, not small instability.
- Five postings, one board, one persona, one prompt, one model, one day. Nothing here covers other
  prompts (see the prompt experiment), other models, or the same calls on another day.
- The 4 repeats ran in parallel and close together, so the data cannot show variation tied to
  time of day or service load.
