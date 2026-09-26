# BUILD-PROMPT.md — why-subtract-the-max

The actual prompts and commands used, in order. Build date: **2026-09-22/23**.

---

## The originating prompt (verbatim)

> I'm building a Week 1 explainer video assignment for INFO7375 using the
> Brutalist toolkit that's cloned in this project. The concept is: "Why
> subtracting the maximum changes the intermediates but not the distribution"
> (from softmax/temperature sampling, Chapter 1 of the course "Randomness and
> first prompts").
> Before writing anything, do these steps in order:
>
> 1. Read this project's own README and any docs describing how scenes,
>    narration, and rendering are structured (Manim and/or Remotion, Kokoro for
>    narration). Tell me what conventions it expects for file layout before
>    creating anything.
> 2. Clone or locate the course repo if it's not already present:
>    https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai
>    — specifically I need lessons/01-randomness-and-first-prompts/code/main.py.
>    Run it and show me the exact printed output. Do not use numbers from the
>    chapter text or from memory — only use what this script actually prints
>    when run here, now.
> 3. Once I confirm the real numbers with you, build a beat_sheet.json for a
>    2:45-3:15 minute video with these beats:
>    * Hook: why does this code subtract the max before doing anything else?
>    * Setup: introduce the three scores and what softmax does at a high level
>    * Show the shift: animate raw scores -> subtract max -> exponentiate ->
>      normalize, using the real numbers from step 2
>    * Identity check: side-by-side comparison showing the shifted path and the
>      unshifted (direct exponentiation) path produce identical final
>      probabilities
>    * Why bother: the equal-large-score case [1000,1000] -> [0.5,0.5], showing
>      why the shift avoids numeric blowup
>    * Boundary statement (must appear on screen, verbatim in spirit): "This
>      shows the shifted and direct calculations agree on this input. It does
>      not prove the implementation handles every possible numeric input safely
>      — floating-point arithmetic has its own limits, and passing this test is
>      a narrower claim than 'numerically stable' in general."
>    * Close: one-sentence recap
> 4. Build the Manim scene(s) for the bar-chart animation described above using
>    the real numbers only. No invented/placeholder numbers anywhere in the
>    final render.
> 5. Write the narration script text for Kokoro matching the beat sheet.
> 6. After the video renders, generate these five files matching this project's
>    existing format conventions: README.md (my name goes as a placeholder for
>    me to fill in, the concept, why I chose it, runtime, rebuild instructions),
>    BUILD-PROMPT.md (the actual prompts/commands used, including this one),
>    SOURCES.md (chapter numbers cited, main.py output, note explicitly that no
>    Claude transcript is required for this topic since it's a pure code/math
>    demonstration), FRICTIONAL.md (log anything that broke or needed adjusting
>    along the way, dated), and confirm beat_sheet.json is finalized.
>
> Do not fabricate any numbers, transcripts, or test results at any step. If
> something fails, tell me exactly what failed rather than working around it
> silently — I need to log real friction, not a clean story.

---

## Step 1 — read the conventions

Read: `README.md`, `HOW-TO.md`, `CLAUDE.md`, `RENDER-TARGETS.md`,
`skills/make/ai-explainer/SKILL.md`, `skills/make/explainer/` (MOTION.md,
EQUATIONS.md, REMOTION.md), `runtime/scripts/generate_audio_kokoro.py`,
`runtime/scripts/build_safety.py`, `runtime/scripts/run.sh`, and the worked
example `examples/cli-explainer/brand-palette-accessibility-auditor/`.

## Step 2 — get the real numbers

```bash
cd ~/Downloads
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai
cd info-7375-prompt-engineering-for-generative-ai/lessons/01-randomness-and-first-prompts/code
python3 main.py          # run three times to confirm determinism
```

Then, because `main.py` prints only two of the objects this reel needs, a
diagnostic script imported the module and called its own `probabilities()`,
checking every recomputed stage against the function's return value. Full
method and results in SOURCES.md.

## GATE L — library-first, before authoring any beat

Mandatory per CLAUDE.md rule 8. Three searches:

```bash
./art scenes 'animated bar chart of probabilities growing from a baseline'
./art scenes 'side by side comparison two calculation paths reaching the identical result'
./art scenes 'step by step numeric transformation subtract exponentiate normalize'
./art scenes --check BarChart
```

Outcome: `BarChart` is RENDERABLE (props `title, data, accentIndex, unit`) but
carries a single series; the comparison hits are bespoke figures exposing only
a `sparkLine` prop; the transformation search was a **genuine miss**. A miss is
a punt, not a licence to slate — hence purpose-built Manim scenes.

## Steps 3–5 — author, then build audio-first

Authored `beat_sheet.json` (7 beats) and `scenes.py` (7 scene classes, every
number a module constant with provenance noted). Then:

```bash
REEL=/path/to/info7375/youtube/why-subtract-the-max

python3 runtime/scripts/generate_audio_kokoro.py "$REEL"
```

Narration is written into the beat sheet as `narration_text`; Kokoro `af_bella`
generated seven MP3s and wrote the measured `actual_duration_s` back. Those
measurements — not the estimates — are the clock:

```
B00 13.63s · B01 24.55s · B02 40.23s · B03 31.84s · B04 24.94s · B05 22.19s · B06 10.41s
total 167.79s
```

## Gate debugging (the bulk of the work)

Each of these was a failed run, diagnosed and fixed. Full detail in
FRICTIONAL.md.

```bash
# GATE F — paperwork must exist BEFORE rendering
#   wrote FACTCHECK.md, SHOTLIST.md, PROMPTS.md

# GATE A — run per scene, the way run.sh does
python3 runtime/qc/static_scene_check.py "$REEL/scenes.py" --class B00_Hook
#   ... repeated for all seven classes

# GATE W — independent WCAG / margin / chapter-on-slide pre-flight
# GATE B — post-render pixel-true layout audit  -> layout_audit.md
# GATE V — frame-level QC on the compiled reel  -> _qc/REPORT.md
python3 runtime/qc/final_frame_check.py "$REEL"
```

## Compile and master

```bash
ART_NO_DRAWTEXT=1 ./art run   "$REEL"     # review cut, all gates -> exit 0
ART_NO_DRAWTEXT=1 ./art final "$REEL"     # clean 4K master       -> exit 0
```

`ART_NO_DRAWTEXT=1` is required: without it Gate V returns 14 `edge-bleed`
blockers caused by the compiler's own review timecode, not by these scenes.
Confirmed by toggling only that variable — blockers went 14 → 0.

## Verification (not by probe alone, per CLAUDE.md rule 4)

```bash
# looked at the contact sheet and extracted late frames from B00 and B02
ffmpeg -ss 11.5 -i "$REEL/manim/B00.mp4" -frames:v 1 B00_end.png
ffmpeg -ss 33   -i "$REEL/manim/B02.mp4" -frames:v 1 B02_end.png

ffprobe -v error -show_entries stream=codec_type,codec_name,width,height \
        -show_entries format=duration -of default=nw=1 renders/why-subtract-the-max.mp4
ffmpeg -i renders/why-subtract-the-max.mp4 -af volumedetect -f null -
```

Result: 3840×2160 h264 + aac, 167.958 s, 13.4 MB, mean_volume −24.1 dB,
Gate V BLOCKER=0 MAJOR=0, Gate B audit CLEAN.

## Step 6 — paperwork

`README.md`, `BUILD-PROMPT.md` (this file), `SOURCES.md`, `FRICTIONAL.md`,
plus `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` written earlier for GATE F.

---

## One deviation from the brief, on purpose

The brief's identity-check beat asked to show the two paths "produce **identical**
final probabilities." The measured run disproves that: two of three components
differ in the final bit, max abs difference `1.1102230246251565e-16`. Writing
"identical" on screen would have been fabricating a test result, which the
brief's own closing instruction forbids. B03 shows the real per-component
differences and states **"agreement, not identity."** Raised with the user
before the beat sheet was written.
