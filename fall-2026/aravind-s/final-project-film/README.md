# Final Project Pitch Film: Klaxon

- **Student:** Aravind Sundaravadivelu (`aravind-s`)
- **Course:** INFO 7375 Prompt Engineering for Generative AI, Fall 2026
- **Project working title:** Klaxon, an AI on-call engineer for a payments system
- **Target role:** new-grad software engineer, backend or infrastructure
- **Film:** `klaxon-pitch.mp4`, runtime 3:48, 1920x1080, synthetic narration (Kokoro `am_onyx`, disclosed in the first beat)
- **Built with:** the Brutalist toolkit (`nikbearbrown/brutalist.art`, commit `22264a3`, show-tell format), Manim, Remotion and local Kokoro narration. Claude Code did most of the build at my request; SOURCES.md says who did what.

## The pitch in one line

Klaxon will save a payments on-call engineer from approving a fix that looks green while the money is still wrong.

## What is real and what is a plan

- **Real, and shown as real:** the first piece. A synthetic, seeded demo of the money check, with 91 passing tests, ran on 2026-10-09. The naive webhook handler kept the dashboard green (7 requests, 0 errors) and the ledger balanced, while the money check found one payment posted twice and the books off by +$69.68. The idempotent handler passed. Those numbers appear on screen under a "real run, Oct 9, 2026" tag and on the real-run card.
- **A plan, labelled "constructed" on screen:** everything Klaxon itself will do. The narration uses "will" for all of it.
- No Claude response is shown in the film.

## Contents

| File | What it is |
|---|---|
| `klaxon-pitch.mp4` | The film |
| `PROJECT-BRIEF.md` | One page answering the seven questions, ending with "exists today" and "will exist" |
| `beat_sheet.json` | The narration and visual plan (22 beats, measured audio durations) |
| `make_sheet.py`, `scene_body.py`, `build_scenes.py`, `finish_audio.py`, `make_shotlist.py` | The sources that rebuild the film |
| `BUILD-PROMPT.md` | The commands and a paste-ready prompt that rebuild it |
| `FACTCHECK.md` | Every claim in the film, its verdict and its source |
| `SHOTLIST.md`, `PROMPTS.md` | The toolkit's work order and prompts file (no generation prompts) |
| `SOURCES.md` | What I used, what was made, who did what, licences |
| `FRICTIONAL.md` | The dated log |
| `evidence/` | The two raw outputs of the first piece's runs on 2026-10-09 (naive and idempotent handler; synthetic data), copied from the Klaxon repo |
| `qc/` | The toolkit's gate reports (see below) |

## Gate reports (`qc/`)

| Gate | Result |
|---|---|
| F paperwork + `factcheck_check.py` | clean (25 claims, all resolved) |
| L beat lint | clean |
| A static pre-flight, W contrast and margins, B layout (strict) | clean on all 19 drawn scenes |
| V frame check on the compiled cut | 0 blockers, 0 majors (44 frames) |
| T type check | pass |
| Loudness | pass (-24.2 LUFS integrated, -2.9 dBTP true peak) |
| Final render receipt | `final-receipt.json`, SHA-256 of the mp4 |
| `bookend_check.py` | fails on the outro only, on purpose: the toolkit's outro card hard-codes the instructor's handle, which this assignment forbids, so the film ends on its own drawn title. See FRICTIONAL.md |

## Check the numbers yourself

`evidence/` holds the two JSON files the first piece wrote on 2026-10-09. Each one has the deliveries, the dashboard numbers, the full money-check report, the ledger, the printed output and a SHA-256 of the code that produced it. Every number in the film appears in them: 7 requests, 0 errors, `money_off_cents: 6968` for the naive handler, and a passing check for the idempotent one.

The Klaxon code itself is private for now (local commit `801a0bf`); it will be public when the repository is. With it, the runs repeat exactly:

```bash
python3.12 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m klaxon.demo duplicate-webhook --handler naive
.venv/bin/python -m klaxon.demo duplicate-webhook --handler idempotent
```

## Rebuild the film

BUILD-PROMPT.md has the full recipe, including the order of the audio steps and one rule learned the hard way: never regenerate the beat sheet while a render is running.
