# Week 1 Explainer Video — Same Odds, Smaller Numbers

**Student:** Aravind Ravi (`aravind-r`) · INFO 7375, Fall 2026
**Concept (Chapter 1, Part 2):** why subtracting the maximum score changes the intermediate weights but not the softmax distribution.
**Why this one:** it's a claim you can check with real numbers on screen. The weights visibly change, the probabilities visibly don't, and the same trick has a boundary (underflow) you can also show with a real run.
**Runtime:** 3:24 (203.75 s).
**Narration:** synthetic Kokoro voice `am_onyx`, disclosed in the first sentence.

## What the video shows

0. **Title card**, then **the real Claude Code check** (verbatim reply, dated 2026-09-27; its "identical to 15 decimal places" is flagged as a claim and checked later).
1. **The rule:** the scores 1, 2, 3 (constructed input) drop into the softmax formula; T = 1 throughout.
2. **Direct route:** exp(1), exp(2), exp(3) = 2.718, 7.389, 20.086 (sum 30.193). As a stacked bar drawn to scale, it squashes to the probabilities 0.0900 / 0.2447 / 0.6652.
3. **Shifted route:** on a number line the scores slide left by 3, and the gaps stay 1 and 1. The shifted weights (0.135, 0.368, 1.000; sum 1.503) make a tiny bar at the same scale that stretches onto exactly the same probability bar. The recorded run agrees to 15 decimal places (largest difference 1.1 × 10⁻¹⁶), but the results aren't bit-identical.
4. **Why:** the shared factor exp(−m) cancels.
5. **Why it exists:** a recorded sweep of `math.exp` hits the largest float at x = 710 (OverflowError). The shifted route returns [0.5, 0.5] for [1000, 1000].
6. **What it does not establish:** the mirror sweep of `math.exp(−x)` loses digits down to 0.0, so [0, −1000] reports `[1.0, 0.0]`. The shift prevents overflow, not underflow.
7. Takeaways → "Your turn" prompt → outro.

## Contents

| File | Purpose |
|---|---|
| `aravind-r-same-odds-smaller-numbers.mp4` | The video (1080p) |
| `beat_sheet.json` | Reviewed narration and visual plan (approved at each GATE P) |
| `scenes.py` | Manim scenes for every beat except the title card, B01 and the outro; reads every number from `evidence/` |
| `evidence/` | My own dated `main.py` and `verify_numbers.py` runs, the real B00 Claude reply, and the `exp_sweep.py` output |
| `verify_numbers.py`, `exp_sweep.py` | Evidence scripts |
| `fill_math.py`, `add_holds.py`, `add_markers.py` | Build helpers: equation typesetting, per-beat hold, section markers |
| `toolkit-patches/` | 3-line toolkit patch so the outro card shows my name |
| `FACTCHECK.md` | Every claim, its verdict and its source |
| `SHOTLIST.md`, `PROMPTS.md` | Work order and prompts (toolkit Gate F paperwork) |
| `BUILD-PROMPT.md` | Commands and prompts that rebuild the video |
| `SOURCES.md` | What I did, what Claude contributed, tools and licences |
| `FRICTIONAL.md` | Dated process log |
| `TYPECHECK.md` | The toolkit's type-lock report for the final (Gate T) |
| `_context/ASSIGNMENT.md` | The assignment text this was built against |

## Rebuild

Full setup, with this machine's fixes, is in `BUILD-PROMPT.md`. From a set-up `brutalist.art` checkout (`V` = this folder):

```bash
python3 "$V/fill_math.py" .
python3 runtime/scripts/generate_audio_kokoro.py "$V"
python3 "$V/add_holds.py"
python3 runtime/scripts/align.py "$V"
ART_STRICT=0 ./art run "$V" --height 1080
ART_STRICT=0 ./art final "$V" --height 1080 --out /tmp/final
python3 "$V/add_markers.py" /tmp/final/aravind-r-same-odds-smaller-numbers.mp4 "$V/aravind-r-same-odds-smaller-numbers.mp4"
```

To reproduce the numbers alone (no toolkit needed), run from the course repo root:

```bash
python3 lessons/01-randomness-and-first-prompts/code/main.py
python3 fall-2026/aravind-r/week-01-video/verify_numbers.py
python3 fall-2026/aravind-r/week-01-video/exp_sweep.py
```

## Credits

Built with the course's brutalist.art toolkit (`cd4bf20`). Claude drafted the first beat sheet and helper scripts. Claude Code wrote `scenes.py`, the build helpers and the docs, and ran the build. Details and licences are in `SOURCES.md`.
