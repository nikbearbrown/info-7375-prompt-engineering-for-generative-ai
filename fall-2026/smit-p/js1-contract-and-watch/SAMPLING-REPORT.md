# Sampling report (Chapter 1)

> **Authorship.** Drafted by Claude Code from runs it carried out on 2026-10-24 in Smit P.'s session. The hand labels and the decisions are Smit's (see DECISIONS.md). Every number can be recomputed with `python3 experiments/score.py`.

## Executive summary

Claude Code (in my build session) asked Claude the same question about the same five real job postings four
times each, each time in a brand-new conversation, and compared the answers with each other and with
my own hand label. Claude was almost perfectly consistent: every accepted answer for a
given posting matched the others, and one of the 20 replies was thrown out for breaking
the required format. But consistency is not correctness. On one posting, a Software
Engineer role in São Paulo, Claude said "relevant" all four times and I say it is not,
because an F-1 student's OPT work has to be in the US. Four identical wrong answers are
still wrong. The cause is in my own prompt contract, not in randomness: it never mentions
location.

## Setup

| | |
|---|---|
| Postings | the first 5 of the development set in `experiments/selection.json` (chosen by seeded random sample before any labeling) |
| Question | `prompts/baseline.md` (the CONTRACT.md rule as a prompt contract) plus the persona résumé and one posting |
| Calls | 5 postings × 4 repeats = 20 calls, each a fresh `claude -p` conversation: empty working directory, no tools, no settings, no MCP, no saved session (`src/claude_judge.py`) |
| Model | `claude-sonnet-5-5` (CLI alias `sonnet`), default sampling settings. The CLI does not expose temperature |
| Hand label | `experiments/labels.json`, given by me under `experiments/LABELING-RULE.md` before any prompt ran |
| Raw data | `experiments/results/sampling-baseline.jsonl`: every reply verbatim, accepted or rejected |
| Recompute | `python3 experiments/score.py` → `experiments/results/SCORES.md` |
| Date | 2026-10-24 |

## Results

| posting | title | hand label | rule (record) | Claude r1–r4 (judgment) | accepted | agree with each other | agree with hand label |
|---|---|---|---|---|---|---|---|
| 7716341 | Machine Learning Engineer, Assistance Engineering (China) | not | not | not ×4 | 4/4 | 4/4 | 4/4 |
| 8284841 | Staff Data Engineer, Tech Foundations | not | not | not ×4 | 4/4 | 4/4 | 4/4 |
| 8165656 | Senior Software Engineer, Storage | not | not | not, **REJECTED**, not, not | 3/4 | 3/3 | 3/4 |
| 8154749 | Software Engineer, Tech Foundations (São Paulo) | **not** | relevant | **relevant ×4** | 4/4 | 4/4 | **0/4** |
| 8154705 | Staff Software Engineer, Data Catalog | not | not | not ×4 | 4/4 | 4/4 | 4/4 |

**Spread.** Across 19 accepted replies, no posting got two different verdicts. The only
variation was in form: 1 of 20 replies (5%) was rejected. That reply cited
`devops_cicd[0]` instead of `skills.devops_cicd[0]`, a résumé path that does not exist.
The quoted evidence and the wording of the reason also varied from call to call even when
the verdict did not. For example, on 8154749 all four calls cited the same four skills, but two cited
`experience[0].title` and two did not.

**Agreement with my hand label:** 15/20 replies (75%). All of the disagreement is one
posting, 8154749, which was wrong 4/4.

## What I can conclude

- Under this prompt, on these five postings, Claude's **verdict** is repeatable. Its
  **form** is not perfectly repeatable: about 1 in 20 replies broke the format, and the
  validator caught it.
- The 8154749 error is **systematic, not random**. More samples would not fix it, and a
  majority vote over 4 runs would lock it in. The written rule in CONTRACT.md makes the
  same mistake (rule verdict: relevant). Claude did what the contract said. The contract
  is what disagrees with my judgment, because it has no location check.
- Repeating the same answer showed **repeatability**. Only the comparison with my hand
  label showed **correctness**, and only for these five postings.

## What I cannot conclude

- Anything about postings that are not like these. Four of the five are easy no's (Staff,
  Senior, wrong title). Only one is a hard case.
- That the verdict would stay stable at another temperature, on another model, or on
  another day. I did not control or vary temperature (the CLI does not expose it).
- That 4 repeats are enough to see rare flips. If a verdict flips 1 time in 10, there is
  about a 66% chance (0.9⁴) that four samples never show it.
- Whether Claude actually checked the skills or matched the title and filled in the rest.
  The validator only confirms that what it quoted exists.
