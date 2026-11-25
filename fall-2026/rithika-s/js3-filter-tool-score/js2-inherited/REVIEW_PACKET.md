# Review packet — empty_after_nonempty

Change reviewed: Claude Code patch to `agent/loop.py`, committed as `7de028b2`.
Reviewer and decider: Rithika Sankar Rajeswari, 2026-11-10.

## 1. Defect, reproduced before any fix

SEEDED day-2 run `20261110T193722Z-SEEDED` (commit `5e49e71`): Scale AI's
replayed response was a valid 200 with zero postings (handmade,
`data/seeded_demo/day2/scaleai.json`). Its saved state held 169 IDs.

- Agent: `finished (0)`, Scale AI `ok`, postings 0, new 0. **Wrong.**
- Independent check: `FLAG scaleai: board previously had 169 postings but now reports 0`, exit 1.
- Evidence: `evidence/2026-11-10_demo_day2_SEEDED.txt`, `evidence/2026-11-10_demo_day2_independent_check.txt`

This was the "known limit" I accepted in GATE §4. I withdrew it (GATE.md
error-policy log, 2026-11-10) because of this evidence.

## 2. Test written before the patch

`tests/test_review_empty_board.py`, committed in `b8a5df3` before Claude Code
was asked for a patch. Drafted with Claude (chat), reviewed and run by me.

- Test 1: saved state [1,2,3] + 200 with zero → must be `incomplete`, reason
  `empty_after_nonempty`, new unknown, state file byte-for-byte unchanged, 1 request.
- Test 2 (guard against over-fixing): no saved state + 200 with zero → still `finished`, new 0.

Before the patch: test 1 FAILED, test 2 passed, as I predicted.
Evidence: `evidence/2026-11-10_review_test_BEFORE_patch.txt`

## 3. Prompt given to Claude Code

Allowed: `agent/loop.py`; delete only
`test_known_limit_zero_postings_accepted_as_empty_board` from `tests/test_loop.py`.
Not allowed: the review test, GATE.md, BOUNDARY_TESTS.md, policy, checker,
mutants, config, data, out, evidence. No live runs, no commit.
If anything else needed changing: stop and ask.

## 4. Scope

Claude Code stopped and asked to change one more test,
`test_flags_board_that_had_postings_and_now_reports_zero` in
`tests/test_independent_check.py`. I approved ("Yes, update it") at 2:51 PM,
before seeing the edit. Evidence: `evidence/2026-11-10_claude_code_scope_approval.png`
(screenshot retaken at 2:56 PM). I then read the edit; see section 5.

Files changed (`git diff --stat`): `agent/loop.py` (+12/−2),
`tests/test_loop.py` (−12), `tests/test_independent_check.py` (+10/−2).
Nothing else. Full diff: `evidence/2026-11-10_review_patch.diff`

## 5. The diff read as behaviour

| Input | Before | After |
|---|---|---|
| Saved state has IDs, 200 with zero postings | `ok`, new 0, state stamped as updated, run can end `finished` | `failed` (`empty_after_nonempty`), new unknown, state untouched, run `incomplete` |
| No saved state (or empty), 200 with zero | `ok`, new 0 | unchanged |

- The check sits in `_succeed` after `dedupe`, and calls the existing `_fail`.
  I read `_fail` (lines 466–475): it sets new via `failed_board_new()`, never
  writes state, schedules no retry. The patch's comments match the code.
- Checker test: now asserts the agent reports new as unknown, then rewrites the
  summary to look like the OLD agent's output and checks the checker still
  FLAGs it. This keeps the checker tested against a wrong agent. It uses a
  simulated summary, not a real run.
- Side effect: `_fail` sets `postings_seen` to unknown even though we know it
  was 0. The raw response still records the truth. Not a reason to reject.

## 6. Tests run by me after the patch

- Full suite: 142 OK (141 − 1 deleted + 2 new). `evidence/2026-11-10_full_suite_AFTER_patch.txt`
- Review tests: 2 OK. `evidence/2026-11-10_review_test_AFTER_patch.txt`
- Mutant check: 7 OK. `evidence/2026-11-10_mutant_check_AFTER_patch.txt`
- Day-2 SEEDED rerun `20261110T200439Z-SEEDED`: agent `incomplete (1)`, Scale AI
  `failed (empty_after_nonempty)`, new unknown; checker PASS ×3, exit 0.
  Scale AI's seeded state file was not modified (databricks/openai were).
  `evidence/2026-11-10_demo_day2_AFTER_patch*.txt`

Before rerunning, I checked the buggy run had not emptied Scale AI's state:
only the `"updated"` field differed from the `state_before` snapshot; all IDs
were intact, because state only ever adds IDs.

## 7. Decision

**ACCEPT.** The patch does what the gate decision says, stayed inside the scope
I approved, and the evidence above was produced by me, not taken from Claude
Code's summary.

## 8. One case the test still misses

**An Ashby board that had postings and now returns zero.** `_succeed` is shared
by both ATS types (`adapters.PARSERS[board["ats"]]`), so the code should cover
Ashby, but every review test uses a Greenhouse board. Nothing proves it.

Not handled by design either: a board that drops sharply but not to zero
(for example 169 → 1). The rule only fires on exactly zero.
