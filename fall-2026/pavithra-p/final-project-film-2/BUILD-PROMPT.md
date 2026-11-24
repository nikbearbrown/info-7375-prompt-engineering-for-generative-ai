# BUILD-PROMPT: how to rebuild the DryRun Final Project Film

Everything is free and local: Kokoro for the voice, Manim for the drawings, ffmpeg for the cut. No API keys, no accounts, no uploads.

## 1. What you need

- macOS (or Linux) with Python 3.12, `ffmpeg`, and `cairo`, `pkg-config` and `pango` (Manim needs the last three)
- The Brutalist toolkit checked out beside this folder, at the commit used for this film:

```bash
git clone https://github.com/nikbearbrown/brutalist.art
```

```bash
git -C brutalist.art checkout b21f625
```

```bash
cd brutalist.art && python3.12 -m venv .venv && . .venv/bin/activate && ./setup --install
```

## 2. Rebuild, in order

Run from `brutalist.art/` with the venv active.

```bash
REEL=../final-project-film-2
```

a. Beat sheet (the four-part script and picture plan):

```bash
python3 $REEL/make_sheet.py
```

b. Narration, the master clock (Kokoro `af_heart`, speed 0.95), then +3 dB with a limiter:

```bash
python3 runtime/scripts/generate_audio_kokoro.py $REEL --speed 0.95 && python3 $REEL/boost_audio.py
```

c. Drawings (the toolkit's kit and props pasted in front of `scenes_body.py`):

```bash
ART_HOME=$PWD python3 $REEL/build_scenes.py
```

d. Gates and review cut (Gates F, L, A, W, B, V; every scene rendered at 4K):

```bash
./art run $REEL --height 2160
```

e. Clean master (GATE T, then the master):

```bash
./art final $REEL --height 2160 --out $REEL/exports
```

f. Sharpness on the delivered film:

```bash
python3 $REEL/sharpness_on_final.py runtime/scripts/sharpness_check.py $REEL
```

## 3. The prompts behind it

Built in one Claude Code session on 2026-11-23, from my October pitch film. The main prompts and decisions (quotes are my words; the rest is summarised):

- Pasted the professor's description of the Final Project Film and asked to start from my submitted work.
- Confirmed the film is about DryRun, the final project I pitched, not the job-search agent.
- Asked Claude Code to check the description line by line and include everything it asks for.
- Asked for a strict score of the script before rendering, then: "Apply fixes" (what the research got, a coding agent's permission prompt, dates for each step).
- Brought a ChatGPT review of the draft (22.5/25) and had each point checked against the files before applying it: the evaluation metric, two narration lines (B05, B07) and one sentence in the Frictional log. A second ChatGPT check found two appendix sentences with the old wording; both were fixed.
- Asked for a final grade as the strictest TA (23.5/25), then: "Yes, fix both" (ShellCheck and explainshell in the appendix's prior work, and fixed task counts in its evaluation).
