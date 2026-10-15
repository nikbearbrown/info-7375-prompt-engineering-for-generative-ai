# SOURCES — Quote It or Refuse. (ClaimCheck pitch)

## Executive summary

What this film was made with, what I made, what Claude contributed, and the licence of
every third-party piece. There is no stock footage, no screenshot of anyone else's
product, no AI-generated image or video, and no real claim or personal data. Every
document shown on screen is synthetic text written for this film.

## What I used

| Thing | What for | Licence / terms |
|---|---|---|
| Brutalist toolkit (`github.com/nikbearbrown/brutalist.art`, local clone at commit `6a8380a`, 2026-09-20) | pipeline: beat sheet → audio → render → QC gates | course toolkit, used as instructed by the assignment; not modified |
| Kokoro TTS v1.0 (`kokoro-v1.0.onnx`, voice `am_onyx`), bundled in the toolkit | narration audio, generated locally | Apache-2.0 (Kokoro-82M model) |
| Manim Community v0.18.1 | the eight body animations and the outro card (`scenes.py`) | MIT |
| Remotion v4 (toolkit's `runtime/remotion`) | bookend scenes: `ClaudeComposerAsk`, `BrutalistHesitantWriter`, `ClaudeCodeBeat`, `ClaudeVerdictArtifact` | Remotion licence: free for individuals |
| EB Garamond (bundled with the toolkit) | serif type | SIL Open Font License 1.1 |
| Menlo, Helvetica Neue (macOS system fonts) | mono / sans type in Manim scenes | Apple system fonts, used locally for rendering |
| ffmpeg | audio/video assembly (called by the toolkit) | LGPL/GPL |

No paid service, API key, or account was used. Nothing was uploaded.

## What I made

- The project idea and every decision in it: ClaimCheck, the target role, the scope, what is
  deliberately out, the risk.
- The confirmation that I tried the two alternatives in B05 myself (a chat assistant with
  a PDF upload; a LlamaIndex/LangChain RAG template), recorded 2026-10-07.
- The choices of what to leave out: no Cybersenz mention, no classmate blind questions
  promised, no Dovetail benchmark numbers (not re-run).
- The only real output in the film: Dovetail's test run (`pytest -q`, 2026-10-07,
  `47 passed in 0.62s`), saved verbatim in `evidence/dovetail-pytest-2026-10-07.txt`.
  Dovetail is my own earlier project.

## What Claude contributed

All in Claude Code sessions on 2026-10-07 and 2026-10-14 (models: Claude Sonnet 5, then
Claude Opus 5.5):

- Suggested the project options; I picked option 1 (ClaimCheck).
- Drafted `PROJECT-BRIEF.md`, `PLAN.md`, the beat sheet narration and visual plan,
  `scenes.py`, `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`, this file, `README.md`,
  `BUILD-PROMPT.md`, `build.sh`, and the first draft of `FRICTIONAL.md`, from my answers.
- Ran the toolkit commands, read the preview frames, and fixed layout and gate failures
  (logged in `FRICTIONAL.md`).
- No Claude response appears in the film. The composer screens are reconstructed
  interface with no model output; B00 says so on screen.

## Synthetic / constructed material

| Beat | What | Label on screen |
|---|---|---|
| B02 | homeowner policy, endorsement E-2, the "Section 4(b)" answer | CONSTRUCTED EXAMPLE - synthetic text |
| B03 | pipeline diagram | PLANNED DESIGN - not built |
| B04 | answer contract JSON | PROPOSED answer contract - not written yet |
| B06 | eval report table (placeholder rows) | CONSTRUCTED MOCK-UP - no results exist |
| B07–B09 | skills map, scope, mitigations | PLAN |
