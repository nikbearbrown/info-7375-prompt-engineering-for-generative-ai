# A finished wrong answer, and the independent check that catches it

**This demonstration is SIMULATED in one place, and labelled so everywhere.** Every input is a
real raw response saved by live run 1 (`out/runs/20261111T004140Z-live/raw/`), except figma's,
which is replaced by the valid but empty body `{"jobs": []}`, as if the board had silently
returned nothing. The deliberately misspelled board is left out so that a run *can* end `finished`.

Command: `cd scripts && python3 finished_wrong_demo.py --live-check`. Output:
[`out/demo/finished-wrong/demo-output.txt`](out/demo/finished-wrong/demo-output.txt).

| Step | Who decides | Result |
|---|---|---|
| 1 | Correct loop, replay of the real responses | `finished`; anthropic 679, figma 144, openai 826 → saved as `state_before.json` |
| 2 | **Wrong version 1** (GATE §6.1, `tests/wrong_versions.py::WV1EmptyIsSuccess`) on the emptied figma | **`FINISHED, 0 new`** — ends cleanly, and is wrong |
| 3 | **Independent check** (`scripts/independent_check.py`) on step 2's report | **`CONTRADICTED`**: "agent says 0 jobs; 144 were saved before this run" and "agent says 0 jobs; a fresh GET counts 144" |
| 4 | The real loop on the same input | `incomplete`; figma `suspicious_empty`; figma's saved history unchanged |

## Why the check is independent

`independent_check.py` does not import or call the loop and does not read the agent's
conclusions as truth. It compares the report's per-board count with two sources the agent did not
produce in that run:
1. **The count saved for that board before the run.** It goes from 144 to 0, with no "board
   closed" signal.
2. **A fresh GET of the same public board,** counted by its own code (`len(json["jobs"])`). It is
   restricted to the same allow-listed hosts.

It also flags any report that says `finished` while a board was not `ok`.

## What this does not show

- It catches an empty board only when the board had jobs before, or when a live recount differs.
  A board that is truly empty on its first run would need a human to say whether that is expected.
- The live recount happened at the time in `demo-output.txt`, about 20 minutes after run 1. It
  confirms what figma had then; it is not proof about any other time.
- The independent check is a second piece of code written by Claude Code in the same session as
  the loop. It shares the allow-list module, but none of the counting code.
