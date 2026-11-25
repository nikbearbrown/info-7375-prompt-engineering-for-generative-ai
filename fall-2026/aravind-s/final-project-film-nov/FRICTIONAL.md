# FRICTIONAL: Final Project Film (Klaxon, November 2026)

INFO 7375, Canvas assignment 3551817 ("Final Project Film", Brown's brief of 2026-11-18), due Mon 2026-11-23,
11:30 PM ET. Folder: `fall-2026/aravind-s/final-project-film-nov/`. The folder's final commit is named in the Canvas
comment and the pull request (a file cannot name the commit that holds it).

## Claude Code's part (written by Claude Code, from the session record)

- 2026-11-20: read Brown's brief on Canvas; researched prior work (every source in SOURCES.md, read that day).
- Drafted SCRIPT.md (21 beats in Brown's four parts) from Klaxon's own records at `fef450b`.
- FACTCHECK.md: 66 claims checked against those records and the web pages; 6 corrected before any render (for
  example, "customers' money is still wrong" became "the books are still wrong", since the provider charged once).
- Captured the footage: Klaxon's web panel served from a scratch copy of `fef450b` (it only reads saved runs), the
  five screenshots the panel saved during the week 7 live run, real output of `make eval-cases`, and two public
  GitHub pages, signed out. No Docker and no model calls.
- Built the review cut (narration: Kokoro, am_onyx; soft captions), then checked frames from every beat and fixed
  what was misaligned, clipped or too small (list in SHOTLIST.md, under "Review cut (2026-11-20)").
- Aravind's answers on 2026-11-20: the film's form (real footage, a few title cards and a disclosed synthetic voice);
  B15 changed to say Claude Code wrote the code under his direction; the held-out fault stays a stated limit; the
  film is posted in the course repo with his own FRICTIONAL entries.
- Other changes on 2026-11-20: B01 "my script" became "the script" (Claude Code drafted it); OpenHands stays out of
  this film, as his week 8 plan (`9cfc249`) keeps its non-Claude runs out of INFO 7375's materials; the panel's
  "Signals at the alert" card from the same run stands in for the optional Grafana shot; week 8 is said as
  "planned", since it is not merged on `main`.
- 2026-11-21: checked Klaxon's `main` on GitHub again: still `fef450b`, week 8 not merged, so B13 keeps "planned" and
  nothing was re-rendered. Made `tts.py` read the voice model folder from `KOKORO_MODELS` and wrote the Pythons the
  build uses as environment variables in build/BUILD-NOTES.md, so no build file names a folder on this Mac. Changed
  one line of `stage.py` that only parsed on Python 3.12 (this repo's CI also parses with 3.11). Checked every file
  here for the user name, full home-folder paths, emails and tokens, and read the text of every committed screenshot
  with OCR: none found.
  Rebuilt the film from a copy of this folder: the same file, byte for byte. Built this folder and the Canvas zip;
  nothing pushed.
- 2026-11-22: Aravind approved the review cut with no changes. Rendered the final under its own name, with the title
  tag "Klaxon: Final Project Film" (the review cut's ended "(review cut)"): its video, audio and caption streams
  are the same as the cut he approved, so only the file's SHA-256 changed (README.md). Marked SCRIPT.md,
  FACTCHECK.md, SOURCES.md and BUILD-NOTES.md final, and fixed two stale lines in SHOTLIST.md ("nothing captured
  yet", and the postmortem screenshot's size, 1440 x 6000). Rebuilt the film from a copy of this folder: the same
  file, byte for byte. At his request, organized his rough notes into the author entries below and added
  their evidence lines; his notes, word for word, are kept outside the repo. Nothing pushed.

## Traceability

| What | Where | Built from |
|---|---|---|
| The film | `klaxon-final-project-film.mp4` | The final render of 2026-11-22: the same streams as the cut of 2026-11-20 that Aravind approved (its SHA-256 is in README.md), from Klaxon's records at `fef450b` |
| Script, claims and their sources | `SCRIPT.md`, `FACTCHECK.md`, `SOURCES.md` | Klaxon's records at `fef450b` and web pages read on 2026-11-20 |
| How each shot was made | `SHOTLIST.md`, `build/` | The steps in `build/BUILD-NOTES.md`; the film rebuilds byte for byte from this folder |

## Author's entries (Aravind's notes, organized by Claude Code at his request)

Aravind wrote rough notes for each question on 2026-11-22, at about 1 AM ET. At his request, Claude Code organized
them, tightened the wording and added the times, beat numbers, quotes and Evidence lines from the record, as the
Frictional guide allows ("AI can organize your notes; you must supply the actual experience"). The experiences,
decisions and reasons are his. His notes, word for word, are kept outside the repo.

### Friday 11/20: the decisions (written Sunday 11/22, about 1 AM ET)

**What did you decide about the film (its form, its voice, what stays out), and why?**

- Form: real footage of Klaxon (its web panel, the screenshots it saved, real terminal output, GitHub), a few title
  cards, and a synthetic voice that the first line discloses. I wanted the film to show the actual project instead of
  only explaining it. My October pitch film used drawings, and they came out repetitive and misaligned.
- B15 (3:11): the draft said "Claude Code wrote most of the code under my direction". I answered "No, Claude Code
  wrote it", so the film now says Claude Code wrote the code under my direction. I wanted to be clear about that.
- The missing held-out fault stays a stated limit (B19, 3:58). I chose that over adding one to the plan before Dec 4.
- OpenHands stays out, because my week 8 plan keeps non-Claude runs out of INFO 7375.
- The film is posted in the course repo with this log, not only on Canvas.

**What did you expect the first cut to get wrong?**

I didn't expect anything major to go wrong. When Claude Code sent me the first cut (Friday 11/20, 6:17 AM), it asked
me to check that the voice said my name and the acronyms (SRE, AWS, API, MCP) correctly. Beyond that, I wanted the
film to be easy to follow and the technical parts to be clear.

**What, if anything, confused you in Brown's four-part brief?**

The four parts and their order were clear. I wasn't sure how much detail each part needed. I wanted Methods (1:46 to
3:20) to explain how Klaxon works and Evaluation (3:20 to 4:30) to show the actual results, without mixing the two.

Evidence: Aravind's answers of 2026-11-20 (README.md, "His decisions"); the four parts and their start times
(README.md, TIMINGS.md); FACTCHECK.md, the B15 and B19 rows; Klaxon's records at `fef450b` and its week 8 plan
`9cfc249`.

### Weekend: your review of the cut (written Sunday 11/22, about 1 AM ET)

**What did you watch or check yourself, and what did you find?**

Just after midnight on Sunday (about 12:25 AM), I opened the cut in a player Claude Code set up in the app's browser,
with captions on by default and buttons that jump to each part and to each spot where the voice says my name or an
acronym. I paid attention to the narration, the technical explanations and the overall flow. I found nothing I
wanted changed, and I accepted it at 12:30 AM. I didn't note which jump buttons I used, so I am not claiming
specific pronunciation checks.

**What did you accept, change or reject from Claude Code's script or cut, and why?**

- Accepted: the whole cut as Claude Code built it (script, footage, captions and its own fixes), with no changes,
  because I was satisfied with how the project and its results were presented.
- Changed: B15, from "most of the code" to "the code" (11/20), so the film describes my contribution accurately.
- Rejected: nothing in this cut.

**What surprised you?**

Nothing major. The cut presented the project clearly, and I was happy with how the real footage, the narration and
the explanations came together.

Evidence: Aravind's messages "show the film" (2026-11-22, 12:19 AM ET) and "No changes, finalize" (12:30 AM); the
final render keeps the review cut's video, audio and caption streams (SHA-256 in README.md); Claude Code's fixes in
SHOTLIST.md, under "Review cut (2026-11-20)".
