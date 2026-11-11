# My gate answers — 2026-11-10 (verbatim, before any JS2 code existed)

Given in chat to Claude Code on 2026-11-10, answering `notes/GATE-QUESTIONS.md` (written by Claude on 2026-11-05).
Claude turned these into `GATE.md`; every change it made is listed at the end of GATE.md.

**My reply:** "All ★ except 4b". Then, for 4b: **"A + B + C"**.

| # | Decision | My answer (the ★ option, accepted) |
|---|---|---|
| 0 | Language | Python, standard library only. The course CI rejects .js files, and all 15 of your JS1 files are already on its failure list. |
| 1a | One board fails, the others work | Run ends finished, with that board marked error in the report |
| 1b | Is finished "success"? | No. Whether the answers are right is a separate check |
| 2a | Caps per run | 5 boards · 10 requests · 60 s total · 10 s per request |
| 2b | Who may change the caps? | Only you, by a dated line in GATE.md; a test fails if the code's config differs |
| 3a | What counts as "the same action"? | Same ATS + same board slug (ignoring case and URL-encoding) |
| 3b | What happens on a repeat? | Skip it and log skipped: repeat |
| 4a | A board fails | Retry once, only for a timeout or a server (5xx) error. Never retry a 404 or a garbled response. Then mark the board error, leave its saved state untouched, and move on. |
| 4b | Escalation | **A + B + C**: the report's top line says "needs Mayank" for every error or suspect board, and the agent never fixes a slug itself (A); a non-zero exit code (3) when any board needs me (B); an error/suspect board's seen-ids are held, even with --approve-state, until I acknowledge it with --ack <board> (C) |
| 4c | Never | Report a failed board as "0 jobs" or "no new jobs" |
| 5a | Independent check for the empty-HubSpot run | A separate checker that reads only the saved raw responses, plus an expected-boards.json floor you write. Also flag any board that drops by more than 80%. |
| 5b | Who sets the floors? | You, each with a named source; "unknown" if there isn't one |
| 6a | Allowed hosts | boards-api.greenhouse.io and api.ashbyhq.com only, HTTPS, no redirects. Claude judge: out. |
| 6b | Folders | Free writes to runs/<this-run>/ only. Writing state/seen-ids.json needs your approval. Everything else is off-limits. |
| 6c | How you approve | --approve-state <exact run id>; "yes" or "1" doesn't count |
| 6d | Never-do list | Apply, email, message, log in, submit forms, any request other than GET, credentials, redirects |
| 7 | Wrong versions the tests must catch | All 8: prefix trick, symlink escape, "truthy" approval, empty board = fine, failure reported as zero, stopped = success, repeat counted as progress, host check by substring |
| 9 | Review-packet defect | JS1's safeWrite follows symlinks out of its folder |

**My failure sentence (2026-11-10):** "If my loop were wrong, I would see a board reported as 'no new jobs' while its saved raw response is empty or an error."

**My own wrong version (W9):** "When a board fails, its seen-ids are saved as empty, so the next run reports every job as "new"." (It tests my 4a rule "leave its saved state untouched".)
