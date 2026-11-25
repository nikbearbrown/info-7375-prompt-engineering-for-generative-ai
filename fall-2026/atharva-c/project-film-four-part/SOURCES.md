# SOURCES

## What I used
- **Brutalist toolkit**: https://github.com/nikbearbrown/brutalist.art, commit `b21f625`, same as the pitch film. No LICENSE file at that commit. The show-tell drawing kit (`skills/make/show-tell/templates/iso_kit.py`) is pasted into `film-source/scenes.py`, together with helpers carried over from the pitch film.
- **Kokoro-82M TTS** via kokoro-onnx, voice `am_michael`, run locally (Apache-2.0).
- **Manim Community** and **ffmpeg** for rendering; **EB Garamond** font (SIL OFL).
- **faster-whisper** (base.en) for the pronunciation check only. Nothing it produced is in the film.
- **NYC TLC Trip Record Data**: yellow taxi trips, January 2024, public download (2026-10-09). Data files are not committed.
- **pandera 0.36.0** and **pandas** for the 2026-11-22 schema-inference run (`evidence/2026-11-22-pandera-infer-schema/`).
- **Prior work cited in the film** (details and links in `PRIOR-WORK-CHECK.md`): Amazon Deequ docs; Great Expectations legacy docs (0.15/0.16); DeMillo, Lipton & Sayward, "Hints on Test Data Selection", IEEE Computer 11(4), 1978; Akella et al. (IBM Research), arXiv 2509.10572, 2025.

## What I made
- The fault catalogue, `FAULT-CATALOGUE.md`: the clean-baseline choice, the 18 faults and my reason for each, the pass/fail thresholds and the resource cap (commit `e5aac1c`, 2026-11-22). Claude proposed 22 candidates and checked them against the data; I chose, wrote and committed the catalogue.
- `FRICTIONAL.md`, in my own words. Claude reviewed every entry for accuracy. The Nov 22 first entry was pasted in unchanged; in the second, at my request, Claude corrected five factual slips (listed in CLAUDE-LOG.md) before saving. The Nov 23 entry is my own revision: Claude pointed out factual slips against the files, and I rewrote it myself twice; Claude saved my final text verbatim.
- Decisions: making a new four-part film rather than reusing the pitch; locking the narration; the thresholds.
- Runs: on 2026-11-22 I reran every evidence script myself in my sandbox venv: the data profile, the baseline check, and both pandera scripts (pandera 0.36.0, pandas 3.0.6). The output matched Claude's first run exactly (50 not_nullable; 14, 17, 16, 13, 25 rows flagged).

## What Claude contributed
Logged as facts in `CLAUDE-LOG.md`. In short, Claude Code (Opus 5.5), 2026-11-22:
- drafted `SCRIPT-DRAFT.md` (v1, then v2 filled from my catalogue), which I read and locked; after I asked whether the film met every requirement, reworded I3, M4 and V1 (Claude Pro is my plan, as I told it) and trimmed other beats to stay under 4 minutes;
- ran the prior-work check and found the IBM paper, which narrowed my claim;
- wrote and first ran the pandera, data-profile and baseline-check scripts in `evidence/`;
- reviewed my FRICTIONAL entry and catalogue drafts, flagging overclaims and clashes with the data, without rewriting them;
- built the film: `beat_sheet.json` (via `film-source/write_beat_sheet.py`), `scenes.py` (14 new drawn scenes plus the outro), `make_sheet.py`, FACTCHECK.md and SHOTLIST.md; generated the audio; ran the Whisper check and the toolkit's gates; drafted this file, README.md and BUILD-PROMPT.md.

## Third-party assets
No third-party images, video, music or stock footage. Every visual is drawn in code; the only audio is Kokoro narration.

## Not included
No résumé, contacts, application data or conversation transcripts are in this folder or the film.
