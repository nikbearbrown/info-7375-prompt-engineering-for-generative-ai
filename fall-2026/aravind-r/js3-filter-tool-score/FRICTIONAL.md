# FRICTIONAL — Job-Search Agent 3

**Status: in progress (2026-11-25).** Aravind writes this log. Entries Claude Code typed from Aravind's
dictation are marked as dictated.

## 2026-11-25: manual Phase 3 replies saved under the wrong filenames (dictated by Aravind)

- **What happened.** I skipped a `pbcopy` step while pasting the manual claude.ai replies, so the
  clipboard still held the previous reply. The replies for **A005** and **A010** were first saved
  under the wrong filenames (`A010.txt` and `A014.txt`).
- **How I caught it.** I grepped the replies for `posting_id` and compared each one with its
  filename. I renamed the files; **no content was edited**. A014 was then run afterward in its own
  incognito chat.
- **What changed.** `tools/import-manual.mjs` now rejects any reply whose `posting_id` names a
  different posting than its filename (`checkReplyPosting` in `src/justify.mjs`). Nothing is written
  for that reply, and the exit code is 3 (`test/import-manual.test.mjs`).
- **Verified before import (Claude Code, read-only, 2026-11-25):** all 7 files now have a
  `posting_id` that matches their filename.
