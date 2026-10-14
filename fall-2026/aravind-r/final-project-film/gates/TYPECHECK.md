# TYPECHECK.md — GATE T

Reel: `aravind-r-readback-pitch`  |  Checked: 2026-10-14T14:34  |  Overall: PASS  |  Beats checked: 10  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| BIDEA | bookend | light | min-size §8.1: min text-run height 60px >= floor 41px | PASS | — |
| B01 | manim | light | min-size §8.1: min text-run height 53px >= floor 41px | PASS | — |
| B02 | manim | light | min-size §8.1: min text-run height 51px >= floor 41px | PASS | — |
| B03 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B04 | manim | light | min-size §8.1: min text-run height 51px >= floor 41px | PASS | — |
| B05 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| B06 | manim | light | min-size §8.1: min text-run height 51px >= floor 41px | PASS | — |
| B07 | manim | light | min-size §8.1: min text-run height 53px >= floor 41px | PASS | — |
| B08 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| BOUT | bookend | dark | min-size §8.1: min text-run height 44px >= floor 41px (individual-char fallback at 2×) | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 0 | 0 |
| min-size §8.1 | 10 | 0 |
| overflow §8.2 | 10 | 0 |
| contrast §8.3 | 10 | 0 |
| contrast-local §8.3b | 10 | 0 |
| bbox-overlap §8.6b | 10 | 0 |
| card-clip §8.13 | 10 | 0 |
| kerning §8.4 | 8 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
