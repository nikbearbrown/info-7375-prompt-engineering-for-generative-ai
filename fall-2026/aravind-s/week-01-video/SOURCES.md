# SOURCES

## What I used

- **Course repository** `nikbearbrown/info-7375-prompt-engineering-for-generative-ai`, commit `24f4af3` (MIT License):
  - `lessons/01-randomness-and-first-prompts/code/main.py`: `probabilities()`, run unchanged. Beat B03 shows lines 9-17, with lines 10-13 (input checks) elided and labelled.
  - `chapters/01-randomness-and-first-prompts.md`, section "Three scores are not yet three chances": the concept, the divide-by-sum contrast, and the "exact arithmetic" limit.
  - `lessons/01-randomness-and-first-prompts/docs/en.md`: the point that softmax probabilities describe sampling, not calibrated correctness (used in B07).
- **Brutalist toolkit** `nikbearbrown/brutalist.art`, commit `cd4bf20`: pipeline, QC gates, Kokoro audio script, word alignment, compile.
- **Manim Community 0.18.1** (MIT): every visual in the video.
- **Kokoro-82M** voice model (Apache-2.0) via the kokoro-onnx model files v1.0, voice `am_onyx`: synthetic narration, generated locally.
- **faster-whisper 1.2.1** (MIT): word timings, so values appear when spoken.
- **Fonts:** EB Garamond (SIL Open Font License, bundled with the toolkit) and Menlo (macOS system font, used only for rendering).
- **No third-party images, footage, music, or sound effects.**

## What was made for this video

- `evidence/softmax_steps.py` and its saved outputs `evidence/softmax_steps_output.txt` and `evidence/main_py_output.txt`
- `beat_sheet.json`: the narration and visual plan, 9 beats
- `scenes.py`: 9 Manim scenes
- `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`, `BUILD-PROMPT.md`, `README.md`, `SOURCES.md`, `FRICTIONAL.md`
- The rendered mp4

## Who did what

**Claude (Claude Code in the Claude desktop app, model Claude Opus 5.5), at my request:**

- Read the Canvas brief, the syllabus, the course repo, and the Brutalist docs.
- Proposed and picked the concept after checking which concepts classmates had already posted.
- Wrote `evidence/softmax_steps.py` and ran it together with the lesson's `main.py`.
- Wrote the narration, the beat sheet, and all nine Manim scenes.
- Installed the toolkit and its dependencies and debugged the build; the problems are logged in FRICTIONAL.md.
- Ran every QC gate, rendered the video, and wrote the first drafts of these documents.

**Me (Aravind Sundaravadivelu):**

- Set up the course environment with Claude's guidance: I ran the PATH fix, the fork and clone, and `validate_course.py` in my own terminal.
- Approved creating `~/.claude/settings.json` so Claude Code would use Python 3.12.
- Asked Claude to build the video end to end, in line with the course policy that AI assistance is allowed and expected, and said I would study it before submitting.
- Watched the final cut on 2026-09-26. I did not edit the script, code, or scenes myself.
- Re-ran `lessons/01-randomness-and-first-prompts/code/main.py` myself and confirmed that its probabilities (0.0900, 0.2447, 0.6652 to 4 places) match the video. Claude ran `evidence/softmax_steps.py` and checked every other on-screen number against `evidence/`.
- Asked Claude to write the FRICTIONAL.md reflection and this section from our session record.

## Synthetic narration

The narrator is Kokoro's synthetic `am_onyx` voice. It is not my voice or the
instructor's, and it is not an endorsement. The video says so on screen in B00.

## No Claude output is shown

The video does not show or quote any Claude response. Every number on screen
comes from running the lesson's code, as recorded in `evidence/`. The only
constructed inputs are the scores `[1, 2, 3]` and `[-1, 2, 3]`, and the
divide-by-sum rows, which are labelled on screen as "NOT the lesson's rule".
