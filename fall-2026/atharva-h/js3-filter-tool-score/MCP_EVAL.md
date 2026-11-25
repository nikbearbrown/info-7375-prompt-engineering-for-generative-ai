# MCP_EVAL — the tool server, and one other server

**Status: Claude's draft, from the code and the two transcripts below. Waiting for my review.**

## The server: `mcp_server.py`
- **Built from scratch:** standard-library Python, JSON-RPC 2.0, one message per line over stdio. No MCP SDK.
- **Methods:**
  - `initialize`, `notifications/initialized`, `ping`, `tools/list`, `tools/call`
  - anything else gets error -32601, "method not found"
  - a message without an `id` is a notification and gets no reply
- **One tool, `score_posting`:** it takes a posting key (`system/board/id`) and returns the v1.0 filter's verdict, with the words behind every rule and point.
  - It returns no description text, only title, locations, URL, and the evidence words.
- **Tests:** 9 in `tests/test_mcp_server.py`, covering the protocol, the errors, the logging, a real stdio process, and the read-only claim below.

## Real transcripts, both directions
The server logs every message it receives (`in`) and sends (`out`) to `state/mcp/transcript_<UTC>.jsonl`.

| Transcript | Client | What it shows |
|---|---|---|
| `transcript_2026-11-25T190338Z.jsonl` | `mcp_client.py`, a minimal client written for this | The handshake; `tools/list`; three `score_posting` calls (FanDuel data analyst, Veeva ADP, Stripe Data Analyst SF); and a call to a tool that doesn't exist (`send_application`), answered with error -32602 |
| `transcript_2026-11-25T190356Z.jsonl` | **Claude Code 2.1.331**, through `.mcp.json` (`claude -p`, only `score_posting` allowed) | Claude Code's real handshake and two tool calls it chose to make. Its final answer is saved in `state/mcp/claude_code_run_2026-11-25T190356Z.json`. |

**What Claude Code actually sent, and what the server did with it:**
1. **A probe first:** `server/discover`, with protocol version `2026-07-28` and a `tasks` extension in `_meta`. The server doesn't implement it and answered -32601. Claude Code then fell back to the ordinary handshake. A server built from the spec I read would never have seen this method in a test, so the real client found it.
2. **`initialize` with protocol version `2025-11-25`.** The client offered `roots` and `elicitation` (form and url). The server echoed the version and declared only `tools`, so it never asks for either.
3. **Two `tools/call` requests.** Each carried `_meta` with Claude Code's `toolUseId` and a `progressToken`. The server ignores `_meta` and never sends progress.

## Declared vs actual

| Declared | Actual | How I know |
|---|---|---|
| `readOnlyHint: true`, `openWorldHint: false`: no writes, no outside world | **True of a request:** while handling `initialize`, `tools/list`, and `tools/call`, the code never calls `open`, `urlopen`, `socket`, or `os.remove` | `test_a_request_never_writes_fetches_or_connects` replaces all four with a function that fails if called |
| (not declared to the client) | **The server process does write one file:** its transcript log, opened once at start. It records every argument a client sends. A client reading `tools/list` can't see this. | `open_log` in `mcp_server.py`; the log files in `state/mcp/` |
| The `key` must match a pattern (`inputSchema.pattern`) | **Enforced on the server too, not just declared.** `../../etc/passwd`, an extra argument, or a key that isn't in the corpus returns a tool error (`isError: true`). The lookup is only ever a dictionary lookup, never a file path. | `test_bad_arguments_are_tool_errors_not_protocol_errors` |
| `idempotentHint: true` | True: the corpus is loaded once at start and never changes while the server runs | The code; the corpus is frozen (FILTER.md) |
| It supports protocol versions `2025-11-25`, `2025-06-18`, `2025-03-26`, and `2024-11-05` | **Weaker than it sounds.** The server echoes any of these, but I haven't checked every difference between them. It works for the tools-only subset used here, with Claude Code and with my client. | The two transcripts |
| `structuredContent` in each result | Sent without an `outputSchema`, so a client has no declared shape to check it against | `TOOL` in `mcp_server.py` |

**The annotations are hints, not guarantees.** A client cannot check `readOnlyHint`. It has to trust the server, and it does. That is why the read-only test exists.

## What a client is not entitled to
- **Any action outside reading:** there is no tool that writes, sends, applies, emails, or fetches. A call to one (`send_application` in the first transcript) is a protocol error, not something that silently does nothing.
- **Arbitrary files:** the key never becomes a path.
- **The full posting text, my labels, my audit verdicts, the persona file, or the transcript log:** none of them is reachable through the tool.
- **Changing the filter:** the only argument is `key`. The rules, weights, and threshold change only by a new FILTER.md version.
- **A decision about applying:** every result carries "A rule output from FILTER.md v1.0, not a judgment of whether to apply". Claude Code repeated that line in its answer. Whether a posting is worth Riley's application stays with me (see SIGNOFF).

## Trust decision
- **I let Claude Code use this server, with `score_posting` as its only allowed tool** (`--strict-mcp-config --allowedTools mcp__js3-job-filter__score_posting`). The reasons:
  - I've read the whole server (about 190 lines).
  - It has no network or write path during a request, and a test fails if one appears.
  - It reads only the frozen corpus.
- **The risk I keep:** the result passes job titles through verbatim, and a title is text the employer wrote. A title with instructions in it would reach the model as tool output. The mitigation is the client's: treat tool output as data. In this server, the only other thing returned is the rule output.
- **Not allowed:** giving the server more tools without a new version of this evaluation, or running it with a client that is allowed other tools in the same session.

## The other server
_To be written. Which server, and whether to install it, needs my OK first._
