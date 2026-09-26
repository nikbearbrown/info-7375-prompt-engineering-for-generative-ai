# PROMPTS — claude-liam-only-the-gaps

Beat-prefixed authoring prompts. **No beat has an open slot**: four beats are
registered Remotion compositions and eight are Manim scenes authored in `scenes.py`.
There are no image or video generation prompts, no pantry requests, no third-party
assets, and no paid calls.

`./art scenes "softmax temperature"` returned a genuine library miss, logged to the
toolkit's `TEMPLATE-MISSES.md`. Per the library-first rule a miss is a design card,
not a licence to slate — so the eight maths beats were authored as Manim scenes rather
than slated or borrowed from another reel's components. Bookend prop names were read
from `./art scenes --check`, not guessed; an early draft used `title` / `lines` /
`handle` and was corrected to `artifactTitle` / `artifactLines` / `slug`.

What follows is the authoring intent per beat — the spec each scene was built against,
kept so a future rebuild can be checked against what was asked for.

- **B00** — `ClaudeComposerAsk`. Cold open on the Claude UI. The ask must land
  *answered*: three output lines stating the thesis without spending the body's
  reveals. Greeting `Atharva`; the narrator names himself in the first breath.
- **B01** — `B01_ScoreToChances`. Build the frame the whole reel lives in. Numerals
  visible on the bars, not just heights. The readout arrives at full ten-decimal
  precision immediately, so the freeze in B03 has something to be measured against.
  The CONSTRUCTED mark appears here and stays.
- **B02** — `B02_WhatIsAGap`. Define the one word everything downstream depends on,
  before anything uses it. Two number lines; the distance arrows under `1,2,3` and
  under `101,102,103` must be visibly the *same length*. That equality is the beat.
- **B03** — `B03_SlideAndFreeze`. Nudge one bar alone FIRST; the output must visibly
  redraw. Only then slide all three as a rigid group with the gap measured in the
  accent. The readout must not flicker through +1e6, +1e15, or below zero. The gap
  marker is derived from the bar geometry — an earlier version was hardcoded and
  annotated empty air.
- **B04** — `B04_ControlAndLunch`. Two negative controls beside the real thing,
  comparison held ≥2s: `x²` and `|x|` CHANGED, softmax UNCHANGED. Then relabel the
  same frame to lunch, drop every score 100, and hold a beat before revealing the
  identical answer. Second CONSTRUCTED mark for the invented labels.
- **B05** — `B05_PayoffAndStretch`. The thesis line sets alone on cream with nothing
  else animating — a real hold, not a transition. Then temperature is *shown*, never
  asserted: SLIDE moves everything and the output holds; STRETCH pulls the gaps apart
  and the favourite's slice grows; SQUASH closes them and the slices even out. Both
  directions land on recorded rows (gaps ×2 = T 0.5, gaps ×0.5 = T 2.0).
- **B06** — `B06_OutOfDigits`. Show the digits actually running out. A 16-cell box
  nearly empty for a score of `3`, completely full for a 16-digit score; then the
  three values we wanted against the three that can be stored, with the arrows going
  from "1 apart" to "2 apart". The whole comparison must be on screen before the
  midpoint — the frame is sampled there and a half-built beat reads as empty.
- **B07** — `B07_PredictConfirm`. The scan first, break marked past 2⁵³. Then the
  prediction typed into an accent-framed card and HELD with nothing computed. The
  confirmation lands only after that hold. Prediction before computation is the point;
  reversing the order destroys it. The headline is a number a person can hold — "past
  about 9 quadrillion" — with the exact 2⁵³ figure small underneath.
- **B08** — `B08_FlatAndCheck`. Collapse the three scores onto one value, flatten the
  output, then place both wrong answers side by side and stamp each with the passing
  check. Un-highlighted elements never below ~40% opacity.
- **B09** — `ClaudeVerdictArtifact`. 0.5s lead pause, then "Let's recap with Claude."
  (the prior beat is Liam, not Bear). Recap lines are bare sentences — the card numbers
  them. The scope limit and the invalid search method are ON the card, not merely
  spoken.
- **B10** — `ClaudeComposerAsk`, greeting `Your turn.` The prompt must be runnable by
  the viewer on their own machine with no key, and it is read in full
  (`props.command` == `narration_text`).
- **B11** — `ClaudeTitleOutro`. Title re-read as the sign-off, `@Atharva` on the card,
  then "Liam, in for Atharva."
