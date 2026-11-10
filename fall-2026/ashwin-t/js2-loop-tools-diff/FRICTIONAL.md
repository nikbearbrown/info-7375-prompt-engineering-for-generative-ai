# FRICTIONAL: JS2

"What happened" and "Evidence" lines are facts organized by Claude Code from the commits and outputs.
Every `TODO(Ashwin)` line is mine to write from my own experience; none is filled in for me.

## 2026-11-08: questions before the gate

- **What happened:** Claude Code probed nine public board URLs (one GET each) and wrote questions, not
  answers, for each GATE.md section. `hubspot` returned 404, although Lectern had recorded it as an empty
  200 board in September, so a live empty board could not be counted on.
- **I tried / expected:** TODO(Ashwin)
- **Evidence:** `drafting/GATE-QUESTIONS.md` (`545562c`).

## 2026-11-09: writing and approving the gate

- **What happened:** GATE.md was written (TODO(Ashwin): confirm who drafted it, and any Codex role). Claude Code asked about four things before committing: the "approval
  pending" status, the fact that a run with the deliberate-failure board can never finish (so no state is
  ever saved), whether the agent may call `claude -p`, and who drafted the text. I approved the gate's
  decisions as written and asked Claude Code to change the status to "Approved on 2026-11-09".
- **What I did / why:** TODO(Ashwin)
- **Evidence:** `c9ff312` (gate alone, no code).

## 2026-11-09: the build and the live run

- **What happened:** Code at `e270605`, 43 tests. Live run: 5 boards observed on 3 ATSs, the deliberate
  failure 404 not retried, incomplete (exit 1), independent check PASS. Claude Code's first seeded demo
  printed a misleading state line ("not beneath runs/"); it deleted those two uncommitted runs, fixed the
  wording (`a11a167`) and re-ran.
- **What I checked / understand now:** TODO(Ashwin)
- **Evidence:** `f224899`, `a11a167`, `f7ce9e7`.

## 2026-11-09: a real defect

- **What happened:** Claude Code found that an interrupted in-flight request is not counted in the budget and
  is missing from the board's report; the independent checker flagged it (C7, C2). Not patched, so my test
  could come first.
- **What I decided:** TODO(Ashwin)
- **Evidence:** `fb35380`.

## 2026-11-09 / 11-10: predictions, then boundary tests

- **What happened:** I wrote predictions for B01-B18. Claude Code asked who wrote them, because the header
  called them "proposed expectations for Ashwin to review"; I answered that I wrote them myself, and the
  header was reworded. Tests were written after `6c1c5b3`; first run: 18/18 matched.
- **What surprised me / what I would test next:** TODO(Ashwin)
- **Evidence:** `6c1c5b3`, `e3d7b55`.

## Review packet

- TODO(Ashwin): attempts, the decision, what I accepted / changed / rejected from Claude, with commits.

## Unresolved

- TODO(Ashwin)
