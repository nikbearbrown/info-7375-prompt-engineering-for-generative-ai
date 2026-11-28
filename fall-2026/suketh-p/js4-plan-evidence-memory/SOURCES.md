# SOURCES · Job-Search Agent 4

Claude Code drafted this file on 2026-11-28, and the student checks it.

## Course material

- **The brief:** `assignments/assignment-js4-the-plan-the-evidence-and-the-memory.md` in the course repository (last changed in `408a8fac`, 2026-10-11). The student also pasted the Canvas page on 2026-11-25. It has the same words and ends after the grading section.
- **Chapter 10:** `chapters/10-planning-before-acting.md`.
- **Chapter 11:** `chapters/11-tool-use-and-verification.md`.
- **Chapter 12:** `chapters/12-memory-and-multiple-agents.md`. Its gate section gave the memory gate's shape, and its premortem rows gave the premortem's.
- All three chapters are in the course repository at the commit this branch starts from, `2db0c546`.
- **The course AI policy and video,** linked from the brief.

## Code and data this builds on

- **JS3 at `ae850602`,** copied unchanged in `a470a831`.
- **The Nov 8 capture,** from JS2 at `9c1db18`, copied unchanged in `184081d0`.
- **The Nov 24 capture,** JS3's.
- **The public board APIs:** both captures came from the public Greenhouse and Ashby job-board APIs when JS2 and JS3 ran. JS4 sent no request.

## Who did what

| Part | Who |
| --- | --- |
| PLAN.md v0.1 and Frictional entry 1 | The student. On 2026-11-28 Claude Code asked whether anyone or anything helped draft v0.1; the student answered "Yes, done by me" |
| The PLAN worksheet: questions and facts, no answers | Claude Code, 2026-11-25. It is in the student's local notes, not in this folder |
| The 271 count, `evidence/2026-11-25-memory-vs-nov-24-lists.txt` | Claude Code. See the correction below |
| The review of v0.1 | Claude, model alias `sonnet`, in the student's own `claude -p` session. The record is in `evidence/plan-review/` |
| PLAN.md v0.2 and its approval | The student |
| PREMORTEM.md's prediction, MEMORY-GATE.md, and Frictional entries 2 and 3 | The student. Their question skeletons, the line labels the student reworded, were Claude Code's, built from the brief and Chapter 12 |
| Every state-write approval, and the line-5 decision | The student. Quoted in `replay/APPROVALS.md` |
| The hand check in `evidence/student-checks/` | The student |
| The JS4 code: `checks/independent_check.py`'s count-only and `--earlier` modes, `jobwatch/memory.py`, `jobwatch/watchers.py` and `jobwatch/replay.py` | Claude Code (Claude Opus 5.5), in the student's Claude Code session, 2026-11-25 to 2026-11-28 |
| JS4's tests, fixtures and run records | Claude Code, in the same session |
| The notes beside the student's text, the READMEs, EVIDENCE-MATRIX.md and this file | Claude Code, in the same session |
| The choices marked "Claude Code's choice" in the code, including the closure fixture's key | Claude Code. The student can override them |
| Which checks count as independent, the sign-off and the driver's seat | The student |

The approvals in the tests are simulated fixtures in temporary folders. Every write to `replay/` used the student's own approval.

The student's sign-off says: "I used drafting help for the plan, premortem, memory gate, and Frictional entries." The table above lists only the help on the record: Claude Code's PLAN worksheet and question skeletons. Whether the sign-off means that help or other help too is *waiting for the student's answer*.

## Corrections

- **Commit `2f4d80d8`'s timing.** Its message says the 271 count was made "before the student wrote PLAN.md v0.1". The record shows only two things: the count (14:49 UTC, 2026-11-25) came before Claude Code's worksheet reported it, and PLAN.md v0.1 cites it. When the student began writing is not on the record. Git history was not rewritten.
- **PREMORTEM.md's two commands.** Claude Code's record first showed the trigger and the resume as `python3 -m jobwatch.replay …`. They ran as `python3 -B -W error -m jobwatch.replay …`, and the record was corrected on 2026-11-28.
- **One test literal.** In `ae31e644`, one expected value in the resume test was corrected before the test passed. `evidence/test-runs/10-green-premortem-resume.txt` says so.
