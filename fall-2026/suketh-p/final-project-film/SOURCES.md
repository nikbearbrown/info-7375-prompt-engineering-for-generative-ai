# SOURCES — Fine Print (pitch film)

What I used, what I made, what Claude Code contributed, and every third-party asset with its licence.

## 1. What the film is built from

| Source | What it gave the film | Where |
|---|---|---|
| My Assignment 3 repository: `sukethrp/the-reallocation-engine`, branch `contrib/2026fa-sukethrp-ml-newgrad-sponsor-match`, commit `95d4982` (a fork of `nikbearbrown/the-reallocation-engine`, MIT licence) | The recipe and prototype; the 36 tests; the eight-posting review (`POSTING-REVIEW.md`); defect D9 (`PROPOSED-ADDITIONS.md`); my 2026-10-02 decisions and reflection | B00, B01, B07, B08, B13; FACTCHECK rows 6–16, 23, 25 |
| [PR #12](https://github.com/nikbearbrown/the-reallocation-engine/pull/12) to the course engine | "an open pull request" | B13 |
| [github.com/sukethrp/agentos](https://github.com/sukethrp/agentos) (my project, Apache-2.0): its README and its CI run of 2026-09-19 | Evidence for "budget limits and a kill switch" | B12; FACTCHECK row 29 |
| The assignment text (Canvas, "Final Project Pitch Film") and the course's final-project spec (`assignments/assignment-final-project.md`, upstream, posted 2026-10-11) | The seven questions; the requirement that the final project be agentic | the whole film |
| My own answers (FRICTIONAL.md, entry 1) | Why this project, my skills, the alternatives, the background rule, the risk I expected | B02, B04, B05, B12 |
| My LinkedIn check of two graduate ML postings, 2026-10-14 (Qualcomm; TikTok), `evidence/linkedin-check-2026-10-14.md` | The alternative compared in B08, in my wording | B08; FACTCHECK rows 24–25 |
| My review of the script and the first render (FRICTIONAL.md, entries 2–3) | Four beat changes: B01, B07, B08, B09 | those beats |

**Evidence files made for this film** (all in `evidence/`, each says who ran it and when):
`a3-tests-rerun-2026-10-13.txt` (36 tests OK, fresh clone), `a3-pr12-state-2026-10-13.txt`,
`toolkit-setup-2026-10-13.txt`, `whisper-check-v1*.txt` (pronunciation check of the narration).

**Privacy.** My résumé was shared with Claude Code only to check the claims in B05 and B12; nothing from it is in this
folder or the film except the two durations I stated myself ("about two and a half years at Amazon and six months at
Vertex"). No contacts, application tracker or conversation transcript is included. No real posting text is copied
here: the only posting sentence shown ("5 yrs preferred", B04) is a constructed example and says so on screen.

## 2. Third-party tools and assets

| Asset | Used for | Licence |
|---|---|---|
| **brutalist.art** toolkit, `github.com/nikbearbrown/brutalist.art` at `519fcbb` (fresh clone 2026-10-13) | The `show-tell` skill, its pipeline, gates and compiler; `iso_kit.py`; the 25 original isometric props (`templates/iso_originals_25.py`, "25 original procedural illustrations, created 2026-10-01" per `icons/show-tell-originals/README.md`); the Remotion opening `BrutalistHesitantWriter` (no banner, no handle). *Not used:* `ClaudeTitleOutro` (hard-codes the handle `@NikBearBrown`), `ClaudeDefinitions` (failed GATE T at 40 px) | The repository has no licence file at this commit; used as the course's assigned toolkit. The Isocons-derived prop packs in the toolkit were **not** used |
| Manim Community v0.20.1 | Rendering the drawn beats | MIT |
| Remotion 4 | Rendering the opening hesitant-writer beat | Remotion licence (free for individuals) |
| Kokoro-82M (via `kokoro-onnx` 0.6.1), voice `am_eric` | The narration, synthesized locally from my script; my name is spoken from phonemes that kokoro-onnx's espeak Hindi phonemizer made from my Devanagari guide (`name_voice.py`) | Kokoro-82M: Apache-2.0; kokoro-onnx: MIT |
| faster-whisper 1.2.1 with Whisper `small.en` | Checking the narration's pronunciation only (nothing in the film) | MIT |
| EB Garamond (all on-screen type) | Type | SIL Open Font License 1.1 (`brutalist.art/runtime/fonts/*/OFL.txt`) |
| FFmpeg 8.1 | Audio padding, measuring, encoding | LGPL/GPL |

No stock footage, music, screenshots, or AI-generated images or video are used. No Claude response appears in the film.

## 3. What Claude Code contributed

Claude Code (Claude Opus, in the Claude desktop app), 2026-10-13 and 2026-10-14:

- **Research:** read the assignment, the course's final-project and Update 1 specs, the instructor's example folder and the
  classmates' pitch folders already posted upstream; re-read my A3 record; checked AgentOS's README and CI.
- **Checks it ran on my machine:** the A3 test re-run from a fresh clone; the PR #12 state; the toolkit install and its
  readiness checks; the Whisper pronunciation check; Gate A pre-audits; every toolkit gate in `gate-reports/`.
- **Files it wrote:** the drafts of `PROJECT-BRIEF.md` and the script; `make_sheet.py`, `build_audio.sh`,
  `finish_audio.py`, `make_srt.py`, `name_voice.py`, `scenes_body.py`, `build_scenes.py` (which assembles `scenes.py` from the toolkit's kit
  and props plus `scenes_body.py`); `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`, `BUILD-PROMPT.md`, `README.md`, this file; the
  factual timeline and the "added by Claude Code" notes in `FRICTIONAL.md`.
- **Errors it caught in its own drafts:** listed in FRICTIONAL.md (timeline) and FACTCHECK.md (CORRECTED rows).

## 4. What I did

- Chose the project, the target role, the voice, the title, and to say on screen that I am on F-1.
- Wrote my Frictional entries and the answers that §7 and §2 of the brief are built from.
- Changed the design: an experience requirement must be compared with the applicant's documented background (entry 1,
  point 4), and the interpretation error had to be shown on screen (entry 1, point 5; beat B04).
- Reviewed the script and the film (FRICTIONAL.md entries 2–4) and changed four beats: the fictional applicant in B01, approval
  as a separate field from the model's source label in B07, my LinkedIn comparison in B08, the recorded-outputs demo in B09.
- Checked two graduate ML postings on LinkedIn myself (`evidence/linkedin-check-2026-10-14.md`).
- Gave my name's pronunciation in Devanagari and approved the voiced result by ear.
