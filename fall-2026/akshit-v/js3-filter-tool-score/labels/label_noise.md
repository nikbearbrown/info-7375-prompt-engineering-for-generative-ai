# Known label noise under the 2026-11-25 definition

Labels the accepted definition contradicts, **by Claude Code's reading** of each posting's title, my note and the text. Not checked by me. The labels are unchanged; these are reported, not corrected.

## Clause "its work isn't technical" (6)

| # | title | my label | my note | why it conflicts |
|---|---|---|---|---|
| 35 | Enterprise Account Executive | relevant | partial match | Account Executive: the work is selling |
| 44 | Account Executive, SMB (Berlin, Germany) | relevant | partial match | Account Executive: the work is selling |
| 71 | Strategic Account Executive, Majors Acquisition | relevant | partial match | Account Executive: the work is selling |
| 38 | Sr Product Marketing Manager, Media, Entertainment and Advertising | relevant | partial match | Product Marketing Manager: the work is marketing |
| 54 | Partner Development Manager | relevant | partial match | Partner Development Manager: the work is partner business development |
| 60 | Product Manager, AI Growth | relevant | partial match | Product Manager: the work is product management |

## Clause "requires clearly more experience than 5 years", read as 8+ years (9)

| # | title | my label | my note | the posting says |
|---|---|---|---|---|
| 9 | Data Engineering Solutions Specialist | relevant | skillset matches | "10+ years of professional experience and at least 6 of years sales experience with consistently exceeding sales objectives selling technical" |
| 12 | Staff Software Engineer - Metadata | relevant | some skills matches | "10+ years building large-scale distributed systems or database internals" |
| 24 | Senior Solution Engineer | relevant | partial match | "8+ years of experience in pre-sales solution engineering, technical consulting, or data engineering in enterprise B2B technology, with signi" |
| 30 | Manager, Software Engineering - External Platform | relevant | skillset matches | "• 8+ years of total engineering experience, ideally reaching a staff engineering level as an individual contributor" |
| 32 | Principal Engineer | relevant | partial match | "15+ years of software engineering experience, with a demonstrated track record of architecting and shipping production-grade developer platf" |
| 48 | Senior Solution Engineer (Expansion) | relevant | partial match | "Extensive 10 years working experience in customer facing solution engineering role" |
| 56 | Activation Solution Engineer | relevant | skillset matches | "Extensive 8 years of working experience in data technologies" |
| 76 | Activation Solution Engineer | relevant | skillset matches | "Extensive 8 years of working experience in data technologies" |
| 78 | Engineering Manager | relevant | skillset matches | "10+ years of experience building and operating large-scale systems (distributed systems, databases, or cloud services)" |

## Same clause, opposite direction

#40, #50, #65, #66 were labeled `not_relevant` for experience ("requires lots of experience"). Their own text was not compared with the 9 above, so whether one experience line separates them is **not established**.

**Total contradicted: 15 of 80 (19%).**

## Addendum, 2026-11-25, found **after** the held-out `prompt_v3_definition` run (so it is not independent of that result)

Under `judge_v3_definition.md`, Claude flipped three of my `not_relevant` labels' postings to `relevant`. Reading them again: each is a technical solution- or account-engineering role, and the definition I accepted says solution or sales engineering **does not count against** a posting. My note on all three was "not data engineer role". So these three labels also contradict the definition, and the list above (made before that run) missed them.

| # | title | my label | my note |
|---|---|---|---|
| 10 | Senior Solution Engineer - Expansion | not_relevant | not data engineer role |
| 18 | Commercial Solutions Engineer - Acquisition | not_relevant | not data engineer role |
| 59 | Account Engineer | not_relevant | no data engineer role |

**Revised total: at least 18 of 80 (23%).** This list was made by reading, not by a rule, so there may be more.
