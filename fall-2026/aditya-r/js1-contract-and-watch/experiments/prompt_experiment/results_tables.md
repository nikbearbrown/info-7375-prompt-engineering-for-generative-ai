## dev (n = 10)

- Hand labels: {'not_relevant': 7, 'relevant': 3}
- 'Always not_relevant' baseline: 7/10
- Deterministic RECORD vs hand label: 10/10

| prompt | format/contract pass | agreement (invalid = wrong) | agreement among valid | confusion (label → pred) |
|---|---|---|---|---|
| v1 | 10/10 | 10/10 | 10/10 | not_relevant→N: 7; relevant→R: 3 |
| v2 | 10/10 | 10/10 | 10/10 | not_relevant→N: 7; relevant→R: 3 |

| posting id | title | hand label | RECORD | v1 | v2 |
|---|---|---|---|---|---|
| 7647369002 | Senior Software Engineer (Data Platform) | N | N | N | N |
| 8755666002 | Manager, Field Engineering - Polish speaker | N | N | N | N |
| 7630152002 | Sr Staff Software Engineer (Backend) | N | N | N | N |
| 8493168002 | Sr. IT Site Reliability Software Engineer | N | N | N | N |
| 7006090002 | Engineering Manager - Core Experiences  | N | N | N | N |
| 8495065002 | APJ Manufacturing & Automotive Industry GTM Leader | N | N | N | N |
| 8829029002 | Software Engineer, Infrastructure | R | R | R | R |
| 8829039002 | Software Engineer, Infrastructure | R | R | R | R |
| 6865698002 | Software Engineer - New Grad (2027 Start) | R | R | R | R |
| 8716314002 | Sr. Manager, Field Engineering - Sports | N | N | N | N |

## heldout (n = 10)

- Hand labels: {'not_relevant': 8, 'relevant': 2}
- 'Always not_relevant' baseline: 8/10
- Deterministic RECORD vs hand label: 10/10

| prompt | format/contract pass | agreement (invalid = wrong) | agreement among valid | confusion (label → pred) |
|---|---|---|---|---|
| v1 | 10/10 | 10/10 | 10/10 | not_relevant→N: 8; relevant→R: 2 |
| v2 | 10/10 | 10/10 | 10/10 | not_relevant→N: 8; relevant→R: 2 |

| posting id | title | hand label | RECORD | v1 | v2 |
|---|---|---|---|---|---|
| 8921585002 | Solutions Architect Israel | N | N | N | N |
| 8575251002 | Sr. Staff Software Engineer — Observability, Insights & Governance | N | N | N | N |
| 7925560002 | Sr. Software Engineer - Observability | N | N | N | N |
| 8012650002 | Software Engineer - Backend | R | R | R | R |
| 8029666002 | Software Engineer - Backend | R | R | R | R |
| 6704975002 | Staff Fullstack Engineer | N | N | N | N |
| 8589172002 | Sr Technical Solutions Engineering | N | N | N | N |
| 8679982002 | Sr Software Engineer - Agentic Applications (Full Stack) | N | N | N | N |
| 8760165002 | Staff Software Engineer, Ads Measurement & Orchestration | N | N | N | N |
| 8656202002 | Forward Deployed Engineering - Senior Architect | N | N | N | N |
