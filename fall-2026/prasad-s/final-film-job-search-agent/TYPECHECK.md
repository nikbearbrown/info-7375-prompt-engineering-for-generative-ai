# TYPECHECK.md — GATE T

Reel: `job-search-agent-film`  |  Checked: 2026-11-22T19:53  |  Overall: PASS  |  Beats checked: 17  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B1 | manim | light | min-size §8.1: min text-run height 70px >= floor 41px | PASS | — |
| B2 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B3 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B4 | manim | light | min-size §8.1: min text-run height 57px >= floor 41px | PASS | — |
| B5 | manim | light | min-size §8.1: min text-run height 57px >= floor 41px | PASS | — |
| B6 | manim | light | min-size §8.1: min text-run height 57px >= floor 41px | PASS | — |
| B7 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B8 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B9 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B10 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B11 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B12 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B13 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B14 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B15 | manim | light | min-size §8.1: min text-run height 41px >= floor 41px | PASS | — |
| B16 | manim | light | min-size §8.1: min text-run height 43px >= floor 41px | PASS | — |
| B17 | manim | light | min-size §8.1: min text-run height 63px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 0 | 0 |
| min-size §8.1 | 17 | 0 |
| overflow §8.2 | 17 | 0 |
| contrast §8.3 | 17 | 0 |
| contrast-local §8.3b | 17 | 0 |
| bbox-overlap §8.6b | 17 | 0 |
| card-clip §8.13 | 17 | 0 |
| kerning §8.4 | 17 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
