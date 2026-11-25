# Evaluation: my own server, `earlybird-score`, judged like someone else's

Evaluated 2026-11-25 with Claude's help (SOURCES.md). The server was written by Claude from Vrajesh's decisions (read-only,
one tool, `score_posting`), tests written before the code. Evidence: `earlybird-score/results.json` (from
`scripts/eval_own_server.py`), `tests/test_mcp.py`, and the real Claude Code run in `transcripts/`.

## Declared vs actual

| Declared (module docstring, `tools/list`, annotations) | Actual (evidence) | Match |
|---|---|---|
| Exactly one tool, `score_posting`, read-only, not open-world | `tools/list` returns one tool with those annotations (test) | yes |
| Capabilities: tools only | `initialize` returns `{"tools": {"listChanged": false}}` and nothing else | yes |
| No network | no network library imported by `mcp_server`, `rule`, `claims`, `boards`, `resume` (only `socket`, to disable it); after the start-up patch `connect`, `connect_ex` and `create_connection` all refused | yes, **after a fix** (see below) |
| Writes nothing except an optional log | project tree hashed before and after a full scripted run: 0 files changed | yes |
| Refuses bad input | path traversal, wrong types, extra arguments, unknown board: tool errors; unknown tool: -32602; unknown method: -32601; malformed JSON: -32700 (tests and `scripted-client-2026-11-25.jsonl`) | yes |
| Works with a real client | Claude Code 2.1.332 connected, listed the tool and called it twice (`claude-code-session-2026-11-25.md`) | yes |

## Defects found by evaluating it (not by Claude Code)
1. **My network guard was weaker than my claim.** It patched `socket.connect` only; `connect_ex()` still connected to a local
   listener. Fixed with a failing test first (`review/14-network-guard-red.txt`, then `review/15-...`). It is a guard, not a
   sandbox: the real guarantee is the import check above.
2. **Protocol lifecycle is not enforced.** A `tools/call` before `initialize` is answered normally.
3. **No input size limit.** A line of any size was read whole, so a client could make the server hold a huge message in memory.
   **Fixed 2026-11-25** with failing tests first (`review/20-input-limit-red.txt`, then `review/21-...`): messages over 1 MiB are discarded
   unread and answered with error -32600, and the server keeps running (4 tests in `InputLimit`). Not tested: many requests in parallel, or a
   slow client sending one message very slowly.
4. **Newer protocol not supported.** Claude Code first sent `server/discover` for protocol revision 2026-07-28; my server
   answered -32601 and Claude Code fell back to `initialize`. It worked, but only because the client fell back. The official
   fetch server does support the newer revision.
5. **The result drops information the reader needs** (found by Claude, reading the real result): each claim has a label and a
   quote but not the claim's statement, and `why` is empty for supported and contradicted claims. Claude said the
   `early_career` quote "seems to cut against the label".
6. **The result tells the model about the persona.** The justification text includes facts such as "the resume needs
   sponsorship". With the fictional persona that is fine; with a real resume this server would hand the model those facts on
   every call.

## What a compatible client is and is not entitled to
- **Not entitled** to send, apply, email, message, log in, write, or reach the network: no such tool exists, and the one tool
  validates its arguments against an allow-list (`posting_id`, `board`).
- **Entitled** to score any posting in the local snapshot and read the quoted spans the labeler returns, and to learn the
  persona's facts through the justification text (defect 6).
- The optional log path comes from `EARLYBIRD_MCP_LOG`, so whoever starts the server decides where it writes; it records every
  message in both directions.

## Not checked
- Many requests in a row (no rate limit), many clients at once, and a client that sends one message very slowly. (A single very large message is now refused: defect 3.)
- Behaviour with a client other than my scripted client and Claude Code 2.1.332.
- Running it with a real resume (the whole project is built on the fictional persona).
- That the labels in the results are right for every posting; only the 24 claim-check items and the 62-item audit sample were compared with Vrajesh's labels.

## Trust decision
Vrajesh's decision, in his words (2026-11-25):

> "I would trust it provisionally for the fictional persona and local snapshot. I would withhold approval for a real resume because its justifications can expose persona information to the model. The network guard is useful, but it is not a sandbox."
