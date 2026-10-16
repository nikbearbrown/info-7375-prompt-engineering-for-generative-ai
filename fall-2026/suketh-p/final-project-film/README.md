# Fine Print — Final Project Pitch Film

| | |
|---|---|
| **Student** | Suketh Reddy Produtoor (GitHub `sukethrp`) · INFO 7375 Prompt Engineering for Generative AI · Fall 2026 |
| **Working title** | *Fine Print* |
| **Target role** | New-grad ML/AI engineer |
| **Runtime** | **3:15** (195.0 s) · 3840×2160 · 24 fps · H.264 + AAC · captions in `fine-print-pitch.srt` |
| **Film** | `fine-print-pitch.mp4` · 11.7 MB · SHA-256 `75acbe180e1b7d81555639df23f8aa3734e03c802c8875eb737f2acc5392b1cf` |
| **Made with** | brutalist.art `show-tell` at `519fcbb`, free local pipeline (Kokoro, Manim, Remotion); no keys, nothing uploaded |

**Where the film is.** `fine-print-pitch.mp4` is in the Canvas zip, `Produtoor_Suketh_INFO7375_FinalProjectFilm.zip`.
The course repository keeps generated audio and video out of Git (its `.gitignore`: `*.[mM][pP]4`), so the GitHub copy
of this folder holds every other file, and the SHA-256 above identifies the film.

## What the film pitches

*Fine Print* will be an agent that reads new-grad ML job postings for an F-1 student, quotes the exact sentence behind
every requirement that could rule them out, compares it with the applicant's documented background, and stops for my
approval before anything reaches my shortlist. It grows out of my Assignment 3 recipe, which screened eight real postings
by title and sponsorship record for a fictional applicant. Read in full, six of them asked for 2 to 12+ years of
experience or excluded new graduates. The film answers the assignment's seven questions; `PROJECT-BRIEF.md` answers them in text and ends with the
**exists today** and **will exist** lists.

**What is real and what is not.** Every beat that shows the project carries a stamp in its top-left corner: `real · …`
for Assignment 3 evidence (B00, B01; the eight postings were judged for a fictional applicant) and my LinkedIn check (B08,
left side), `constructed · not built` for every picture of the proposed agent, and
`constructed example` for the made-up sentence "5 yrs preferred" (B04). Nothing of the agent exists yet. The film shows no
screenshots and no Claude responses. The narration is my script, in the first person, synthesized locally by Kokoro
(voice `am_eric`, my choice); it is not a recording of my voice.

## Contents

| File | What it is |
|---|---|
| `fine-print-pitch.mp4`, `fine-print-pitch.srt` | The film and its captions |
| `PROJECT-BRIEF.md` | The seven answers, then *exists today* / *will exist* |
| `beat_sheet.json` | Narration and visual plan, one entry per beat, with measured durations and build stamps |
| `BUILD-PROMPT.md` | The commands and prompts that rebuild the film |
| `SOURCES.md` | What I used, what I made, what Claude Code contributed, third-party licences |
| `FRICTIONAL.md` | My dated entries, the factual timeline, who did what |
| `FACTCHECK.md` | Every spoken or shown claim, with verdict and source (33 rows) |
| `SHOTLIST.md`, `PROMPTS.md` | Shot list (props, labels, stamps) · "no generation prompts" |
| `make_sheet.py`, `build_audio.sh`, `name_voice.py`, `finish_audio.py`, `make_srt.py` | Script → sheet → narration (my name from my pronunciation guide) → captions |
| `scenes_body.py`, `build_scenes.py`, `scenes.py` | The 15 drawn beats; `scenes.py` is generated (toolkit kit + props + `scenes_body.py`) |
| `gate-reports/` | Every gate run and report (see below) |
| `evidence/` | A3 test re-run, PR #12 state, toolkit setup log, pronunciation checks, my LinkedIn check |

## Quality gates (the toolkit's own checks, all run on 2026-10-14)

| Gate | Result | Report |
|---|---|---|
| F (paperwork) + fact-check table | PASS; 33 rows, every claim-bearing beat covered | `gate-reports/factcheck_check.log` |
| A (static scene check) | 15/15 scenes clean | `gate-reports/art-run-*.log` |
| W (contrast, margins, overlap) | clean (the outro by hand on a renamed copy: clean) | `gate-reports/gate-w-BOUT_Outro-manual.txt` |
| B (layout audit, strict) | 0 errors, 0 warnings (one B08 label fixed after a strict-mode block) | `layout_audit.md`, `gate-reports/art-run-7.log` |
| V (frame-level visual QC) | 32 frames, 0 BLOCKER, 0 MAJOR | `_qc/REPORT.md`, `qc-sheet.png` |
| T (type check, the final-cut gate) | **PASS**, 16 beats, 0 FAILs (after 3 FAILs on a dropped card: see FRICTIONAL.md) | `TYPECHECK.md`, `gate-reports/TYPECHECK-*-fail-*.md` |
| Master (render integrity) | PASS: 3840×2160, 24 fps, yuv420p, H.264, audio present, 195.0 s = beat sheet, no review markers | `MASTERCHECK.md` |
| Loudness | PASS: −22.01 LUFS, true peak −6.89 dBTP | `LOUDNESS.md` |
| Sharpness | PASS, 16 beats, on the final master | `gate-reports/SHARPNESS-final-master.md` |
| Captions | PASS, 70 cues, 0 errors | `SRTCHECK.md` |
| Receipt | `art final` status "ready", SHA-256 above | `gate-reports/fine-print-pitch.verified.redacted.json` |

## How to rebuild the film

Short version (full detail, versions and the prompts are in `BUILD-PROMPT.md`), with the toolkit cloned beside this
folder as `../brutalist.art` at commit `519fcbb` and its venv active:

```bash
python3 build_scenes.py && bash build_audio.sh
../brutalist.art/art run . --height 2160
../brutalist.art/art final . --height 2160 --out exports/landscape
python3 make_srt.py
```

## Credits and assistance

Built with Claude Code (Claude Opus 5.5), which drafted the script, the scenes and these documents and ran the toolkit;
I chose the project, the role, the voice and the title, changed the design (the background comparison), wrote my Frictional
entries, and reviewed the script and the film. Details in `SOURCES.md` and `FRICTIONAL.md`. Toolkit: brutalist.art
(github.com/nikbearbrown/brutalist.art) and its 25 original isometric props. The film uses no instructor persona,
handle or outro: the toolkit's outro card hard-codes one, so the outro here is a drawn beat with my name.
