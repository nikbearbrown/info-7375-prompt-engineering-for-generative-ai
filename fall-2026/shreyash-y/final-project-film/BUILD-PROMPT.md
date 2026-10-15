# BUILD-PROMPT.md — Quote It or Refuse. (ClaimCheck pitch)

## Executive summary

How to rebuild this film from scratch: the commands first, then the prompts I gave
Claude Code that produced the folder. Everything runs locally and for free: no API
keys, no paid generation, no account, no upload.

---

## Part 1 — Rebuild (commands)

### 0. Prerequisites (macOS)

```bash
brew install ffmpeg pkgconf cairo pango
```

Node >= 20 is needed for Remotion. LaTeX is not needed (no `MathTex` in `scenes.py`).

### 1. Toolkit and Python environment

```bash
git clone https://github.com/nikbearbrown/brutalist.art
python3.11 -m venv .venv-brutalist
source .venv-brutalist/bin/activate
pip install -r brutalist.art/requirements.txt
cd brutalist.art && ./setup --install && cd ..
```

Built against toolkit commit `6a8380a` (2026-09-20), Manim Community 0.18.1.

### 2. Build

From this folder, with the venv active:

```bash
./build.sh /path/to/brutalist.art
```

`build.sh` runs, in order:

```bash
export CLAIMCHECK_REEL="$PWD"                                   # lets the gates' isolated copy of scenes.py find beat_sheet.json + evidence/
python3 <toolkit>/runtime/scripts/generate_audio_kokoro.py .    # 14 narration mp3s; their lengths are the clock
<toolkit>/art run .                                             # gates F, L, A, W -> render -> gate B -> compile -> visual QC + type check
<toolkit>/art final . --out .                                   # clean master (default output is <toolkit>/renders/)
```

The Manim scenes read each beat's measured `actual_duration_s` from `beat_sheet.json`
and place their events at fractions of it, so if you change the narration you only
need to regenerate the audio and rebuild.

The Dovetail evidence in beat B10 is read from `evidence/dovetail-pytest-2026-10-07.txt`.
To refresh it, re-run the tests in the Dovetail repo and save the output in that file
(`python -m pytest -q -p no:warnings`), with a new date in the filename.

---

## Part 2 — The prompts that built it

Claude Code sessions on 2026-10-07 and 2026-10-14. These are my asks, in order, cut down
to what they actually asked for. `FRICTIONAL.md` records what went wrong in between.

**1 — Plan it**

```
plan this  [pasted: the Final Project Pitch Film assignment]
```

Claude proposed reusing my Reallocation Engine recipe and drafted a plan and brief.

**2 — Change the project**

```
cant we change the final project?
go with option 1, rewrite the brief
```

Option 1 was the insurance-claims document Q&A tool with a citation checker (ClaimCheck).

**3 — The beat sheet**

```
go ahead and build the beat sheet
```

Claude read the toolkit's ai-explainer skill and my Week 1 beat sheet, checked which scene
components can actually render (`./art scenes --check ...`), and confirmed Dovetail's test
count (`pytest --collect-only -q` -> 47) before putting it in the narration.

**4 — Close the open questions**

```
do this [the three todos] and fill it
```

Claude re-ran Dovetail's tests (47 passed) and saved the output as evidence. It then
asked me the three questions it could not answer for me. My answers: yes, I tried both
alternatives; no classmate blind questions; don't mention Cybersenz.

**5 — Build and submit**

```
lets complete it ? today is the deadline
```

Claude generated the audio, wrote `scenes.py`, previewed every scene at low resolution,
fixed the layout problems it found, wrote the paperwork the gates require, ran the
toolkit's full gated build, and assembled the submission folder.
