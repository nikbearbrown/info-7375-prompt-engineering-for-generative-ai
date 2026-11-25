# TYPECHECK.md — GATE T

Reel: `sponsorscout-final-project-film`  |  Checked: 2026-11-23T20:04  |  Overall: **FAIL**  |  Beats checked: 16  |  FAILs: 5

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| BOPEN | manim | light | kerning §8.4: max inter-glyph gap 147px > threshold 32px (16.3× expected 9px) — check kern… | **FAIL** | Add font='EB Garamond' to all Text() in scenes.py |
| P1A | manim | light | min-size §8.1: min text-run height 25px >= floor 20px | PASS | — |
| P1B | manim | light | kerning §8.4: max inter-glyph gap 131px > threshold 24px (19.3× expected 7px) — check kern… | **FAIL** | Add font='EB Garamond' to all Text() in scenes.py |
| P1C | manim | light | min-size §8.1: min text-run height 25px >= floor 20px | PASS | — |
| P2A | manim | light | min-size §8.1: min text-run height 25px >= floor 20px | PASS | — |
| P2B | manim | light | min-size §8.1: smallest text run 8px < floor 20px (1.9% of 1080px logical); likely a capti… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| P3A | manim | light | min-size §8.1: min text-run height 25px >= floor 20px | PASS | — |
| P3B | manim | light | min-size §8.1: min text-run height 25px >= floor 20px | PASS | — |
| P3C | manim | light | min-size §8.1: min text-run height 24px >= floor 20px | PASS | — |
| P3D | manim | light | min-size §8.1: min text-run height 25px >= floor 20px | PASS | — |
| P3E | manim | light | min-size §8.1: min text-run height 24px >= floor 20px | PASS | — |
| P4A | manim | light | min-size §8.1: min text-run height 23px >= floor 20px (individual-char fallback at 1×) | PASS | — |
| P4B | manim | light | min-size §8.1: smallest text run 19px < floor 20px (1.9% of 1080px logical); likely a capt… | **FAIL** | Increase font_size in scenes.py or Remotion component |
| P4C | manim | light | min-size §8.1: min text-run height 25px >= floor 20px | PASS | — |
| P4D | manim | light | kerning §8.4: max inter-glyph gap 399px > threshold 69px (20.2× expected 20px) — check ker… | **FAIL** | Add font='EB Garamond' to all Text() in scenes.py |
| BOUT | bookend | light | no-wordy-card §8.5: no prose payload found | PASS | — |

---

## Failures requiring action before cut

### BOPEN (manim)
- **kerning §8.4**: max inter-glyph gap 147px > threshold 32px (16.3× expected 9px) — check kern tables or Pango shaping for this font at this size
- **Fix:** Add font='EB Garamond' to all Text() in scenes.py

### P1B (manim)
- **kerning §8.4**: max inter-glyph gap 131px > threshold 24px (19.3× expected 7px) — check kern tables or Pango shaping for this font at this size
- **Fix:** Add font='EB Garamond' to all Text() in scenes.py

### P2B (manim)
- **min-size §8.1**: smallest text run 8px < floor 20px (1.9% of 1080px logical); likely a caption/label too small — increase font_size or check if this is a data label needing §7 treatment
- **Fix:** Increase font_size in scenes.py or Remotion component

### P4B (manim)
- **min-size §8.1**: smallest text run 19px < floor 20px (1.9% of 1080px logical); likely a caption/label too small — increase font_size or check if this is a data label needing §7 treatment
- **kerning §8.4**: max inter-glyph gap 684px > threshold 11px (209.5× expected 3px) — check kern tables or Pango shaping for this font at this size
- **Fix:** Increase font_size in scenes.py or Remotion component

### P4D (manim)
- **kerning §8.4**: max inter-glyph gap 399px > threshold 69px (20.2× expected 20px) — check kern tables or Pango shaping for this font at this size
- **Fix:** Add font='EB Garamond' to all Text() in scenes.py

---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 1 | 0 |
| min-size §8.1 | 16 | 2 |
| overflow §8.2 | 16 | 0 |
| contrast §8.3 | 16 | 0 |
| contrast-local §8.3b | 16 | 0 |
| bbox-overlap §8.6b | 16 | 0 |
| card-clip §8.13 | 16 | 0 |
| kerning §8.4 | 15 | 4 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
