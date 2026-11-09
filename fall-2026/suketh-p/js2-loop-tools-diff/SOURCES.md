# SOURCES: who wrote what, and where facts came from

Claude Code drafted this file from the commit record and the student's answers. The student's statements about authorship are quoted as the student gave them. Claude Code cannot see how a file was drafted before it arrived, only when it arrived and what it said.

The student's answers were given in chat, mostly as choices among options Claude Code wrote. The brief keeps conversation transcripts on the student's machine ("Privacy and boundaries"), so this file quotes only the short answers, and **they cannot be checked from this repository.**

## The student's files, and the Claude Code drafts each one builds on

| File | Written by | Claude Code drafts it builds on | Record |
|---|---|---|---|
| [GATE.md](GATE.md) | The student. Asked whether they wrote it or an AI tool helped, they answered "I wrote it myself" (2026-11-08) | The GATE worksheet: the brief's questions, the probe's board facts, "cases to decide" posed as questions | Committed byte-for-byte before any new code, `b55d2a5` |
| Predictions in [policy/BOUNDARY-PREDICTIONS.md](policy/BOUNDARY-PREDICTIONS.md) | The student, pasted in chat | **The 21 cases are Claude Code's list**; the predictions are the student's | `f871ccb`, before any policy code |
| [review-packet/REVIEW-GATE.md](review-packet/REVIEW-GATE.md) | The student, who answered "I wrote both myself" (this file and Frictional entry 2) | The review-gate sheet: the candidate change and its rule, `classify_response` among four places, example reproductions, the file name | `64357fe`, before any test or patch |
| [tests/test_review_empty_board.py](tests/test_review_empty_board.py) | The student, who answered "I wrote it myself" | Claude Code's test helpers (`tests/test_loop.py` `LoopCase`, `tests/fakes.py`) and the two model tests it pointed to; the all-empty case, Claude Code's proposal, which the student adopted | v1 `2eb4a5f`, v2 `a61f07e`, both before the patch |
| [review-packet/REQUEST.md](review-packet/REQUEST.md) | The student's chat message, verbatim | Claude Code's plan, which the student checked against their scope | `4dccaee` |
| [review-packet/AUDIT-RECORD.md](review-packet/AUDIT-RECORD.md), [review-packet/DECISION.md](review-packet/DECISION.md) | The student. Asked who wrote them, they answered "I wrote both myself" (2026-11-09) | Claude Code's two templates (Chapter 6's audit record; the decision questions with the verb ladder). The decision's missed case is the gap PLAN.md named | `82739cd` |
| The student's entries in [FRICTIONAL.md](FRICTIONAL.md) | The student (see the next paragraph) | The final retrospective answers the four questions on Claude Code's FINAL-STEPS sheet | Verbatim, under headings Claude Code added |
| The sign-off in [README.md](README.md) (withheld) | The student | Claude Code's list of facts, which the sign-off's items match | `dfe7203` |

**Correction at sign-off, 2026-11-09.** The student's sign-off says the review tests were "prepared before the patch with drafting help", and the student asked for "the authorship correction" to be carried into this file. Asked which drafting help they meant, the student answered: "Claude's drafts only". So "Written by: the student" in the table means written by the student, with the Claude Code drafts named in the same row. Per the student, no other tool or person helped. The student's earlier answers are kept as given.

On 2026-11-08 Claude Code asked once more. The question named the folder outside this repository that the student's files had come from, and the student's remark that the new test was "verified on a local copy". It said that using an AI tool is allowed when it's disclosed, and asked whether SOURCES.md was accurate in saying the student wrote GATE.md, REVIEW-GATE.md, the test and the Frictional entries themselves. The student answered: "Yes, all written by me".

## What the sheets suggested

[evidence/sheets-given-to-the-student/](evidence/sheets-given-to-the-student/README.md) holds every sheet, byte-for-byte. They carried questions and facts, and in places a suggestion that later appears in the student's work:

- **The GATE worksheet** raised "cases to decide" as questions: a board listed twice, a URL asked for again after a failure, some boards working while one fails. The student's repeat rule and exits answer those cases.
- **The review-gate sheet** offered one candidate change, with its rule in the heading: "an empty jobs list must leave the board unverified, not count as 'checked, 0 new'". It listed `classify_response` among the four places the behavior lived, and gave example reproductions: "an empty Greenhouse board and an empty Ashby board, or a first run and a later run". The student's two reproductions combine those examples (an empty Greenhouse board on a first run; an empty Ashby board after a baseline). The comparison case and the wrong-patch sentence are not in the sheet.
- **It also suggested the file name** `tests/test_review_empty_board.py`; see "Other students' work".
- **Claude Code's PLAN.md** (`231c4cf`, before the patch) named the gap "a board that answers 200 with far fewer postings than before (say 1 instead of 675) still counts as usable". The student's "one case my test would still miss" in DECISION.md is the same case.

