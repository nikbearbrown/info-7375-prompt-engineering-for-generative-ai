# MCP transcripts

Every file is written by `mcp/server.mjs` itself: one JSON object per line, `{at, dir, raw}`.
- `dir` is `client->server`, `server->client`, or `meta`.
- `raw` is the exact line on the wire.
- Test runs write to a subfolder that the tests delete afterwards, so every file here is from a real
  run.

| File | Client | What happened |
|---|---|---|
| `2026-11-26T003743686Z-69681.jsonl` | **Claude Code 2.1.323** (`claude -p`; config `--mcp-config` with only this server, `--strict-mcp-config`, `--tools ""`, `--allowedTools mcp__js3-filter__score_posting`), 2026-11-26 00:37 UTC (2026-11-25 19:37 ET) | **A real client, partial session.** The client sent a `server/discover` probe (`_meta` protocol 2026-07-28), and the server answered -32601. Then `initialize` with `protocolVersion` 2025-11-25 and capabilities `roots`, `elicitation`; the server answered 2025-06-18 and `tools` only. The client accepted that, sent `notifications/initialized`, then `tools/list`, and received `score_posting`. **No `tools/call`:** the model request failed before the model could use the tool (client result `is_error: true`, `api_error_status: 429`, `usage_limit_reached`, "You've hit your individual spend limit", session `e3ca2d1f-5432-49d2-9a10-4252ccd4bca6`). |
| `2026-11-26T004239686Z-70583.jsonl` | **Claude Desktop**, `clientInfo` `claude-ai` 0.1.0, 2026-11-26 00:42:39 UTC (2026-11-25 19:42 ET) | A real client, handshake only: `initialize` (2025-11-25, server answered 2025-06-18), `notifications/initialized`, `tools/list`. No calls. |
| `2026-11-26T004241768Z-70635.jsonl` | **Claude Desktop**, `clientInfo` `local-agent-mode-js3-filter` 1.0.0, 2026-11-26 00:42:41–00:46:01 UTC (19:42–19:46 ET); three calls made by Aravind in one chat | **A real client, full session.** Handshake as above, then 3 × `notifications/roots/list_changed` (the server ignores them: it never asks for roots), then three `tools/call`: (1) `gh-stripe:8186541` → `isError: false`, decision **keep**; (2) `gh-airbnb:8299386` → **reject**, with `veto.quote` "This position needs to be based in the Beijing, China office 5 days a week. No Visa/Relocation Support.", which is posting text, despite the tool description's "no posting text returned"; (3) `posting_id: "../../README.md"` → `isError: true`, "invalid arguments: expected exactly {\"posting_id\": \"board:id\"} …", so the pattern check refused it before any lookup. |

**Server for the first three files:** `mcp/server.mjs` at commit `461b608d`, SHA-256
`d5fd7291a3a5b7dffed2b416a4ff5f94886618b62dc1e9d4b82ce8ef8ca7fa39`, checked after the Desktop run. The tool
description was fixed afterwards, in a separate commit (see `evaluations/own-server.md`).

**Screenshots** (taken by Aravind in Claude Desktop, 2026-11-25, ET; originally named by macOS "Screenshot 2026-11-25 at …"):
- `screenshots/desktop-call-1.png` (19:45:35): call 1, `gh-stripe:8186541`, full tool output, decision keep.
- `screenshots/desktop-call-2.png` (19:45:48): call 2, `gh-airbnb:8299386`, decision reject, with the veto quote visible.
- `screenshots/desktop-call-3.png` (19:46:47): call 3, `../../README.md`, the tool "Failed" with the "invalid arguments" error.
- They show Claude's answer prose next to the tool output. The prose is not evidence: the transcript is.

**Appended after the commits (2026-11-26, about 02:49–02:50 UTC, when Claude Desktop reconnected).**
The server only appends, and every earlier line is unchanged.
- `…70583.jsonl` gained `{"event":"stdin closed"}` (02:49:32): that client disconnected.
- `…70635.jsonl` gained one more `notifications/roots/list_changed` (02:50:02).
- New file `2026-11-26T025001610Z-77519.jsonl`: a `claude-ai` 0.1.0 handshake and `tools/list` only,
  no calls. It ran the **current** server (description fixed, SHA-256 `326f656b…`, `111cc67b`), not
  the `d5fd7291…` server that the evaluations cover.

**Closed (2026-11-25).** Aravind removed `js3-filter` from the Claude Desktop config and restarted
Desktop.
- The restored config is byte-identical to `claude_desktop_config.backup-2026-11-25.json`, saved
  22:02:21 ET.
- Both remaining servers logged `{"event":"stdin closed"}` at 02:59:32 UTC (21:59:32 ET), in
  `…70635.jsonl` and `…77519.jsonl`. No server process was running afterwards.
- Every line after the last committed timestamp (00:46:01 UTC) came from Desktop reconnecting or
  disconnecting. **None is a tool call**, and no client is configured to start this server any
  more, so no further line can be written.
