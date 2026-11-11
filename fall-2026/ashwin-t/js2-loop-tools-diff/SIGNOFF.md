# Sign-off and driver's seat: JS2

## Sign-off

```text
Sign-off — Job-Search Agent 2
Checked:      Interrupted-request accounting and report/trace agreement via
              tests.test_review_interrupt (3 tests); processing deadline handling and
              report-before-state ordering via tests.test_gate_gaps (6 tests);
              permission boundaries via tests.test_boundaries (8 tests, 18 cases).
              Full suite: 60 tests on Python 3.9.6 and 3.12.15.
How:          I personally ran review-packet/run-checks-ashwin.sh at commit 89013cf.
              Every command exited 0; output is in review-packet/checks-run-by-ashwin.txt.
              Test authorship and assistance are recorded in SOURCES.md. This personal
              run checked the updated code after the original patch acceptance.
Not checked:  Real slow-server deadline enforcement; concurrent symlink replacement;
              manual rule-verdict accuracy for Ashby/Lever; new-job detection across
              two live runs; interruption during retry sleep or response processing;
              stopping a classification already running when the deadline passes.
Not claiming: Independently authored tests; all interruption paths are fixed; a strict
              deadline can interrupt an active classification; live new-job detection
              was demonstrated; or the repository-wide validator passes.
Signed or withheld: Signed, Ashwin Thankachan, 2026-11-10. Reaffirmed after the gate-gap
                    fixes and my personal check run at 89013cf.
```

### Evidence and test authorship

| Evidence | Written by | Last result |
|---|---|---|
| `GATE.md` | Codex draft; Ashwin approval | approved 2026-11-09, `c9ff312` |
| Boundary predictions B01-B18 | Codex initial draft; see SOURCES.md | committed `6c1c5b3`, before the tests existed |
| `tests/test_boundaries.py` (B01-B18 + wrong versions 11, 12, 14, 15) | Claude Code, after the predictions | 8 tests OK, 18/18 matched predictions |
| `tests/test_loop.py`, `test_providers.py`, `test_independent_check.py`, `test_wrong_versions.py` | Claude Code | OK on 3.9.6 and 3.12.15 |
| `tests/test_review_interrupt.py` (review-packet test) | Codex draft, committed before the patch | red 3/3 at `279c10f`; green 3/3 after `be7a54a` |
| `independent_check.py` on the live run / the wrong-version run | Claude Code | PASS (exit 0) / FAIL (exit 1) |
| `tests/test_gate_gaps.py` | Claude Code, before the fix | 6 tests red at `e27a5cc`; green after `5917493` |
| Personal check run | Ashwin execution; Claude Code script | `89013cf`; all exits 0, full suite 60 tests on both Pythons |
| Things a human could recompute by hand | — | posting counts in `runs/*/raw/` vs `report.md`; the 404 body; attempts in `trace.jsonl` |

## Driver's seat

> Assisted drafting from the commit history; contribution details are in SOURCES.md.
> The table states responsibilities; evidence records which actions actually occurred.

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence |
|---|---|---|---|---|
| Loop: exits, budgets, repeat rule, error policy | Implement them in code exactly as written, test them offline, flag consequences (it flagged that the deliberate failure means no run can finish) | Review the drafted rules and approve them before any code; decide whether a consequence changes the rule | The rules decide what "done" and "safe" mean for my agent; a budget changes only by my written decision | `GATE.md` at `c9ff312` precedes all code (`e270605`); state rule retained; the deliberate-failure run cannot update baseline state |
| Loop: the live run | Run it, save raw bytes, trace and report; run the independent check; report the real exit code | Read the trace and the attention section; decide what the run shows and does not show | Claude can run it; only I can say what I am willing to claim from it | `runs/2026-11-09T20-21-52Z-live/` (exit 1, check PASS) |
| Permission policy | List boundary cases, write the policy code and tests, fill the Actual column only from test output | Review the assisted predictions before tests exist; review mismatches | A prediction checked after the fact is not a prediction | predictions `6c1c5b3` precede `tests/test_boundaries.py` at `e3d7b55` |
| Review: the defect | Reproduce it and show the output; not patch it before my test exists | Decide whether it is the change I review | Choosing what to review is choosing what to trust | `fb35380` reproduction, exit 1 |
| Review: the test | Preserve the failing test before patching; record who drafted and ran it | Review the assisted test against the gate | The expected behavior must be fixed before seeing a patch pass | Codex draft; red test committed at `279c10f` |
| Review: the patch | Make the smallest change that fixes the defect, in scope | Read the diff as behavior, run the commands myself, decide | Accept / revise / reject is my authorized decision | accepted 2026-11-10; patch `be7a54a`; initial checks run by Claude Code; later personal checks at `89013cf` passed (`checks-run-by-ashwin.txt`) |
