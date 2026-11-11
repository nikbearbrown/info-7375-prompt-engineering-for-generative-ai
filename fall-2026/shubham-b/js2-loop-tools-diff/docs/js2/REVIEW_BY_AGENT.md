# Independent review by a fresh Claude agent (2026-11-09)

A fresh Claude reviewer agent (read-only tools, no shared conversation) reviewed the JS2 work at
commit `eb7b03c` against Google's
engineering practices and Python style guide, and requirement by requirement against the JS2
assignment. It was given the code and the assignment, not the building session's conclusions.
Its report follows verbatim. What was done about each finding is at the end.

---

VERDICT: NEEDS_CHANGES

SUMMARY: I'd call the JS2 engineering strong. It was built gate-first, every live run is real and checkable, the boundary table has 20 cases, and the review order is honest. The problems are a handful of real code edge cases, a few places where the docs overstate what was done or speak for Shubham, and a packaging guard that doesn't check every placeholder. As it stands, about half of the 80 criterion points depend on parts only Shubham can write.

Goal: JS2 needs a bounded loop over at least 3 boards on at least 2 ATSs, a deliberate failure, a finished wrong answer caught by an independent check, a policy enforced in code with at least 10 cases predicted before running, a review packet, a sign-off and driver's seat, and honest past-tense evidence.

## Findings

**Blockers**

1. **`SOURCES.md` (JS2 "Review" bullet) and `docs/js2/FOR_SHUBHAM.md` item 9.** Both say "its report is `docs/js2/REVIEW_BY_AGENT.md`" and mention "the fixes Claude made from it". That file does not exist and no fixes exist yet, so this is past tense for work that hasn't happened. Fix: write that file (and the fixes) before submission, or delete both lines.
2. **`scripts/package_js2.sh:14`.** It only greps `README.md` and `FRICTIONAL.md` for placeholders. Placeholders in `SOURCES.md` ("What I wrote", the A1/A2 adoption note) and `REVIEW_PACKET.md:105,116` (the commands run and the decision) would still be zipped. `FOR_SHUBHAM.md` item 11 claims it "refuses while any `[Shubham` placeholder … remains", which is false today. Fix: `grep -rq "\[Shubham" README.md FRICTIONAL.md SOURCES.md GATE.md docs/js2/`.

**Should-fix**

3. **`watch.py:303-306`: a transient failure followed by an exhausted budget throws away the real failure.** If the next attempt is refused by `_refusal`, `get()` returns a synthetic `BUDGET_EXHAUSTED` result instead of the 503. I confirmed this with a scratch test using the harness, `max_requests=1` and a 503: the board shows `fetch_error=BUDGET_EXHAUSTED`, `http_status=None`, `raw_evidence=None`. That breaks GATE §5 ("its saved response … is kept as evidence"). `test_request_budget_also_bounds_a_retry` (test_loop.py:238) only checks the counts, so it passes anyway. Fix: when a retry is refused, emit `retry_skipped` and return the previous `result`, as the time branch already does at line 314. Then assert `http_status == 503` and that the raw was saved.
4. **The policy is defined by the file it governs (`watch.py:165-171`, `watch_cli.py:49-55`).** `allowed_hosts` and `write_root` come from the plan file. `--plan` accepts any project file, including one inside the writable `data/watch/`. I confirmed in scratch that `write_root="data"` allows writing `data/live/state.json`, and that any host is accepted. GATE §3 and §6 argue the agent "cannot change" these because `config/` is unwritable. That argument fails once the plan path is free. Separately, `check_read` runs after `load_plan` has already read the file. Fix: fix the hosts and the `data/watch` ceiling as code constants and validate the plan against them, refuse plans under `write_root`, and call `check_read` before `load_plan`.
5. **`policy.py:148-158`: `check_action` and `TOOLS` have no caller.** No production code calls them, so B19 tests a function that nothing uses. `check_read` guards only the plan file; the résumé read done by the JS1 pass is never checked, although GATE §6 says "Reads … never `private/`". Fix: call `check_action` and `check_read` at each tool entry point (the fetcher, the writer, reset, the résumé path), or reword GATE §6 and the B19 row to "enforced by having no such tool".
6. **GATE.md:194 ("a floor written by Shubham").** Claude wrote the floors; `checks/expectations.toml:4` itself says "Recorded by Claude". Fix: "drafted by Claude, for Shubham to confirm".
7. **README.md:113-120: the driver's-seat "What I should do" column is written in Shubham's first person by Claude.** Fix: label it "(Claude's draft)" or leave it as a placeholder.
8. **`checks/check_watch.py` was relaxed after it disagreed (c51335d).** The original output on 08-23-46Z was "3 failed". The `or failed` change turned it to 7/7, and the earlier evidence files were regenerated. It is disclosed in FINISHED_WRONG.md, but the checker now treats the agent's own FAILED as agreement, so it can't catch a board that was wrongly failed. Fix: keep the original red output as evidence and add a separate "agent failed but expectation met" check.
9. **`watch.py:824-858`: `reset_board` doesn't validate the token.** I confirmed that `greenhouse/x/../ashby-ramp` resolves to `ashby-ramp`'s state and gets NEEDS_APPROVAL. The `unlink()` also bypasses `OutputRoot`'s O_NOFOLLOW. Fix: call `get_provider(p).jobs_url(t)` first, as `plan_boards` does.
10. **`docs/js2/review/REVIEW_PACKET.md` and the assignment's "your test".** The A2 test, the request to the subagent and the recommendation are all Claude's. The order is correct, but nothing in the review belongs to the student yet.

