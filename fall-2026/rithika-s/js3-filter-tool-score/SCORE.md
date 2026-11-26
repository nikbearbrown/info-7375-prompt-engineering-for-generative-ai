# What moves the score — origins of every number, and one change at a time

## Where each number came from
| Object | Value | Origin |
|---|---|---|
| R1 role words | 6 phrases | **Inherited** from Priya's JS1 target (`data/target.example.json`) |
| R1 `research engineer` (v1.1) | added | **Hand-set after reading audit labels** (informal fit, no optimization) |
| R2 topic words | 10 words | **Hand-set** before measuring (FILTER.md v1.0) |
| Weights +3 (R1), +1 (R2), cap 3 | | **Hand-set** |
| Threshold | 4 | **Hand-set**; 3 tested below |
| R3 `clearance` | reject | **Inherited** (JS1 target) |
| R4 management words | reject | **Hand-set** (v1.0) |
| R4 customer-facing words (v1.1) | reject | **Hand-set after audit labels** (see AUDIT.md) |
| Sampling seed 7375; sizes 24 / 30 / 10 / 10 | | **Hand-set** |
| Wilson 95% interval | | Convention |
| Claude judge prompt (`agent/claude_judge.py`) | | **Inherited** from JS1, unchanged |
| Claude justification prompt (`prompts/justify-v1.md`) | | **Drafted by Claude Code** from my spec |

Nothing in this system was **trained** or fitted by optimization. No model weights changed.

## One change at a time, measured on the held-out 24
The held-out set was drawn first (seed 7375), excluded from the audit, and **never used for tuning**. Labels: Claude-suggested, each reviewed by me (20 approved, 4 corrected); see `labels/LABELING_METHOD.md`. Result: 2 relevant, 17 not, 5 unsure.

| Run | Object changed | Kept on corpus | Held-out: kept&rel / kept&not / rej&rel / rej&not |
|---|---|---|---|
| v1.0 | (baseline) | 70 | 0 / 0 / 2 / 17 |
| v1.1 | **filter file** (FILTER.md change log) | 36 | 0 / 0 / 2 / 17 |
| v1.1-t3 | **one setting**: threshold 4 → 3 | 133 | 0 / 0 / 2 / 17 |

**Finding:** neither change made any measurable difference on the held-out set. With only 2 relevant postings and no postings kept by any version, this held-out set **cannot distinguish the versions**. The audit improvement (14 → 5 errors) was measured on the labels used for tuning, so it remains unconfirmed on unseen data. The threshold alone moves the corpus-level kept list from 36 to 133 postings, and these held-out labels cannot say whether that helps.

**What would be needed:** a larger held-out sample, stratified toward likely positives and labeled before any tuning.

## What persistence is not proof of
v1.1 behaves differently in every new session because a **file** changed (`config/filter-v1.1.json`), not because anything learned. Likewise, if Claude answers differently across sessions after a prompt or context change, nothing was trained: the weights are fixed, and only its input changed.

## The two held-out relevant postings (generated from the files)
- v1.0: [databricks] 'Staff Software Engineer - Ingestion': score 0, rejected
- v1.0: [openai] 'Software Engineer, Platform Systems': score 2, rejected
- v1.1: [databricks] 'Staff Software Engineer - Ingestion': score 0, rejected
- v1.1: [openai] 'Software Engineer, Platform Systems': score 2, rejected
- v1.1-t3: [databricks] 'Staff Software Engineer - Ingestion': score 0, rejected
- v1.1-t3: [openai] 'Software Engineer, Platform Systems': score 2, rejected
