# BUILD-LOG.md — gate findings, fixed and accepted

Reel: `yadav-shreyash-week01-softmax-max-subtraction` · 2026-09-21

The `ai-explainer` skill requires that any gate finding is either resolved or
**explicitly justified here**. Nothing below was silently passed.

## Fixed

| Gate | Finding | Fix |
|---|---|---|
| GATE F | no `FACTCHECK.md` / `SHOTLIST.md` / `PROMPTS.md` | written before the first render |
| Manim stage | "nothing to render" — the collector regex `class ([A-Z][A-Za-z0-9]*_\w+)\(Scene\)` did not match scenes inheriting a shared base | every scene declares `(Scene)` literally; shared behaviour attached by the `@paced` decorator |
| GATE A | `'B03_TwoColumns' object has no attribute '_held'` — the gate calls `construct()` without Manim's `setup()` | initialisation made idempotent and invoked from `@paced`'s `construct` wrapper |
| GATE A | scenes could not find `evidence/evidence.json` — the gate copies `scenes.py` alone into a temp dir | lookup chain: `$WEEK01_EVIDENCE` → beside `scenes.py` → walk up. `build.sh` exports it |
| GATE A | B05, B07, then B04: "shapes never change — repeated animation" | rebuilt rather than suppressed. B05 became a growing exponent bar crossing a marked float64 ceiling; B07 animates the disagreeing entries relocating between interpreters; B04 draws its fraction bars on and rules under the merged distribution |
| GATE B | title and footer outside the ±3.4 safe area | heading buff 0.45 → 0.78, footer 0.3 → 0.68 |
| GATE B | B05: `logits = [1000, 1000]` overlapped the ceiling label; the result line overlapped the title | setup moved left; result moved to the base of the frame |
| GATE B | B06: full-precision reprs ran off-frame at x=7.96 | re-laid out as three stacked pairs |
| GATE B | B06: incoming numbers collided with the pair below | slide distance 0.95 → 0.60/0.33 |
| GATE B | B04: "label on a curve/line" — the strike-through crossed its own text | the cancelled factor now **fades out** instead of being struck. Better visual: cancellation removes a term, it does not annotate it |
| GATE V | B04 underfill 40% | scaled the columns and identity up; reordered so the identity is on screen longer |
| GATE V | B06 underfill 47% | the stacked-pair rebuild resolved it |
| **GATE T §8.3** | terracotta `#D97757` text on cream measures **2.74:1**, below the 4.5:1 floor | accent-coloured **text** switched to `#A44A32` (5.11:1, measured). Terracotta still carries every non-text mark, which is where the brand's accent law actually applies. `GOOD` also darkened `#4A7C59` → `#3C6647` (4.26:1 → 5.78:1) — it failed the same floor and had not been flagged yet |
| **GATE T §8.13** | B02 "text blob touches card right boundary" | the flagged blob was my own `brandLabel: "INFO 7375"` in the bottom row, right-aligned to the same margin as the card. §8.13 locates the card by column and then scans **every row** of those columns, so footer text aligned to the card's right margin reads as a blob touching the card boundary. Removed `brandLabel` from this beat. The code was never clipped — verified on the rendered frame |

## Corrected mid-build

My first diagnosis of the §8.13 failure was **wrong**, and it is worth recording
because the wrong answer was the plausible one.

I assumed the flagged element was `ClaudeCodeBeat`'s language badge — it is laid
out `marginLeft: 'auto'`, so it genuinely is always flush to the card's inner
edge, and `language` feeds nothing else. I set `language: ""`, re-rendered, and
**the check failed again at the identical column (3567)**. That identical column
was the evidence that the diagnosis was wrong: a real fix would have moved it.

I then replicated §8.13's own pixel logic on the rendered frame instead of
reading the component source. It reported `card_right 3567` — matching the gate
exactly — and located the offending blob at rows 1977–2014, which is *below the
card entirely*. Cropping those pixels showed `INFO 7375`: my own `brandLabel`,
right-aligned to the card's margin.

The language badge was never the problem, so `language: "python"` is restored.

## Resolved after the write-up above

**GATE V `underfill` on B01 — fixed, not accepted.**

I had written this up as an unavoidable conflict: B01 is the hesitant-writer
BLUF beat the skill mandates, it is a typing animation, and the gate samples it
at 50% and 85% of its duration when the text is only partly written. That
reasoning was sound as far as it went, and it was still the wrong conclusion.

What forced the issue: `compile.py` invokes GATE V **without** `--lenient` and
does not consult `ART_STRICT`, so `./art final` cannot emit a master while any
MAJOR exists. `ART_STRICT=0` unblocks `./art run` only. Since the review cut
carries burned-in beat labels, the master is the only usable deliverable — so
"accept and move on" was not actually available.

Measured series, each a real render scored with the gate's own
`--frames-dir` mode (50% / 85% fill):

| config | 50% | 85% |
|---|---|---|
| 4 lines @ 92 | 19% | 29% |
| 5 lines @ 104 | 17% | 26% |
| 5 lines @ 104, faster typing | 36% | 47% |
| 5 long lines @ 92 | 29% | 40% |
| 6 short lines @ 104 | 35% | 45% |
| 5 lines @ 128 | 38% | 54% |
| **+ `contextTitle`, @ 120** | **PASS** | **PASS** |

Two things I had wrong:

1. **`charMs` does not shorten the timeline.** I lowered it to 20 expecting the
   writing to finish early and hold the completed text across both sample
   points. The 50% frame still showed 3 of 5 lines — the component spreads its
   timeline across the beat regardless. Verified on the frame, not assumed.
2. **The component has a `contextTitle` prop I had not used.** It renders a
   persistent full-width heading from frame 0, so the content bounding box is
   large even while the body is still being typed. Adding it — with the body at
   120 pt — clears the floor at both sample points with the mandated component
   intact.

So the "two parts of the toolkit disagree" conclusion was premature: I had not
read the component's full prop surface before declaring the conflict
irreducible. The beat is also better for it — it now names what the summary is
instead of opening on bare text.

One content bug caught on the way: the trigger-word replacement rendered
"looks like **a** identity", ungrammatical and redundant against the next line.
The pair is now `rounding` → `algebra`, which reads correctly in place and
still performs the correction the BLUF exists to show.

The master is therefore exported with **strict gates on**. No gate finding is
accepted, and `ART_STRICT=0` is not used for the final cut.

## Not done

- No reel was published or uploaded. `./art post` was never run.
- The toolkit was not modified. Both upstream bugs recorded in `FRICTIONAL.md`
  §4 were worked around from outside.
