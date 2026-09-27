# TYPECHECK.md — GATE T

Reel: `aravind-r-same-odds-smaller-numbers`  |  Checked: 2026-09-27T14:19  |  Overall: PASS  |  Beats checked: 13  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| BTTL | card | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B00 | manim | light | min-size §8.1: min text-run height 48px >= floor 41px | PASS | — |
| B01 | bookend | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| B02 | manim | light | min-size §8.1: min text-run height 55px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B03 | manim | light | min-size §8.1: min text-run height 46px >= floor 41px | PASS | — |
| B04 | manim | light | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B05 | manim | light | min-size §8.1: min text-run height 53px >= floor 41px | PASS | — |
| B06 | manim | light | min-size §8.1: min text-run height 75px >= floor 41px | PASS | — |
| B07 | manim | light | min-size §8.1: min text-run height 42px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B08 | manim | light | min-size §8.1: min text-run height 46px >= floor 41px | PASS | — |
| BVDT | manim | light | min-size §8.1: min text-run height 46px >= floor 41px | PASS | — |
| BHTF | manim | light | min-size §8.1: min text-run height 48px >= floor 41px | PASS | — |
| BOUT | bookend | light | min-size §8.1: min text-run height 66px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 1 | 0 |
| min-size §8.1 | 13 | 0 |
| overflow §8.2 | 13 | 0 |
| contrast §8.3 | 13 | 0 |
| contrast-local §8.3b | 13 | 0 |
| bbox-overlap §8.6b | 13 | 0 |
| card-clip §8.13 | 13 | 0 |
| kerning §8.4 | 10 | 0 |
| redundancy §8.10 (advisory) | 1 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
