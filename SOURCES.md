# SOURCES

## What this builds on
- **My Job-Search Agent 1** (INFO 7375, 2026-10-31). Copied unchanged in commit `09b1056`: `jsagent/` (fetch, rule R1–R5, résumé
  loader, audit, Claude judge, state), its 75 tests, the fictional personas, the prompts and `CONTRACT.md`. The Oct 31 Samsara
  response and state are in `baseline/2026-10-31/` with sha256s.
- I did **not** use the Reallocation Engine or Lectern code.

## Public endpoints called (read-only GET)
| Endpoint | Used by | Documentation |
|---|---|---|
| `https://boards-api.greenhouse.io/v1/boards/{board}/jobs` and `…/jobs/{id}` | the agent | Greenhouse Job Board API, https://developers.greenhouse.io/job-board.html |
| `https://api.lever.co/v0/postings/{company}?mode=json` | the agent | Lever Postings API, https://github.com/lever/postings-api |
| `https://api.ashbyhq.com/posting-api/job-board/kraken.com` | **only** my cross-check script, outside the agent | Ashby public job posting API, https://developers.ashbyhq.com/docs/public-job-posting-api |

All three documentation links returned HTTP 200 on 2026-11-10. These docs describe the APIs as public endpoints meant for showing job
listings. I did not read each site's full terms of use (see SIGNOFF.md, Not checked). The agent sent 27 network requests in total
(10 in run A, 9 in B, 8 in D), paced 1 s apart per host. Run C used no network. The cross-check sent 1.

## Python standard library
- `urllib.request`: `HTTPRedirectHandler.redirect_request` is overridden to check and count every hop. TLS is verified by the default
  context.
- `pathlib.Path.resolve` and `Path.is_relative_to` (3.9+): containment is compared on real paths, by components.
- `urllib.parse.urlsplit`: `.hostname`, `.port` (raises `ValueError` for a bad port) and `.netloc`, used for the review-packet fix.
- `os.replace`: atomic replacement of the state file.

## AI assistance
- **Claude Code** (Anthropic, model Opus 5.5), 2026-11-10. It drafted GATE.md, wrote the JS2 code and tests, made the review-packet
  patch, ran the commands and drafted these documents. Who did what is in SIGNOFF.md (the driver's seat) and in the commit messages
  (`Co-Authored-By`). My own edit to the gate is `a67bdbf`.
- The in-agent Claude judge (JS1's `claude -p` path) was **not** used in JS2's graded runs.

## Course
- INFO 7375 Job-Search Agent 2 brief, Chapters 4–6, and the course AI policy.
- My JS1 grade feedback (2026-11-10): keep the evidence for every run I cite, get a real second-day run, and write the driver's seat
  in my own voice.
