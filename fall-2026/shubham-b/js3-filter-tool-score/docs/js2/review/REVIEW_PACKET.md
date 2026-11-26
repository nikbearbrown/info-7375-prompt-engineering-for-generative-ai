# Review packet: the GATE A2 floor change

**The change:** a planned board may carry `min_postings`. A board whose response parses but
lists fewer postings than its floor is a failed board (`INVALID_RESPONSE`, note `below_floor`),
its state is not written, and the loop cannot end `FINISHED`. Why it is non-trivial: it changes
when the loop may say "finished", it must not write state, and it must leave JS1's `jsa run` and
the empty-board rule alone.

**Who did what.** Claude (this orchestrating session) wrote amendment A2 and the test. A fresh
Claude Code subagent, with no shared conversation, wrote the patch in an isolated worktree from
the request in [`PROMPT.md`](PROMPT.md). Claude then read the diff and ran the checks below. The
decision at the end is mine.

## 1. The defect, reproduced first

Two live runs on 2026-11-09 08:16 UTC (code `e54a26d`) of `config/watch-wrong-board.toml`
ended `FINISHED`, the second with `SUCCESS_NO_NEW`, for `greenhouse/ramp`: one stale posting
("Copy of Chief Legal Officer", "dublin") while Ramp's real board on Ashby lists 169. Only the
independent check caught it (3 failures). Full account:
[`../FINISHED_WRONG.md`](../FINISHED_WRONG.md).

## 2. The test, written before the patch

Order in git, each committed before the next existed:

| Commit | What |
|---|---|
| `e8816e4` | The wrong runs and the check's failure, committed as evidence |
| `b4582e7` | GATE amendment A2: the written decision |
| `affcbdd` | [`tests/watch/test_floor.py`](../../../tests/watch/test_floor.py), 7 test cases |
| `4f22eec` | The red run and the request to Claude Code |
| `8259d8b` | The patch, applied unchanged from the subagent's worktree |

Red on `affcbdd` ([`red-before-patch.txt`](red-before-patch.txt)): **4 failed, 3 passed**. The
four fail because the plan has no `min_postings` field at all (`Extra inputs are not
permitted`), so the feature is missing rather than wrong; the loop-level misbehaviour itself is
the live reproduction in §1. Of the three that passed before the patch:
`test_board_without_a_floor_has_no_floor` is meant to (no floor means no change), and the two
cases of `test_floor_must_be_positive` passed **for the wrong reason**: the old plan refused
every extra key. They only discriminate after the patch.

Green on `8259d8b` ([`green-after-patch.txt`](green-after-patch.txt)): 7 passed; full suite
**1083 passed**. No test file changed in the patch.

## 3. The diff, read as a change in behaviour

The diff is [`patch.diff`](patch.diff) (69 lines added, 6 removed; `watch.py` and the two plans).

| Before | After |
|---|---|
| A plan entry with `min_postings` is refused (`ConfigError`). | `BoardEntry.min_postings: int \| None`, at least 1; absent means no floor. |
| `greenhouse/ramp` with 1 posting: `BASELINE`/`SUCCESS_NO_NEW`, board OK, loop `FINISHED`, the stale ID saved in state. | The board's provider is wrapped in `FlooredProvider`. Its first `parse` raises `InvalidResponse("below_floor", "1 < 20")`; JS1's `run_once` already turns that into `INVALID_RESPONSE` and writes no state; the raw response was saved before the parse and is kept. The board is FAILED with note `below_floor`; the loop cannot be `FINISHED`. |
| Empty board: `EMPTY_RESPONSE`. | Unchanged: the floor is skipped when `is_empty`. |
| `jsa run`, `pipeline.py`, `board_ok`, `decide_exit`. | Unchanged. The wrapper exists only inside the watch loop, and only for a board with a floor. |
| Plans: no floors. | `config/watch.toml`: Stripe 100, Figma 20, Ramp 20, Linear 5, none for `linearapp`. `config/watch-wrong-board.toml`: `greenhouse/ramp` 20. These are A2's numbers. |

One design choice the subagent made and flagged: **only the first `parse` in a run is
floored.** `run_once` parses the live response first, then may re-parse older saved responses to
retry pending judgments (JS1 A26); flooring those would make an old saved response unreadable
for a retry. This is correct today, but it depends on `pipeline.run_once` parsing the live body
first, which nothing outside the docstring enforces (see §6).

## 4. Did it stay in scope?

