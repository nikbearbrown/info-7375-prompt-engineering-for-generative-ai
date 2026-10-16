# Early Bird: final project pitch film

**Vrajesh N. · INFO 7375 · Fall 2026**

- **Working title:** Early Bird: a job-search agent for SWE and AI roles
- **Target role:** full-stack software engineer / AI engineer
- **Runtime:** 3:38 (218.27 s), 1920x1080, 30 fps
- **Film:** `final/early-bird-pitch.mp4`
- **Status:** a pitch. Only `evidence/probe.py` has run (2026-10-14). Everything else is proposed and labelled PLANNED or CONSTRUCTED on screen.

## What is here
| File | What it is |
|---|---|
| `PROJECT-BRIEF.md` | the seven answers on one page, ending with *exists today* / *will exist* |
| `SCRIPT.md` | the narration exactly as voiced |
| `beat_sheet.json` | narration and visual plan per beat, synced to measured audio |
| `build_beats.py` | writes and syncs `beat_sheet.json` |
| `evidence/` | the real probe script and its dated raw responses (public posting data only) |
| `toolkit/EarlyBirdPitch.tsx.txt` (stored as .txt: the course CI rejects .tsx files; copy it to `runtime/remotion/src/EarlyBirdPitch.tsx` to use it) | copy of the ten Remotion scenes (they run from the brutalist.art clone) |
| `BUILD-PROMPT.md` | prompts and commands that rebuild the film |
| `FACTCHECK.md` | every on-screen figure and its source |
| `SOURCES.md` | sources, my material, Claude's contributions, third-party licenses |
| `FRICTIONAL.md` | dated work log, including the change from my Doorman draft |
| `_qc/REPORT.md`, `TYPECHECK.md`, `final/*.verified.json` | toolkit gate reports: GATE V 0 BLOCKER / 0 MAJOR, GATE T PASS, GATE F clean |

## Rebuild
See `BUILD-PROMPT.md`. In short: `python build_beats.py` → Kokoro narration → `align.py` → `python build_beats.py --sync` → `remotion_scenes.py` → `./art final`. Free and local; no keys.

## Privacy
No resume file, contact details, private company list or LinkedIn data is in this folder. The five boards in the probe are example companies, not my list.
