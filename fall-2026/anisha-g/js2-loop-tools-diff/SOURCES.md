# Sources — Job-Search Agent 2
Anisha Gaikar · 2026-11-09 to 2026-11-10

## What I used
- **Assignment:** INFO7375 "Job-Search Agent 2 — The Loop, the Tools, and the Diff".
- **My JS1 agent** (`../js1-contract-and-watch/`): the starting point.
- **Public job-board APIs, read-only GET:**
  - Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs` (boards: klaviyo, datadog);
  - Lever Postings API, `https://api.lever.co/v0/postings/{slug}?mode=json` (board: palantir).
- **Tools:** Python 3 standard library, `unittest`, `curl` (the independent check only), `git`, `shasum`.

## What I did
- Made the gate decisions: exits, budgets 5/15/60, the repeat rule, the error policy, the allowed hosts, the report folder and the never-list. I committed GATE.md **alone, first** (`cdc62ba`), before any code.
- Gave my 17 boundary predictions before any test existed, and chose the boards.
- Made later decisions:
  - keep 15 requests as a safety cap;
  - keep the apply-URL test;
  - keep seen ids after an empty list;
  - correct the authorship lines (choice A);
  - **accept** the review-packet patch, after seeing the test fail before and pass after.
- Ran every test, every live run, the demos and the checks on my Mac, and committed each stage.
- Wrote the sign-off "Not checked" choices, the driver's-seat reasons and my FRICTIONAL lines.

## What Claude (this chat, claude.ai) contributed
- Wrote all the code (`watcher/`, `watch.py`, `wrong_versions/`, `tools/`) and all the tests (`tests/`), from my GATE.md and my predictions. The tests were committed before the code.
- Wrote the review-packet test (`tests/test_review_packet.py`) from my rule, before the patch.
- Copied my gate answers and predictions into GATE.md and PREDICTIONS.md unchanged. Drafted README.md, TRACE.md, PERMISSIONS.md, REVIEW-PACKET.md, this file and the factual entries of FRICTIONAL.md, which I reviewed.

## What Claude Code (on my Mac) contributed
- **Reviewed stage B** (2026-11-09 ~3:30 pm) and found 7 problems. Problem 1, the empty list wiping seen ids, became my review packet.
- **Made the review-packet change**, the one line in `watch.py`, on 2026-11-10 ~9:35 pm. It didn't edit tests or commit.
- **Also started a second, parallel build in my folder** on 2026-11-09, which I removed (`3ac13df`).

## What ChatGPT (OpenAI) contributed
- **Drafted the wording of my answers** to the gate questions and the boundary predictions (2026-11-09). I read them, changed some, and chose what to keep.
- **Reviewed stage B** and found: redirects bypass the request cap, the report-folder-symlink escape, the timeout floor, and a broken config crashing the run.

## Not included
No real résumé, credentials or caches (`.gitignore`). JS2 doesn't use a persona or a relevance rule.
