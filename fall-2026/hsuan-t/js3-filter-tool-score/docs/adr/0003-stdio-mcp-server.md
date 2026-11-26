# 0003 — MCP server: hand-written stdio JSON-RPC, one read-only tool

## Status
Accepted (JS3).

## Context
The rule judge should be callable from an MCP client (Claude Code) so a person can ask "how does
this posting score?" while reading it. The project keeps its dependencies minimal and treats any
network or process access as something to justify.

## Decision
- `job_agent/mcp_server.py` implements the stdio transport and the few JSON-RPC methods it needs
  (`initialize`, `ping`, `tools/list`, `tools/call`) with the standard library, instead of the
  `mcp` SDK. It imports no networking or subprocess modules.
- One tool, `score_posting(board, posting_id)`, read-only: it only reads the newest saved raw
  file of a board and runs `rule.judge` with the default criteria. It never fetches a board, so
  results are reproducible from files in the repo.
- `board` is an enum of boards from `data/boards.json` that have a saved raw file; anything else
  (including path-like values) is rejected with `-32602` before any file path is built.
- Every message in and out is appended to a dated JSONL transcript (`transcripts/`, or
  `JSA_MCP_TRANSCRIPT_DIR`), so a session can be audited afterwards.

## Consequences
- New protocol versions need an edit to the supported-version list; unknown versions fall back
  to `2025-06-18`.
- The schema check is hand-written for this one schema; a second tool would need its own check.

## Alternatives considered
- The `mcp` Python SDK: a new dependency tree for four methods, and harder to show it opens no
  sockets.
- A tool that fetches live boards: open-world, slower, and not reproducible from saved evidence.
