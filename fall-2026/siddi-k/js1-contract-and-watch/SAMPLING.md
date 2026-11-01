# Sampling report (Chapter 1)

**Question:** if Claude is asked the same contract about the same posting in fresh conversations, how much do its verdicts vary, and does a repeated verdict mean a correct one?

## What ran

- **Postings:** the first 5 ids of the `dev` split, in the selection's own order (`experiments/output/label_selection.json`). That rule was fixed before any Claude call; nobody looked at verdicts to pick them.
- **Prompt and invocation:** `prompts/judge_v1.md`, the same prompt as the agent's Claude judge, with the exact command in `config/claude_cmd.txt`.
- **Fresh conversations:** every call is a new `claude -p` process, started in a new empty temp directory with no session persistence, so no call can see another.
- **Repeats:** 4 per posting, `python -m experiments.runner sample --ids <5 ids> --repeats 4`.
- **Records:** each call's raw stdout is in `experiments/output/sampling/judge_v1/`, and each verdict is a line in `experiments/output/sampling.jsonl`.
- **No retries:** an output that fails the validator counts as ✗. The variation is the thing being measured.

## Results

<!-- generated:start -->
| posting_id | title | verdicts in run order (R relevant, N not, ✗ invalid) | modal share | hand label | modal = hand? |
|---|---|---|---|---|---|
| 8333122 | Master's Machine Learning Engineer, Intern | N N N N | 4/4 | (not labelled) | – |
| 8224915 | Machine Learning Engineer, Growth Platform | R R R R | 4/4 | (not labelled) | – |
| 8113100 | Data Scientist, Fraud | N N N N | 4/4 | (not labelled) | – |
| 8194283 | PhD Data Scientist, Intern | N N N N | 4/4 | (not labelled) | – |
| 8333074 | Master's Machine Learning Engineer, Intern | N N N N | 4/4 | (not labelled) | – |

20 calls on 5 postings, prompt `judge_v1`, model claude-sonnet-5-5, run 2026-11-01T02:59 → 2026-11-01T03:00 UTC. 5 of 5 postings got the same verdict on every call. Invalid outputs: 0.
<!-- generated:end -->

## What this can and cannot show

- **Repeatability is not correctness.** Four identical verdicts show that this prompt, this model and this posting give a stable answer *today*. They don't show the answer is right. The only check on correctness here is the hand-label column, and that is one person's label under `LABELING.md`.
- **Small numbers.** 5 postings × 4 calls is 20 calls. A posting that never flipped in 4 calls could still flip on the 5th; 4/4 is weak evidence of stability, not proof.
- **Fixed conditions.** Model, prompt and CLI version were all held fixed. A different model or a reworded prompt is a different experiment.
