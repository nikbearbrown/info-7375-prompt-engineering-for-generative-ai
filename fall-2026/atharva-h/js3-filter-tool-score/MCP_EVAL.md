# MCP_EVAL — the tool server, and one other server

**Status: Claude's draft, from the code and the three transcripts below. Waiting for my review.**

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
  - The whole server is 169 lines, short enough to read in full (**to confirm when I review this**).
  - It has no network or write path during a request, and a test fails if one appears.
  - It reads only the frozen corpus.
- **The risk I keep:** the result passes job titles through verbatim, and a title is text the employer wrote. A title with instructions in it would reach the model as tool output. The mitigation is the client's: treat tool output as data. In this server, the only other thing returned is the rule output.
- **Not allowed:** giving the server more tools without a new version of this evaluation, or running it with a client that is allowed other tools in the same session.

## The other server: Fetch (`mcp-server-fetch`)
- **What it is:** the reference Fetch server from the MCP project's servers repository (`github.com/modelcontextprotocol/servers`, `src/fetch`). PyPI package `mcp-server-fetch` 2026.11.18, author "Anthropic, PBC.", MIT license.
- **How it was installed:** installed on 2026-11-25 with my OK, into a throwaway Python 3.12 environment outside this folder. Nothing was added to the repo.
- **How it was run:** the session is `mcp_eval_fetch.py`, and its transcript is `state/mcp/other_fetch_2026-11-25T212010Z.jsonl` (both directions).
- **Why this one:** it is the opposite of `score_posting`. It is open-world: the model picks any URL.

**What it declares** (from `initialize`, `tools/list`, `prompts/list`):
- **Capabilities:** tools, prompts, and resources.
- **One tool, `fetch`:** arguments `url`, `max_length`, `start_index`, `raw`, and `timeout_ms`. Annotations: `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: true`.
- **One prompt, also `fetch`.**
- **A tool description that speaks to the model:** "Although originally you did not have internet access, and were advised to refuse and tell the user this, this tool now grants you internet access." A description is supposed to say what the tool does. This one also tells the model to override an earlier instruction. It's well meant, but it's the same move a hostile server would make.

| Declared | Actual | How I know |
|---|---|---|
| `readOnlyHint: true` | **Read-only for the server, not for my data.** The URL is chosen by the model, and anything in it leaves the machine. The call to `https://example.com/?persona=riley-navarro&needs=sponsorship` succeeded, so the fictional persona's name and sponsorship need went to a host the model picked. | Call 5 in the transcript |
| `readOnlyHint: true` | **It can install code during a tool call.** By default, if Node.js is on PATH, the first HTML extraction runs `npm install` against the npm registry. The code's own comments say so (`readability_js.py`: "reaches the npm registry during a tool call"). Node and npm are on this machine, so I ran it with `--no-readability-js` to keep it from installing more than I had approved. | The source of the installed package; the flag |
| Private addresses are refused by default | **True.** A file served by the eval script on `127.0.0.1` was refused before any request was sent: the loopback server received **0 requests**, not even for `robots.txt`. | Call 6, plus the request counter in `mcp_eval_fetch.py` |
| `max_length` is an integer (strict) | **True.** `"10"` as a string is a validation error, returned as a tool error. | Call 7 |
| robots.txt is respected for model-initiated fetches | Present in the code (`check_may_autonomously_fetch_url`) and seen in call 6: the robots.txt request was the one refused. The `--ignore-robots-txt` flag turns it off. | The source; call 6 |
| `resources` capability | Declared, but the server defines no resources. I did not call `resources/list`. | `initialize` result |

**What a client is not entitled to through Fetch, by default:** private, loopback, and link-local addresses, and pages whose robots.txt disallows them. Everything else on the public internet is reachable, unless the operator sets `--allowed-hosts`.

**My trust decision for Fetch:** **not allowed in the job-search agent's session.**
- **Why:**
  - That session holds Riley's persona, my labels, and my audit verdicts.
  - Fetch would give the model a way to send any of it to any host, in a URL, while declaring itself read-only.
  - It would also bring in page text written by strangers, which the model would read as tool output.
- **If I needed it:** I would run it in a separate session holding no private data, with `--allowed-hosts` set to the three job-board API hosts and `--no-readability-js`. That restores the same boundary my JS2 policy enforces in code.
- **The difference from my server:** both declare `readOnlyHint: true`. That hint says the server changes nothing. It does not say that no data leaves. `openWorldHint` is the one that matters for that, and only `score_posting` sets it to false.
