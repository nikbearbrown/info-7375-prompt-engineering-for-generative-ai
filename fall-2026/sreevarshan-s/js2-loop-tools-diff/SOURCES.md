# Sources — Sreevarshan Sathiyamurthy, 2026-11-06

## What I wrote
- GATE.md: all eight decisions, in my own words, before any code (commit 733869b)
- BOUNDARY_TESTS.md: the 12 predictions (commit c7fe0a5) and the results (commit 59142a6)
- The review-packet failing test, before the patch (commit 8624b8f). Claude Code fixed three errors in it so that it would run (see FRICTIONAL.md)
- REVIEW_PACKET.md
- SIGN_OFF.md content
- FRICTIONAL.md content

## What Claude Code wrote
- js2/policy.py, js2/fetch.py, js2/loop.py, js2/__main__.py, js2/wrong_answer_demo.py, js2/independent_check.py
- All test files except the review-packet test: tests/helpers.py, tests/test_policy.py, tests/test_fetch.py, tests/test_loop.py (all but the review-packet test), tests/test_independent_check.py, tests/test_cli.py
- The repeat-rule patch (commit 31149a6), shown to me as a diff and applied only after I approved it
- README.md
- SOURCES.md structure
- The persona copies in persona/, with the `_js2_source` field added

## What the chat assistant (claude.ai session) did
- Critiqued the GATE.md decisions
- Chose the review-packet defect (Claude Code had noted that failures are not cached, while answering my cache-key question)
- Wrote the paste prompts
- Reviewed the diff before it was applied

## Outside sources
- Greenhouse public job board API: boards-api.greenhouse.io (`/v1/boards/<token>/jobs`)
- Lever public postings API: api.lever.co (`/v0/postings/<token>?mode=json`)
- Priya Nair persona from JS1 (fall-2026/sreevarshan-s/js1-contract-and-watch/), copied from my local JS1 project (Downloads/Eng_job/persona/)
