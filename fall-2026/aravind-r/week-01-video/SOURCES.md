# SOURCES — Same Odds, Smaller Numbers

## What the video explains, and where it comes from

- **Concept:** Chapter 1, Part 2, "The subtraction that changes nothing important": why subtracting the maximum score changes the intermediate weights but not the softmax distribution.
- **Reference code:** `lessons/01-randomness-and-first-prompts/code/main.py` (course repo, commit `149c8e7`). `verify_numbers.py` contains a verbatim copy of its `probabilities()` function; both print the same result for `[1, 2, 3]`.

## Evidence I produced (Aravind Ravi)

| File | What | How |
|---|---|---|
| `evidence/main_py_output.txt` | `main.py` output | I ran it in my own terminal from the course repo root, 2026-09-27, Python 3.13.0 (macOS, Homebrew) |
| `evidence/verify_numbers_output.txt` | Every number shown on screen | I ran `verify_numbers.py` myself, 2026-09-27 00:59 EDT, Python 3.13.0 |
| `evidence/b00_claude_reply.txt` | The Claude reply shown in the cold open | I sent the B00 prompt to a fresh Claude Code session (v2.1.7, model Sonnet 4.5) on 2026-09-27 and copied its final message. Session IDs and account details are omitted. |
| `evidence/exp_sweep_output.txt` | The exp(x) / exp(−x) sweeps shown in B07 and B08 | `exp_sweep.py`, run by Claude Code on my machine, 2026-09-27 13:21 EDT, Python 3.13.0 (re-run with `python3 exp_sweep.py`; the values are deterministic) |

Claude Code had run both scripts once earlier (2026-09-26, same Python), with identical numbers. My own runs above replaced them as the recorded evidence.

## What I decided and verified

- Chose the concept, and approved the narration on 2026-09-27 after two changes I asked for or accepted:
  - Replaced the toolkit's "Liam, in for Bear" persona with my name and an explicit disclosure that the voice is synthetic.
  - Corrected B04 from "about sixteen digits" to "fifteen decimal places". The B00 Claude reply said 15; a re-check showed the largest difference, 1.1 × 10⁻¹⁶, is in the 16th decimal place.
- Re-ran both evidence scripts myself (above) and ran the B00 prompt myself.
- Watched each review cut and asked for changes (see FRICTIONAL.md): my name instead of the Liam persona, B01's unfinished typing, the outro handle, more reading time, a synthesis page, a title card, section markers, then a second full pass for polish and animation.

## What Claude contributed

- **Claude (separate chat):** drafted `beat_sheet.json` (the narration and visual plan), `verify_numbers.py` and `fill_math.py`.
- **Claude Code (Opus 5.5, this build, both iterations):** set up the toolkit and diagnosed the install failures in FRICTIONAL.md. It wrote `scenes.py`, FACTCHECK.md, SHOTLIST.md, PROMPTS.md, BUILD-PROMPT.md and this file, and drafted README.md and FRICTIONAL.md entries for me to review. It edited `beat_sheet.json` at my request (persona, the B00 lines, the B04 correction). It generated the audio, ran the build and looked at rendered frames for layout defects.
- **Claude Code (Sonnet 4.5, fresh session):** the B00 reply, used verbatim.

## Iteration 2 (2026-09-27): what changed

- Rebuilt in Manim, inside `scenes.py`: B00 (Claude composer), B02, B05, B06, BVDT and BHTF. The stock Remotion components had fixed stage colours, fixed typing speed or fixed small type, and the brief ruled out editing the toolkit.
- New evidence script `exp_sweep.py` for the B07/B08 sweeps. `scenes.py` reads every on-screen number from `evidence/` (map in `_qc/phase2/NUMBERS.md`). The stacked-bar widths were pixel-checked against the evidence values (`_qc/phase2/BAR-MEASURE.txt`, not committed; `_qc/` is ignored).
- `add_holds.py` (per-beat reading time) and `add_markers.py` (section markers) are my build helpers, written by Claude Code.
- **Sound:** none. No sound effects were added, synthesized or downloaded.

## Tools and third-party assets (all free, local)

| Asset | Use | Licence |
|---|---|---|
| brutalist.art toolkit @ `cd4bf20` (github.com/nikbearbrown/brutalist.art) | Pipeline, Remotion scene components, outro mascot art | Instructor's public course toolkit |
| Kokoro-82M via kokoro-onnx 0.6.1, voice `am_onyx` | Synthetic narration (disclosed in B00) | Apache 2.0 |
| espeak-ng 1.52 (Homebrew) | Phonemizer backend for Kokoro | GPL-3.0 |
| Manim Community 0.18.1 | B03, B04, B07, B08 | MIT |
| Remotion | Bookends, equation and predict beats | Remotion License (free for individuals) |
| matplotlib 3.11 (mathtext) | Equation typesetting for B02/B05 (no LaTeX) | Matplotlib License (BSD-style) |
| faster-whisper | Word timing for cue alignment and captions | MIT |
| FFmpeg 9.0 | Assembly | LGPL/GPL |
| EB Garamond (bundled with toolkit) | Serif type | SIL Open Font License 1.1 |
| Menlo (macOS system font) | Numbers and recorded output in Manim beats | Apple system font, rendered locally |

No stock footage, no downloaded images, no paid services, no generated imagery, and no voice cloning.

## Toolkit modification

The stock outro card (`ClaudeTitleOutro`) hard-codes the `@NikBearBrown` handle. The course's Brutalist guide says a student video must not imply an official endorsement, so I patched the component to take an optional `handle` prop (3 lines; `toolkit-patches/ClaudeTitleOutro-handle.patch`). The card now reads "Aravind Ravi · INFO 7375". The mascot art is still the toolkit's.
