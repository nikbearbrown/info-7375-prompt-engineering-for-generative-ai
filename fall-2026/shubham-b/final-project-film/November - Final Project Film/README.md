# A11yProof: final project film

| | |
|---|---|
| Student | Shubham Bagwe |
| Course | INFO 7375 · Prompt Engineering & AI (Northeastern) |
| Instructor | Prof. Nik Bear Brown |
| Working title | A11yProof: Accessibility Fixes With Proof |
| Runtime | about 4:39, 3840x2160, Kokoro voice `am_onyx` |

A11yProof is spoken as "A-eleven-Y Proof" in the film.

## What the film says, in one breath

Almost every home page has accessibility bugs, and the tools that exist either only list them or claim to fix them with a script that does not. A11yProof is a planned agent that scans a website for accessibility bugs, fixes the source code in a sandbox, re-scans to prove each fix worked, and opens a pull request only after a person approves the exact diff. The film covers why this matters, how it differs from prior work, the agent loop and its permissions, the data and plan, and how it would be tested, including planted failures and honest limits.

## Structure

Times measured from the narration audio of this master.

| Part | Beats | Time |
|---|---|---|
| Title card (topic, course, student, instructor) | B00 | 0:00-0:09 |
| 1. Executive summary (what and why, no how) | B01-B05 | 0:09-1:12 |
| 2. Introduction (prior art, then why mine) | B06-B07 | 1:12-1:49 |
| 3. Methods (loop, tools/permissions, human gate, data and budget, step plan) | B08-B12 | 1:49-3:12 |
| 4. Evaluation (measures, planted failures, controlled failure, limits) | B13-B15 | 3:12-4:06 |
| Recap, your turn, outro | B16-B18 | 4:06-4:39 |

## Read in this order

1. `README.md` (this file)
2. `PROJECT-BRIEF.md` - the project itself
3. `Bagwe_Shubham_INFO7375_A11yProof_FinalProjectFilm.mp4` - the film
4. `beat_sheet.json` - the script and scene plan, beat by beat
5. `SOURCES.md` - where each number in the film comes from
6. `FRICTIONAL.md` - what went wrong or got in the way during the build
7. `BUILD-PROMPT.md` - commands and prompts to rebuild the film
8. `gate-reports/` - frame check (GATE V), type check (GATE T), QC contact sheet, `verified.json`, run logs
9. `youtube/fixproof-pitch/` - the full reel folder (`build_sheet.py`, `tts.py`, `REVIEW.md`, `FACTCHECK.md`, ...). The folder keeps its old name because the toolkit uses it as the reel ID.

## How to rebuild the film

Short version: install the toolkit (brutalist.art, https://github.com/nikbearbrown/brutalist.art, cloned at `vendor/brutalist.art`), then from the reel folder run `python3 build_sheet.py`, `python3 tts.py .`, render the beats, and compile the 4K master. Exact commands, in order, are in `BUILD-PROMPT.md`.

## Changes since the October pitch

- The October pitch was a different project, a Marino desk RAG assistant. The final project switched to A11yProof. The two are kept separate.
- Renamed from FixProof to A11yProof on 2026-11-23, because the old name did not say the project was about accessibility. The title card narration explains that "a11y" is developer shorthand for accessibility. The reel folder and some file names still say `fixproof-pitch`.
- The toolkit hardcodes the handle `@NikBearBrown` on the table cards and the outro. At my request these now say "Shubham Bagwe" (the narration ends "By Shubham Bagwe"). This is a local edit to the toolkit copy (see `BUILD-PROMPT.md`) and departs from the toolkit's OUTRO-LOCK rule, so the professor may expect his handle there.

## Honesty notes

- The system is not built. Only the film exists. Targets in the film (for example 80% of held-out violations fixed, 0 new violations) are proposals, labeled as targets, not results.
- GATE T (type-size check, section 8.1) blocked `./art final`. It measures the height of short lowercase words, so making text bigger made its measured size smaller (40 to 37 px). I treated that as a false positive and compiled the master with the same `compile.py --height 2160` step `art final` uses. GATE V (frame check) passed with 0 blockers and 0 majors. This is a judgment call, recorded in REVIEW.md item 11.
- I watched the full film end to end with sound on 2026-11-23, including the narration of "A-eleven-Y Proof", "accessiBe", "WebAIM" and "WAVE", and checked every packet file.
- Other figures (WebAIM 95.9%, UsableNet 5,114 lawsuits, Deque 57%, FTC/accessiBe $1M, AccessGuru up to 84%) were checked by web search on 2026-11-23, some only through secondary coverage. Re-open the links in `SOURCES.md`.
- The video is built with Claude Code - Claude Opus 5.5 along with brutalist toolkit by Prof. Nik Bear Brown.
