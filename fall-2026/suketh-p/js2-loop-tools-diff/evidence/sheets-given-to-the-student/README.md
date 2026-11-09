# The sheets Claude Code gave the student

So a reader can see what help the student had for each part they own. Each file here is a `.txt` copy, byte-for-byte, of a sheet Claude Code wrote in the student's local `Assignment 7/` folder.

The sheets hold the brief's or a chapter's questions and the facts the student needed. **Two of them also hold suggestions that appear in the student's answers**, listed below the table. The times are the files' last-saved times (EST).

| Sheet | Last saved | What it held | The student's answer in this repo |
|---|---|---|---|
| `GATE-WORKSHEET.md.txt` | 2026-11-08 04:22 | The six GATE.md questions from the brief; board facts from Claude Code's probe; "cases to decide" posed as questions | [GATE.md](../../GATE.md) |
| `GATE.md.txt` | 2026-11-08 04:22 | A blank file with only the brief's six headings. The student wrote their GATE.md elsewhere and did not use this one | — |
| `BOUNDARY-PREDICTIONS.md.txt` | 2026-11-08 05:15 | The 21 cases with empty prediction columns. Written by Claude Code shortly after 05:00; last saved 05:15:14 with its content unchanged. The student answered in chat | [policy/BOUNDARY-PREDICTIONS.md](../../policy/BOUNDARY-PREDICTIONS.md) |
| `REVIEW-GATE.md.txt` | 2026-11-08 05:48 | Chapter 6's review-gate questions; one candidate change; the files where the behavior lived; example reproductions | [review-packet/REVIEW-GATE.md](../../review-packet/REVIEW-GATE.md) |
| `AUDIT-RECORD.md.txt` | 2026-11-09 00:10 | Chapter 6's audit-record template | [review-packet/AUDIT-RECORD.md](../../review-packet/AUDIT-RECORD.md) |
| `DECISION.md.txt` | 2026-11-09 00:10 | The brief's and Chapter 6's decision questions, with the chapter's verb ladder | [review-packet/DECISION.md](../../review-packet/DECISION.md) |

**Suggestions that later appear in the student's work:**

- **GATE worksheet.** Its "cases to decide" are questions, not answers: "some boards worked and one failed. Which exit is that?", "the same board listed twice; asking for the same URL again after it failed". The student's exits and repeat rule answer them.
- **Review-gate sheet, the change and its rule.** It offered one candidate change, with the rule in its heading: "an empty jobs list must leave the board unverified, not count as 'checked, 0 new'". The student chose that change.
- **Review-gate sheet, the scope.** It listed `classify_response` (`jobwatch/loop.py`) among four places the behavior lived. The student limited the patch to it.
- **Review-gate sheet, the reproductions.** It gave examples: "an empty Greenhouse board and an empty Ashby board, or a first run and a later run". The student's two reproductions combine them.
- **Review-gate sheet, the file name.** It suggested `tests/test_review_empty_board.py`. A file with the same name exists in another student's folder in this repository; see [SOURCES.md](../../SOURCES.md).

The comparison case, the wrong-patch sentence, the test's code, the audit and the decision are not in any sheet.
