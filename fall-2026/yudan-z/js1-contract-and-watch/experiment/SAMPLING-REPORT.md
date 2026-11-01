# Sampling report (Chapter 1)

## Executive summary

I asked Claude the same contract question about the same five real postings four times each, every time in a fresh conversation (20 calls, 2026-10-30). The verdicts barely moved: 19 of 20 answers were valid, and in every posting all valid answers agreed. But on one posting, the Robinhood fraud analyst, all three valid answers agreed with each other and **disagreed with my hand label**. Repeating the same answer showed the answer is repeatable. It did not show the answer is right.

## Setup

- **Postings:** #1, #3, #4, #9, #10 from the **development** split only, so the held-out set stayed unseen.
- **Prompt:** `prompts/contract_v1.txt`, the baseline contract with R1–R9 and the fixed JSON format.
- **Calls:** 4 per posting, each a separate `claude -p` process (no shared conversation, no tools). Run 2026-10-30, 23:38–23:40 UTC.
- **Validator:** `agent/judge.py validate_answer`. An answer that breaks the format counts as `invalid` and is never repaired.
- **Command:** `python -m experiment.sampling --ns 1 3 4 9 10 --times 4`
- **Raw answers:** `experiment/results/sampling.json` (every raw reply, with a timestamp)

## Results

| # | Posting | My hand label | Try 1 | Try 2 | Try 3 | Try 4 | Agreement with my label |
|---|---|---|---|---|---|---|---|
| 1 | Affirm — Analyst, Early Career | not_relevant | not_relevant | not_relevant | not_relevant | not_relevant | 4/4 |
| 3 | Stripe — Data Analyst, Intern | relevant | relevant | relevant | relevant | relevant | 4/4 |
| 4 | Robinhood — Fraud Investigations Analyst | **relevant** | not_relevant | *invalid* | not_relevant | not_relevant | **0/4** |
| 9 | Pinterest — Software Engineer II, Data Analytics | relevant | relevant | relevant | relevant | relevant | 4/4 |
| 10 | DoorDash — Data Analyst, In-Store | relevant | relevant | relevant | relevant | relevant | 4/4 |

- **Spread in the verdict:** none among valid answers. Every posting got one verdict whenever the answer was valid.
- **Spread in format:** 1 of 20 was invalid (#4, try 2: justification over 400 characters).
- **Spread in the reasoning:** for #1, three answers cited R6 ("visa sponsorship is not available") and one led with R1 (title). The verdict was stable while the cited reason moved.

## What I can conclude

- With this prompt, Claude's verdict on these five postings is **repeatable**: four independent conversations gave the same verdict.
- About 1 in 20 answers breaks the output contract, so the validator is needed. Without it, the bad answer would have been coerced into something.

## What I cannot conclude

- **Correctness.** #4 is the counter-example. Claude was consistently "wrong" against my label because it followed R1 literally: the title "Fraud Investigations Analyst" contains none of my target roles. Repetition measured agreement with itself, not with me.
- **Anything beyond five postings, four tries, one day, one prompt.** Four samples cannot show a rare flip. A 1-in-10 disagreement would often not appear in 4 tries.
- **Whether the cited reason is the real reason.** The justification is the model's account of its verdict, not a trace of how it decided.

## A run I discarded

My first sampling run (kept in `results/superseded-truncated-input/`) sent each posting truncated at 6,000 characters. On #1 that hid the sponsorship sentence, and 2 of 4 answers were invalid. After the fix, all four #1 answers cite that sentence. The discarded run's numbers are not used above.
