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

<!-- How: which of these did YOU check, and how? Which were Claude's help only? Say so per row. -->

## Not checked (my words; at least three, specific to this agent)

<!-- Questions to help you find real ones:
- The timeout and 5xx retry were only tested with constructed responses. Did a real timeout ever happen?
- Was a REAL empty board ever seen, or only the constructed one?
- Was the seconds budget ever hit by a real run?
- Was the symlink test run on anything but macOS?
- Did a second live run ever show a real "new since last run" posting?
- Is check.py's "drop to zero" rule right for a company that really closes all its jobs?
-->

1.
2.
3.

## Not claiming

<!-- e.g. that it judges relevance (JS2 has no relevance rule), that it watches more than these boards... -->

## Driver's seat

| part | Claude should | I should | why that part stays mine | pointer |
|---|---|---|---|---|
| the loop: exits, budgets, error policy | | | | GATE.md `6833492`; tests `40d904c` |
| the loop: approving the state write | | | | `--approve-state-write`; `evidence/run-live-1/report.md` (held) |
| the review: reproduce + test | | | | `772af22` |
| the review: accept / revise / reject | | | | review/REVIEW.md §6; patch commit |

Signed or withheld: ____________
