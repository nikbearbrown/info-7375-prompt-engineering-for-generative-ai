# The held-out comparison, run once

Run at 2026-11-25T00:43:26Z by `python3 -m jobwatch.js3 held-out runs/2026-11-24-js3-corpus --sample labels/v0.1-sample.json --labels labels/hand-labels.json --variant variants/v0.2-experience-minimum.json --out reports/held-out`. Scored the way FILTER.md says ("After the reject audit, before any held-out label was scored"): Can’t tell rows left out; pass when at least 90% of the Yes and No rows match, no more than one Yes is rejected, and no unmet requirement is cleared.

| Check | v0.1 | v0.2 |
| --- | --- | --- |
| Rows labelled / Can’t tell / scored | 30 / 4 / 26 | 30 / 4 / 26 |
| Matches among the scored rows | 18 of 26 | 24 of 26 |
| Yes rejected (false exclusions) | none | none |
| No kept or held for review (false inclusions) | P17, P18, P27, P34, P41, P53, P55, P69 | P27, P53 |
| Of those, an unmet requirement cleared | P17, P18, P34, P41, P53, P55, P69 | P53 |
| at least 90% of the Yes and No rows match | FAIL | pass |
| no more than one Yes rejected | pass | pass |
| no unmet requirement cleared | FAIL | FAIL |
| **Bar met (these three checks)** | **no** | **no** |

## Every held-out row

