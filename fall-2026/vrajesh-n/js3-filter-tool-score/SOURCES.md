# SOURCES.md - JS3: the filter, the tool, and the score

## What I started from
- **Early Bird, my JS2** (commit `3bd808f`, folder `js2-loop-tools-diff/`). JS3 copies from it: the board parsers (`boards.py`), the
  rule (`rule.py`, JS1's R1-R4), the persona loader, the permission policy, budget and loop code (not used by JS3), the 9-board
  config, the 2026-11-01 snapshot, and the fictional persona. It does **not** start from the Reallocation Engine or Lectern.
- **JS1's contract** is where the 3-year threshold and the seniority words came from (REPORT-one-change.md lists the origin of every number).

## Data
- **Snapshot `data/snapshot-2026-11-01/`**: 3,068 postings from 9 public job boards (Ashby: commure; Greenhouse: stripe, figma,
  gleanwork, databricks, doordashusa, twitch, roblox; Lever: palantir), collected in JS2 on 2026-11-01 through each board's public
  JSON endpoint under the JS2 allow-list and budget. **JS3 fetched no new postings.**
- **Persona**: Rohan Desai, fictional. My real resume, contacts and conversation transcripts are not in this folder.
- Posting text belongs to the companies; it is included as the evidence the claims are checked against.

## External software and specifications
- **Model Context Protocol** (JSON-RPC 2.0 over stdio; `initialize`, `tools/list`, `tools/call`): https://modelcontextprotocol.io. My
  server was written from that message shape, not from an SDK.
- **`mcp-server-fetch` 2026.11.18** (PyPI; source https://github.com/modelcontextprotocol/servers, MIT, author Anthropic, PBC):
  evaluated, not used by the agent. Installed in a throwaway virtual environment outside this folder.
- **Claude Code 2.1.332** and model **`claude-sonnet-5-5`**: the client in the real MCP transcript and the model in the one-change
  experiment (40 calls, 2026-11-25).
- **Python 3.13.3**, standard library only for everything in this folder.

## What Claude (Claude Code, `claude-sonnet-5-5`) contributed
Claude wrote the code and drafted the prose; Vrajesh made the decisions and labelled the sample items. By part:

| Part | Claude | Vrajesh |
|---|---|---|
| `FILTER.md` v1 | formatted it and drafted the one-line reasons from his answers (his to rewrite) | decided the role list, excluded ML roles, kept AI engineer, chose the abstention conditions, named the three wrong filters, chose the fetch server |
| `rule.py`, `claims.py`, `mcp_server.py`, all scripts and tests | wrote all of it, tests before code | read the red/green outputs; chose the changes (R4/R5/R1 widening, shipped-only `stack_fit`, option lists count, variant B as default) |
| Reject audit, claim-check, one-change sheets | built the blind sheets, seeds and keys; computed the numbers | labelled every item; his labels were committed before each key was opened, and the sheets hid the filter's verdicts |
| MCP server evaluations | installed and read the fetch server, ran the experiments, wrote the evidence | **trust decisions: to be written in his words** |
| `REPORT-one-change.md`, `review/AUDIT.md`, README, this file | drafted | to review and rewrite; his reasons and trust decisions are marked as his to add |
| `FRICTIONAL.md`, the sign-off and the driver's seat table | will list the facts to prompt him | **will be his words** |

## What I accepted, changed or rejected from Claude (details go in FRICTIONAL.md in my own words)
- Claude's first claim labeler wording said "shipped" but the code matched my whole skills list; my labels showed it, and I chose
  the "shipped only" reading.
- Claude's first option-list exclusion was dropped after my own labels (items 22, 23) contradicted it.
- Claude's first "no network" guard patched `connect()` only; evaluating the server found `connect_ex()` got past it.

## Not mine to claim
No part of this agent applies, emails, messages or logs in. Any Claude response quoted in this folder is one I got, with the date.
