# Sign-off — Job-Search Agent 2

```text
Checked:      (the properties, by which of my own tests — names below)
How:          by hand / by a test I wrote before reading Claude's code / by recomputation / with Claude's help
Not checked:  at least three real items
Not claiming: what this agent does not show
Signed or withheld: ____________ (name, date)
```

## Checked (facts Claude Code can point to; confirm or remove each)

| property | test / evidence | how |
|---|---|---|
| 3 boards + 1 deliberate failure across Greenhouse and Ashby; 404 not retried, no value invented | `evidence/run-live-1/report.md`; `tests/test_loop.py::Exits.test_one_404_is_incomplete_with_no_count` | live run + test written before code (`40d904c`) |
| exit is never `finished` when a board failed, was empty, or a budget hit | `Exits.*`, `Budgets.test_budget_never_reported_as_finished`, `tests/test_wrong_versions.py::WrongLoops.test_finished_always_caught` | tests before code |
| budgets: boards, requests (retries counted), seconds | `tests/test_loop.py::Budgets` (constructed responses, fake clock) | tests before code |
| repeat rule: same URL fetched once | `RepeatRule.test_board_listed_twice_fetched_once` | test before code |
| 16 permission boundary cases | `tests/test_policy.py::BoundaryCases.test_all_16_cases`; BOUNDARY-PREDICTIONS.md | my predictions before tests; tests before code |
| finished wrong answer caught by an independent check | `demo_wrong_answer.py` (SEEDED), `tests/test_check.py` | recomputation from raw files, not the agent's report |
| saved raw bytes match the trace | `check.py evidence/run-live-1/trace.json --root evidence/run-live-1/root` → no findings | recomputation (sha256) |
| Ashby names with spaces | `tests/test_providers.py` (before patch, `772af22`) | test before patch |

How, for all rows: the tests and code were written by Claude Code (with Claude's help); the tests were written from GATE.md before the code (`40d904c` before `21db57c`). I ran the full suite (43 OK), the reproduction and an approved live run myself: `review/02-my-commands.txt`.

## Not checked (my words; at least three, specific to this agent)

1. I didn't test an actual Ashby timeout or server error during a live run.
2. I didn't test an actually empty live Ashby board. The Figma empty result was from the demo.
3. I didn't check whether the seconds budget gets hit during a real run.

## Not claiming (my words)

- I am not claiming every job board will work in every situation.
- I am not claiming the agent finds every available job.
- I am not claiming an empty result always means there are no jobs.
- This is fully production-ready or has been tested against every possible edge case.

## Driver's seat

"Claude should" / "I should" / pointer columns: what actually happened, filled by Claude Code.
"Why that part stays mine": my words.

| part | Claude should | I should | why that part stays mine (my words) | pointer |
|---|---|---|---|---|
| the loop: exits, budgets, error policy | explain the options, draft GATE.md, write tests from it before code | decide the rules and accept or change the draft; check runs end with the right exit | Deciding when to exit, how much to retry, and how to report errors affects the results, so that decision should stay mine. | GATE.md `6833492`; tests `40d904c`; exits in `evidence/run-live-1/report.md` |
| the loop: approving the state write | hold the write and report `held-for-approval` without the flag | pass `--approve-state-write` myself when I want the state changed | Writing state can affect future runs. I should decide before allowing that change. | held: `evidence/run-live-1/report.md`; written by me: `review/02-my-commands.txt`, `9bb4241` |
| the review: reproduce, test, patch | find the defect, reproduce it, write the test before the patch, write the patch and the behaviour reading | run the reproduction, tests and diff myself | (same as next row) | `772af22`, `review/01-before-patch.txt`, `review/patch.diff` |
| the review: accept / revise / reject | lay out the scope facts (Greenhouse newline change) and not decide | decide on the evidence I ran | I need to review the actual changes and test results before accepting a patch. Claude shouldn't make that decision for me. | REVIEW.md §5–6; `review/02-my-commands.txt`; accept `34ed521` |

Signed or withheld: **Signed — Arundhati Kandelkar, 2026-11-10**
