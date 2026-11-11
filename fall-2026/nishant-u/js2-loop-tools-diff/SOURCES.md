# SOURCES — Job-Search Agent 2 (nishant-u)

JS1's own sources list is in `fall-2026/nishant-u/js1-contract-and-watch/SOURCES.md` at `d63ee48`. This
file covers JS2.

## Sources used

- **Greenhouse Job Board API.** Endpoint used, GET only, no login:
  `https://boards-api.greenhouse.io/v1/boards/<board>/jobs?content=true`. Documentation:
  <https://developers.greenhouse.io/job-board.html> (it redirects to
  <https://docs.greenhouse.io/job-board.html>), read 2026-11-10. It says "authentication is not required
  for any GET endpoints". It states no rate limit and links to no API terms page.
- **Ashby public job posting API.** Endpoint used, GET only, no login:
  `https://api.ashbyhq.com/posting-api/job-board/<board>`. Documentation:
  <https://developers.ashbyhq.com/docs/public-job-posting-api>, read 2026-11-10. It shows no
  authentication for this GET and states no rate limit or terms.
- **The boards**, all public: Greenhouse `faire`, `instacart`, `poshmark` and the deliberately wrong
  `no-such-board-js2-test`, and Ashby `poshmark`. Each was chosen from a GET-only probe on 2026-11-10.
  Every response the agent received is saved verbatim under `out/*/runs/*/raw/` with its sha256.
  - Faire's Greenhouse bodies include a contact address Faire itself published in its postings, an
    accommodations contact at `faire.com`. As in JS1, the bodies are kept unedited so their recorded
    sha256 hashes stay valid. No other email address appears in any saved body.
  - I haven't read the companies' own careers-site terms.
- **Lectern**, the instructor's collector, `fall-2026/nik-bear-brown/lectern/` in this repository
  (`collect.py`, `ATS.md`, `sources.json`). Used for the endpoint formats and the lesson that an empty
  200 board can mean a wrong slug (HubSpot in `ATS.md`). No code was copied.
- **The Reallocation Engine** (<https://github.com/nikbearbrown/the-reallocation-engine>, local checkout
  at `95f2545`): `scripts/ats/providers/*.mjs` and `.claude/skills/greenhouse-watch/` for the endpoint
  formats and Ashby's response shape. No code was copied. The fictional persona Priya Nair
  (`data/resume.example.json`) comes from it through JS1.
- **My JS1** (`nishant-u-js1`, `d63ee48`): copied unchanged in `ca43940`. JS2 reuses its rule judge,
  validator, résumé check and optional Claude judge.
- **Course chapters** in this repository: Chapter 4, `chapters/04-the-agent-loop.md` (exits, budgets,
  the finished wrong answer, the separate outcome check); Chapter 5,
  `chapters/05-tools-and-permissions.md` (the permission gate, containment, boundary matrix); and
  Chapter 6, `chapters/06-claude-code-and-diff-review.md` (reproduce first, test first, scope, accept or
  revise or reject).
- **The JS2 brief**, `assignments/assignment-js2-the-loop-the-tools-and-the-diff.md`, and the course AI
  policy, `prerequisites/ai-policy.md`, with the video
  [AI Policy for Professor Bear's Courses | Using AI Responsibly in Class](https://youtu.be/8Ut0Cdl6vMw?si=9w3aEpt1ZyAR4Kiz).

## What I wrote or decided

- **The gate decisions** (`GATE.md`, `58d6431`): the five boards, including the empty Greenhouse
  poshmark board and the deliberate 404; the exits; the budgets (5 boards, 10 requests, 60 seconds); the
  repeat rule; the error policy; the permission policy; the 14 boundary predictions; the five wrong
  versions; and the failure statement.
- **Every amendment:** before code (`c5ee0fe`: the profiles, `read_file`, merge-only `update_state`,
  case 15, wrong version 6); after implementation (`d5640de`: I accepted the 8 decisions Claude Code
  made); and before the patch (`4ba8bd3`: an empty 200 board is `unverified-empty`).
- **The order of work:** gate, then tests, then code, then live runs, then the review packet.
- **The limits on Claude Code:** no push until the end, a separate state per live run, every run
  reported verbatim, and no patch before the regression test failed in my own run.
- **The review:** the scope widened before the patch (`bccbc41`), and the decision to ACCEPT on evidence
  (`REVIEW-PACKET.md`, `cd15d19`).
- **My test runs:** the regression test before the patch (2 failures on `bccbc41`) and after (3 ok), the
  full suite (131 tests, 1 skip), and `git diff --stat`, in my own Git Bash (recorded verbatim in
  `REVIEW-PACKET.md`).
- **The sign-off and driver's seat** in `README.md`: approved and signed by me, 2026-11-10.

## What Claude contributed

### claude.ai (chat), 2026-11-10

- Drafted with me the gate text, the prompts I gave Claude Code, the sign-off and the driver's seat.
- Checked the boundary-case table against GATE.md. I reviewed it.

### Claude Code, 2026-11-10

- **Research:** the summaries of Chapters 4–6; the Lectern and Reallocation Engine endpoint survey; the
  GET-only board probe; reading the API docs.
- **Gate review:** found three gaps before any code. The finished-wrong-answer demo couldn't happen in a
  run that includes the failing board; boundary case 9 didn't fit the operation list; and nothing
  distinguished a merging `update_state` from a replacing one. These became `c5ee0fe`.
- **Tests:** `tests/test_js2_*.py`, `tests/js2_helpers.py` and `tests/js2_mutants.py`, written from my
  gate before the implementation (`e666f6e`), and the regression test `tests/test_js2_review.py`
  (`4ba8bd3`).
- **Code:** `agent2/`, written against the gate (`5e3e3d0`), and the patch (`cd15d19`).
- **Decisions it made while implementing,** listed for me and accepted in `d5640de`.
- **Its own weak first regression test:** the first draft constructed a board the state had never seen,
  so it would have passed without the fix. It caught this before the commit and split the test into
  "seen" and "fresh" cases (`FRICTIONAL.md`).
- **Ran the live runs** (`6399099`, `c050acd`, `c51b1af`, `98ae593`), the outcome checks, the offline
  replay smoke test and the fresh-clone check.
- **Drafted** `FINISHED-WRONG.md`, `REVIEW-PACKET.md`, `POLICY.md`, this file, `FRICTIONAL.md` and
  `README.md`. I edited and approved them.

No Claude judge call (`claude -p`) was made in JS2. Every JS2 run was without `--claude`.
