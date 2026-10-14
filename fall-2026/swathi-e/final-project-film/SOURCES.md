# SOURCES

**Swathi Baba Eswarappa** · INFO 7375 · Final Project Pitch Film
Build date: **2026-10-13** · macOS 26.6.2, Apple Silicon (arm64)

---

## 1. My part, and who drafted each file

| Artifact | Description |
|----------|-------------|
| Project concept, "Cite or Refuse" | chosen by me from ideas suggested in a separate Claude chat session; the personal reason is mine |
| `PROJECT-BRIEF.md` | drafted by Claude (chat) from my answers; reviewed and edited by me |
| `TEST-NOTES.md` | my tests and observations (ChatGPT, Gemini and Claude, Oct 9, 2026), written up by Claude (chat) from the results I pasted |
| `beat_sheet.json` narration | original narration drafted by Claude (chat) and approved by me; spoken by a synthetic voice (below); revisions listed in §3 |
| `FRICTIONAL.md` | written by me; Claude (chat) helped organize it and suggested accuracy fixes |
| Week 1 helpers | `Beat` class, `at`/`pin` cue system, `build_mux.py`, `qc_frames.py`, `make_srt.py`, carried over from my Week 1 build |
| Review decisions | I listened to the voice samples and chose the voice and the "AI" spelling, and approved Claude Code's recommendations for the loudness (−19 LUFS) and the 4K master |

## 2. What Claude (chat) contributed

In a separate Claude chat session (not this Claude Code build session), Claude:

- suggested project ideas, from which I chose this one;
- drafted `PROJECT-BRIEF.md`, `TEST-NOTES.md`, `beat_sheet.json` (the original narration)
  and `CLAUDE-CODE-PROMPT.md`;
- located the page 7 passage in the 2025 Instructions for Form 1040-NR;
- wrote the B02 narration revision;
- helped organize `FRICTIONAL.md`.

## 3. What Claude Code (Opus 5.5) contributed

I used Claude Code for the build in this session. Specifically it:

- checked prerequisites and found that `.venv-kokoro` was missing and the toolkit's `./setup`
  stopped early; proposed using the Anaconda Python and four named toolkit gates in place of a
  "render-integrity" check, which I approved;
- wrote `data/facts.json` from `TEST-NOTES.md` and `PROJECT-BRIEF.md`, including the
  per-tool summary of the B05 grid (see §5 for the judgment calls);
- wrote `check_facts.py`;
- wrote the 13 new scenes in `scene.py` and extended the Week 1 `Beat` class: checks after
  every animation, a left/right safe-area check, chrome inside the title-safe area, a
  higher-contrast grey, and a midpoint guard so no animation is mid-flight where the
  toolkit's GATE T samples each beat;
- updated `build_mux.py`, `qc_frames.py` and `build.sh`, and wrote `build/render_all.sh` and
  `build/run_upstream_gates.sh`; rewrote `make_srt.py` to produce short caption cues that
  always show "AI"; added two-pass loudness normalisation to `build_mux.py` at my request;
- listed the Kokoro voices when I asked for a female American English narrator, and voiced
  test samples of five spellings of "AI" for me to choose from (test files since deleted);
- checked the submission against the assignment rubric when I asked. It found that this
  machine's toolkit copy predates the toolkit's current gates, ran those upstream gates, and
  reported three failures (LOUDNESS, MASTER, T). It proposed fixes, and I chose −19 LUFS, a
  3840×2160 24 fps master, and the fixes to B04, B05, B10 and B11;
- ran the narration, renders and every gate, read the rendered frames, and fixed what it
  found: B13 had no drawn picture (Gate A); footer text touched the safe edge (Gate B);
  B10's label ran into its box (found by eye); GATE T failures in B04, B10 and B11;
- drafted `BUILD-PROMPT.md`, this file and `README.md`.

**Narration revisions** (each confirmed by diff; no cuts were needed):
- **B02**: written by Claude (chat) and approved by me, replacing the original second to
  fourth sentences.
- **B08, B09**: "A I" → "AI", my choice after listening to the samples.
- **B08**: "they run one command" → "they will run one command". The future-tense wording
  was proposed by Claude Code to meet the honesty rule, and approved by me.

