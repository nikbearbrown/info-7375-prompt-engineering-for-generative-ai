# JS2 build log (factual, written by Claude)

What happened while Claude built JS2 on 2026-11-09 (ET, overnight; Shubham was away). Times are commit times from `git log`; work before a
commit happened in the minutes before it. Facts
and commits only. This is raw material for Shubham's `FRICTIONAL.md`, not a substitute for it:
the course AI policy says Claude must not invent his struggle or understanding.

| Time (ET) | What | Evidence |
|---|---|---|
| 02:51–03:00 | Read `CONTRACT.md`, the JS1 code and the JS2 assignment. Chose to build on JS1 (not the Reallocation Engine or Lectern). | — |
| before 03:03 | Probed the public APIs. Every nonexistent board answers 404 on all three systems tried (Greenhouse, Ashby, Lever). Found two wrong boards that answer **200**: `ashby/vercel` returns `{"jobs":[]}` (28 bytes), and `greenhouse/ramp` returns one stale posting ("Copy of Chief Legal Officer", "dublin"). | probe output in this session's transcript |
| before 03:03 | Picked boards by size so committed evidence stays small: Stripe (6.0 MB) and Figma (1.7 MB) on Greenhouse, Ramp (2.8 MB) and Linear (0.45 MB) on Ashby. Left out OpenAI on Ashby (13.6 MB) and Anthropic on Greenhouse (10.3 MB). Left out Lever (a third system) to keep the change small. | `config/watch.toml` |
| 03:03 | Wrote `GATE.md` v0.1 and the plan, committed before any JS2 code. | `f524c91` |
| 03:03–03:14 | Ashby IDs are UUIDs, but JS1's `PostingId` allowed only positive decimals. Widened it to decimal-or-lowercase-UUID; Greenhouse still requires integers. | `642f550` |
| 03:03–03:14 | Ashby fields mapped onto the rule's Greenhouse names, so the rule and the evidence validator did not change. Known cost: record paths cite the mapped view, not Ashby's field names (GATE §9). | `642f550` |
| 03:03–03:14 | Designing the fetcher showed GATE §3 counted redirect hops as requests, which the JS1 fetcher cannot do from outside. Wrote amendment A1 instead of quietly counting differently. | `0afcf05`, `e955298` |
| 03:14 | Claude mistake: grouped files wrongly into the first build commits (the Ashby commit lacked `models.py`). Reset the three unpushed commits and recommitted them (so their commit times are 03:14); checked that each commit imports. | `642f550`..`0afcf05` |
| 03:14 | **Live run 1.** Exit `INCOMPLETE`; the deliberate `ashby/linearapp` got a 404 and was not retried. | `43143ad`; `docs/js2/TRACE.md` |
| 03:14 | Claude mistake: a `cmd && pytest \| tail -1 && git commit` chain committed a red test, because the pipe's exit status was `tail`'s. Fixed in the next commit; used `set -o pipefail` afterwards. | `437946b` (red), `6fe3ec1` (fix) |
| 03:15–03:16 | Checked each careers page outside the agent (ramp.com/careers: `ashbyhq` 338 times, `greenhouse` 0). Wrote `checks/check_watch.py` and `checks/expectations.toml`. | `e54a26d` |
| 03:16 | **Wrong-board runs.** `greenhouse/ramp` ended `FINISHED` twice (`BASELINE`, then `SUCCESS_NO_NEW`). The independent check failed it on 3 checks. | `e8816e4`; `docs/js2/FINISHED_WRONG.md` |
| 03:17–03:18 | Wrote GATE A2 (a board below its floor is a failed board), then the test, committed red before any patch. | `b4582e7`, `affcbdd`, `docs/js2/review/red-before-patch.txt` |
| 03:18 | Sent the patch request to a fresh Claude Code subagent in an isolated worktree. A local plugin hook appended its own tool-usage block to that prompt; the request text itself is in `docs/js2/review/PROMPT.md`. | `4f22eec` |
| 03:23 | Patch came back. Its worktree had started from the stale `origin/main` (JS1), so the subagent fast-forwarded it to local `main` without committing. Claude read the diff, applied it unchanged to `main`, and ran ruff, mypy, the floor test (7 passed) and the full suite (1083 passed). | `8259d8b`, `docs/js2/review/` |
| 03:23 | Re-ran the wrong-board plan live on the patched code: `greenhouse/ramp` now `below_floor`, exit `ERROR`, state byte-identical. | `c3e937f` |
| 03:24 | Claude mistake, caught later: relaxed the checker so a failed board's missed expectations counted as agreement. | `c51335d` (see 03:40) |
| 03:25 | Mutated the patch three ways: two mutations caught, "floor every parse" survives every test. | `docs/js2/review/mutations.txt` |
| 03:27 | **Live run 2** on the patched code with floors: four boards `SUCCESS_NO_NEW`, no floor tripped, `linearapp` 404 again, exit `INCOMPLETE`. | `3019f50` |
| 03:28–03:37 | A fresh reviewer agent reviewed everything: **NEEDS_CHANGES**, 2 blockers and 8 should-fix items, three of them reproduced with scratch tests. | `832f1ec`, `docs/js2/REVIEW_BY_AGENT.md` |
| 03:37 | Fix: a retry the budget refuses had replaced the real 503 (and its saved body) with a synthetic budget error. Test strengthened first (red), then fixed. | `7e01e26` |
| 03:38–03:39 | The plan file could widen its own policy (any host, `write_root = "data"`). Wrote A3 with predictions B21–B27, then the ceilings, the read-before-parse check, the résumé read check and reset-token validation. | `e1e41b5`, `0c48e2e` |
| 03:40 | Checker reworked: a failed board's expectations are facts; one decisive row asks whether the failure is justified. The pre-relaxation output is kept. | `32d0d8c` |
| 15:40 | Second audit of the whole repo (Claude, at Shubham's request). Fixed with tests seen failing first: an I/O error on a board left no loop report; the board that stopped the loop was listed `NOT_ATTEMPTED`; the checker counted only jobs with an ID; Ctrl-D at the reset question crashed. 1096 tests. | GATE A4 |
| 20:26 (11-10) | Third main-plan live run, loop `2026-11-11T01-26-35Z` (run by Claude at Shubham's request): `INCOMPLETE` (only `ashby/linearapp` 404), 5 requests, 1.8 s. New postings: Stripe 29, Figma 6, Ramp 12, Linear 1 (the first live Ashby postings the rule judged: 13). One rule `MATCH`: Ramp `d1183b00-6590-4fe4-a585-28d84e578fe3` "Software Engineer, Security, Stablecoin", New York. Judgments deferred (no model in the loop). Independent check 25 passed, 0 failed. | `docs/js2/evidence/check-2026-11-11T01-26-35Z.txt` |

## Things that are still open

- `test_floor_must_be_positive` passed before the patch for the wrong reason (the plan refused
  every extra key). It discriminates only after the patch.
- The 94dd41a commit (policy and boundary tests) imports `reset_board` from `watch.py`, which
  arrives one commit later, so the tests do not run on that single commit. Every later commit
  runs.
- No live retry happened in any run; retries are shown only by constructed tests.
- ~~`FlooredProvider` floors "the first parse"~~ Closed 2026-11-10: Shubham decided to revise,
  wrote the m2 test (`5a08794`), and the revision floors the live response by its bytes
  (review packet §8).
