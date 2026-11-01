# Prompt experiment results: held-out split, run by hand in the Claude app

- **Run:** 2026-10-31, run by me in the Claude app (incognito, Sonnet 4.6, web search off), one reply per prompt per posting, no retry.
- **Why the app:** the CLI held-out run hit the usage limit (commit `4a46925`).
- **Prompts:** `experiments/heldout_app/prompts/`, built with `js1.claude_judge.build_prompt`, byte for byte what the judge would send.
- **Replies:** `experiments/heldout_app/replies/`, one reply per posting per prompt, saved by hand. There is no automatic retry in the app.
- **Validator:** `js1.claude_judge.validate`, unchanged from the dev run.
- **Hand labels:** `labels/HAND_LABELS.md`
- **Scoring:** a prompt passes on a posting when its reply is valid and its verdict equals my hand label; an invalid or missing reply is a fail.

| posting_id | title | my hand label | rule verdict | baseline verdict | revised verdict | baseline | revised |
|---|---|---|---|---|---|---|---|
| 7958982002 | Staff Software Engineer - Machine Learning (Search) | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8091041002 | Applied AI Engineer | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8540267002 | Senior Staff Applied AI Engineer - Context Retrieval | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8560779002 | Software Engineer, Web Products | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8574655002 | AI Engineer - FDE (Forward Deployed Engineer) | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8656900002 | Senior Applied ML Engineer - ML4Sys | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8760167002 | AI Engineer – Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus) | not relevant | relevant | not relevant | not relevant | pass | pass |
| 8829033002 | AI Automation Engineer | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8870159002 | Specialist Solutions Architect - Data Engineering | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8923831002 | Staff Machine Learning Engineer, CustomerLake (ML/LLM) | not relevant | not relevant | not relevant | not relevant | pass | pass |

- **Baseline:** 10/10
- **Revised:** 10/10
- **Rule:** 9/10
- **Invalid replies:** baseline 0, revised 0
- **Missing replies:** baseline 0, revised 0

## Invalid or missing replies

None.
