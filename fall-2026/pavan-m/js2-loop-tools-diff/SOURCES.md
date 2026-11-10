# SOURCES — Job-Search Agent 2

## What I used
- Public job-board APIs: Greenhouse (`boards-api.greenhouse.io`, Glean), Lever (`api.lever.co`, Palantir), Ashby (`api.ashbyhq.com`, OpenAI)
- Python 3.14.3; httpx 0.28.1; pytest 9.2.0 (full list in `requirements.txt`)
- Claude Code (desktop app): wrote the implementation
- Claude (claude.ai chat): guidance and drafting, listed below
- INFO7375 JS2 assignment brief; my JS1 grade feedback (add .DS_Store, run on two real days, show real improvement)
- Starting point: my own JS1 (`../js1-contract-and-watch` at `9b381ec`). I did not use the Reallocation Engine, Lectern, or classmates' work.

## What I wrote or did myself
- The choice of boards, and the manual curl captures on Nov 8 and Nov 9 (Nov 8 commands suggested by Claude Code)
- GATE.md decisions: exits, budgets, retries, permissions, wrong versions (`e9b38ea`)
- Checking and committing the 16 boundary predictions before any test (`9c5efe0`)
- Every assert in `tests/test_policy.py`, `tests/test_loop.py` and `tests/test_string_ids.py`, before the code each one tests
- Every live run, replay, and checker run, and reading their results and exit codes
- The review decision: rejecting patch v1's scope, accepting v2 on evidence
- Removing the two empty state files left by the bug (`a249b3d`)
- The "Not checked" list and the sign-off

## What Claude Code contributed
- In a read-only first session: a plan for JS2 and the discovery that JS1's `_usable_id` accepts only integers
- `agent/policy.py`, `agent/adapters.py`, `agent/loop.py`, `check_run.py`, `config/boards.json` (`7596cdf`), plus 19 choices my spec didn't cover, which I reviewed (FRICTIONAL Entry 6)
- The string-id patch: v1 in watch.py (revised at my request), then v2 in adapters.py (accepted, `e7ae2b0`), with an honest list of callers and side effects

## What Claude (chat) contributed (claude.ai, Nov 9–10, 2026)
- A step-by-step plan for the assignment and a breakdown of each requirement
- Review of my GATE.md draft (3 gaps found and fixed) and a full revised version I adopted
- The draft of the 16 boundary predictions, and test skeletons with TODOs (I wrote the asserts); caught a test that could fail for the wrong reason
- The idea of saving the string-id defect for the review packet, and of a replay mode for before/after evidence on identical input
- The Claude Code prompts I used
- Drafts of REVIEW_PACKET.md, DEMO_FINISHED_WRONG.md, the README, and wording for several FRICTIONAL entries, all from my results; I checked them against the evidence files and commits