**Nits**

- "1083 passed" in README.md:44, FACTS_FOR_SIGNOFF.md:21 and REVIEW_PACKET is stale; it is now 1084.
- `_sent` (the repeat counter) lives in each per-board `LoopFetcher`, so B20 is per board, not "per loop run" as GATE §4 says. It can't be reached today.
- `plan_boards` returns `list | str` as an error channel, carries a dead `""` tuple slot (watch.py:606), and uses `self.d`. `_plan_and_policy` returns `tuple[Any, Any, Any]`.
- `run_loop`'s docstring says it raises `PathRejected`, but it raises `ConfigError`.
- `FlooredProvider`'s "first parse" coupling is honestly flagged (mutation m2 survives). The packet's own suggestion (floor the live body explicitly) is the better design.
- The Ashby mapping drops `isRemote`, `workplaceType` and `secondaryLocations` (153 of 169 Ramp jobs are remote). This is listed under Not checked.
- `BUILD_LOG.md` stops at 03:18; nothing after the patch is logged.
- `DEFAULT_PLAN_PATH` is relative to the current directory, not the project root.

## Requirement table

| Requirement | Status | Evidence |
|---|---|---|
| GATE: exits, budgets, repeat, error, permission, wrong versions | Satisfied. Authored by Claude, not yet adopted | f524c91 (03:03 ET) before code (03:14); GATE §2–8 |
| Loop: at least 3 boards, at least 2 ATSs, budget, exit, observations | Satisfied | Loop 08-14-22Z: 4 real boards on GH and Ashby, 22 trace events, exit INCOMPLETE |
| Deliberate failure, no invented value | Satisfied | linearapp 404, counts null, 1 request, no state.json |
| Finished wrong answer and independent check | Satisfied (caveat in finding 8) | 08-16-16Z FINISHED; I re-ran the checker: 3 FAIL |
| At least 10 boundary cases predicted first | Satisfied (predictions by Claude) | GATE §7 B01–B20 in f524c91; 38 cases pass |
| Policy in code | Partly | Findings 4 and 5 |
| Review: reproduce, test first, diff, scope, missed case | Satisfied | Order checked; patch.diff identical to 8259d8b (same md5 of the +/- lines); red 4F/3P |
| Review: your own commands, decision | Not done (placeholders) | REVIEW_PACKET:105,116 |
| Sign-off | Not done (placeholder) | README:98-106 |
| Driver's seat | Partly | Finding 7; "why" column empty |
| Saved raw responses | Satisfied | sha256 raw = report = trace, verified by the checker |
| SOURCES / FRICTIONAL | Partly / not done | Finding 1 |
| GitHub folder and commit hash | Not done | Finding 2 |
| Honesty rule | Mostly | Runs are dated and labelled CONSTRUCTED; findings 1 and 6 break it |

## Score estimate (out of 80)

