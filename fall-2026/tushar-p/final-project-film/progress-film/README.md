# Agent Proving Ground — progress film (through M5)

**Name:** Tushar Patel
**Course:** INFO 7375 Prompt Engineering, Final Project Film (progress version)
**Working title:** Agent Proving Ground — progress film (through M5)
**Target role:** Software engineer, agent infrastructure
**Runtime:** 3:24 (203.917 s, 3840×2160, 24 fps, H.264 + AAC, 20.4 MB)
**Film:** `agent-proving-ground-progress.mp4`, SHA-256 `d5b507681caaf91e977c480557c65dc408e858e2dec9a6d6181d65404869e886`

This film **supersedes nothing**. The October pitch in `../` (`agent-proving-ground.mp4` and its files) stays exactly as graded. This folder is new.

## What the film is

A 13-beat progress film. It covers what Agent Proving Ground is, what already exists, and what ran from M0 through M5: the Go harness, the policy and human gate, the 16-task suite, the isolation tests, and the held-out comparison of two system prompts. It ends with the next steps and what would count as failure.

- **Narration:** my approved BEAT-PLAN.md (Nov 23), word for word, except B4 (below). It is voiced with the same local Kokoro voice as the October pitch (`am_onyx`), one sentence at a time.
- **REAL beats (B06–B12)** show text captured from my repo on Nov 23, read-only, in terminal-style frames. Each frame's title bar shows the source path and the source's own date, and the top rail says "Real output". The commands and full output are in `evidence/`.
- **CONSTRUCTED beats (B01–B05, B13)** are drawn diagrams, labelled "Constructed" in the top rail for the whole beat.
- **Tense:** past tense for what ran (M0–M5); "will" for what comes next.
- No Claude responses, logos, people, mascots or channel styling are on screen.

### The one narration change: B4

The October PROJECT-BRIEF.md names only E2B and Langfuse. I chose to use its wording and drop the tools it doesn't mention. The Drupal sentence is new and is kept (sourced in SOURCES.md).

| | B4 narration |
|---|---|
| **Before** (BEAT-PLAN) | Pieces of this already exist. E2B and Runtime give agents sandboxes. Langfuse and Raindrop trace and evaluate model calls. oh-my-pi is a harness for coding agents. And a Drupal project, AI Proving Ground, grades what an agent actually saved instead of what it reports, but only for Drupal sites. |
| **After** (in the film) | Pieces of this already exist. E2B provides sandboxes for running AI-generated code. Langfuse records LLM traces and scores. And a Drupal project, AI Proving Ground, grades what an agent actually saved instead of what it reports, but only for Drupal sites. |

## Folder contents

| File | Purpose |
|---|---|
| `agent-proving-ground-progress.mp4` | The film (4K master from `./art final`) |
| `BEAT-PLAN.md` | My approved beat plan, verbatim |
| `NUMBER-CHECK.md` | Every number in the narration checked against the captures before rendering (all 18 match) |
| `PROJECT-BRIEF.md` | The seven questions, plus "Exists today (through M5)" and "Will exist". Drafted by Claude Code for my review |
| `beat_sheet.json` | Narration, visual plan, measured durations and sentence times (the build's source of truth) |
| `BUILD-PROMPT.md` | The exact commands that rebuild the film, and the prompt that produced it |
| `SOURCES.md` | Tools and licences, the source of every REAL beat, what I made and what Claude contributed |
| `FRICTIONAL.md` | My log (header only; the entries are mine to write) |
| `evidence/` | `B6.txt` … `B13.txt`: each capture's command, date and output; `capture.sh` reruns them |
| `gates/` | Quality-gate reports, `SUMMARY.txt` and `run_gates.sh` |
| `make_sheet.py`, `sentence_audio.py`, `scenes.py` | Build files: the beat sheet, per-sentence narration and the Manim scenes |
| `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` | The paperwork the toolkit requires before it renders |

## How to rebuild

Full commands are in BUILD-PROMPT.md, Part A. In short, from the Brutalist toolkit root (commit `3a6d397`):

```bash
python3.12 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
./setup && ./art smoke
R=youtube/brutalist/agent-proving-ground-progress
mkdir -p $R/mp3 && cp <this folder>/{make_sheet.py,sentence_audio.py,scenes.py,FACTCHECK.md,SHOTLIST.md,PROMPTS.md} $R/
python3 $R/make_sheet.py && python3 $R/sentence_audio.py     # audio first
./art run $R && ./art final $R --out $R/exports               # full path, not the bare slug
bash <this folder>/gates/run_gates.sh                         # gates 01–13
```

Everything is free and local, with no API keys. Remotion isn't needed.

## Quality gates

All run against the final sheet, scenes and master on Nov 23, 2026 (`gates/SUMMARY.txt`).

| # | Gate | Result | Report |
|---|---|---|---|
| 00 | `./setup` readiness (step 1) | All core features ready. "Remotion beats + bookends" blocked: `npm install` not run (network allowed for pip only), and this film uses no Remotion | `00_setup.txt` |
| 00 | `./art smoke` (step 1) | PASS | `00_smoke.txt` |
| — | Whisper pronunciation check, 13 beats | PASS (heard as written; "E2B" and the repo URL respelled for the voice only) | `whisper_check.txt` |
| 01 | Beat-sheet schema | PASS (0 errors) | `01_schema.txt` |
| 02 | Project and approval safety (`build_safety.py`) | PASS | `02_build_safety.txt` |
| 03 | Paperwork / fact-check (`factcheck_check.py`) | PASS (18 rows) | `03_paperwork.txt` |
| 04 | Beat lint | PASS | `04_beat_lint.txt` |
| 05 | Chart shape | PASS (not a finance reel) | `05_gate_shape.txt` |
| 06 | Gate A: static pre-flight, 13 scenes | PASS | `06_gate_A.txt` |
| 07 | Gate W: contrast, margins, text overlap, 13 scenes | PASS | `07_gate_W.txt` |
| 08 | Gate B: strict layout audit, 13 scenes | PASS | `08_gate_B/<scene>.md` |
| 09 | Gate V: frame check on the final master | PASS (26 frames, 0 blockers, 0 majors) | `09_gate_V*.{txt,md,png}` |
| 10 | Gate T: type check (run by `./art final`) | PASS (13 beats) | `10_gate_T_TYPECHECK.md` |
| 11 | Render integrity | PASS (see below) | `11_render_integrity.txt` |
| 12 | Toolkit unit tests | PASS (290 tests) | `12_unit_tests.txt` |
| 13 | Smoke test | PASS | `13_smoke.txt` |

Render integrity confirmed:
- one H.264 3840×2160 24 fps video stream and one AAC audio stream
- duration matches the timeline, and all 4,894 frames decode
- a full error-checked decode is clean
- audio averages −25.9 dB and peaks at −4.2 dB
- the SHA-256 matches the export receipt

**Gate failures during the build, all fixed and re-rendered:**
- Gate A stopped B13: a line positioned from text measurements fell outside the frame in the gate's stub. It now uses fixed coordinates.
- Gate V flagged B03 at its halfway frame: 55% fill against a 55% floor. The cards were made taller.

No gate was skipped or waived.

## GitHub

Posted at `fall-2026/tushar-p/final-project-film/progress-film/` in https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai. The project itself is at https://github.com/tushar-patel28/agent-proving-ground.