## The student's choices among options Claude Code laid out

- **Two exits.** An approval naming another run or file: **incomplete**, not error. A redirect from a configured board: **the board is unverified and the run keeps going**, not a policy denial that stops it. Each was two options with no recommendation.
- **The all-empty reproduction,** Claude Code's proposal: **adopted** and added to the test before the patch. It was offered as adopt or leave out, with no recommendation.
- **The review-packet change.** Claude Code offered **one candidate, with its reasons**, and said the student could name another. The student chose it.
- **The boards.** Anthropic and Databricks (Greenhouse) and Linear (Ashby), plus the made-up Greenhouse name as the failure control. They were chosen from the nine boards and the 404 behavior Claude Code's probe reported, with no recommendation.

## The student's own runs

Each was pasted from the student's Terminal and committed with the prompt and login line removed for privacy:
- `2026-11-08-normal-1`, the first finished run. The student typed their own approval ([output](evidence/terminal/2026-11-08-normal-1-run-by-student.txt)).
- `2026-11-08-failure-2`, with the student's own before-and-after copy of the state and their `cmp` ([output](evidence/terminal/2026-11-08-failure-2-run-by-student.txt)).
- The review test:
  - two attempts while the file was still outside this folder ([output](evidence/test-runs/2026-11-08-04x-student-review-test-not-found.txt))
  - v1 before the patch ([output](evidence/test-runs/2026-11-08-05-student-red-review-test-v1.txt))
  - the four tests on the patch ([output](evidence/test-runs/2026-11-09-07-student-review-tests-on-patch.txt))

## Claude Code's work, by named action

Claude Code ran as the desktop app, model Claude Opus 5.5 (`claude-opus-5-5`), on 2026-11-08 and 2026-11-09.

- **Probed** 12 board URLs before GATE.md existed, then timed the full downloads ([evidence/probes/](evidence/probes/)).
- **Wrote the question sheets** described above.
- **Copied** 12 files unchanged from JS1 (`d133453`). In JS1:
  - the student wrote CONTRACT.md: the persona, the screening rule JS2 reuses, the refusals and the wrong versions
  - the student wrote one of JS1's 93 tests (`tests/test_my_cases.py`, not carried)
  - Claude Code wrote JS1's code and its other 92 tests; the 30 carried here are among them
- **Wrote the tests from GATE.md** before any new agent code (RED `7db4ab4`): the 21 boundary cases (Claude Code's list, with the student's predictions as the expected results) and the wrong versions as code. The six JS1 modules copied in `d133453` already existed. The commit message of `7db4ab4` calls them "the student's 21 boundary cases"; the cases are Claude Code's list. **Wrote the agent** (GREEN `208d1e3`).
- **Found and fixed, test-first, three defects** in its own work:
  - the request deadline could be overrun (`431ac57`, then `5d8bc8c`)
  - `trace.md` misplaced the exit status (`8020acb`)
  - the CLI checked one path without the policy (`c17621e`)

  Twice its first test was too weak and was strengthened. For the socket deadline, both runs are kept: 03a passed on the old code and 03b failed as it should. For the CLI check, only the commit message of `c17621e` records it.
- **Ran** the first live run, `2026-11-08-failure-1`, and every seeded demonstration.
- **Wrote** the independent check (`checks/independent_check.py`, which does not import the agent), `jobwatch verify`, and the boundary table script.
- **Wrote the plan and the patch** in the review packet (`231c4cf`, `4e39762`), and ran no test on the patch before the student's review.
- **Drafted** README.md, POLICY.md, this file, review-packet/README.md, the timeline in FRICTIONAL.md, and the list of facts for the sign-off. The sign-off itself is the student's to write.

## Facts from elsewhere

- **The endpoints,** and the observation that a wrong board name can look like an empty board, come from **Lectern's `ATS.md`**, the instructor's collector in this repository (`fall-2026/nik-bear-brown/lectern/`), probed there on 2026-09-26. Claude Code's own probe on 2026-11-08 found Greenhouse `hubspot` returning 404, no longer an empty board.
- **The Greenhouse and Ashby API documentation** links are in the student's GATE.md.
- **Chapters 4–6** of this course shaped the gate, the boundary matrix and the review packet.

## Other students' work

Two other students' JS2 folders are in this repository's main branch, so they are in this checkout too. **Claude Code did not open any file in them.** On 2026-11-08, while looking for the student's misplaced test file with `find`, Claude Code saw that `fall-2026/rayudu-h/js2-loop-tools-diff/tests/test_review_empty_board.py` exists. `git log` (read without opening the file) shows that student committed it on 2026-10-31 (`998e487`), with the message "JS2 review packet — failing test for the empty-board defect, before any patch". The name `test_review_empty_board.py` in this folder came from Claude Code's own review-gate sheet (2026-11-08 05:48), written before Claude Code knew the other file existed. The student was told not to open the other folder.
