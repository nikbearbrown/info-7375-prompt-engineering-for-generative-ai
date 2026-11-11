# SOURCES

## Started from

- **My JS1 work** (`../js1-contract-and-watch/`): the idea of an allow-listed GET that refuses redirects, raw responses saved byte for byte, and "new since last run" by id. JS2's code is new; nothing is imported from JS1.
- **The instructor's Lectern collector** (`fall-2026/nik-bear-brown/lectern/`): **only** the field names for Ashby (`jobs[].id/title/location`) and SmartRecruiters (`content[].id/name/location.fullLocation`, `totalFound`). As Siddi specified in GATE.md, none of its implementation was copied and none of its behaviour was assumed correct. Its `ATS.md` also documents that a wrong board name can come back empty rather than as an error.
- **Public APIs:** `boards-api.greenhouse.io`, `api.ashbyhq.com`, `api.smartrecruiters.com`. All were probed on 2026-11-10 with curl to choose the boards (see the `check/verified_boards.json` note).
- **Python 3.13 standard library.**

## What Siddi wrote or decided

- **`GATE.md`:** the boards, exits, budgets, repeat rule, error policy, permission policy and wrong versions. Typed in chat, saved verbatim (`1793a11`).
- **Building on JS1:** the decision, and the instruction to take only field names from Lectern.
- **Still to come:** the boundary predictions, the review decision and the commands in REVIEW-PACKET §5, FRICTIONAL.md, and the sign-off.

## What Claude contributed

- **The agent:** `agent2/` (policy, providers, http, loop, CLI).
- **Checking tools:** `check/independent_check.py` and its roster (probed by Claude with curl).
- **Tests:** all of `tests/`, including the review-packet test and the patch `ef6456a`.
- **The boundary case list** (Siddi writes the predictions).
- **Documents:** the README, this file and REVIEW-PACKET.md.
- **Claude's own mistakes, found and fixed:**
  - The first real run's trace logged a false `board_done failed` line for every successful board (a `finally` block ran before success was recorded). The run was kept as evidence and fixed before the next run.
  - The first test harness reused one run id, so a second run hit the policy's overwrite refusal.
