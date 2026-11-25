# FRICTIONAL — Final Project Film

There are two parts, kept apart on purpose.

1. **The student's entries**, in their own words, placed verbatim with the date they were written. Claude Code never
   writes or edits these.
2. **Claude Code's timeline**: what Claude did, recommended or got wrong. Times come only from file times and the
   timestamps inside the captured logs. Rows marked "—" come from the chat and are listed in order, without a
   provable time.

---

## 1. The student's entries

### Entry 1 — during the build (received in chat, logged 2026-11-21 19:04 EST)

The questions asked were: why this direction (it started as Claude's recommendation), what changed since the October
pitch, and what the student expects to be hardest. When the entry arrived, the Nov 21 runs had been captured
(18:43–18:45), the draft script existed (18:47), and production had started (scenes and narration audio were being
built).

> I went with Fine Print because, as an F-1 student looking for new-grad ML roles, I want to know what a posting
> actually requires and what it says about sponsorship before I spend time tailoring an application. In October I
> planned to build the reader first, and now I can build it on top of jobwatch, which already monitors three job
> boards. I think the hardest part will be showing how the reader can quote a posting word for word and still get it
> wrong by treating “five years preferred” as a requirement.

### Entry 2 — after watching the draft film and setting the bar (received in chat, logged 2026-11-21 19:58 EST)

The question asked was: what the student noticed when watching the draft, and why the bar is set where it is.

> The empty “kept” tray stood out to me in the draft: jobwatch rejected all 172 postings on keywords alone, and I
> still couldn’t tell whether it had thrown out a role the applicant qualified for. I set the bar at zero false
> clearances because a wrong green light could cost me time tailoring an application for a role I don’t qualify
> for. I allowed one wrong rejection in the 30-posting test because I can review an isolated miss against the
> original posting, and a second would send me back to the filter.

---

## 2. Claude Code's timeline (2026-11-21, EST)

| Time | What happened | Record |
|---|---|---|
| 17:33 | The student asked for the folder "Final project Film"; Claude created it | folder time |
| — | The student asked whether Claude could see the October pitch film. Claude found it in `Assignment 4/final-project-film/` (PR #20, `8e244c3`) | chat |
| — | The student pasted the assignment and said: "This is the Assignment now you need to work on". Claude read the October film, JS1, JS2 and the course's Final Project brief | chat |
| — | The student asked: "Which will work best in this to make it impactful in class. To score the best marks". Claude recommended framing the film as "Fine Print, built on jobwatch". The student answered: "Yes, go with it" | chat |
| — | Claude laid out three ways to make the film and said it would use the mix (drawn scenes, plus terminal replays of real runs) unless the student objected. The student answered the next question, "Only Claude Code", and raised no objection | chat |
| — | Claude wrote `DESIGN.md`. A reviewer subagent read it and raised five questions | `DESIGN.md` §13 |
| 18:30 | The brief saved verbatim | `ASSIGNMENT-BRIEF.md` |
| 18:32–18:34 (the clock in the screenshots) | The student shared Canvas screenshots: the pitch film scored 49/50 ("nice work!!"); there is no Final Project Update 1 on Canvas; JS3 is due Nov 25 | chat |
| 18:42 | Design and plan last edited | `DESIGN.md`, `PLAN.md` |
| 18:43:06 | Fresh clone of JS2 at `9c1db18`: 164 tests OK | `evidence/terminal/tests-2026-11-21.*` |
| 18:43:15 | Live run without approval: 635 / 895 / 32 jobs, 83 / 88 / 1 new; `incomplete`; state unchanged (`cmp`) | `evidence/terminal/film-normal-noapproval-2026-11-21.*`, `evidence/state-*.json` |
| 18:43:27 | The independent check on that run: PASS | `evidence/terminal/film-normal-noapproval-check-2026-11-21.*` |
| 18:43:36 | Failure-control run: the 404 board failed as expected; `incomplete` | `evidence/terminal/film-failure-2026-11-21.*` |
| 18:45:12 | Rule records counted: 172 `not_relevant`, 0 `relevant` | `evidence/terminal/film-rule-*.json` |
| 18:47–18:49 | Draft script, beat sheet and fact-check table written | `SCRIPT.md`, `film/make_sheet.py`, `FACTCHECK.md` |
| 18:43–18:54 | A research subagent read six prior-work sources on their own pages | `evidence/prior-art/PRIOR-ART.md` (access times per entry) |
| — | The research changed the script. A 2025 paper already separates required from preferred, and Jobscan already has a review step before sending. B06 no longer claims either as new; it claims only the combination, and the exact sentence checked by code | `FACTCHECK.md` (rows B05–B06), `APPENDIX.md` §9 |
| — | With the student's agreement ("Sure proceed"), B07 and B16 now use the student's own words from Entry 1: what changed since October, and the predicted "five years preferred" failure | `film/make_sheet.py`, `FACTCHECK.md` |
| — | An independent fact-check subagent found 5 must-fix and 5 should-fix problems in Claude's draft script. All were judged genuine and fixed, except one already moot. Among them: the outro said "my script" although Claude drafted it; a picture showed sponsor records for all eight A3 postings although only four had one; "half of Fine Print runs" overstated the watcher. The script was also trimmed to leave room under 5:00 | `FACTCHECK.md` (last section) |
| 19:36 | First 4K master of the draft; the 1080p copy was made at 19:38 (SHA-256 `9f109205…`) and sent to the student | `film/exports/landscape/`, `submission/` |
| 19:51–19:57 | Pronunciation fix for "Jobscan", "Anthropic" and "either-or", checked with a Whisper transcript; B17 (the student's bar) voiced and rendered | `film/gate-reports/build-audio-4…5`, `whisper-check-pronunciation.txt` |
| — | A final-review subagent checked the rendered draft and the records: 12 findings. Among them, the unbuilt reader was drawn solid under `real` stamps (B07, B09); B16 showed a code check catching a failure that only the student's hand label can catch; the README still said "waiting for approval"; the captions drifted up to 0.45 s. All were fixed | this file, `README.md`, `SOURCES.md`, `film/make_srt.py` |
| 21:34–22:26 | The production subagent re-voiced B08 and re-rendered the scenes the review changed. Then it stopped: the student's 5-hour usage limit was hit | `film/gate-reports/build-audio-6…`, `art-run-6…7` |
| 22:55 | Claude resumed. Gate V had blocked one frame of B08: the terminal window's light title bar and shadow pulled the ink/background separation to 0.23 (floor 0.30). The window was redrawn (white title bar, ink outline); a 1080p test render measured 0.63 | `film/scenes_body.py` (`term_window`), `film/gate-reports/art-run-8-contrast.log` |

### What Claude got wrong, and how each was caught

- **"JS3 is due the same night."** Claude took Nov 23 from the course repo's JS3 file. The student's Canvas screenshot
  shows Nov 25, and Canvas governs. Corrected in `DESIGN.md` and in memory.
- **"jobwatch doesn't use a model yet."** That is true only of JS2, where the student's gate turned the model off. JS1's
  judge read 27 postings through the student's Claude Code login. Claude corrected it in chat.
- **The Update 1 question confused the student** ("Which one you are talking I didn't get what you are asking about?").
  Claude had found a promise of "Update 1" in October's Frictional log, but Canvas never posted that assignment.

### Recommendations the student accepted, and choices that were the student's

| Decision | Claude's part | The student's part |
|---|---|---|
| The film's framing | Recommended "Fine Print, built on jobwatch" when asked what would score best | "Yes, go with it" |
| How the film is made | Chose the mix (drawn scenes plus terminal replays of real runs) and said so | Raised no objection |
| Model access | Asked | "Only Claude Code" |
| Voice | Proposed keeping `am_eric` after the 49/50 grade | The October choice of `am_eric`; no objection now |
| Resolution | Rendered at 4K without asking. It is the toolkit's default and what October used, but the brief doesn't require it | "Who told you to do it 4k?", then "So cut it down to the normal 1080p". The submitted file is a 1080p copy of the checked 4K render |
| Draft film | Sent the 1080p draft (3:54) with what only the student can do: watch, read the script, write the bar, write Frictional entry 2 | "Approve it" (the bar and entry 2 came in the next messages) |
| Approval | Asked for approval of the design | "make it the best that will be outstanding, After everything you finished setting up let me know for approval" |
