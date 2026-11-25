# Agent Proving Ground — progress film (through M5)

**Name:** Tushar Patel
**Course:** INFO 7375 Prompt Engineering, Final Project Film (progress version)
**Working title:** Agent Proving Ground — progress film (through M5)
**Target role:** Software engineer, agent infrastructure
**Runtime:** 3:55 (235.250 s, 3840×2160, 24 fps, H.264 + AAC, 19.7 MB)
**Film:** `agent-proving-ground-progress.mp4`, SHA-256 `fe084d7258d59dd8325b7e99db123d898cbe0863e08f86dfe09d916846bee146`

This film **supersedes nothing**. The October pitch in `../` (`agent-proving-ground.mp4` and its files) stays exactly as graded. This folder is new.

## What the film is

A 13-beat progress film (v2). It explains the project first, keeps "built so far" short, and ends on what's left:
- **Executive summary (B01–B04):** who I am, the problem ("done" is a claim, not a result), what Agent Proving Ground is, and who opens it in their first minute.
- **Introduction (B05–B06):** what already exists (E2B, Langfuse) and why mine joins the pieces.
- **Methods (B07–B09):** one run, step by step; the tasks and the frozen split; then what is built and tested through M5, shown with real output.
- **Evaluation (B10–B11):** how it's judged, and the first results with real output.
- **Close (B12–B13):** the three things left, the biggest risk, and the repo.

Details:
- **Narration:** my v2 BEAT-PLAN.md (Nov 23), word for word, including two later changes:
  - B10's last sentence: "…and I wrote my predictions down before the held-out runs" (it said "before every run", which the captures don't show).
  - B12's third item: "Third, I'll harden the check, so it confirms every test actually ran" (it was the write-up and submission). Card 3 now reads "Harden the check", and a footer under the three cards reads "All by Dec 18". It is voiced with the same local Kokoro voice as the October pitch (`am_onyx`), one sentence at a time, with 0.25 s between sentences.
- **REAL beats (B09, B11)** show text captured from my repo on Nov 23, read-only, in terminal-style frames. Each frame's title bar shows the source path and the source's own date, and the top rail says "Real output". The commands and full output are in `evidence/`.
- **CONSTRUCTED beats (all the others)** are drawn diagrams, labelled "Constructed" in the top rail for the whole beat. B04's terminal is a mock-up, and its title bar says so.
- **Tense:** past tense for what ran (M0–M5); "will" for what's left.
- No costs, Claude responses, logos, people, mascots or channel styling are on screen.

### v1 was superseded

v1 of this film (also Nov 23) led with implementation and ended without explaining what's left, so I rewrote the narration. v1's beat plan is kept at the bottom of BEAT-PLAN.md. Its clips, audio and export are kept, not deleted, in the toolkit reel's `_superseded/v1/` (outside this folder).

## Folder contents

| File | Purpose |
|---|---|
| `agent-proving-ground-progress.mp4` | The film (4K master from `./art final`) |
| `BEAT-PLAN.md` | My v2 beat plan, verbatim, with the superseded v1 at the bottom |
| `NUMBER-CHECK.md` | Every number in the v2 narration checked against the captures before rendering (all 26 match), plus three wording points with their sources |
| `PROJECT-BRIEF.md` | The seven questions, plus "Exists today (through M5)" and "Will exist". Drafted by Claude Code for my review |
| `beat_sheet.json` | Narration, visual plan, measured durations and sentence times (the build's source of truth) |
| `BUILD-PROMPT.md` | The exact commands that rebuild the film, and the prompt that produced it |
| `SOURCES.md` | Tools and licences, the source of every REAL beat, what I made and what Claude contributed |
| `FRICTIONAL.md` | My log (header only; the entries are mine to write) |
| `evidence/` | `B6.txt` … `B13.txt`: each capture's command, date and output (named for v1 beats; SOURCES.md maps them to v2); `capture.sh` reruns them |
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
| — | Whisper pronunciation check, 13 beats | PASS (heard as written; "E2B", "INFO 7375" and the repo URL respelled for the voice only) | `whisper_check.txt` |
| 01 | Beat-sheet schema | PASS (0 errors) | `01_schema.txt` |
| 02 | Project and approval safety (`build_safety.py`) | PASS | `02_build_safety.txt` |
| 03 | Paperwork / fact-check (`factcheck_check.py`) | PASS (23 claims) | `03_paperwork.txt` |
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
- duration matches the timeline, and all 5,646 frames decode
- a full error-checked decode is clean
- audio averages −25.6 dB and peaks at −3.9 dB
- the SHA-256 matches the export receipt

**Gate failures during the v2 build, all fixed and re-rendered:**
- Gate A stopped B10 and B12: its stub doesn't measure text, so scenes that only fade text into fixed cards look as if no shape ever changes. Both gained drawn marks (ticks, a cross, an underline, open checkboxes).
- B04 crashed while rendering: an empty spacer line in the mock-up. It was removed.
- Gate T blocked the first master in 6 beats:
  - Labels at size 20–24 measured under the 41 px floor. They were raised to size 24–30.
  - Chip outlines were read as text, so text inside them looked like overlapping labels. The outlines are now a lighter grey.
  - All 13 scenes were re-rendered. B09 needed one more size step.
- Render integrity (gate 11) failed once after the B12 change: the master was one frame short. The cause was the toolkit's three-decimal final cut at 235.2083 s. B12 got a 0.04 s silent tail so the timeline is 235.250 s, and it passed.
- Frame review (not a gate) caught two more problems, both fixed before the master:
  - B08's tiles were hidden behind the dev/held-out cards.
  - B01's title finished too late.

BUILD-PROMPT.md has the details. The v1 gate failures are recorded there too.

No gate was skipped or waived.

## GitHub

Posted at `fall-2026/tushar-p/final-project-film/progress-film/` in https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai. The project itself is at https://github.com/tushar-patel28/agent-proving-ground.
