# SOURCES — Job-Search Agent 2

Drafted by Claude Code from the committed records and my instructions;
reviewed by Swathi.

## What I used

- **Greenhouse public Job Board API**, boards `databricks` and `stripe`, plus
  the deliberately nonexistent board `js2-nonexistent-board-swathi`:
  `https://boards-api.greenhouse.io/v1/boards/<board>/jobs`. Public GET, no
  login. Response shape and the bad board's 404 checked with one read-only
  request each on 2026-11-04 (15:12 ET), before any code.
- **Ashby public Job Board API**, board `plaid`:
  `https://api.ashbyhq.com/posting-api/job-board/plaid`. Public GET, no login.
  Checked on 2026-11-04 (15:12 ET); the shape of `secondaryLocations` and
  `address` was checked with one more read-only request on 2026-11-04 before
  the parser was written.
- Saved responses from my live runs: `runs/2026-11-04T22-44-47-181789-0500/`
  and `runs/2026-11-05T23-11-48-228373-0500/`.
- **Priya Nair, a fictional persona**, via my JS1 agent: `persona/` was copied
  unchanged from JS1 commit `ebcd515` (JS2 commit `5a8f4cf`). JS1's
  `SOURCES.md` records where those files come from (the Reallocation Engine's
  `search/examples/priya-nair/`). No real résumé is used anywhere.
- **Claude Code** (desktop app), model `claude-opus-5-5`.
- **Claude chat** (claude.ai), in a separate session.

## What I wrote myself

- `GATE.md`: my decisions (`510a59a`) and both revisions (`96dde19`, `d131b5f`).
- My 15 boundary predictions in `BOUNDARY-CASES.md` (`85dbd4c`), including
  changing case 13.
- Approving every test file before its code was written.
- My reproduction and test runs, in my own Terminal: `review-packet/` files
  01–04.
- My review decision in `review-packet/REVIEW-PACKET.md`.
- `FRICTIONAL.md`.
- The "why" sentences in the driver's seat table in `SIGNOFF.md`, and my
  sign-off.

## What Claude Code wrote

- All code: `policy.py`, `loop.py`, `parsers.py` (and the Plaid fix,
  `4a3db26`), `independent_check.py`, `demo_finished_wrong_answer.py`. The
  JS1 files (`watch.py`, `rule.py`, `persona.py`) were written by Claude Code
  for JS1 and copied unchanged.
- All tests: `tests/test_policy.py` (from my 15 predictions),
  `tests/test_loop.py`, `tests/test_independent_check.py`,
  `tests/test_ashby_address.py`.
- The SIMULATED demo folder, `runs/simulated-2026-11-05-finished-wrong-answer/`.
- The text of `review-packet/REVIEW-PACKET.md` except my Decision section, and
  the headers of review-packet files 01–04 (the terminal output in them is
  mine, pasted and saved verbatim, with my username and home path redacted).
- This `SOURCES.md` and `README.md` (drafts).
- It also checked my `FRICTIONAL.md` and `SIGNOFF.md` against the records and
  pointed out mistakes, which I then corrected myself.

## What Claude chat helped with

- Phrasing my GATE.md decisions.
- Proposing the 15 boundary cases for me to confirm.
- Giving me fact lists and fill-in prompts for `FRICTIONAL.md` and my review
  decision. Some wording it suggested was wrong, and I corrected it.
- Compiling the tables in `SIGNOFF.md`, which I checked row by row.
