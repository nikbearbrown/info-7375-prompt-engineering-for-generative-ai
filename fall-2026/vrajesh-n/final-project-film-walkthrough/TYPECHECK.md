# TYPECHECK.md — GATE T

Reel: `early-bird-final-film`  |  Checked: 2026-11-23T22:58  |  Overall: **FAIL**  |  Beats checked: 7  |  FAILs: 1

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B01 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B02 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B03 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B04 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B05 | ? | light | contrast-local §8.3b: per-blob contrast 2.94:1 < 3.0:1 — text unreadable on actual local b… | **FAIL** | Use INK on cream; add backing plate under accent text |
| B06 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |

---

## Failures requiring action before cut

### B05 (?)
- **contrast-local §8.3b**: per-blob contrast 2.94:1 < 3.0:1 — text unreadable on actual local background (blob@(264,966)–(427,993) fg≈(61, 58, 58) bg≈(129, 129, 144)); move label off its background or change text color
- **Fix:** Use INK on cream; add backing plate under accent text

---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 7 | 0 |
| min-size §8.1 | 7 | 0 |
| overflow §8.2 | 7 | 0 |
| contrast §8.3 | 7 | 0 |
| contrast-local §8.3b | 7 | 1 |
| bbox-overlap §8.6b | 7 | 0 |
| card-clip §8.13 | 7 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
