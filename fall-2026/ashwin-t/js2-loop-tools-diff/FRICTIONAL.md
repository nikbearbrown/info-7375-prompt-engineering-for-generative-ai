# FRICTIONAL: JS2

"What happened" and "Evidence" lines are facts organized by Claude Code from the commits and outputs.
The completed entries below describe the recorded sequence and its limitations. Drafting contributions
are listed in SOURCES.md; personal feelings and unrecorded checks are not inferred.

## 2026-11-08: questions before the gate

- **What happened:** Claude Code probed nine public board URLs (one GET each) and wrote questions, not
  answers, for each GATE.md section. `hubspot` returned 404, although Lectern had recorded it as an empty
  200 board in September, so a live empty board could not be counted on.
- **Plan and limit:** Use multiple boards and include an intentional failure. A live empty-board
  example was uncertain, so the gate allowed a clearly labeled seeded replay.
- **Evidence:** `drafting/GATE-QUESTIONS.md` (`545562c`).

## 2026-11-09: writing and approving the gate

- **What happened:** A gate draft was prepared before implementation; its drafting history is recorded in SOURCES.md. Claude Code asked about four things before committing: the "approval
  pending" status, the fact that a run with the deliberate-failure board can never finish (so no state is
  ever saved), whether the agent may call `claude -p`, and who drafted the text. I approved the gate's
  decisions as written and asked Claude Code to change the status to "Approved on 2026-11-09".
- **Decision and consequence:** The approved gate permits state updates only after a finished run.
  Keeping the deliberate failure means that run stays incomplete and cannot save a baseline. The
  README records this limitation rather than claiming new-job detection was demonstrated.
- **Evidence:** `c9ff312` (gate alone, no code).

## 2026-11-09: the build and the live run

- **What happened:** Code at `e270605`, 43 tests. Live run: 5 boards observed on 3 ATSs, the deliberate
  failure 404 not retried, incomplete (exit 1), independent check PASS. Claude Code's first seeded demo
  printed a misleading state line ("not beneath runs/"); it deleted those two uncommitted runs, fixed the
  wording (`a11a167`) and re-ran.
- **Evidence and limit:** The independent checker passed the live evidence even though the loop
  exited 1. Those results answer different questions: the report matches the evidence, but one
  configured board failed. The seeded demonstration remains separate from live observations.
- **Evidence:** `f224899`, `a11a167`, `f7ce9e7`.

## 2026-11-09: a real defect

- **What happened:** Claude Code found that an interrupted in-flight request is not counted in the budget and
  is missing from the board's report; the independent checker flagged it (C7, C2). Not patched, so my test
  could come first.
- **Review choice:** Use this reproduced accounting defect for the review packet, because the
  proposed empty-board defect was absent from normal code. Preserve a failing test before patching.
- **Evidence:** `fb35380`.

## 2026-11-09 / 11-10: predictions, then boundary tests

- **What happened:** Predictions were committed at `6c1c5b3` before the boundary tests existed.
  The first run matched all 18 predictions. Earlier authorship labels needed clarification;
  SOURCES.md records the drafting contribution rather than relying on those labels.
- **Next case worth checking:** A concurrent symlink swap between path validation and file opening.
  The existing symlink-escape case does not establish resistance to that timing-dependent case.
- **Evidence:** `6c1c5b3`, `e3d7b55`.

## Review packet

- The red regression test was committed at `279c10f` before the patch. Claude Code changed only
  `jobloop/loop.py` as executable code; the unchanged test then passed. Acceptance was recorded on
  2026-11-10 and the patch committed at `be7a54a`.
- Personal check attempts ran from the wrong directory and did not test the patch. Claude Code
  subsequently ran the checks at my request and saved the output. The packet preserves that
  distinction instead of treating those runs as personal execution.

## Unresolved

- Interruptions during retry sleep or response processing are outside the verified patch path.
- No new posting was demonstrated across two live runs, and the deliberate-failure run saves no state.
- JS1 prompt-default and held-out-experiment limits remain.
- The course validator exits 1; passing project tests do not make that validator pass.
- Final personal sign-off remains pending.
