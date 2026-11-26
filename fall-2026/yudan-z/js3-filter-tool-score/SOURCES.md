# SOURCES

## Data

| What | Where from | When |
|---|---|---|
| `data/postings.jsonl`: 1,595 postings | my JS2 runs 1 and 2, public job-board APIs: Greenhouse (`pinterest`, `databricks`), Ashby (`ramp`), Lever (`palantir`) | fetched 2026-11-09 and 2026-11-10; not re-fetched for JS3 |
| `persona/resume.json` | fictional persona, written for JS1 | 2026-10 |
| `audit/labels-*.csv`: verdicts | **my own hand labels** | 2026-11-25 |

## Code

| What | Origin |
|---|---|
| `agent/rule.py` and the other files in `agent/` other than those below | my JS1/JS2 submission (GitHub commit `47bab91`) |
| `agent/filter.py`, `agent/run_filter.py`, `agent/shortlist.py`, `audit/measure.py` | new for JS3, written by Claude in this session |
| `mcp/server.py` | new for JS3, written from scratch by Claude in this session. No MCP SDK was used. The message shapes follow the MCP specification (modelcontextprotocol.io, protocol version 2025-06-18) |
| `tests/test_filter.py` | written from FILTER.md **before** `agent/filter.py` existed (commit `daf96ca`) |
| `tests/test_filter_v2.py`, `tests/test_mcp_server.py` | new for JS3, written by Claude |

## The other tool server I evaluated

The `@modelcontextprotocol/server-filesystem` package, v2.4.0:
- source at github.com/modelcontextprotocol/servers, `src/filesystem/`, commit `a13c39e647d8c553501ffe4d3f5d9db9dcc534f7` (2026-11-18);
- files read: `server.ts`, `lib.ts`, `index.ts`, `path-validation.ts` and `README.md`, on 2026-11-25;
- not installed and not run.

## What Claude contributed

The course allows Claude, and asks that its contribution be named. I used Claude Code (model claude-opus-5-5) for the whole assignment, on 2026-11-25.

**Claude did:**
- drafted FILTER.md v1 and the tests;
- wrote all new code;
- drew the sample and built the blind label sheet;
- proposed and measured each filter step;
- found the "Excel" false friend and the relocation and executive-sponsorship evidence;
- wrote the first drafts of AUDIT, SHORTLIST, SCORE-CHANGES, TOOL-SERVER, README and FRICTIONAL;
- ran the MCP session.

**I did:**
- every hand label and every change to a label;
- my definition of a relevant posting;
- the decisions to adopt v2f and v2g;
- the review of every document before signing.

The Driver's seat table in README.md lists each decision.

**The one Claude response shown as output** is in `mcp/session/`. It is the real response I got on 2026-11-25 at 20:28 EST, unedited except for the removed `system/init` line.
