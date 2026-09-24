# River Moves the Bank.

**Gnanasudharsan Ashokumar** · `ashokumar.g@northeastern.edu`
INFO 7375 — Prompt Engineering for Generative AI · Week 01 · Chapter 1, Part 1

| | |
|---|---|
| **Concept** | Attention — how `river` changes the vector for `bank` |
| **Why it matters** | A word does not arrive at the model carrying its meaning; attention recomputes that meaning from the sentence around it, which is why the same token resolves differently in two different contexts. |
| **Runtime** | **3:50.9** (230.9 s) · 3840×2160 · 24 fps · 13 beats |
| **Deliverable** | `video/claude-tom-river-moves-the-bank.mp4` |
| **Source** | `chapters/01-randomness-and-first-prompts.md` § *Inside one prediction step* @ `a0d8a1e` |
| **Cost** | $0.00 — Kokoro TTS, Remotion and ffmpeg, all local. No API key, no paid call. |

---

## What the video does

Chapter 1 makes this claim in a single clause and publishes **no numbers** for it:

> "the vector for `bank` after `river` ends up somewhere different from the
> vector for `bank` after `savings`"

The video supplies the arithmetic the chapter skips, and keeps the two things
visibly separate the whole way through.

| Beat | Act | What happens on screen |
|---|---|---|
| B00–B01 | open | The ask, then the one-breath overview written and corrected live |
| B02 | the problem | A static embedding table has **one** row for `bank`; both sentences pull it |
| B03 | honest setup | The constructed 2-D toy, with all five simplifications listed |
| B04 | **step 1** | `q · k` written out per term — `2×1 + 2×1 = 4` — then `÷ √2` |
| B05 | **step 2** | Softmax: three scores become three weights, assembling one bar to **Σ = 1.000** |
| B06 | **step 3** | The weighted sum; `bank` travels **(2, 2) → (1.58, 2.14)**, drawn to scale |
| B07 | the payoff | Both runs side by side: `river` → (1.58, 2.14), `savings` → (2.14, 1.58) |
| B08 | boundary | ESTABLISHES / DOES NOT ESTABLISH ledger |
| B09 | **boundary** | The limit, full-frame and verbatim (below) |
| BVDT–BOUT | close | Verdict, viewer prompt, title card |

### The three rubric constraints

1. **Show the mechanism, don't assert it.** The dot products, the softmax
   normalisation and the vector shift all compute on screen, term by term, as
   they are spoken. No beat is a slide with a voice over it.
2. **Constructed example, labelled.** A terracotta **`CONSTRUCTED EXAMPLE`**
   stamp is on screen for the whole of B03–B07 — every beat that shows vector
   math — alongside a ledger headed *EVERY NUMBER HERE IS INVENTED*.
3. **Name the boundary.** B09 states it full-frame and reads it aloud verbatim:

   > What this single-head 2D example does not establish is how multi-head
   > attention handles dozens of nuanced semantic dimensions simultaneously.

---

## Verify

```bash
python3 src/verify_numbers.py
```

Expected: `ALL CHECKS PASS`. It re-derives every number in the video from the
four embeddings `the (1,1)` `river (0,3)` `savings (3,0)` `bank (2,2)`,
evaluates the arithmetic strings the video prints, asserts the softmax weights
total exactly **1.000** (and that at 2 d.p. they would total 1.01 — which is
why the video prints three), and then asserts the rubric constraints above:
runtime inside 3:30–4:00, the stamp on all five math beats, and the boundary
statement present verbatim both on screen and in the narration.

## Rebuild

```bash
cd /path/to/brutalist.art
source .venv/bin/activate                      # required
export REEL=/path/to/youtube/claude-tom-river-moves-the-bank

python3 "$REEL/verify_numbers.py"                              # arithmetic + rubric
python3 runtime/scripts/generate_audio_kokoro.py "$REEL"       # audio = master clock
#   then set each Ch1Attn* durationInFrames in
#   runtime/remotion/src/Root.tsx to round(actual_duration_s * 30)
(cd runtime/remotion && npx tsc --noEmit -p tsconfig.json)
./art scene-index
python3 runtime/scripts/remotion_scenes.py "$REEL" --force     # --only takes ONE beat
./art run   "$REEL"                                            # compile + Gate V
./art final "$REEL"                                            # → renders/*.mp4
```

Full detail, including why the frame counts must be re-tuned, is in
`docs/BUILD-PROMPT.md`. Attributions are in `docs/SOURCES.md`; the honest process log —
including the rebuild that produced B09 — is in `FRICTIONAL.md`.

---

## Package contents

```
README.md                         this file
FRICTIONAL.md                     process log (graded separately)
video/claude-tom-...mp4           the deliverable, 3840x2160, 3:50.9
docs/SOURCES.md                   attributions, tools, human/AI split, licences
docs/BUILD-PROMPT.md              exact prompt + commands to rebuild end to end
docs/FACTCHECK.md                 claim-by-claim check; the constructed numbers
docs/SHOTLIST.md                  typed work order, library-search result
docs/PROMPTS.md                   on-screen prompts + authoring prompts
src/beat_sheet.json               13 beats: timing, narration, visual plan
src/verify_numbers.py             re-derives every figure + asserts the rubric
src/Ch1Attn*.tsx  (8)             the scene components written for this video
src/Ch1Chrome.tsx                 shared chassis (reused; extended additively)
evidence/gate-v-REPORT.md         final visual QC: 0 BLOCKER / 0 MAJOR
evidence/qc-sheet.png             contact sheet for the whole reel
evidence/frames/B*.png            final-state frame from each of the 13 beats
```
