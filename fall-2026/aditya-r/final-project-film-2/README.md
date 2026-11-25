# DayThread — Final Project Film

**Aditya Raj** · INFO 7375 Prompt Engineering and Agentic AI · Fall 2026
**Project:** DayThread, a planned check-in assistant for home care. It will remember what a
client says across days and show the client's exact words to a care coordinator, who decides
what happens next.
**Target role:** AI Engineer
**Runtime:** 3:13 (193.1 s, measured)

## What this film is

A plan, in the four parts the assignment asks for, in its order:

| Part | Beats | Covers |
|---|---|---|
| 1. Executive summary | BIDEA–B03 | what DayThread is and why it matters; what exists today |
| 2. Introduction | B04–B05 | Lifeline and DailyCall, from their own documentation; why DayThread again |
| 3. Methods | B06–B12 | the delegation contract; the loop; the fine-tuned checker (DistilRoBERTa from Hugging Face); data; resources; order of work |
| 4. Evaluation | B13–B16 | checker vs keyword list and untrained model on a sealed held-out set; five deliberate failures; the controlled failure; what it can't show |

The detail behind parts 3 and 4 is in [APPENDIX.md](APPENDIX.md).

## What changed since the October pitch

- **New:** a delegation contract (one testable condition per handoff, written with its tests
  before Claude implements anything).
- **New:** a fine-tuned open model as the separate check. It reads the raw transcript, never the
  summary.
- **Changed risk:** the October replay showed summaries kept the fall in 10/10 but changed its
  meaning in 9/10. The controlled failure will force an omission, and meaning drift is stated as a
  limit.

## What exists and what doesn't

- **Exists:**
  - the October pitch film and brief;
  - the two-day replay run on 2026-10-25 (`../final-project-film/replay/`);
  - this film and its plan.
- **Does not exist yet:**
  - the contract, the checker (not downloaded or trained), the loop, memory, review page,
    executor;
  - tests and evaluation;
  - PyTorch is not installed yet.

Every drawing of the planned system is captioned "Constructed — proposed workflow". The only
observed result shown (B02) is captioned "Replay run 2026-10-25 · synthetic data · fictional
client".

## The film

| | |
|---|---|
| File | `Raj_Aditya_INFO7375_FinalProjectFilm2.mp4` (Canvas only; the course repo's `.gitignore` excludes `*.mp4`) |
| Format | 3840×2160, 24 fps, H.264 + AAC |
| Size | 21,391,364 bytes |
| SHA-256 | `71cd25736c32a9fe9e1354c0d153dc1f52591b3fcc241508b0cd4a9efde20faf` |
| Voice | synthesized (Kokoro `am_onyx`, local) reading Aditya's script, disclosed on screen and aloud |
| Gates | F, L, A, W, B, V, T all pass (`gate-reports/`) |

## Contents

| Path | What it is |
|---|---|
| `SCRIPT.md` | narration and visual plan (v1) |
| `APPENDIX.md` | methods and evaluation detail (plan) |
| `beat_sheet.json` | toolkit beat sheet with measured audio and build stamps |
| `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` | the toolkit's paperwork set |
| `BUILD-PROMPT.md` | the requests and the commands that rebuild the film |
| `SOURCES.md` | sources, licences, and who contributed what |
| `FRICTIONAL.md` | dated log for this film |
| `source/` | `make_sheet.py`, `audio_post.py`, `assemble_scenes.py`, `scenes_body.py`, `scenes.py`, `final_checks.py`, `mp3/timings` |
| `gate-reports/` | TYPECHECK.md (GATE T), Gate V report and contact sheet, layout audit, run/final logs, `checks/` (probe, transcript, frame sheets) |

## GitHub folder vs Canvas ZIP

The ZIP is built from this folder, and the GitHub folder holds the same files except the media
the course repo's `.gitignore` excludes (`*.mp4`, `*.mp3`). These are in the Canvas ZIP only:
- `Raj_Aditya_INFO7375_FinalProjectFilm2.mp4`: the film (SHA-256 above);
- `source/mp3/beat-*.mp3` (18 files): the narration.

The ZIP's own checksum and the commit hash are in the Canvas submission text.

## Rebuild

See [BUILD-PROMPT.md](BUILD-PROMPT.md). Cost: $0.00; no network calls while rendering.
