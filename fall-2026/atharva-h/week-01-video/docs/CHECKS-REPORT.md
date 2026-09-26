# CHECKS-REPORT — claude-liam-only-the-gaps

Written before the first slate compiled, per the PROOF GATE exit condition.

```
12 SHOW / 0 justified-HOLD / 0 PUNT-flagged
Teaching arc: FRAMEWORK ✓ | WORKED EXAMPLE ✓ | FALSIFIABILITY ✓
```

## Per-beat classification

| Beat | Class | Artifact named in `shot` | Notes |
|---|---|---|---|
| B00 | SHOW | `ClaudeComposerAsk` | ask lands answered |
| B01 | SHOW | `B01_ScoreToChances` | framework beat — the frame the reel lives in |
| B02 | SHOW | `B02_WhatIsAGap` | **definition beat** — defines the term the rest depends on |
| B03 | SHOW | `B03_SlideAndFreeze` | worked example; the hero |
| B04 | SHOW | `B04_ControlAndLunch` | negative control, held side by side ≥2s |
| B05 | SHOW | `B05_PayoffAndStretch` | thesis + temperature shown as gap-stretching |
| B06 | SHOW | `B06_OutOfDigits` | **explainer beat** — the digits running out, and the gaps doubling |
| B07 | SHOW | `B07_PredictConfirm` | prediction held with nothing computed, then confirmed |
| B08 | SHOW | `B08_FlatAndCheck` | falsifiability beat — the passing test that proves nothing |
| B09 | SHOW | `ClaudeVerdictArtifact` | scope limit and invalid method on the card |
| B10 | SHOW | `ClaudeComposerAsk` | scaffolded viewer task, runnable with no key |
| B11 | SHOW | `ClaudeTitleOutro` | title re-read |

No beat is a bare CARD. No beat is a PUNT. No slates in the final cut.

## Teaching-arc checklist

- **Framework before examples** — B01 establishes scores → chances, and B02 defines
  "gap", before any experiment runs.
- **Worked example** — B03, with real computed values at ten decimal places.
- **Falsifiability** — B08 shows two wrong answers passing the reference check; B09
  states what the reel does not establish.
- **Scaffolded viewer task** — B10 is runnable on the viewer's machine, stdlib only.
- **Four bookends** — B00 ask, B09 verdict, B10 your-turn, B11 title outro.
- **No-source-no-verdict** — every numeric claim carries a claim ID traceable to
  `verify_claims.py`; see `FACTCHECK.md`.

## Library-first record

`./art scenes "softmax temperature"` → genuine miss, logged to `TEMPLATE-MISSES.md`.
`./art scenes --check` confirmed `ClaudeComposerAsk`, `ClaudeVerdictArtifact` and
`ClaudeTitleOutro` RENDERABLE; their prop names were read from the library rather than
guessed (an early draft used `title`/`lines`/`handle` and was corrected to
`artifactTitle`/`artifactLines`/`slug`). The eight math beats were authored as Manim
scenes because the library genuinely had no component for them.

## Gate results (final run)

| Gate | Result |
|---|---|
| GATE L — beat-mix lint | clean |
| GATE A — static pre-flight | 8/8 scenes clean |
| GATE W — contrast / margins / overlap | 8/8 scenes clean |
| GATE B — layout audit | 0 errors, 0 warnings |
| GATE V — frame QC on the compiled cut | BLOCKER 0, MAJOR 0 |
| slots | 12/12 filled, 0 slates |

Known accepted warning: `graphic` carries 66% of beats, above the ~40% guidance.
Rationale in `FRICTIONAL.md`.

**Gates are necessary, not sufficient.** With all of the above green, reading the
contact sheet and a full-resolution frame still found the B03 gap marker annotating
empty space — and watching the whole cut found that it never defined its own central
term. Neither is visible to a gate. See `FRICTIONAL.md`.
