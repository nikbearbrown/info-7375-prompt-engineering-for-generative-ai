# Agent Proving Ground: Final Project Pitch Film

**Name:** Tushar Patel
**Course:** INFO7375 Prompt Engineering, Final Project pitch film
**Working title:** Agent Proving Ground
**Target role:** Early-career Software Engineer, AI agent infrastructure / platform
**Runtime:** 3:14 (194.542 s, 3840×2160, 24 fps)

## What the film is

A 13-beat pitch for a project that does not exist yet. Agent Proving Ground will run an AI coding agent on small tasks inside an isolated Kubernetes sandbox, record every step it takes, and check whether it actually did the task. Every sentence about Agent Proving Ground’s features is in future tense, or sits inside a sentence framed with ‘will’ or ‘you’ll’ (B04, B08). The only things described as existing are this plan and my public OmniSQL-Postgres project (B10, B11). B08’s opening line describes the plan’s first step, not something that has run.

- **Mock-ups are labelled.** B00, B02, B05 and B08 show "Constructed — not built yet." in the top rail for the whole mock-up. Their contents illustrate the plan; they are not output from running code (see SOURCES.md, "Illustrative content").
- **No Claude responses are shown**, and there is no product, brand or channel styling.

## Folder contents

| File | Purpose |
|---|---|
| `agent-proving-ground.mp4` | The rendered film (4K master from `./art final`) |
| `PROJECT-BRIEF.md` | The project brief: the seven questions, plus what exists today and what will exist |
| `BEAT-PLAN.md` | My human-readable beat plan (narration and visual per beat), which beat_sheet.json was built from |
| `beat_sheet.json` | Narration, visual plan, measured durations and sentence start times (the source of truth for the build) |
| `scenes.py` | Manim scenes, one class per beat (B00–B12) |
| `sentence_audio.py` | Voices each beat one sentence at a time with Kokoro `am_onyx` and a 0.35 s pause between sentences; voices "AWS" as "A-W-S" so Kokoro doesn't read it as one word |
| `BUILD-PROMPT.md` | The prompts and commands that built it, in order |
| `SOURCES.md` | Tools and licences, what I made, what Claude contributed, illustrative content, alternatives looked at |
| `FRICTIONAL.md` | My dated log of what broke, what I decided, and why |
| `FACTCHECK.md`, `SHOTLIST.md`, `PROMPTS.md` | Claims and their status, the shot work order, and the (empty) open-slot list. The toolkit refuses to render without them |
| `gates/` | Quality-gate reports (see below) |

## How to rebuild

1. Clone the toolkit and set it up:

   ```bash
   git clone https://github.com/nikbearbrown/brutalist.art
   cd brutalist.art
   ./setup --install
   ```

   `./setup --install` installs the Python dependencies, downloads the Kokoro model files (`kokoro-v1.0.onnx`, `voices-v1.0.bin`) and checks every dependency. This build used Manim 0.18.1, kokoro-onnx 0.6.1 and ffmpeg 9.0.1. The scenes use no LaTeX. Everything runs locally and free, with no API keys.

2. Copy this folder into the toolkit at `youtube/brutalist/agent-proving-ground/`. `sentence_audio.py` finds the toolkit from its own location, so the path matters.

3. Generate narration first, because the measured audio is the clock for every scene:

   ```bash
   python3 youtube/brutalist/agent-proving-ground/sentence_audio.py
   ```

   Use this, **not** the toolkit's usual `runtime/scripts/generate_audio_kokoro.py`. That script voices each beat in one pass, so it would drop the sentence pauses and the sentence start times that `scenes.py` uses for cue timing.

4. Render. `./art run` needs the full path; the bare slug `agent-proving-ground` fails, because the script resolves it from the current folder.

   ```bash
   ./art run youtube/brutalist/agent-proving-ground      # review cut, beside the reel
   ./art final youtube/brutalist/agent-proving-ground    # 4K master -> renders/agent-proving-ground.mp4
   ```

   Without `--out` or `$ART_OUT`, the master is written to the toolkit's `renders/` folder.

The submitted master's SHA-256 is `3c0c67e121088abc2c24b4b9e36be515088e34e6ee4cce59ab9170cc290e2bf0`.

## Quality gates

Every gate in the toolkit was run against this reel and its final master, in order. Reports are in `gates/`; the run-by-run log is `gates/SUMMARY.txt`.

| # | Gate | Result | Report |
|---|---|---|---|
| 1 | Beat-sheet schema | PASS (0 errors) | `01_schema.txt` |
| 2 | Project and approval safety (`build_safety.py`) | PASS | `02_build_safety.txt` |
| 3 | Paperwork (FACTCHECK, SHOTLIST, PROMPTS) | PASS | `03_paperwork.txt` |
| 4 | Beat lint | PASS | `04_beat_lint.txt` |
| 5 | Chart shape | PASS | `05_gate_shape.txt` |
| 6 | Gate A: static pre-flight, 13 scenes | PASS (one non-blocking warning on B05) | `06_gate_A.txt` |
| 7 | Gate W: contrast, margins, text overlap, 13 scenes | PASS (no warnings) | `07_gate_W.txt` |
| 8 | Gate B: strict layout audit, 13 scenes | PASS (0 findings) | `08_gate_B/<scene>.md` |
| 9 | Gate V: frame check on the final master | PASS (26 frames, 0 blockers, 0 majors) | `09_gate_V.txt`, `09_gate_V_REPORT.md`, `09_gate_V_contact_sheet.png` |
| 10 | Render integrity (manual; see note) | PASS | `10_render_integrity.txt` |
| 11 | Toolkit unit tests | PASS (122 tests). An earlier run failed because `matplotlib` was missing | `11_unit_tests.txt`, `11_unit_tests_run1.txt` |
| 12 | Smoke test | **FAIL**: toolkit issue, not this film | `12_smoke.txt`, `12_smoke_scratch.txt` |

- **Gate 6 warning:** the B05 warning comes from the gate's simulated Manim, which doesn't place the step chips and so sees an arrow outside the frame. Gate B, which checks the real layout, reports it clean.
- **Gate 10:** the toolkit has no gate called "render integrity", so this check was done manually (`10_render_integrity.txt`). It confirms:
  - one H.264 3840×2160 24 fps video stream and one AAC audio stream
  - the duration matches the timeline and 4,669 frames decode
  - a full error-checked decode is clean
  - the audio averages −25.9 dB and peaks at −4.5 dB
  - the SHA-256 matches the export receipt, and all 26 input files are unchanged since export
- **Gate 12:** the toolkit's own smoke-test sample (`examples/_smoke`) has the slug `"_smoke"`, which the toolkit's safety check rejects because a slug must start with a letter or digit. The smoke script hardcodes that sample's path, so it couldn't be run against a corrected copy without editing the toolkit. I did not edit the toolkit (`12_smoke_scratch.txt`).

## GitHub

Posted at `fall-2026/tushar-p/final-project-film/` in https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.
**Progress film (through M5, Nov 23, 2026):** [`progress-film/`](progress-film/README.md). It is a separate film; this pitch stays as graded.
