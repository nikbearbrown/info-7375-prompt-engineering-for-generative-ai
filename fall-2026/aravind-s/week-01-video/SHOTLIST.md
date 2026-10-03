# SHOTLIST: typed work order

All beats are rendered by the pipeline from `scenes.py` (Manim, free and
local). No beat needs human-supplied media, stills, screen recordings, or
paid generation.

| Beat | Act | Lane | Scene class | What the viewer sees | Evidence |
|---|---|---|---|---|---|
| B00 | Hook | manim | B00_ThreeScores | Score cards 1, 2, 3; "constructed input" tag; "Are these three chances? Not yet." | constructed input |
| B01 | Overview | manim | B01_Overview | Typed misconception corrected to "only rank three outcomes"; method line; "it has a limit" | none (framing) |
| B02 | Wrong turn | manim | B02_DivideBySix | Divide-by-sum rows: works for [1,2,3], negative for [-1,2,3], ZeroDivisionError for [-1,0,1] | softmax_steps_output.txt |
| B03 | The code | manim | B03_RealCode | main.py probabilities() excerpt, three moves boxed in turn | main.py lines 9-17 |
| B04 | Worked example | manim | B04_WorkedExample | Columns score, minus peak, weight, chance with bars; total 1.5032; sum 1.0000 | softmax_steps_output.txt |
| B05 | Mechanism | manim | B05_GapMultiplier | x 2.7183 hops on weights and on chances; divide-by-six ratio 1.5000 | softmax_steps_output.txt |
| B06 | Hard case | manim | B06_NegativeScores | [-1, 2, 3] to weights and chances; all positive; gap 3 is x 20.0855 | softmax_steps_output.txt |
| B07 | Limit | manim | B07_WhatItDoesNotProve | Sampling bars; "not the chance of being right"; guaranteed vs not established | Lesson 1 notes, Chapter 1 |
| B08 | Recap | manim | B08_Recap | Title, recipe, viewer task probabilities([1, 2, 4]), credits | none |
