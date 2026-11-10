# Sources — who made what

*Drafted by Claude Code. Reviewed by Atharva C., 2026-10-31: I confirmed the
"What I wrote or decided" and "Who ran what" sections from memory, and
corrected the line about commits.*

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
- **Commits.** I ran the first contract commit myself. For every later
  commit, I approved it and Claude ran the git command. I made the decisions
  behind each one: what went in, and when.
- **Pushing.** I signed in to GitHub as Arc-211 (gh browser login) and
  approved the push and the pull request; Claude ran the commands in my
  terminal.

## Who ran what

- **Tests:** I ran them. Claude also ran them while building.
- **Baseline run** (2026-10-30T063746Z): Claude typed the command into my
  Terminal panel; I watched it.
- **Same-day re-runs** (2026-10-30T070159Z and 2026-10-30T075724Z): I ran
  them.
- **Run 2** (2026-10-31T040628Z, with `--claude`): I ran it.
- **Experiment, sampling, and action-surface calls:** Claude ran them on
  2026-10-30, after I approved each step.

## Timeline note

The contract commit `19bbfae` shows an author date of 2026-10-29 16:54. That
date is from my first attempt, which committed an empty `CONTRACT.md` by
mistake. The real contract text was amended into that commit on 2026-10-30,
before any code was written, which is why the file says 2026-10-30.

## Commit hashes: local repo vs pull request

These documents cite hashes from my local working repo. The same commits were
copied, in order and with their original dates, onto the pull-request branch
(nikbearbrown/info-7375-prompt-engineering-for-generative-ai#31). There they
have new hashes, because they sit on top of the class repo's `main`. Use the
right-hand column to find them on GitHub.

| local | on the PR branch | commit |
|---|---|---|
| `19bbfae` | `cf7041d` | contract written before any code |
| `0b50ec8` | `3f178f5` | watcher, rule judge, and contract tests |
| `0a67bba` | `e9fb7f6` | baseline run (738 postings, 0 new) |
| `e70631f` | `7246932` | labeling rule and blank sheet (before any labels) |
| `e977e6f` | `fcfad78` | Claude judge, validator, study scripts |
| `ff49997` | `9a01944` | hand labels (before any Claude run on them) |
| `1e11045` | `15dec8e` | prompt experiment on dev |
| `f82287b` | `af848ca` | prompt experiment held-out (run once) |
| `13e0832` | `122dd42` | sampling run |
| `6a9b31d` | `73e1e51` | watch --claude uses revision prompt |
| `6ccc9a1` | `e292be8` | run 2 (18 new) and action-surface runs |
| `26d048d` | `681352a` | draft reports |
| `c054115` | `a3f76f1` | FRICTIONAL, sign-off, driver's seat |

For commits after this table was written, see the pull request's commit list.
