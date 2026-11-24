# TYPECHECK.md — GATE T

Reel: `coop-sponsor-check-final`  |  Checked: 2026-11-23T16:25  |  Overall: PASS  |  Beats checked: 24  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| BNAME | bookend | light | min-size §8.1: min text-run height 61px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| BBUILD | bookend | light | min-size §8.1: min text-run height 61px >= floor 41px | PASS | — |
| BIDEA | bookend | light | min-size §8.1: min text-run height 54px >= floor 41px | PASS | — |
| BWHAT | manim | light | min-size §8.1: min text-run height 67px >= floor 41px | PASS | — |
| P2 | bookend | light | min-size §8.1: min text-run height 78px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B05 | manim | light | min-size §8.1: min text-run height 60px >= floor 41px | PASS | — |
| BOS | manim | light | min-size §8.1: min text-run height 58px >= floor 41px | PASS | — |
| BGL | manim | light | min-size §8.1: min text-run height 57px >= floor 41px | PASS | — |
| BCARE | manim | light | min-size §8.1: min text-run height 56px >= floor 41px | PASS | — |
| P3 | bookend | light | min-size §8.1: min text-run height 81px >= floor 41px | PASS | — |
| B00 | manim | light | min-size §8.1: min text-run height 41px >= floor 41px | PASS | — |
| B01 | manim | light | min-size §8.1: min text-run height 72px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B02 | manim | light | min-size §8.1: min text-run height 57px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B03 | manim | light | min-size §8.1: min text-run height 218px >= floor 41px | PASS | — |
| BFIX | manim | light | min-size §8.1: min text-run height 73px >= floor 41px | PASS | — |
| B06 | manim | light | min-size §8.1: min text-run height 105px >= floor 41px | PASS | — |
| BRES | manim | light | min-size §8.1: min text-run height 91px >= floor 41px | PASS | — |
| B09 | manim | light | min-size §8.1: min text-run height 60px >= floor 41px | PASS | — |
| P4 | bookend | light | min-size §8.1: min text-run height 81px >= floor 41px | PASS | — |
| B07 | manim | light | min-size §8.1: min text-run height 60px >= floor 41px | PASS | — |
| B07A | manim | light | min-size §8.1: min text-run height 63px >= floor 41px | PASS | — |
| BAFTER | manim | light | min-size §8.1: min text-run height 63px >= floor 41px | PASS | — |
| BBAR | manim | light | min-size §8.1: min text-run height 50px >= floor 41px | PASS | — |
| BOUT | bookend | light | min-size §8.1: min text-run height 43px >= floor 41px (individual-char fallback at 2×) | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 0 | 0 |
| min-size §8.1 | 24 | 0 |
| overflow §8.2 | 24 | 0 |
| contrast §8.3 | 24 | 0 |
| contrast-local §8.3b | 24 | 0 |
| bbox-overlap §8.6b | 24 | 0 |
| card-clip §8.13 | 24 | 0 |
| kerning §8.4 | 17 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
