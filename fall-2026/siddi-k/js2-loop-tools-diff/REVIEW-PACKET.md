# Review packet (Chapter 6): an empty 200 needs a confirmed board identity

**The change Siddi asked for:** implement GATE.md §4's rule that "a 200 with 0 postings" is a valid empty result *only after* the board's identity is confirmed. Loop v0 (`24d6e27`) checked the response structure but not identity. Claude wrote both the test and the patch; Siddi reviews and decides.

## 1. The defect, reproduced

- **Live run `2026-11-11T03-09-02Z`** (`config/boards.wrong-answer.json`, Canva misspelled as `Canvaa`): SmartRecruiters answered **200 with `totalFound: 0`**. The agent reported `EXIT finished` with `Canvaa success, postings 0`. The run ended cleanly and was wrong.
- **The independent check caught it, not the agent** (`evidence/checks/2026-11-11T03-09-02Z.txt`): `CHECK FAILED … Canvaa: reported as a valid empty board, but nothing independent shows this board exists (closest verified board: 'Canva')`.

## 2. The test, written before the patch

- **What and when:** `tests/test_review_identity.py`, committed in `c0eea55` at 22:12 ET, before the patch commit `ef6456a` (22:13 ET).
- **Who wrote it:** Claude, from GATE §4's wording. Siddi did not write it.
- **Before the patch** (`evidence/review/1-test-before-patch.txt`):
  - `test_review_empty_200_without_identity_is_not_success` **FAILED**.
  - `test_review_empty_200_after_a_nonempty_run_is_valid` passed. This guards against an over-correction that would reject every empty board, so it was expected to pass already.

## 3. The diff, read as a change in behaviour

```diff
-        # NOTE: GATE §4 also asks that an empty 200 be accepted only once the board's identity is confirmed.
-        # This first build checks structure only; the identity check is the change reviewed in REVIEW-PACKET.md.
+        if not found and not self.previous_postings(b):
+            # GATE §4: an empty 200 is a valid result only once the board's identity is confirmed. The evidence used:
+            # an earlier run saw this same provider+slug with at least one posting. Otherwise it may be a wrong name.
+            self.emit(event="identity_unconfirmed", board=b["slug"],
+                      detail="empty board never seen non-empty in an earlier run")
+            return fail("empty_unverified")
```

(Full diff: `evidence/review/3-patch.diff`. It changes 1 file, +6/−2.)

| Situation | Before | After |
|---|---|---|
| Board returns postings | success, N | **unchanged**: the new branch only runs when `found` is empty |
| Empty 200, and an earlier run saw this board non-empty | success, 0 | **unchanged**: success, 0 |
| Empty 200, never seen non-empty (e.g. `Canvaa`) | success, 0 → run can be `finished` | **failed `empty_unverified`, no count** → run is `incomplete` |
| 404, timeout, malformed, repeat, budget | as before | **unchanged** (those paths return earlier) |

- **New side effects:** one read of earlier runs' `postings/` files, only for empty boards, through `policy.read_bytes`, so it stays inside the allowed folder. No new writes. One new trace event, `identity_unconfirmed`.
- **Did it stay in scope?** Yes:
  - One function in `agent2/loop.py`.
  - No change to the policy, the providers, the budgets or any config.
  - No existing test edited or weakened: the five wrong-version tests are byte-identical to `c0eea55`.

## 4. Evidence after the patch

- **Tests:** `python tests/run_tests.py` gives **8/8 passed**, and `python tests/mutants.py` still catches **5/5** (`evidence/review/2-tests-after-patch.txt`).
- **Live rerun** of the same `Canvaa` config, run `2026-11-11T03-12-55Z` (`evidence/review/4-wrong-answer-rerun.txt`):
  - Agent: **`EXIT incomplete`**, `Canvaa failed, reason empty_unverified (no count reported)`.
  - Independent check: **CHECK PASSED**.

## 5. Commands Siddi ran

_Siddi: run these yourself in this folder, then paste the last line of each output here._

```bash
python tests/run_tests.py
python check/independent_check.py evidence/runs/2026-11-11T03-12-55Z
```

- run_tests: ____
- independent_check: ____

## 6. One case this test would still miss

**A misspelling that lands on another company's real board.** If a typo matched a different SmartRecruiters company that does have postings, the response would be non-empty. The identity rule only runs for empty boards, so the wrong company's jobs would be reported as `success`.

A second gap: a board that was non-empty once, then left that applicant-tracking system, keeps returning a well-formed empty 200. Its old history "confirms" it, so a dead board would be accepted as genuinely empty.

## 7. Decision

**Siddi:** accept / revise / reject: ____  · because: ____
