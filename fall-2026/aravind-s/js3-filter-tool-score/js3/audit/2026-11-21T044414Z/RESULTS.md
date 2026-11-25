# Audit results, filter run 2026-11-21T044414Z

Computed by `tools/score_audit.py` from Aravind's verdicts in VERDICTS.md (committed before the answers were opened) and `sealed/answers.json` (SHA-256 `b812a56034ab763ce429eeef5ff2de40e9d688dc454bcc4a2709709b6b107e86`, the hash SAMPLE.md published before any verdict). Claude Code wrote the script and this file; the verdicts are his.

## By group

| Group | Cards | Agree | Miss | Wrong keep | ? |
|---|---:|---:|---:|---:|---:|
| random reject | 30 | 29 | 1 | 0 | 0 |
| kept sample | 10 | 9 | 0 | 0 | 1 |
| close call: kept near the cutoff | 8 | 7 | 0 | 0 | 1 |
| close call: failed one rule | 7 | 6 | 0 | 0 | 1 |
| **all** | **55** | **51** | **1** | **0** | **3** |

## The miss count (random rejects only)

1 misses in 30 judged random rejects (0 marked ?). As a sample result: 1/30. The exact one-sided 95% upper bound (Clopper-Pearson) is 14.9%, which for the 1409 postings this run rejected means up to about 209 misses. This bounds what the sample supports; it is not a measured rate for every reject.

## With the checks asked after the reveal (AFTER-REVEAL.md)

These were asked after `sealed/answers.json` was opened, so they are reported beside the frozen result, never in place of it. VERDICTS.md is unchanged.

| Card | Frozen verdict | After the reveal | When | Why it was asked | His words |
|---|---|---|---|---|---|
| 17 | Keep | Reject | 2026-11-22, about 1:58 AM ET | The card showed no status line, but the posting's requirements list says "U.S. Person Required", which R5 read: the filter's sentence splitter cut that line at "U.S.", so the card never picked it up. Shown the line, he was asked whether he would still keep the posting. | "No, reject it" |

With these checks: 0 misses in 30 judged random rejects (0 marked ?); the exact one-sided 95% upper bound is 9.5%, up to about 134 of the 1409 rejected postings.

## Every disagreement and every ?

| Card | Title | Group | Filter | His verdict | His note |
|---|---|---|---|---|---|
| 17 | Forward Deployed Software Engineer, New Grad - Warp Speed | random reject | rejected by R4 (also fails R5) | Keep (miss) | Forward Deployed Software Engineer, New Grad, in New York; matches Jane's experience level and preferred location. |
| 29 | Software Engineer - Core Interfaces | close call: failed one rule | rejected by R5 (its only failed rule) | ? | Software engineering in New York, but the security clearance requirement makes Jane's eligibility unclear. |
| 31 | Software Engineer, CI/CD & ML Infrastructure | kept sample | kept, score 55 | ? | Relevant CI/CD and ML infrastructure engineering, but the export control requirement makes Jane's eligibility unclear. |
| 35 | Host Systems Software Engineer | close call: kept near the cutoff | kept, score 55 | ? | Host systems software engineering looks relevant, but the export control requirement makes Jane's eligibility unclear. |

## Misses by the rule that decided them

| Rule | Misses | Cards | Of these, the only rule the posting failed |
|---|---:|---|---:|
| R4 | 1 | 17 | 0 |
