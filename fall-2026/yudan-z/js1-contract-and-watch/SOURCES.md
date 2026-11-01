# SOURCES

## Executive summary

This page lists what this submission uses, what I wrote, and what Claude contributed. No real résumé, contact or private transcript is included. The persona is invented, and every posting is a public posting fetched from one allow-listed host.

## What I used

| Item | Use | Terms |
|---|---|---|
| Greenhouse Job Board API, `boards-api.greenhouse.io` | public job listings (Pinterest board for the agent; 9 other companies' boards for the 20 experiment postings) | public, unauthenticated endpoints; read-only; no login, no applying |
| Python 3.14 standard library | the whole agent and tests | PSF |
| Claude Code CLI 2.1.314 (`claude -p`) | the Claude judge, sampling, prompt experiment, action surfaces; logged in with my own account | Anthropic terms |
| Course materials | assignment brief (Chapters 1–3) | course |

## What I wrote / decided

- The relevance rule and its refinements (CONTRACT §4), the failure conditions (§6), and both dated revisions (R3 Canada, R9 graduation).
- The labeling rule (`experiment/LABELING-RULE.md`) and **all 20 hand labels with my reasons** (`experiment/labels.json`).
- The single prompt change for v2, and the choice of the least-autonomy surface.
- The decision to keep label #3 against Claude's suggestion.

## What Claude contributed

Claude Code, model Claude Opus 5.5, in the Claude desktop app.

- Integrated my rule into the English `CONTRACT.md` and proposed refinements (listed in FRICTIONAL #2–#4).
- Wrote the tests (from the contract, before the code), the implementation in `agent/`, the experiment scripts, and the fictional persona.
- Diagnosed the bugs in FRICTIONAL #5, #7, #9 and #14.
- Chose which 20 postings went on the labeling sheet. It did not label them.
- Drafted `README.md`, the three reports, this file and `FRICTIONAL.md`. I reviewed them.
- **The Claude verdicts inside the results files are Claude's judgments**, produced 2026-10-30 through `claude -p`. They are labeled `model-judgment` everywhere and are never presented as facts.
