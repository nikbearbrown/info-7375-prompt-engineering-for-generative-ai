# Prompt experiment (Chapter 2)

## Set-up

- **Labelling rule:** `LABELING.md`, written by Siddi and committed before any posting was labelled.
- **Labels:** 20 real Stripe postings in `labels/hand_labels.jsonl`, labelled by hand by Siddi.
- **Selection and split:** chosen by the contract's seed-42 code from the baseline board `raw/2026-10-31T10-48-38Z/board.json`, then split 10 `dev` / 10 `held_out` (`experiments/output/label_selection.json`).
- **Baseline prompt:** `prompts/judge_v1.md`, the prompt contract the agent's Claude judge uses.
- **Revision:** `prompts/judge_v2.md`, with exactly one change, an added sentence:

  > A posting is not worth the candidate's time if it is clearly more senior than the candidate (a senior, staff, principal, lead, manager, director, head or VP title, or a minimum experience requirement above years_experience + 2), even when the skills match.

  The change was chosen and committed **before** any experiment result existed. The deadline left no time to iterate on dev results, so this is a pre-registered single change, not one tuned to dev.
- **Order:**
  1. `judge_v1` on dev.
  2. `judge_v2` on dev.
  3. Freeze the final prompt: whichever scores higher on dev, with judge_v1 winning a tie (the rule was fixed before running).
  4. Score `held_out` once with that final prompt (`python -m experiments.runner score --prompt <p> --split held_out` refuses a second scoring).
- **Fixed for every call:** the model, the invocation and the requirements text (the contract's text preparation, boilerplate v2). There are no retries; an invalid output counts as a miss.

## Results

<!-- generated:start -->
_No experiment runs yet._
<!-- generated:end -->

## Honest limits

- **Ten cases per split.** One posting flipping moves a pass rate by 10 points. The 95% intervals above are wide for this reason. A difference of one or two postings between prompts is not evidence that one prompt is better.
- **The labels are one person's**, made in one sitting against a rule that person wrote. Disagreement with Claude can mean Claude is wrong, the label is wrong, or the rule doesn't decide the case.
- **The revision overlaps the labelling rule.** If `LABELING.md` also treats seniority as decisive, judge_v2 pushes Claude toward that rule, so higher agreement would show alignment with the rule, not better judgment.
- **The held-out set is small and from the same board on the same day** as dev, so it can't show how the prompt does on other companies or later postings.
