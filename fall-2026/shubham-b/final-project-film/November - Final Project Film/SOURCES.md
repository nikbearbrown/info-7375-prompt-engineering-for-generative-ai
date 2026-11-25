# SOURCES — A11yProof project film

What I used from others, where every number came from, what I made, and what Claude contributed. Paths are relative to the packet root.

## What I used (third-party), with licences

Licences below were read from files in the clone or the venv metadata, not guessed.

| Item | What it is | Licence (as found) | Where checked |
|---|---|---|---|
| brutalist.art toolkit (Prof. Nik Bear Brown) | The video toolkit the film is built with: https://github.com/nikbearbrown/brutalist.art | Licence not found in the clone. There is no LICENSE file at the top level or one level down. The README says "Free by default" (Kokoro, Manim, Remotion, no account) but that is not a licence grant. Used as course material, with the professor's toolkit as the assigned tool. | `vendor/brutalist.art/` |
| Kokoro model `kokoro-v1.0.onnx` and voices `voices-v1.0.bin` (voice `am_onyx`) | Local text-to-speech model and voice pack | Apache 2.0 for the model, per the kokoro-onnx package metadata. No separate licence file ships next to the model files. | `vendor/brutalist.art/runtime/models/kokoro/`, kokoro-onnx METADATA in `vendor/brutalist.art/.venv` |
| kokoro-onnx 0.6.1 | Python runner for the Kokoro model | MIT (LICENSE file in the dist-info: Copyright 2025 thewh1teagle) | `vendor/brutalist.art/.venv/lib/python3.14/site-packages/kokoro_onnx-0.6.1.dist-info/` |
| espeak-ng, via espeakng-loader 0.2.4 | Phoneme engine Kokoro uses (shared library and data) | Licence not found in the clone. The espeakng-loader metadata states no licence and ships no licence file. | `vendor/brutalist.art/.venv/.../espeakng_loader-0.2.4.dist-info/` |
| Remotion | React-based video renderer | Remotion's own licence: free for individuals and small companies (even commercial use); a company licence is needed for for-profit organisations above a size threshold. I am an individual student, so the free licence applies. | `vendor/brutalist.art/runtime/remotion/node_modules/remotion/LICENSE.md` |
| Fonts in the Claude palette | `CLAUDE_FONT` in `runtime/remotion/src/tokens/claude.ts` names "Tiempos Text" first, then "EB Garamond" as the bundled serif fallback; the UI stack is system fonts (SF Pro, Segoe UI, Helvetica Neue) | Tiempos Text is not bundled, so the film falls back to EB Garamond (SIL Open Font License 1.1, `runtime/fonts/EB_Garamond/OFL.txt`). Other bundled fonts in the toolkit: Inter (OFL, `runtime/fonts/Inter/OFL.txt`), Lato and Montserrat (OFL, in `runtime/remotion/public/fonts/`). System fonts are not redistributed. Which exact font each frame used I did not check frame by frame. | `vendor/brutalist.art/runtime/fonts/`, `vendor/brutalist.art/runtime/remotion/public/fonts/` |
| Pixel mascot in the outro | Animated pixel mascot drawn by `MascotSVG` in `ClaudeMascotScene`, used by `ClaudeTitleOutro` | Comes from the toolkit. Licence not found in the clone (no licence file covers it). The mascot is Claude-branded artwork; I did not check Anthropic's terms for it. | `vendor/brutalist.art/runtime/remotion/src/scenes/ClaudeTitleOutro.tsx` |
| ffmpeg 9.0.2 | Encoding and joining video/audio | Local build at `/opt/homebrew/bin/ffmpeg`, configured with `--enable-gpl` and `--enable-version3`, so GPL v3 or later. I did not open a licence file; this is from the build flags. | `ffmpeg -version` |

## Data sources for every number

Copied from `youtube/fixproof-pitch/FACTCHECK.md`, checked 2026-11-23 via web search. "Primary" means the publisher's own page appeared in results; "secondary" means news or law-firm coverage of it. Re-open each link before submitting.

| # | Claim in film | Figure | Source | Confidence |
|---|---|---|---|---|
| 1 | Top 1M home pages with detectable WCAG 2 failures, 2026 | 95.9% (up from 94.8% in 2025) | WebAIM Million 2026 — https://webaim.org/projects/million/ | secondary (several outlets agree; open the report) |
| 2 | Average errors per home page, 2026 | 56.1 | same | secondary |
| 3 | ADA digital accessibility lawsuits filed in 2025 | 5,114 (web + app + video, Jan 1 – Dec 15 2025) | UsableNet 2025 Year-End Report — https://info.usablenet.com/2025-year-end-digital-accessibility-lawsuit-report-plain-text | primary |
| 4 | US adults with a disability | "up to 1 in 4" | CDC, Disability Impacts All of Us — https://www.cdc.gov/disability-and-health/articles-documents/disability-impacts-all-of-us-infographic.html | checked against the CDC page by Shubham, 2026-11-23. Spoken in B04. |
| 5 | Automated testing catches ~57% of issues (by issue volume) | 57.38% | Deque, 2021 study — https://www.deque.com/blog/automated-testing-study-identifies-57-percent-of-digital-accessibility-issues | primary, but vendor's own study |
| 6 | FTC ordered accessiBe to pay $1M over claims its AI widget makes sites WCAG-compliant | $1M; proposed Jan 3 2025, final order Apr 22 2025 | FTC — https://www.ftc.gov/news-events/news/press-releases/2025/04/ftc-approves-final-order-requiring-accessibe-pay-1-million | primary (URL) |
| 7 | LLM repair research: AccessGuru reduced violation score up to 84% | up to 84% avg decrease | AccessGuru, ASSETS '25 — https://arxiv.org/abs/2507.19549 | primary (abstract) |

The targets shown in the film (at least 80% of held-out violations fixed, 0 new violations, 0 broken layouts, at least 7 of 10 PRs accepted, at least 5 planted failure cases) are my proposals, labelled as targets, not facts.

## What I made

My choices, in the order they happened:

- Chose to pitch an agentic system, and asked for options that read as real impact for SWE and FDE roles.
- Picked idea A (the accessibility repair agent) over the dependency-patch, incident, leaked-secret and invoice-fraud ideas.
- Required that the project stay isolated from my other course work.
- Renamed the project from FixProof to A11yProof, because the old name did not say it was about accessibility.
- Replaced the professor's handle on the outro and table cards with my name.
- Confirmed the course name on the title card.
- Reviewed the film.

## What Claude contributed

Claude Opus 5.5 (Claude Code, 2026-11-23):

- The project options I chose from.
- Research and fact-check (`youtube/fixproof-pitch/FACTCHECK.md`).
- The beat sheet script `youtube/fixproof-pitch/build_sheet.py`, which holds all narration and on-screen text.
- `youtube/fixproof-pitch/tts.py`, the wrapper that runs Kokoro from a short path.
- The GATE F paperwork (FACTCHECK.md, SHOTLIST.md, PROMPTS.md).
- Rendering and fixes.
- An inline review (`youtube/fixproof-pitch/REVIEW.md`). It is not independent: it ran in the same session as the build.
- The `handle` prop edit to two toolkit scenes (`ClaudeTitleOutro` and the table scene).

## Not included, on purpose

- The 2.4 GB toolkit clone is not part of the packet. Rebuild it by following `BUILD-PROMPT.md`.
- No AI-generated video and no paid services were used (no Higgsfield).
- Nothing else.
