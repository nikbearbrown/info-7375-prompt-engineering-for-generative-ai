# SOURCES — what I used, what I wrote, what Claude contributed

## External sources and data

| Source | Used for | Retrieved |
|---|---|---|
| Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` (public, no login) | the only board the agent fetches; raw responses in `runs/raw/` | 2026-10-31 22:41 EDT (baseline) and 23:11 EDT (second live run) |
| `nikbearbrown/the-reallocation-engine`, `search/examples/maya-sehgal/resume.example.json` | the fictional persona résumé, copied unchanged to `personas/maya-sehgal.resume.json` (`@example.com`, 555 numbers) | local clone, 2026-10-31 |
| The INFO 7375 JS1 assignment brief (Canvas) | requirements and rubric | 2026-10-31 |
| Course repo `AGENTS.md` | the constraint "Python standard library, Claude as the only model provider" | 2026-10-31 |
| Python 3.13 standard library (`urllib`, `json`, `ssl`, `subprocess`, `unittest`, `csv`, `re`) | everything; there are no third-party packages | — |
| Claude Code CLI 2.1.316 (`claude -p`), model reported as `claude-sonnet-5-5` | the Claude judge, the sampling and experiment calls, the action-surface runs | 2026-10-31 |

No other code, posting or résumé was copied from anywhere.

## Who did what

The whole build happened in one Claude Code session (Claude Opus 5.5) on 2026-10-31. Commits marked `Co-Authored-By: Claude` were made by Claude Code in that session.

| Part | Aditya | Claude Code |
|---|---|---|
| **CONTRACT.md** | Made every decision in chat: the board, the persona, the five title phrases, no seniority exclusion, title-only matching, the US-location rule, and which three wrong versions. Chose the failure sentence from four drafts. Asked for a TA-style review. Approved the text. | Wrote the skeleton, then the wording from Aditya's answers. Checked two points against the live board: "N/A" locations, and how many postings match in the body. Drafted four failure sentences. Did the TA-style tightening. Recorded all of this in the contract's provenance block. |
| **Board choice** | Picked Stripe. | Measured board sizes and posting churn for 14 Greenhouse boards. |
| **Code** (`jobwatch/`) | Ran the tests and the wrong-version harness in their own terminal (`evidence/test-run-by-aditya-2026-10-31.md`). | Wrote all the code. |
| **Tests** (`tests/`) | Ran them. | Wrote them from the contract and committed them before the code (`e405c9f`, `5f3aed3`). Wrote `wrong_versions.py`, which plants each contract wrong version. |
| **Hand labels** (20) | **Labeled all 20 by hand** in chat. Reviewed the two that disagreed with the rule and judged both to be labeling slips. | Selected and split the postings (seeded). Transcribed the labels verbatim. Found the 18/20 mismatch by recomputing. |
| **Prompts** | Chose "the contract rule" as the labeling rule. | Wrote `judge_v1.txt` and `judge_v2.txt` and froze both before any experiment call. |
| **Sampling, experiment, action-surface runs** | Asked Claude Code to run them. | Ran every call and wrote the reports. |
| **Write-ups** (README, reports, this file, FRICTIONAL) | Reviews them, adds personal reflections to FRICTIONAL, and signs or withholds the sign-off. | Drafted all of them from the session record. |
| **Second run** | Decided to submit with a same-day live run plus a labeled SEEDED run (deadline). | Ran both, and wrote `seed_state.py`. |

## What I accepted, changed or rejected from Claude

- **Accepted:** the code, the tests, the prompt designs, and the stratified selection.
- **Changed:** "matches all" (posting body included) was my first answer. After Claude showed it would flag 101 postings, including Android Engineer and Customer Success Manager roles, I changed it to title-only matching.
- **Rejected:** Claude refused to write the failure sentence and record it as written by me, and refused to produce the hand labels. I chose a drafted sentence (marked as drafted) and labeled the 20 postings myself.
