# CheckedSQL — Final Project Pitch Film

- **Name:** Siddhesh Nikam
- **Course:** INFO 7375, Fall 2026
- **Project working title:** CheckedSQL — plain-English questions about marketing-campaign data, answered by Claude-written SQL and scored against hand-verified answers
- **Target role:** Data Analyst (marketing analytics)
- **Film:** `checkedsql-pitch.mp4` · runtime **3 min 34 s** · 16:9, 3840×2160, 24 fps
- **Status (v2, 2026-10-24):** a pitch with its first piece running. `checkedsql/` holds the synthetic data, ten test questions, the answer key and the checker; the baseline SQL (drafted with Claude) scores **10/10**, and two deliberately wrong ROAS queries are caught. The Claude step isn't built yet; see *exists today / will exist* at the end of `PROJECT-BRIEF.md`.
- **Revision:** v2 answers the 2026-10-24 feedback. It adds a real chat-assistant test (P2), shows real data and real results on screen instead of generic props (P6), and expands the log (FRICTIONAL).

## What's in this folder

| File | What it is |
|---|---|
| `checkedsql-pitch.mp4` | the rendered film |
| `checkedsql-pitch.srt` | captions, timed from the measured narration |
| `checkedsql/` | **the first runnable piece:** `python3 checkedsql/checker.py` prints the score table (see its README) |
| `PROJECT-BRIEF.md` | the seven answers in text, ending with *exists today* and *will exist* |
| `beat_sheet.json` | narration and visual plan, beat by beat (with measured durations) |
| `BUILD-PROMPT.md` | the prompts and commands that rebuild the film |
| `SOURCES.md` | what I used, what I made, what Claude contributed, licences |
| `FRICTIONAL.md` | dated log of what happened while making it |
| `gate-reports/` | the toolkit's quality-gate reports (type check, render integrity, loudness, bookends, layout, fact check) |
| `build/` | film sources: `make_sheet.py`, `scenes.py`, `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` |
| `build_film.sh` | one command that rebuilds the film from `build/` |

## How to rebuild the film (macOS)

```bash
brew install python ffmpeg node cairo pango pkg-config
git clone https://github.com/nikbearbrown/brutalist.art ~/brutalist.art
cd ~/brutalist.art && ./setup --install     # Python deps, Remotion deps, fonts, Kokoro model
./setup                                     # readiness table: everything required should be green
cd <this folder>
chmod +x build_film.sh
./build_film.sh ~/brutalist.art
```

Free pipeline only: narration is local Kokoro (`am_onyx`, synthetic voice), drawings are Manim, the two opening cards are Remotion. No API keys, no paid generation, no upload.
