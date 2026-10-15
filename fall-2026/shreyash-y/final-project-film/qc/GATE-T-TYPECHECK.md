# TYPECHECK.md — GATE T

Reel: `yadav-shreyash-final-project-pitch-film`  |  Checked: 2026-10-14T03:28  |  Overall: PASS  |  Beats checked: 14  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B01 | ? | light | min-size §8.1: min text-run height 113px >= floor 41px | PASS | — |
| B02 | ? | light | min-size §8.1: min text-run height 520px >= floor 41px | PASS | — |
| B03 | ? | light | min-size §8.1: min text-run height 79px >= floor 41px | PASS | — |
| B04 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B05 | ? | light | min-size §8.1: min text-run height 45px >= floor 41px | PASS | — |
| B06 | ? | light | min-size §8.1: min text-run height 58px >= floor 41px | PASS | — |
| B07 | ? | light | min-size §8.1: min text-run height 79px >= floor 41px | PASS | — |
| B08 | ? | light | min-size §8.1: min text-run height 118px >= floor 41px | PASS | — |
| B09 | ? | light | min-size §8.1: min text-run height 1046px >= floor 41px | PASS | — |
| B10 | ? | light | min-size §8.1: min text-run height 80px >= floor 41px | PASS | — |
| BVDT | ? | light | min-size §8.1: hand-drawn pattern (ClaudeVerdictArtifact) — §8.1 hachure/crossbar fragment… | PASS | — |
| BHTF | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| BOUT | ? | light | min-size §8.1: min text-run height 92px >= floor 41px (individual-char fallback at 2×) | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 1 | 0 |
| min-size §8.1 | 14 | 0 |
| overflow §8.2 | 14 | 0 |
| contrast §8.3 | 14 | 0 |
| contrast-local §8.3b | 14 | 0 |
| bbox-overlap §8.6b | 14 | 0 |
| card-clip §8.13 | 14 | 0 |
| kerning §8.4 | 9 | 0 |
| redundancy §8.10 (advisory) | 1 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
