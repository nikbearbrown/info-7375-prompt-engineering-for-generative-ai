# Sources

- Real script: `../info-7375-prompt-engineering-for-generative-ai/lessons/01-randomness-and-first-prompts/code/main.py`
- Real evidence: running the unmodified script with seed 7 twice gives
  probabilities `[0.0900, 0.2447, 0.6652]` and counts `{0: 102, 1: 268,
2: 630}`; `sample([1,2,3], seed=99)` gives `{0: 93, 1: 267, 2: 640}`.
- The prompt and concept/script content were developed with Claude (chat).
- The JSON authoring, build, rendering, and QC work were done by Claude Code.
- Voice: the final video uses free local Kokoro `af_bella`. `am_onyx` was
  initially selected from the ai-explainer `claude-hai` channel table, but was deliberately overridden because the assignment did not require the
  toolkit's internal branding convention; the repository's final beat sheet
  and every narration beat use `af_bella`.
- Narration: v2 is the single rewrite from v1, made to fix flat, monotonous
  pacing and confirmed by reviewing a faster-whisper transcript. Kokoro's
  `--help` was also checked: the free engine supports only global speed, not
  prosody or emphasis controls, so the monotone voice quality has no further
  engine setting to fix.
- B03 and B04 show the verified source runs with the `ShellSession`       
  component, including real terminal output and highlighted lines. B04A was added after B04 using the built-in `DivergentFates` pattern to show the same starting distribution producing different outcomes from different seeds. It is a supporting visual layer, not a replacement for the terminal evidence.
- B05 is deliberately visually distinct: it is a constructed wrong-answer
  illustration, not output from the source script, and is labeled on screen
  `ILLUSTRATION — CONSTRUCTED` and `ILLUSTRATIVE EXAMPLE — NOT ACTUAL OUTPUT.`
- The native-component gap for animated zooming into a specific terminal  
  value was logged as the dated 2026-09-15 PUNT in `TEMPLATE-MISSES.md`; it was not faked with an unsupported component.
