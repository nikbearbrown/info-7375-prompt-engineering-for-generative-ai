# SOURCES.md

## What I used

- **The assignment:** INFO 7375 "Job-Search Agent 2 — The Loop, the Tools, and the Diff" (course repo, `assignments/assignment-js2-the-loop-the-tools-and-the-diff.md`).
- **My own JS1 agent:** `../js1-contract-and-watch/`, final commit `72141da`. JS2 starts from an unchanged copy (commit `2c3654d`).
- **Public job boards** (read-only, no login, fetched a handful of times on Oct 31, 2026). The posting text belongs to each company; it's kept here only as raw evidence.
  - Greenhouse Job Board API: `boards-api.greenhouse.io/v1/boards/anthropic/jobs`
  - Ashby Posting API: `api.ashbyhq.com/posting-api/job-board/{notion, perplexity, openai}`
- **For checking which boards respond:** the instructor's Lectern `sources.json` (course repo, `fall-2026/nik-bear-brown/lectern/`). No code was copied from it.
- **The persona:** Priya Nair, a fictional persona from The Reallocation Engine (`search/examples/priya-nair/`).
- **Software:** Python 3.9.10, pytest 8.3.3, Claude Code 2.1.316.

## What I decided

- The three boards and all three kinds of deliberate failure.
- Delegating the rest of the gate to Claude's proposal, then accepting it, then accepting amendments A1 and A2.
- Running the failing test and the full suite myself.
- **Accept** on the reviewed patch, and the case the test still misses.

## What Claude contributed (Claude Code, Opus 5.5, Oct 31, 2026)

- **The gate:** everything in it except the board choices, as a proposal Hemanth accepted. Also amendments A1 and A2, which Claude found while building.
- **The boundary-test predictions:** derived from the accepted gate and committed before the policy code.
- **All code and tests:** `jsagent/`, `tests/`, `scripts/`, `boards*.json`.
- **All runs:** the live run, the seeded runs and the independent check.
- **The review packet:** reproducing the defect, the test written first, and the patch.
- **Drafts:** this file, `README.md`, `REVIEW-PACKET.md`, `BOUNDARY-TESTS.md` and `FRICTIONAL.md`.