| Component | As it stands | If Shubham completes his parts honestly |
|---|---:|---:|
| Loop | 11/12 | 11/12 |
| Trace and wrong answer | 11/12 | 11/12 |
| Policy | 11/14 | 11/14 |
| Review packet | 8/14 | 12–13/14 |
| Sign-off and driver's seat | 1/8 | 6–7/8 |
| Frictional | 0–1/10 | 7–9/10 |
| GitHub posting | 0–2/10 | about 9/10 |
| **Total** | **about 44/80** | **about 68–72/80** |

**What would most help the relative-quartile 20.** Shubham should write one test himself before reading the code, aimed at the gap the packet already names (m2: a pending retry whose older saved response is below the floor). He should then make the "revise" call based on it: floor the live body explicitly. That one step gives a real "test I wrote" for the sign-off, a decision grounded in evidence, and a Frictional entry tied to a commit. Next priorities: fix findings 3 and 4, do the B18 reset live himself, and run one more live loop on a later day so a SUCCESS_WITH_NEW actually runs the rule on Ashby postings.

VERIFIED:
- Ran `uv run pytest -q` (1084 passed), `ruff check .` (clean) and `mypy src` (clean).
- Ran `checks/check_watch.py` on all five loop runs; the counts match the docs.
- Checked commit order and times, `code_commit` / `code_dirty` per run, and that patch.diff equals 8259d8b.
- Checked test counts (76 in tests/watch, 20 for Ashby).
- Inspected the Ashby raw data and the Ramp record contents (empty, because every board was a baseline or had no new postings).
- Reproduced findings 3, 4 and 9 with scratch-only scripts.

NOT CHECKED:
- Whether the subagent's isolated-worktree session happened as described.
- The careers-page facts.
- A fresh-clone `uv sync`.
- The meta-test outputs one by one; they pass as part of the suite.
- I did not run any network command.

---

## What was done about each finding

| # | Finding | What was done | Commit |
|---|---|---|---|
| 1 | This file and "the fixes" did not exist yet | This file is the report; the fixes are below | `832f1ec` |
| 2 | Packaging guard missed placeholders | Guard greps README, FRICTIONAL, SOURCES, GATE and `docs/js2/` (except the two files that quote the marker) and refuses while `GATE.md` is still a draft | `5e6eb70` |
| 3 | Budget-refused retry discarded the real failure | Test strengthened and red first, then fixed: the board keeps HTTP 503 and its saved body; `retry_skipped` says `max_requests` | `7e01e26` |
| 4 | The plan defined its own policy | Code ceilings `HOST_CEILING` and `WRITE_CEILING`; plan read-checked before parsing and refused if writable; predictions B21–B25 in GATE A3 before the tests | `e1e41b5`, `0c48e2e` |
| 5 | `check_action` unused; résumé read unchecked | Résumé read checked at loop start (B26). Never-actions reworded precisely: enforced by having no such tool plus GET-only; `check_action` kept as the name-level list | `0c48e2e`, `e1e41b5`, POLICY.md |
| 6 | A2 said the floors were Shubham's | A3 item 6 corrects it; A2 carries a pointer to the correction | `e1e41b5`, `5e6eb70` |
| 7 | Driver's seat written in Shubham's voice | The column is labelled "Claude's draft; Shubham edits" | `5e6eb70` |
| 8 | Checker relaxed after it disagreed | Reworked: facts plus one decisive "is the failure justified" row; new test catches an agent that fails a good board; the original red output is kept | `32d0d8c` |
| 9 | Reset did not validate the token | Validated with the provider first; B27 | `0c48e2e` |
| 10 | Nothing in the review is the student's yet | Left for Shubham: his commands, his decision, ideally his own test (`docs/js2/FOR_SHUBHAM.md`) | — |
| nits | Stale counts; per-board repeat counter; dead tuple slot; `Any` return; `run_loop` docstring; build log stops at 03:18 | Fixed (`7e01e26`, `b187a32`, `0c48e2e`, `5e6eb70`, this commit) | |
| nits not changed | `plan_boards` returns `list \| str`; `DEFAULT_PLAN_PATH` is relative to the current directory (same convention as JS1's `config/agent.toml`); "first parse only" design; Ashby `secondaryLocations` | Kept and disclosed; the first-parse design is Shubham's accept/revise call | |

After the fixes: `uv run pytest -q` 1093 passed; `ruff check .`, `ruff format --check .` and `mypy src` clean (run by Claude).
