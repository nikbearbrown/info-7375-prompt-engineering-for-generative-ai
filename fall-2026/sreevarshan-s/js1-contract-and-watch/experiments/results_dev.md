# Prompt experiment results: development split

- **Run:** 2026-10-31T00-59-14Z (UTC)
- **Model:** claude-sonnet-4-6, one call per posting per prompt (plus at most one retry on an invalid reply)
- **Postings:** real postings from `evidence/raw/2026-10-30T23-59-22Z.json`, split frozen in `LABEL_SET.md`
- **Hand labels:** `labels/HAND_LABELS.md`
- **Evidence:** `evidence/experiment/dev/2026-10-31T00-59-14Z/`
- **Scoring:** a prompt passes on a posting when its result is valid and its verdict equals my hand label; an invalid result is a fail.

| posting_id | title | my hand label | rule verdict | baseline verdict | revised verdict | baseline | revised |
|---|---|---|---|---|---|---|---|
| 7737233002 | Software Engineer - Backend | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8029666002 | Software Engineer - Backend | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8401114002 | Staff Machine Learning Engineer | not relevant | not relevant | not relevant | invalid | pass | fail |
| 8546367002 | AI Engineer – Forward Deployed Engineering (AI FDE) | not relevant | relevant | not relevant | not relevant | pass | pass |
| 8569392002 | Senior AI Engineer - FDE (Forward Deployed Engineer) | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8648494002 | Forward Deployed Engineer | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8692962002 | Specialist Solutions Architect - Data Engineering & Warehousing (Financial Services) | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8824168002 | Technical Enablement Specialist  - Field Engineering Onboarding | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8847738002 | Software Engineering Intern (2027 Start) - London | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8921476002 | Forward Deployed Engineer | not relevant | not relevant | not relevant | not relevant | pass | pass |

- **Baseline:** 10/10
- **Revised:** 9/10
- **Rule:** 9/10
- **Invalid results:** 1 (baseline 0, revised 1)
