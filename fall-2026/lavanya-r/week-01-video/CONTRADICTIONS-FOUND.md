# Contradictions Found

The toolkit documentation disagrees about the Kokoro voice for this requested
channel.

- `README.md` says the `hai` persona uses `af_bella`.
- `./art ai-explainer --help` and `skills/make/ai-explainer/SKILL.md` define the
  `claude-hai` channel as Plain register with Kokoro `am_onyx`.

Decision: this reel uses `am_onyx`. The ai-explainer skill's channel table is
the more authoritative source for a reel explicitly requested as the
`claude-hai` channel, and the current builder is the contract governing this
beat sheet. The HAI skill's separate `hai` variant workflow is a different
entry point and does not override the explicitly requested ai-explainer
channel.

The reference `examples/ai-explainer/claude-debunked/beat_sheet.json` also
omits the required `BrutalistHesitantWriter` Beat 2, while the current
ai-explainer skill requires it. This reel follows the current skill and
includes it.