# SOURCES — what was used, who did what, and licences

Drafted by Claude Code on 2026-11-21. The student's own words and choices are quoted. Everything Claude Code did is listed
as Claude's.

## 1. The student's own work and choices

| What | Where it shows | Record |
|---|---|---|
| Chose the film's framing from Claude's recommendation: "Yes, go with it" | the whole film | chat, 2026-11-21 |
| Model access for the plan: "Only Claude Code" | B13 | chat, 2026-11-21 |
| The October choices kept here: the voice `am_eric`, "Say I'm on F-1", the target role, the title *Fine Print*, the name's pronunciation (सुकेत रेड्डी फ्रंदटूर, approved by ear on 2026-10-14) | BIDEA, BOUT, the voice | `../Assignment 4/final-project-film/BUILD-PROMPT.md` §3 |
| The LinkedIn check of two graduate ML postings, written by the student | B04 | `../Assignment 4/final-project-film/evidence/linkedin-check-2026-10-14.md` |
| The approved state update on Nov 8, typed by the student | B10 | `evidence/terminal/2026-11-08-normal-1-run-by-student.txt` |
| JS1's `CONTRACT.md` and JS2's `GATE.md`, written before any code | B11 | fork commits `29b3a26`, `b55d2a5` |
| Frictional entry 1, in the student's own words | `FRICTIONAL.md` | chat, logged 2026-11-21 19:04 EST |
| The approval of the draft film: "Approve it" | the whole film | chat, 2026-11-21 |
| The "worked / didn't work" bar and the labelling plan (60 postings, 30 random rejects, 30 held out), in the student's own words | B17; `APPENDIX.md` §8 | chat, 2026-11-21 |
| Frictional entry 2 (why the bar is set where it is), in the student's own words | `FRICTIONAL.md` | chat, logged 2026-11-21 19:58 EST |

## 2. Claude Code's work (Claude Opus 5.5, in the Claude desktop app)

- **Planning:** the recommendation of the framing, the design (`DESIGN.md`) and the build plan (`PLAN.md`).
- **The draft script**, in the student's first-person voice, for the student to correct (`film/make_sheet.py`, rendered
  as `SCRIPT.md`), and the fact-check table (`FACTCHECK.md`).
- **The Nov 21 runs**, on a fresh clone of JS2 at `9c1db18`: the tests, the live run without approval, the independent
  check, the failure-control run and the rule counts (`evidence/terminal/`). Also the capture tool (`tools/capture.py`).
- **Subagents** (fresh Claude instances given a written brief):
  - a reviewer that read the design and raised five questions (`DESIGN.md` §13);
  - a researcher for the prior work in Part 2 (`evidence/prior-art/PRIOR-ART.md`);
  - a producer that drew every picture (in Manim code, from the toolkit's props), made the narration audio and the
    master, and fixed the pronunciations (`film/PRODUCTION-NOTES.md`);
  - a fact-checker that checked every sentence of the draft script against the records (10 findings; `FACTCHECK.md`);
  - a final reviewer that checked the rendered draft and these records (12 findings, fixed before the final render).
- **The records:** this file, `FRICTIONAL.md` §2, `APPENDIX.md` and `README.md`.

All of the code inside jobwatch was written by Claude Code in JS1 and JS2, except the student's tests named in those
READMEs.

## 3. Third-party assets and licences

| Asset | Used for | Licence |
|---|---|---|
| **brutalist.art** toolkit, `github.com/nikbearbrown/brutalist.art` at `519fcbb` (the course's toolkit) | The `show-tell` pipeline, gates and compiler; `iso_kit.py`; the 25 original isometric props; the Remotion opening `BrutalistHesitantWriter` (no banner, no handle). *Not used:* `ClaudeTitleOutro` (it hard-codes the handle `@NikBearBrown`) and `ClaudeDefinitions` | The repository has no licence file at this commit; it is used as the course's assigned toolkit |
| Manim Community v0.20.1 | Rendering the drawn beats | MIT |
| Remotion 4 | Rendering the opening beat | Remotion licence (free for individuals) |
| Kokoro-82M via `kokoro-onnx` 0.6.1, voice `am_eric` | The narration, synthesized locally from the script | Kokoro-82M: Apache-2.0; kokoro-onnx: MIT |
| EB Garamond (labels) and PT Mono (the terminal replays), both from the toolkit's `runtime/fonts/` | On-screen type | SIL Open Font License 1.1 (`brutalist.art/runtime/fonts/EB_Garamond/OFL.txt`, `…/PT_Mono/OFL.txt`) |
| FFmpeg 8.1 | Audio and video encoding and measuring | LGPL/GPL |

No stock footage, screenshots of other sites, logos, or image- or video-generation models are used. Every picture is
drawn in code by Claude Code from the toolkit's props. Company names appear as
text only.

## 4. Records the script relies on

See `FACTCHECK.md`. It lists, for every factual sentence, the file, commit or log behind it and whether the sentence
says *did*, *is* or *will*.
