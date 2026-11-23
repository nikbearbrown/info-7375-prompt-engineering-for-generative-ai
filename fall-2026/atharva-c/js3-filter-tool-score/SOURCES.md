# Sources

## Starting point

- **My Job-Search Agent 2** (`../js2-loop-tools-diff/`). Copied into this folder on Nov 23, 2026:
  - `agent/policy.py` (allow-list and write policy) and `agent/loop.py` (bounded collection loop), changed only in the User-Agent string and two comments naming the folder.
  - `agent/skills.py` (skill matcher with the JS2 React/Go fix, `80e4fa1`), unchanged.
  - `budget.json`, unchanged; `.gitignore`, unchanged.
- **New in JS3:** `boards.json` (Greenhouse URLs add `?content=true`; the 404 board is dropped), `agent/postings.py`, `agent/label_sheet.py`, `FILTER.md`.
- The Reallocation Engine and Lectern were **not** used.

## Public endpoints used (read-only GET, no login)

| Board | System | Endpoint |
|---|---|---|
| robinhood | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/robinhood/jobs?content=true` |
| affirm | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/affirm/jobs?content=true` |
| wealthfront | Lever | `https://api.lever.co/v0/postings/wealthfront?mode=json` |

## Toolchain

Python 3 standard library only, as in JS2.

## What Claude Code (Opus 5.5) contributed

| Date / commit | What Claude did | What I did |
|---|---|---|
| Nov 23 (planning) | Explained the assignment; proposed a 3-day plan for the Nov 25 deadline | Chose re-collection and the persona target |
| Nov 23 | Ran the live collection; wrote `agent/postings.py` and `agent/label_sheet.py`; drafted FILTER.md v1.0 from a survey of the data | TODO: review and edit FILTER.md; hand-label all 90 postings |
