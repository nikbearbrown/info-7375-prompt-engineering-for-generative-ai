# PROMPTS — Same Odds, Smaller Numbers

No generative media: no image, video or voice-cloning prompts. Narration is the free local Kokoro voice `am_onyx`. Every visual is a deterministic Remotion or Manim render.

## Prompts that appear in the video

**B00 (cold open).** Sent by the author to a fresh Claude Code session (Sonnet 4.5), 2026-09-27. The reply is saved verbatim in `evidence/b00_claude_reply.txt`:

```
Run lessons/01-randomness-and-first-prompts/code/main.py and show me what probabilities([1, 2, 3]) returns. Then compute the same distribution without subtracting the max, and print both sets of intermediate weights side by side.
```

**BHTF (your turn).** Suggested to the viewer; not run for the video:

```
Here is my softmax function: [paste your code]. Don't fix it, and don't tell me whether it's correct. Give me one finite input where subtracting the max still doesn't protect me, predict exactly what my function returns for it, and give me the one line I'd run to check.
```

## Prompts that built the video

See `BUILD-PROMPT.md`. Claude drafted `beat_sheet.json`, `verify_numbers.py` and `fill_math.py` in a separate chat. Claude Code wrote `scenes.py` and these docs, and ran the build.
