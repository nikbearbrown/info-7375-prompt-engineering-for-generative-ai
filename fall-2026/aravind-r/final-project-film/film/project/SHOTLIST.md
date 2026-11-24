# SHOTLIST — Readback project film (four-part brief)

Typed work order. Everything comes from the free local pipeline: Kokoro narration (`am_onyx`), Manim drawings for B01–B20 (`scenes.py`) and the patched Remotion outro. There are no slates, pantry media, stock footage, generated images or sound effects.

**Design system:** `DESIGN.md` (colour roles, type scale, grid, motion, the hero chip). Since the positioning revision (23 Nov 2026) there is no section bar: a chapter card opens each part, and corner tags (illustration, planned, vision, test case) replace the full-sentence captions on concept diagrams. **Storyboard:** `storyboard.png`; style frames in `style-frames/`.
- Every cue is a spoken word from `mp3/words.json`. Entrances are a fade with a 0.15 rise; exits finish before entrances.
- Nothing animates across a clip's midpoint (`P()`), and every scene opens on the previous scene's last frame.
- Gaps between beats are 0.35–0.55 s of silence, varied (`add_holds.py` trims each clip's edges to 0.05 s and pads its hold).
- The ground is `#F2F0E9` at every cut, the outro included (`polarity`/`background` props from my patch).

| Beat | Lane | Fill | What moves | Output |
|---|---|---|---|---|
| B01 | manim | `B01_Hook` | Frame 0 is the poster and chapter card 1: “1 · Executive summary”, “Readback”, the value line, the generic criterion chip, my name, corner tag “planned”. The poster clears and the chip drops to the bottom; an AI feature; the PM's “acceptance criteria” page, which becomes a “rubric” checklist on “rubric”; the AI judge; arrows from the rubric and the output; criterion 3 outlined on “criterion”; “what the PM meant · how the judge read it”; the judge's pass; the feature leaves and “ships” | `manim/B01.mp4` |
| B02 | manim | `B02_Stakes` | Three constructed vignettes land on “teams”, “trust” and “dies”: a support-reply bot, a document summariser and a search answer, each with one criterion chip, an output and a judge's pass. The launch-gate line on “gate”; each card stacks on “scale”; the pass stamps pulse on “passing” | `manim/B02.mp4` |
| B03 | manim | `B03_Readback` | “Readback”; the criterion chip lights; the PM and “What did you mean?”; the score appears dimmed on “trusts”; the vision: tile 1 (criteria · module 1 · Readback), the vision line, then system prompts and PRDs (later); “Readback is planned · nothing has run yet” | `manim/B03.mp4` |
| B04 | manim | `B04_Maxim` | Chapter card 2 (about 1.5 s) replaces the old near-empty frame; the generic criterion chip top right; three tool names; the Maxim AI flow builds node by node | `manim/B04.mp4` |
| B05 | manim | `B05_Orq` | The title becomes orq.ai; all three nodes leave with the old tool and come back, one by one, on their spoken words | `manim/B05.mp4` |
| B06 | manim | `B06_SpecKit` | The title becomes GitHub Spec Kit; the nodes leave and come back on their words; “clearer spec” | `manim/B06.mp4` |
| B07 | manim | `B07_Gap` | “From the tools I checked”: the three outputs appear; the criterion chip drops into an empty dashed slot; under each tool a ✗, then on “October” “not found in docs”; “names the clause behind a disagreement” | `manim/B07.mp4` |
| B08 | manim | `B08_WhyMine` | “Why Readback matters on any AI feature”; the chip lights in tile 2; three tiles build: a score, the criterion, a question; “not a rewrite”; the question tile flashes on “decision” | `manim/B08.mp4` |
| B09 | manim | `B09_TestBench` | Chapter card 3 replaces the old near-empty frame. The three things the test needs (a real AI feature, public data, human ground truth) and their ticked answers (a meeting-recap feature; the AMI Meeting Corpus · CC BY 4.0; human-written decision lists); “test case, not the product”, which then leaves for the corner tag “test case”; the method strip, the ten real meeting cards with their lengths, their DECISIONS counts and “86 decisions” | `manim/B09.mp4` |
| B10 | manim | `B10_Feature` | Strip: Recaps; the real transcript line; the CONSTRUCTED recap prompt → Claude; the real recap line; nine more recaps stack behind it; corner tag “test case” | `manim/B10.mp4` |
| B11 | manim | `B11_Rubric` | Strip: Rubric; the CONSTRUCTED rubric's clauses; on “report” C4 lands as the two-line chip “C4 · Don't report open questions as decisions”; the real ES2007a DECISIONS list slides in; C1 links to it; on “answer” the reference card flashes and ticks mark the reference answers | `manim/B11.mp4` |
| B12 | manim | `B12_Labels` | Strip: Labels; the C4 chip is swapped for its compact form and parks; 86 empty label cells, row by row; the meeting IDs pulse on “covers”; my human labels, not marked yet; the commit order draws; corner tag “planned · test case” | `manim/B12.mp4` |
| B13 | manim | `B13_Judges` | Strip: Judges; three planned judges; the C1–C5 header with the chip in the C4 slot; each judge named on its word, then the empty cells; on “measure” the names pulse and “agreement between judges —”; on “human” “judges vs my labels, decisions clause —”; on “decisions” the C1 column pulses | `manim/B13.mp4` |
| B14 | manim | `B14_Trace` | Strip: Readback; the judges' rows pull apart and the C4 cells split ✓ ✗ ✓; the trace runs up to the chip, which lights; the PM. On “real” the grid clears and the real ES2010b cards land: the transcript (“Do we want this thing to be able to be found easily?” · “I think so.” · “Sure, yeah.”), then the recap's Decisions line and AMI's “will consider”; “Does a quick yes count as a decision?” with the C4 chip; “C4 · revised by the PM” | `manim/B14.mp4` |
| B15 | manim | `B15_Have` | What I have, in three columns that fill on their words: have (ticks), account, not yet wired, planned; pulses on “repository”, “subscription” and “wired”; the status tag | `manim/B15.mp4` |
| B16 | manim | `B16_Planted` | Chapter card 4 replaces the old near-empty frame; the scorecard frame draws and its header pulses on “fail”; row 1; C1–C5 with C4 planted (the label pulses on “advance”); Readback's ring on C4 ✓, the pass condition and label pulse on “planted”; another clause ✗; noise ✗ | `manim/B16.mp4` |
| B17 | manim | `B17_Kappa` | Row 2; my human labels (86 decisions, marked by me) and each judge, the two labels pulsing on “measured”; the Cohen's kappa scale; the 0.6 bar and pass zone; the lock, the 0.6 pulsing on “fix”; the fail zone; on “fails” it flashes inverted | `manim/B17.mp4` |
| B18 | manim | `B18_BeforeAfter` | Row 3; C4 → “C4 · revised”; before “—” / after “—”; held-out meetings, locked; the up arrow; on “say” the result cell flashes inverted | `manim/B18.mp4` |
| B19 | manim | `B19_Scorecard` | The scorecard spreads to fill the frame; every Result “—” flashes inverted on “blank”; “Result: will be measured · nothing has run as of 23 Nov 2026”; on “failed” “a failed check goes on the scorecard too”; the Result header pulses | `manim/B19.mp4` |
| B20 | manim | `B20_Close` | The scorecard clears; the three checks as planned passes; the PM, “what the PM meant = what the score means · pass”; the three kinds of feature; “the goal: any AI feature”; “Readback is module 1 of a copilot for what PMs write for AI”; corner tag “planned · vision” | `manim/B20.mp4` |
| BOUT | bookend | Remotion `ClaudeTitleOutro` (my patch: handle, `tagline`, `credit`, `hideMascot`, `polarity: light`, `background: #F2F0E9`) | The end card: “Readback.”, the value line “Check that AI judges read your acceptance criteria the way you meant them.”, “Aravind Ravi · INFO 7375”, “read by a synthetic voice”, in larger type; no mascot | `media/BOUT.mp4` |

## Holds over 2.5 s

Measured on the delivered file with ffmpeg `freezedetect=n=0.003:d=2.5` (23 Nov 2026, evening, after the positioning revision). There are 5, each on a line that is being spoken, and none reaches 3 s except the end card:

| From – to (film time) | Beat | Length | What is said over it |
|---|---|---|---|
| 19.54 – 22.50 s | B02 | 2.96 s | “…And because evals are becoming the launch gate for AI…” |
| 37.29 – 40.21 s | B03 | 2.92 s | “…for what PMs write for AI. Readback is planned;…” |
| 86.04 – 88.54 s | B08 | 2.50 s | “…A score tells you something is wrong. The criterion tells…” |
| 222.96 – 225.67 s | B20 | 2.71 s | “…a PM could trust a passing score to mean what they meant.…” |
| 233.38 – 238.46 s | end of BOUT | 5.08 s | “Readback. A project film by Aravind Ravi, read by a synthetic voice.” (the end card, static by design) |

At `d=3` (the gate), the frozen time is 5.08 s, which is 2.1 % of the 238.46 s runtime: only the end card. The revision first measured 47.62 s (20.0 %), over the 15 % cap; colour flashes on large cards and soft bands, each on a spoken word, brought it down.

## Storyboard and style frames

`storyboard.png` and `style-frames/` were regenerated on 23 Nov 2026 (evening) from the final master: each beat's last frame, and four moments (B02's vignettes, B07, B14's real example at 8.6 s, B16 at 11.0 s).
