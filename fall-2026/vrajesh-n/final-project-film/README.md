# Early Bird: final project pitch film (v1.0)

**Vrajesh N. · INFO 7375 · Fall 2026**

- **Working title:** Early Bird: a job-search agent for SWE and AI roles
- **Target role:** full-stack software engineer / AI engineer
- **Runtime:** 3:47 (227.32 s narration), 1920x1080, 30 fps
- **Film:** `final/early-bird-pitch.mp4`
- **Version:** v1.0, rebuilt from scratch on 2026-10-24 after the v0.2 film (2026-10-14) was graded. Changes are logged in `FRICTIONAL.md`.
- **Status:** a pitch. Early Bird is not built. What has run: the probe (2026-10-14), a second board snapshot (2026-10-23), and my new-ID diff and greenhouse-watch runs (2026-10-24). Everything else is labelled PLANNED or CONSTRUCTED on screen.
- **Authorship:** the script was drafted with Claude from my decisions and my run outputs; the voice is synthetic (Kokoro). Both are said in the film. Details in `SOURCES.md`.

## What is here
| File | What it is |
|---|---|
| `PROJECT-BRIEF.md` | the seven answers on one page, ending with *exists today* / *will exist* |
| `SCRIPT.md` | the narration exactly as voiced |
| `beat_sheet.json` | narration and visual plan per beat, synced to measured audio |
| `build_beats.py` | writes and syncs `beat_sheet.json` |
| `evidence/` | probe script; board snapshots `2026-10-14/`, `2026-10-23/`; my ID diff; my greenhouse-watch runs `gw/` (public posting data only) |
| `toolkit/EarlyBirdFilm.tsx.txt` | copy of the ten Remotion scenes (stored as .txt: course CI rejects .tsx) |
| `BUILD-PROMPT.md` | prompts and commands that rebuild the film |
| `FACTCHECK.md` | every on-screen figure and its source |
| `SOURCES.md` | sources, my material and runs, Claude's contributions, third-party licenses |
| `FRICTIONAL.md` | dated work log (Part 2 = v1.0, in my own words) |
| `SHOTLIST.md`, `PROMPTS.md` | per-beat visuals; narration respellings (no generated imagery) |
| `_qc/REPORT.md`, `TYPECHECK.md`, `final/*.verified.json` | toolkit gate reports |

## Rebuild
See `BUILD-PROMPT.md`. In short: evidence commands → `python build_beats.py` → Kokoro narration → `align.py` → `python build_beats.py --sync` → `remotion_scenes.py` → `./art run` → `./art final`. Free and local; no keys.

## Privacy
No resume file, contact details, private company list or LinkedIn data is in this folder. The probe boards are example companies, not my list. greenhouse-watch scored against the course's fictional sample resume, not mine.
