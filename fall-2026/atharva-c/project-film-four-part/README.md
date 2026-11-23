# Seeded Faults — Project Film (four-part)

- **Name:** Atharva C
- **Course:** INFO 7375, Fall 2026
- **Working title:** Seeded Faults — data-quality tests, tested
- **Target role:** Data Engineer / BI Engineer
- **Structure:** Executive summary → Introduction (prior work) → Methods → Evaluation
- **Runtime:** 3:57 (237.2 s) — `seeded-faults-project.mp4`, 3840×2160, Brutalist show-tell, free local pipeline
- **Status:** the project is not built. The fault catalogue and pass/fail thresholds are locked in commit `e5aac1c` (2026-11-22), before any test was written.

## Appendix: detail behind each part of the film
The film keeps detail out of the executive summary. The full detail is here:

| Film part | Appendix | What it holds |
|---|---|---|
| 2. Introduction (prior work) | [A1 — `PRIOR-WORK-CHECK.md`](PRIOR-WORK-CHECK.md) | Every tool and paper the film names, what each does, what was confirmed and how, with links |
| 3. Methods | [A2 — `FAULT-CATALOGUE.md`](FAULT-CATALOGUE.md) | The clean-baseline filters (with row counts), all 18 faults and how each is planted, the holdout and prompt-sample setup, the Claude Pro / Opus 5.5 / 3-prompt cap |
| 4. Evaluation | [A2 — `FAULT-CATALOGUE.md` §3](FAULT-CATALOGUE.md) | The pass/fail thresholds, locked in commit `e5aac1c` before any test was written |
| Numbers spoken in the film | [A3 — `evidence/`](evidence/) | The scripts and outputs behind every past-tense number (October hand test in `../final-project-film/evidence/`) |
| All claims | [A4 — `film-source/FACTCHECK.md`](film-source/FACTCHECK.md) | Each spoken claim, its verdict and its source |

## What's in this folder
| File | What it is |
|---|---|
| `seeded-faults-project.mp4` | The film |
| `SCRIPT-DRAFT.md` | Locked narration, with a fact-check table |
| `beat_sheet.json` | Narration and visual plan, one idea per beat |
| `FAULT-CATALOGUE.md` | The locked fault list, clean baseline and pass/fail thresholds |
| `PRIOR-WORK-CHECK.md` | What already exists, with sources |
| `FAULT-CATALOGUE-CANDIDATES.md` | Claude's 22 candidate faults, before I chose |
| `evidence/` | Scripts and outputs behind every past-tense number in the film |
| `BUILD-PROMPT.md` | Commands and prompts that rebuild the film |
| `SOURCES.md` | What I used, what I made, what Claude contributed |
| `CLAUDE-LOG.md` | What Claude did, as facts |
| `FRICTIONAL.md` | My dated work log |
| `gate-reports/` | Brutalist quality-gate reports |
| `film-source/` | `scenes.py`, `make_sheet.py`, `write_beat_sheet.py` and the toolkit paperwork |

## How to rebuild the film
See `BUILD-PROMPT.md`. In short: install Brutalist at `b21f625`, run `film-source/write_beat_sheet.py`, copy `film-source/` into a build folder, run `make_sheet.py`, generate Kokoro audio, then `./art run` and `./art final`.
