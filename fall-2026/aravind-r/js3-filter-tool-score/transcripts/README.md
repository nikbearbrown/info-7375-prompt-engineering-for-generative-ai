# MCP transcripts

Every file is written by `mcp/server.mjs` itself: one JSON object per line, `{at, dir, raw}`.
- `dir` is `client->server`, `server->client`, or `meta`.
- `raw` is the exact line on the wire.
- Test runs write to a subfolder that the tests delete afterwards, so every file here is from a real
  run.

| File | Client | What happened |
|---|---|---|
| `2026-11-26T003743686Z-69681.jsonl` | **Claude Code 2.1.323** (`claude -p`; config `--mcp-config` with only this server, `--strict-mcp-config`, `--tools ""`, `--allowedTools mcp__js3-filter__score_posting`), 2026-11-26 00:37 UTC (2026-11-25 19:37 ET) | **A real client, partial session.** The client sent a `server/discover` probe (`_meta` protocol 2026-07-28), and the server answered -32601. Then `initialize` with `protocolVersion` 2025-11-25 and capabilities `roots`, `elicitation`; the server answered 2025-06-18 and `tools` only. The client accepted that, sent `notifications/initialized`, then `tools/list`, and received `score_posting`. **No `tools/call`:** the model request failed before the model could use the tool (client result `is_error: true`, `api_error_status: 429`, `usage_limit_reached`, "You've hit your individual spend limit", session `e3ca2d1f-5432-49d2-9a10-4252ccd4bca6`). |
