# Sources and contributions

## What was used

- **The brief:** `assignments/assignment-js2-the-loop-the-tools-and-the-diff.md` in this repository, read 2026-11-09.
- **Starting point:** my JS1 folder `fall-2026/shreyash-y/js1-contract-and-watch` at the submitted commit `bb193d9`. `jsagent/posting.py`, `rule.py` (v1), `persona.py`, `validator.py`, `persona/alex_morgan.json` and `tests/test_rule.py` were copied unchanged in `4213c8c`. JS1's saved raw responses supplied the real postings in `tests/fixtures/js1_real_postings.json`, with sha256 recorded. The Reallocation Engine and Lectern were not used.
- **Boards:** the public job-list endpoints of Greenhouse (`boards-api.greenhouse.io`: oscar, klaviyo), Ashby (`api.ashbyhq.com`: linear) and Lever (`api.lever.co`: palantir, whoop, and the deliberately non-existent oscarhealth-doesnotexist).
  - **Live runs 1 and 2 (2026-11-09) and 3 (2026-11-10):** the agent fetched these and saved every response unchanged in `runs/<run_id>/raw/`.
  - **Before GATE.md existed:** Claude Code fetched a few Ashby and Lever boards with `curl`, only to see which names answer and what the responses look like. Nothing from those fetches was saved or used.
- **Classmates:** two classmates' JS2 folders were visible in the repository listing on 2026-11-09. Only their file names were seen, and no code or text was taken.
- **Tools:** Python 3.14.6 standard library; Claude Code (model `claude-opus-5-5`) as the coding agent; `git`, `gh`, `shasum`.

## What Shreyash wrote or decided

| Part | Where |
|---|---|
| GATE.md: boards, exits, budgets, repeat rule, error policy, permission policy, wrong versions, review-packet plan. Pasted 2026-11-09; Claude Code changed formatting only and added the labeled budget table. | `GATE.md` (`9fbab0d`) |
| The review decisions: rev 1 revise, rev 3 accept with known limitations | `review/05-decision-on-rev1.md`, `review/18-decision-on-rev3.md` |
| Commands run in Shreyash's own terminal, with their output | `review/04`, `review/17` |
| The JS1 rule decisions (mandatory experience only; remote must be workable from Massachusetts) and the JS1 hand labels used as expectations | JS1 `labels/DISPUTED-POSTINGS-REVIEW.md`, JS1 experiment-2 `hand-labels.csv` |
| "What I understood from the diffs" | the top of `REVIEW-PACKET.md` |
| Three open items settled after reading the ads (7809608003, the two Linear ads, Palantir `Dev`) | `review/19-open-items-decided-2026-11-10.md` |
| Commands run in Shreyash's own terminal on 2026-11-10 (the `2b8ed44` check, the full suite, the frozen hashes) | `evidence/commands-run-by-shreyash-2026-11-10.txt` |
| The README summary, Part 1 of FRICTIONAL.md (including the three entries added 2026-11-10), and the signature | `README.md`, `FRICTIONAL.md` |

## What Claude Code contributed

| Part | Notes |
|---|---|
| `GATE-NOTES.md` | how each GATE.md phrase became code, with the open choices marked |
| All new code: `jsagent/policy.py`, `providers.py`, `transport.py`, `loop.py`, `check.py`, `__main__.py`, and the rule v2 patch (three revisions) | written by Claude Code |
| All tests, the boundary-test predictions, and the wrong-version implementations | written by Claude Code before the code they test (commit order in README) |
| Running the live run, the seeded demo, the mutation check and the behavior diffs | at Shreyash's request |
| The reading of the behavior diffs that found the rev 1 and rev 2 defects | `review/03`, `review/11`, `review/16`; Shreyash decided on rev 1 and rev 3 |
| `README.md` (except the summary and the signature), `REVIEW-PACKET.md`, `TRACE.md`, `BOUNDARY-TESTS.md`, and Part 2 of `FRICTIONAL.md` | drafted by Claude Code from the files |
