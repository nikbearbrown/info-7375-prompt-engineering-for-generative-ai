# Review packet — Job-Search Agent 2

## The change
I asked Claude Code to make Lever and Ashby posting ids usable. JS1's `_usable_id` (agent/watch.py) accepts only integers, but Lever and Ashby ids are string UUIDs, so every posting on those boards was counted as unusable and never tracked.

## 1. Defect reproduced (before any fix)
- **Live, run 1** (Nov 10, 10:25 AM; out/runs/2026-11-10T102543/): Palantir 304/304 ids unusable, OpenAI 826/826 unusable, Glean 123/123 usable.
- **Replay on identical saved input** (config/replay_nov9.json, my Nov 9 captures): Palantir **0/304** usable, OpenAI **0/825** usable (evidence/review/1_replay_BEFORE_patch.txt).

## 2. Test written before the patch
tests/test_string_ids.py, committed in `9684c62` (Nov 10, 10:56 AM) before Claude Code made any change:
- `test_string_ids_are_tracked_not_dropped`: a UUID id is usable, and a new UUID on the next run is reported as new.
- `test_empty_or_missing_ids_are_still_unusable`: `""` and a missing id stay unusable, so a lazy "accept everything" fix fails. The bad postings have the same shape as real ones, so they can only fail for the id reason.
Both failed before the patch with `assert 0 == 1` (evidence/review/2_test_FAILS_before_patch.txt).

## 3. Patch v1, read as a change in behavior → REVISED
Claude Code changed `_usable_id` in agent/watch.py: a usable id is a non-boolean int or a non-empty string (evidence/review/3_patch_v1.diff; 1 file, 3 lines added, 1 removed). All 40 tests passed (evidence/review/4_tests_after_patch_v1.txt).
Behavior change: Lever/Ashby UUIDs became usable, which was intended. But `_usable_id` is shared, so the patch **also changed JS1's code path** (`run_watch` and `_load_seen_ids` now accept string ids). Claude Code reported that this adds a new failure mode there: `sorted()` crashes on mixed int and str ids in JS1's state write.
**Scope: not fully in scope.** I asked for the JS2 loop path only.
**Decision: revise.** Keep the rule, but apply it only where the JS2 loop decides whether an id is usable, and leave watch.py exactly as in JS1.

## 4. Patch v2 → ACCEPTED
Claude Code reverted agent/watch.py (`git diff agent/watch.py` prints nothing) and added `_usable_posting_id` in agent/adapters.py, used only by `posting_key` (evidence/review/5_patch_v2_revised.diff; 1 file, 9 lines added, 4 removed). The old import of JS1's `_usable_id` was removed.
Behavior change: in the JS2 loop, UUID ids are usable; integers unchanged; `None`, `""`, missing ids and booleans stay unusable. JS1's path is unchanged.
**Scope: in scope.** One file, one new function, one call site; no refactor, no state migration, no test or GATE change (`git diff tests/ GATE.md BOUNDARY_TESTS.md` empty).

## 5. Commands I ran myself
- `python -m pytest -v` after v1 and after v2: 40 passed each time (files 4 and 6)
- `git diff agent/watch.py` after v2: empty
- `git diff tests/ GATE.md BOUNDARY_TESTS.md`: empty
- Replay after v2 on the same Nov 9 input: Palantir **304/304** usable, OpenAI **825/825** usable, exit code 0 (evidence/review/7_replay_AFTER_patch.txt)

## 6. Decision and evidence
**Accepted v2.** The failing tests now pass; all 38 earlier tests still pass; on identical real input, usable ids went from 0 of 1,129 to 1,129 of 1,129; and the change touches only the JS2 path.

## 7. One case my test would still miss
A whitespace-only id like `" "` is accepted as usable, and nothing checks that a string id is a well-formed UUID. Neither test covers this. Also out of scope and not fixed: run 1 already wrote empty state for Palantir and OpenAI, so without action, their next live run would report every posting as new.