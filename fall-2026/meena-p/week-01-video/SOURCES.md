# SOURCES.md — why-subtract-the-max

## Primary source

**Course repo:** https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai
**Cloned:** 2026-09-22 · **HEAD at clone:** `8f590fa` ("Add Frictional teaching module")
**File:** `lessons/01-randomness-and-first-prompts/code/main.py`
**Companion doc named in that file's header:** `lessons/01-randomness-and-first-prompts/docs/en.md`

**Chapter cited:** Chapter 1 — *Randomness and first prompts*. The chapter is
cited as the origin of the concept; **no number in this video comes from the
chapter prose.** (The chapter number is also absent from every frame: Gate W's
SLATE-RUNNER recap law bans chapter numbers on screen. It appears in the
narration only.)

**Environment of record:** Windows 11, Python 3.13.5, `math` / `random` /
`collections` from the standard library only.

---

## Tier 1 — PRINTED by `python3 main.py`

Run in `lessons/01-randomness-and-first-prompts/code/`. Byte-identical across
three consecutive runs (the sampler is seeded, `seed=7`):

```
$ python3 main.py
{
  "probabilities": [
    0.09003057317038046,
    0.24472847105479764,
    0.6652409557748218
  ],
  "counts": {
    "1": 268,
    "2": 630,
    "0": 102
  }
}
```

Used on screen: the three `probabilities` values (B01, B02, B03).

**`counts` is deliberately unused.** It is the output of `sample()`, which is
about the sampler, not the distribution. Recorded here for completeness; it
appears in no beat.

---

## Tier 2 — DERIVED by importing `main.py` and calling its own functions

`main.py` prints only the two objects above. The intermediates, the unshifted
path and the `[1000,1000]` case are **never emitted by it**, so they could not
be sourced from its stdout. They were produced by loading the module with
`importlib` and calling its real `probabilities()`, on this machine.

Two safeguards, both of which held:

1. `demo()` was called first and reproduced `main.py`'s stdout exactly,
   confirming the same code was under test.
2. Each recomputed stage was compared against the function's own return value.
   **Max absolute difference: `0.0`** — the recomputation is not an
   approximation of what the function does, it is what the function does.

### Shifted path — `[1, 2, 3]`, temperature 1.0

| stage | value |
|---|---|
| `peak = max(logits)` | `3` |
| `x - peak` | `-2, -1, 0` |
| `exp(...)` | `0.1353352832366127`, `0.36787944117144233`, `1.0` |
| `total = sum(...)` | `1.5032147244080551` |
| `w / total` | `0.09003057317038046`, `0.24472847105479764`, `0.6652409557748218` |
| `sum(probabilities)` | `0.9999999999999999` |

### Direct path — no max subtraction, same input

| stage | value |
|---|---|
| `exp(x)` | `2.718281828459045`, `7.38905609893065`, `20.085536923187668` |
| `total` | `30.192874850577365` |
| normalized | `0.09003057317038045`, `0.24472847105479764`, `0.6652409557748219` |

### Comparison — the measured result

```
index 0: shifted=0.09003057317038046  direct=0.09003057317038045  equal=False  diff=1.3877787807814457e-17
index 1: shifted=0.24472847105479764  direct=0.24472847105479764  equal=True   diff=0.0
index 2: shifted=0.6652409557748218   direct=0.6652409557748219   equal=False  diff=1.1102230246251565e-16
all exactly equal: False
max abs difference: 1.1102230246251565e-16
```

**The two paths are not bit-identical.** B03 says so. See FACTCHECK.md for the
correction this forced against the original brief.

In the B03 table the per-row difference column is shown at 3 significant
figures (`1.39e-17`, `0.0`, `1.11e-16`) so it fits the title-safe width; the
exact `1.1102230246251565e-16` appears on the same frame in the verdict line.

### Equal large scores — `[1000, 1000]`

| | |
|---|---|
| `probabilities([1000, 1000])` | `0.5`, `0.5` (exactly) |
| `x - peak` | `0, 0` |
| `exp(0)` | `1.0`, `1.0` |
| direct path: `math.exp(1000)` | raises `OverflowError: math range error` |
| `sys.float_info.max` | `1.7976931348623157e+308` |

The `OverflowError` is a caught-and-printed real exception, not a predicted one.

---

## Reproducing Tier 2

The deriving script is not shipped in this folder (it is a diagnostic, not part
of the reel). It does exactly this:

