# Review packet: an empty board after a non-empty baseline

**The change.** Make the loop treat a `200` with zero postings, arriving after a baseline that
had postings, as `suspect` instead of `ok`. The run ends `incomplete` rather than `finished`,
the board is escalated, its baseline is kept, and its count is `null`.

**Who did what.** Smit asked Claude Code (this session, 2026-11-08) to build the assignment.
Claude Code wrote loop v1, the test, and the patch, and ran every command quoted below. The
decision at the end belongs to Smit and is left for Smit to make after re-running the commands
in "Commands to run yourself".

## 1. The defect, reproduced before any fix

Loop v1 (commit `f2c97b4`, demo runs in `337cf1b`) reported a vanished board as healthy. Full
output and the independent check are in [WRONG_ANSWER.md](WRONG_ANSWER.md). In short:

```text
run seeded-vanish-2  [SEEDED ...]
  figma                  greenhouse ok                         count=0  new=0
exit: finished (code 0)
...
FAIL  figma: empty after non-empty        145 postings in seeded-vanish-1, 0 now, yet reported as status ok
```

The next run with Figma restored reported **all 145 old postings as new**
(`jobs/runs/seeded-vanish-3/summary.json`), because v1 had overwritten the baseline.

## 2. The test, written and committed before the patch

`tests/test_empty_after_nonempty.py`, committed alone in `66d0cbc`, before `agent/loop.py`
changed. Each assertion comes from a row of GATE.md's error policy, not from the code:

| Test | GATE.md says | On v1 |
|---|---|---|
| `test_W1_run_is_not_finished` | a suspect board makes the run `incomplete` | FAIL: `('finished', 0) != ('incomplete', 2)` |
| `test_W1_board_flagged_suspect` | status `suspect:empty_after_nonempty` | FAIL: `'ok' != 'suspect:...'` |
| `test_W1_escalated_to_human` | a `NEEDS HUMAN` line names it | FAIL: `[]` |
| `test_W1_baseline_kept` | baseline kept | FAIL: `[] != ['1', '2', '3']` |
| `test_W1_next_good_run_reports_nothing_old_as_new` | (consequence of the above) | FAIL: `['1', '2', '3'] != []` |
| `test_empty_first_observation_is_still_ok` | control: no baseline, nothing to contradict | ok |
| `test_shrinking_but_nonempty_board_is_ok` | control: shrinking is not vanishing | ok |

Saved output: `evidence/review-1-test-before-patch.txt` (`FAILED (failures=5)`). The two
controls passing on v1 matters. They show the test is about this defect and not a blanket
"empty is bad" rule that would also misfire on new or shrinking boards.

## 3. The diff, read as a change in behavior

Final diff: `evidence/review-patch.diff` (`git diff 66d0cbc 1b7f999 -- agent/loop.py`),
+10 / −2 lines, one file of production code.

```diff
-def _watch_board(base, board, budgets, budget, fetcher, trace, identical, run_dir, sleep):
+def _watch_board(base, board, budgets, budget, fetcher, trace, identical, run_dir, sleep,
+                 state_dir):
 ...
+        previous = load_state(base, board["name"], state_dir)
+        if not ids and previous and previous["count"] > 0:
+            # GATE.md error policy: empty after a non-empty baseline is not "no news".
+            result.update(status="suspect:empty_after_nonempty", count=None, observed_count=0,
+                          duplicate_ids=0, previous_count=previous["count"],
+                          reason=f"0 postings now, {previous['count']} in the baseline")
+            break
         result.update(status="ok", count=len(ids), ids=ids, duplicate_ids=dups,
```

What the diff changes in behavior, line by line:

1. **When the new branch runs.** Only after a `200` whose body parsed. A 404, timeout, 3xx, or
   bad body never reaches it, so those paths are unchanged.
2. **When it fires.** Zero distinct ids now *and* a stored baseline with `count > 0`. No
   baseline (first run) or a baseline that was already empty does not fire, so a new or
   genuinely empty board is still `ok`.
3. **What it changes downstream without touching that code.** The status is no longer `ok`, so
   three existing rules apply unchanged. `run()` marks the run `incomplete`. The state-update
   loop skips the board, which is why the baseline survives. `_finish` adds a `NEEDS HUMAN`
   line. No other function needed editing.
4. **What it reads.** One extra state-file read per successful board, through `load_state`,
   which goes through `guarded_read`. It cannot read outside `jobs/`.
5. **A side effect worth knowing.** If *every* board in a run is suspect, the existing rule
   "every board not ok → `error`" makes the run `error`, not `incomplete`. GATE.md meant
   `error` for "every board *failed*". This is arguably right (nothing trustworthy came back)
   but it was not a deliberate decision. Flagged for Smit, not changed.

## 4. Did it stay in scope?

`git diff --stat 66d0cbc 1b7f999`:

```text
 GATE.md                                       |  3 ++-
 agent/loop.py                                 | 12 ++++++++++--
 tests/mutation_check.py                       |  3 +++
 tests/test_empty_after_nonempty.py            |  6 ++++++
```

`agent/loop.py` is the fix. `tests/mutation_check.py` adds the W1 mutant (see 6).
`test_empty_after_nonempty.py` gained one assertion in the revise step (see 5); none of the
original assertions were edited or loosened. `GATE.md` changed because the review found a
contradiction in it (see 5). The policy, adapters, fetcher, and verifier did not change.
**In scope, with one disclosed widening to GATE.md.**

## 5. The first patch was revised, and why

The first version of the patch set `count=0` on the suspect board. The tests passed (57 OK),
and stopping there would have looked finished. The seeded rerun and the independent check
disagreed:

