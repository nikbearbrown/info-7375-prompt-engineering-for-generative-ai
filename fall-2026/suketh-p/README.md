# suketh-p

A place for the public work of Suketh P — INFO 7375, Fall 2026.

## Submissions

| Week | Assignment | What it is | Status |
|---|---|---|---|
| 1 | [`week-01-video/`](week-01-video/) | **Shifted, Not Changed** — an explainer on Chapter 1's max-subtraction: why softmax subtracts the largest score before exponentiating, what that changes, and where the fix runs out | Posted here; the video goes to Canvas |
| Final project pitch | [`final-project-film/`](final-project-film/) | **Fine Print** — a 3:15 pitch for an agent that reads new-grad ML job postings for an F-1 student, quotes the sentence behind every requirement, compares it with the applicant's documented background, and stops for my approval. Nothing of the agent is built yet; the film says so on every picture of it | Posted here; the MP4 goes to Canvas (SHA-256 in the folder's README) |

## Week 1 — the short version

The concept is the **max-subtraction** (Chapter 1, Part 2, *"The subtraction that changes
nothing important"*). It is the smallest idea in the chapter — one subtraction — and the
only candidate that pairs a provable core with a failure you can actually run.

The film's claim: this code is **overflow-safe**, not *numerically stable*.

- `math.exp(1000)` raises `OverflowError`. Shift first and the same input returns
  `[0.5, 0.5]` — Chapter 1's own canonical test.
- The shift rewrites every intermediate and leaves the distribution alone, because
  `exp(−m/T)` is a common factor top and bottom.
- Measured, the shifted and direct paths differ by `1.1102230246251565e-16` — exactly 2⁻⁵³,
  half of Python's `sys.float_info.epsilon`: the answers are adjacent floats. Identical in
  algebra; in floating point merely indistinguishable.
- **What it does not establish:** `probabilities([0, −800])` returns a hard `0.0` for an
  outcome whose true share is ~`1e-348`. The cliff is `−1075 · ln 2 = −745.133219102`,
  confirmed by bisection to nine decimal places — so `−746` is simply the first integer
  past it. The subtraction protects the large end and does nothing for the small one.

## The video is on Canvas, not here

The rendered MP4 is the Canvas deliverable. This repository carries the **docs, evidence
and a description of the source** — everything a reviewer can read, run and diff. Per
[`youtube/README.md`](../../youtube/README.md), large media is not committed by default.

## Verify any claim in about a minute

Every figure in the film is reproducible from the course's own unmodified
`lessons/01-randomness-and-first-prompts/code/main.py`:

```bash
cd fall-2026/suketh-p/week-01-video
python3 evidence/verify_claims.py          # every claim beside the value the code returns
python3 evidence/boundary_analysis.py      # the cliff, derived and then measured
python3 -m unittest discover -s evidence   # 29 tests; each names the beat it defends
python3 evidence/mutation_check.py         # do those tests bite? 4/4 mutations caught
python3 evidence/gate_t_typecheck.py       # WCAG contrast, type floor, figure wiring
python3 evidence/cross_check.py            # same figures under every python3.N on PATH
```

The scripts locate the course reference by walking up from their own location, so they run
from anywhere in the repo (or set `INFO7375_REF`).

Every displayed figure is byte-identical across CPython 3.10.19, 3.12.7, 3.13.3 and
**3.14.6 — the interpreter Chapter 1 records its own run on**. Scope, stated at the size
of the evidence: four interpreters, one platform and architecture.

## AI assistance

Claude Opus 5 via Claude Code (2026-09-15 to 2026-09-24), and Claude Opus 5.5 for the
final pass on 2026-09-24. Claude wrote the evidence scripts, the Remotion scenes, the beat
sheet and the documents; what it contributed and what I decided is set out **portion by
portion** in [`week-01-video/SOURCES.md`](week-01-video/SOURCES.md) §4, and the sessions
are logged with dates in [`week-01-video/FRICTIONAL.md`](week-01-video/FRICTIONAL.md). The
narration is synthetic (Kokoro `am_onyx`, local) and disclosed on screen. Not affiliated
with or endorsed by the @NikBearBrown channel.
