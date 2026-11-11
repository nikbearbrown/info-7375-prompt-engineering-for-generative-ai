# Review packet: the empty-board change

**The change.** In `agent/loop.py`, a board that answers HTTP 200 with a valid but **empty** posting list must stop counting as `ok` / "0 new jobs". It becomes `empty_unverified` with `new: null`, its state is left alone, and the run cannot exit `finished`.

**Who did what (honest version).** Omkar delegated the whole assignment to Claude Code on 2026-11-09 and was offline while it ran. **Claude Code chose this change, wrote the test, wrote both patches, and ran every command below.** Omkar did not type the prompt for this specific change. **The defect was planted:** GATE.md §4 already required the empty-board rule, and Claude Code left it out of the first `loop.py` on purpose, so the failure could be reproduced on real data and fixed through this packet (WRONG-ANSWER.md, *What was real and what was planned*). The live data, the failing test and both patches are real. The parts of a review that must be the human's are marked **[Omkar]**: running the commands himself, reading the diff, and the accept / revise / reject decision. Omkar did them on 2026-11-10 (§5, §6). Every time below is UTC and is backed by a file.

## 1. The defect, reproduced before any fix

| UTC | What | Evidence |
|---|---|---|
| 08:00:21 | Plain `curl`, before any code: Greenhouse `webflow/jobs` → 200, 30 bytes, `{"jobs":[]...}`; Ashby `webflow` → 200, 508,635 bytes | `evidence/probes/PROBES.log` and the saved bodies |
| 08:07:38 | Pre-patch loop, wrong-answer watch list, baseline | `runs/wrong-answer-demo/2026-11-09T08-07-38Z-wrong-answer-prepatch/` |
| 08:07:44 | Pre-patch loop, same list, watch run → **FINISHED, exit 0**, `greenhouse:webflow ok 0 postings 0 new` | `runs/wrong-answer-demo/2026-11-09T08-07-44Z-wrong-answer-prepatch-run2/report.md` |
| ~08:08 | Independent check → **CONTRADICTED** (Ashby has 22) | `…prepatch-run2/independent-check.md` |

## 2. The test, written before the patch

`tests/test_review_empty_board.py` was written and then **run against the unchanged pre-patch `loop.py`**. `cmp agent/loop.py review/before/loop.py` printed "loop.py is still the pre-patch version" just before that run.

Result at 08:08:48 (`review/test-before-patch.txt`):

```text
test_empty_board_does_not_write_state ... FAIL   (state file was written for the empty board)
test_empty_board_is_not_finished      ... FAIL   AssertionError: 'finished' == 'finished'
test_empty_board_status_and_null_new  ... FAIL   AssertionError: 'ok' != 'empty_unverified'
test_non_empty_board_still_ok         ... ok     (guard: the normal path must keep working)
FAILED (failures=3)
```

The three failures are the defect itself, each for the right reason. The fourth test is a guard against a "fix" that breaks normal boards.

The wrong version is also kept as mutant **W1** in `tests/mutants/mutants.py`. Before the patch, `run_mutants.py` reported W1 as **STALE** (`evidence/test-runs/2026-11-09T08-07-17Z-pre-patch-suite-and-mutants.txt`): the line it disables did not exist yet, because the pre-patch code **was** W1.

## 3. The diff, read as a change in behavior

**Patch v1** (08:08:54, `review/patch-v1.diff`) added 7 lines in the `outcome == "ok"` branch: if `parsed` is empty, set `status="empty_unverified", postings=0` and return no postings. Afterwards: the 4 review tests passed, the suite was 57/57, and mutants were 10/10 KILLED (`review/test-after-patch-v1.txt`).

**Reading v1's live output, not just its tests, showed it was incomplete.** In the v1 live run (`runs/2026-11-09T08-09-13Z-main-postpatch/`):
- `trace.jsonl` still recorded the Webflow observation as **`"outcome": "ok"`**, while `board_done` said `empty_unverified` (`review/v1-trace-contradiction.txt`). Anyone reading the trace alone would see an `ok` board.
- `report.md` printed `Postings: 0 (null = not observed; no value invented)`, which mixes up 0 and null in one sentence.

**Decision on v1: revise.** A fifth test, `test_empty_board_trace_and_report_agree`, was written first and run against v1. It **failed**: `Lists differ: ['ok'] != ['empty']` (`review/test-before-patch-v2.txt`).

**Patch v2** (`review/patch-final.diff`, which shows the full change from the original; `review/patch-v1-to-v2.diff` shows only the revision). Behavior, line by line:

