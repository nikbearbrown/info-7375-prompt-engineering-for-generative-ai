## Sampling (v1_baseline, 4 fresh calls per posting)

| # | title | hand label | Claude verdicts (4 calls) | agree with hand |
|---|---|---|---|---|
| 1 | Manager, Field Engineering France  - Specialist Solutions Architects | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 |
| 2 | Sr. Software Engineer - Storage I/O | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 |
| 3 | Solutions Engineer | relevant | relevant, relevant, not_relevant, REJECTED | 2/4 |
| 4 | Software Engineer - New Grad, Distributed Data Systems (2027 Start) | relevant | not_relevant, not_relevant, not_relevant, not_relevant | 0/4 |
| 5 | Data+AI Workforce Transformation Practitioner — Customer Delivery | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 |

## Prompt experiment (pass = Claude verdict equals hand label; a validator rejection is a fail)

| judge | dev (10) | held-out (10) | rejected by validator |
|---|---|---|---|
| Claude, v1 prompt | 9/10 | 10/10 | 0 |
| Claude, v2 prompt | 8/10 | 10/10 | 1 |
| written rule (record) | 8/10 | 10/10 | n/a |
| always 'not_relevant' | 8/10 | 10/10 | n/a |

Hand labels: dev 2 relevant / 8 not; held-out 0 relevant / 10 not.
