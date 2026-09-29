# SHOTLIST — Same Odds, Smaller Numbers (iteration 2)

Typed work order. Everything is filled by the free local pipeline: no slates, pantry media, stock footage, generated imagery or sound effects.
**Motion language:** nothing pops in; eased moves of about 0.4–0.6 s; the score chips travel B02 → B03 → B04; T = 1 stays pinned top-left from B02 to B08; one terracotta accent per beat, on a shape, when the narration points at it (word clock from `mp3/words.json`).

| Beat | Lane | Fill | What moves (and why) | Output |
|---|---|---|---|---|
| BTTL | card | Remotion `FormACard` | Title → subtitle → colophon build line by line; held 2.5 s after the narration | `media/BTTL.mp4` |
| B00 | manim | `B00_ColdOpen` (Claude composer rebuilt) | Prompt types; "running main.py…"; the three verbatim reply lines type in; "identical to 15 decimal places" underlined + tag "claim — checked later"; date stamp | `manim/B00.mp4` |
| B01 | bookend | Remotion `BrutalistHesitantWriter` | Types the misconception, corrects "answer" → "arithmetic" | `media/B01.mp4` |
| B02 | manim | `B02_Rule` | Formula (typeset SVG, largest element); chips drop into the z_i slot one at a time, on "one", "two", "three"; T = 1 pins to the corner | `manim/B02.mp4` |
| B03 | manim | `B03_DirectRoute` | Opens on B02's last frame; chips travel into the column; x climbs beside exp(x); the weights build a stacked bar at true widths; the stack squashes to unit width (probabilities); 0.6652 turns terracotta | `manim/B03.mp4` |
| B04 | manim | `B04_ShiftedRoute` | Opens on B03's last frame; chips move onto a number line (gap 1, gap 1); the line slides left by 3, the gaps unchanged; chips read −2, −1, 0; a tiny shifted stack (same scale) stretches onto B03's unit bar: same partition; footnote pays off B00's claim | `manim/B04.mp4` |
| B05 | manim | `B05_Cancel` (typeset pieces) | Shifted fraction; factored fraction built piece by piece; both exp(−m) boxed, struck and removed; the fraction collapses | `manim/B05.mp4` |
| B06 | manim | `B06_Predict` | Question held still; commit line; a 3-2-1 ring during the pause | `manim/B06.mp4` |
| B07 | manim | `B07_Overflow` | Opens on B06's card (question → title); shifted route's three steps; recorded exp(x) sweep climbs a log axis to the largest float, stops at x = 710 (OverflowError); recorded exp(1000) card | `manim/B07.mp4` |
| B08 | manim | `B08_Underflow` | Recorded commands shown first; true-size marker; recorded exp(−x) sweep falls, losing digits, through the smallest float to 0.0; outputs land as they are spoken; prevents / does not prevent | `manim/B08.mp4` |
| BVDT | manim | `BVDT_Takeaways` | Five takeaways, each on its spoken phrase; the limit line underlined | `manim/BVDT.mp4` |
| BHTF | manim | `BHTF_YourTurn` (composer rebuilt) | The prompt types word by word as it is read; both held-back clauses underlined on "It holds back…" | `manim/BHTF.mp4` |
| BOUT | bookend | Remotion `ClaudeTitleOutro` (+ handle patch) | Title restate; "Aravind Ravi · INFO 7375" | `media/BOUT.mp4` |

Post-compile: `add_markers.py` burns a section marker into the top-right corner of every beat except the title card and outro.
Pacing: `add_holds.py` pads each narration with its `hold_after_s` (0.6–2.5 s) so the final state of each beat stays readable.
