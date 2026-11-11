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
| 8333122 | Master's Machine Learning Engineer, Intern | N N N N | 4/4 | not_relevant | yes |
| 8224915 | Machine Learning Engineer, Growth Platform | R R R R | 4/4 | relevant | yes |
| 8113100 | Data Scientist, Fraud | N N N N | 4/4 | not_relevant | yes |
| 8194283 | PhD Data Scientist, Intern | N N N N | 4/4 | relevant | no |
| 8333074 | Master's Machine Learning Engineer, Intern | N N N N | 4/4 | relevant | no |

20 calls on 5 postings, prompt `judge_v1`, model claude-sonnet-5-5, run 2026-11-01T02:59 → 2026-11-01T03:00 UTC. 5 of 5 postings got the same verdict on every call. Invalid outputs: 0.
<!-- generated:end -->

## What happened

- **Spread: none.** All 5 postings got the same verdict on all 4 calls (20/20 identical within posting), with no invalid outputs.
- **Correctness: 3 of 5.** The unanimous verdict matched Siddi's hand label for 3 postings. It disagreed, **unanimously and 4 times out of 4**, on the two internships Siddi labelled relevant:
   - 8333074, Master's ML Engineer Intern;
   - 8194283, PhD Data Scientist Intern.
- **Why they differ.** Claude's justifications say both internships require *current enrollment* in a master's or PhD program, and the persona's `highest_degree` is bachelors. Siddi's `LABELING.md` counts "Masters or some internships".
- **What that means.** This is the chapter's point in miniature: four identical answers were four identical answers to a different question than the labeller's, so the repetition carried no information about correctness.

## What this can and cannot show

- **Repeatability is not correctness.** Four identical verdicts show that this prompt, this model and this posting give a stable answer *today*. They don't show the answer is right. The only check on correctness here is the hand-label column, and that is one person's label under `LABELING.md`.
- **Small numbers.** 5 postings × 4 calls is 20 calls. A posting that never flipped in 4 calls could still flip on the 5th; 4/4 is weak evidence of stability, not proof.
- **Fixed conditions.** Model, prompt and CLI version were all held fixed. A different model or a reworded prompt is a different experiment.
