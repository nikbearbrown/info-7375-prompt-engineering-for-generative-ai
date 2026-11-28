# The student's own checks

The files here are output from commands the student ran in their own terminal, pasted into the chat and saved as pasted at the student's request. Claude Code added only this note.

| File | What the student ran | What Claude Code compared it with |
| --- | --- | --- |
| [2026-11-28-hand-check-as-pasted.txt](2026-11-28-hand-check-as-pasted.txt) | From the JS4 folder: `shasum -a 256` on `replay/state/state.json` and `replay/premortem/state.json`; then `python3 -I checks/independent_check.py replay/runs/SEEDED-2-2026-11-24 --earlier runs/2026-11-08-normal-1`. Pasted in the chat by 08:58 EST on 2026-11-28. | Both SHA-256 values equal the files committed at `17a5a2ca`. They also match the receipts in [SEEDED-2's publish.json](../../replay/runs/SEEDED-2-2026-11-24/publish.json) (`dc40d7b9…`) and [the premortem resume record](../../replay/premortem/resume-PREMORTEM-databricks-2.json) (`96016689…`). The checker's PASS and its counts match the replay's own Step 5 check. |

`shasum` is a standard macOS tool, outside this project's code. It confirms the bytes, not what they say. `checks/independent_check.py` parses the raw bodies with its own code, but Claude Code wrote it. Which of these counts as independent is the student's call.