Yes, for the code: three files, all named by the request; no test edited; no unrelated refactor;
no change to JS1 behaviour (the full suite, including every JS1 test, passes). Two things the
subagent did that the request did not name, both reported by it:

- Its worktree started from the stale `origin/main` (`4b6c80f`, JS1), where none of the JS2 files
  existed. It ran `git merge --ff-only main` inside the worktree to reach `4f22eec`. That made no
  commit and did not touch `main`.
- The first `uv run` built a `.venv` inside the worktree (23 packages from `uv.lock`); nothing was
  installed outside the project.

## 5. Commands run

**By the subagent** (its report): `uv run ruff format src tests` (124 files unchanged),
`uv run ruff check src tests` (2 long docstring lines on the first run, fixed, then all passed),
`uv run mypy src` (no issues, 51 files), `uv run pytest -q` (1083 passed),
`uv run pytest -q tests/watch/test_floor.py` (7 passed), and `load_plan` on both plans.

**By Claude, after reading the diff:**

| Command | Result |
|---|---|
| `git apply --check docs/js2/review/patch.diff` then `git apply` on `main` | Clean |
| `uv run ruff check src tests`, `uv run mypy src` | All passed; no issues |
| `uv run pytest -q -p no:cacheprovider tests/watch/test_floor.py` | 7 passed |
| `uv run pytest -q -p no:cacheprovider` | 1083 passed |
| `uv run jsa watch run --plan config/watch-wrong-board.toml` (live) | `ERROR`, `greenhouse/ramp` `INVALID_RESPONSE` `below_floor`, exit 10 |
| `cmp` the board's `state.json` with that run's `state.before.json` | Identical: no state written |
| `uv run python checks/check_watch.py data/watch/loops/2026-11-09T08-23-46Z` | 7 passed, 0 failed |
| Three mutations of the patch ([`mutations.txt`](mutations.txt)) | `<=` caught; flooring empty boards caught; **flooring every parse survives** |

After the independent review, later commits fixed other parts of the loop (`docs/js2/REVIEW_BY_AGENT.md`); the full suite is 1096 tests after the second audit (GATE A4). None of those commits changed `FlooredProvider`.

**What I ran and verified:**:

```bash
git checkout affcbdd && uv run pytest -q -p no:cacheprovider tests/watch/test_floor.py   # expect 4 failed, 3 passed
git checkout main    && uv run pytest -q -p no:cacheprovider tests/watch/test_floor.py   # expect 7 passed
git show 8259d8b --stat && git show 8259d8b -- src/job_search_agent/watch.py             # read the diff yourself
uv run pytest -q                                                                          # expect every test to pass
uv run python checks/check_watch.py data/watch/loops/2026-11-09T08-23-46Z                 # expect 0 failed
```

On November 10, 2026, I checked out commit `affcbdd` and executed `uv run pytest -q -p no:cacheprovider tests/watch/test_floor.py`. It failed 4 tests and passed 3; the test was red because the floor feature didn't exist yet in the plan schema, while the defect itself had already been proven by the live runs and my manual Ramp check where Greenhouse returned a single stale posting. I then returned to `main` and ran the same test command, which passed all 7 test cases cleanly. Next, I inspected git commit `8259d8b`, verifying that the diff added 69 lines and removed 6 across `watch.py` and the two watch plans without altering `pipeline.py` or leaking into JS1 logic. I then ran the full test suite (`uv run pytest -q`), which reported 1096 passed. Finally, I executed `uv run python checks/check_watch.py data/watch/loops/2026-11-09T08-23-46Z`, which reported 6 passed, 0 failed, confirming that the independent external checker verified the patched behavior on the live loop run.

## 6. Decision

