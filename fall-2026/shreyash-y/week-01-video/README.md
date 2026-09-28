# Subtract the Max.

**Shreyash Yadav** · INFO 7375 · Week 1 explainer video · 2026-09-21

## The concept

**Subtracting the maximum logit changes every intermediate weight but not the
resulting distribution — and that invariance is exactly what buys numerical
stability.**

From Chapter 1, Part 2: *"Why subtracting the maximum changes the intermediates
but not the distribution."* One line of the Week 1 reference implementation:

```python
peak = max(logits)
weights = [math.exp((x - peak) / temperature) for x in logits]
```

## Why this one

Because I had it backwards, and I suspect most people do. I assumed the
subtraction was an approximation that trades a little accuracy for safety with
big numbers. It is the opposite: it is an **exact algebraic identity** — every
weight is scaled by the same `e^max`, which cancels in the normalisation — and
being exact is precisely what makes it *legal* to use as a fix. The stability
is the consequence, not the justification.

It also has a boundary I could measure rather than assert, which is the part
of this chapter I actually wanted to practise.

## Runtime

**3 minutes 06 seconds** (185.75 s), 11 beats, 3840×2160, h264 + AAC.

## What the video shows

| Beat | What happens |
|---|---|
| B00 | The ask, against the real file |
| B01 | The framing most people arrive with, corrected on screen |
| B02 | The unmodified course `main.py` |
| B03 | Both weight columns, and the *same* factor `e³ = 20.085537` on every row |
| B04 | Both normalise to one distribution; the shared factor cancels and leaves |
| B05 | An exponent bar growing past the float64 ceiling at `e^709.78` → `OverflowError`; the shift drags it back to `e^0` |
| B06 | **The boundary:** the two paths are not bit-identical — ±1 ULP, and Σp = 0.9999999999999999 |
| B07 | And *where* that gap lands changes between Python 3.14.6 and 3.11.15 on the same laptop |
| BVDT | Verdict, including what this establishes and what it does not |
| BHTF | Your turn |

## The one thing this does not establish

That the two paths return **bit-identical floats**. They do not. On this
machine they differ by one unit in the last place, and the unshifted
probabilities sum to exactly `1.0` while the shifted ones sum to
`0.9999999999999999`.

Worse — and this is B07 — *which* entries disagree is not even a property of
the code. Under Python 3.14.6 the difference is `[+1, 0, −1]`; under 3.11.15 on
the same machine it is `[0, −1, −1]`. `math.exp` is bit-identical across both;
`sum()` is not, because CPython adopted compensated summation in 3.12. I
verified that behaviourally rather than citing it:
`sum([1e100, 1.0, -1e100, 1.0])` returns `2.0` on 3.14.6 and `1.0` on 3.11.15.

The gap is real and reproducible. Where it lands belongs to your interpreter.

Separately, and stated in the verdict: none of this says anything about whether
the likeliest token is the **correct** one. A numerically stable computation of
a confident wrong answer is still a wrong answer.

## Evidence discipline

**No number in this video was typed by hand.** `scenes.py` reads
`evidence/evidence.json`, which `evidence/run_evidence.py` generates by
importing the course's `main.py` *unmodified* and recording the course commit,
the interpreter, and the platform alongside the results. Change the source and
the frames change with it.

There are **no constructed illustrations** — no invented distributions, nothing
drawn for effect. There is **no Claude transcript** on screen, because none was
used as evidence for anything.

Per-claim backing is in [`FACTCHECK.md`](FACTCHECK.md).

## Where the video is

The rendered master is **not in this repository** — the course repo's
`.gitignore` excludes `*.mp4`, so it lives with the Canvas submission instead.

| | |
|---|---|
| file | `Yadav_Shreyash_INFO7375_Week01_Video.mp4` |
| runtime | 3:06 (185.75 s) |
| format | 3840x2160, h264 + AAC |
| size | 15,183,729 bytes |
| sha256 | `a85ba1729f1c82e2726906434a7c9bfb0c9e983986ebb8923d05f2896b46d6fd` |

Everything needed to **rebuild it byte-for-byte** is in this folder: run
`./build.sh` (see below). `evidence/run_evidence.py` regenerates every number
the video displays, from the unmodified course `main.py`.

## Rebuild

```bash
./build.sh /path/to/brutalist.art /path/to/course /path/to/another/python3
```

The third argument is a second Python of a different minor version — it is what
B07 compares against. Full instructions, prerequisites, and the two upstream
toolkit bugs you will hit on a clean clone are in
[`BUILD-PROMPT.md`](BUILD-PROMPT.md).

Cost to rebuild: **$0.00**. Kokoro narration, Manim and Remotion rendering, all
local. No API keys, no paid services, no upload.

**A note on the two filenames.** The toolkit names its output from the reel
slug, so a rebuild produces `yadav-shreyash-week01-softmax-max-subtraction.mp4`
(and a `-slate.mp4` review cut alongside it). The copy in this folder is that
same master renamed to the Canvas convention,
`Yadav_Shreyash_INFO7375_Week01_Video.mp4`. Same file, two naming schemes —
the toolkit's and the assignment's.

## Files

| File | What it is |
|---|---|
| `Yadav_Shreyash_INFO7375_Week01_Video.mp4` | the video |
| `README.md` | this file |
| `beat_sheet.json` | narration + visual plan, one entry per beat |
| `scenes.py` | the five Manim mechanism scenes |
| `evidence/run_evidence.py` | generates every on-screen number |
| `evidence/evidence.json` | those numbers, with provenance |
| `evidence/pacing.json` | per-scene timing, derived from the measured narration |
| `BUILD-PROMPT.md` | commands + the prompts that built it |
| `FACTCHECK.md` | every claim, and what backs it |
| `SOURCES.md` | what I used, made, and what Claude contributed |
| `FRICTIONAL.md` | the honest log |
| `BUILD-LOG.md` | every QC gate finding and how it was resolved |
| `TYPECHECK.md` | GATE T typography report (PASS) |
| `qc/GATE-V-REPORT.md` | GATE V frame QC (0 blockers, 0 majors) |
| `SHOTLIST.md` / `PROMPTS.md` | the toolkit's required work order |
| `build.sh` | one-command rebuild |

## A note on the toolkit's house style

Brutalist's default persona narrates as "Liam, in for Bear" under the
`@NikBearBrown` chip. I removed it. This is coursework and the explanation is
mine, so presenting it as another channel's content would be a false claim in
the one assignment that is specifically about not making those. The narration
voice is synthetic (Kokoro `am_onyx`, local) and disclosed as such in
`SOURCES.md`; the words are mine.
