# FRICTIONAL — what I tried and what happened

**About this log:** Claude Code drafted Part 1 on 2026-11-10 from what actually happened in the session. Each row is traceable to a commit or file. Part 2 is mine.

## Part 1 — Log of events

| # | When | What was tried | What happened | Checked / changed / learned | Trace |
|---|---|---|---|---|---|
| 1 | Nov 9 | Use Lectern's documented "valid but empty board" (`greenhouse/hubspot`) for the finished-wrong demo | Probed live: `hubspot` now returns **404**, not an empty board. The lesson in Lectern's notes was no longer true. | **Changed:** I used a real case found the same day instead: Greenhouse `ramp` returns 200 with 1 stale posting, while Ashby `ramp` has 175. | GATE.md provenance |
| 2 | Nov 9 | Probe the candidate boards | `greenhouse/notion`, `greenhouse/openai`, `lever/netflix` and `lever/plaid` all returned 404 | I picked boards from probes, not memory: Ashby for OpenAI and Notion, Lever for Palantir. | GATE.md |
| 3 | Nov 9 | Write tests before the code | The first implementation passed all 50 tests immediately | Passing on the first try isn't proof the tests bite, so I planted each wrong version: caught by 4, 1 and 1 tests. Wrong versions 2 and 3 are each caught by a **single** test, which is thin. | `9ff7b87`, `tests/wrong_versions.py` |
| 4 | Nov 9 15:45 | First live run with the deliberate-failure board | Exit `incomplete`, not `finished`, so the run that shows the failure can't also be the "ends cleanly" demo | **Changed:** I added `boards.finished-wrong.json` and a second run (15:46) that ended `finished` and was still caught as wrong. | `1c5760f` |
| 5 | Nov 9 | Claude Code read its own `check_run.py` | Found that it read `raw_path` without the permission policy, a gap between the gate and the code that no test covered | It became the review packet. | `aae20af` |
| 6 | Nov 10 | Claude Code re-ran the check on the real run while testing patch v1 | **It overwrote the committed `check.json` / `check.md`** with new numbers (18 days, 173 postings) | Claude Code restored them with `git checkout -- runs/` before any commit. **Learned:** the check writes to a fixed filename, so re-running it overwrites earlier evidence. **Unresolved:** it should write timestamped files. | session; `runs/…906e94/check.*` unchanged since `1c5760f` |
| 7 | Nov 10 | Review patch v1 | Green: 51 tests and the repro passed | **I revised it anyway**: a wrong file *inside* the folder still passed. My 3 new tests failed on v1, then passed on v2. | `1567edd`, `ca8725e`, `a5dc929` |
| 8 | Nov 10 | Rebased onto `main` before writing commit hashes into the docs | 76 new commits on `main` changed all my hashes | I rebased *before* citing hashes (in JS1 I had to remap them afterwards). | git log |
| 9 | Nov 10 13:47 | Second calendar day run | 57 new postings across 5 boards; 1 relevant | First real "new" data. The Nov 9 15:45 run was the baseline; the 15:46 run had state but found 0 new 30 s later. | `1997454` |
| 10 | Nov 10 | Asked Claude Code to review the work as a TA; it used an independent reviewer subagent | It found 7 real problems. The worst: **patch v2, which I had accepted, broke re-checking committed runs on any other machine** (absolute `raw_path`s). Others: GATE said the check "has its own trace" (it didn't); "recomputes every count" was overstated; the CLI read `--boards` without the policy; `run --approve-reset` was documented but missing; wrong versions 2 and 3 were each caught by only 1 test. | **Learned:** green tests on my machine were not a fresh-clone check, and a review I accepted still missed a scope effect. Fixed test-first: 7 new tests failed, then patch v3, now 67 pass and the wrong versions are caught by 5, 4 and 5 tests. **Not changed:** GATE.md stays as approved; the code now matches it. | `a08f363`, v3 |

### Unresolved
- The retry path and `budget-exhausted` never happened live; they are tested only with fakes. Policy refusals were shown on the real CLI (evidence/).
- The check overwrites its output files on re-run (row 6).
- The wrong-attempt raw file case (review packet).
- The independent check can't catch a wrong board that is large and fresh.

## Part 2 — My reflections (Aditya)

*Written by Aditya in chat on 2026-11-10. At Aditya's request, Claude Code fixed only the grammar and kept the meaning; the original wording is kept below the fixed version.*

- **What surprised me:** I expected patch v1 to work perfectly without revision. That was the only thing that surprised me.
- **Why I revised v1:** it did not catch every case it should have. To be fully honest, it was Claude that found the missing case, but the decision to revise was mine.
- **What I would do differently:** expand the scope and add more tests. A job-search agent can have a much broader scope, and could find roles that don't match my titles closely but would still be an okay fit to apply for.

<details><summary>Original wording (verbatim)</summary>

a. I expected v1 to work perfectly without revision. That is the only thing that surprised me.

b. It was not catching all the test cases as expected. Full honesty, it was claude that caught the case, but the decision was mine.|

c.Probably expand the scope and increase the tests. The job search agent can have a much broader scope and possibly find roles that don't align much but would still be a okay fit to apply for.
</details>