| Hunk | Before | After | Behavior change |
|---|---|---|---|
| `fetch_board`, after parsing | a 200 with `[]` falls through as `outcome = "ok"` | `if outcome == "ok" and not parsed: outcome = "empty"`, decided **before** the observation is traced | The trace now says `empty` for an empty board. Trace and report agree |
| `fetch_board`, outcome branches | only `ok` / `permanent` / transient | a new `empty` branch: `status="empty_unverified"`, `postings=0`, returns no postings | `diff_and_judge` is never called → **state not written**, `new` stays `None`. `exit_status` sees a non-`ok` board → **`incomplete`**, never `finished`. **No retry**: the same request returns the same body |
| `render` | one sentence for every non-ok board | an empty board says "Postings: 0 observed; new: null (an empty board is not evidence of 'no new jobs')" | Report wording only |

**What did *not* change, which matters as much:** `exit_status()` is untouched. The run is `incomplete` only because the board's status is not `ok`, so the existing rule does the work. The patch also did not touch `policy.py`, `budgets.json`, the retry logic, or any other board's path.

## 4. Did it stay in scope?

**Yes.** `diff -u review/before/loop.py agent/loop.py` shows only `agent/loop.py`: 3 hunks, +14 −2 lines. No other file in `agent/` was modified after 08:07, before patch v1 at 08:08:54 (`evidence/agent-mtimes.txt` lists each file's modification time; only `loop.py` is later). Two changes **outside** `agent/` were made alongside the patch, and both are disclosed here:
- `tests/mutants/mutants.py`: the W1 mutant was re-pointed at the v2 line. Otherwise W1 would have gone STALE again (the runner refuses to apply a mutant whose source text is missing).
- `tests/test_review_empty_board.py`: the fifth test was added. **No existing assertion was weakened.**

**A later, separate change (not part of this review):** at 08:16, the end-to-end check found that two runs with the same label in the same second made the second run exit 5. `loop.py` got a 5-line fix that gives the new run a `-2` folder. At 08:21, after an independent review, the state-file read was also routed through `policy.check_read` (1 line). At 08:29, after a second review, the loop also records each request decision and each state read in the trace, with relative paths. All of these are in `review/later-fixes-after-review.diff` (5 hunks). So `diff -u review/before/loop.py agent/loop.py` now shows **extra hunks** that have nothing to do with empty boards. The reviewed v2 file is kept exactly as `review/before/loop-v2-reviewed.py`; its sha256 `55c67f41…` equals the hash recorded for `loop.py` at 08:09:42 (`evidence/agent-mtimes.txt`). To see only the reviewed change, diff against that file (command below).

**Not done, though tempting:** changing the watch list to `ashby:webflow`. That is a watch-list decision (GATE §5: the watch list and budgets change only by a written decision) and belongs to Omkar.

## 5. Commands run (by Claude Code, 2026-11-09)

```bash
python3 -m unittest tests.test_review_empty_board -v          # before patch: 3 FAIL, 1 ok
# patch v1
python3 -m unittest discover -s tests -t .                    # 57 OK
python3 tests/run_mutants.py                                  # 10/10 KILLED
python3 -m agent.loop --label main-postpatch                  # live: trace still says "ok"
python3 -m unittest tests.test_review_empty_board -v          # new 5th test: FAIL on v1
# patch v2
python3 -m unittest discover -s tests -t .                    # 58 OK (65 at the end, after later tests were added)
python3 tests/run_mutants.py                                  # 10/10 KILLED
python3 -m agent.loop --label main-final                      # live: incomplete (3), webflow empty_unverified, outcome "empty"
python3 -m agent.loop --watchlist config/wrong-answer-watchlist.json --out runs/wrong-answer-demo --label wrong-answer-postpatch   # incomplete (3)
```

**[Omkar] Commands I ran myself:**

- Old loop review tests — **2026-11-10 06:34:07 UTC** (my first run of it had no timestamp, so I re-ran it with `date -u`; both printed the same result): `FAILED (failures=4)`
- Current full test suite — **2026-11-10 06:33:01 UTC**: `Ran 66 tests`, followed by `OK`
- Mutant check — **2026-11-10 06:33 UTC**: `11/11 wrong versions KILLED` (I printed only the last 3 lines, so the `CONTROL passed` line is not shown below)

```text
$ date -u && python3 -m unittest discover -s tests -t . 2>&1 | tail -3 && python3 tests/run_mutants.py | tail -3
Tue Nov 10 06:33:01 UTC 2026
Ran 66 tests in 0.179s

OK
       killed by: test_retry_never_waits_past_deadline

11/11 wrong versions KILLED

$ date -u && T=$(mktemp -d) && cp -R agent tests persona config "$T"/ && cp review/before/loop.py "$T"/agent/loop.py && (cd "$T" && python3 -m unittest tests.test_review_empty_board 2>&1 | tail -1)
Tue Nov 10 06:34:07 UTC 2026
FAILED (failures=4)
```

The commands, at minimum:

```bash
cd fall-2026/omkar-s/js2-loop-tools-diff
# 1. the review tests against the OLD loop, in a throwaway copy (the real file is never touched)
T=$(mktemp -d) && cp -R agent tests persona config "$T"/ && cp review/before/loop.py "$T"/agent/loop.py
(cd "$T" && python3 -m unittest tests.test_review_empty_board -v)   # expect FAILED (failures=4), 1 ok
# 2. the same tests and the whole suite on the CURRENT code
python3 -m unittest discover -s tests -t . -v            # expect Ran 66 ... OK
python3 tests/run_mutants.py                             # expect CONTROL passed, then 11/11 wrong versions KILLED
# 3. read the reviewed diff yourself (only the empty-board change)
diff -u review/before/loop.py review/before/loop-v2-reviewed.py
```

## 6. Decision

**Claude Code's own decision on its v1:** *revise*. The evidence is in §3: v1 passed its tests, but its live trace contradicted its report.

**Claude Code's recommendation on v2:** accept. The 5 review tests pass, the suite passed (58 tests at v2; 66 at the end), all 10 wrong versions then defined were killed, the live run shows `incomplete` with `outcome: "empty"` in the trace, and the diff stays in one file.

**[Omkar] My decision (accept / revise / reject), my reason, and the evidence I looked at** (2026-11-10):

I would accept the patch. In the old loop, the response with code 200 and no jobs was considered successful. This is why Webflow could say "0 new" and successfully exit when 22 jobs moved to Ashby because its 22 jobs have been transferred. With the patch, the run will be exited as `incomplete`.

My decision was made based on the four tests in the review section, which failed in the old loop but passed in the new one, 66 successfully passed tests in the full suite, 11 found mutants, and the trace that showed the outcome "empty". Still, I would include a rule later for boards that return significantly fewer jobs than expected.

## 7. A case this test would still miss

**A board that is almost empty, not empty.** Suppose Webflow had moved 26 of its 27 postings to Ashby and left one old posting on Greenhouse. The loop would see 1 posting, report `ok`, and exit `finished`. Every review test still passes, because they only test the exactly-empty case, and independent-check C3 does not fire either, because it only looks at boards with 0 postings. Catching it needs a **drop rule**, for example "a board that loses more than half its postings since the last run is `suspicious`". No such rule is written in GATE.md yet, so it is not built.

A second, smaller miss: an **Ashby board whose postings are all unlisted** (`isListed: false`) parses to `[]` and is reported `empty_unverified`. That is correct by the rule, but the report does not say the postings exist and are hidden. No test covers it.

---

# Second review: Omkar's drop rule (2026-11-10)

**This change was asked for by Omkar.** §7 above names the almost-empty board as the case the first review still misses. On 2026-11-10 Omkar decided the rule himself. Claude Code asked the questions and offered options, and Omkar chose each answer. It is written in GATE.md's change log (10:37 UTC) **before** any test or code. Claude Code then wrote the test first and the code second, and ran the commands below.

**Omkar's rule:**
- A board that answers `ok` with **more than 50% fewer** postings than its last run gets the warning `suspicious_drop`, but only if the last run had **at least 10** postings.
- The first run of a board gets the warning `no_baseline`.
- Warnings **do not change the exit**: a run where every board answered is still `finished` (0). Each warning is shown in `report.md`, `report.json` and the trace.

## S1. The test, written before the change
`tests/test_drop_rule.py`, 9 tests. Run against the **unchanged** loop (`review/drop-rule/loop-before.py`): **`FAILED (failures=5)`**, saved in `review/drop-rule/test-before.txt`.
- The 5 that fail are the cases where a warning must appear: 27 → 1, 20 → 9, 10 → 4, the first run, and the report/trace check.
- The 4 that pass are the cases where nothing may be flagged: exactly 50% (20 → 10), a small board (9 → 1), growth (12 → 30), and the exit staying `finished`. The old code flags nothing, so those pass both before and after. They guard the edges of the rule.

## S2. The diff
`review/drop-rule/patch.diff`: one file (`agent/loop.py`), 4 hunks.
- Two constants: `DROP_KEEP_FRACTION = 0.5` and `DROP_MIN_PREVIOUS = 10`.
- A new method `check_drop()`, called once from `diff_and_judge()`. That is only reached for boards that answered `ok`, so empty and failed boards never get a drop warning.
- A `## Warnings` section in `report.md`.

`exit_status()` is **not** touched. The previous count comes from the board's state file (`runs[-1].postings`), which the loop already wrote.

## S3. Commands run (by Claude Code, 2026-11-10)
| UTC | What | Result | File |
|---|---|---|---|
| 10:37 | rule written in GATE.md; `loop.py` copied unchanged | — | `review/drop-rule/TIMES.txt`, `loop-before.py` |
| 10:37 | new tests vs. the **unchanged** loop | `FAILED (failures=5)`, 4 ok | `review/drop-rule/test-before.txt` |
| 10:38 | new tests vs. the **changed** loop | `Ran 9 tests … OK` | `review/drop-rule/test-after.txt` |
| 10:38 | full suite | `Ran 75 tests … OK` | — |
| 10:38 | mutants, with 3 new ones for this rule (W11: exactly 50% flagged; W12: a board of exactly 10 skipped; W13: no `no_baseline` warning) | `CONTROL passed`, **14/14 KILLED** | `review/drop-rule/mutants-after.txt` |
| 10:38:43 | live run, main watch list | `incomplete` (3), as before: Webflow empty, `klaviyoo` 404. **No warnings**, since every count moved by less than 50% (Klaviyo 152 → 148, HubSpot 122 → 125). **9 real new postings** (HubSpot 5, Spotify/Lever 4), all judged `not_relevant` by the JS1 rule. Independent check: C1 and C2 all OK; C3 Webflow CONTRADICTED again (Ashby now has 21) | `runs/2026-11-10T10-38-43Z-drop-rule-live/` |

**Not shown live:** a real `suspicious_drop`. No board dropped by more than half today. That case is shown only by the tests.

## S4. [Omkar] Commands I ran myself (2026-11-10, my terminal)

```text
$ date -u && T=$(mktemp -d) && cp -R agent tests persona config "$T"/ && cp review/drop-rule/loop-before.py "$T"/agent/loop.py && (cd "$T" && python3 -m unittest tests.test_drop_rule 2>&1 | tail -1)
Tue Nov 10 10:44:32 UTC 2026
FAILED (failures=5)

$ date -u && python3 -m unittest discover -s tests -t . 2>&1 | tail -3
Tue Nov 10 10:44:35 UTC 2026
Ran 75 tests in 0.232s

OK

$ date -u && python3 tests/run_mutants.py | grep -E "CONTROL|KILLED$|SURVIVED|INVALID"
Tue Nov 10 10:44:38 UTC 2026
CONTROL  passed: the unmutated copy passes every test
14/14 wrong versions KILLED
```

The commands, for reference:
```bash
cd ~/Desktop/info7375-week01-video/course/fall-2026/omkar-s/js2-loop-tools-diff
date -u && T=$(mktemp -d) && cp -R agent tests persona config "$T"/ && cp review/drop-rule/loop-before.py "$T"/agent/loop.py && (cd "$T" && python3 -m unittest tests.test_drop_rule 2>&1 | tail -1)   # expect FAILED (failures=5)
date -u && python3 -m unittest discover -s tests -t . 2>&1 | tail -3      # expect Ran 75 ... OK
python3 tests/run_mutants.py | grep -E "CONTROL|KILLED$|SURVIVED|INVALID"  # expect CONTROL passed ... 14/14
less review/drop-rule/patch.diff
```

## S5. [Omkar] My decision (accept / revise / reject), my reason, and the evidence I looked at (2026-11-10)
- **Decision:** Accept.
- **Does it do what I decided?** Yes, all three: more than 50% (20 → 10 is not flagged, 20 → 9 is), a minimum of 10 postings in the last run, and a warning only (`exit_status()` is untouched).
- **Evidence:** the live run report `runs/2026-11-10T10-38-43Z-drop-rule-live/report.md` (no warnings, 9 new postings), plus my own runs in §S4 (5 failures on the old loop, 75 OK, 14/14 killed) and the diff `review/drop-rule/patch.diff`.
- **What I'd change later:** nothing for now. (§S6 notes the slow-decline case as a known limit.)

## S6. A case this still misses
A board that loses jobs **slowly**, for example 30 → 20 → 13 → 8 over four runs. Each step is under 50%, so nothing is flagged, though the board lost most of its postings. Catching that would mean comparing against an older run or a running high, not just the last run.

