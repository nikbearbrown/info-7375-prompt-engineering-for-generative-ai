# TYPECHECK.md — GATE T

Reel: `job-search-agent-final-project-film`  |  Checked: 2026-11-22T22:06  |  Overall: PASS  |  Beats checked: 11  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B01 | ? | dark | min-size §8.1: min text-run height 91px >= floor 41px | PASS | — |
| B02 | ? | dark | min-size §8.1: min text-run height 173px >= floor 41px | PASS | — |
| B03 | ? | dark | min-size §8.1: min text-run height 282px >= floor 41px | PASS | — |
| B04 | ? | dark | min-size §8.1: min text-run height 123px >= floor 41px | PASS | — |
| B05 | ? | dark | min-size §8.1: min text-run height 125px >= floor 41px | PASS | — |
| B06 | ? | dark | min-size §8.1: min text-run height 135px >= floor 41px | PASS | — |
| B07 | ? | dark | min-size §8.1: min text-run height 123px >= floor 41px | PASS | — |
| B08 | ? | dark | min-size §8.1: min text-run height 122px >= floor 41px | PASS | — |
| B09 | ? | dark | min-size §8.1: min text-run height 123px >= floor 41px | PASS | — |
| B10 | ? | dark | min-size §8.1: min text-run height 123px >= floor 41px | PASS | — |
| B11 | ? | dark | min-size §8.1: min text-run height 143px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 0 | 0 |
| min-size §8.1 | 11 | 0 |
| overflow §8.2 | 11 | 0 |
| contrast §8.3 | 11 | 0 |
| contrast-local §8.3b | 11 | 0 |
| bbox-overlap §8.6b | 11 | 0 |
| card-clip §8.13 | 11 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
