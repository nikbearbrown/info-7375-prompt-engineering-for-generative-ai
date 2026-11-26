# Expected results, transcript C (the course's Chapter 8 teaching server): the prediction

Written by Claude Code (a subagent working for Mayank) at 2026-11-25T20:30Z, **before** `other-server/main.py`
had been run. The basis is source inspection only: `other-server/main.py` (the course file
`lessons/08-mcp-from-scratch/code/main.py` at commit a8629ce1c437abee3a2c4f025bd8be3183b0f0af, run with
`--stdio`) and the lifecycle table in `chapters/08-mcp-from-scratch.md`. The message sequence is the same as
transcript A, byte for byte except the posting id. The recorder copies this expected column into each
`C-teaching-server-<UTC>.md` next to what was observed.

## Session 1

| # | Client sends | Expected reply (from reading the source) | Why (branch) |
|---|---|---|---|
| 1 | `tools/list` before initialize | error `-32000` | `not self.ready` |
| 2 | `initialize`, protocolVersion `2025-11-25` | result, protocolVersion `2025-11-25` | constant reply |
| 3 | `tools/list` before the notification | error `-32000` | `ready` still false |
| 4 | `notifications/initialized` | no line | sets `ready` |
| 5 | `tools/list` | result: one tool, `lookup` | |
| 6 | `tools/call` `score_posting` (real id) | error `-32602` (Unknown tool) | name != `lookup` |
| 7 | `tools/call` `score_posting` unknown id | error `-32602` | name != `lookup` |
| 8 | `tools/call` `score_posting` `{"posting_id": 5}` | error `-32602` | name != `lookup` |
| 9 | `tools/call` `apply_to_job` | error `-32602` | name != `lookup` |
| 10 | method `jobs/apply` | error `-32601` | final `else` |
| 11 | raw `{` | error `-32700`, id null | main loop `ValueError` |
| 12 | `ping` | error `-32601` (**ping is not implemented**) | final `else` |
| 13 | `tools/call` `lookup` `{"key": "office"}` | result, `isError` false, text `505A Dana Hall` | fixture mapping |
| 14 | `tools/call` with no id | no line (dropped; nothing on stderr) | `"id" not in message` -> `return None` |
| 15 | second `initialize`, protocolVersion `2024-11-05` | result, protocolVersion `2025-11-25` (accepted again) | `initialize` branch has no guard |
| 16 | `tools/list` | result (`ready` was **kept** through the re-initialize) | `ready` is never reset |

## Session 2 (fresh process)

| # | Client sends | Expected reply | Why |
|---|---|---|---|
| 17 | `initialize` with **no params** | result, protocolVersion `2025-11-25` (params never read) | |
| 18 | `initialize`, protocolVersion `2024-11-05` | result, protocolVersion `2025-11-25` (re-initialize accepted) | |
| 19 | `notifications/initialized` | no line | |
| 20 | `tools/list` | result: `lookup` | |
| 21 | raw `{}` | error `-32600`, id null | `jsonrpc` missing |
| 22 | raw `[]` | error `-32600`, id null | not a dict |
