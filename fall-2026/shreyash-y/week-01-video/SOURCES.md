# SOURCES.md

Shreyash Yadav · INFO 7375 Week 1 explainer · 2026-09-21

---

## What I used (course material)

| Thing | Where | Licence | How it's used |
|---|---|---|---|
| `main.py` — the softmax/sampling reference implementation | `lessons/01-randomness-and-first-prompts/code/main.py`, [nikbearbrown/info-7375-prompt-engineering-for-generative-ai](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai) @ `a0d8a1e` | MIT | Imported **unmodified** by `evidence/run_evidence.py`. Every probability in the video comes out of it. Lines 9 and 14–17 are quoted on screen in B02. |
| `docs/en.md` — the Week 1 lesson | same repo | MIT | Read for framing. Not quoted on screen. |
| `prerequisites/frictional.md` | same repo | MIT | The format `FRICTIONAL.md` follows. |

## What I used (tools)

| Thing | Version / source | Licence | Role |
|---|---|---|---|
| **Brutalist** video toolkit | [nikbearbrown/brutalist.art](https://github.com/nikbearbrown/brutalist.art) @ `6a8380a` | no LICENSE file in the repo at this commit — used as the course directs | The whole pipeline: beat sheet → audio → render → conform → QC gates |
| **Kokoro-82M** (`kokoro-onnx`) voice `am_onyx` | model fetched by `./setup --install` | Apache-2.0 (model), MIT (`kokoro-onnx` wrapper) | All narration. Local, free, no key, no account |
| **Manim Community** v0.18.1 | pip | MIT | The five mechanism scenes (B03–B07) |
| **Remotion** ^4.0.0 | bundled in the toolkit | Remotion licence — free for individuals and small companies; **not** OSI open source | The six chassis beats (B00–B02, BVDT, BHTF, BOUT) |
| **EB Garamond** | bundled at `runtime/fonts/EB_Garamond` | SIL Open Font License 1.1 | On-screen serif |
| **Menlo** | macOS system font | Apple system font, not redistributed | On-screen monospace (numbers) |
| **FFmpeg** 8.1.2 | brew | LGPL/GPL | Conform, mux, probe |
| `pkgconf` | brew | ISC | Build dependency for `pycairo` (see `FRICTIONAL.md` §3) |

**Cost: $0.00.** No paid generation, no API keys, no media accounts, no upload.
Higgsfield was never logged in; no AI-video beats exist in this reel.

## What I made

- The concept choice, the argument, and the script (all narration text in `beat_sheet.json`).
- `evidence/run_evidence.py` — generates every on-screen number from the course
  `main.py`, including the cross-interpreter comparison and the
  compensated-summation probe.
- `scenes.py` — the five Manim scenes, the `@paced` timing contract, the
  evidence-lookup chain.
- `beat_sheet.json`, `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`,
  `FRICTIONAL.md`, `BUILD-PROMPT.md`, `build.sh`, this file.
- The finding in B06/B07 (the ±1 ULP gap and its interpreter dependence) is
  mine — it is not stated in the lesson.

## What Claude contributed

Model: Claude Opus 5, via Claude Code. Two sessions: 2026-09-21 (build) and 2026-09-27 (submission check against the Canvas page).

**Wrote most of the code I specified.** The Python and Manim in this folder was
largely typed by Claude against my design decisions — scene layouts, the
evidence-generator structure, the pacing mechanism, and all of the prose
documents drafted from my notes and from real command output.

**Proposed one substantive hypothesis, which I did not accept on its word.**
When I showed it that the ULP vector differed between two interpreters, it
immediately proposed compensated (Neumaier) summation in CPython ≥ 3.12. That
is the kind of fluent, plausible, unverified claim this chapter is about, so I
had it construct a behavioural probe instead —
`sum([1e100, 1.0, -1e100, 1.0])`, which returns `2.0` on 3.14.6 and `1.0` on
3.11.15 and 3.9.6. **The probe is what appears in the video.** The explanation
is a caption on a measurement, not the evidence itself.

**Did the toolkit spelunking.** Finding why GATE A rejected the scenes (it
copies `scenes.py` alone and calls `construct()` without `setup()`), and why
the Manim stage silently did nothing (the scene-collector regex requires a
literal `(Scene)` base), was Claude reading the toolkit's source.

**What I rejected or changed:**

- Its first B04 drew the cancellation strike-throughs at hard-coded
  coordinates. On the rendered frame they struck the wrong glyphs. I caught it
  by pulling a frame, and the fix — making the factor *fade out* rather than be
  crossed out — is a better visual than either of us started with.
- It initially wrote the reel in the Brutalist house persona, with
  "this is Liam, in for Bear" and the `@NikBearBrown` folder chip, because that
  is the toolkit's documented default (IN-FOR-BEAR LAW). **I removed it.** This
  is coursework, the explanation is mine, and dressing it as another channel's
  content would be a small false claim in the one assignment that is about not
  making those. The chip reads `INFO 7375`; the greeting persona is my own
  name. This is a deliberate, documented deviation from the skill's default.
- It suggested showing a Claude response on screen. There isn't one, because I
  didn't use one as evidence for anything, and manufacturing a transcript for
  texture would fail this assignment on its own terms.
- Late check: the toolkit's cold-open chassis renders a Claude *composer*, and
  with its default props it showed a model chip ("Fable 5") and lines beneath
  the card that could be read as a Claude reply — for a conversation that never
  happened. I blanked the model and effort chips, labelled both composer beats
  `RECONSTRUCTED INTERFACE` on screen, and rewrote the lines to state in view
  that they are quoted from `main.py`. A depicted UI is a constructed
  illustration and this assignment requires it to say so.

**My estimate of the code contribution split:** Claude wrote roughly 80% of the
lines; the design, the numbers that had to appear, the verification standard,
and every decision about what the video claims are mine. I can explain any line
in `scenes.py` and `run_evidence.py`, and the FRICTIONAL log records where my
understanding actually changed.

## Third-party media

**None.** No stock footage, no stills, no music, no screen recordings, no
AI-generated imagery, no logos other than the toolkit's own chassis. Every
frame is generated from this folder's `scenes.py` and the Brutalist Remotion
components.

## Narration disclosure

The voice is **synthetic** — Kokoro `am_onyx`, generated locally. It is not my
recorded voice and is not presented as one. The words are mine.

## Style and standards

- Python: PEP 8, standard library only in `run_evidence.py`.
- The one hard rule I set myself: **no figure is typed into a scene by hand.**
  `scenes.py` reads `evidence/evidence.json`; if a number changed, the frame
  changes with it. See `FACTCHECK.md`.
