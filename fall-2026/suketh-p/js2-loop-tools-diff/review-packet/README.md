# Review packet: an empty board must not count as checked

Claude Code drafted this page from the commits and files it links. Every judgment in it is quoted from the student's files. The chain runs in the order it happened; each link names the commit that shows it. Times are EST.

**The change:** a board that answers HTTP 200 with an empty jobs list. Before the patch, the loop called it `usable` with 0 postings, so a run could end `finished` and save an empty snapshot as history. That is GATE.md's first wrong version, and the brief's own example.

## The chain

| # | Step | Who | When | Evidence |
|---|---|---|---|---|
| 1 | **Defect reproduced** (SEEDED). Replayed real bodies, with Linear's body CONSTRUCTED empty. The run ended `finished` and reported Linear "usable, 0 jobs, no new postings". The independent check flagged it | Claude Code ran it | 11-08 05:47 at `8020acb` | [demos/finished-wrong-answer/at-8020acb-before-fix/SUMMARY.md](../demos/finished-wrong-answer/at-8020acb-before-fix/SUMMARY.md) |
| 2 | **Review gate:** the rule, two reproductions plus a comparison case, the allowed scope (only `classify_response` in `jobwatch/loop.py`; the parsers keep accepting an empty array), and the wrong-patch sentence, dated | The student (who states they wrote it) | saved 06:23, committed `64357fe` | [REVIEW-GATE.md](REVIEW-GATE.md) |
| 3 | **Claude's proposal:** add a third reproduction, all three boards empty, ending `error` | Claude proposed; the student chose "Adopt it" | 11-08 ~06:52 | the commit message of `a61f07e` |
| 4 | **The student's test, version 1:** an empty Greenhouse board on a first run, an empty Ashby board after a baseline, and the comparison case. **RED** in the student's own run: 2 FAIL (`'usable' != 'unverified'`), comparison ok | The student wrote and ran it | saved 07:16, committed `2eb4a5f` | [tests/test_review_empty_board.py](../tests/test_review_empty_board.py), [their run](../evidence/test-runs/2026-11-08-05-student-red-review-test-v1.txt) |
| 5 | **Version 2** adds the all-empty case. **RED:** 3 FAIL, comparison ok. The student reported verifying it "on a local copy"; that output was not shared | The student wrote it; Claude Code ran it | saved 07:26, committed `a61f07e` | [Claude's run](../evidence/test-runs/2026-11-08-06-claude-red-review-test-v2.txt) |
| 6 | **Plan, before any edit:** one edit in `classify_response`, with what stays unchanged and why, and what the plan misses | Claude Code | `231c4cf`, 07:30 | [PLAN.md](PLAN.md) |
| 7 | **The request:** "Please make the change only in classify_response in jobwatch/loop.py. […]" | The student, in chat | 11-09 ~00:09, `4dccaee` | [REQUEST.md](REQUEST.md) |
| 8 | **The patch:** 2 added lines, 1 file. Claude Code ran no test on it before the student's review | Claude Code | `4e39762`, 00:10 | [PATCH-4e39762.diff](PATCH-4e39762.diff) |
| 9 | **Audit record:** verdict "Proceed to verification", target, mechanism, what would change the student's view | The student | saved 00:36:08, **18 s after** step 10 started | [AUDIT-RECORD.md](AUDIT-RECORD.md) |
| 10 | **The student's checks:** `python3 -m unittest -v tests.test_review_empty_board` on `4e39762`, 4/4 OK. The full-suite command ran in the same line, but its output is not in the paste | The student, in their Terminal | started 00:35:50 | [their run](../evidence/test-runs/2026-11-09-07-student-review-tests-on-patch.txt) |
| 11 | **Decision: accept `4e39762`**, "for the empty-board fix", resting on the four focused tests | The student | saved 00:37:32, committed `82739cd` | [DECISION.md](DECISION.md) |
| 12 | **After the decision:** full suite on `4e39762`, `python3 -W error -m unittest -v`, 163 OK. The seeded demo rerun: the same empty Linear body now ends `incomplete`, Linear `unverified` with an unknown count, state not advanced, and the independent check passes | Claude Code | 00:41, `11bd1f6` | [full suite](../evidence/test-runs/2026-11-09-08-claude-full-suite-on-patch.txt), [after-fix demo](../demos/finished-wrong-answer/at-4e39762-after-fix/SUMMARY.md) |

## The four questions the brief asks

- **The diff, read as a change in behavior** (the student, DECISION.md): "A successfully parsed HTTP 200 response with an empty jobs list now leaves the board unverified, with its counts unknown and its raw response saved. The loop ends incomplete if another board is usable or in error if none are usable, and skips the state update in both cases."
- **Did the change stay in scope?** The student compared `4e39762` with its parent: "two added lines in `classify_response` in `jobwatch/loop.py`. That is the only function and file allowed by my review gate." `git diff --numstat 4e39762^ 4e39762` agrees: `2 0 …/jobwatch/loop.py`.
- **The commands the student ran:** the test run in step 4 (version 1, RED) and step 10 (the patch, 4/4 OK), in their own Terminal, pasted in chat.
- **One case the test would still miss** (the student): "A board could return a valid but partial list, such as one posting from a board that usually has hundreds. The response would still count as usable." PLAN.md named the same gap before the patch.

## What the record does not show

- **That the audit came before the checks.** Chapter 6 asks for the audit record to be written before any check runs. The student's test command started at 00:35:50, and the audit file was saved at 00:36:08. The student's first chat line said the file was saved "before running any tests on the patch". Their DECISION.md corrects that: "The Terminal command is dated 00:35:50 EST. The audit copy was saved at 00:36:08 EST, 18 seconds after that command started." The audit may have been drafted earlier, but the record cannot show it.
- **The student's own full-suite result on the patch.** It was not in the paste. Claude Code's full-suite run (step 12) came after the decision, not before it.
- **Any rejection or change of a Claude proposal inside this packet.** The student adopted the one case Claude Code proposed. The scope, `classify_response` only with the parsers left alone, is the student's own choice among the four places Claude Code's sheet listed (`board.py`, `ats.py`, `loop.py`, `tests/test_inputs.py`).

## The driver's seat, for this review

| Task | Claude Code did | The student did | Why it stays the student's |
|---|---|---|---|
| The rule and the reproductions | Listed where the behavior lived; reproduced the defect in a seeded run; proposed the all-empty case | Wrote the rule, the two reproductions, the comparison case and the wrong-patch sentence; adopted the all-empty case | The requirement is the student's: Claude could implement a wrong rule perfectly |
| The regression test | Pointed to helpers and a model test; copied the file into place; ran version 2 | Wrote both versions before the patch; ran version 1 | A test written after the patch tends to bless it |
| The scope | Kept the plan and the patch inside the allowed list | Chose `classify_response` only; checked the plan and then the diff against it | The student owns what this change is for |
| The patch | Wrote it; ran no test on it before the review | Asked for it in their own words | — |
| Checks and decision | Ran the full suite and the demo after the decision | Ran the focused tests; decided accept, with the verb "show" | Their name is on the decision |
