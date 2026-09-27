# BUILD-PROMPT — rebuild "Same Odds, Smaller Numbers"

Everything is local and free: no API keys, paid services or uploads. Tested on macOS (Apple Silicon), 2026-09-27.

## 1. One-time setup (with this machine's fixes; see FRICTIONAL.md for why each is needed)

```bash
V="/path/to/info-7375-prompt-engineering-for-generative-ai/fall-2026/aravind-r/week-01-video"
brew install ffmpeg python@3.12 pkg-config cairo pango espeak-ng
git clone https://github.com/nikbearbrown/brutalist.art      # tested at cd4bf20
cd brutalist.art
mv youtube ../_toolkit-youtube-parked        # setup's ElevenLabs guard trips on these example films
/opt/homebrew/bin/python3.12 -m venv .venv   # manim 0.18 needs Python < 3.13
source .venv/bin/activate
pip install -r requirements.txt matplotlib   # matplotlib: typeset_math.py needs it, requirements.txt omits it
git apply "$V/toolkit-patches/ClaudeTitleOutro-handle.patch"   # outro shows the author's handle, not @NikBearBrown
export PHONEMIZER_ESPEAK_LIBRARY=/opt/homebrew/lib/libespeak-ng.1.dylib   # bundled espeak-ng is broken on macOS
./setup --install
./setup                                       # all ready except "Manim equation beats" (LaTeX), which isn't used
```

In later shells, activate the venv and set `PHONEMIZER_ESPEAK_LIBRARY` again (the author's `brutalist-env.sh` does both).

## 2. Build commands (run from the toolkit folder; `V` = this folder)

```bash
python3 "$V/verify_numbers.py" > /dev/null   # sanity check only; the recorded run is evidence/verify_numbers_output.txt
python3 "$V/exp_sweep.py" > /dev/null        # sanity check; recorded run: evidence/exp_sweep_output.txt
python3 "$V/fill_math.py" .                  # typeset B02/B05 equation rows into beat_sheet.json
python3 runtime/scripts/generate_audio_kokoro.py "$V"   # narration = master clock → mp3/, timings.json
python3 "$V/add_holds.py"                               # silent hold after each beat (hold_after_s)
python3 runtime/scripts/align.py "$V"                   # word timings → mp3/words.json (Manim cues read this)
ART_STRICT=0 ./art run "$V" --height 1080                # review cut; ART_STRICT=0 = accepted underfill MAJORs (FRICTIONAL.md)
ART_STRICT=0 ./art final "$V" --height 1080 --out /tmp/final   # clean master (no review labels; Gate T must pass)
python3 "$V/add_markers.py" /tmp/final/aravind-r-same-odds-smaller-numbers.mp4 "$V/aravind-r-same-odds-smaller-numbers.mp4"
```

If the narration or any `hold_after_s` changes, rerun audio → add_holds → align, then delete `manim/` and `media/*.mp4` so every beat re-renders against the new clock.

## 3. The prompt given to Claude Code for the build

Claude Code (Opus 5.5) ran in the Claude desktop app with normal permissions. Condensed from the working session; the full conversation is not included:

```
My video folder is <course repo>/fall-2026/aravind-r/week-01-video/.
Read skills/make/ai-explainer/SKILL.md, docs/MATH-TYPESETTING.md and
docs/EXECUTABLE-EVIDENCE.md first, then the beat_sheet.json in my folder.
1. Write scenes.py with B03_DirectRoute, B04_ShiftedRoute, B07_Overflow and
   B08_Underflow, following each beat's `show` events. Use Text, not MathTex
   (no LaTeX). Every number on screen must come from verify_numbers.py output.
2. Write FACTCHECK.md, SHOTLIST.md and PROMPTS.md (required before ./art run).
3. Run fill_math.py.  4. Generate audio.  5. Review cut: ./art run --height 1080.
6. Pull frames into _qc/ and actually look at them; fix defects and re-run.
Stop after the review cut and report. Don't run ./art final yet.
```

Later instructions in the same session: replace the Liam persona with my name and a synthetic-voice disclosure; use my own `main.py`/`verify_numbers.py` runs as evidence; use the real B00 reply; change B04 to "fifteen decimal places".

## 4. How scenes.py stays honest

- Each on-screen number is a constant, and on import `_check_evidence()` asserts it appears in `evidence/verify_numbers_output.txt`. A mismatch stops the render.
- Reveals are keyed to narration phrases through `mp3/words.json`. Each scene lasts exactly its beat's measured audio.

## 5. Iteration 2 prompt (2026-09-27, condensed; the author's brief to Claude Code)

```
Second pass on my Week 1 explainer. Goals, in order: (1) fix every flaw found in review; (2) make it more
animated, with motion that enacts the math, without weakening a single evidence rule. Work in phases and STOP
where I say STOP.
Rules: every number on screen is real and comes from evidence/ (scenes.py reads it, never hard-codes it);
no fake in-between numbers (a counter shows x and exp(x) together); the Claude response in B00 stays verbatim,
plus its date; schematics stay labelled; motion must carry meaning; sound optional, self-made, quiet;
narration changes go through me as before/after diffs (GATE P); don't modify the toolkit (rebuild a beat in
Manim instead); no LaTeX; no Co-Authored-By trailers; final ≤ 3:30.
Phase 0: reproduce the review measurements (beat starts, silences, background colours, LUFS, whisper diff).
Phase 1: fix structure, pacing, continuity, background, the B00 date, B03's false counter values, and the
layout issues in B02/B04/B06/B08/BVDT/BHTF.
Phase 2: one motion language (score chips travel B02→B04, T = 1 pinned, one accent per beat on the word clock);
stacked bars at true widths (pixel-checked); number-line slide; B05 cancellation from separate typeset pieces;
B06 countdown; B07/B08 driven by a new evidence script exp_sweep.py.
Phase 3: final render, paperwork, git status and commit message, then commit and push on my go.
```

Later instructions in the same session: restore a short title card (B00's first sentence moved onto it
verbatim, approved at GATE P); give every beat enough reading time; "best production quality".
