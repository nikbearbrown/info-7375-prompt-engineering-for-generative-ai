# TYPECHECK.md — GATE T

Reel: `fixproof-pitch`  |  Checked: 2026-11-23T02:31  |  Overall: **FAIL**  |  Beats checked: 19  |  FAILs: 6

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

> **§8.10 REDUNDANCY (advisory — does not block cut):**
> Narration should DISCUSS on-screen text, not recite it.
> Exception: LITERAL beats (viewer types/copies/runs the text) are exempt.

> - §8.10 [B08] narration recites the card (1.00) — discuss it, don't read it

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | light | min-size §8.1: smallest text run 37px < floor 41px (1.9% of 2160px logical); likely a capt… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| B01 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B02 | ? | light | min-size §8.1: min text-run height 81px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B03 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B04 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B05 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B06 | ? | light | min-size §8.1: smallest text run 37px < floor 41px (1.9% of 2160px logical); likely a capt… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| B07 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B08 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B09 | ? | light | min-size §8.1: smallest text run 37px < floor 41px (1.9% of 2160px logical); likely a capt… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| B10 | ? | light | min-size §8.1: smallest text run 40px < floor 41px (1.9% of 2160px logical); likely a capt… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| B11 | ? | light | min-size §8.1: smallest text run 37px < floor 41px (1.9% of 2160px logical); likely a capt… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| B12 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B13 | ? | light | min-size §8.1: smallest text run 37px < floor 41px (1.9% of 2160px logical); likely a capt… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| B14 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B15 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B16 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeVerdictArtifact) — §8.1 hachure/crossbar fragment… | PASS | — |
| B17 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B18 | ? | light | min-size §8.1: min text-run height 43px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

### B00 (?)
- **min-size §8.1**: smallest text run 37px < floor 41px (1.9% of 2160px logical); likely a caption/label too small — increase font_size or check if this is a data label needing §7 treatment
- **contrast §8.3**: terracotta accent #D97757 on cream 2.74:1 < 4.5:1 WCAG — accent text must switch to INK #3D3929 or carry a backing plate
- **Fix:** Increase font_size in scenes.py or Remotion component

### B06 (?)
- **min-size §8.1**: smallest text run 37px < floor 41px (1.9% of 2160px logical); likely a caption/label too small — increase font_size or check if this is a data label needing §7 treatment
- **Fix:** Increase font_size in scenes.py or Remotion component

### B09 (?)
- **min-size §8.1**: smallest text run 37px < floor 41px (1.9% of 2160px logical); likely a caption/label too small — increase font_size or check if this is a data label needing §7 treatment
- **Fix:** Increase font_size in scenes.py or Remotion component

### B10 (?)
- **min-size §8.1**: smallest text run 40px < floor 41px (1.9% of 2160px logical); likely a caption/label too small — increase font_size or check if this is a data label needing §7 treatment
- **bbox-overlap §8.6b**: text-run bbox overlap 100% >= 10% — two labels are printing on top of each other: blob@(600,600)–(3239,919) ∩ blob@(1492,700)–(1566,747) (100% of smaller); separate label positions in scenes.py or Remotion component
- **Fix:** Increase font_size in scenes.py or Remotion component

### B11 (?)
- **min-size §8.1**: smallest text run 37px < floor 41px (1.9% of 2160px logical); likely a caption/label too small — increase font_size or check if this is a data label needing §7 treatment
- **Fix:** Increase font_size in scenes.py or Remotion component

### B13 (?)
- **min-size §8.1**: smallest text run 37px < floor 41px (1.9% of 2160px logical); likely a caption/label too small — increase font_size or check if this is a data label needing §7 treatment
- **Fix:** Increase font_size in scenes.py or Remotion component

---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 14 | 0 |
| min-size §8.1 | 19 | 6 |
| overflow §8.2 | 19 | 0 |
| contrast §8.3 | 19 | 1 |
| contrast-local §8.3b | 19 | 0 |
| bbox-overlap §8.6b | 19 | 1 |
| card-clip §8.13 | 19 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 7 | 1 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
