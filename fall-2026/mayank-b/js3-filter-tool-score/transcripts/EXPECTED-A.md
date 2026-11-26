# Expected results, transcript A (own server): the prediction

Written by Claude Code (a subagent working for Mayank) at 2026-11-25T20:30Z, **before** `src/jsa3/mcp_server.py`
or `scripts/mcp_record.py` had been run even once. Nothing below was observed; it is what the server's
documented choices (the docstring of `src/jsa3/mcp_server.py`) say should happen. The recorder copies this
same expected column (from its `STEPS` table) into each `A-scripted-<UTC>.md` next to what was observed.

`ID` = the real posting id the recorder picks from the corpus: the first posting whose filter verdict is
`keep`, else the first posting. State is written (initialized, ready).

## Session 1 (one server process)

| # | Before | Client sends | Expected reply | After |
|---|---|---|---|---|
| 1 | F, F | `tools/list`, id 1 (before initialize) | error `-32000`, id 1 | F, F |
| 2 | F, F | `initialize`, id 2, protocolVersion `2025-11-25` | result, protocolVersion `2025-11-25`, capabilities.tools | T, F |
| 3 | T, F | `tools/list`, id 3 (no notification yet) | error `-32000`, id 3 (WF6 would answer a result here) | T, F |
| 4 | T, F | `notifications/initialized` (no id) | **no line** within the wait | T, T |
| 5 | T, T | `tools/list`, id 5 | result: exactly one tool, `score_posting` | T, T |
| 6 | T, T | `tools/call` `score_posting` `{"posting_id": ID}`, id 6 | result, `isError` false, record.id == ID | T, T |
| 7 | T, T | `tools/call` `score_posting` `{"posting_id": "no-such-posting-0000"}`, id 7 | result, `isError` **true** (task error, not protocol error) | T, T |
| 8 | T, T | `tools/call` `score_posting` `{"posting_id": 5}`, id 8 | error `-32602` | T, T |
| 9 | T, T | `tools/call` name `apply_to_job`, id 9 | error `-32602` (unknown tool) | T, T |
| 10 | T, T | method `jobs/apply`, id 10 | error `-32601` | T, T |
| 11 | T, T | the raw text `{` | error `-32700`, id **null** | T, T |
| 12 | T, T | `ping`, id 12 | result `{}` | T, T |
| 13 | T, T | `tools/call` name `lookup` `{"key": "office"}`, id 13 (the teaching server's tool) | error `-32602` (unknown tool) | T, T |
| 14 | T, T | `tools/call` `score_posting` `{"posting_id": ID}` with **no id** (a notification) | **no line** within the wait; stderr notes it was not executed | T, T |
| 15 | T, T | `initialize` again, id 15, protocolVersion `2024-11-05` | error `-32600` (already initialized), state unchanged | T, T |
| 16 | T, T | `tools/list`, id 16 | result: one tool, `score_posting` (still ready) | T, T |

## Session 2 (a fresh server process)

| # | Before | Client sends | Expected reply | After |
|---|---|---|---|---|
| 17 | F, F | `initialize`, id 17, **no params** | error `-32602`, state unchanged | F, F |
| 18 | F, F | `initialize`, id 18, protocolVersion `2024-11-05` | result, protocolVersion `2025-11-25` (the version this server supports) | T, F |
| 19 | T, F | `notifications/initialized` | no line | T, T |
| 20 | T, T | `tools/list`, id 20 | result: one tool, `score_posting` | T, T |
| 21 | T, T | the raw text `{}` | error `-32600`, id null | T, T |
| 22 | T, T | the raw text `[]` (a batch) | error `-32600`, id null | T, T |