**Claude's recommendation: accept.** Evidence: the defect is reproduced live (§1); the test
existed before the patch and was red (§2); the patch is in scope and leaves JS1 alone (§3, §4);
1083 tests pass; the patched loop fails the real stale board without writing its state, and the
independent check agrees (§5). If you would rather revise, the one revision worth making is to
remove the ordering dependency: floor the live response explicitly (for example, check the
count in `LoopFetcher`'s result before `run_once` parses it) instead of "the first parse".

**My decision:** Revise — The patch addresses the defect shown by the live runs (§1), was caught red before the patch because the feature didn't exist yet (§2), stays in scope without altering JS1 (§3, §4), and passes all 1096 tests alongside the independent check (§5). However, wrapping the provider to floor only the first call to `parse()` introduces a fragile hidden ordering dependency. It relies entirely on an unwritten assumption that `pipeline.run_once` will always parse the live payload before any older saved responses for pending retries. As demonstrated by mutation `m2` in §7, our tests would fail to detect if that call order shifted or if an older saved response was mistakenly floored during a retry. I want us to revise the design to enforce the floor check explicitly at the `LoopFetcher` level before passing the live response body into `run_once`, rather than intercepting it inside a wrapped provider. — Shubham Bagwe, November 10, 2026

## 7. One case the test would still miss

> **Update 2026-11-10:** the m2 gap below is now closed by Shubham's test (`5a08794`) and the
> revision (§8). The cases the floor cannot catch at all, at the end of this section, remain.

**Flooring every parse instead of only the first.** Mutation m2 changes `FlooredProvider` to
floor every `parse` call, and all 76 tests in `tests/watch` still pass. No test has a board with
a pending judgment whose older saved response is below the floor, so nothing checks that a
pending retry can still read it. The same gap means no test would notice if `run_once` ever
parsed a saved response before the live one.

Two more the floor cannot catch at all: a stale board that still lists more postings than its
floor, and a floor written too low by hand.

## 8. The revision (after Shubham's decision to revise)

Facts, in commit order; recorded by Claude. Shubham's review of the revision is his to add.

| Step | Who | Commit | Result |
|---|---|---|---|
| The missing test from §7: a pending retry from an old saved raw below the floor keeps the board OK | Shubham | `5a08794` | Passed on `8259d8b`'s design; **failed under mutation m2** (board `FAILED`, note `below_floor`, although the live board met its floor) |
| Order-independence test, written before the revision: an old raw parsed first is not floored, the live one still is | Claude | this revision commit, file `tests/watch/test_floor_live_body.py` | Red before the revision for a missing feature (`TypeError: ... 'live_body'`), [`revision-red.txt`](revision-red.txt) |
| The revision: the floor applies to the live response, recognised by its bytes from the loop's fetcher (`LoopFetcher.live_body`), not to "the first parse"; `FlooredProvider`'s first-parse flag is gone | Claude | this revision commit, [`revision.diff`](revision.diff) | 10 floor tests pass ([`revision-green.txt`](revision-green.txt)); full suite 1099 passed; ruff, mypy clean |
| Four mutations of the revision | Claude | [`revision-mutations.txt`](revision-mutations.txt) | All four caught: floor every parse (3 tests fail, including Shubham's), fetcher never records the live body (2), `<=` (2), flooring empty boards (1) |
| Live run of `config/watch-wrong-board.toml`, loop `2026-11-11T01-14-05Z` | Claude | this revision commit | `ERROR`, `greenhouse/ramp` `INVALID_RESPONSE` `below_floor`, exit 10; `state.json` SHA-256 unchanged; independent check 6 passed, 0 failed ([`../evidence/check-2026-11-11T01-14-05Z.txt`](../evidence/check-2026-11-11T01-14-05Z.txt)) |

Why not check the floor inside `LoopFetcher`, before `run_once`, as §6 proposed: a refusal there
would reach JS1 as a failed fetch, so the board would become `FETCH_FAILED`, not the
`INVALID_RESPONSE` that GATE A2 requires, and keeping `INVALID_RESPONSE` that way would mean
changing JS1's `pipeline.py`. The revision keeps A2 and JS1 unchanged and removes the ordering
dependency by identifying the live response explicitly. The gap §7 named is now closed by
Shubham's test; the two cases the floor cannot catch at all (a stale board above its floor, a
floor written too low) remain.

**My review of the revision:** On November 10, 2026, I ran `uv run pytest -q -p no:cacheprovider tests/watch/test_floor.py tests/watch/test_floor_live_body.py` (all 10 passed) and inspected the revision diff via `git show 707ecea -- src/job_search_agent/watch.py`. Recognizing the live response by its exact bytes (`LoopFetcher.live_body`) instead of a boolean `first` flag cleanly eliminates the fragile call-ordering dependency I objected to in §6. While I originally suggested enforcing the check wholly inside `LoopFetcher`, I accept the hybrid approach because rejecting inside the fetcher would report `FETCH_FAILED` instead of GATE A2's required `INVALID_RESPONSE`, which would have forced an unwanted rewrite of JS1's `pipeline.py`. I accept the revision; the only remaining edge case is if an older saved response happens to be byte-identical to a live payload that falls below the floor, in which case the board would rightfully fail on the live response anyway. — Shubham Bagwe, November 10, 2026
