# Sign-off and driver's seat: JS2

## Sign-off

```text
Sign-off — Job-Search Agent 2
Checked:      TODO(Ashwin)
How:          TODO(Ashwin)
Not checked:  TODO(Ashwin) (at least three real items)
Not claiming: TODO(Ashwin)
Signed or withheld: TODO(Ashwin) (name, date)
```

### Facts to choose from (organized by Claude Code; who wrote each test matters for "my own tests")

| Evidence | Written by | Last result |
|---|---|---|
| `GATE.md` | Ashwin (TODO(Ashwin): confirm, and any Codex role) | approved 2026-11-09, `c9ff312` |
| Boundary predictions B01-B18 | Ashwin | committed `6c1c5b3`, before the tests existed |
| `tests/test_boundaries.py` (B01-B18 + wrong versions 11, 12, 14, 15) | Claude Code, after the predictions | 8 tests OK, 18/18 matched predictions |
| `tests/test_loop.py`, `test_providers.py`, `test_independent_check.py`, `test_wrong_versions.py` | Claude Code | OK on 3.9.6 and 3.12.15 |
| Review-packet test | TODO(Ashwin) | TODO |
| `independent_check.py` on the live run / the wrong-version run | Claude Code | PASS (exit 0) / FAIL (exit 1) |
| Things a human could recompute by hand | — | posting counts in `runs/*/raw/` vs `report.md`; the 404 body; attempts in `trace.jsonl` |

Candidate "Not checked" facts (Ashwin to choose, reword or replace): the watchdog deadline in
`fetch.https_get` against a slow server; rule verdicts for Ashby/Lever postings by hand; a concurrent
symlink swap; detecting a new posting across two live runs (never happened); JS1's prompt default;
`validate_course.py` exits 1.

## Driver's seat

> Drafted by Claude Code on 2026-11-10 from the commit history, for Ashwin to accept, edit or replace.
> The "why it stays mine" column is a proposal, not Ashwin's words, until Ashwin says otherwise.

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence |
|---|---|---|---|---|
| Loop: exits, budgets, repeat rule, error policy | Implement them in code exactly as written, test them offline, flag consequences (it flagged that the deliberate failure means no run can finish) | Write and approve the rules before any code; decide whether a consequence changes the rule | The rules decide what "done" and "safe" mean for my agent; a budget changes only by my written decision | `GATE.md` at `c9ff312` precedes all code (`e270605`); TODO(Ashwin): my decision on the finished-run consequence |
| Loop: the live run | Run it, save raw bytes, trace and report; run the independent check; report the real exit code | Read the trace and the attention section; decide what the run shows and does not show | Claude can run it; only I can say what I am willing to claim from it | `runs/2026-11-09T20-21-52Z-live/` (exit 1, check PASS) |
| Permission policy | List boundary cases, write the policy code and tests, fill the Actual column only from test output | Predict every outcome before the tests exist; review mismatches | A prediction checked after the fact is not a prediction | predictions `6c1c5b3` precede `tests/test_boundaries.py` at `e3d7b55` |
| Review: the defect | Reproduce it and show the output; not patch it before my test exists | Decide whether it is the change I review | Choosing what to review is choosing what to trust | `fb35380` reproduction, exit 1 |
| Review: the test | Nothing, or answer questions | Write the test, run it red | The test is my independent claim about correct behavior | TODO(Ashwin): commit of my test |
| Review: the patch | Make the smallest change that fixes the defect, in scope | Read the diff as behavior, run the commands myself, decide | Accept / revise / reject is my authorized decision | TODO(Ashwin) |
