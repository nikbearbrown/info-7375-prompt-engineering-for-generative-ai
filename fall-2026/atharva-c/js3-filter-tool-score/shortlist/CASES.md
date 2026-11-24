# Shortlist cases

DRAFT (Claude, Nov 24, 2026), to be checked and rewritten by me. Every quote below is copied from `shortlist/shortlist.json`, which `tests/test_shortlist.py` checks are substrings of the postings in `evidence/run-20261123-185425Z`.

Shortlist from `evidence/filter-v1.2/decisions.jsonl` (15 kept, no duplicate board and title): **10 ranked, 1 "I cannot tell", 4 contradicted.**

## Relevance is not entailment: `robinhood:7263592`, Software Engineer, Backend (Menlo Park, CA; New York, NY)

- The filter gave it **0.90**, the highest score in the run: role phrase, "2+ years" (≤ 2, so +0.30), a skill.
- The years span is **relevant** to Sam's level, and it **supports** the narrow claim "asks for at most 2 years": “2+ years of experience in software development.”
- It does **not entail** "written for an entry-level engineer." Nothing in the posting says new grad, early career or entry level, and the next requirement says the opposite: “Strong track record of successfully delivering large-scope technical projects in cross-functional team environments.” → **contradicted**.
- My hand label (held-out) and audit judgment: reject, "mid-level backend, asks track record delivering large-scope projects". The filter scored a relevant span as if it settled the question; the claim check does not.

## Abstention rule and its counterexample

**Rule (FILTER.md section 2):** if 2 or more claims are insufficient, the posting is not ranked; it goes in "I cannot tell".

**Counterexample: `affirm:7749755003`**, Software Engineer II, Fullstack (Capital Orchestration), Remote US.

- Abstained: `entry` insufficient (no entry wording) and `skill` insufficient. The only sentence naming Sam's skills is a nice-to-have: “Knowledge of Python, JavaScript/React, Airflow, Spark, Horizon Portal, and SQL is a plus.”
- But it asks for the same thing as its ranked sibling `affirm:7819445003` (ranked #1): “You have a total of 1.5+ years of experience as a software engineer.” The two differ only in whether a skill sentence is phrased as a requirement or as a plus.
- My audit judgment: **keep** ("SWE II asking 1.5+ yrs, Python/React/SQL match, US remote").
- So the rule counts missing claims without weighing them: a missing `skill` claim (a small R4 bonus in the filter) costs as much as a missing `us` or `role` claim. Here it hid a posting I would apply to.

## What does not count as a measurement

- The 4 contradicted entries are exactly the 4 kept postings I judged reject after v1.2 (3 Robinhood backend, 1 Wealthfront iOS). That match is **not** evidence that the claim check works: the `track record` / `proven ability` cue was chosen after reading those postings in the audit, and all 4 are held-out rows. So is the abstention counterexample (`affirm:7749755003`). These cases come from postings I had already seen; none of them measures anything.
- In the audit I wrote "early career SWE I" for `affirm:8017340003`, `affirm:8181183003` and `affirm:8201469003`. Their text never says "early career". The span that supports `entry` is “You have previous work or internship experience …”.
