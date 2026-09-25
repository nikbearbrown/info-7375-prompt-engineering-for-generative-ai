# Build Prompt

Rebuild the unpublished `claude-hai-seed-repeatable` reel from this folder.

Read `beat_sheet.json`, `CONTRADICTIONS-FOUND.md`, `SOURCES.md`, and the
current `skills/make/ai-explainer/SKILL.md` first. Preserve every supplied
number and claim. Use the final beat sheet as the build contract: Plain
register, students audience, `@HumanitariansAI`, Claude palette, and Kokoro
`af_bella`. The skill table initially suggested `am_onyx`, but this reel
deliberately overrides that internal branding convention because the actual
assignment does not require it.

1. Verify the source at `../info-7375-prompt-engineering-for-generative-ai/lessons/01-randomness-and-first-prompts/code/main.py` and its exact seed 7 and seed 99 outputs.
2. Use the current narration in `beat_sheet.json` (the v2 rewrite). It was
	changed once from v1 to fix flat, monotonous pacing and checked with a
	faster-whisper transcript review. Generate its audio with
	`python3 runtime/scripts/generate_audio_kokoro.py youtube/claude-hai-seed-repeatable --speed 1.0`.
	Kokoro's `--help` confirms that the free local engine exposes only a global
	speed control, not prosody or emphasis controls; do not invent a missing
	voice-quality setting.
3. Render the registered Remotion scenes with
	`python3 runtime/scripts/remotion_scenes.py youtube/claude-hai-seed-repeatable`.
	Keep the final 11-beat structure: B03 and B04 use `ShellSession` for the
	real terminal evidence and highlighted output; B04A uses the built-in
	`DivergentFates` rhetorical pattern after B04 as a supporting illustration
	of the same distribution with different seeds; B05 remains visually
	distinct as the constructed wrong-answer illustration and must show
	`ILLUSTRATIVE EXAMPLE — NOT ACTUAL OUTPUT.` on screen.
4. Run `./art run youtube/claude-hai-seed-repeatable`, inspect
	`./art todo youtube/claude-hai-seed-repeatable`, and fill any missing
	native media without inventing evidence. After any voice or beat-sheet
	edit, check file timestamps or build metadata to confirm a rebuild really
	ran before reviewing the video.
5. Sample at least 2 fps plus 15%, 50%, and 85% of every beat into `_qc/frames/`,
	read the PNGs, and write `_qc/REPORT.md`. Fix every BLOCKER and MAJOR defect
	before continuing.
6. Run `./art final youtube/claude-hai-seed-repeatable` and stop. Never publish
	or upload.

The wrong-answer example must remain labeled `ILLUSTRATION — CONSTRUCTED`, must
also show `ILLUSTRATIVE EXAMPLE — NOT ACTUAL OUTPUT.`, and must never be
presented as source-script output.