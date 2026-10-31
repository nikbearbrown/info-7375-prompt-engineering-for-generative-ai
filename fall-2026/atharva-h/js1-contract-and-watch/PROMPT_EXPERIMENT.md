# Prompt experiment — citation path syntax

The v1 prompt called citation locations "dot paths" without specifying how to
write list positions. V2 added one sentence requiring square brackets such as
`offices[0].location`; the validator stayed the same. Saved answers and scores
are in `experiments/prompt/`. The four score files were recomputed on 2026-10-31
after I hand-labeled the 20 postings in `experiments/label_pool/LABELS.md`.

| Prompt | Set | Invalid outputs | Passes / committed | Coverage |
|---|---|---:|---:|---:|
| v1 baseline | development | 5/10 | 5/5 | 5/10 |
| v2 path syntax | development | 0/10 | 9/9 | 9/10 |
| v1 baseline | held out | 7/10 | 3/3 | 3/10 |
| v2 path syntax | held out | 0/10 | 10/10 | 10/10 |

The one uncommitted v2 development answer was `needs_human` for Point72
8877421002, matching that posting's hand label but excluded from pass
rate by the contract. V2 eliminated invalid outputs on these 20 saved answers.
The change demonstrates better compliance with citation syntax, not a measured
improvement in semantic judgment.

Nineteen of 20 are `not_relevant`, and every held-out label is `not_relevant`.
An always-`not_relevant` answer would score 19/20 overall and 10/10 held out,
so the held-out pass rate cannot show whether the prompt recognizes a relevant
posting. The rule agrees with all 20 labels because the same written rule was
used to assign them; that agreement is a consistency check, not independent
validation.
