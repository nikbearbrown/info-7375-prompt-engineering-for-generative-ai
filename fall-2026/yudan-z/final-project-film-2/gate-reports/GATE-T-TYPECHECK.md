# TYPECHECK.md — GATE T

Reel: `job-search-agent-film`  |  Checked: 2026-11-23T15:23  |  Overall: PASS  |  Beats checked: 15  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| BIDEA | bookend | light | min-size §8.1: min text-run height 76px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B01 | manim | light | min-size §8.1: min text-run height 68px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B02 | manim | light | min-size §8.1: min text-run height 229px >= floor 41px | PASS | — |
| B03 | manim | light | min-size §8.1: min text-run height 199px >= floor 41px | PASS | — |
| B04 | manim | light | min-size §8.1: min text-run height 563px >= floor 41px | PASS | — |
| B05 | manim | light | min-size §8.1: min text-run height 77px >= floor 41px | PASS | — |
| B06 | manim | light | min-size §8.1: min text-run height 68px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B07 | manim | light | min-size §8.1: min text-run height 87px >= floor 41px | PASS | — |
| B08 | manim | light | min-size §8.1: min text-run height 444px >= floor 41px | PASS | — |
| B09 | manim | light | min-size §8.1: min text-run height 67px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B10 | manim | light | min-size §8.1: min text-run height 42px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B11 | manim | light | min-size §8.1: min text-run height 253px >= floor 41px | PASS | — |
| B12 | manim | light | min-size §8.1: min text-run height 72px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B13 | manim | light | min-size §8.1: min text-run height 68px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| BOUT | bookend | dark | no-wordy-card §8.5: no prose payload found | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 1 | 0 |
| min-size §8.1 | 15 | 0 |
| overflow §8.2 | 15 | 0 |
| contrast §8.3 | 15 | 0 |
| contrast-local §8.3b | 15 | 0 |
| bbox-overlap §8.6b | 15 | 0 |
| card-clip §8.13 | 15 | 0 |
| kerning §8.4 | 13 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
