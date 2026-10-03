# SHOTLIST.md — typed work order

Reel: `yadav-shreyash-week01-softmax-max-subtraction`  ·  11 beats  ·  16:9  ·  target 3:05

Every slot is filled by the pipeline. There are no human-supplied media slots,
no pantry shopping list, no AI-generated video, and no screen recordings.

| Beat | Type | Renderer | Scene / pattern | Slot | Responsible |
|------|------|----------|-----------------|------|-------------|
| B00  | GRAPHIC | Remotion | `ClaudeComposerAsk` | `media/B00.mp4` | pipeline |
| B01  | GRAPHIC | Remotion | `BrutalistHesitantWriter` | `media/B01.mp4` | pipeline |
| B02  | GRAPHIC | Remotion | `ClaudeCodeBeat` | `media/B02.mp4` | pipeline |
| B03  | GRAPHIC | Manim | `B03_TwoColumns` | `manim/B03.mp4` | pipeline |
| B04  | GRAPHIC | Manim | `B04_Normalize` | `manim/B04.mp4` | pipeline |
| B05  | GRAPHIC | Manim | `B05_Overflow` | `manim/B05.mp4` | pipeline |
| B06  | GRAPHIC | Manim | `B06_Boundary` | `manim/B06.mp4` | pipeline |
| B07  | GRAPHIC | Manim | `B07_Interpreter` | `manim/B07.mp4` | pipeline |
| BVDT | GRAPHIC | Remotion | `ClaudeVerdictArtifact` | `media/BVDT.mp4` | pipeline |
| BHTF | GRAPHIC | Remotion | `ClaudeComposerAsk` | `media/BHTF.mp4` | pipeline |
| BOUT | GRAPHIC | Remotion | `ClaudeTitleOutro` | `media/BOUT.mp4` | pipeline |

## Timing

Audio is the clock. Kokoro `am_onyx` mp3 durations were measured first
(`mp3/beat-*.mp3`), then the five Manim scenes were retimed to match via
`evidence/pacing.json`, so the compiler retimes each clip by well under 1%
instead of slowing a short clip to fill a long beat.

| Scene | narration (s) | rendered clip (s) | error |
|-------|---------------|-------------------|-------|
| B03_TwoColumns | 20.18 | 20.00 | -0.91% |
| B04_Normalize | 20.11 | 20.08 | -0.15% |
| B05_Overflow | 19.44 | 19.50 | +0.31% |
| B06_Boundary | 19.42 | 19.42 | +0.00% |
| B07_Interpreter | 21.74 | 21.71 | -0.17% |

Measured with `ffprobe` on the rendered `manim/*.mp4`, against the
`mutagen`-measured narration mp3 for the same beat. Every clip lands
inside the compiler's ±5% silent-retime band, so no clip is slowed to fill.

## Open slots

None.
