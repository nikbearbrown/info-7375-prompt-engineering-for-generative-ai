# Sources

## Starting point
- **My Job-Search Agent 2 (`../js2-loop-tools-diff/`).** Copied into this folder on Nov 23, 2026:
  - `agent/policy.py` (allow-list and write policy) and `agent/loop.py` (bounded collection loop), changed only in the `User-Agent` string and two comments naming the folder.
  - `agent/skills.py` (skill matcher with the JS2 React/Go fix, `80e4fa1`), unchanged.
  - `budget.json`, unchanged; `.gitignore`, unchanged.
- **New in JS3:** `boards.json` (Greenhouse URLs add `?content=true`; the 404 board is dropped), `agent/postings.py`, `agent/label_sheet.py`, `agent/filter.py`, `agent/audit_sheet.py`, `agent/evaluate.py`, `agent/shortlist.py`, `agent/mcp_server.py`, `score/recount.py`, all tests, `FILTER.md`, and the other write-ups.
- **Not used:** The Reallocation Engine and Lectern were not used.

## Other references
- **Official MCP Filesystem server**, `modelcontextprotocol/servers` `src/filesystem` (package `2.4.0`), README and source read on Nov 24, 2026 for the second server evaluation. Not installed or run.

## Public endpoints used (read-only GET, no login)

| Board | System | Endpoint |
| :--- | :--- | :--- |
| `robinhood` | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/robinhood/jobs?content=true` |
| `affirm` | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/affirm/jobs?content=true` |
| `wealthfront` | Lever | `https://api.lever.co/v0/postings/wealthfront?mode=json` |

## Toolchain
Python `3.12.7`, standard library only, as in JS2. Claude Code `2.1.283` was the MCP client for the real transcript.

## What Claude Code (Opus 5.5) contributed

| Date / commit | What Claude did | What I did |
| :--- | :--- | :--- |
| **Nov 23 (planning)** | Explained the assignment; proposed a 3-day plan for the Nov 25 deadline | Chose re-collection and the persona target |
| **Nov 23** | Ran the live collection; wrote `agent/postings.py` and `agent/label_sheet.py`; drafted `FILTER.md` v1.0 from a survey of the data | Reviewed `FILTER.md` and committed it as is (`0041401`); hand-labeled all 90 postings (`215f29a`) |
| **Nov 24 (`3beb6f0`)** | Wrote `tests/test_filter.py` (26 tests) before any filter code | Approved tests-first; reviewed the 26 test cases covering decimal years (`1.5+`), the 60-char window, gates, `W1`–`W5`, the threshold, and the `"I cannot tell"` cases |
| **Nov 24** | Wrote `agent/filter.py` to `FILTER.md` v1.1, `tests/wrong_versions.py` (patches in `W1`–`W5`, checks each makes a test fail), `agent/audit_sheet.py`; ran `v1.0` rules on all 400 | Hand-judged all 53 audit postings (`30` rejects, `22` kept, and the extra close call; `c87c9b6`, `cd6bfe8`) |
| **Nov 24** | Wrote my audit judgments into the CSVs; checked cited years against the text; computed Wilson intervals; proposed the `N ≥ 3` change, wrote its tests and code, measured it on `dev` | Judged all 53 audit postings; approved running `v1.2` on `dev` (`6dc9c6a`) and the single `heldout` run (`bdf8998`) |
| **Nov 24 (`f89aef7`)** | Wrote shortlist tests, then `agent/shortlist.py`; drafted `shortlist/CASES.md` | Checked the claim rules and verbatim quotes, and rewrote `shortlist/CASES.md` (`17f1a98`) |
| **Nov 24 (`8458710`)** | Wrote MCP server tests, then `agent/mcp_server.py` and `tests/mcp_scripted_client.py`; recorded the scripted transcript | Reviewed the 4 read-only tools, stdio transport, and `out/` log-path confinement |
| **Nov 24** | Registered the server in Claude Code (local scope) with my approval; ran one `claude -p` session against it and saved the trimmed transcript | Approved registering; reviewed the transcript, including the substring-match problem and the 22-vs-23 miscount that Claude's recount found |
| **Nov 24** | Probed my server; had a web-fetch subagent read the Filesystem server's README and source (`github.com/modelcontextprotocol/servers`, `src/filesystem`, `v2.4.0`); drafted `mcp/EVALUATIONS.md` | Reviewed and rewrote `mcp/EVALUATIONS.md`, and approved the schema-validation and unknown-board fix (`e273c8e`) |
| **Nov 24 (Day 3)** | Wrote `score/origins.md`, `score/report.md`, `score/recount.py`, `PERSISTENCE.md`, and drafts of `SIGNOFF.md` and `README.md`; found the second false survey fact (`91` vs `173`) and wrote `FILTER.md` v1.3 | Rewrote `FRICTIONAL.md`, `score/report.md`, `PERSISTENCE.md`, `README.md` (`4d0c744`), and `SOURCES.md`; picked the false friend; rewrote and signed `SIGNOFF.md` (`ad0a87e`) |
| **Nov 24–25 (final checks)** | Checked the repo against the assignment and my past TA reviews; added the Wilson interval to `score/recount.py`, the rejected-rules row to `FILTER.md`, and replaced local paths in `evidence/mcp/client-config.json` (`0fcd674`); fact-checked my rewrites; re-ran every README command from a fresh clone at `9a30e25` | Wrote the `FRICTIONAL.md` reflection (`4387c98`), `mcp/EVALUATIONS.md` section 4 with my trust decisions (`51b9e41`), and the `SIGNOFF.md` "How each item was checked" section, and re-signed it (`9a30e25`) |
