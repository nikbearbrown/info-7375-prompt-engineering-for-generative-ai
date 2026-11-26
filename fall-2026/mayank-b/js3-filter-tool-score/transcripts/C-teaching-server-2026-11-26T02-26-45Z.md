# Transcript C-teaching-server-2026-11-26T02-26-45Z

Recorded 2026-11-26T02:26:45Z by `scripts/mcp_record.py` (a scripted client, not a model). Raw lines in both
directions: `C-teaching-server-2026-11-26T02-26-45Z.jsonl`. Server stderr: `C-teaching-server-2026-11-26T02-26-45Z.stderr.txt`.

- Server command: `python3 -I other-server/main.py --stdio` (cwd = project root; one fresh process per session)
- Expected column: profile `teaching` (the predictions in `transcripts/EXPECTED-C.md`, written before the first run)
- Corpus run: `2026-11-26T02-20-27Z-content` (950 postings); posting id used: `5183044008` (first posting whose filter verdict is keep)
- SHA-256 of src/jsa3/mcp_server.py at record time: `4143fd10c80d48eddcee102e676c34bb1550ebf0fc9ae8546cfa0c8b91fd64ed` (not the server under test; recorded for completeness)
- Server exit codes: session 1: 0, session 2: 0
- Result: 22 of 22 steps matched the prediction

| # | Session | Step | Sent (raw) | Expected | Observed | |
|---|---|---|---|---|---|---|
| 1 | 1 | tools/list before initialize | `{"jsonrpc":"2.0","id":1,"method":"tools/list"}` | error -32000 | error -32000 | match |
| 2 | 1 | initialize (2025-11-25) | `{"jsonrpc":"2.0","id":2,"method":"initialize","params":{"protocolVersion":"2025-11-25",...` | result protocolVersion 2025-11-25 | result protocolVersion 2025-11-25 | match |
| 3 | 1 | tools/list before notifications/initialized | `{"jsonrpc":"2.0","id":3,"method":"tools/list"}` | error -32000 | error -32000 | match |
| 4 | 1 | notifications/initialized | `{"jsonrpc":"2.0","method":"notifications/initialized"}` | no reply | no reply | match |
| 5 | 1 | tools/list | `{"jsonrpc":"2.0","id":5,"method":"tools/list"}` | result tools lookup | result tools lookup | match |
| 6 | 1 | tools/call score_posting real id 5183044008 | `{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"score_posting","argumen...` | error -32602 | error -32602 | match |
| 7 | 1 | tools/call score_posting unknown id | `{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"score_posting","argumen...` | error -32602 | error -32602 | match |
| 8 | 1 | tools/call bad argument (posting_id: 5) | `{"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"score_posting","argumen...` | error -32602 | error -32602 | match |
| 9 | 1 | tools/call unknown tool apply_to_job | `{"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"apply_to_job","argument...` | error -32602 | error -32602 | match |
| 10 | 1 | unknown method jobs/apply | `{"jsonrpc":"2.0","id":10,"method":"jobs/apply"}` | error -32601 | error -32601 | match |
| 11 | 1 | unparseable line '{' | `{` | error -32700 | error -32700 | match |
| 12 | 1 | ping | `{"jsonrpc":"2.0","id":12,"method":"ping"}` | error -32601 | error -32601 | match |
| 13 | 1 | tools/call lookup office (teaching tool) | `{"jsonrpc":"2.0","id":13,"method":"tools/call","params":{"name":"lookup","arguments":{"...` | result isError false; text '505A Dana Hall' | result isError false; text '505A Dana Hall' | match |
| 14 | 1 | tools/call as a notification (no id) | `{"jsonrpc":"2.0","method":"tools/call","params":{"name":"score_posting","arguments":{"p...` | no reply | no reply | match |
| 15 | 1 | second initialize (asks 2024-11-05) | `{"jsonrpc":"2.0","id":15,"method":"initialize","params":{"protocolVersion":"2024-11-05"...` | result protocolVersion 2025-11-25 | result protocolVersion 2025-11-25 | match |
| 16 | 1 | tools/list after second initialize | `{"jsonrpc":"2.0","id":16,"method":"tools/list"}` | result tools lookup | result tools lookup | match |
| 17 | 2 | initialize with no params | `{"jsonrpc":"2.0","id":17,"method":"initialize"}` | result protocolVersion 2025-11-25 | result protocolVersion 2025-11-25 | match |
| 18 | 2 | initialize asking 2024-11-05 | `{"jsonrpc":"2.0","id":18,"method":"initialize","params":{"protocolVersion":"2024-11-05"...` | result protocolVersion 2025-11-25 | result protocolVersion 2025-11-25 | match |
| 19 | 2 | notifications/initialized | `{"jsonrpc":"2.0","method":"notifications/initialized"}` | no reply | no reply | match |
| 20 | 2 | tools/list | `{"jsonrpc":"2.0","id":20,"method":"tools/list"}` | result tools lookup | result tools lookup | match |
| 21 | 2 | raw '{}' | `{}` | error -32600 | error -32600 | match |
| 22 | 2 | raw '[]' (batch) | `[]` | error -32600 | error -32600 | match |

## Server stderr (verbatim)

Session 1:

```text
(empty)
```

Session 2:

```text
(empty)
```

