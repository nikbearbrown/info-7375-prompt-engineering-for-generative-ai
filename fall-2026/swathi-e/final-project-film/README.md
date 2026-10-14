# Cite or Refuse — Final Project Pitch Film

**Swathi Baba Eswarappa** · INFO 7375 · Final Project Pitch Film
**Working title:** Cite or Refuse
**Target role:** AI/ML engineer or data engineer · **Reader:** a hiring manager or engineer reviewing me for that role
**Runtime:** 3:38 (218.68 s)
**Film:** `BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.mp4` · 3840×2160, 24 fps · −19 LUFS
**Captions:** `BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.srt`

> The film (`.mp4`) and the narration files (`mp3/*.mp3`) are in the Canvas zip only: the
> course repo's `.gitignore` excludes `.mp4` and `.mp3`. Everything else is identical in both.

## What the film is

A pitch for **Cite or Refuse**, a tax helper for international students that will answer
only from official IRS publications, show the exact passage and tax year, and refuse when
the publications do not cover the question. When done, it will be a GitHub repository.

**Nothing in the pitched project exists yet.** What exists today is the plan
(`PROJECT-BRIEF.md`), my dated test notes (`TEST-NOTES.md`), and one check against page 7 of
the 2025 Instructions for Form 1040-NR. The film labels everything else as planned:
PROPOSED · NOT BUILT on the planned-system pictures, CONSTRUCTED MOCK-UP on the terminal,
and "will" in the narration.

## The 13 beats

| Beat | Scene | Picture |
|---|---|---|
| B01 | `B01_TwoAnswers` | two ChatGPT number cards (Oct 9, 2026), same question, $15,750 ≠ $15,000 |
| B02 | `B02_OfficialCheck` | IRS instructions page 7 highlights the $15,750 filing threshold; run A ticked, run B crossed |
| B03 | `B03_Problem` | a student facing a yearly stack of IRS documents, Form 8843 on top |
| B04 | `B04_What` | CITE OR REFUSE: a question branches to *answer + passage + tax year* or *refuse* (PROPOSED) |
| B05 | `B05_Alternatives` | result grid from my Oct 9, 2026 test: 3 tools × 3 questions |
| B06 | `B06_Plan` | planned pipeline, dashed boxes (PROPOSED) |
| B07 | `B07_Versions` | clarified instructions, answers carry their tax year, human approval gate (PROPOSED) |
| B08 | `B08_FirstMinute` | a reviewer's first minute in a terminal (CONSTRUCTED MOCK-UP, dashes for scores) |
| B09 | `B09_Proves` | five skills point to three evidence boxes that will exist |
| B10 | `B10_Scope` | OUT (struck through) vs FIRST, with the fresh-clone test that will run |
| B11 | `B11_Risk` | table extraction with one bad cell, checked by hand; the rest marked UNVERIFIED (PROPOSED) |
| B12 | `B12_Why` | ALREADY HAVE (with my Reallocation Engine PR) vs NEW TO ME |
| B13 | `B13_Close` | EXISTS TODAY (ticked) vs WILL EXIST (dashed), then sign-off |

## How it was made

Free local pipeline, no API keys, no paid generation, no upload:
**Kokoro** (`af_heart`) for narration → **Manim CE** for the 13 scenes → **FFmpeg** to
mux, concatenate and normalise loudness. Audio is the master clock: each scene reads its
narration length and pins its cues to phrases in the script.

Every number on screen is read from `data/facts.json`; `check_facts.py` fails the build
if a number is typed into a scene or if a shown number's spoken form is missing from the
narration.

## Quality gates

All reports are in `qc_reports/`; every gate passes on the final film.

| Gates | Where the reports are |
|---|---|
| Brutalist toolkit, local copy: A (static scene), W (WCAG and margins), B (layout audit), V (final frames) | `qc_reports/gateA_*`, `gateW_*`, `gateB/`, `gateV_*`, `_qc/` |
| Brutalist toolkit, current upstream: LOUDNESS, MASTER, T (typography), SRT, SHARPNESS | `qc_reports/upstream/` |
| Week 1 gates: frame-safety sweep, 2–4 min runtime | `qc_reports/week1_*` |
| Numbers from one file | `qc_reports/facts_check.txt` |
| Final master: streams, loudness, silence, captions | `qc_reports/final_master_verification.txt` |

## Rebuild

```bash
./build.sh                    # narration -> scenes -> local gates -> mux -> captions
./build.sh --mux-only         # re-run every local gate and re-mux from existing renders
build/run_upstream_gates.sh   # current upstream toolkit gates -> qc_reports/upstream/
```

Needs ffmpeg, espeak-ng, and a Python with `kokoro-onnx`, `manim`, Pillow and SciPy
(see `BUILD-PROMPT.md` §5), plus the Brutalist toolkit at `../brutalist.art`. From the
GitHub copy, run the full `./build.sh`: it regenerates the narration that git does not hold.
`--mux-only` also needs the rendered scenes in `media/`, which are not submitted.

## Files

| Path | What |
|---|---|
| `PROJECT-BRIEF.md` | the seven answers, ending with *exists today* and *will exist* |
| `beat_sheet.json` | 13 beats: narration, visual plan, measured durations |
| `TEST-NOTES.md` | my dated chatbot test, and the IRS check |
| `data/facts.json` | every on-screen number, its source, and where it is spoken |
| `scene.py` | the 13 Manim scenes and the `Beat` base class with its layout checks |
| `check_facts.py` | numbers-from-one-file gate |
| `build.sh`, `build/render_all.sh`, `build/run_upstream_gates.sh`, `build_mux.py`, `make_srt.py`, `qc_frames.py` | build pipeline |
| `mp3/` | the 13 narration files (Canvas zip only) and `timings.json`, their measured durations |
| `qc_reports/`, `_qc/` | every gate report |
| `BUILD-PROMPT.md` | prompts and the commands actually executed |
| `SOURCES.md` | sources, tools, licences, and what Claude contributed |
| `FRICTIONAL.md` | my dated log of what went wrong and what I did about it |