**What Claude Code did not do:** it did not choose the project, run the chatbot tests, or
write `FRICTIONAL.md`. Every number on screen traces to `TEST-NOTES.md`, `PROJECT-BRIEF.md`
or page 7 of the 2025 Instructions for Form 1040-NR, through `data/facts.json`.

I am responsible for this submission and can explain any part of it.

## 4. Evidence behind the film

| Claim on screen | Source |
|---|---|
| ChatGPT gave $15,750 in one run and $15,000 in another, Oct 9, 2026 | `TEST-NOTES.md`, Results table, ChatGPT Q2 (logged in / logged out) |
| 2025 Instructions for Form 1040-NR, p. 7: $15,750 filing threshold for single students eligible under Art. 21(2) of the U.S.–India treaty | IRS i1040nr.pdf (2025), p. 7, "Do You Have To File?", checked Oct 9, 2026 (`TEST-NOTES.md`) |
| The 2025 instructions were clarified after release | `TEST-NOTES.md`: IRS lists "Clarifications to the 2025 Instructions for Form 1040-NR" |
| B05 grid (exact passage / tax year / declined the refund question), dated Oct 9, 2026 | `TEST-NOTES.md` Results table; derivation per cell in `data/facts.json` → `test_grid` |
| Scope (1 tax year, 1 publication, 10 held-out questions), risk, skills | `PROJECT-BRIEF.md` §4–§7 |
| Reallocation Engine pull request #6 | `PROJECT-BRIEF.md` §7 (link there) |

No chatbot screenshots are shown. Screenshots containing personal details are excluded
from the film and this folder.

## 5. Judgment calls to review

- **B05 grid.** Each cell summarises three questions. Claude's "tax year stated" cell spells
  out **No / No / Partly** (Q1–Q3), at my request. ChatGPT's row covers both its logged-in
  and logged-out runs. The header shows the test date, Oct 9, 2026, because the results come
  from real chatbot answers.
- **B02 wording.** B02 calls page 7's $15,750 the *filing threshold*, and says one run's
  *number matched that figure*. B01 still reports what ChatGPT said, that it was the
  standard deduction.
- **Numbers shown but not spoken:** the date on the B01 cards and B05 header, the
  2023/2024/2025 tabs on the B03 stack, and "#6" on the B12 PR card.
- **Simplified from the beat-sheet mechanics:** B06 drops the "versioned store" box (B07
  covers versions); B09 omits course-week tags because no source says which week each skill is from.
- **B08's `$ ./demo`** is a placeholder command inside the labelled mock-up.

## 6. Tools and licences

| Tool | Version | Licence | Role |
|------|---------|---------|------|
| Brutalist toolkit (local copy) | commit `29ba0e8` (2026-09-15) | no `LICENSE` file at root as of this commit | `generate_audio_kokoro.py` used unmodified; Gates A, W, B, V from `runtime/qc/` |
| Brutalist toolkit (upstream gates) | `origin/main` commit `519fcbb` (2026-10-12) | as above | GATE LOUDNESS, MASTER, T, SRT, SHARPNESS, run unmodified by `build/run_upstream_gates.sh` |
| [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) | weights `v1.0` | **Apache-2.0** | narration voice `af_heart` (female American English; replaced `am_michael` at my request) |
| [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) | 0.6.1 | MIT | ONNX runtime wrapper for Kokoro |
| [Manim Community](https://www.manim.community/) | v0.18.1 | MIT | visual engine |
| [FFmpeg](https://ffmpeg.org/) | 9.0.1 | LGPL-2.1+ | mux, concat, loudness, verification |
| [eSpeak NG](https://github.com/espeak-ng/espeak-ng) | 1.52.0 | GPL-3.0 | phonemizer backend for Kokoro |
| onnxruntime | 1.30.0 | MIT | Kokoro inference |
| NumPy | 2.2.6 | BSD-3-Clause | array maths |
| Pillow | 10.4.0 | MIT-CMU (HPND) | frame analysis in the gates |
| SciPy | 1.18.1 | BSD-3-Clause | GATE T text-run detection |
| Menlo | macOS system font | Apple | on-screen type |

No third-party images, video, music or sound effects are used; every picture is drawn by
`scene.py`.

**Free pipeline only.** No paid generation, no API keys, no media account, no upload.
Total generation cost reported by the Kokoro engine: **$0.00**.
