# SOURCES — Expected 665.24, Observed 630

INFO 7375 Week 1 explainer video by Prathamesh P. Prepared 2026-09-27. Crediting format follows the course's `prerequisites/brutalist-video-sources.md`: what was used, from which revision, what was retained, and corrections applied. Every licence below was read from a local licence file, font metadata or package metadata, and the source is named in each row. Where none was found, the row says **licence not found**. Nothing here is a guess.

## What I used — course material

Course repository: [nikbearbrown/info-7375-prompt-engineering-for-generative-ai](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai), cloned 2026-09-27 at commit `b293224d5c6f078ce5f793c7ea0f73c9af3f19a0`.

| Source | Path in the course repo | What the video retains |
|---|---|---|
| Chapter 1 code | `lessons/01-randomness-and-first-prompts/code/main.py` | Run unmodified on Python 3.11.9: every probability and count on screen (`main_output_2026-09-27.txt`). Lines 9, 14–17, 19, 22–24 shown verbatim in B02. `probabilities()` and `sample()` imported by `evidence/seed7_sequence.py` and the B08 snippet |
| Chapter 1 text | `chapters/01-randomness-and-first-prompts.md` | Line 247 (no fixed quota, B04), line 249 (665.24 is an expected count, not an integer, B03), line 259 (two questions, B05), line 261 (acceptance criterion first, B07). Paraphrased in my narration, not quoted on screen |
| Chapter 1 tests (checked, not used) | `lessons/01-randomness-and-first-prompts/code/tests/test_main.py` | Not cited: `test_04` tests `sample([1, 2])`, not the `[1, 2, 3]` run in the video |
| Assignment brief | Canvas, pasted into `ASSIGNMENT.md` | Requirements: one concept, real numbers, constructed items labelled, one stated boundary |
| Course guides | `prerequisites/brutalist-video.md`, `prerequisites/brutalist-video-sources.md`, `prerequisites/frictional.md`, `prerequisites/github-submission.md`, `ASSESSMENT.md` | Workflow (venv, 1080p final with `--out`, avoid equation beats, disclose synthetic narration, no instructor persona), this file's format, FRICTIONAL.md format |

## What I made

| Item | File(s) | Notes |
|---|---|---|
| Concept choice, takeaway and boundary | `PEDAGOGY.md`, `README.md` | Chosen from the assignment's list |
| Narration (351 words) | `beat_sheet.json` `narration_text` | Drafted with Claude in this session. The B03, B06 and B07 wording edits were proposed by a separate Claude chat, and the B07 cut and the B08 folder path were suggested by Claude Code. I reviewed and approved each one before signing GATE P. **GATE P signed by me** (`PEDAGOGY.md`, SHA-256 `8afc5b04…c358c`) |
| Build decisions | `FRICTIONAL.md` Entries 6–13 | No Claude interface, no instructor persona, counters only, voice `af_bella`, all approved fixes |
| Review of the cut | `FRICTIONAL.md` Entry 13 | I watched the review cut with sound twice |
| Beat plan, visuals, evidence scripts | `beat_sheet.json`, `scenes.py`, `evidence/seed7_sequence.py`, `evidence/b08_your_turn_snippet.py` | Written by Claude to my specification and approved by me (see below) |

## What Claude contributed

- **This Claude Code session (2026-09-27, model Claude Opus 5.5):**
  - Setup and diagnosis on native Windows, including three local toolkit patches (see below).
  - Running the course code and the evidence scripts.
  - Drafting the narration, which I edited and signed.
  - Writing `beat_sheet.json`, `scenes.py`, `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`, `CHECKS-REPORT.md`, this file and `README.md`.
  - Generating audio, rendering, and reading the QC output.
  - Recording my decisions in `FRICTIONAL.md`, `PEDAGOGY.md` and `BUILD-PROMPT.md`.

  Claude signed no gate. `PEDAGOGY.md`'s verdict is mine, recorded verbatim.
- **A separate Claude chat (planning help):** A separate Claude chat (claude.ai) helped me plan the whole project. It explained the assignment and rubric, recommended the concept after I shared my real main.py output (it first suggested max-subtraction, then recommended expected versus observed once it saw the output), guided my setup in WSL and then on native Windows, suggested the seed sweep for the Your Turn beat, proposed three narration edits (B03, B06, B07) that I reviewed and adopted before signing GATE P, and drafted the instructions I gave Claude Code. It also drafted the wording of my "Why this concept" sentence and the personal fields in FRICTIONAL.md from what I told it during the chat; I reviewed them and confirmed they are accurate. I made all decisions.
- No Claude response appears anywhere in the video, and no Claude interface is shown.

## Toolkit

