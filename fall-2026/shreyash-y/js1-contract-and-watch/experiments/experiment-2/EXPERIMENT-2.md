# Prompt experiment 2: a set with positives (Chapter 2, added after review)

*Written by Claude Code on 2026-10-31 from the saved calls and the two score files, `score-development-2026-10-31.txt` and `score-held-out-2026-10-31.txt`, in this folder. The labels and their reasons are Shreyash's.*

## Why there is a second experiment

In [experiment 1](../PROMPT-EXPERIMENT.md), on Oscar, all 20 hand labels were Not Relevant. A judge that always answers "Not Relevant" would have scored 10/10, so the pass mark could not show that either prompt finds a match. There were also no per-condition labels made before the calls.

The TA-style review on 2026-10-31 named this as the main weakness, and Shreyash agreed. Experiment 1 is left exactly as it ran. This is a second, separate experiment on fresh postings, set up so that it can fail in both directions.

## Order of work, with commits

| Step | Commit / time (EDT) | Fixed before the next step |
|---|---|---|
| Both prompts written and frozen | `5c34654` (experiment 1), 15:57 | [baseline-v1](../../prompts/baseline-v1.md) and [revision-1](../../prompts/revision-1-quote-evidence.md), unchanged since. Neither prompt had seen Klaviyo. |
| Scouting: 20 Greenhouse boards counted for rule-positives (counts only, nothing saved; see SOURCES.md) | 16:52 | Klaviyo picked: 156 postings, 4 rule-Relevant |
| Klaviyo fetched through `jsagent/fetch.py`, raw saved; seeded pick of 20; blind label sheet | `c3eaff1`, 16:56 | [selected_postings.json](selected_postings.json), [select_postings.py](select_postings.py), [POSTINGS-TO-LABEL.md](POSTINGS-TO-LABEL.md) |
| **Shreyash's labels:** verdict, failed conditions, reason | `8e2c92b`, 17:05:38 | [hand-labels.csv](hand-labels.csv) |
| Both prompts on development (20 calls, last at 17:06:13) | `fd985ba`, 17:07:05 | — |
| Both prompts on held-out (20 calls, first at 17:07:05) | after `fd985ba` | — |

How the 20 were picked:
- **Pool:** the 22 postings whose title passes condition 1.
- **Split:** by the rule v1 record into Relevant and other, so that both halves contain positives. The output file and the label sheet do not say which is which.
- **Labeling instructions:** the sheet asked Shreyash to label by the contract as decided on 2026-10-31: mandatory years only, and remote must be workable from Massachusetts. The prompts carry the contract's original wording.

## Results

Model `claude-opus-5-5`, 40 calls, $1.62, all on 2026-10-31. Every answer passed the validator.

| | Dev, baseline | Dev, revision-1 | Held-out, baseline | Held-out, revision-1 | Rule v1 record, dev / held-out |
|---|---|---|---|---|---|
| **Verdict = hand label** | **10/10** | **10/10** | **10/10** | **10/10** | 10/10 / 10/10 |
| Relevant found (TP / FP / FN) | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 2/0/0 / 2/0/0 |
| Failed-condition set = hand label | 9/10 | 9/10 | 8/10 | 8/10 | 9/10 / 9/10 |
| Quoted spans found word for word | — | 38/39 | — | 42/42 | — |

- **The one quote not found** (dev, 7986459003) is not a made-up citation. Claude quoted a rule word, in the passage *("Management" is not "Manager")*.
- **Every disagreement is about conditions, not verdicts.**

| Posting | Hand label | Judge | What the ad says | Reading |
|---|---|---|---|---|
| 7822352003, Full Stack SWE – People Systems (dev) | fails 2, 3, 5 | Claude (both prompts): fails 2, 5 | location "San Francisco, CA", offices ["Boston"] | **Ambiguous.** Claude passed condition 3 on the Boston office and said so. Shreyash and the rule went by the location field. The contract's "located in Boston, MA" does not say which field wins. |
| 8044834003, Senior Lead AI Engineer (held-out) | fails 2, 3, 5, 6 | Claude (both prompts): fails 2, 5, 6 | location "San Francisco, CA", offices ["Boston", "San Francisco"] | The same ambiguity. |
| 7809608003, Senior Lead SWE – Data Platform (held-out) | fails 5, 6 | Claude (both prompts) **and** rule: fail 4, 5, 6 | Of Alex's skills, only Python appears ("Python-based data platform tooling") | **Probably a labeling slip.** Three judges agree that condition 4 fails, and the hand reason doesn't mention skills. The label stays as committed; Shreyash has not re-checked it. |
| 7783904003, Senior SWE – Platform Engineering (dev) | fails 4, 5 | rule: fails 4 | "5+ years of responsibility operating and scaling…" | **The rule's known condition 5 defect again:** the word "experience" isn't there, so it found no requirement. Claude and Shreyash both caught it. |

## What this shows and does not show

- **What it shows.** Both prompts found all 4 positives Shreyash marked, in both halves, and called none of the 16 negatives relevant. Unlike experiment 1, a judge that always said "Not Relevant" would score 16/20 here and miss all 4 positives. So the 10/10s now mean something.
- **The one change still made no measurable difference to accuracy.** Revision-1 gave the same verdicts and condition sets as the baseline on all 20 postings. Its gain is only that 80 of its 81 quotes can be checked word for word, and the remaining one is a rule word.
- **Claude and the rule are not ground truth, and neither is the hand label.** Of the four condition disagreements:
  - two come from a genuine ambiguity in the contract (location vs offices);
  - one is probably a hand-label slip;
  - one is the rule's known defect.
- **Small numbers.** Four positives and 16 negatives are very few. 2/2 true positives per half cannot rule out a real miss rate of 50% or more, and 10/10 per half still has a one-sided 95% lower bound of about 74% on accuracy.
- **Selection was by the rule.** The pool was limited to postings that pass condition 1, and the halves were balanced using the rule's record. So these 20 are easier on titles than a random Klaviyo posting. Nothing here measures how either judge handles title mistakes.
- **Different labeling instructions from the prompts.** Shreyash labeled with the 2026-10-31 decisions on experience and remote; the prompts used the original contract wording. On these 20 postings that difference did not change any verdict.
- **One model, one day,** and the prompts were not tuned on Klaviyo.
