# BUILD-PROMPT

Part A has the exact commands that rebuild the film. Part B records the one prompt that produced it.

## Part A: Commands that rebuild the film

Everything is free and local. No API keys and no paid generation. Only the pip install needs the network.

```bash
# 0. Toolkit: the Brutalist checkout at commit 3a6d397 (folder Brutalist-latest here).
cd Brutalist-latest
python3.12 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt          # Manim 0.20.1, kokoro-onnx 0.6.1, faster-whisper 1.2.1
# Kokoro model files: ./setup --install downloads them. This build copied them from an
# earlier checkout instead (same SHA-256, no download):
#   cp ../Brutalist/runtime/models/kokoro/{kokoro-v1.0.onnx,voices-v1.0.bin} runtime/models/kokoro/
./setup                                            # readiness table (Remotion is not needed)
./art smoke                                        # end-to-end render proof

# 1. Put this folder's build files in the toolkit, at the path the scripts expect:
R=youtube/brutalist/agent-proving-ground-progress
mkdir -p $R && cp <progress-film>/{make_sheet.py,sentence_audio.py,scenes.py,FACTCHECK.md,SHOTLIST.md,PROMPTS.md} $R/

# 2. Evidence (read-only, from the APG repo; writes evidence/B6.txt … B13.txt)
bash <progress-film>/evidence/capture.sh <progress-film>/evidence

# 3. Beat sheet, then narration (audio first: the measured mp3s are the clock)
python3 $R/make_sheet.py
mkdir -p $R/mp3 && python3 $R/sentence_audio.py   # NOT generate_audio_kokoro.py (it would drop the sentence pauses and times)

# 4. Review cut (Gates F, L, A, W, strict B per scene, then V), then the 4K master (Gate T first)
./art run   $R                                     # full path; a bare slug fails
./art final $R --out $R/exports                    # -> $R/exports/agent-proving-ground-progress.mp4
```

`beat_sheet.json` in this folder is the measured sheet after step 3, stamped by `./art final`. Re-running `make_sheet.py` resets it, so run `sentence_audio.py` after it.

Gates, run after the master. Each report goes to `$R/_qc/gates/`; this folder's `gates/` is a copy, with paths shortened:

```bash
bash <progress-film>/gates/run_gates.sh
# 01 schema · 02 build_safety · 03 factcheck · 04 beat_lint · 05 gate_shape ·
# 06 Gate A · 07 Gate W · 08 Gate B (strict) · 09 Gate V on the master ·
# 10 Gate T (from ./art final) · 11 render integrity · 12 unit tests · 13 smoke
```

The whisper pronunciation check (`gates/whisper_check.txt`) used the cached faster-whisper `small.en` model offline (`HF_HUB_OFFLINE=1`) and transcribed each `mp3/beat-*.mp3`.

## Part B: The prompt

One prompt, given to Claude Code on Nov 23, 2026 ("BUILD MY FINAL PROJECT FILM (progress film, through M5), end to end"). It set the scope, the read-only rules for the APG repo, and the 11 steps, and it included my approved BEAT-PLAN (saved verbatim as `BEAT-PLAN.md`).

One decision was put back to me during the build:

> **B4 check.** My October PROJECT-BRIEF.md names only two tools: "E2B provides sandboxes for running AI-generated code, and Langfuse records LLM traces and scores." Runtime, Raindrop and oh-my-pi aren't in the brief at all. Which B4 should be voiced?

*My answer:* "Brief only". B4 uses the brief's wording for E2B and Langfuse, drops Runtime, Raindrop and oh-my-pi, and keeps the Drupal sentence. README.md has the before and after.

*Outcomes during the build:*
- The number check found no mismatches (NUMBER-CHECK.md).
- Gate A first stopped on B13: an underline placed with `get_left()` measured outside the frame in Gate A's stub. It was fixed with fixed coordinates.
- Long Menlo lines wrapped in low-resolution previews, because Pango wraps at the render's pixel width. Mono text is now built at a 48 pt reference size. Pango also drops leading spaces, even no-break spaces (see the last outcome).
- Gate V then flagged B03 at its halfway frame (55% fill against a 55% floor). B03's cards were made taller, and only B03 was re-rendered.
- The first 4K frames showed lost indents, which put B11's "a" and "b" column headers over the wrong columns. Indents are now rebuilt as an x offset, and B07–B11 were re-rendered. After that, every gate passed on the final master (`gates/SUMMARY.txt`).
