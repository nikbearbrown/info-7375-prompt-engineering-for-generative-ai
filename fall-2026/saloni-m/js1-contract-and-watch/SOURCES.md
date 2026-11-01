# SOURCES

## What I used

| Source | Used for |
|---|---|
| Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` (public, unauthenticated) | the one board; one GET on 2026-11-01 18:58 UTC |
| The Reallocation Engine, `search/examples/priya-nair/resume.example.json` and `profile.yml` | the fictional persona; the `search` block was added from `profile.yml`'s `target_role` |
| Course assignment text, `assignments/assignment-js1-the-contract-and-the-watch.md` | requirements |
| Python 3.13.5 standard library | all code |
| Claude Code CLI 2.0.20, `claude -p --model claude-sonnet-5-5` | the Claude judge, sampling, prompt experiment, action surfaces (83 recorded calls: 20 sampling, 40 experiment, 20 seeded run 2, 3 action surfaces; plus 1 unrecorded smoke test) |
| Claude Code desktop app (Claude Opus 5.5), one session on 2026-11-01 | building this folder (see below) |

No other students' folders were read or used. Two incidental exposures, disclosed:
- `git pull` / `git log` in the course repo printed another student's recent JS1 commit
  subjects (for example "prompt v2 (one change: judge the role, not the keyword match)").
- A search for a missing labels file turned up a classmate's `hand_labels.csv` path. It was not
  opened.

## What I did

- Chose the persona (Priya Nair), the rule shape ("title + level"), the board (Greenhouse
  `anthropic`) and the folder name, from options Claude offered.
- Labelled all 20 experiment postings by hand with `scripts/label.py`. Claude did not see or
  suggest any label before they were saved (`labels/hand_labels.csv`).
- Logged the Claude CLI in so the judgment steps could run.
- Rejected Claude's second batch of contract questions (keywords, wrong versions, failure
  sentence, labeling-rule style). Claude then wrote those as flagged defaults; see the CONTRACT.md
  header.
- Review and the sign-off: see the README sign-off line.

## What Claude (Opus 5.5, Claude Code desktop) contributed

- **CONTRACT.md text**, built from my three choices: the keyword and exclusion lists, the two
  wrong versions, the failure sentence, and the 2026-11-01 amendment.
- **`labels/LABELING-RULE.md`** text.
- **All code and tests**: `agent/`, `tests/`, `scripts/`, `prompts/v1_baseline.md` and the one
  change in `prompts/v2_years_soft.md`. Claude chose that change after reading the dev results.
- **Running everything**: the tests, the live fetch, the seeded runs, the 83 Claude CLI calls.
- **First drafts of every report**: README, SAMPLING-REPORT, PROMPT-EXPERIMENT, ACTION-SURFACES,
  this file and FRICTIONAL. Every number in them is recomputable from the saved files by
  `scripts/score.py` or the commands in the README.
- **Finding its own mistakes during the build**: the run-2 citation gap, the 4,000-character cap
  that would have cut off requirements sections, a "13 of 15" count in a draft that it re-checked
  and corrected to 14, and a "15/20" that it corrected to 14/20.

## What the Claude judge (Sonnet 5.5, via CLI) contributed

Only the judgments in `results/**/calls.jsonl`, `results/seeded-run2.txt` and
`results/action-surfaces/`. They are labelled as judgments everywhere and were validated, not
trusted.
