# Layout + contrast audit — all 25 scenes

Run 2026-11-23T22:20 on the scenes.py that
produced the delivered master. Each scene is snapshotted at every animation boundary.

- scenes audited: **25 / 25**
- snapshots inspected: **346**
- GATE B text-overlap / out-of-frame errors: **0**  ·  warnings: **11**
- GATE W (WCAG contrast + margins, palette `claude`): **25 / 25 clean**
- safe area (half-extents): ±6.3 x / ±3.4 y

## Every GATE B finding

All of them are `TEXT_ON_CURVE`: a text box that touches a stroked curve. In this film that
is deliberate in both places it happens — a number centred inside its node circle, and a
product label seated on the bottom rule. Both render legibly; GATE V (compiled frames) and
GATE T (typography) pass on all 25 beats. None is an overlap between two pieces of text.

| beat | type | severity | text | t (s) |
|---|---|---|---|---|
| B05 | TEXT_ON_CURVE | WARN | `HolmesGPT` | 1.87 |
| B06 | TEXT_ON_CURVE | WARN | `HolmesGPT` | 0.53 |
| B07 | TEXT_ON_CURVE | WARN | `AIOpsLab` | 0.0 |
| B10 | TEXT_ON_CURVE | WARN | `HolmesGPT` | 0.0 |
| B10 | TEXT_ON_CURVE | WARN | `AIOpsLab` | 0.0 |
| B10 | TEXT_ON_CURVE | WARN | `TraceCase` | 8.53 |
| B12 | TEXT_ON_CURVE | WARN | `1` | 4.2 |
| B14 | TEXT_ON_CURVE | WARN | `1` | 2.53 |
| B14 | TEXT_ON_CURVE | WARN | `2` | 2.53 |
| B14 | TEXT_ON_CURVE | WARN | `3` | 2.53 |
| B14 | TEXT_ON_CURVE | WARN | `4` | 2.53 |

| beat | snapshots | B errors | B warnings | W |
|---|---|---|---|---|
| B00 | 11 | 0 | 0 | clean |
| B01 | 16 | 0 | 0 | clean |
| B02 | 15 | 0 | 0 | clean |
| B03 | 17 | 0 | 0 | clean |
| B04 | 14 | 0 | 0 | clean |
| B05 | 13 | 0 | 1 | clean |
| B06 | 9 | 0 | 1 | clean |
| B07 | 12 | 0 | 1 | clean |
| B08 | 19 | 0 | 0 | clean |
| B09 | 13 | 0 | 0 | clean |
| B10 | 16 | 0 | 3 | clean |
| B11 | 17 | 0 | 0 | clean |
| B12 | 16 | 0 | 1 | clean |
| B13 | 13 | 0 | 0 | clean |
| B14 | 16 | 0 | 4 | clean |
| B15 | 13 | 0 | 0 | clean |
| B16 | 16 | 0 | 0 | clean |
| B17 | 11 | 0 | 0 | clean |
| B18 | 14 | 0 | 0 | clean |
| B19 | 9 | 0 | 0 | clean |
| B20 | 10 | 0 | 0 | clean |
| B21 | 15 | 0 | 0 | clean |
| B22 | 15 | 0 | 0 | clean |
| B23 | 15 | 0 | 0 | clean |
| B24 | 11 | 0 | 0 | clean |
