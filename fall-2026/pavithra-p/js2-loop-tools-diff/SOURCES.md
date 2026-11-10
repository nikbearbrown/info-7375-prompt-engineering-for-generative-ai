# SOURCES: Job-Search Agent 2

## What I used

| Source | Used for | Terms |
|---|---|---|
| The JS2 assignment and course Chapters 4–6 (`assignments/assignment-js2-the-loop-the-tools-and-the-diff.md`) | the task, the gate, the sign-off template | course material |
| My JS1 work, `fall-2026/pavithra-p/js1-contract-and-watch/` | the starting point: the relevance rule, the résumé check, the persona, the rule's wrong versions and the Pinterest seen IDs (copied in `b1b415f`) | my own work |
| [Greenhouse Job Board API](https://developers.greenhouse.io/job-board.html), `boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true` | Pinterest and Figma | public, no login; one GET per board per run |
| [Lever Postings API](https://github.com/lever/postings-api), `api.lever.co/v0/postings/{company}?mode=json` | Spotify, and `no-such-board` (fails on purpose) | public, no login; one GET per board per run |
| Ashby public job posting API, `api.ashbyhq.com/posting-api/job-board/{board}` | Ramp | public, no login; one GET per board per run |
| [The Reallocation Engine](https://github.com/nikbearbrown/the-reallocation-engine) `search/examples/aarav-patel/`, commit `d08afdd` | the fictional persona (renamed Rohan Mehta in JS1) | course repository |
| Python 3.13.1 standard library | all code and tests | PSF licence |
| Claude Code 2.1.294 (Opus 5.5) | writing the code, the tests and the first drafts of the documents | my NEU Claude Code access |

## What I made

- The `GATE.md` draft (`034c127`): the exits, budgets, repeat rule, error policy, permission policy, wrong versions and the truth line.
- The choice of boards, and the check of the 18 boundary predictions.
- Run 1, the two wrong-version runs and run 2, in my own terminal.
- The review packet's test cases and expected answers (`a5fc261`), the request for the fix, the commands I ran, and the decision to accept.
- The sign-off's checks and signature, and the reflections in `FRICTIONAL.md`.

## What Claude (Claude Code, Opus 5.5) contributed

- Tightened my `GATE.md` draft (exact boards, folders, a 10-second timeout, a third wrong version, one clarification about invalid data).
- Checked which public boards answer on each system, and drafted the 18 boundary predictions before the policy code.
- Wrote all the code in `agent/` except the files copied from JS1, and all the tests except `test_rule.py` and `test_resume.py` (from JS1). `tests/test_year_ranges.py` holds my cases, typed by Claude Code.
- Wrote the year-range fix I asked for (`0ecb3d5`), the before-and-after comparison on real jobs, and the escaped-title fix (`a18ab88`).
- Drafted `README.md`, `TRACE.md`, `FINISHED-WRONG.md`, `BOUNDARY-TESTS.md`, `REVIEW-PACKET.md`, this file and the factual entries in `FRICTIONAL.md`. The checks in the sign-off, the decision in the review packet and the reflections are mine.

## Other AI

- ChatGPT was used as a cross-check at each step.

## Constructed or real

- Real: every response body in `evidence/raw/`, every run in `runs/`, and the review evidence in `evidence/review/`, each with its date.
- Labelled: the two wrong-version runs (`WRONG-V3` in every file name), which are deliberate demonstrations.
- Constructed, and labelled CONSTRUCTED: every test fixture in `tests/`. No run was seeded.
