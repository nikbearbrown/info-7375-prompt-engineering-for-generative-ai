# FRICTIONAL — Job-Search Agent 2

## Entry 1 — November 9, 2026: Starting point
Started from my own JS1 (../js1-contract-and-watch, submitted at 9b381ec), copied unchanged into this folder so JS2 runs on its own from a fresh clone and JS1 stays untouched. The first copy failed 1 test because I forgot JS1's prompts/ folder; after copying it, 9/9 passed. Committed as 9b66b8d. Added .DS_Store to .gitignore (JS1 grader feedback).
Python is now 3.14.3 (Homebrew, venv created with conda deactivated) instead of JS1's 3.14.6 from Anaconda.
An earlier read-only Claude Code session pointed out that JS1's `_usable_id` accepts only integer ids, so Lever/Ashby postings (string ids) would be dropped. Candidate defect for the review packet.

## Entry 2 — November 9, 2026: Choosing and checking the boards
On Nov 8, I ran curl (commands suggested by Claude Code) and saved OpenAI (Ashby, 816 postings) and Palantir (Lever, 305). Today, I captured all four boards myself:
- Glean, Greenhouse: 200, 123 postings
- Palantir, Lever: 200, 304 postings (a plain JSON list, no "jobs" key)
- OpenAI, Ashby: 200, 825 postings
- pavan-js2-no-such-board, Greenhouse: 404, {"status", "error"}: the deliberate failure
Chose these 3 real boards on 3 systems plus 1 deliberate bad name. The counts changed between Nov 8 and Nov 9, so the boards do change from day to day.