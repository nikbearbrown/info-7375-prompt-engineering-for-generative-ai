# SHOTLIST — claude-tom-river-moves-the-bank

Typed work order. **Nothing here is owed by a human.** Zero pantry stills, zero
archive slots, zero AI-generated media. Every frame is a deterministic Remotion
render from source in this repository, so there is no `SHOPPING.md` and Gate D2
closes empty.

## The spine

```
B00  cold open             ClaudeComposerAsk          (reused)
B01  hesitant-writer BLUF  BrutalistHesitantWriter    (reused)
  ACT I    B02        The problem: one word, one row
  ACT II   B03–B05    The honest setup, and steps 1–2
  ACT III  B06–B07    Step 3, and the chapter's sentence computed
  ACT IV   B08–B09    The boundary: the ledger, then the statement
BVDT verdict               ClaudeVerdictArtifact      (reused)
BHTF your turn             ClaudeComposerAsk          (reused)
BOUT title restate         ClaudeTitleOutro           (reused, locked card)
```

No act-divider cards. Even at 3:51 they would spend ~12s carrying structure the
`act` fields already carry; the sibling reels use them because they run 10
minutes. **Act IV is deliberately two beats:** B08 enumerates the limits as a
ledger, B09 lands the single most important one as a full-frame sentence. The
enumeration is for the careful viewer; the statement is the one thing a viewer
should leave with.

## GATE L — what the library already had

```
./art scenes "attention vectors embedding dot product softmax"
```

8 candidates, **none about attention** (top: BrandAgentMapper 6.0,
FinanceDotPlot 5.5, AlgArtOrganicTurbulence 4.0). A genuine miss → seven design
cards, not seven slates.

**Reused unchanged:** `ClaudeComposerAsk`, `BrutalistHesitantWriter`,
`ClaudeVerdictArtifact`, `ClaudeTitleOutro`, and the `Ch1Chrome` primitives
(`Ch1Frame` / `Panel` / `Kicker` / `Chip` / `Arrow` / `Stamp` / `Bar`) built for
the sibling chapter-1 reels. The new scenes inherit this reel's eyebrow, serif
title, spark line and credit from `Ch1Frame`, so a layout fix lands on all seven.

**Added to `Ch1Chrome` (additive, existing scenes untouched):** `useSpAt` /
`useDrawAt` — reveals keyed to a FRACTION of the beat's own duration instead of
absolute frames, so a re-measured beat stays correct. Plus `whiteSpace: nowrap`
on `Stamp` (see FRICTIONAL, 2026-09-22).

## Beat-by-beat work order

| Beat | Component | Built | What it must show |
|---|---|---|---|
| B02 | `Ch1AttnStaticRow` | NEW | Two sentence strips → one junction → one arrow into the highlighted `bank` row. A dashed, empty CONTEXT column: the missing input, drawn legible rather than struck out |
| B03 | `Ch1AttnToySetup` | NEW | Left: ledger of five simplifications + the CONSTRUCTED EXAMPLE stamp. Right: equal-scaled 2-D plane, four tokens, 45° guide |
| B04 | `Ch1AttnScores` | NEW | Query bar, then three rows of literal multiply-and-add → raw → ÷√2 → scaled. The scaling column tinted: it is a real step, not decoration |
| B05 | `Ch1AttnSoftmax` | NEW | Three scores → three weights → one unit bar assembling from three segments, running total landing on 1.000 |
| B06 | `Ch1AttnWeightedSum` | NEW | Left: the sum term by term. Right: `bank` leaving (2,2) for (1.58, 2.14), arrow drawn to scale, displacement printed |
| B07 | `Ch1AttnTwoContexts` | NEW | Two runs side by side; shared rows printed once; mirror note; the chapter's clause verbatim + citation |
| B08 | `Ch1AttnBoundary` | NEW | Two-column ledger. The right column is longer and wider **on purpose** |
| B09 | `Ch1AttnMultiHead` | NEW (rebuild) | The brief's boundary sentence full-frame and verbatim, over a density comparison: one labelled head vs a grid of unlabelled ones. Labelling the grid would claim to explain multi-head attention — the one thing this beat says the video has not done |

## Standing constraints applied

- Content band **y 232…930**, x = `SAFE` (96…1824). Type floor 24px; credits 20px.
- One terracotta moment per beat. **Documented exception:** the persistent
  CONSTRUCTED EXAMPLE stamp is terracotta on B03–B07 alongside each beat's own
  accent. The honesty label outranks accent purity; logged in FRICTIONAL.
- `durationInFrames` in `Root.tsx` are the **measured Kokoro lengths**, not
  estimates — audio-first, set after the audio stage.
- B07 holds both panels together ≥2s for the comparison.
