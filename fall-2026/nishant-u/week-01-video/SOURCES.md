# SOURCES

## Used

| What | Version / location | Licence (where it was checked) |
|---|---|---|
| Brutalist toolkit (`brutalist.art`) | local clone, commit `6a8380a` + `brutalist-fixes.diff` | No LICENSE file in the repo; licence not stated |
| `main.py` (`probabilities()`) | `info-7375-prompt-engineering-for-generative-ai/lessons/01-randomness-and-first-prompts/code/main.py`, sha256 `df9940ca…43e5d` | Course repo `LICENSE`: MIT, Copyright (c) 2026 Rohit Ghumare. `ATTRIBUTION.md`: the course is adapted from *AI Engineering from Scratch* by Rohit Ghumare under MIT |
| Kokoro-82M voice model, voice `am_onyx` | `kokoro-v1.0.onnx`, `voices-v1.0.bin` via `kokoro-onnx` 0.6.1 | Apache-2.0 according to the toolkit's `generate_audio_kokoro.py`; the `kokoro-onnx` package metadata lists no licence; not checked further |
| Manim Community | 0.18.1 | MIT (package metadata) |
| MiKTeX (LaTeX for `MathTex`) | 25.12 | Not checked |
| EB Garamond (serif) | `runtime/fonts/EB_Garamond/` | SIL Open Font License 1.1, © 2017 The EB Garamond Project Authors (`OFL.txt`) |
| PT Mono (code/output) | `runtime/fonts/PT_Mono/` | SIL Open Font License 1.1, © 2011 ParaType Ltd. (`OFL.txt`) |
| Equation glyphs | LaTeX default fonts via MiKTeX | Not checked |
| ffmpeg | 9.0.2 gyan.dev full build | Built with `--enable-gpl --enable-version3` (`ffmpeg -version`) |
| faster-whisper (QC transcripts only; not in the video) | 1.2.1 | MIT (package metadata) |

No stock media, generated images, AI video or paid APIs. No ElevenLabs, no Higgsfield.

## Made for this video

- `maxsub_runs.py` additions and its saved output `maxsub_runs.stdout.txt`
- `beat_sheet.json`, `manim/scenes.py`, `pad_gaps.py`
- The narration audio in `mp3/` (Kokoro, generated locally)
- `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`, the QC logs, and these write-ups

## What Claude contributed

- **Claude (claude.ai)** helped me choose the concept and drafted the narration script.
- **Claude Code** (this build session, 2026-09-26/27):
  - `maxsub_runs.py`: Claude Code wrote it at my request in an earlier session (in the course
    repo). It imports `probabilities()` from `main.py` without editing it. In this build session,
    Claude Code added the `[1000, 1001]`, `[0, 1]` and `[0, -1000]` blocks on 2026-09-27 and saved
    the output.
  - Wrote `beat_sheet.json`, `manim/scenes.py` and `pad_gaps.py`.
  - Generated the audio, ran the renders and builds, did the frame and transcript QC, and drafted
    `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` and these write-ups.
- **I (Nishant)** chose the scope and all the wording changes, approved each step, and reviewed
  and signed off `FACTCHECK.md`, re-running `maxsub_runs.py` myself.

No Claude responses appear in the video.
