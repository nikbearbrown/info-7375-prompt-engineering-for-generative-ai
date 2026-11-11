# SOURCES

## Executive summary

This page lists what this submission uses, what I decided, and what Claude contributed. No real résumé, contact or private transcript is included. The persona is invented, and every posting is a public posting from one of three allow-listed hosts.

## What I used

| Item | Use | Terms |
|---|---|---|
| Greenhouse Job Board API, `boards-api.greenhouse.io` | Pinterest, Databricks (and the deliberate `no-such-board-js2`) | public, unauthenticated, read-only |
| Ashby Posting API, `api.ashbyhq.com` | Ramp | public, unauthenticated, read-only |
| Lever Postings API, `api.lever.co` | Palantir | public, unauthenticated, read-only |
| My Job-Search Agent 1 code | the starting point (`317d931`): rule R1–R9, persona check, JS1 tests | mine |
| Lectern (`fall-2026/nik-bear-brown/lectern`, read 2026-11-09) | read, not copied. One idea taken: refuse HTTP redirects (GATE revision). Its `ATS.md` note on HubSpot's empty `hubspot` board is cited in `FINISHED-WRONG.md` | course material |
| Python 3.14 standard library | the whole agent and tests | PSF |
| Claude Code CLI 2.1.314 | a separate session wrote the R3 patch and its revision (`review/03-*`, `review/10-*`) | Anthropic terms |
| Course materials | the assignment brief (Chapters 4–6) | course |

## What I wrote or decided

- The GATE choices:
  - the boards (four real ones across three systems, plus one that fails on purpose);
  - the budgets, 6 boards / 12 requests / 120 seconds;
  - one retry, for temporary errors only;
  - my approval needed for both a state reset and replacing evidence;
  - approval of the whole of `GATE.md` on 2026-11-09.
- The redirect revision: I decided to close the gap.
- The expected R3 answers for the review test (which locations count as the US).
- The review decision: revise (Georgia, and the unapproved "Revision" wording), then accept. I made it after reading `git diff` and running the tests and the comparison myself.
- The README sign-off.

## What Claude contributed

Claude Code, model Claude Opus 5.5, in the Claude desktop app, plus one separate `claude -p` session for the review.

- Drafted `GATE.md` from my choices, including the four exits, the repeat rule and the wrong versions W1–W5, which I approved.
- Wrote the tests (before the code), `agent/loop.py`, `tools.py`, `policy.py`, `ats.py`, `cli.py`, and `check/crosscheck.py`.
- Probed the boards and found the Ramp-on-Greenhouse board used in `FINISHED-WRONG.md`.
- Found the R3 defect by running the rule over run 1's real postings, and wrote the reproduce and compare scripts.
- **The R3 patch itself was written by a separate Claude Code session**, given only the prompt in `review/03-prompt-to-claude-code.txt` and then my revision prompt.
- Found the redirect gap while reading Lectern, and the workdir gap while trying the README commands.
- Drafted `README.md`, `POLICY.md`, `REVIEW-PACKET.md`, `FINISHED-WRONG.md`, this file and `FRICTIONAL.md`. I reviewed them.
