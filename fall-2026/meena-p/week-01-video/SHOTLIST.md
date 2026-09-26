# SHOTLIST.md — why-subtract-the-max

Typed work order. Seven beats, all filled by the pipeline (Manim). **No open
slots, no pantry stills, no human capture required** — this reel is a pure
code/math demonstration, so every frame is generated from the real numbers.

Runtime: **170.79 s (2:50.8)** — 167.79 s of measured narration plus a 3 s
silent title card. Audio is the clock for every beat that has narration.

| Beat | Act | Scene class | Slot | Owner | Measured audio |
|---|---|---|---|---|---|
| BINTRO | TITLE | `BINTRO_Title` | `manim/BINTRO.mp4` | pipeline | — (silent, 3 s) |
| B00 | HOOK | `B00_Hook` | `manim/B00.mp4` | pipeline | 13.63 s |
| B01 | SETUP | `B01_Setup` | `manim/B01.mp4` | pipeline | 24.55 s |
| B02 | MECHANISM | `B02_Shift` | `manim/B02.mp4` | pipeline | 40.23 s |
| B03 | IDENTITY | `B03_Identity` | `manim/B03.mp4` | pipeline | 31.84 s |
| B04 | MOTIVATION | `B04_WhyBother` | `manim/B04.mp4` | pipeline | 24.94 s |
| B05 | BOUNDARY | `B05_Boundary` | `manim/B05.mp4` | pipeline | 22.19 s |
| B06 | CLOSE | `B06_Close` | `manim/B06.mp4` | pipeline | 10.41 s |

---

## Per-shot direction

**BINTRO — Title card.** Three seconds, silent. Course line at top; the full
title across three lines with "but not the distribution" in terracotta; a rule
beneath it with a marker that travels its length; week and topic line under
that. No narration, so the beat sets `"silent": true` and compile.py fills its
audio slot with `anullsrc`. Inserted as a new first beat — no existing beat was
renumbered, because compile.py walks `beats` in array order rather than by
sorted id.

**B00 — Hook.** The two real source lines from `main.py` (14–15) in a hairline
box, attributed. Beneath: "Why subtract first?" in terracotta, then the
sub-line "Nothing in the math asks for it." Question only; no answer yet.

**B01 — Setup.** Left: three score chips `1 / 2 / 3`. Middle: a `softmax`
block captioned "exponentiate, then normalise". Right: three terracotta
probability bars labelled `0.0900 / 0.2447 / 0.6652`. Footer states the two
invariants (positive, sums to 1).

**B02 — Mechanism.** The spine of the reel. Four columns revealed left to
right — `raw` → `− max (3)` → `exp( · )` → `÷ 1.5032` — three real values in
each, arrows between. Final column in terracotta. Bottom band re-draws the
resulting distribution as bars, with `sum = 0.9999999999999999` set small
beneath it (an honest detail, not an error).

**B03 — Identity.** Four-column table: score label, shifted value, direct
value, `|difference|`. Values at full `repr()` precision so the final-digit
disagreement is legible. Differences that are non-zero are terracotta; the
exact-zero row is muted. Verdict line: `max |difference| = 1.1102230246251565e-16`,
then **"agreement, not identity"** set large.

**B04 — Motivation.** Split by a vertical hairline. Left, the shift succeeds:
`[1000,1000]` → `− max` → `0, 0` → `exp` → `1.0, 1.0` → two equal 0.5 bars.
Right, the direct path fails: `exp(1000)`, the largest float for scale, and
the real exception text `OverflowError: math range error` boxed in terracotta.
Closing line: "not a worse answer — no answer at all."

**B05 — Boundary.** MANDATORY. The boundary statement set large across the
safe area, first sentence in ink, the qualifying clause in terracotta, a
rule down the left margin. No decoration. Do not trim this beat to save
runtime.

**B06 — Close.** "The intermediates change." / "The distribution does not."
then the one-line takeaway and the course attribution.

---

## Gate notes

- Gate V title-safe inset is x 96–1824, y 54–1026 on 1920×1080. In Manim units
  that is x ±6.4, y ±3.6; `scenes.py` provides `fit()` (FIT_W 12.2, FIT_H 6.9)
  and every composed group is passed through it.
- Gate V also fails < 55 % coverage of the safe area as underfill, which is why
  B02 carries a bottom bar band and B03/B05 set type large rather than centring
  a small block.
