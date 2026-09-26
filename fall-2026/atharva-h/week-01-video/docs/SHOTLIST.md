# SHOTLIST — claude-liam-only-the-gaps

Typed work order. Every beat is either a registered Remotion composition or a Manim
scene authored in `scenes.py`. **No open slots, no pantry requests, no slates, no
paid calls.** Durations are the measured narration MP3s, which are the master clock —
never hand-tuned. Rendered master: **184.58s (3:04.6)**.

| Beat | Lane | Composition / Scene | What the viewer watches | Audio | Claim |
|---|---|---|---|---|---|
| B00 | bookend | `ClaudeComposerAsk` | the ask lands answered in three lines; greeting `Atharva` | 12.27s | — |
| B01 | manim | `B01_ScoreToChances` | scores become chances; the master frame builds; CONSTRUCTED mark appears | 17.02s | C1 |
| B02 | manim | `B02_WhatIsAGap` | **the definition.** `1,2,3` over `101,102,103` with identical distance arrows, both tagged "1 apart" | 15.15s | — |
| B03 | manim | `B03_SlideAndFreeze` | **hero.** One bar nudged → output redraws. Then all three slide, readout frozen at ten decimals | 16.62s | C3 |
| B04 | manim | `B04_ControlAndLunch` | x² CHANGED, \|x\| CHANGED, softmax UNCHANGED, held side by side. Then the rotten kitchen | 17.75s | C4 |
| B05 | manim | `B05_PayoffAndStretch` | the thesis line alone; then SLIDE (nothing), STRETCH (favourite grows), SQUASH (slices even out) | 18.65s | C12 |
| B06 | manim | `B06_OutOfDigits` | **the explainer.** A 16-cell box fills up; wanted `…993·994·995` against stored `…992·994·996`; gaps 1→2 | 17.28s | C14 |
| B07 | manim | `B07_PredictConfirm` | the scan past 2⁵³, the prediction held with nothing computed, then the gaps stretch and it matches | 17.26s | C6, C7, C12 |
| B08 | manim | `B08_FlatAndCheck` | scores collapse, output flattens, both wrong answers stamped as passing | 17.83s | C8, C9 |
| B09 | bookend | `ClaudeVerdictArtifact` | seven verdict lines, including the scope limit and the invalid method | 18.99s | C10 |
| B10 | ask | `ClaudeComposerAsk` | the viewer's prompt, read in full | 11.29s | — |
| B11 | bookend | `ClaudeTitleOutro` | title re-read, `@Atharva`; "Liam, in for Atharva" | 4.33s | — |

Beat-sheet total 184.94s; the encoded master is 184.58s. The difference is frame
quantisation at 24 fps, not a timing edit.

## Frame law

One split frame — **WHAT THE MODEL THINKS** (left: scores as bars on a number line
with zero marked) / **WHAT COMES OUT** (right: one fixed-width bar always the same
total width). Established in B01 and never abandoned. Every later beat is an
experiment run on that same frame, so the audience learns the layout once.

## Non-negotiables

- **B03's nudge cannot be cut.** The output panel must be seen moving *before* it is
  seen refusing to move, or "nothing changed" reads as a broken render.
- **Ten decimal places during the proof.** Bar heights can be redrawn; a frozen
  ten-digit readout cannot. Round to `67%` only when teaching, never when proving.
- **Bars cross below zero on screen** in B03 and B04. That is what makes "every option
  is bad" land without narration having to insist on it.
- **B07 holds the prediction with nothing computed** for ~1.7s. The audience must get
  to disbelieve it before the confirmation arrives.
- **B06 must show numbers that are actually big.** An earlier version said "very big
  numbers" over a ruler showing `1, 2, 3`; the visual contradicted the voice and the
  beat taught nothing. See `FRICTIONAL.md`, REV 3.
- **CONSTRUCTED mark** stays up through B01 and B04 — the scores and the lunch labels
  are both invented, and the rubric requires that said on screen, not only aloud.

## Palette

Cream `#FAF9F5` ground, warm ink `#3D3929`, terracotta `#D97757` as **one accent event
per scene**: B02 the distance arrows · B03 the gap measurement · B04 the UNCHANGED
verdict · B05 the stretch and squash · B06 the stored row · B07 the prediction frame ·
B08 the two check marks. No gradients, no shadows, no rounded corners, no colour-only
meaning — every accent is paired with a word.
