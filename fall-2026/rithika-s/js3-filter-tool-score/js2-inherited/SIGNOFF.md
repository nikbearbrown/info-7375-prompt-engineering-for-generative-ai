# SIGN-OFF — JS2 Loop, Tools, and Diff

Rithika Sankar Rajeswari, INFO 7375, Fall 2026.

## Who was in the driver's seat

| Step | Proposed by | Decided / done by | Evidence |
|---|---|---|---|
| Copy JS1 as the starting point | me | me | `b9ede94`, 42 tests pass |
| GATE.md (exits, budgets, repeat rule, error policy, permissions, W1–W11) | Claude (chat), one section at a time | me (accepted each section) | `d761cc3`, `7af9366` |
| Boundary-test predictions B01–B19 | Claude (chat) | me, before any policy code | `7af9366` |
| Build: loop, policy, adapters, transport, checker, tests, mutants | Claude Code | Claude Code wrote it; I reviewed it and ran every suite | `e9d8ef1`, `evidence/2026-11-10_full_suite_run.txt` |
| Budget reasoning correction, B20 | Claude Code found both gaps | me (kept 90 s, added B20) | `82e67f8` |
| Live run 1 | me | me | `3749c43`, `evidence/2026-11-10_live_run1_terminal.txt` |
| `--boards` option | me (asked for it) | Claude Code wrote it; I checked scope and ran 141 tests | `d18025d` |
| SEEDED finished-wrong-answer demo | Claude (chat) suggested the design | me (built the inputs, ran it) | `5e49e71` |
| Withdraw the GATE §4 known limit | me, based on the demo | me | `b8a5df3` (GATE.md log) |
| Review test, written before the patch | Claude (chat) drafted it | me (predicted, ran, committed it failing) | `b8a5df3` |
| `empty_after_nonempty` patch | Claude Code | Claude Code wrote it | `evidence/2026-11-10_review_patch.diff` |
| Extra checker-test change (out of scope) | Claude Code asked | me (approved before seeing it, then read it) | `evidence/2026-11-10_claude_code_scope_approval.png` |
| Accept the patch | Claude (chat) drafted the packet | me (decision: ACCEPT) | `7de028b2`, `764ac2f6` |
| FRICTIONAL, README, SOURCES | Claude (chat) drafted | me (reviewed and edited) | `bcfa0cef`, `ef9ceba0`, `b8a645fb` |

## What I am signing for

- I can explain every file in this folder, including the parts Claude Code wrote.
- Every test count and run result in these documents comes from a run I did
  myself, saved in `evidence/`, not from an AI summary.
- SEEDED runs and inputs are labeled SEEDED. The only live run is `20261110T183029Z`.
- Known limits I accept: no test covers `empty_after_nonempty` on an Ashby
  board; a sharp drop that is not to zero (for example 169 → 1) is not caught;
  the fix has not been seen on a live board that really went empty.

Signed: Rithika Sankar Rajeswari 2026-11-10
