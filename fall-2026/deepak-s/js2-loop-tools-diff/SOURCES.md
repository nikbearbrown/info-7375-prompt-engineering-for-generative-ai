# SOURCES.md: endpoints and documentation

Listed 2026-11-10. Claude Code (Claude Opus 5.5) did not fetch or read any page below in this session. Everything this folder says about how an endpoint behaves comes from the responses captured in `evidence/manual-capture/20261110T184001Z/` (table: `evidence/manual-capture/CAPTURE.md`) and from the committed runs under `runs/`, not from these pages.

## Endpoints the agent calls (GET only; GATE.md section 5)

| System | Host | URL pattern (jobwatch/providers/) | Captured in |
|---|---|---|---|
| Greenhouse | boards-api.greenhouse.io | `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs` | CAPTURE.md rows 01, 02 |
| Lever (US) | api.lever.co | `https://api.lever.co/v0/postings/{slug}?mode=json` | CAPTURE.md rows 03, 05 |
| Lever (EU) | api.eu.lever.co | `https://api.eu.lever.co/v0/postings/{slug}?mode=json` | CAPTURE.md row 04 |
| Ashby | api.ashbyhq.com | `https://api.ashbyhq.com/posting-api/job-board/{slug}` | CAPTURE.md rows 06, 07 |

## Documentation

| Source | URL | Used for | Read by Deepak |
|---|---|---|---|
| Greenhouse Job Board API (the URL in JS1's SOURCES.md at b91c877) | https://developers.greenhouse.io/job-board.html | the Greenhouse endpoint | Not read by Deepak |
| Lever postings API | https://github.com/lever/postings-api | the Lever endpoints, US and EU | Not read by Deepak |
| Ashby public job posting API | https://developers.ashbyhq.com/docs/public-job-posting-api | the Ashby endpoint | Not read by Deepak |
| A third-party Lever API guide | https://100hires.com/lever-api.html | the defensive non-JSON row in GATE.md section 4 | no (GATE.md section 4: "not read by me") |

## Code and other material reused

- Deepak's JS1 agent, "The Contract and the Watch", personal repo commit b91c877: the jobwatch/ modules imported in d3ae571 (listed as legacy in GATE.md Amendments A-1), the tests under tests/acceptance, tests/spec and tests/unit, the persona `examples/persona_resume.json`, `schema/`, `labels/`, `prompts/`, and `scripts/presubmit_check.sh` (rewritten for JS2). One JS1 capture, `evidence/manual/stripe_20261030T000804Z.raw`, was imported unchanged (see README.md).
- The JS1 test fakes in `tests/conftest.py`, written with Claude in chat on 2026-10-29 (credited in JS1's SOURCES.md).
- Python standard library (urllib, json, hashlib, os.path); jsonschema 4.26.0; pytest 9.2.0; anthropic 2.3.0, which is installed for the JS1 judge and never called by the JS2 loop.
