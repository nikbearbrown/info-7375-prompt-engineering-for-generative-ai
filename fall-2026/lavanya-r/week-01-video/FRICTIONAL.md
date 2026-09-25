# Frictional Notes

- 2026-09-15 — Earlier pycairo build failure was fixed with:
  `brew install cairo pango pkg-config`
- 2026-09-15 — Toolkit contradiction: `README.md` maps HAI to `af_bella`,
  while the ai-explainer `claude-hai` channel table maps it to `am_onyx`.
- 2026-09-15 — Toolkit contradiction: the worked `claude-debunked` example
  lacks the hesitant-writer Beat 2 required by the current ai-explainer skill.
- 2026-09-22 — Voice decision: `am_onyx` was initially chosen from the
  ai-explainer channel table, then deliberately overridden to `af_bella`
  because nothing in the assignment required the toolkit's internal branding
  convention. The final beat sheet, audio, and video use `af_bella`.
- 2026-09-22 — Narration was rewritten once, from v1 to v2, to fix flat,
  monotonous pacing. A faster-whisper transcript review confirmed the pacing
  change; it was not a guess based only on listening.
- 2026-09-22 — B03 and B04 were changed from a plain data-table visual to
  `ShellSession`, showing the real terminal output with highlighted lines.
- 2026-09-22 — B05 was kept visually distinct from the evidence beats as a
  constructed wrong-answer illustration, explicitly labeled on screen
  `ILLUSTRATIVE EXAMPLE — NOT ACTUAL OUTPUT.`
- 2026-09-22 — B04A was added after B04 using the built-in `DivergentFates`
  pattern: same starting distribution, different seed, different outcome.
  This is a supporting visual layer, not a replacement for the real terminal
  evidence.
- 2026-09-22 — Kokoro's audio-engine `--help` was checked for prosody and
  emphasis controls. It exposes only a global speed setting, so there is no
  free-engine setting that fixes the monotone voice quality.
- 2026-09-15 — Genuine gap logged as a dated PUNT in `TEMPLATE-MISSES.md`:
  no native component supports animated zoom into a specific terminal value.
- 2026-09-22 — Process mistake caught: the video was reviewed and critiqued
  after the voice-swap edit, including transcript and pacing review, before
  confirming that a rebuild had run. File timestamps proved the video was
  still the old version. The build was then re-run correctly before the final review.