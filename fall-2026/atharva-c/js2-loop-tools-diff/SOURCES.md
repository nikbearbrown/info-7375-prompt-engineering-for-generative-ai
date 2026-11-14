# Sources

## Starting point

- **My Job-Search Agent 1** (`../js1-contract-and-watch/`). The skill matcher (`_word()` and the matching loop from JS1 `agent/rule.py`) was copied unchanged into `agent/skills.py` in `f982c6a`, then fixed in the review packet (`80e4fa1`). The known React/Go defect came from my JS1 README and the JS1 grader's feedback.
- The Reallocation Engine and Lectern were **not** used.

## Public endpoints used (read-only GET, no login)

| Board | System | Endpoint |
|---|---|---|
| robinhood | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/robinhood/jobs` |
| affirm | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/affirm/jobs` |
| wealthfront | Lever | `https://api.lever.co/v0/postings/wealthfront?mode=json` |
| nonexistent-co-xyz | Greenhouse | deliberate 404 |

Each run made at most 4 requests. I did not read each company's terms of use; these are the public job-board APIs that the boards themselves publish.

## Standard library only

Python 3.12.7: `urllib`, `json`, `re`, `pathlib`, `unittest`, `tempfile`, `argparse`. No third-party packages.

## What Claude Code (Opus 5.5) contributed

All in one Claude Code session, Nov 5–9, 2026.

| Commit | What Claude did | What I did |
|---|---|---|
| (planning, Nov 5) | Explained the assignment and proposed a plan and schedule | Read it; chose to start from JS1 |
| `ed62f68` | Created the folder skeleton (empty headings) | |
| `777cef4` GATE | Asked questions; wrote 4 sentences from my choices (other-4xx bullet, `out/seen.json`, `--approve` sentences, the `error`-exit exception); pointed out contradictions | Made every decision (boards, budget, retry, empty boards, `--approve`, seen-jobs option A); wrote the rest |
| `ab4ac2c` boards | Checked that the banks I first named had no Greenhouse/Lever boards; checked endpoints; wrote `boards.json` | Chose Robinhood, Affirm, Wealthfront |
| `459e7b3`, `75ff81e` | Reviewed my drafts and pointed out gaps | Wrote WRONG_VERSIONS and the boundary-table predictions |
| `f357831` | Wrote `agent/policy.py` and `tests/test_policy.py` | Ran the tests in my terminal (12/12) and saved the output to `evidence/policy-tests-20261108.txt` before the table's Actual column was filled |
| `6981c72` | Filled the Actual/Pass columns from my evidence file | Ran the tests, saved evidence |
| `4369abf` | Wrote `agent/loop.py`, `budget.json`, `tests/test_loop.py`; ran live run 1 | Ran the tests (29/29); read the trace; copied the run to evidence |
| `f982c6a` | Ported the JS1 matcher; wrote `agent/reproduce_skills.py`; made the fictional persona | |
| `e5a4ebc` | Turned my labels into `tests/test_skills.py` | Labeled the 5 real matches and chose the extra cases; ran the RED tests |
| `80e4fa1` | Wrote the React/Go patch (`review/`) | Wrote the prompt; read the diff; ran the GREEN tests; accepted |
| `b690f1b` | Fact-checked my review packet | Wrote REVIEW_PACKET.md; ran the after-patch check |
| `47a5e5d`, `27483af` | Spotted the "stopped mid-board" mislabel in my run output; wrote the failing test and the fix | Ran live run 2 and the budget demo; re-ran the demo after the fix and checked it showed `not reached` and 2 boards used |
| `b166b17` | Wrote `agent/naive_demo.py`, `agent/independent_check.py`, and the SEEDED input | Ran the naive demo, the independent check, and the recompute |
| `5f0e305` | Wrote the GATE timeout line from my decision | Decided to keep 10 seconds |
| `64d795f` README | Wrote everything except "How the loop works"; tested the commands on a fresh clone | Wrote "How the loop works" |
| FRICTIONAL, SIGNOFF | Checked my entries against the commits and evidence | Wrote them |
| This file | Drafted it from the commit history | Checked it |

## Other AI tools

None.
