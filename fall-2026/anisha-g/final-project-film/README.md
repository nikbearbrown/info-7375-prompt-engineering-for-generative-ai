# A job-search agent that shows its reasons: final project film, in four parts
**Anisha Gaikar · INFO 7375 · Fall 2026**

A film about my final project, the **job-search agent** I'm building in layers (JS1, JS2, …). It watches public job boards, shows me only new postings, says which ones are worth my time with the posting's own words as the reason, and says "I cannot tell" instead of guessing. It never applies, emails, messages anyone, or logs in.

**Built in Professor Bear's four parts, in his order.** Each beat prints its part's name on screen, so the structure is readable with the sound off.

| Part | Beats | What it answers |
|---|---|---|
| 1 · Executive summary | B00–B03 | what I'm building and why anybody would care, with no "how" |
| 2 · Introduction | B04–B07 | what already exists (job alerts; my own dated chatbot tests; the course's collectors, Lectern and the Reallocation Engine) and the gap |
| 3 · Methods | B08–B11 | where the data comes from, what I already built (layers 1–2), what comes next (layer 3, the final shortlist), and what it needs (incl. the Claude-credit constraint) |
| 4 · Evaluation | B12–B15 | my own labels, the checks that don't trust the agent, **my pass mark**, and what exists vs. will exist |

**On-screen honesty labels:**
- **REAL · IN MY GITHUB FOLDER:** results that ran, in `../js1-contract-and-watch/` and `../js2-loop-tools-diff/`.
- **PLANNED · NOT BUILT YET:** layer 3 and the final project.
- **ILLUSTRATION · EXAMPLE ROWS:** B03's example short list.

The detail that doesn't belong on screen is in [APPENDIX.md](APPENDIX.md). Every claim and its source is in [FACTCHECK.md](FACTCHECK.md).

**Narration:** the macOS voice "Samantha" (`say`) reads the script. The same practice as my October pitch film; it is disclosed in the last beat and in SOURCES.md.

## Build
```bash
bash make_film.sh Gaikar          # macOS: makes the narration with `say`, joins it with clips/B00-B15 -> Gaikar_pitch.mp4
```
- **Needs:** `ffmpeg` and macOS `say`.
- **The clips** (`clips/`, silent) were drawn by `tools/render.py` from `beat_sheet.json`, with `python3 tools/render.py beat_sheet.json tools/fonts clips`.
- **Fonts:** in `tools/fonts/` (SIL Open Font License).

## Files
| File | What it is |
|---|---|
| `Gaikar_pitch.mp4` | **The film** (four-part version, 2026-11-23) |
| `beat_sheet.json`, `RECORDING-SCRIPT.txt`, `SCRIPT.md` | The narration, one beat per idea |
| `clips/`, `audio/` | The silent scenes and the narration audio |
| `make_film.sh`, `tools/` | The build |
| `evidence/` | My dated screenshots: ChatGPT 2026-10-13, Claude 2026-10-31 |
| `APPENDIX.md` | Methods and evaluation detail |
| `FACTCHECK.md`, `SOURCES.md`, `FRICTIONAL.md` | Claims and sources, what I used, the honest log |
| `previous-pitch-2026-10/` | My October pitch film (*JobPost Contracts*, graded), kept unchanged |
