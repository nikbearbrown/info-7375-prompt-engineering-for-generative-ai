# SOURCES — cite-the-line-project-film

## What I used
- **Brutalist toolkit** (https://github.com/nikbearbrown/brutalist.art, commit `b21f6253a336098f3f55847a9525ae6868ccbdb7`), `show-tell` skill, its isometric drawing kit, Remotion bookends, and quality gates. No LICENSE file in the checkout; used for INFO7375 coursework as the assignment directs.
- **Local toolkit patch** `outro-handle.patch` (from my pitch film): optional `handle` and `hideMascot` props on `ClaudeTitleOutro`, so the outro shows my name, not the instructor's hard-coded credit.
- **Kokoro TTS** (`kokoro-onnx`, voice `am_onyx`), run locally. The narration is a **synthetic voice reading a script written in my first person**, not a recording of me. Kokoro-82M weights: Apache 2.0.
- **Manim Community 0.18.1** and **Remotion**, installed by the toolkit. Fonts bundled by the toolkit under the SIL Open Font License.
- **Chen et al., "Automatic Root Cause Analysis via Large Language Models for Cloud Incidents"**, arXiv:2305.15778 (read 2026-11-22). Source of the RCACopilot description and the "up to 0.766" accuracy figure, shown on screen as "up to 77%, per Microsoft Research".
- **Datadog Bits AI SRE documentation** (read 2026-10-09). No logos or screenshots used.

## What I made
- The project, its decisions (including adding the human gate for the final project's agentic requirement), and approval of every line of narration.
- The evaluation criteria in APPENDIX.md (what counts as working and not working).

## What Claude contributed
- Restructured my pitch into the assignment's four parts and drafted the narration, which I approved.
- Found the RCACopilot paper as a second real alternative; I read it before it went into the film.
- Wrote `make_sheet.py`, the 18 Manim scenes (`scenes_body.py`), FACTCHECK.md, SHOTLIST.md, PROMPTS.md, APPENDIX.md, README.md, and this file, and adapted my helper scripts.
- No Claude response is shown on screen in the film.

## Third-party assets
None beyond the toolkit's bundled drawing kit, components, and fonts. No stock images, music, or footage.
