# Prompt experiment results: held-out split

> **Superseded.** This CLI run hit the usage limit: 38 of its 39 Claude calls failed, so its Claude scores reflect the limit, not the prompts. The held-out results are in `experiments/results_heldout_app.md` (rerun in the Claude app). This file is kept as evidence of the failed run.

- **Run:** 2026-10-31T01-26-20Z (UTC)
- **Model:** claude-sonnet-4-6, one call per posting per prompt (plus at most one retry on an invalid reply)
- **Postings:** real postings from `evidence/raw/2026-10-30T23-59-22Z.json`, split frozen in `LABEL_SET.md`
- **Hand labels:** `labels/HAND_LABELS.md`
- **Evidence:** `evidence/experiment/heldout/2026-10-31T01-26-20Z/`
- **Scoring:** a prompt passes on a posting when its result is valid and its verdict equals my hand label; an invalid result is a fail.

| posting_id | title | my hand label | rule verdict | baseline verdict | revised verdict | baseline | revised |
|---|---|---|---|---|---|---|---|
| 7958982002 | Staff Software Engineer - Machine Learning (Search) | not relevant | not relevant | not relevant | invalid | pass | fail |
| 8091041002 | Applied AI Engineer | not relevant | not relevant | invalid | invalid | fail | fail |
| 8540267002 | Senior Staff Applied AI Engineer - Context Retrieval | not relevant | not relevant | invalid | invalid | fail | fail |
| 8560779002 | Software Engineer, Web Products | not relevant | not relevant | invalid | invalid | fail | fail |
| 8574655002 | AI Engineer - FDE (Forward Deployed Engineer) | not relevant | not relevant | invalid | invalid | fail | fail |
| 8656900002 | Senior Applied ML Engineer - ML4Sys | not relevant | not relevant | invalid | invalid | fail | fail |
| 8760167002 | AI Engineer – Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus) | not relevant | relevant | invalid | invalid | fail | fail |
| 8829033002 | AI Automation Engineer | not relevant | not relevant | invalid | invalid | fail | fail |
| 8870159002 | Specialist Solutions Architect - Data Engineering | not relevant | not relevant | invalid | invalid | fail | fail |
| 8923831002 | Staff Machine Learning Engineer, CustomerLake (ML/LLM) | not relevant | not relevant | invalid | invalid | fail | fail |

- **Baseline:** 1/10
- **Revised:** 0/10
- **Rule:** 9/10
- **Invalid results:** 19 (baseline 9, revised 10)
