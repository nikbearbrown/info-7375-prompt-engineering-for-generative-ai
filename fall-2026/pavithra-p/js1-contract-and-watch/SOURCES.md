# SOURCES: Job-Search Agent 1

## What I used

| Source | Used for | Terms |
|---|---|---|
| The JS1 assignment and course Chapters 1–3 (`assignments/assignment-js1-the-contract-and-the-watch.md`) | the task, the contract format, the sign-off | course material |
| [Greenhouse Job Board API](https://developers.greenhouse.io/job-board.html), public GET endpoint `boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true` | Pinterest (watched); Figma and Twilio (experiment 1 snapshots); Affirm, Airbnb, Brex, Databricks, Figma, Reddit and Stripe (experiment 2 snapshots) | public, no login; read only, one request per run |
| [The Reallocation Engine](https://github.com/nikbearbrown/the-reallocation-engine) `search/examples/aarav-patel/`, commit `d08afdd` | the fictional persona, renamed Rohan Mehta (only the name, email, LinkedIn and GitHub changed) | course repository |
| Python 3.13.1 standard library | all code and tests | PSF licence |
| Claude Code 2.1.294 (`claude -p`, model `claude-sonnet-5-5`) | the Claude judge in the agent, sampling, the prompt experiment, the file surface | my NEU Claude Code access |
| claude.ai (Opus 5.5, high) | the chat surface, one posting, 2026-10-31 | my account |

## What I made

- The contract draft (`586c296`) and the decision to keep `CONTRACT.md` to the six sections.
- The 20 hand labels and my labelling rule (`7327ccd`), before any Claude answer.
- The choices: Pinterest as the board, non-senior roles for the 20 postings, the persona's name, the one prompt change ("drop the years check").
- Run 1 and run 2 of the watch, in my own terminal; the claude.ai chat for the action surfaces.
- The label audit run, and the four postings I checked by hand.
- The 20 labels of experiment 2 (`experiment-2/my-labels.txt`).
- The sampling conclusion, the sign-off's checks and signature, and the reflections in `FRICTIONAL.md`.

## What Claude (Claude Code, Opus 5.5) contributed

- Sharpened my contract draft (exact rule words, the "CA" location trap, the refuses list) and later cut it back to six sections when I asked.
- Wrote all the code in `agent/` and all 46 tests in `tests/`, including the label audit command (`python3 -m agent audit`).
- For experiment 2: froze the 20 postings, listed each posting's years lines and résumé skills by text search for my labelling, chose the one prompt change when I asked it to, and ran its 40 calls.
- Counted relevant jobs per board, which led to the switch from GitLab to Pinterest.
- Ran the snapshots, the freeze, the sampling (20 calls), the prompt experiment (40 calls) and the file surface, and saved every reply.
- Checked some of Claude's quotes against the saved postings.
- Drafted `SAMPLING-REPORT.md`, `PROMPT-EXPERIMENT.md`, `ACTION-SURFACES.md`, `experiment/README.md`, this file, the README and the factual entries in `FRICTIONAL.md`. The conclusion, the checks in the sign-off and the reflections are mine.

## Other AI

- ChatGPT was used as a cross-check at each step.

## Constructed or real

- Real: every raw response in `evidence/raw/`, every run report, every Claude reply in `evidence/claude/` and `action-surfaces/`, with its date.
- Constructed, and labelled CONSTRUCTED: every test fixture in `tests/`. No seeded run was needed.
