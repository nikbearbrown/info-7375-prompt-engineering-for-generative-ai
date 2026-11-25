# SOURCES — Job-Search Agent 3

## What I built on
- **My Job-Search Agent 2 code,** `../js2-loop-tools-diff/` at commit `41ae85c` (submitted 2026-11-10). JS3 kept its collector, permission policy, tools, adapters, and loop. It extended the adapters to keep full posting text, and the loop to save raw responses gzip-compressed.
- **My Job-Search Agent 1 persona,** `../js1-contract-and-watch/persona/resume.json`: Riley Navarro, who is fictional. Every label, verdict, and claim is about Riley. No real résumé is used.
- **The instructor's Lectern collector:** only its idea of a filter as a versioned document, with every rule added, cut, or rejected recorded. No Lectern code or board list is used.
- **Course materials:**
  - the Job-Search Agent 3 brief
  - the course AI policy: [AI Policy for Professor Bear's Courses | Using AI Responsibly in Class](https://youtu.be/8Ut0Cdl6vMw?si=9w3aEpt1ZyAR4Kiz)
- **JS1 grading feedback:** "real relevant cases" and a two-valued rule. That's why the boards were chosen by a probe, and why a second probe was run (v1.1) when the first corpus held no posting Riley would apply to.

## Public endpoints
Public, with no login. Everything said about how they behave comes from responses saved in `runs/*/raw/` and the probe summaries in `probe/`.

| System | Endpoint | Used for |
|---|---|---|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true` | Job list with full descriptions |
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{token}` | The board's own name (identity check) |
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/{token}` | Job list with `descriptionPlain` |
| Lever | `https://api.lever.co/v0/postings/{token}?mode=json` | Job list with `descriptionPlain`, `lists`, and `additionalPlain` |

**The probes:**
- **2026-11-18:** 116 boards, titles only.
- **2026-11-25:** 196 boards, full text.
- Both made one GET per board, and they saved counts and matched titles only.

## The Model Context Protocol
- **My server (`mcp_server.py`)** is written from scratch on the standard library: JSON-RPC 2.0 over stdio, with the methods `initialize`, `notifications/initialized`, `ping`, `tools/list`, and `tools/call`. No MCP SDK is used.
- **What the protocol looks like in practice** comes from the two real transcripts in `state/mcp/`, especially Claude Code's own messages: its `server/discover` probe and the `2025-11-25` handshake.
- **The client:** Claude Code 2.1.331, connected through `.mcp.json`.
- **The other server:** `mcp-server-fetch` 2026.11.18, from PyPI.
  - **Source:** `github.com/modelcontextprotocol/servers`, `src/fetch`. Author "Anthropic, PBC.", MIT license.
  - **Install:** installed on 2026-11-25 with my OK, into a throwaway environment outside this folder.
  - **Evidence:** its declared behavior is taken from its own `initialize` and `tools/list` replies. Its actual behavior comes from the recorded calls and from reading its installed source (`server.py`, `readability_js.py`, `allowlist.py`, and `pinning.py`).

**Python standard library modules used:** `urllib.request`, `urllib.parse`, `urllib.error`, `http.server`, `socket`, `subprocess`, `concurrent.futures`, `threading`, `json`, `csv`, `gzip`, `html.parser`, `os`, `re`, `sys`, `io`, `math`, `random`, `argparse`, `datetime`, `time`, `tempfile`, `functools`, `importlib`, `unittest`, and `unittest.mock`.

## What Claude Code contributed
- **When:** I used Claude Code (desktop app, Claude Opus 5.5) in sessions on 2026-11-17, 11-18, 11-20, 11-24, and 11-25.
- **Where Claude is called:** in two places only.
  - `claims.py` calls `claude -p`. The recorded model is `claude-opus-5-5`, and each prompt and raw result is saved in `state/claims/`.
  - Claude Code was the MCP client for one recorded session.
- **The filter itself never calls a model.**

| Part | Claude Code | Me |
|---|---|---|
| `FILTER.md` | Interviewed me with all the questions in one list, with options and a recommendation for each. Flagged that its own abstention recommendation would abstain on almost everything, and narrowed it. Wrote v1.0 and v1.1 from my answers. | Chose every answer. Approved v1.0 before any code existed, and chose to add boards (v1.1) rather than drop Riley's sponsorship need. |
| Board choice | Proposed fixing the selection rule before the probe ran. Wrote and ran both probes. Found and fixed the Israel "IL" false match. Tightened the v1.1 title rule before the probe read any new board. | Accepted the 12 boards and the 2 supplement boards the rules picked |
| Code | Wrote every Python file: `adapters.py`, `text.py`, `loop.py`, `corpus.py`, `labels.py`, `filter.py`, `measure.py`, `measure_changes.py`, `audit.py`, `claims.py`, `mcp_server.py`, `mcp_client.py`, `mcp_eval_fetch.py`, and the probes. Ran the collection and every script. | — |
| Tests | Wrote all 98 tests, including the two wrong versions, run as checks the real filter must fail | — |
| Labels | Drafted all 114 labels against Riley's profile | Reviewed every one, and kept every draft |
| Reject audit | Drew the seeded sample, wrote the sheet with no verdict drafted, copied my verdicts in unchanged, and ran the report | Judged all 50 rows, with a reason for each |
| Claims | Wrote them (through `claude -p`), with the checker that labels them | **Pending:** confirm every claim label in the base sheet |
| Measurements | Ran every change, caught its own checker bug and its own R2 misreading, ran the base prompt twice to measure noise, and recommended what to adopt | **Pending:** decide which changes to adopt |
| MCP | Wrote the server, the client, and the Fetch evaluation script. Ran Claude Code as the client and installed and ran Fetch. Read Fetch's source and found its `npm install` behavior before running it. | Approved installing Fetch. **Pending:** review `MCP_EVAL.md` |
| Documents | Drafted `README.md`, `SCORE.md`, `SHORTLIST.md`, `MCP_EVAL.md`, `AUDIT.md`, this file, `SIGNOFF.md`, and the `FRICTIONAL.md` entries from my sessions and this folder's files | **Pending:** review them. The signature in `SIGNOFF.md` is mine. |

I am responsible for everything submitted here and can explain any part of it.
