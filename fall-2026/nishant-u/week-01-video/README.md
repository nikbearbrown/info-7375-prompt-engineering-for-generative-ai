# Why subtracting the maximum changes the intermediates but not the distribution

**Author:** Nishant U · INFO 7375, Week 1
**Video:** `week-01-softmax-max-subtraction.mp4` — 1:56 (116.4 s), 3840×2160, 24 fps

## Concept

Softmax turns scores into probabilities. Subtracting the largest score from every score before
exponentiating changes every in-between number (the largest weight becomes exactly 1), but the
final probabilities are the same, because the same factor e^{−m} multiplies the top and bottom of
the fraction and cancels. The film shows this on real output from `maxsub_runs.py`: it works on
[1, 2, 3], it prevents the overflow on [1000, 1000] and [1000, 1001], and it does not prevent the
underflow on [0, −1000].

**Why I chose it:** I chose this because it has a real, visible failure (an actual OverflowError) and a one-line fix, so I could show the mechanism with real output instead of just describing it.

## What is in this folder

| File | What it is |
|---|---|
| `week-01-softmax-max-subtraction.mp4` | The final 4K master |
| `beat_sheet.json` | The beat sheet: narration, visuals, labels, measured durations |
| `maxsub_runs.py` / `maxsub_runs.stdout.txt` | The script whose printed output supplies every number on screen, and its saved output |
| `manim/scenes.py` | One Manim scene per beat |
| `pad_gaps.py` | Adds the 0.8 s pause after each narrated beat except the last |
| `mp3/` | Kokoro narration per beat. Created by the rebuild, not included. |
| `FACTCHECK.md` | Every on-screen number and spoken claim, its source and date |
| `SHOTLIST.md`, `PROMPTS.md` | Toolkit paperwork required for a final build |
| `FRICTIONAL.md`, `SOURCES.md`, `BUILD-PROMPT.md` | Assignment write-ups |
| `_qc/MANUAL-QC.md`, `_qc/REPORT.md` | QC logs (manual, Gate V) |
| `TYPECHECK.md` | Gate T typography report. Created by the rebuild, not included. |
| `brutalist-fixes.diff` | Local fixes to the toolkit needed to run it on Windows |

## Rebuild from this folder

Requirements: the Brutalist toolkit at `~/brutalist.art` (with `brutalist-fixes.diff` applied and
`./setup --install` run for Kokoro), Python 3.12, Manim 0.18.1, a LaTeX install (MiKTeX was
used), and ffmpeg on PATH. Commands are for Git Bash.

`maxsub_runs.py` expects the course repo cloned at
`%USERPROFILE%\info-7375-prompt-engineering-for-generative-ai` (`~/info-7375-prompt-engineering-for-generative-ai`
in Git Bash). It imports `probabilities()` from
`lessons/01-randomness-and-first-prompts/code/main.py` there, and fails if the repo is elsewhere.

```bash
cd ~/week-01-video

# 1. Evidence: rerun the script; compare against the saved output
python maxsub_runs.py > maxsub_runs.stdout.new.txt
diff maxsub_runs.stdout.txt maxsub_runs.stdout.new.txt && echo "output matches"

# 2. Narration (Kokoro am_onyx, local, free), then the 0.8 s inter-beat pauses
python ~/brutalist.art/runtime/scripts/generate_audio_kokoro.py ~/week-01-video
python pad_gaps.py

# 3. Visuals: render each beat's Manim scene at 4K into manim/<BID>.mp4
cd manim
for pair in B00:TitleCard B01:OverflowOpen B02:SoftmaxDefinition B03:RawPath \
            B04:ShiftedPathSideBySide B05:ShiftInvariance B06:OverflowVsShifted \
            B06B:GapNotSize B07:LastDigit B08:Limits; do
  b=${pair%%:*}; c=${pair##*:}
  python -m manim render -r 3840,2160 --fps 24 --media_dir ../_manim_build \
         --disable_caching -v ERROR scenes.py "$c"
  cp "$(find ../_manim_build/videos -name "$c.mp4" | head -1)" "$b.mp4"
done
cd ..

# 4. Clean 4K master (runs Gate T, Gate F and Gate V; refuses to build on a failure)
cd ~/brutalist.art
bash ./art final ~/week-01-video --out ~/week-01-video
```

Step 2 regenerates every beat's audio. Kokoro output can vary slightly between runs, so the
durations (and the total runtime) may differ by a fraction of a second from this build.
