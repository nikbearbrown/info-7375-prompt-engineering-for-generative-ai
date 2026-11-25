# TYPECHECK.md — GATE T

Reel: `seeded-faults-project`  |  Checked: 2026-11-23T12:24  |  Overall: PASS  |  Beats checked: 15  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| E1 | manim | light | min-size §8.1: min text-run height 837px >= floor 41px | PASS | — |
| E2 | manim | light | min-size §8.1: min text-run height 69px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| E3 | manim | light | min-size §8.1: min text-run height 69px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| I1 | manim | light | min-size §8.1: min text-run height 66px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| I2 | manim | light | min-size §8.1: min text-run height 69px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| I3 | manim | light | min-size §8.1: min text-run height 78px >= floor 41px | PASS | — |
| M1 | manim | light | min-size §8.1: min text-run height 69px >= floor 41px | PASS | — |
| M2A | manim | light | min-size §8.1: min text-run height 223px >= floor 41px | PASS | — |
| M2B | manim | light | min-size §8.1: min text-run height 70px >= floor 41px | PASS | — |
| M3 | manim | light | min-size §8.1: min text-run height 70px >= floor 41px | PASS | — |
| M4 | manim | light | min-size §8.1: min text-run height 76px >= floor 41px | PASS | — |
| V1 | manim | light | min-size §8.1: min text-run height 69px >= floor 41px | PASS | — |
| V2 | manim | light | min-size §8.1: min text-run height 76px >= floor 41px | PASS | — |
| V3 | manim | light | min-size §8.1: min text-run height 42px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| BOUT | manim | light | min-size §8.1: min text-run height 69px >= floor 41px (individual-char fallback at 2×) | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 0 | 0 |
| min-size §8.1 | 15 | 0 |
| overflow §8.2 | 15 | 0 |
| contrast §8.3 | 15 | 0 |
| contrast-local §8.3b | 15 | 0 |
| bbox-overlap §8.6b | 15 | 0 |
| card-clip §8.13 | 15 | 0 |
| kerning §8.4 | 15 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
