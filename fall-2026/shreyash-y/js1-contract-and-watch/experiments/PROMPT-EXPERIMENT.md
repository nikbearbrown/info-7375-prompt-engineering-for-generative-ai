# Prompt experiment (Chapter 2)

> **See also [experiment 2](experiment-2/EXPERIMENT-2.md)**, added on 2026-10-31 after review. It runs the same two prompts on 20 fresh Klaviyo postings, 4 of them hand-labeled Relevant, with per-condition labels committed before any call. That answers the main limit of this experiment: a set with no positives can't test finding a match.

*Written by Claude Code on 2026-10-31 from the saved calls and the two score files: `experiments/prompt-experiment/score-development-2026-10-31.txt` and `score-held-out-2026-10-31.txt`.*

## Order of work, with commits

| Step | Commit | What was fixed before the next step |
|---|---|---|
| 20 postings picked, seeded, split 10 development / 10 held-out | `20041e3` | the list and the split ([selected_postings.json](selected_postings.json), [select_postings.py](select_postings.py)) |
| Baseline prompt contract written | `6d74630` (with the code) | [prompts/baseline-v1.md](../prompts/baseline-v1.md) |
| Shreyash's labeling rule and 20 labels | `b3faea5` | [labels/LABELING-RULE.md](../labels/LABELING-RULE.md), [labels/hand-labels.csv](../labels/hand-labels.csv) |
| Baseline and revision on development; revision written after reading the baseline's development answers | `5c34654` | [prompts/revision-1-quote-evidence.md](../prompts/revision-1-quote-evidence.md) |
| First call on any held-out posting, both prompts | `9402a60` | — |

No Claude call touched a held-out posting before `5c34654` was committed. The selection script never looked at content or verdicts.

## The labels and the pass mark

- **The labeling rule is Shreyash's,** in Shreyash's own words in LABELING-RULE.md, and it is the contract's six conditions.
- **The labels are all Not Relevant.** All 20 postings got that verdict, with no per-condition labels.
- **Pass mark:** an answer passes when it passes the validator **and** its verdict equals the hand label.
- **Second score, not a pass mark:** whether Claude's failed-condition set equals the rule's record. The record is recomputable but is not a hand label, and this experiment found it wrong in places (below).

## The one change

The baseline and revision-1 differ in one sentence of the output format, which is the justification instruction (`diff prompts/baseline-v1.md prompts/revision-1-quote-evidence.md`). Revision-1 adds:

> for every failed condition, quote in double quotes the exact words from the posting that make it fail, or write not stated when the failure is that the posting does not mention something

- **Why this change.** On development, the baseline already passed 10/10, so no change could raise the pass mark. What the development answers lacked was anything a person could check quickly. The baseline justifications paraphrased the ad, for example "The content describes a hybrid role", and the reader had to go and find it. The contract says the agent must not present a model's judgment as a fact. A quote can be checked against the saved response by a program, so the change aims at that.
- **Who chose it.** Claude Code proposed and made the change after reading the development answers. Shreyash did not choose it, so it is recorded as Claude's choice.
- **Validator unchanged.** The new instruction only changes what goes inside the justification string.

## Results

| | Development, baseline | Development, revision-1 | Held-out, baseline | Held-out, revision-1 |
|---|---|---|---|---|
| Passed validator | 10/10 | 10/10 | 10/10 | 10/10 |
| **Pass mark: verdict = hand label** | **10/10** | **10/10** | **10/10** | **10/10** |
| Failed-condition set = rule record | 8/10 | 8/10 | 8/10 | 8/10 |
| Answers quoting the posting | 0/10 | 10/10 | 0/10 | 10/10 |
| Quoted spans found word for word in the saved posting | — | 58/58 | — | 54/54 |

- **Model and date:** `claude-opus-5-5`, all on 2026-10-31.
- **Where the record disagreed:** the same postings disagreed with the record under both prompts. Both disagreements on each set were on conditions 3 and 5:
  - **Development:** 8083703 on condition 5 and 6555819 on condition 3. These are the two described in the sampling report.
  - **Held-out:** 8319419 on condition 5 and 8250366 on condition 3. For 8319419 the ad's "5+ years of technical program or project management/process-oriented operations work experience" puts "experience" more than 60 characters after the number. For 8250366 the office tag "Remote (New York)" sits on an ad saying "requiring a hybrid work schedule with 3 days of in-office work per week".
- **Who was right.** All four times, revision-1 quoted the ad words that settle it, and they were in the saved response. In all four, Claude's reading fits the ad and the rule's does not.

## Honest limits

- **The pass mark could not tell the prompts apart.** Every label is Not Relevant, so a judge that always answered "Not Relevant" would also score 10/10 on both sets. The pass mark shows that neither prompt broke the verdict, and no more. It does not show that either prompt can find a relevant job. Oscar listed no posting that passes all six conditions, by the rule or by Shreyash's labels.
- **The revision's measurable gain is checkability only.** The quotes were word for word 112 of 112 times. That shows the quotes are real text, not that they are the right text to quote, and nobody judged that.
- **Ten cases per set is very few.** With 10/10 on a set, the one-sided 95% lower bound on the true pass rate is still only about 74% (0.05^(1/10), exact binomial). Four-out-of-four repeats on five postings are no better.
- **The rule's record is not ground truth.** The 8/10 condition agreement measures agreement with a rule that this experiment found two defects in. It is not a measure of accuracy.
- **What a better experiment needs.** Postings near the line, like a 3-years-required Boston engineering job, which Oscar did not have, and per-condition hand labels.
