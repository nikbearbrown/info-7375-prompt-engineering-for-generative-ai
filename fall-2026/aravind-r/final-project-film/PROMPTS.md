# PROMPTS — Readback

No generative media: no image, video or voice-cloning prompts. Narration is the free local Kokoro voice `am_onyx`, synthesized from my approved script. Every visual is a deterministic Manim or Remotion render.

## Prompts behind real material shown in the film

**Recap feature (B08 excerpt).** The system prompt is `case-study/constructed/recap-system-prompt.md` (everything below its `---` line). `case-study/run_feature.py` sent it with `claude -p --system-prompt … --tools "" --output-format json` and each meeting's `transcript.txt` as the input. The outputs, with date, Claude Code version and model, are in `case-study/outputs/feature-run/`.

No other Claude response appears on screen.
