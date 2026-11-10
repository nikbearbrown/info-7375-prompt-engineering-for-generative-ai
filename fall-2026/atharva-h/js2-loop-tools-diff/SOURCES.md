# SOURCES — Job-Search Agent 2

## What I built on
- **My Job-Search Agent 1 code,** `../js1-contract-and-watch/` at commit `f0b7a6b` (submitted 2026-10-31). JS2 kept its Python-standard-library approach, the idea of an allow-list, the path check, and saved state. JS2's code is new.
- **Not used:** the Reallocation Engine and the instructor's Lectern collector.
- **Course materials:**
  - the Job-Search Agent 2 brief
  - Chapters 4–6 (the agent loop and its exits, tools and permissions, and diff review)
  - the course AI policy: [AI Policy for Professor Bear's Courses | Using AI Responsibly in Class](https://youtu.be/8Ut0Cdl6vMw?si=9w3aEpt1ZyAR4Kiz)
- **JS1 grading feedback:** the TA's advice to use labels with real relevant cases and keep the rule two-valued. JS2 does no labeling or judging. Its only outcomes are the four exits in `GATE.md`, each defined with what it reports.

## Public endpoints
These are public and need no login. Everything this folder says about how they behave comes from the responses saved in `runs/*/raw/`, not from documentation.

| System | Endpoint | What it was used for | First probed |
|---|---|---|---|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true` | job list | 2026-11-01 |
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{token}` | the board's own name (identity check) | 2026-11-01 |
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/{token}` | job list; a wrong name gives a plain-text 404 body | 2026-11-01 |
| Lever | `https://api.lever.co/v0/postings/{token}?mode=json` | job list | 2026-11-01 |

**Python standard library modules used:** `urllib.request`, `urllib.parse`, `urllib.error`, `socket`, `json`, `os`, `re`, `sys`, `argparse`, `datetime`, `time`, `tempfile`, `unittest`, and `unittest.mock`.

## What Claude Code contributed
I used Claude Code (desktop app, Claude Opus 5.5) in sessions on 2026-11-01, 2026-11-09, and 2026-11-10. The JS2 code itself never calls Claude: there's no `claude -p` and no API call. No Claude response is quoted in this folder.

| Part | Claude Code | Me |
|---|---|---|
| `GATE.md` | Interviewed me one section at a time and offered options. Pointed out that my first exit choice left `incomplete` undefined. Proposed the four wrong versions and the 2026-11-09 additions. Wrote the wording from my answers. | Chose every rule, accepted the wrong versions, and made the 2026-11-10 decision after review |
| `PERMISSIONS.md` | Drafted the 23 boundary cases and their predicted outcomes from the gate. They were committed before any test or policy code (`159adc2`). Filled in the Actual column from the test run (`e32740e`). | Accepted the cases |
| Code | Wrote every Python file: `loop.py`, `adapters.py`, `tools.py`, `policy.py`, `agent.py`, `check_identity.py`, `crosscheck_days.py`, and `precheck.py` | Reviewed the test results and the after-patch run. Both ran with AI help. |
| Tests | Wrote `tests/helpers.py`, `test_policy.py`, `test_loop.py`, and `test_adapters_and_gate.py`. Supplied the setup lines of `test_review_identity.py` and helped draft its assertions. | Accepted the assertions in `test_review_identity.py` before any patch existed |
| Review patch | Wrote `b3f5adb`. Flagged before patching that existing request counts would change and the gate would gain a rule. Kept `check_identity.py` separate. Helped run the review commands and review the changed budget test. | Chose the defect, reviewed the diff and the results of the commands in `REVIEW_PACKET.md`, and accepted the patch on that evidence. Left aliases and the `KeyError` handler out of scope. |
| Live runs | Ran day 1, the wrong-board demo, both identity checks, day 2, and the day-2 cross-check in my session. Found that the "new" Abacus posting was a relisting. Helped run the after-patch wrong-board run and the live approval prompt. | Confirmed the after-patch run's command and results. Exercised the live y/N approval prompt with AI help: `N` on the real state, and `Y` only on a disposable copy. |
| Documents | Drafted `README.md`, `WRONG_ANSWER.md`, `REVIEW_PACKET.md`, this file, `SIGNOFF.md`, and the `FRICTIONAL.md` entries, from my sessions and this folder's files | Reviewed them. The signature in `SIGNOFF.md` is mine. |

I am responsible for everything submitted here and can explain any part of it.
