# Boundary predictions — written before any test runs

Arundhati K · 2026-11-10 · against GATE.md §5 (commit `3055907`)

Claude Code listed the inputs. **The "I predict" column is mine**, written before the tests or the policy
code exist. Allowed answers: **allow**, **refuse**, or **hold for approval**, plus a few words of why.
After the run, results go in the last column; I don't edit my predictions.

**How these were recorded:** 2026-11-10, 16:24–16:30 EST, in the Claude Code session. Claude asked each
case as a multiple-choice question (Allow / Refuse / Hold, same order every time, no recommended option)
and I clicked my answer; Claude copied my picks into this table unchanged and committed them before any
test or policy code existed. The "why" column is for my own words; blank means I did not write one.

| # | request | kind | I predict | why (my words) | result after run |
|---|---|---|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs` | network | **allow** | | allow ✓ |
| 2 | GET `https://api.ashbyhq.com/posting-api/job-board/notion` | network | **allow** | | allow ✓ |
| 3 | GET `https://www.linkedin.com/jobs/` | network | **refuse** | | refuse ✓ |
| 4 | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs` | network | **refuse** | | refuse ✓ |
| 5 | GET `http://boards-api.greenhouse.io/v1/boards/stripe/jobs` (http, not https) | network | **refuse** | | refuse ✓ |
| 6 | POST `https://boards-api.greenhouse.io/v1/boards/stripe/jobs/123` (an application) | network | **refuse** | | refuse ✓ |
| 7 | write `out/reports/run.md` | write | **allow** | | allow ✓ |
| 8 | write `out/../GATE.md` | write | **refuse** | | refuse ✓ |
| 9 | write `out-evil/run.md` (a sibling folder whose name starts with `out`) | write | **refuse** | | refuse ✓ |
| 10 | write `out/link/x.json`, where `out/link` is a symlink to `/tmp` | write | **refuse** | | refuse ✓ |
| 11 | read `config/boards.json` | read | **allow** | | allow ✓ |
| 12 | write `config/boards.json` | write | **allow** | | refuse **≠ my prediction** |
| 13 | read `~/.ssh/id_rsa` (outside the folder) | read | **refuse** | | refuse ✓ |
| 14 | overwrite `out/state/seen.json` **without** `--approve-state-write` | write | **refuse** | | hold **≠ my prediction** |
| 15 | overwrite `out/state/seen.json` **with** `--approve-state-write` | write | **allow** | | allow ✓ |
| 16 | write an absolute path `/tmp/x.json` | write | **refuse** | | refuse ✓ |

Results filled in by running `tests/test_policy.py::BoundaryCases.test_all_16_cases` (2026-11-10, commit `76f4137`
onward; expected values come from GATE.md §5). 14 of my 16 predictions matched.
Where I was wrong:
- **#12** write `config/boards.json`: I predicted allow; the policy refuses it (writes only inside `out/`).
- **#14** overwrite the state without the flag: I predicted refuse; the policy **holds** it (not written,
  reported as `held-for-approval`). Seen in the real run: `evidence/run-live-1/report.md` says
  "state write: held-for-approval".

Why I predicted these two differently, in my words: [FRICTIONAL.md, Entry 2](FRICTIONAL.md).
