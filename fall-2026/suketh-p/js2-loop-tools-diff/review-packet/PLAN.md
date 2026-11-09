# Claude Code's plan for the review-packet change (before any edit)

Drafted by Claude Code on 2026-11-08, after the student's review gate (`64357fe`) and the student's regression test (`2eb4a5f`, then `a61f07e`), and **before any edit to the agent's code**. It is a proposal: the student checks it against the allowed list in [REVIEW-GATE.md](REVIEW-GATE.md) and decides whether the edit may go ahead.

## Goal, from the student's review gate

A board that answers HTTP 200 with an empty jobs list is `unverified`, with the reason "empty jobs list" and unknown job and new-posting counts. The run keeps checking the other boards. It ends `incomplete` if another board is usable and `error` if none is, and in both cases the state is left untouched.

## The edit

| | |
|---|---|
| File | `jobwatch/loop.py`, the student's allowed list |
| Function | `classify_response`, only |
| Change | After a 200 response parses, if the parser returned no postings, return `("unverified", None, "empty jobs list: …")` instead of `("usable", [], None)` |

## What stays as it is, and why

- **`jobwatch/board.py` and `jobwatch/ats.py`.** Both parsers keep accepting an empty array, as the gate says ("The loop decides whether the response is usable"). So JS1's `tests/test_inputs.py::test_accepts_an_empty_jobs_array` stays valid.
- **Every test file.** The gate says the student's test "stays fixed during the patch".
- **The failure-control branch.** It runs before this check, so any answer other than 404, an empty 200 included, still means the failure control broke.
- **The exit logic.** It already ends the run `error` when no normal board is usable and `incomplete` when some board is unverified, and it leaves the state untouched in both cases. So the edit should need nothing else.

## What I expect, to be checked by the student's own commands

- `python3 -m unittest -v tests.test_review_empty_board`: the student's 4 tests pass (3 fail today).
- `python3 -m unittest`: the whole suite passes.

## What this plan does not address (for the student's "one case your test would still miss")

- A board that answers 200 with far fewer postings than before (say 1 instead of 675) still counts as usable. A board that was emptied **partly** is not caught.
- The trace records the empty response's bytes and sha256, but no field counts how many postings it held.
