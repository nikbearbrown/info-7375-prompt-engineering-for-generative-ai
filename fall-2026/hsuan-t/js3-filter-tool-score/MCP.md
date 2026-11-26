# MCP server: `score_posting`

`job_agent/mcp_server.py` is a small stdio MCP server (JSON-RPC 2.0, one message per line) with
one read-only tool. It uses only the Python standard library and the project's own code; it never
opens a network connection or starts a process. Design notes: `docs/adr/0003-stdio-mcp-server.md`.

## Run

From the repo root:

```
.venv/bin/python -m job_agent.mcp_server
```

stdout carries only JSON-RPC messages; logs go to stderr. The server exits with code 0 when stdin
closes.

## Register with Claude Code

```
claude mcp add job-search-agent -e PYTHONPATH="$PWD" -- "$PWD/.venv/bin/python" -m job_agent.mcp_server
```

Run this from the repo root. `$PWD` makes both paths absolute, because the docs don't say which
folder Claude Code starts a stdio server in, and `-m job_agent…` only imports when the repo is on
the path. Syntax checked against `claude mcp add --help` on 2026-11-25
(`claude mcp add [options] <name> <commandOrUrl> [args...]`, `-e KEY=value`, default scope `local`).
The same command, started from `/tmp` with that `PYTHONPATH`, answered `initialize` and
`tools/call` (2026-11-25).

## Protocol

- `initialize`: answers with the client's `protocolVersion` if it is one of `2024-11-05`,
  `2025-03-26`, `2025-06-18`, `2025-11-25`, otherwise `2025-06-18`. `serverInfo` is
  `{"name": "job-search-agent", "version": "js3"}`; `capabilities.tools` is present.
- Notifications (any message without an `id`, e.g. `notifications/initialized`) get no reply.
- `ping` returns `{}`.
- `tools/list` returns the one tool below.
- Errors: unknown tool or arguments that break the schema → `-32602`; unknown method → `-32601`;
  a line that is not JSON → `-32700` with `id: null`; a message that is not a request object →
  `-32600`. The server keeps reading after any error.

## Tool contract: `score_posting`

Input (`additionalProperties: false`, both required):

| field        | type   | notes                                                                  |
|--------------|--------|------------------------------------------------------------------------|
| `board`      | string | enum: boards in `data/boards.json` that have a saved `evidence/raw/*/<board>_content.json` |
| `posting_id` | string | compared with `str(posting.id)`, so Greenhouse ints and Ashby UUIDs both work |

Annotations: `readOnlyHint: true`, `openWorldHint: false`.

The server reads the **newest** saved raw file of the board (by run folder name), finds the
posting, and judges it with `rule.judge` and the default criteria (`personas/aarav-patel.*`).

- Found: `isError: false`, `structuredContent` = the rule verdict (CONTRACT Out shape), and a text
  block with the title, the verdict and every justification line.
- Not found: `isError: true` with a text message.

## Transcript

Every message received and sent is appended, in order, as `{"ts", "dir": "in"|"out", "msg"}` to
`transcripts/mcp-<UTC YYYY-MM-DD>.jsonl`. Set `JSA_MCP_TRANSCRIPT_DIR` to write to another folder
(created if missing). A line that is not JSON is recorded as its raw text.

## Tests

`tests/test_js3_mcp_server.py` starts the server as a subprocess and talks to it over stdin/stdout.
