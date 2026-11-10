# Boundary predictions — written before any test runs

Arundhati K · 2026-11-10 · against GATE.md §5 (commit `6833492`)

Claude Code listed the inputs. **The "I predict" column is mine**, written before the tests or the policy
code exist. Allowed answers: **allow**, **refuse**, or **hold for approval**, plus a few words of why.
After the run, results go in the last column; I don't edit my predictions.

**How these were recorded:** 2026-11-10, 16:24–16:30 EST, in the Claude Code session. Claude asked each
case as a multiple-choice question (Allow / Refuse / Hold, same order every time, no recommended option)
and I clicked my answer; Claude copied my picks into this table unchanged and committed them before any
test or policy code existed. The "why" column is for my own words; blank means I did not write one.

| # | request | kind | I predict | why (my words) | result after run |
|---|---|---|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs` | network | **allow** | | |
| 2 | GET `https://api.ashbyhq.com/posting-api/job-board/notion` | network | **allow** | | |
| 3 | GET `https://www.linkedin.com/jobs/` | network | **refuse** | | |
| 4 | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs` | network | **refuse** | | |
| 5 | GET `http://boards-api.greenhouse.io/v1/boards/stripe/jobs` (http, not https) | network | **refuse** | | |
| 6 | POST `https://boards-api.greenhouse.io/v1/boards/stripe/jobs/123` (an application) | network | **refuse** | | |
| 7 | write `out/reports/run.md` | write | **allow** | | |
| 8 | write `out/../GATE.md` | write | **refuse** | | |
| 9 | write `out-evil/run.md` (a sibling folder whose name starts with `out`) | write | **refuse** | | |
| 10 | write `out/link/x.json`, where `out/link` is a symlink to `/tmp` | write | **refuse** | | |
| 11 | read `config/boards.json` | read | **allow** | | |
| 12 | write `config/boards.json` | write | **allow** | | |
| 13 | read `~/.ssh/id_rsa` (outside the folder) | read | **refuse** | | |
| 14 | overwrite `out/state/seen.json` **without** `--approve-state-write` | write | **refuse** | | |
| 15 | overwrite `out/state/seen.json` **with** `--approve-state-write` | write | **allow** | | |
| 16 | write an absolute path `/tmp/x.json` | write | **refuse** | | |
