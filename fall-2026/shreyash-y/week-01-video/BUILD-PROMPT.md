# BUILD-PROMPT.md

Everything needed to rebuild this reel from an empty machine: the commands, and
the Claude Code prompts that produced the folder in the first place.

Free pipeline only — Kokoro narration, Manim + Remotion rendering, all local.
No API keys, no paid generation, no account, no upload.

---

## Part 1 — Rebuild (commands)

### 0. Prerequisites

```bash
brew install ffmpeg pkgconf cairo pango
```

`pkgconf` matters: without it `pycairo` fails to build and the whole Python
install dies. Node ≥ 20 is required for Remotion. LaTeX is **not** required —
no scene in this reel uses `MathTex`.

### 1. Clone the toolkit and the course

```bash
git clone https://github.com/nikbearbrown/brutalist.art
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai course
```

### 2. Python 3.11 environment

`manim` and `kokoro-onnx` are installed into a 3.11 venv rather than a newer
default interpreter:

```bash
python3.11 -m venv .venv-brutalist
source .venv-brutalist/bin/activate
pip install -r brutalist.art/requirements.txt
```

### 3. Toolkit install

```bash
cd brutalist.art && ./setup --install
```

**`./setup` exits 1 on a clean clone** — its ElevenLabs guard matches the
toolkit's own shipped example reels, so the readiness table never prints. See
`FRICTIONAL.md` §4a. The install steps themselves run fine. Verify readiness
directly instead:

```bash
python3 -c "import PIL, manim, faster_whisper, kokoro_onnx; print('deps ok')"
python3 runtime/scripts/setup_smoke_kokoro.py     # expect: kokoro synth OK
```

### 4. Build this reel

One command, from inside this folder:

```bash
./build.sh /path/to/brutalist.art /path/to/course /path/to/another/python3
```

The third argument is optional — it is the second interpreter used for the
cross-check in beat B07. Without it, `evidence.json` has no `crosscheck` block
and B07 cannot render. Any Python of a *different* minor version works; I used
3.11.15 against a 3.14.6 default.

`build.sh` runs, in order:

```bash
# 1. evidence — every on-screen number is generated here, never typed
python3 evidence/run_evidence.py --course <course> --compare <other python3>

# GATE A copies scenes.py alone into a temp dir; this is how it finds the data
export WEEK01_EVIDENCE="$PWD/evidence/evidence.json"

# 2. audio is the clock
python3 <toolkit>/runtime/scripts/generate_audio_kokoro.py .

# 3. render + compile (Manim 4K, Remotion, conform to audio, QC gates A/W/B/V)
<toolkit>/art run .
```

### 5. Master

```bash
<toolkit>/art final .
```

### Re-timing, if you change the narration

The Manim scenes are pinned to the measured mp3 durations via
`evidence/pacing.json`. If you edit `narration_text`, regenerate the audio and
recompute the multipliers, or the compiler will slow the clips to fit:

```bash
python3 evidence/run_evidence.py --course <course> --compare <other python3>
python3 <toolkit>/runtime/scripts/generate_audio_kokoro.py .
# then re-measure: set each pace to 1.0, render -ql, read the HOLDSUM line and
# the clip duration, and set pace = (target - (natural - held)) / held
```

---

## Part 2 — The prompts that built it

These are the asks, in order, that produced this folder in one Claude Code
session on 2026-09-21. They are paraphrased to their operative content — the
session was conversational, and `FRICTIONAL.md` records where I pushed back.

**1 — Choose the concept against real output, not against the reading**

```
Run lessons/01-randomness-and-first-prompts/code/main.py and show me the
actual numbers. Then compute the naive softmax path and the max-shifted path
side by side at full float precision, and tell me every way in which they
differ. Do not round anything yet.
```

This is the prompt that produced the whole video: the answer contained the
±1 ULP discrepancy, which is what made this concept worth three minutes.

**2 — Make the numbers impossible to fabricate**

```
Write evidence/run_evidence.py. It must import the course main.py unmodified,
compute both paths, and write evidence.json with provenance (course commit,
interpreter, platform). scenes.py will read that file. No figure may be typed
into a scene by hand.
```

**3 — Verify the cause instead of narrating it**

```
Do not assert that CPython changed sum(). Write a probe that distinguishes
compensated from naive summation and run it on every interpreter on this
machine. Put the probe's output in evidence.json and check whether math.exp
itself differs. I want the measurement on screen, not the explanation.
```

**4 — Build the scenes**

```
Write scenes.py with five Manim scenes reading evidence.json: the two weight
columns and the shared e^3 factor; the normalisation and the cancellation;
the overflow; the ULP boundary; the interpreter comparison. Claude palette,
no MathTex - this machine has no LaTeX.
```

**5 — Audio is the clock**

```
Generate the Kokoro narration first, measure the real mp3 durations, then
retime the Manim scenes to match so compile.py never has to slow a clip.
Write the multipliers to evidence/pacing.json.
```

**6 — Check the frames, not the code**

```
Render each scene at low quality, extract a frame near the end, and show it to
me. I want to see what the viewer sees.
```

This is what caught the B04 strike-throughs landing on the wrong glyphs and
the B05 error string running off the canvas. Both looked fine in the source.

**7 — Fix the gates honestly**

```
GATE A rejects B05 and B07 for "shapes never change". Do not suppress the
gate or add decorative motion. Rebuild those beats so the movement carries
the idea.
```

Result: B05 became a growing exponent bar crossing a marked float64 ceiling,
and B07 animates the disagreeing entries relocating between interpreters. Both
are better than what the gate rejected.

**8 — Strip the house persona**

```
Remove the "Liam, in for Bear" narration and the @NikBearBrown chip. This is
coursework; the explanation is mine. Use my name and an INFO 7375 chip, and
record the deviation in SOURCES.md.
```
