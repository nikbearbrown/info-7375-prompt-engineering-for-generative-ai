# SHOTLIST — week-01-softmax-max-subtraction
## Total: 1:56.2 (116.22s) · 10 beats · 16:9 · all Manim (MathTex + EB Garamond / PT Mono)

Durations are measured Kokoro `am_onyx` narration plus a 0.8 s trailing gap on B01–B06B and B07
(`pad_gaps.py`). B00 is a silent card. B08 has no gap.

| Beat | Start | Act | Lane | Medium | Source/Pattern | Duration | Notes |
|---|---|---|---|---|---|---|---|
| B00 | 0:00.0 | TITLE | card | MANIM | TitleCard | 3.0s | Silent title card: title · "Nishant · INFO 7375 Week 1" |
| B01 | 0:03.0 | COLD OPEN | manim | MANIM | OverflowOpen | 9.89s | Recorded-output card, OverflowError in dark accent #A44A32 (WCAG AA); "The fix: one subtraction." |
| B02 | 0:12.9 | FRAMEWORK | manim | MANIM | SoftmaxDefinition | 14.05s | Heading; two columns: z = [1,2,3] + later p row (left), large softmax fraction with numerator/denominator highlights (right) |
| B03 | 0:26.9 | WORKED EXAMPLE | manim | MANIM | RawPath | 10.29s | e^z values, total 30.193 (computed label), three fractions → p |
| B04 | 0:37.2 | WORKED EXAMPLE | manim | MANIM | ShiftedPathSideBySide | 11.72s | Raw vs Shifted table; 1.000 accent; both p rows boxed |
| B05 | 0:49.0 | MECHANISM | manim | MANIM | ShiftInvariance | 12.83s | Shift-invariance derivation; e^{−m} struck through top and bottom |
| B06 | 1:01.8 | STRESS TEST | manim | MANIM | OverflowVsShifted | 15.43s | [1000,1000]: Directly → OverflowError / Subtract the max → [0,0]→[1,1]→[0.5,0.5]; brace "shared by both" |
| B06B | 1:17.2 | STRESS TEST | manim | MANIM | GapNotSize | 10.27s | Input rows [1000,1001] and [0,1] with p = ? placeholders; [1000,1001] − 1001 = [−1,0] (by hand); placeholders resolve to [0.269, 0.731], both boxed |
| B07 | 1:27.5 | HONEST DETAIL | manim | MANIM | LastDigit | 8.52s | 0.09003057317038045 vs …046; last digit boxed. Narration: "for two of the three probabilities…" |
| B08 | 1:36.0 | LIMITS | manim | MANIM | Limits | 20.22s | Three limits; then [0,−1000] Printed vs True value panel; "Prevents overflow, not rounding." |

Framing beats (ClaudeComposerAsk cold open, hesitant-writer overview, Your Turn, title outro)
deliberately skipped at the author's request — see `beat_sheet.json` `_comment_skipped_framing`.