```python
import importlib.util, math
spec = importlib.util.spec_from_file_location("lesson01_main", "<path>/main.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

m.demo()                          # must match main.py stdout
official = m.probabilities([1, 2, 3], 1.0)

peak    = max([1, 2, 3])
weights = [math.exp((x - peak) / 1.0) for x in [1, 2, 3]]
total   = sum(weights)
assert [w / total for w in weights] == official      # holds exactly

w_direct = [math.exp(x / 1.0) for x in [1, 2, 3]]
p_direct = [w / sum(w_direct) for w in w_direct]     # differs by 1.11e-16

m.probabilities([1000, 1000])                        # [0.5, 0.5]
math.exp(1000)                                       # OverflowError
```

---

## On the absence of a Claude transcript

**No Claude transcript is required for this topic, and none is cited.**

This reel is a pure code-and-mathematics demonstration. Every claim it makes is
settled by running a twenty-line standard-library Python file and reading the
output. There is no model behaviour to evidence, no generated artifact to
attribute, no prompt whose response is the subject matter. The evidence is the
arithmetic, and the arithmetic is reproducible by anyone with the repo and a
Python interpreter.

A transcript would add nothing verifiable here. Where a reel's subject *is* a
model interaction, the transcript is the record and must be cited; that is not
this reel.

Claude Code was used as a build tool — authoring `scenes.py`, the beat sheet,
and this paperwork. That is tooling, not a source, and the commands used are
logged in BUILD-PROMPT.md.

---

## What I used, what I made, what Claude contributed

### Used (inputs I did not create)

- `main.py` from the course repo — the subject of the video and the origin of
  every number. Course material, not mine.
- The `brutalist.art` toolkit — the audio-first pipeline, QC gates, and compile
  machinery.

### Made (original to this submission)

- `scenes.py` — all eight Manim scenes, written for this reel. The layout, the
  four-stage chain in B02, the side-by-side table in B03, the split screen in
  B04, and the title card are original compositions.
- `beat_sheet.json` — the beat structure, act breakdown, and all narration text.
- The narration script itself — written to match the measured mechanism, not
  adapted from the chapter prose.
- All paperwork in this folder.

### Claude's contribution

Claude Code (Opus 5) was used as a build tool throughout, under direction:
it read the toolkit's conventions, ran `main.py` and the derivation script,
authored `scenes.py` and the beat sheet to specification, diagnosed the gate
failures logged in FRICTIONAL.md, and drafted this paperwork. Every number it
placed on screen was taken from a command executed on this machine, and the
commands are reproduced in BUILD-PROMPT.md so the work can be re-run
independently.

One substantive correction came out of that process and is worth naming: the
original brief asked to show the shifted and direct paths producing *identical*
probabilities. The measured run disproved it, so B03 states "agreement, not
identity" instead. See FACTCHECK.md.

**No Claude-generated prose, image, audio or video appears in the deliverable.**
The narration is written text spoken by a local TTS model; the visuals are
Manim renders of real numbers. There is no model output being passed off as
evidence, and therefore no transcript to cite.

### Third-party assets embedded in the rendered video

| Asset | Role | Licence | How verified |
|---|---|---|---|
| EB Garamond | every glyph on screen | SIL Open Font License 1.1 | read `runtime/fonts/EB_Garamond/OFL.txt` |
| Kokoro-82M (`af_bella`) | the narration audio | Apache-2.0 | as documented by the toolkit at `runtime/scripts/generate_audio_kokoro.py:5`. The `kokoro-onnx` package metadata declares **no** licence field, so confirm upstream before redistributing the audio commercially. |

### Build dependencies (tools, not embedded assets)

| Tool | Version | Licence | How verified |
|---|---|---|---|
| Manim Community | 0.19.2 | MIT | `pip show manim` |
| Pillow | 12.3.0 | MIT-CMU | `pip show Pillow` |
| NumPy | 2.5.3 | BSD-3-Clause (and others) | `pip show numpy` |
| ffmpeg | 9.0.1, Gyan.dev full build | per that build's own configuration — a "full" build links GPL components; check `ffmpeg -version` before redistributing binaries | not independently verified here |
| MiKTeX | 25.12 | per MiKTeX project | installed for Manim's LaTeX path; **not exercised by this reel** — no beat uses MathTex |

No paid service, no API key, no network call at render time. Cost: $0.00.
