# Tool server — my MCP server and one I did not build

## My server: `priya-filter` (`mcp/server.py`)
stdio, newline-delimited JSON-RPC 2.0, standard library only. One tool, `score_posting(board, id)`, runs filter v1.1 on the frozen corpus. The config path is fixed at startup; no client input can choose a file. It writes only its own transcript (`transcripts/server-*.jsonl`).

### Evidence (all actually run, 2026-11-25)
| Test | Result | Evidence |
|---|---|---|
| Scripted client, 8 steps (`python3 -m mcp.client`) | 8/8 OK | `transcripts/client-20261126T021226Z.jsonl`, `server-20261126T021226Z.jsonl` |
| Valid call `databricks/8656900002` | kept, score 5, R1+R2 | same |
| Unknown id | `isError: true`, "no posting … in the frozen corpus" | same |
| Extra argument `"path": "../../etc/passwd"` | JSON-RPC −32602, "unexpected arguments" | same |
| Undeclared tool `delete_posting` | −32602 "unknown tool" | same |
| Unknown method | −32601 | same |
| **Claude Code as client** (attempt 1) | Server not connected (relative path in registration). Claude made **no** tool calls and refused to fall back to other tools. | `transcripts/claude-code-client-attempt1-not-connected.txt` |
| **Claude Code as client** (attempt 2) | Correct result reported field by field (`openai/0ca02747…`: kept, score 6, R1+R2). It tried `../../etc/passwd` as the `id` (the only string field); the server returned "no posting with id '../../etc/passwd'" and read no file. | `transcripts/claude-code-client-attempt2.txt`, `transcripts/server-20261126T031249Z.jsonl` |
| What Claude *said* vs what it *sent* | The server log shows exactly 2 `tools/call` requests with the arguments Claude reported. **Match.** | `server-20261126T031249Z.jsonl` |

### What I found
- The schema did the defending: `additionalProperties: false` and a board enum leave no path field to abuse. The path-as-id attempt reached the server only as a lookup key.
- Claude Code sent a method I never defined (`server/discover`); my server answered −32601. Clients send things you do not plan for, so the server logs every message.
- Claude Code also used **ToolSearch** (to load my tool's definition) despite my "use ONLY the priya-filter tool" instruction. It disclosed this itself. A tool-only instruction is not a hard boundary; the server's own limits are.
- Deviation from the MCP spec: my server refuses `ping` before `initialize`; the spec allows ping at any time.

### Not checked
Concurrent clients, very large or non-ASCII ids, remote (HTTP) transport, any client other than my scripted one and Claude Code. Whether a client could send `tools/call` after `initialize` but before `notifications/initialized` (my server does not gate on that notice).

### My trust decision
*[Your words: would you let Claude Code use this server unattended for Priya's search, and under what limits?]*

## Server I did not build: the course's Week 8 teaching server
`lessons/08-mcp-from-scratch/code/main.py` (instructor material, run read-only, unmodified). One tool, `lookup(key)`, over a hard-coded dict. Probed with `mcp/probe_other.py`: 11 lines sent (10 requests + 1 malformed). Transcript: `transcripts/teaching-server-probe-20261126T031810Z.jsonl`.

| Probe | Reply |
|---|---|
| `tools/list` before `initialize` | −32000 "Initialize and notify before using tools" |
| `initialize` (I asked for 2025-06-18) | result, protocolVersion **2025-11-25**, serverInfo `info7375-readonly` |
| `tools/list` after initialize, before `notifications/initialized` | −32000 (refused) |
| `tools/list` after the notice | one tool, `lookup`, `additionalProperties: false` |
| `lookup {"key": "office"}` | "505A Dana Hall", `isError: false` |
| `lookup` missing key | "Record not found", `isError: true` |
| `lookup` with extra `"path": "../../etc/passwd"` | −32602 "Expected a string key" |
| undeclared tool | −32602 "Unknown tool" |
| `ping` | −32601 "Method not found" |
| malformed JSON line | −32700 "Parse error", id null; the server did not crash |

### What I found
- **Stricter than mine on startup:** it refuses tools until the client has sent `notifications/initialized`. Mine does not gate on that notice.
- **No version negotiation:** it answered 2025-11-25 although I asked for 2025-06-18.
- **No `ping`**, which the spec expects servers to answer.
- **The error for the path attempt is misleading:** "Expected a string key", when the key *was* a string and the problem was the extra argument. The attempt was still refused.
- **Read-only, as its name says:** the source has no `open(` or write calls (checked by grep), and every probe read only the in-memory dict. That is checked for this file only, not proven in general.
- **Silent demo mode:** started without `--stdio`, it ignored every message I sent and printed its own demo reply with exit 0. My first probe run hit this; I deleted that transcript and re-ran with `--stdio`.
- **No transcript of its own:** unlike mine, it does not log what clients send, so only the client side can be audited.



