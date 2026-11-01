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
| prompt | split | agree with hand labels | 95% Wilson interval | invalid outputs |
|---|---|---|---|---|
| `judge_v1` | dev | 8/10 | 49%–94% | 0 |
| `judge_v1` | held_out | 8/10 | 49%–94% | 0 |
| `judge_v2` | dev | 8/10 | 49%–94% | 0 |

**dev**

| posting_id | title | hand | `judge_v1` | `judge_v2` |
|---|---|---|---|---|
| 8333122 | Master's Machine Learning Engineer, Intern | N | N | N |
| 8113100 | Data Scientist, Fraud | N | N | N |
| 8333074 | Master's Machine Learning Engineer, Intern | R | N ✗ | N ✗ |
| 8224915 | Machine Learning Engineer, Growth Platform | R | R | R |
| 8194283 | PhD Data Scientist, Intern | R | N ✗ | N ✗ |
| 8258078 | Account Executive, Commercial Hunter, AUNZ | N | N | N |
| 7396679 | Software Engineer, Secrets Infrastructure | N | N | N |
| 7893199 | Account Executive, Cross Border China | N | N | N |
| 8124304 | Staff Product Manager, Stripe Tax | N | N | N |
| 8264421 | Engineering Manager - Support Experience | N | N | N |

**held_out**

| posting_id | title | hand | `judge_v1` |
|---|---|---|---|
| 8144196 | AI Engineer | R | N ✗ |
| 8222149 | Data Scientist | R | N ✗ |
| 8243617 | Machine Learning Engineer, Radar | R | R |
| 8328664 | PhD Machine Learning Engineer, Intern | N | N |
| 8194285 | PhD Data Scientist, Intern | N | N |
| 8195440 | Product Manager, Connect Growth & Monetization | N | N |
| 7392697 | Product Manager, Link - Consumer | N | N |
| 8112043 | Staff Software Engineer, Risk Data Engineering | N | N |
| 8224620 | Strategy & Operations Business Partner, Customer Success | N | N |
| 7369543 | Backend/API Engineer, Money as a Service (Product) | N | N |

R relevant, N not relevant; a trailing ✗ marks disagreement with the hand label.
<!-- generated:end -->

## What happened (2026-10-31, 23:19–23:22 ET)

- **Dev tie.** `judge_v1` and `judge_v2` both scored **8/10 on dev**, with the same verdict on every dev posting. The added seniority sentence changed nothing on these ten.
- **Final prompt.** Under the tie rule fixed before running, `judge_v1` stayed final.
- **Held-out.** `judge_v1` scored **8/10**, run once.
- **All four misses go the same way.** In every one, Siddi labelled the posting relevant and Claude said not relevant:
   - **Two dev internships**, 8333074 and 8194283. Claude: they require current master's or PhD enrollment, and `highest_degree` is bachelors.
   - **8144196, AI Engineer, Chicago.** Claude: 4+ years required against 2, and Chicago is not in `preferred_cities`.
   - **8222149, Data Scientist, Seattle.** Claude: a master's + 5 years, or a bachelor's + 7, required against 2 years.
- **Most of these are disagreements about the persona, not about Claude.** `LABELING.md` says "Anywhere in usa" and accepts master's roles and some internships. The prompt instead hands Claude the persona's `preferred_cities` and `highest_degree: bachelors`, so Claude applied the persona and Siddi applied the labelling rule. A revision that would plausibly move the score is to put the labelling rule's location and degree stance into the persona or the prompt. The seniority sentence tested here does not. That is a next experiment, not a result.

## Honest limits

- **Ten cases per split.** One posting flipping moves a pass rate by 10 points. The 95% intervals above are wide for this reason. A difference of one or two postings between prompts is not evidence that one prompt is better.
- **The labels are one person's**, made in one sitting against a rule that person wrote. Disagreement with Claude can mean Claude is wrong, the label is wrong, or the rule doesn't decide the case.
- **The revision overlaps the labelling rule.** If `LABELING.md` also treats seniority as decisive, judge_v2 pushes Claude toward that rule, so higher agreement would show alignment with the rule, not better judgment.
- **The held-out set is small and from the same board on the same day** as dev, so it can't show how the prompt does on other companies or later postings.
