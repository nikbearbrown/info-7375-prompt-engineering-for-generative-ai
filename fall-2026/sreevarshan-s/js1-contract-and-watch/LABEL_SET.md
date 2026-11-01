# Label set — 20 postings, split frozen 2026-10-30, before labeling

## Selection method

All 20 postings come from the saved live response `evidence/raw/2026-10-30T23-59-22Z.json` (901 postings), and were selected by title text only, before any posting was labeled or judged. Group A is all 4 titles that contain an approved role phrase from CONTRACT.md and no seniority term. Group B is all 6 titles that contain an approved role phrase and a seniority term. Group C is 10 titles drawn from a pool of 39: titles outside groups A and B that contain "engineer" (any form) or "data" and no seniority term from CONTRACT.md. The pool was sorted by posting id and the 10 were drawn with Python's `random.Random(7375).sample` (seed 7375). Role phrases, seniority terms and title normalization are the ones in `js1/rule_judge.py`, applied to titles only.

Only 4 of 901 titles pass the contract's title check, so the set cannot reach 10 relevant; per LABELING_RULE.md §5 I did not force the split.

## The 20 postings and the frozen split

Sorted by posting id. Entries 1, 3, 5, … are development; entries 2, 4, 6, … are held-out.

| # | posting id | title | split |
|---|---|---|---|
| 1 | 7737233002 | Software Engineer - Backend | development |
| 2 | 7958982002 | Staff Software Engineer - Machine Learning (Search) | held-out |
| 3 | 8029666002 | Software Engineer - Backend | development |
| 4 | 8091041002 | Applied AI Engineer | held-out |
| 5 | 8401114002 | Staff Machine Learning Engineer | development |
| 6 | 8540267002 | Senior Staff Applied AI Engineer - Context Retrieval | held-out |
| 7 | 8546367002 | AI Engineer – Forward Deployed Engineering (AI FDE) | development |
| 8 | 8560779002 | Software Engineer, Web Products | held-out |
| 9 | 8569392002 | Senior AI Engineer - FDE (Forward Deployed Engineer) | development |
| 10 | 8574655002 | AI Engineer - FDE (Forward Deployed Engineer) | held-out |
| 11 | 8648494002 | Forward Deployed Engineer | development |
| 12 | 8656900002 | Senior Applied ML Engineer - ML4Sys | held-out |
| 13 | 8692962002 | Specialist Solutions Architect - Data Engineering & Warehousing (Financial Services) | development |
| 14 | 8760167002 | AI Engineer – Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus) | held-out |
| 15 | 8824168002 | Technical Enablement Specialist  - Field Engineering Onboarding | development |
| 16 | 8829033002 | AI Automation Engineer | held-out |
| 17 | 8847738002 | Software Engineering Intern (2027 Start) - London | development |
| 18 | 8870159002 | Specialist Solutions Architect - Data Engineering | held-out |
| 19 | 8921476002 | Forward Deployed Engineer | development |
| 20 | 8923831002 | Staff Machine Learning Engineer, CustomerLake (ML/LLM) | held-out |
