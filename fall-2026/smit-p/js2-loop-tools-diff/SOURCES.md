# Sources and contributions

## What this started from

- **Smit's own project, [job-board-aggregator](https://github.com/SmitPatel-31/job-board-aggregator).**
  It already scrapes Greenhouse, Lever, and Ashby. The endpoint shapes used here
  (`boards-api.greenhouse.io/v1/boards/{slug}/jobs`, `api.lever.co/v0/postings/{slug}`) come
  from its `scripts/scraper.py`. None of its code was copied. That project is a bulk
  scraper, and this one is a bounded, policy-guarded loop, so the loop, policy, and checker
  were written new.
- **No JS1 submission was found** in `fall-2026/smit-p/` when this work began (2026-11-08).
  This layer therefore does not build on a JS1 folder. If a JS1 exists elsewhere, Smit should
  say so here.
- Not used: the Reallocation Engine or Lectern code. Lectern's folder listing was viewed only
  to see what the instructor's collector covers.

## Public endpoints (read 2026-11-08)

| ATS | Endpoint | Notes |
|---|---|---|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs` | Returns `{"jobs": [...], "meta": {"total": n}}`; 404 `{"status":404,"error":"Job not found"}` for a bad slug. robots.txt disallows only `/embed/`. |
| Lever | `https://api.lever.co/v0/postings/{slug}?mode=json` | Returns a list; 404 `{"ok":false,"error":"Document not found"}` for a bad slug. robots.txt: `Crawl-delay: 1`. |
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/{slug}` | Returns `{"jobs": [...]}` with an `isListed` flag. Returned 403 to Python's default User-Agent; robots.txt returned "Unauthorized". |

Boards watched: Figma (Greenhouse), Spotify (Lever), Linear (Ashby). The deliberate failure is
the Greenhouse slug `figma-no-such-board-js2`.

## Claude Code's contribution

Smit asked Claude Code, in a single session on 2026-11-08, to do this assignment. Claude Code
(running in a claude.ai cloud session) did the following:

- Drafted GATE.md and the 25 boundary predictions in POLICY.md, and committed each before
  any code.
- Wrote all code in `agent/`, `run_agent.py`, `verify_run.py`, and every test, including
  `tests/mutation_check.py`.
- Ran every live and seeded run in `jobs/runs/` and every command quoted in WRONG_ANSWER.md
  and REVIEW_PACKET.md.
- Found and fixed three issues during the build: seeded runs sharing the live baseline
  (`45480d2`), a count 0 / null contradiction in GATE.md (`1b7f999`), and redirects bypassing
  the allow-list (`1bfbb6d`).
- Drafted SIGNOFF.md, the README, and this file.

**Not done by Claude Code:** the accept/revise/reject decision in REVIEW_PACKET.md, the "How"
line and signature in SIGNOFF.md, confirmation of the two GATE.md Decisions rows, and Smit's
entries in FRICTIONAL.md. Those are Smit's.

No Claude output appears inside the agent. This layer uses no model calls; it is plain
Python.

## Toolchain

Python 3.13.17 standard library only (`urllib`, `json`, `unittest`, `http.server` for one
test). No third-party packages. Linux. Git.
