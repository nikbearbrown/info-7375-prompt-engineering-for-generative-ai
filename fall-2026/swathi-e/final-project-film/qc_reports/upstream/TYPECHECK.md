# TYPECHECK.md — GATE T

Reel: `cite-or-refuse-pitch`  |  Checked: 2026-10-13T20:41  |  Overall: PASS  |  Beats checked: 13  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B01 | ? | dark | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B02 | ? | dark | min-size §8.1: min text-run height 160px >= floor 41px | PASS | — |
| B03 | ? | dark | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B04 | ? | dark | min-size §8.1: min text-run height 125px >= floor 41px | PASS | — |
| B05 | ? | dark | min-size §8.1: min text-run height 246px >= floor 41px | PASS | — |
| B06 | ? | dark | min-size §8.1: min text-run height 125px >= floor 41px | PASS | — |
| B07 | ? | dark | min-size §8.1: min text-run height 125px >= floor 41px | PASS | — |
| B08 | ? | dark | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B09 | ? | dark | min-size §8.1: min text-run height 174px >= floor 41px | PASS | — |
| B10 | ? | dark | min-size §8.1: min text-run height 68px >= floor 41px | PASS | — |
| B11 | ? | dark | min-size §8.1: min text-run height 93px >= floor 41px | PASS | — |
| B12 | ? | dark | min-size §8.1: min text-run height 316px >= floor 41px | PASS | — |
| B13 | ? | dark | min-size §8.1: min text-run height 41px >= floor 41px (individual-char fallback at 2×) | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 0 | 0 |
| min-size §8.1 | 13 | 0 |
| overflow §8.2 | 13 | 0 |
| contrast §8.3 | 13 | 0 |
| contrast-local §8.3b | 13 | 0 |
| bbox-overlap §8.6b | 13 | 0 |
| card-clip §8.13 | 13 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
