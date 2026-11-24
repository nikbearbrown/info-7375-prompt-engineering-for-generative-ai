# TYPECHECK.md — GATE T

Reel: `sponsorscout-final-project-film`  |  Checked: 2026-11-23T21:41  |  Overall: PASS  |  Beats checked: 16  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| BOPEN | manim | light | min-size §8.1: min text-run height 70px >= floor 41px | PASS | — |
| P1A | manim | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |
| P1B | manim | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |
| P1C | manim | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |
| P2A | manim | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |
| P2B | manim | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |
| P3A | manim | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |
| P3B | manim | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |
| P3C | manim | light | min-size §8.1: min text-run height 47px >= floor 41px | PASS | — |
| P3D | manim | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |
| P3E | manim | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |
| P4A | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| P4B | manim | light | min-size §8.1: min text-run height 42px >= floor 41px | PASS | — |
| P4C | manim | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |
| P4D | manim | light | min-size §8.1: min text-run height 44px >= floor 41px | PASS | — |
| BOUT | bookend | light | no-wordy-card §8.5: no prose payload found | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 1 | 0 |
| min-size §8.1 | 16 | 0 |
| overflow §8.2 | 16 | 0 |
| contrast §8.3 | 16 | 0 |
| contrast-local §8.3b | 16 | 0 |
| bbox-overlap §8.6b | 16 | 0 |
| card-clip §8.13 | 16 | 0 |
| kerning §8.4 | 15 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
