# SOURCES: who wrote what, and where facts came from

Claude Code drafted this file from the commit record and the student's answers. The student's statements about authorship are quoted as the student gave them. Claude Code cannot see how a file was drafted before it arrived, only when it arrived and what it said.

## The student's files

| File | Written by | Record |
|---|---|---|
| [GATE.md](GATE.md) | The student. Asked on 2026-11-08, they answered "I wrote it myself" | Committed byte-for-byte before any code, `b55d2a5` |
| Predictions in [policy/BOUNDARY-PREDICTIONS.md](policy/BOUNDARY-PREDICTIONS.md) | The student, pasted in chat (the 21 cases themselves are Claude Code's) | `f871ccb`, before any policy code |
| [review-packet/REVIEW-GATE.md](review-packet/REVIEW-GATE.md) | The student, who answered "I wrote both myself" (this file and Frictional entry 2) | `64357fe`, before any test or patch |
| [tests/test_review_empty_board.py](tests/test_review_empty_board.py) | The student, who answered "I wrote it myself". It uses Claude Code's test helpers (`tests/test_loop.py` `LoopCase`, `tests/fakes.py`). The all-empty case was Claude Code's proposal, which the student adopted | v1 `2eb4a5f`, v2 `a61f07e`, both before the patch |
| [review-packet/REQUEST.md](review-packet/REQUEST.md) | The student's chat message, verbatim | `4dccaee` |
| [review-packet/AUDIT-RECORD.md](review-packet/AUDIT-RECORD.md), [review-packet/DECISION.md](review-packet/DECISION.md) | Supplied by the student as their own | `82739cd` |
| The student's entries in [FRICTIONAL.md](FRICTIONAL.md) | The student, who confirmed on 2026-11-08 that they wrote them | verbatim, under headings Claude Code added |

On 2026-11-08 Claude Code asked once more, naming the folder these files came from on the student's machine, whether any AI tool had helped with GATE.md, REVIEW-GATE.md, the test, or the Frictional entries. The student answered: "Yes, all written by me".

## The student's choices among options Claude Code laid out

Each was a choice between options Claude Code wrote, with no recommendation given:
- An approval naming another run or file: **incomplete**, not error.
- A redirect from a configured board: **the board is unverified and the run keeps going**, not a policy denial that stops it.
- Claude Code's proposed all-empty reproduction: **adopted**, and added to the test before the patch.
- The review-packet change: **Claude Code's candidate** (an empty jobs list), chosen by the student.
- The boards: **Anthropic and Databricks (Greenhouse) and Linear (Ashby)**, plus the made-up Greenhouse name as the failure control, chosen from the nine boards and the 404 behavior Claude Code's probe reported.

## The student's own runs

Each was pasted from the student's Terminal and committed with the prompt and login line removed for privacy:
- `2026-11-08-normal-1`, the first finished run. The student typed their own approval ([output](evidence/terminal/2026-11-08-normal-1-run-by-student.txt)).
- `2026-11-08-failure-2`, with the student's own before-and-after copy of the state and their `cmp` ([output](evidence/terminal/2026-11-08-failure-2-run-by-student.txt)).
- The review test before the patch ([output](evidence/test-runs/2026-11-08-05-student-red-review-test-v1.txt)) and on the patch ([output](evidence/test-runs/2026-11-09-07-student-review-tests-on-patch.txt)).

## Claude Code's work, by named action

Claude Code ran as the desktop app, model Claude Opus 5.5 (`claude-opus-5-5`), on 2026-11-08 and 2026-11-09.

- **Probed** 12 board URLs before GATE.md existed, then timed the full downloads ([evidence/probes/](evidence/probes/)).
- **Wrote question sheets** for the student, with no answers ([evidence/sheets-given-to-the-student/](evidence/sheets-given-to-the-student/README.md)).
- **Copied** 12 files unchanged from JS1 (`d133453`). In JS1, Claude Code wrote the code and tests and the student wrote the persona's preferences (CONTRACT.md).
- **Wrote the tests from GATE.md** before any agent code (RED `7db4ab4`), including the student's 21 cases and the wrong versions as code. **Wrote the agent** (GREEN `208d1e3`).
- **Found and fixed, test-first,** three defects in its own work: the request deadline could be overrun (`431ac57` then `5d8bc8c`); `trace.md` misplaced the exit status (`8020acb`); the CLI checked one path without the policy (`c17621e`). Twice its first test was too weak and was strengthened, and the record keeps both versions.
- **Ran** the first live run, `2026-11-08-failure-1`, and every seeded demonstration.
- **Wrote** the independent check (`checks/independent_check.py`, which does not import the agent), `jobwatch verify`, and the boundary table script.
- **Wrote** the plan and the patch in the review packet (`231c4cf`, `4e39762`), and ran no test on the patch before the student's review.
- **Drafted** README.md, POLICY.md, this file, review-packet/README.md, the timeline in FRICTIONAL.md, and the sign-off draft.

## Facts from elsewhere

- **The endpoints**, and the observation that a wrong board name can look like an empty board, come from **Lectern's `ATS.md`**, the instructor's collector in this repository (`fall-2026/nik-bear-brown/lectern/`), probed there on 2026-09-26. Claude Code's own probe on 2026-11-08 found Greenhouse `hubspot` returning 404, no longer an empty board.
- **The Greenhouse and Ashby API documentation** links are in the student's GATE.md.
- **Chapters 4–6** of this course shaped the gate, the boundary matrix and the review packet.

## Other students' work

Two other students' JS2 folders are in this repository's main branch, so they are in this checkout too. **Claude Code did not open any file in them.** On 2026-11-08, while looking for the student's misplaced test file with `find`, Claude Code saw that `fall-2026/rayudu-h/js2-loop-tools-diff/tests/test_review_empty_board.py` exists. That student committed it on 2026-10-31 (`998e487`), for the same empty-board example from the brief. The name `test_review_empty_board.py` in this folder came from Claude Code's own review-gate sheet (2026-11-08 05:48), written before Claude Code knew the other file existed ([the sheet](evidence/sheets-given-to-the-student/README.md)). The student was told not to open the other folder.
