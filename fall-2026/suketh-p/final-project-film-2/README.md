# Fine Print — Final Project Film

INFO 7375 · Fall 2026 · Suketh Reddy Produtoor · Canvas: "Final Project Film" (25 points, due Mon 2026-11-23 11:30 pm)

**Approved by the student** on 2026-11-21 ("Approve it"). The final render adds the student's bar (B17) and the fixes
from a final review. Claude Code drafted this README from the records in this folder,
and [SOURCES.md](SOURCES.md) says who did what.

## The film

A film of **4:14** (the brief asks for no length; the cap set in the design was five minutes), in the four parts the
brief asks for, in its order ([ASSIGNMENT-BRIEF.md](ASSIGNMENT-BRIEF.md)):

| Part | What it covers | Starts at |
|---|---|---|
| 1 · What and why | What Fine Print is, and why a posting's fine print matters to an F-1 new grad (no "how") | 0:00 |
| 2 · What exists | The student's own A3 recipe and LinkedIn check; the USCIS H-1B data hub, Jobscan, and two research papers; what Fine Print adds | 0:47 |
| 3 · How | The data; jobwatch running for real on Nov 21 (164 tests, 172 postings not in the Nov 8 snapshot, the approval gate); how it is built; the dated steps to Dec 20; the resources | 1:34 |
| 4 · Did it work? | The hand-labelled, held-out evaluation; four measures; deliberate failures; the student's own bar; the limits | 3:08 |
| Close | The title, the student's name, and the credit line | 4:11 |

- **The film** is submitted on Canvas as `Produtoor_Suketh_INFO7375_FinalProjectFilm_1080p.mp4` (1920 × 1080, 24 fps).
  The course's `.gitignore` keeps MP4s out of GitHub. Its captions are `Produtoor_Suketh_INFO7375_FinalProjectFilm_1080p.srt`. It is the student's choice of 1080p ("So cut it down to the normal 1080p"), scaled
  down from the 4K render (`film/exports/landscape/fine-print-film.mp4`). The 4K render passed every gate and check: GATE
  T, Gates F, L, A, W, B and V, the master check, loudness (−22.05 LUFS), sharpness, captions (92 cues) and the
  fact-check table (`film/gate-reports/final-2.log`, `film/_qc/REPORT.md`). The 1080p file's SHA-256 is
  `365cbbc12fa18babe255fa95d43dd7ab6eb69b3858207f43cacd15ef1b1d738c` (also in `submission/SHA256SUMS`).
- **The detail behind it** (as the brief asks): [APPENDIX.md](APPENDIX.md), also as `APPENDIX.pdf` (on Canvas:
  `Produtoor_Suketh_INFO7375_FinalProjectFilm_Appendix.pdf`).

## What is real and what is constructed

Every picture has a stamp in its top left corner.
- **`real · …`** marks something that ran or was checked, with its date. Examples: the Nov 21 terminal replays (excerpts replayed from the saved logs: lines selected, long lines wrapped, column
  spaces squeezed, and the Nov 8 home path shown as `~/…`; every change is listed in
  [evidence/terminal/README.md](evidence/terminal/README.md)) and the student's Nov 8 approval run.
- **`constructed · not built`** marks the plan.

Nothing of Fine Print's reader is built yet. The film says "will" for all of it. [FACTCHECK.md](FACTCHECK.md) gives
the record behind every sentence. A separate Claude Code subagent fact-checked the draft script against the records:
of its ten findings, nine were fixed and one was already moot. A second subagent reviewed the rendered draft, and its
findings were fixed before the final render.

## How it was made

- **Toolkit and pipeline.** The course's brutalist.art toolkit (`show-tell`, commit `519fcbb`), with the same free,
  local pipeline as October's pitch film: Manim for the drawings, Remotion for the opening line, and Kokoro-82M (voice
  `am_eric`) for the narration.
- **Narration.** The script is first person, drafted by Claude Code and approved by the student. The student's name is
  voiced from their own pronunciation guide.
- **Reproducing it.** The pipeline is in [PLAN.md](PLAN.md); the production notes are in `film/PRODUCTION-NOTES.md`.

```bash
cd film
python3 make_sheet.py && python3 build_scenes.py && bash build_audio.sh
../brutalist.art/art run . --height 2160
../brutalist.art/art final . --height 2160 --out exports/landscape
python3 make_srt.py
```

`brutalist.art` here is a link to `../Assignment 4/brutalist.art`, the toolkit install from October.

## Files

| File | What |
|---|---|
| `ASSIGNMENT-BRIEF.md` | The assignment, verbatim |
| `DESIGN.md`, `PLAN.md` | The design (with the questions a reviewer raised) and the build plan |
| `SCRIPT.md` | The narration, beat by beat, with each beat's stamp (generated from `film/make_sheet.py`) |
| `FACTCHECK.md` | Every sentence and its record |
| `APPENDIX.md` / `.pdf` | Detailed methods, data, resources and evaluation |
| `SOURCES.md` | Who did what; licences |
| `FRICTIONAL.md` | The student's entries (verbatim) and Claude Code's timeline |
| `evidence/terminal/` | Exact captures of the Nov 21 runs, plus the student's Nov 8 run; `SHA256SUMS` |
| `evidence/prior-art/PRIOR-ART.md` | The prior work, checked on each source's own page |
| `film/` | The film's source (`make_sheet.py`, `scenes_body.py`, the build scripts) and its gate reports |
| `tools/` | `capture.py` (the terminal captures), `make_script_md.py`, `appendix_pdf.py` |
| `work/` | A scratch clone of jobwatch at `9c1db18` (not submitted) |