[nikbearbrown/brutalist.art](https://github.com/nikbearbrown/brutalist.art), cloned 2026-09-27 at commit `cd4bf20904be4e7d63babd9622b17963c2361b27`, with **three local, uncommitted patches** (diffs in this folder):

| Patch | File | Why |
|---|---|---|
| `brutalist-setup-local-patch.diff` | `setup` | ElevenLabs guard tripped on the toolkit's own `youtube/` files (upstream bug) |
| `brutalist-compile-local-patch-cumulative.diff` (= `brutalist-compile-local-patch.diff` + `brutalist-compile-timecode-local-patch.diff`) | `runtime/scripts/compile.py` | Windows path escaping in ffmpeg `drawtext`; review-cut timecode moved inside title-safe |
| `brutalist-remotion-npx-local-patch.diff` | `runtime/scripts/remotion_scenes.py` | `npx` lookup on Windows (`shutil.which`) |

Toolkit components used in the video: `BrutalistHesitantWriter` (B01), `compile.py`, `generate_audio_kokoro.py`, the QC gates. The Claude palette values in `scenes.py` come from `runtime/remotion/src/tokens/claude.ts`.

## Third-party assets and licences

| Asset | Version / file | Used for | Licence | Where the licence was read |
|---|---|---|---|---|
| Course code (`main.py`) | course repo `b293224` | all numbers; B02 excerpt | MIT (Copyright 2026 Rohit Ghumare); adaptation by Nik Bear Brown | course repo `LICENSE`, `ATTRIBUTION.md` |
| brutalist.art toolkit | `cd4bf20` + 3 local patches | build pipeline, B01 component | **licence not found** | no LICENSE file in the repo root; none stated in README.md, HOW-TO.md or CLAUDE.md |
| `BrutalistHesitantWriter` origin | `runtime/remotion/src/scenes/BrutalistHesitantWriter.tsx` | B01 | **licence not found**. The file says: "Source: brik/base44 auto-converted canvas component `typing-animation-mnzzraks`. Author unknown" | component header comment |
| EB Garamond | `runtime/fonts/EB_Garamond/static/EBGaramond-Regular.ttf` (also installed per-user) | all serif text | SIL Open Font License 1.1, Copyright 2017 The EB Garamond Project Authors | `runtime/fonts/EB_Garamond/OFL.txt` |
| PT Mono | `runtime/fonts/PT_Mono/PTMono-Regular.ttf` | code and file listings (B02, B04, B06, B08) | SIL Open Font License 1.1, Copyright 2011 ParaType Ltd. (Reserved Font Names "PT Sans", "PT Serif", "PT Mono", "ParaType") | `runtime/fonts/PT_Mono/OFL.txt` |
| Oswald | `Oswald-Variable.ttf`, Version 4.103 (downloaded by `setup`, installed per-user) | **not used in this video** (installed by setup) | SIL Open Font License 1.1, Copyright 2016 The Oswald Project Authors | the font's own name table (IDs 0, 13, 14); no licence file was downloaded with it |
| Segoe UI | Windows system font | B01 corner banner "CONSTRUCTED EXAMPLE" (via `CLAUDE_FONT.ui`) | **licence not found** (Windows system font; no licence file checked locally) | — |
| Kokoro model | `runtime/models/kokoro/kokoro-v1.0.onnx` (downloaded by `setup` from the kokoro-onnx GitHub releases, `model-files-v1.0`) | narration | Apache 2.0, as stated by kokoro-onnx: "kokoro model: Apache 2.0" | `kokoro_onnx-0.6.1.dist-info/METADATA`, License section. No licence file ships with the model |
| Kokoro voices (`af_bella`) | `runtime/models/kokoro/voices-v1.0.bin` | narration voice | **licence not found** for the voices file specifically | not stated in kokoro-onnx metadata; no licence file alongside |
| kokoro-onnx | 0.6.1 | TTS runtime | MIT, Copyright 2025 github.com/thewh1teagle | `kokoro_onnx-0.6.1.dist-info/licenses/LICENSE` |
| phonemizer | 3.4.0 | TTS text-to-phoneme | GPL v3 or later | package metadata (License + classifier) |
| espeakng-loader | 0.2.4 | TTS phoneme backend | **licence not found** | no licence file or licence field in its dist-info |
| onnxruntime | 1.30.0 | TTS inference | MIT | package metadata |
| Manim Community | 0.18.1 | B00, B02–B09 | MIT | package metadata |
| ManimPango | 0.5.0 | Manim text | MIT | package metadata |
| Pillow | 10.4.0 | toolkit images / QC | HPND | package metadata |
| Remotion | 4.0.486 | B01 render | Remotion License. Free License for individuals ("Individuals and small companies are allowed to use Remotion to create videos for free") | `runtime/remotion/node_modules/remotion/LICENSE.md` |
| Chrome Headless Shell | downloaded by Remotion 2026-09-27 | Remotion's renderer | Chromium licence file (aggregated third-party notices), not reproduced here | `node_modules/.remotion/chrome-headless-shell/win64/chrome-headless-shell-win64/LICENSE.headless_shell` |
| FFmpeg | 9.0.2 full_build (gyan.dev) | encoding and compile | GPL v3 or later | `ffmpeg -L` |

No stock images, music, video clips or generative media are used. Every visual is rendered locally from the files in this folder.

## Corrections and disclosures

- The narration voice is synthetic (Kokoro `af_bella`), not mine. It's disclosed on every beat.
- B01's typed sentence is a **constructed example**, labelled on screen. B07's axis and empty slots are **constructed**, labelled on screen; only the −35.24 point is real.
- "Computed" values (665.24, 90.03, 244.73, the gaps, 0.630) are arithmetic on main.py's output, labelled on screen.
- The ai-explainer skill's default instructor persona, channel handle and logo were deliberately not used. The course docs say a synthetic narrator must not imply the student is the instructor or an endorsement.
- brutalist.art's HOW-TO.md says the Kokoro model ships in the repo. It doesn't (setup downloads it). The course's `brutalist-video-sources.md` notes the same.
