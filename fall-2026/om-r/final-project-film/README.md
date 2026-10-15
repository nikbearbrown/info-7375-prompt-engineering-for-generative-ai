# agent-reliability-audit — Final Project Pitch Film

**Name:** Om Raut
**Course:** INFO7375 — Final Project Pitch Film
**Working title:** agent-reliability-audit
**Target role:** ML/AI engineer, agent-evaluation / ML-platform reliability
**Runtime:** 2:21 (140.79s)
The video is submitted on Canvas, not in this GitHub folder — this repo's .gitignore excludes .mp4 files, so the video travels only in the Canvas zip.

## What this is

This is a **pitch**, not a finished build. As of this submission, the
project itself (the CLI tool) does not exist yet — what exists is the
brief, the cited research behind its core idea, and this film explaining
what will be built and why. See `PROJECT-BRIEF.md`'s closing
"Exists today" / "Will exist" lists for the exact honest split.

**One-sentence pitch:** a command-line tool that measures whether an AI
agent is reliably right, not just right once, and whether it fails safely
when one of its tools hands it bad data.

## How to rebuild this film from scratch

Full detail in `BUILD-PROMPT.md`. Short version:

```bash
git clone https://github.com/nikbearbrown/brutalist.art
cd brutalist.art
./setup --install   # if pip/ffmpeg are missing, see BUILD-PROMPT.md

mkdir -p youtube/agent-reliability-audit-pitch
# copy in: make_sheet.py, scenes.py, FACTCHECK.md, SHOTLIST.md, PROMPTS.md

cd youtube/agent-reliability-audit-pitch
python3 make_sheet.py   # writes the PRE-AUDIO beat sheet — see BUILD-PROMPT.md
                         # for why the submitted beat_sheet.json differs

cd ../..
python3 runtime/scripts/generate_audio_kokoro.py youtube/agent-reliability-audit-pitch
# Note: the silent tail on BCLOSE is a manual fix — see BUILD-PROMPT.md step 6
# before running ./art final, or the submitted master's tail won't reproduce.
./art run youtube/agent-reliability-audit-pitch --height 2160
./art final youtube/agent-reliability-audit-pitch --height 2160
```

## Files in this submission

- `README.md` — this file
- `agent-reliability-audit-pitch.mp4` — submitted on Canvas, not in this
  folder (SHA-256: 4a78550dbe0e64567e9f05cb7d251f6f3d3ca2619ed8457be14993e51feb136b)
- `PROJECT-BRIEF.md` — the seven required questions, answered honestly
- `beat_sheet.json` — the POST-BUILD narration/visual plan (measured
  durations, render records, and the BCLOSE silent-tail fix included —
  see `BUILD-PROMPT.md` for why this differs from running `make_sheet.py`
  fresh)
- `make_sheet.py`, `scenes.py` — the source that generates the beat sheet
  and the Manim scenes
- `BUILD-PROMPT.md` — the real commands used to build this, including
  every fix required along the way
- `SOURCES.md` — what was used, what Claude contributed, external citations
- `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` — required show-tell paperwork
- `TYPECHECK.md`, `_qc/REPORT.md`, `layout_audit.md` — the toolkit's own
  quality-gate reports
- `FRICTIONAL.md` — dated log of the real build process, including every
  gate failure and fix
