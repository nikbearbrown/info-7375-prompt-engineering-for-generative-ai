# SOURCES — final-project-pitch-nishant-u

## Tools and licences

Each licence is as stated in the repo, package or program itself, checked on 2026-10-14.

| Tool | Version used | Licence, as stated | Where it is stated |
|---|---|---|---|
| Brutalist toolkit (`github.com/nikbearbrown/brutalist.art`) | commit `519fcbb`, plus my `brutalist-fixes.diff` | **No licence stated.** The checkout has no LICENSE file; the only licence files it tracks cover vendored parts (e.g. `runtime/remotion/src/vendor/LICENSE-roughjs`, `icons/NOTICE.md`) | `git ls-files` in the checkout |
| Kokoro: `kokoro-onnx` Python package | 0.6.1 | MIT License, "Copyright (c) 2025 github.com/thewh1teagle" | `licenses/` in the package's `dist-info` |
| Kokoro: model files `kokoro-v1.0.onnx`, `voices-v1.0.bin` | v1.0 | Described by the toolkit as "a local 82M-parameter Apache-2.0 model". No licence file ships with the model files in the checkout | `runtime/scripts/generate_audio_kokoro.py`, line 5 |
| Manim Community | 0.18.1 | MIT License | package metadata (`License: MIT`, OSI classifier) |
| ManimPango (Manim's text engine) | 0.5.0 | MIT License | package metadata |
| Remotion (`remotion`, `@remotion/cli`) | 4.x | "SEE LICENSE IN LICENSE.md": the Remotion License, with a Free License ("Individuals and small companies are allowed to use Remotion to create videos for free (even commercial)") and a Company License for larger for-profit organisations | `runtime/remotion/node_modules/remotion/package.json` and `LICENSE.md` |
| ffmpeg / ffprobe (gyan.dev full build, winget `Gyan.FFmpeg`) | 9.0.2 | GNU General Public License, version 3 or later (build configured `--enable-gpl --enable-version3`) | `ffmpeg -L`, `ffmpeg -version` |
| MiKTeX | 25.12 | "This is free software; see the source for copying conditions." Installed for Week 1; this film has no math, so it was not used | `miktex --version` |
| EB Garamond font (`EBGaramond-Regular.ttf`, used in every Manim scene) | static build in the toolkit | SIL Open Font License, Version 1.1; "Copyright 2017 The EB Garamond Project Authors" | `runtime/fonts/EB_Garamond/OFL.txt` |

Also used, outside the film's pictures and sound:
- `faster-whisper` 1.2.1 (MIT License, package metadata) with locally cached Whisper `small.en` and
  `medium.en` models, only to transcribe narration for pronunciation checks.
- Google Chrome (installed app), only as Remotion's renderer for BIDEA and BDEFS.
- Fonts in BIDEA and BDEFS: these Remotion bookends use the toolkit's CSS font stacks (serif:
  "Tiempos Text", "EB Garamond", Georgia; UI: … "Segoe UI" …), not bundled font files. On this machine
  neither Tiempos nor a system-wide EB Garamond is installed, so Chrome most likely rendered them in
  the Windows system fonts Georgia and Segoe UI. I did not verify this glyph by glyph.

## Sources

- **careery.pro review of Jobright (2026):** <https://careery.pro/blog/ai-job-search/jobright-ai-review>.
  It is the source for the B03 claim that Jobright's H-1B filter relies on sponsorship language or the
  employer's past sponsorship history. It is a third-party review, credited on screen as "careery.pro
  review, 2026". I opened and checked it before signing FACTCHECK.md.
- **LinkedIn Job Alerts:** a tool I used myself. B02 describes my own experience of it.
- **Jobright:** a tool I used myself. B03 describes its match score, H-1B filter and AI agent as I
  looked at them.
- **My own work, cited in B11:** the Week 1 explainer film (PR #10, commit `aad5723` on branch
  `nishant-u-week-01` of this repo) and my Reallocation Engine recipe and prototype (PR #17 in
  `nikbearbrown/the-reallocation-engine`, head commit `ddcecee`).
- No logos, stock images, footage or music are used. Every picture is a drawn Manim scene or one of the
  two Remotion text bookends.

## What I made

- The seven pitch answers in `PROJECT-BRIEF.md` (Claude only tightened the wording and applied my tense rule).
- The decisions on every draft: the project choice, the show-tell format without the instructor's
  persona, the voice, the beat structure, which beats to keep, the BDEFS terms and the definition of
  "record", the BEND labels and lines, the trims, and the runtime limit.
- The name and wording fixes, including the phonetic spelling "Nee-shaant" after hearing my name
  mispronounced.
- Watching the full film on 2026-10-14 and approving it.
- Checking every FACTCHECK.md row against its source myself, including the careery.pro review, and
  signing it off.

## What Claude contributed

- **Claude in claude.ai** helped me choose the project, and drafted the brief text and the prompts I
  gave Claude Code.
- **Claude Code** wrote `make_sheet.py`, `beat_sheet.json` and `scenes.py`; drafted `SHOTLIST.md`,
  `PROMPTS.md`, `FACTCHECK.md`, `FRICTIONAL.md`, `README.md`, `BUILD-PROMPT.md` and this file;
  wrote the toolkit fixes in `brutalist-fixes.diff`; and ran the audio, the render and every gate.
- **No Claude responses appear in the film.** The narration is my own script, voiced by Kokoro.