```text
run seeded-vanishfix-2  [SEEDED ...]
  figma                  greenhouse suspect:empty_after_nonempty count=0
exit: incomplete (code 2)
FAIL  figma: failure has no invented value  status suspect:empty_after_nonempty, count 0
verify seeded-vanishfix-2: agent said 'incomplete'; independent check FAILED (1)
```

Tracing the conflict led to GATE.md itself. Its **Exits** table said a failed or suspect board
reports `count: null`; its **error-policy** table said the suspect case records `count: 0`.
The patch followed one table and the verifier enforced the other. The revision chose `null`,
because a number the agent does not trust should not sit in the field people read as "the
count". The observed zero is kept as `observed_count`, so nothing is hidden. A new assertion,
`test_W1_untrusted_zero_is_not_reported_as_count`, pins this. GATE.md's error-policy row was
reworded, with a dated Decisions entry marked **Smit to confirm**.

Revised: 58 tests OK (`evidence/review-3-suite-after-revision.txt`) and the independent check
passed (`evidence/review-4-seeded-rerun.txt`).

## 6. Commands that were run (by Claude Code, 2026-11-08), with results

| Command | Result |
|---|---|
| `python3 -m unittest tests.test_empty_after_nonempty -v` on v1 | 5 failed, 2 passed (`evidence/review-1-test-before-patch.txt`) |
| `python3 -m unittest discover -s tests -t .` after the first patch | 57 OK (`evidence/review-2-suite-after-patch.txt`) |
| `python3 verify_run.py seeded-vanishfix-2` after the first patch | FAILED (1): count 0 on a suspect board |
| `python3 -m unittest discover -s tests -t .` after the revision | 58 OK (`evidence/review-3-suite-after-revision.txt`) |
| seeded rerun + `python3 verify_run.py seeded-vanishfix-3` | `incomplete`; independent check passed |
| seeded rerun with Figma restored (`seeded-vanishfix-4`) | Figma `new=0`, not 145 (`evidence/review-5-figma-restored.txt`) |
| `python3 tests/mutation_check.py` | W1 mutant (`if False:` in place of the check) caught; 10 of 10 overall (`evidence/mutation-check.txt`) |
| live run `2026-11-08T00-48-58Z` + `verify_run.py` | `incomplete` (deliberate bad name only); independent check passed |

## 7. Commands to run yourself (Smit P)

**ZIP note:** This archive has no Git history. Do not run the historical checkout row
below in the extracted folder. It requires the original clone and the named commits.
Current local verification is recorded separately in [LOCAL_VERIFICATION.md](LOCAL_VERIFICATION.md);
it does not fill in the personal-review column.

The assignment asks for "the commands you ran yourself". The table above records what Claude
Code ran. Before you decide, run these from a fresh clone and fill in the right-hand column
with what you saw:

Run by Smit P on Smit's own Mac on 2026-11-09, in the extracted folder. Output saved verbatim
in `evidence/smit-mac-run-2026-11-09.txt`.

| Command | What Smit saw |
|---|---|
| `python3 -m unittest discover -s tests -t .` | `Ran 59 tests in 0.640s`, `OK` |
| `git checkout 66d0cbc -- agent/loop.py; python3 -m unittest tests.test_empty_after_nonempty; git checkout HEAD -- agent/loop.py` (v1 code; expect `FAILED (failures=5, errors=1)`) | Not run: the extracted ZIP has no Git history. The W1 mutant in the next row plants the same defect and gave the same result, `FAILED (failures=5, errors=1)`. |
| `python3 tests/mutation_check.py` | `10/10 wrong versions caught`. W3b gave `failures=5, errors=30` on macOS, against 1 failure on Linux. |
| `python3 run_agent.py` then `python3 verify_run.py <run-id>` | Live run `2026-11-09T20-19-03Z`, a day after the baseline: Figma 146 (2 new), bad name `failed:not_found` with `null`, Spotify 85 (4 new), Linear 32 (0 new), exit `incomplete` (code 2). Independent check passed. |
| Read `evidence/review-patch.diff` and say in your own words what line 3 of section 3 means | |

## 8. Decision

Evidence for accepting the revised change: the defect reproduced (section 1); the test was
committed before the patch and failed for the right reasons with controls passing (2); the
diff is small and its effects are traced (3); scope stayed narrow with the GATE.md change
disclosed (4); the first patch was not accepted on a green suite alone (5); and the
mutation check shows the test would catch a regression (6).

Claude's recommendation: **accept the revised version**, and decide separately on the
all-suspect → `error` side effect in section 3, item 5.

**Review disposition — Smit P — 2026-11-09:** Personal acceptance withheld.
The technical recommendation is to accept the revised empty-after-nonempty patch:
59 current tests pass, all 10 mutants are caught, and the fresh baseline/empty/restored
replay preserves the baseline and reports zero old postings as new on recovery.
See LOCAL_VERIFICATION.md and evidence/local-replay-2026-11-09.txt.
These automated results do not establish personal review. The all-suspect exit policy,
large nonzero drop threshold, and GATE.md confirmations remain unresolved decisions.

## 9. A case this test would still miss

**A board that collapses but does not reach zero.** If Figma's 145 postings come back as 3
(a truncated response, a server returning one page, a half-finished migration), the guard
does not fire because `ids` is not empty. The run says `finished`, and the next good
response reports 142 old postings as new. `test_shrinking_but_nonempty_board_is_ok`
*asserts* that shrinking is fine, so the suite would defend this miss. A fix would need a
threshold (for example, a drop of more than 80% between runs), and choosing one is a
judgment GATE.md doesn't make yet.
