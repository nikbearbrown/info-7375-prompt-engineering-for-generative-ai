# PROMPTS

## The request that started this build

Aravind asked Claude Code (in the Claude desktop app, 2026-09-26) to build the
Week 1 explainer video end to end, saying they would study it before
submitting so they could explain it to a TA. The Canvas assignment brief was
pasted into the same session.

Claude chose the concept ("Three scores are not yet three chances"),
wrote the evidence script, the narration and beat sheet, the Manim scenes,
and the paperwork, and ran the Brutalist pipeline. The decisions, and what
Aravind reviewed, are recorded in SOURCES.md and FRICTIONAL.md.

## Beat-prefixed visual prompts (all filled by Manim; no open slots)

- **B00** Three large score cards, 1, 2, 3, labelled outcome 0, 1, 2. Tag them as a constructed input. End on "Are these three chances? Not yet."
- **B01** Type "Three scores are three chances.", then delete the wrong half and type "only rank three outcomes." Add the method line and "... and it has a limit."
- **B02** Show divide-by-sum on [1,2,3], [-1,2,3], [-1,0,1] with verdict underlines. Label it as not the lesson's rule.
- **B03** Show the real probabilities() source, with the input checks elided, and box the three moves in narration order.
- **B04** Reveal the columns score, minus peak, weight, total, chance on the spoken numbers. Bars grow with the chances.
- **B05** Show x 2.7183 hops between neighbouring weights, then the same hops between neighbouring chances, and contrast with divide-by-six's x 1.5000.
- **B06** Run [-1, 2, 3] through the same steps. Show that all chances are positive and that a 3-point gap is x 20.0855.
- **B07** Label the bars "chance of being sampled". List what is guaranteed and what is not established.
- **B08** Show the title, the one-line recipe, the viewer task probabilities([1, 2, 4]), and credits.

## Viewer prompt in the video (Your Turn)

"Predict probabilities([1, 2, 4]) before you run it."
