# Shortlist cases

Every quote below is copied verbatim from `shortlist/shortlist.json`, which `tests/test_shortlist.py` checks as an exact substring of the postings in `evidence/run-20261123-185425Z`.

From `evidence/filter-v1.2/decisions.jsonl`, 15 postings passed the filter (with no duplicate `(board, title)` pairs among them): 10 were ranked, 1 went to `"I cannot tell"`, and 4 were flagged as contradicted.

## Relevance is not entailment: `robinhood:7263592`, Software Engineer, Backend (Menlo Park, CA; New York, NY)

- `FILTER.md` v1.2 gave this posting a score of `0.90`—the highest in the run—from a matching role phrase (`+0.50`), a `2+ years` phrase (`+0.30`), and a skill hit (`+0.10`).
- That experience line is relevant to Sam's range and supports the narrow claim `"asks for at most 2 years"`: “2+ years of experience in software development.”
- However, relevance to a filter rule does not entail `"written for an entry-level engineer."` Nothing in the posting mentions new grad, early career, or entry level, and the following requirement directly contradicts an entry-level claim: “Strong track record of successfully delivering large-scope technical projects in cross-functional team environments.” → contradicted.
- In both my held-out label and my v1.0 audit judgment, I marked this posting `reject` (audit reason: `"mid-level backend (2+ yrs), asks track record delivering large-scope projects"`). The numeric filter treated a matching years phrase as sufficient; the claim-level check separates what the text actually entails from what it contradicts.

## Abstention rule and its counterexample: `affirm:7749755003`, Software Engineer II, Fullstack (Capital Orchestration) (Remote US)

- **The rule (`FILTER.md` §2):** If 2 or more justification claims are `insufficient`, the shortlist does not rank the posting and places it in `"I cannot tell"`.
- **Why this posting abstained:** Two claims came back `insufficient`—`entry` (no explicit entry-level wording) and `skill` (under `FILTER.md` §2 rule 1, a nice-to-have list cannot support a core skill claim, and the only sentence mentioning Sam's stack is: “Knowledge of Python, JavaScript/React, Airflow, Spark, Horizon Portal, and SQL is a plus.”).
- **Why this is a counterexample:** Its experience requirement is identical to its ranked sibling `affirm:7819445003` (ranked `#1`): “You have a total of 1.5+ years of experience as a software engineer.” The only difference is whether the stack is written as a required bullet or a `"is a plus"` bullet.
- **My judgment:** I marked `affirm:7749755003` `keep` (`"SWE II asking 1.5+ yrs, Python/React/SQL match, US remote"`). Counting `insufficient` claims without weighting them treats a missing minor skill bonus (`R4`) the same as a missing US location or SWE role claim, hiding a genuine fit in the unranked bucket.

## What does not count as a measurement

- The 4 contradicted entries on the shortlist are the exact 4 postings kept by `v1.2` that I had already judged `reject` during the v1.0 audit (3 Robinhood backend roles and 1 Wealthfront iOS role). That agreement is not independent evidence that the contradiction check generalizes: the `"track record"` / `"proven ability"` cue was added after reading those postings in the audit, and all 4—along with the abstention counterexample `affirm:7749755003`—belong to the `heldout` split. They illustrate how the rules behave on known edge cases rather than serving as an out-of-sample measurement.
- In my own audit notes, I wrote `"early career SWE I"` for `affirm:8017340003`, `affirm:8181183003`, and `affirm:8201469003`. None of those postings actually contain the phrase `"early career"`; the verbatim span supporting entry-level eligibility is “You have previous work or internship experience …”.
