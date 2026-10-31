# Sampling report (Chapter 1)

**Question.** If Claude is asked the same prompt contract about the same posting in separate, fresh conversations, how much do its answers vary? And does a repeated answer tell us it is right?

## What ran

- **When:** 2026-10-31, 09:08:07–09:08:40 EDT, code at `0f3b4af` plus a one-line folder fix (committed in `d2db430`).
- **Command:** `python3 experiments/sample.py --repeats 4`. Output in [terminal](../evidence/terminal/2026-10-31-sampling.txt).
- **Prompt:** `prompts/judge_v1.md`, the same prompt the agent used in run 2.
- **Model and route:** `claude-opus-5-5` through `claude -p`, with tools, settings, MCP servers and saved sessions off. Up to 3 calls ran at once.
- **Fresh conversations:** every call was its own `claude -p --no-session-persistence` process in its own empty temporary folder, so no call could see another.
- **Postings:** 5 real postings from the run-1 baseline. `experiments/select_postings.py` (seed 20261028) chose them before any label existed: 2 the rule calls relevant and 3 it does not, all from the development set.
- **Calls:** 5 postings × 4 = **20 calls**. Every reply is saved verbatim in [experiments/sampling/calls.jsonl](../experiments/sampling/calls.jsonl), and the scores are in [summary.json](../experiments/sampling/summary.json).
- **Cost:** `claude -p` reported $0.24 in total.

## Every verdict

| Posting | Title | Student's label | Rule record | Claude, 4 fresh calls | Valid replies |
|---|---|---|---|---|---|
| 4613568008 | Research Engineer, Machine Learning (Reinforcement Learning) | relevant | relevant | relevant, relevant, relevant, relevant | 4/4 |
| 5418610008 | Data Engineer, GTM | relevant | relevant | relevant, relevant, relevant, relevant | 4/4 |
| 4979585008 | Product Support Specialist | not_relevant | not_relevant | not_relevant ×4 | 4/4 |
| 5198108008 | Research Engineer, Machine Learning (RL Velocity) | not_relevant | not_relevant | not_relevant ×4 | 4/4 |
| 5399158008 | Manufacturing Engineer - Data Center Hardware | not_relevant | not_relevant | not_relevant ×4 | 4/4 |

## How much they varied

**The verdicts didn't vary at all:** 20 of 20 matched the other calls on the same posting, and 20 of 20 matched the student's label.

**What did vary** (from `python3 experiments/describe_calls.py experiments/sampling/calls.jsonl`):

| Posting | Distinct sets of cited fields | Distinct sets of posting quotes | Evidence items per reply | Justification length (words) |
|---|---|---|---|---|
| 4613568008 | 1 | 1 | 9, 9, 9, 9 | 31, 33, 30, 30 |
| 5418610008 | 1 | 1 | 7, 8, 7, 7 | 33, 35, 29, 35 |
| 4979585008 | 1 | 3 | 7, 7, 7, 6 | 32, 41, 37, 35 |
| 5198108008 | 2 | 1 | 6, 7, 7, 7 | 39, 35, 36, 44 |
| 5399158008 | 3 | 3 | 6, 7, 6, 7 | 38, 34, 31, 34 |

The two relevant postings got nearly identical replies. The three not-relevant ones varied more in what they cited. The likely reason: when a condition fails because something is missing ("python" never appears), there is no quote that shows the absence, so each reply picks different passing fields to quote.

## What can and cannot be concluded

**Can:**
- On these 5 postings, with this prompt, model, and route, on this morning, Claude's verdict was repeatable: 4 of 4 agreed every time.
- On these 5 postings, every verdict also equalled the student's label. The labels were committed before the sampling calls (`0f312fb` at 09:05; sampling at 09:08), but after other Claude calls. They were **computed by the student's own script applying the rule, not labeled by hand** (see the README section "The labels were computed by a script").

**Cannot:**
- **Repeatability is not correctness.** Four identical answers would be just as identical if they were all wrong. The only check on correctness here is comparison with the student's labels, on 5 postings, and those labels were computed by a script applying the same rule. So this is agreement with the rule, not independent correctness.
- **This doesn't generalize to the board.** These 5 were chosen to include near-misses, not at random, and 5 postings × 4 calls is a very small sample. A posting where the rule is a close call, like "Data Center Controls Engineer", which is relevant only because "data" is a focus term, could split, and none of those was among the 5.
- **It doesn't hold for other settings.** Variation could differ with another effort level, model version, or route. The `api` route was never run. The chat surface used effort "Max", per the student.
- **The labels check only one thing.** They apply the same rule the prompt describes, so agreement shows that Claude applied the student's rule, not that the rule picks good jobs. The student's Frictional note gives two counter-examples: posting 4616971008 has Python and PyTorch but fails on its title, and posting 5418610008 passes while asking for 5+ years of experience.

## My conclusion

_The student's words, 2026-10-31._

All four calls gave the same verdict for each of the five postings, and all twenty replies passed validation. That shows repeatability under this particular prompt, model, and setup; the quotations and explanation wording still varied. The reference labels were computed by me, so matching them does not provide independent human verification. I take this as evidence that the model consistently applied the rule on these selected postings, not that the rule finds suitable jobs or that the result generalizes to the whole board.
