# BUILD-PROMPT — claude-tom-river-moves-the-bank

**"River Moves the Bank." · INFO 7375 · Chapter 1, Part 1 · 3:51 · 3840×2160 · 13 beats**

The single paste-ready prompt that rebuilds this reel end to end, plus the exact
commands it runs. Everything here is free and local: Kokoro TTS, Remotion,
ffmpeg. **No paid API is called at any point and no key is required.**

---

## The prompt

> Rebuild the reel at
> `info-7375-prompt-engineering-for-generative-ai/youtube/claude-tom-river-moves-the-bank/`
> from its `beat_sheet.json`.
>
> Rules, in force for the whole build:
> 1. **Audio first.** Generate the Kokoro narration and measure it BEFORE
>    rendering anything. The measured MP3 durations are the master clock. Never
>    fix timing by hand — regenerate and recompile.
> 2. **Re-tune `Root.tsx` to the measured audio.** The seven `Ch1Attn*`
>    compositions key their reveals to fractions of their own
>    `durationInFrames` (`useSpAt` / `useDrawAt`), so the registered frame count
>    must equal `round(actual_duration_s × 30)` or every reveal drifts.
> 3. **Verify the arithmetic before rendering.** Run `verify_numbers.py`. It
>    re-derives every figure on screen from the four embeddings and fails on any
>    mismatch. If it fails, the numbers are wrong, not the script.
> 4. **Render Remotion only via `runtime/scripts/remotion_scenes.py`**, in the
>    foreground. Never hand-roll `npx remotion render`.
> 5. **QC by LOOKING at frames.** The mp4 probe is a file check and never counts
>    as QC. Gate V must reach 0 BLOCKER and 0 MAJOR before `./art final`.
> 6. **The boundary beat is not optional.** B09 must state, full-frame and
>    verbatim, *"What this single-head 2D example does not establish is how
>    multi-head attention handles dozens of nuanced semantic dimensions
>    simultaneously."* `verify_numbers.py` asserts it appears both in the
>    scene props and in the spoken narration.
> 7. **Runtime must land inside 3:30–4:00.** The verifier fails outside it.
> 8. **Never publish.** Output stays in the reel folder and `renders/`.

---

## The commands, in order

```bash
cd /path/to/brutalist.art
source .venv/bin/activate          # REQUIRED — a bare ./art doctor
                                   # falsely reports Kokoro/Manim blocked
export REEL=../info-7375-prompt-engineering-for-generative-ai/youtube/claude-tom-river-moves-the-bank
```

**0 — readiness and arithmetic**

```bash
./art doctor
python3 "$REEL/verify_numbers.py"
```

`doctor` must show audio / captions / Manim / Remotion / compile all READY.
`verify_numbers.py` must end `ALL CHECKS PASS` — it now also gates the runtime
window and the boundary-statement requirements, not just the arithmetic.

**1 — audio (the master clock)**

```bash
python3 runtime/scripts/generate_audio_kokoro.py "$REEL"
```

13 beats, Kokoro `am_michael`, cost $0.00. Writes `mp3/beat-*.mp3` and stamps
`actual_duration_s` into the beat sheet.

**2 — re-tune the registered durations** *(only if the audio changed)*

Set each `Ch1Attn*` composition's `durationInFrames` in
`runtime/remotion/src/Root.tsx` to `round(actual_duration_s × 30)`:

| Composition | Beat | s | frames |
|---|---|---|---|
| `Ch1AttnStaticRow` | B02 | 16.28 | 488 |
| `Ch1AttnToySetup` | B03 | 18.79 | 564 |
| `Ch1AttnScores` | B04 | 15.96 | 479 |
| `Ch1AttnSoftmax` | B05 | 17.09 | 513 |
| `Ch1AttnWeightedSum` | B06 | 24.26 | 728 |
| `Ch1AttnTwoContexts` | B07 | 16.17 | 485 |
| `Ch1AttnBoundary` | B08 | 24.53 | 736 |
| `Ch1AttnMultiHead` | B09 | 25.71 | 771 |

**3 — typecheck, then index**

```bash
cd runtime/remotion && npx tsc --noEmit -p tsconfig.json && cd ../..
./art scene-index
./art scenes --check Ch1AttnWeightedSum     # spot-check one
```

A broken `Root.tsx` breaks every reel in the repo, so the typecheck is not
optional. `scene-index` is the only way anyone finds the new components later.

**4 — render the beats**

```bash
python3 runtime/scripts/remotion_scenes.py "$REEL" --force
```

`--only` takes **one** beat id; loop it if you need a subset.

**5 — compile + gates**

```bash
./art run "$REEL"
```

Runs Gate F (paperwork), Gate L (beat-mix lint), Gate SHAPE, compiles the
review cut, writes `qc-sheet.png`, then Gate V (frame-level visual QC) into
`_qc/REPORT.md`.

**6 — visual QC, by eye**

```bash
ffmpeg -i "$REEL/claude-tom-river-moves-the-bank-slate.mp4" \
       -vf fps=2 "$REEL/_qc/frames/%05d.png"
```

Read the PNGs. Audit the 9-point rubric in `CLAUDE-CODE-VISUAL-QC-CHECK.md`.
Fix root causes in the scene source — never by nudging pixels — and re-render
until Gate V reports **0 BLOCKER / 0 MAJOR**.

**7 — the master**

```bash
./art final "$REEL"
```

Writes `renders/claude-tom-river-moves-the-bank.mp4` (3840×2160, 230.9s) and a
`.verified.json` beside it.

---

## Expected output

```
renders/claude-tom-river-moves-the-bank.mp4          3840×2160  230.88s  ~17 MB
renders/claude-tom-river-moves-the-bank.verified.json
<reel>/claude-tom-river-moves-the-bank-slate.mp4     review cut, beat markers
<reel>/mp3/beat-*.mp3                                13 narration files
<reel>/media/*.mp4                                   13 per-beat renders
<reel>/qc-sheet.png  <reel>/_qc/REPORT.md
```

Sanity check the master actually decodes, rather than trusting the file size:

```bash
ffmpeg -hide_banner -i renders/claude-tom-river-moves-the-bank.mp4 \
       -af volumedetect -f null - 2>&1 | grep mean_volume
```

Expect roughly `mean_volume: -27.0 dB`. A silent master with a populated `mp3/`
is a FAILED BUILD, not a quiet one.

---

## Known non-blocking warning

```
WARNING: 'remotion' carries 13/13 beats (100%) — over the ~40% pantry cap
```

Expected and accepted for this episode. MOTION.md wants visual-language
diversity across a reel; this one's evidence is arithmetic, and arithmetic is
best drawn as deterministic Remotion. There are no stills to add because a
still would not be evidence here — adding archive imagery to satisfy a ratio
would be decoration. See SHOTLIST.md.
