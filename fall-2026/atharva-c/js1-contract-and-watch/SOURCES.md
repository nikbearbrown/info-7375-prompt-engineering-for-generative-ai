# Sources — who made what

*Drafted by Claude Code. Check by Atharva C.: PENDING.*

## What I used

- **Stripe's public Greenhouse board:**
  `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`, the
  only fetched host. Raw responses are in `runs/`.
- **Persona résumé:** `examples/rohan-desai.resume.example.json`, copied
  unchanged from The Reallocation Engine's `search/examples/rohan-desai/`. It's
  fictional (`@example.com`, a 555 number). No real résumé was used anywhere.
- **Claude Code** (desktop app session, Opus 5.5) as the coding assistant.
- **The `claude` CLI** (`claude -p`, `claude-sonnet-5-5`, tools off) as the
  agent's Claude judge, signed in with my claude.ai account. No API key is
  stored in this repo.
- **Python 3.12.7**, standard library only.

## What I wrote or decided

- **`CONTRACT.md`:** every decision and most of the wording are mine, given
  as answers in an interview where Claude asked the questions. Some choices
  (title words, location handling, skill matching) I picked from options
  Claude wrote. Claude assembled my answers into the file.
- **`LABELING_RULE.md`:** I chose among options Claude wrote. The
  mixed-location clarification came from my own re-answer during labeling.
- **All 20 hand labels** in `labels/sheet.csv`. Each one is my choice, made
  in a click-through of titles and locations. Claude flagged 5 answers that
  contradicted my own rule or my other answers, and I re-answered them.
- **Choice of board** (Stripe), **choice of persona**, **the one prompt
  change** (list valid field names), **keeping the imbalanced label set**,
  and **switching the agent to the revision prompt**.
- **`FRICTIONAL.md`**, the sign-off's "Not checked" items, and the driver's
  seat table *(to be written by me)*.

## What Claude contributed

- **All code:** `agent/`, `tools/`, `tests/`, and the prompt files in
  `prompts/`.
- **The tests**, written from my contract. Claude also wrote
  `tests/mutants.py`, which showed that one of its own tests was too weak; it
  fixed that test.
- **Bugs Claude caught in its own code before any run:** two-letter state
  codes matched in any case ("Remote **in** Canada" = Indiana).
- **The data checks behind decisions:** comparing 10 Greenhouse boards,
  listing Stripe's real location strings, and checking substring-matching
  risks against Rohan's skills.
- **Drafts** of `README.md`, `SAMPLING_REPORT.md`, `EXPERIMENT.md`,
  `ACTION_SURFACE.md`, and this file, all from committed evidence.
- **Commits.** Claude ran the git commits after I approved each one.

## Who ran what

- **Tests:** I ran them. Claude also ran them while building.
- **Baseline run** (2026-10-30T063746Z): Claude typed the command into my
  Terminal panel; I watched it.
- **Same-day re-run** (2026-10-30T070159Z): I ran it.
- **Experiment, sampling, and action-surface calls:** Claude ran them on
  2026-10-30, after I approved each step.

## Timeline note

The contract commit `19bbfae` shows an author date of 2026-10-29 16:54. That
date is from my first attempt, which committed an empty `CONTRACT.md` by
mistake. The real contract text was amended into that commit on 2026-10-30,
before any code was written, which is why the file says 2026-10-30.
