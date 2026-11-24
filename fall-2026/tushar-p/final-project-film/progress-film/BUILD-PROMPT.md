# BUILD-PROMPT

Part A has the exact commands that rebuild the film (v2). Part B records the prompts that produced it: the first build (v1) and the v2 rebuild.

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
mkdir -p $R/mp3 && python3 $R/sentence_audio.py   # NOT generate_audio_kokoro.py (it would drop the sentence pauses and times); 0.25 s pauses in v2

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

## Part B: The prompts

### v1 build

One prompt, given to Claude Code on Nov 23, 2026 ("BUILD MY FINAL PROJECT FILM (progress film, through M5), end to end"). It set the scope, the read-only rules for the APG repo, and the 11 steps, and it included my approved BEAT-PLAN (saved verbatim as `BEAT-PLAN.md`).

One decision was put back to me during the build:

> **B4 check.** My October PROJECT-BRIEF.md names only two tools: "E2B provides sandboxes for running AI-generated code, and Langfuse records LLM traces and scores." Runtime, Raindrop and oh-my-pi aren't in the brief at all. Which B4 should be voiced?

*My answer:* "Brief only". B4 uses the brief's wording for E2B and Langfuse, drops Runtime, Raindrop and oh-my-pi, and keeps the Drupal sentence. README.md has the before and after.

*Later the same day (Nov 23), my follow-up:* "Make B4 match the October pitch: E2B and Langfuse only." The Drupal sentence and its card were removed. Only B04's audio and scene were regenerated, the master was re-exported, and gates 01–13 were re-run (all PASS).

*Outcomes during the build:*
- The number check found no mismatches (NUMBER-CHECK.md).
- Gate A first stopped on B13: an underline placed with `get_left()` measured outside the frame in Gate A's stub. It was fixed with fixed coordinates.
- Long Menlo lines wrapped in low-resolution previews, because Pango wraps at the render's pixel width. Mono text is now built at a 48 pt reference size. Pango also drops leading spaces, even no-break spaces (see the last outcome).
- Gate V then flagged B03 at its halfway frame (55% fill against a 55% floor). B03's cards were made taller, and only B03 was re-rendered.
- The first 4K frames showed lost indents, which put B11's "a" and "b" column headers over the wrong columns. Indents are now rebuilt as an x offset, and B07–B11 were re-rendered. After that, every gate passed on the final master (`gates/SUMMARY.txt`).

### v2 rebuild (the film in this folder)

A second prompt, the same day (Nov 23, 2026): "REBUILD THE PROGRESS FILM with new narration. The current cut dives into implementation too early and ends without explaining what's left. The new structure explains the project first, keeps "built so far" short, and ends on what's left."

It kept the same scope and read-only rules, and set these rules:
- my new 13-beat narration, word for word (now BEAT-PLAN.md; v1 is kept at the bottom of that file)
- a hard cap of 4:00, with a target of about 3:50, where only the pauses between sentences may be tightened
- REAL visuals reuse the existing captures; everything else is labelled "constructed"
- a fresh number check before rendering
- every gate, with no shipping over a failure
- no commit or zip yet

*Outcomes during the v2 build:*
- The number check found no mismatches (NUMBER-CHECK.md, 24 rows). Three wording points that are not numbers are listed there for me.
- At 0.35 s pauses the narration measured 238.5 s (3:58.5), under the cap but close to it. The pauses were tightened to 0.25 s, giving 234.3 s (3:54.3) of narration. No words changed.
- "INFO 7375" gets a voice-only respelling ("info seventy-three seventy-five"), like "E2B" and the repo URL. The whisper check heard all 13 beats as written.
- Gate A stopped B10, and then B12: its stub doesn't measure text, so scenes that only fade text into fixed cards look as if no shape ever changes. B10 gained a tick, a cross and an underline; B12 gained an open checkbox per card.
- B04's mock-up had an empty spacer line, which Pango renders as an empty object that can't be placed. The spacer was removed.
- The first full review cut passed Gate V, but frame review found two problems the gates don't catch. In B08 the 16 tiles disappeared behind the white dev/held-out cards they moved into, so the tiles now sit above the cards. In B01 the title finished writing only half a second before the cut, so it now appears with "This is my final project". Both were re-rendered; their draft clips are kept in the reel's `_superseded/v2_drafts/`.
- Gate T (run by `./art final`) then blocked the master. Six beats failed, so no master was exported and nothing shipped. Two causes:
  - **Small text:** labels at size 20–24 measured 35–40 px against the 41 px floor; it measures two touching lowercase letters, or a "→", as one text run. Those labels went up to size 24–30.
  - **Chip outlines:** Gate T's text mask also picked up the grey chip outlines, so a two-letter run inside a chip counted as overlapping labels. Chip outlines are now a lighter grey (#A9B0B8), which is decorative and outside the mask.
  - All 13 scenes were re-rendered. A standalone Gate T run then flagged only B09 ("PLAN.md: done through", 40 px), which went to size 28. After that Gate T passed, and the master was exported.

### B10 fix (later on Nov 23)

My follow-up: fix one overclaim in B10. Only its last sentence changed, from "…and I write my predictions down before every run." to "…and I wrote my predictions down before the held-out runs."
- B10's audio (19.45 s, whisper-checked) and scene were regenerated; nothing else was re-rendered.
- The master was re-exported, and gates 01–13 were re-run: all PASS.
- NUMBER-CHECK.md now sources B13's "not a model benchmark" (APG docs/01-brief.md:47, added to `evidence/B13.txt`). It also notes that B12's "clean machine" wording comes from the final-project assignment.

### B12 item 3 (later on Nov 23)

My follow-up: change B12's third item from "submission" to a real implementation item.
- **Narration:** "Third, the full write-up and submission, by December eighteenth." became "Third, I'll harden the check, so it confirms every test actually ran."
- **Card 3:** "Harden the check" / "confirm every test actually ran: a forced exit can't fake a pass", with a footer "All by Dec 18" under the three cards. Cards 1 and 2 are unchanged.
- **Card 3 text size:** its line is longer, so it uses size 26 instead of 30. That is still above Gate T's floor.
- **Sources:** APG docs/03-action-surface-map.md:108–113 and docs/07-evidence.md Honest limits point 4 (lines 517–519), captured read-only into `evidence/B12-v2.txt`.
- **Rebuild:** only B12's audio (whisper-checked) and scene were regenerated. The narration stayed under 4:00, so no pause between sentences changed. The master was re-exported, and gates 01–13 were re-run.
- **Render integrity failed once.** The first export decoded 5,644 frames against the expected 5,645.
  - **Where:** comparing the master with each segment showed every beat aligned; the one missing frame was the very last frame of B13's silent tail. Nothing visible or audible was lost.
  - **Cause:** the toolkit cuts the final encode with `-t` written to three decimals. A timeline of 5,645/24 = 235.2083 s became 235.208, which drops the last frame.
  - **Fix (B12 only):** B12's audio got a 0.04 s silent tail. Its slot became 407 frames and the timeline 5,646 frames = 235.250 s, which three decimals represent exactly.
  - **Kept:** the short master is kept in the reel's `_superseded/v2_drafts/b12_frame_short/`.

