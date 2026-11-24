# Transcripts: real MCP conversations, both directions

**Redaction:** none was needed. I searched every transcript for the home-directory path and for `@` (email or account fields) on 2026-11-24, and neither appears. Claude Code's `_meta.claudecode/toolUseId` is kept: it is a per-call id, not an account field. The config `mcp/claude-mcp-config.json` uses relative paths only, so the committed copy is the one that ran.

Every line is `{"t": UTC time, "dir": "client->server" | "server->client", "line": the raw JSON-RPC line}`. Each `line` is the exact text that crossed the pipe.

| File | Client | Server | How it was made (2026-11-24) |
|---|---|---|---|
| `01-scripted-client-own-server.jsonl` | `mcp/client.py` (mine, from scratch) | `mcp/server.py` | `python3 -B mcp/client.py --out transcripts/01-scripted-client-own-server.jsonl`. Sequence: initialize, notifications/initialized, tools/list, a normal search, `limit: 99` (→ -32602), unknown tool (→ `isError: true`), unknown method (→ -32601). |
| `02-claude-code-own-server.jsonl` | Claude Code 2.1.312 (`claude -p`) | `mcp/server.py`, behind `mcp/tap.py` | `claude -p "…" --mcp-config mcp/claude-mcp-config.json --strict-mcp-config --allowedTools mcp__js3-postings__search_postings`. The tap recorded each line as it relayed it. |
| `02-claude-code-answer.txt` | — | — | Claude's final answer from that same session, verbatim, with the date. |

## What the Claude Code transcript shows

1. **An unrequested probe before the handshake.** First message: `server/discover`, with `_meta` declaring protocol `2026-07-28`. My server doesn't know that method and answered -32601. Claude Code then carried on with a normal `initialize`.
2. **Version negotiation.** Claude Code asked for `2025-11-25`. My server supports `2025-06-18`, `2025-03-26` and `2024-11-05`, so it answered `2025-06-18`. Claude Code accepted that and continued.
3. **The client declared capabilities my server never uses:** `roots` (listChanged), `elicitation` (form, url) and the `io.modelcontextprotocol/tasks` extension. My server ignores them. It never asks for roots and never elicits.
4. **The tool call was exactly what was asked:** `{"query": "MLflow", "board": "greenhouse/databricks", "limit": 5}`, plus `_meta` with a tool-use id and a `progressToken`. My server sends no progress notifications.
5. **Claude's answer matched the tool result.** It gave 45 total and the same five titles, in the same order.
