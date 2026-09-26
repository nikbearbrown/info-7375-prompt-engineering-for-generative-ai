# Why Subtracting the Maximum Changes the Intermediates but Not the Distribution

**INFO 7375 — Prompt Engineering for Generative AI · Week 1 explainer**

**Author:** Meena P
**Submitted:** 2026-09-26

> Name given as first-name + last-initial to match the repository policy stated
> in `fall-2026/README.md` ("No IDs and no full names are stored here"). The
> Canvas archive carries the full name in its filename, as that submission
> requires.

---

## The concept

`softmax` turns scores into probabilities by exponentiating each score and
dividing by the total. The reference implementation in Week 1 does something
the textbook formula never mentions: before it exponentiates anything, it finds
the largest score and subtracts it from every score.

```python
peak = max(logits)
weights = [math.exp((x - peak) / temperature) for x in logits]
```

This video answers two questions about that line. **Does it change the answer?**
(Effectively no — the distribution is preserved.) **Then why is it there?**
(Because without it, realistic inputs overflow and you get no answer at all.)

The reel walks the real arithmetic for `[1, 2, 3]` stage by stage, puts the
shifted and unshifted paths side by side at full precision, and then shows the
case that justifies the whole trick: `[1000, 1000]` returns exactly
`0.5, 0.5` with the shift and raises `OverflowError` without it.

## Why I chose it

Three reasons.

It is a place where **the code disagrees with the formula you were taught**, and
the disagreement is the lesson. A one-line deviation that looks like noise turns
out to be load-bearing.

It is **falsifiable end to end**. Every number in the video came out of running
the course's own `main.py`; nothing is illustrative. That also made it a good
test of whether I could keep a video honest under a no-fabrication rule.

And it has a **clean boundary**. Demonstrating agreement on one input is not the
same as proving numerical stability, and the video says so on screen rather than
letting the demo imply more than it earned. Getting that distinction right felt
more valuable than another "here's how softmax works" explainer.

## Runtime

**2:50.8** (170.8 s) — inside the 2:45–3:15 target.

Duration is mostly an output here, not a target: the seven Kokoro narration
tracks were generated and measured first, and their real lengths are the master
clock every visual conforms to. The one exception is the silent title card,
whose 3 s is a chosen length because it carries no narration to measure.

| Beat | Act | Seconds |
|---|---|---|
| BINTRO | Title card (silent) | 3.00 |
| B00 | Hook | 13.63 |
| B01 | Setup | 24.55 |
| B02 | Show the shift | 40.23 |
| B03 | Identity check | 31.84 |
| B04 | Why bother | 24.94 |
| B05 | Boundary statement | 22.19 |
| B06 | Close | 10.41 |

Master: 3840×2160, h264 + aac, mean volume −24.1 dB.

The title card was added as a **new first beat**, not by renumbering: compile.py
walks `beats` in array order rather than by sorted id, so inserting at index 0
left every existing beat id, clip, mp3 and measured duration untouched.

## A note on the video file

The rendered master `why-subtract-the-max.mp4` (3840×2160, 2:50.96, 14.2 MB) is
committed alongside these files.

It had to be added with `git add -f`: the course repo's root `.gitignore` still
carries a blanket `*.[mM][pP]4` rule under the comment *"Keep generated
audio/video out of Git, at any depth and in any case."* The newer, scoped rules
above it (`youtube/**/*.mp4`) do not reach `fall-2026/`, but the blanket rule
does. Other Week 01 submissions in this directory are committed the same way,
and the assignment lists the rendered mp4 as a required deliverable — so the
force-add follows established practice here rather than inventing one.

The file is 14.2 MB, under the 25 MB threshold the repo inventories separately.

Rebuilding regenerates the video from `scenes.py` + `beat_sheet.json`. The
*numbers* are deterministic — the sampler is seeded and `main.py` reproduces
byte-identically — but the rendered mp4 is not claimed to be bit-identical
across machines; encoder and font-rasteriser differences are not something this
project has tested for.

## Files

| File | What it is |
|---|---|
| `beat_sheet.json` | the single source of truth — beats, narration, durations |
| `scenes.py` | the seven Manim scenes; all real numbers are module constants at the top |
| `FACTCHECK.md` | every on-screen claim, its verdict, and whether it was printed or derived |
| `SOURCES.md` | provenance, `main.py` output, and why no Claude transcript is required |
| `SHOTLIST.md` | per-shot direction and gate notes |
| `PROMPTS.md` | open-slot prompts (there are none — every beat is pipeline-filled) |
| `FRICTIONAL.md` | everything that broke, dated |
| `BUILD-PROMPT.md` | the prompts and commands actually used |
| `mp3/` | generated narration |
| `manim/` | rendered beat clips |
| `_qc/`, `qc-sheet.png`, `layout_audit.md` | QC evidence |

## Rebuilding

Requires the `brutalist.art` toolkit. From the toolkit root, with `REEL` set to
this folder:

```bash
REEL=/path/to/info7375/youtube/why-subtract-the-max
python3 runtime/scripts/generate_audio_kokoro.py "$REEL"   # audio = the clock
ART_NO_DRAWTEXT=1 ./art run   "$REEL"                      # review cut + QC gates
ART_NO_DRAWTEXT=1 ./art final "$REEL"                      # clean 4K master
```

The master lands in `<toolkit>/renders/` by default; pass `--out DIR` to put it
elsewhere.

**Three things you need to know before rebuilding:**

`ART_NO_DRAWTEXT=1` is **required**, not cosmetic. Without it Gate V fails with
14 `edge-bleed` blockers on every frame — caused by the review timecode the
compiler burns 16 px from the frame edge, not by anything in these scenes.
See FRICTIONAL.md item 16.

The toolkit needs **six uncommitted fixes** to run on Windows at all (Python 3.13
manim pin, ffmpeg font-path escaping, UTF-8 text I/O, and others). They live in
the toolkit working tree, not here. See FRICTIONAL.md items 1–5.

To regenerate all beats from scratch rather than reusing cached clips, delete
`manim/*.mp4` first — filled slots are skipped.

## Verifying the numbers

Nothing needs to be taken on trust:

```bash
cd <course-repo>/lessons/01-randomness-and-first-prompts/code
python3 main.py
```

should print the three probabilities shown in B01 and B02. The derived values
(intermediates, the direct path, `[1000,1000]`) are reproduced by the script
recorded in SOURCES.md.
