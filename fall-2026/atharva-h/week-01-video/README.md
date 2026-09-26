# It Can Never Tell You It Hates All Of Them

**Atharva Hambir** · INFO 7375, Week 01 video · hambir.a@northeastern.edu

**The concept (one, from Chapter 1):** the softmax — the last step a language model
takes before it picks a word — keeps only the **gaps** between scores and throws away
their overall level.

**Why this one:** the chapter proves the max-subtraction cancellation and stops at
"the intermediates changed, the distribution didn't." One step further is a
consequence the chapter never states: if only the gaps survive, the model has no way
to express *"every option here is bad."* There is always a winner, and a winner always
looks confident.

**Runtime:** 3:04.6 (184.58s) — measured from the rendered master, not estimated.
**Video:** `claude-liam-only-the-gaps.mp4` — 3840×2160, 24 fps, H.264/AAC, 12.5 MB.
Submitted via Canvas; **not in this folder yet** — media is held back from the repo
for now. Everything needed to rebuild it bit-for-bit is here.
**Cost:** $0.00. No API keys, no paid generation, no network calls, no account.

---

## What the video shows

Twelve beats. Claim IDs in brackets are checks in `verify/verify_claims.py`.

1. **Scores become chances.** A chatbot scores every word, then the last step turns
   those marks into chances that must total 100 — one whole pizza, every time. *(C1)*
2. **What a "gap" is**, defined before the word is used for anything: the distance
   between two scores. `1, 2, 3` are each one apart — and so are `101, 102, 103`.
   Totally different scores, exactly the same gaps.
3. **Sliding changes nothing.** Nudge one score and the output redraws; slide all
   three together and the output is bit-for-bit identical, through +1e6, +1e15, and
   below zero. *(C3)*
4. **That's really this function, not a stuck animation** — `x²` and `|x|`
   normalisation both break under the identical slide. Then the rotten kitchen: every
   lunch option 100 points worse, still "67%, pizza." *(C4)*
5. **The payoff, and what temperature actually is.** It can tell you what it prefers;
   it can never tell you it hates the lot. The one thing that *does* change the answer
   is pulling the gaps apart — stretch them and the favourite wins more often, squash
   them and it picks more evenly. That is what temperature means, shown in both
   directions rather than named. *(C12)*
6. **Why a computer stops being able to tell 1 apart.** A number gets about sixteen
   digits of room. A small score leaves the box nearly empty; a huge one fills every
   cell, so the last digit cannot be written down. Three scores we wanted —
   `…740993 · …740994 · …740995`, one apart — are stored as `…740992 · …740994 ·
   …740996`, two apart. The gaps doubled and nobody asked. *(C14)*
7. **The prediction, stated before it is computed.** Past 2⁵³ the rounding widens the
   gaps from 1 to 2. Twice as far apart is exactly what turning the temperature down
   does — so the broken output *must* be the recorded T=0.5 row. It is, digit for
   digit. *(C6, C7, C12)*
8. **Fake uncertainty.** Push further and all three scores round onto the same number:
   output `0.3333333333` three times. Now it looks completely unsure — by accident. *(C8)*
9. **The check that sees nothing.** Both wrong answers sum to exactly 1.0, and the
   usual safety check only asks whether the chances add to 100. It waves both
   straight through. *(C9)*

**What this does not establish** — said out loud in the closing beat: real chatbots do
not fail this way. Raw next-token logits sit around −10…+10; nobody shifts by 10¹⁶.
The honest claim is narrower than "numerically stable" — exact below 2⁵³, silently
wrong above it.

**Constructed inputs are marked CONSTRUCTED on screen.** The scores `[1, 2, 3]` were
chosen by hand (the chapter says the same of its own, line 134), and the pizza / salad
/ dirt lunch is my invention. Only the labels are invented; every number under them is
computed.

**No Claude transcript appears in the video.** It makes no claim about any model's
actual output, so there was none to show and none was fabricated.

## Reproduce every number

```bash
python3 verify/verify_claims.py
```

14 named claims, standard library only — no dependencies, no network, no keys. Passes
**14/14** on Python 3.14.7 and 3.12.14; both recorded runs are in `verify/`.

`scenes.py` carries no copies of these figures. It imports the chapter's own
`probabilities()` function, computes each displayed value at render time, and asserts
the results still match the chapter's recorded tables — so the video and the evidence
cannot drift apart. An early draft hand-entered one value and got it wrong; that is
logged in `FRICTIONAL.md`, and the assertions exist so it cannot recur.

## Rebuild the video

The reel is built with [Brutalist](https://github.com/nikbearbrown/brutalist.art),
cloned separately. Full command log, per-beat authoring intent, and the one toolkit
edit required: `BUILD-PROMPT.md`.

```bash
git clone https://github.com/nikbearbrown/brutalist.art
```

```bash
cd brutalist.art && source .venv/bin/activate && ./setup
```

```bash
cd brutalist.art && source .venv/bin/activate && python runtime/scripts/generate_audio_kokoro.py <reel-folder>
```

```bash
cd brutalist.art && source .venv/bin/activate && ./art run <reel-folder>
```

```bash
cd brutalist.art && source .venv/bin/activate && ./art final <reel-folder>
```

Copy this folder's `beat_sheet.json` and `scenes.py` into `<reel-folder>` first.
**Activate the venv before anything** — the system `python3` is 3.14 and the
dependencies live in `.venv` (3.12). Skipping it makes `./setup` report five of seven
features "blocked" and point you at `pip`, which is the wrong fix.

## Files

| Path | What it is |
|---|---|
| `claude-liam-only-the-gaps.mp4` | the rendered master, 4K — via Canvas, not in this folder yet |
| `beat_sheet.json` | 12 beats, measured durations, per-beat claim IDs |
| `scenes.py` | the 8 Manim scenes; computes every on-screen number |
| `BUILD-PROMPT.md` | commands and prompts that rebuild the video |
| `SOURCES.md` | what I made, what Claude contributed, third-party assets and licences |
| `FRICTIONAL.md` | the process log — what broke, what I decided, and who did what |
| `docs/FACTCHECK.md` | every screen and voice claim with a verdict and its check |
| `docs/SHOTLIST.md` | typed work order, per beat, with the frame law |
| `docs/PROMPTS.md` | authoring intent per beat; no open slots |
| `docs/CHECKS-REPORT.md` | SHOW/HOLD/CARD classification and teaching-arc check |
| `verify/` | the verification script and both recorded runs |
| `evidence/frames/` | one still per beat, B00–B11 |
| `evidence/qc-sheet.png`, `gate-v-REPORT.md`, `layout-audit.md` | render QC |

## Two findings kept out of the runtime

Both verified, both cut to protect the one-concept rule:

- **`exp` is forced, not chosen.** Chapter line 138 justifies the exponential by
  positivity — but `x²` and `|x|` are positive too, and both break under a shift.
  `exp` is the one function where the probability ratio depends *only* on the gap. *(C4, C5)*
- **The naive form also fails downward.** At `[-800, -801]` every weight underflows to
  zero and the normalisation divides by zero. Chapter line 164 justifies
  max-subtraction only by overflow — numbers getting too *big* — and never mentions
  this direction. *(C13)*
