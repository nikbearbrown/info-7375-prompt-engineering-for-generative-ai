# PROMPTS.md — why-subtract-the-max

Beat-prefixed prompts for open slots.

## There are no open slots.

Every beat in this reel is filled by the pipeline from `scenes.py` using
numbers produced by executing `main.py`. Nothing here requires a generated
image, a stock still, a screen recording, or any human-supplied asset.

That is a property of the topic: "why subtract the max" is a pure code/math
demonstration. The evidence *is* the arithmetic, and the arithmetic renders.

| Beat | Slot | Status |
|---|---|---|
| B00 | `manim/B00.mp4` | pipeline — `B00_Hook` |
| B01 | `manim/B01.mp4` | pipeline — `B01_Setup` |
| B02 | `manim/B02.mp4` | pipeline — `B02_Shift` |
| B03 | `manim/B03.mp4` | pipeline — `B03_Identity` |
| B04 | `manim/B04.mp4` | pipeline — `B04_WhyBother` |
| B05 | `manim/B05.mp4` | pipeline — `B05_Boundary` |
| B06 | `manim/B06.mp4` | pipeline — `B06_Close` |

## If a slot is ever opened

Should a future revision slate a beat, the prompt written here must name the
real artifact wanted — never a decorative stand-in. Per VOX LAW a still is used
only where the still IS the evidence. For this topic the only admissible
stills would be:

- `B00` — a screenshot of the actual `main.py` source in an editor, if the
  typeset lines are ever judged insufficient.
- `B04` — a terminal screenshot of the real `OverflowError` traceback, captured
  by running `python3 -c "import math; math.exp(1000)"`.

Both are records of something that happened, not illustration. Anything else
would be texture, and texture is not permitted here.