| ID | Group | Title | Label | The student's reason | v0.1 fate (outcome) | v0.2 fate (outcome) |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | held-out rejected | Strategic Core Account Executive - CPG | no | The role owns enterprise sales and quota, outside the engineering search. | rejected (agree) | rejected (agree, 7-year minimum) |
| P02 | held-out kept or review | Research Engineer, Knowledge Team | cannot tell | The ML research fits. The posting asks for a “very experienced” Python programmer and leaves the hiring level open. | kept (cannot tell) | kept (cannot tell) |
| P06 | held-out rejected | Specialist Solutions Architect - Data Engineering & Warehousing (Financial Services)  | no | The work centers on solutions architecture and pre-sales, with 6+ years listed. | rejected (agree) | rejected (agree, 6-year minimum) |
| P07 | held-out rejected | Senior Software Engineer - Fullstack | no | The senior full-stack role lists 5+ years each in front-end and server-side web development. | rejected (agree) | rejected (agree, 5-year minimum) |
| P08 | held-out rejected | Solutions Architect (Genie) | no | The customer-facing solutions architect role lists work locations in India. | rejected (agree) | rejected (agree, 6-year minimum) |
| P09 | held-out rejected | Web Strategy Lead | no | This is a web strategy lead role with 12+ years listed. | rejected (agree) | rejected (agree, 12-year minimum) |
| P10 | held-out kept or review | Software Engineer, Sandboxing | cannot tell | The team builds sandbox infrastructure for an AI system. The posting seeks low-level systems experience and leaves the hiring level open. | kept (cannot tell) | kept (cannot tell) |
| P11 | held-out kept or review | Research Engineer, Cybersecurity RL | yes | The U.S. role combines ML research and software engineering for defensive cybersecurity. It asks for demonstrated experience in those areas. | kept (agree) | kept (agree) |
| P17 | held-out kept or review | Data Engineer, Product | no | The data engineering work fits the topic, and the posting describes a candidate with 7+ years of relevant experience. | kept (false inclusion) | rejected (agree, 7-year minimum) |
| P18 | held-out kept or review | Research Engineer, Discovery | no | The posting asks for 6+ years of highly relevant infrastructure engineering experience. | kept (false inclusion) | rejected (agree, 6-year minimum) |
| P21 | held-out kept or review | Research Engineer, Life Sciences | yes | The U.S. role covers LLM training, evaluation, and data pipelines. The 8+ years appear under preferred qualifications. | kept (agree) | kept (agree) |
| P24 | held-out rejected | IP Counsel, Trademarks & Domains | no | This is a trademark and domain counsel role. | rejected (agree) | rejected (agree) |
| P27 | held-out kept or review | Red Team Engineer, Safeguards | no | The core work is application security and red teaming for deployed AI products. | kept (false inclusion) | kept (false inclusion) |
| P28 | held-out rejected | Startup Account Executive | no | This is a direct sales opening in London. | rejected (agree) | rejected (agree) |
| P31 | held-out rejected | Research Scientist, Life Sciences | no | The opening centers on life sciences research and drug discovery in a research scientist role. | rejected (agree) | rejected (agree) |
| P33 | held-out kept or review | Research Engineer, Machine Learning (Reinforcement Learning)  | cannot tell | The RL engineering work fits. The posting asks for industry ML research experience and leaves the hiring level open. | kept (cannot tell) | kept (cannot tell) |
| P34 | held-out kept or review | Forward Deployed Engineer (FDE) - Public Sector | no | The posting sets a 5+ year minimum in data, analytics, or software engineering. | kept (false inclusion) | rejected (agree, 5-year minimum) |
| P40 | held-out rejected | Sr. Forward Deployed Engineer | no | The Senior FDE role lists 6+ years in data or software engineering. | rejected (agree) | rejected (agree, 6-year minimum) |
| P41 | held-out kept or review | Software Engineer, Labs | no | The Labs role lists 8+ years building full-stack applications. | kept (false inclusion) | rejected (agree, 8-year minimum) |
| P51 | held-out rejected | Strategic Account Executive, Insurance | no | This insurance sales opening sets a 5+ year minimum in enterprise sales. | rejected (agree) | rejected (agree, 5-year minimum) |
| P53 | held-out kept or review | Pre-training Data Infrastructure Engineer | no | The description specifies Staff level and asks for 5+ years outside internships. | kept (false inclusion) | kept (false inclusion) |
| P55 | held-out kept or review | Applied AI Engineer, Startups (Life Sciences) | no | The posting seeks 4+ years of technical experience and deep life sciences or biotech experience. | kept (false inclusion) | rejected (agree, 4-year minimum) |
| P58 | held-out rejected | Sr. Solutions Architect | no | The Senior Solutions Architect role lists Singapore as its work location. | rejected (agree) | rejected (agree, 8-year minimum) |
| P62 | held-out kept or review | Data Engineer, Billing & Payments | yes | The U.S. role builds billing data pipelines with SQL and Python. The posting lists 5+ years as preferred. | kept (agree) | kept (agree) |
| P68 | held-out rejected | Applied AI Architect, Beneficial Deployments (Non-Profits) | no | The nonprofit AI architect role centers on technical advisory work and asks for 3+ years in customer-facing roles. | rejected (agree) | rejected (agree, 3-year minimum) |
| P69 | held-out kept or review | Applied AI Engineer, Enterprise  | no | The enterprise AI role centers on customer deployments and lists 4+ years in technical roles. | kept (false inclusion) | rejected (agree, 4-year minimum) |
| P73 | held-out rejected | Staff+ Software Engineer, Backend | no | The Staff+ role lists 8+ years in backend or product engineering. | rejected (agree) | rejected (agree, 8-year minimum) |
| P74 | held-out rejected | Engineering Manager, Enterprise | no | The role manages an engineering team and sets a 4+ year minimum in engineering management. | rejected (agree) | rejected (agree, 4-year minimum) |
| P76 | held-out kept or review | Recruiting Analytics Data Engineer  | cannot tell | The role builds recruiting data infrastructure. The posting prefers 5+ years and expects BigQuery expertise, leaving early-career fit unclear. | kept (cannot tell) | kept (cannot tell) |
| P80 | held-out rejected | Manager, Field Engineering France  - Specialist Solutions Architects | no | This Paris-based field engineering management role leads pre-sales specialists. | rejected (agree) | rejected (agree) |
