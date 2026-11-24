# TYPECHECK.md — GATE T

Reel: `readme-checker-film`  |  Checked: 2026-11-23T15:41  |  Overall: PASS  |  Beats checked: 21  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| BHELLO | manim | light | min-size §8.1: min text-run height 85px >= floor 41px | PASS | — |
| BIDEA | bookend | light | min-size §8.1: min text-run height 93px >= floor 41px | PASS | — |
| B00 | manim | light | min-size §8.1: min text-run height 53px >= floor 41px | PASS | — |
| B00A | manim | light | min-size §8.1: min text-run height 53px >= floor 41px | PASS | — |
| B01 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B01T | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B02T | manim | light | min-size §8.1: min text-run height 53px >= floor 41px | PASS | — |
| B06 | manim | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B06A | manim | light | min-size §8.1: min text-run height 71px >= floor 41px | PASS | — |
| B06B | manim | light | min-size §8.1: min text-run height 64px >= floor 41px | PASS | — |
| B06C | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B03 | manim | light | min-size §8.1: min text-run height 53px >= floor 41px | PASS | — |
| B04 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B05 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B05A | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B05B | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B05C | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B11 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B08 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B08A | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B14 | manim | light | min-size §8.1: min text-run height 56px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 0 | 0 |
| min-size §8.1 | 21 | 0 |
| overflow §8.2 | 21 | 0 |
| contrast §8.3 | 21 | 0 |
| contrast-local §8.3b | 21 | 0 |
| bbox-overlap §8.6b | 21 | 0 |
| card-clip §8.13 | 21 | 0 |
| kerning §8.4 | 20 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
