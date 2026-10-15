# TYPECHECK.md — GATE T

Reel: `checkedsql-pitch`  |  Checked: 2026-10-14T16:14  |  Overall: PASS  |  Beats checked: 14  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| BIDEA | bookend | light | min-size §8.1: min text-run height 59px >= floor 41px | PASS | — |
| BDEFS | bookend | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B00 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B01 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B02 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B03 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B04 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B05 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B06 | manim | light | min-size §8.1: min text-run height 63px >= floor 41px | PASS | — |
| B07 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B08 | manim | light | min-size §8.1: min text-run height 63px >= floor 41px | PASS | — |
| B09 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B10 | manim | light | min-size §8.1: min text-run height 50px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| BOUT | manim | light | min-size §8.1: min text-run height 63px >= floor 41px | PASS | — |

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
| kerning §8.4 | 12 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
