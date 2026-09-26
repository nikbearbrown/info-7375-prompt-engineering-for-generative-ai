# SOURCES — claude-liam-only-the-gaps

## Source material

| What | Where from | Licence / status |
|---|---|---|
| Chapter 1 — *Randomness and first prompts* | INFO 7375 course text (`01-randomness-and-first-prompts.md`) | course material, not redistributed here |
| `probabilities()` / `sample()` reference implementation | reproduced verbatim from that chapter, lines 170–182 and 228–241 | course material; reproduced for verification, attributed in every file that uses it |
| Recorded probability + count tables used as cross-checks | same chapter, lines 206–210 and 253–257 | course material |
| Brutalist toolkit (Kokoro, Manim, Remotion pipeline) | https://github.com/nikbearbrown/brutalist.art | public repository, cloned unmodified |
| Kokoro-82M TTS voice `am_onyx` | bundled in `brutalist.art/runtime/models/kokoro/` | ships with the toolkit; local, free, no account |
| EB Garamond / Oswald | `brutalist.art/runtime/fonts` | bundled with the toolkit |
| Claude UI compositions (`ClaudeComposerAsk`, `ClaudeVerdictArtifact`, `ClaudeTitleOutro`) | toolkit's registered Remotion library | part of the toolkit |

**No third-party images, video, music, or stock assets are used.** No AI-generated
imagery. No paid API calls. Nothing was downloaded from the network during the build.

**No Claude transcript appears in the video.** The reel makes no claim about any
model's actual output, so there was no transcript to show — and none was fabricated.

## What I made

- The concept framing: that the max-subtraction cancellation *is* shift-invariance, and
  that shift-invariance means "everything here is bad" has no output shape.
- The pizza / rotten-kitchen explanation used to carry it in plain language.
- The experimental program: the 2⁵³ threshold, the two failure modes, the negative
  control, and the prediction-then-confirmation structure of Act III.
- All numbers in the video, computed by `verify_claims.py` and recomputed at render
  time by `scenes.py`. The `[1, 2, 3]` input and the lunch labels are constructed and
  marked as such on screen.

## What Claude contributed

Claude (Opus 5, via Claude Code) was used throughout this assignment, and it did a
large share of the production work. Stated plainly:

**Claude wrote:** `verify_claims.py` (all 13 claims), `scenes.py` (all six Manim
scenes), `beat_sheet.json`, the narration script, and the paperwork in this folder
(`FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md`, `FRICTIONAL.md`, `README.md`, this file).
It ran the pipeline, diagnosed every gate failure, and produced the fixes.

**Claude found:** the exact 2⁵³ threshold; that the shift-1e16 output is digit-identical
to the recorded T=0.5 row; that both broken outputs pass a sum-to-one check; that
halving the temperature and doubling the gaps are the same operation; that the
`[-800, -801]` underflow is unmentioned by the chapter; and that its own first search
method was invalid.

**Claude also made a mistake that mattered:** it hardcoded a fabricated value for
`softmax([1, 3.4, 3])` into an early draft of `scenes.py`. It caught this by checking
against a computed result, corrected it, and restructured the file so that no number
can be hand-entered again. This is logged in `FRICTIONAL.md`.

**I directed.** Full dated record in `FRICTIONAL.md`; in summary I:

- set the standard on day one — anyone should understand it — and enforced it twice;
- **rejected the first topic shortlist** as a reranking of the professor's own list,
  duplicable by anyone with the same chapter and the same tools;
- chose the framing sentence the video is built on and titled after;
- demanded the plain-language and "what is this for" pass that produced the pizza
  and rotten-kitchen explanations;
- pushed back that shift-invariance alone is a textbook fact, which forced the
  experimental work that found 2⁵³ and the two failure modes;
- scope-checked that the bug was not eating the concept, producing the runtime split
  and the two guards that keep it an explanation;
- chose the ending — the rounding failure over the underflow failure — after making
  Claude justify its recommendation;
- ran `verify_claims.py` myself rather than trusting the reported result (14/14);
- flagged that `C1`/`B03`-style labels were being used undefined;
- **rejected the first finished cut** as correct but incomprehensible, which produced
  the two explainer beats and the full plain-language rewrite.

**What I am responsible for:** all of it. I can derive the cancellation
`exp((z−m)/T) = exp(z/T)·exp(−m/T)` and explain why the common factor cancels; why
`exp` is forced rather than chosen; why 2⁵³ is the threshold and not an arbitrary
number; why doubling the gaps is identical to halving the temperature; why a
sum-to-one test cannot detect either failure; and why binary search was the wrong
tool for a non-monotonic predicate.

## Attribution note

Per the course AI policy and `brutalist-video-sources.md`, the division above is
reported as it actually happened rather than minimised. The evidence trail —
`verify_claims.py`, its two recorded JSON runs, the QC artifacts, and `FRICTIONAL.md` —
is included so any claim in the video can be checked independently of my account of it.
