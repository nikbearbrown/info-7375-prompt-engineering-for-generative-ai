# Tool server evaluations

Two servers are evaluated the same way: what each one **declares**, what it actually **does**, what a compatible client is **not entitled to**, and a **trust decision**.

- **Mine:** `mcp_server.py`, written from scratch for JS3. I read the other server's code only after mine was written and tested.
- **The other server:** the course's Lesson 8 reference server, `lessons/08-mcp-from-scratch/code/main.py`. It is in the course repository (`nikbearbrown/info-7375-prompt-engineering-for-generative-ai`), and its sha256 is `948337afc71b67b659aac44b4a8f3efec5dc699b9bb7c2e683dd6888068b1769`.

Every claim below points to a transcript, a test, or a line of source. All transcripts are real runs on 2026-11-25 (UTC). Each one is a JSON-lines record of every line in both directions, with a timestamp and direction (`client->server` or `server->client`).

## The transcripts

| File | What it is |
|---|---|
| `transcripts/server-session-2026-11-25T041833Z-8005.jsonl` | **Claude Code → my server**, session 1, recorded by my server. Claude Code 2.1.331, model `claude-opus-5-5`, with every built-in tool switched off (`--tools ""`) and only my server loaded (`--strict-mcp-config`). The prompt is `claude-prompt.txt`. |
| `transcripts/claude-side-session-2026-11-25T041832Z.jsonl` | The same session from Claude's side (stream-json): the prompt, each tool call, each result, and Claude's answer. Only machine details were removed, by `save_claude_session.py`; its first line lists exactly what. |
| `transcripts/server-session-2026-11-25T042642Z-8611.jsonl` and `claude-side-session-2026-11-25T042640Z.jsonl` | Session 2 with the same prompt, after the two fixes below. This is the session that matches the final code. |
| `transcripts/client-own-server-2026-11-25T041816Z.jsonl` | My own scripted client (`mcp_client.py`) against my server: every tool, plus six probes of what a client is not entitled to (`probes/own-server.json`). |
| `transcripts/client-own-server-robustness-before-fix-2026-11-25T042125Z.jsonl` | The lifecycle-and-robustness probe (`probes/lifecycle-and-robustness.json`) against my server **before** the fix: it crashed. |
| `transcripts/client-own-server-robustness-after-fix-2026-11-25T042140Z.jsonl` | The same probe after the fix. |
| `transcripts/client-lesson08-server-2026-11-25T042125Z.jsonl` | The same probe against the Lesson 8 server. My client was the client here, so this is the other direction: my code talking to a server I did not write. |
| `transcripts/server-session-*.jsonl` (the rest) | My server's own record of each scripted session above. |

**Replay check:** `python3 mcp/replay.py <server-session file>` sends every recorded client line to the current server code and compares the replies.
- **Session 2** comes back identical, every reply.
- **The four earlier sessions** (session 1, the scripted session and both robustness probes) were recorded before the two descriptions were corrected at 04:26 UTC. Only their `initialize` and `tools/list` replies differ, and those differences are exactly the corrected wording. Every tool result and every error reply is identical.
- **The before-fix probe** also differs on the deep-nesting line: no reply was recorded then, and the server now returns a parse error.

**Which filter the server serves:** FILTER.md **v1.1**, pinned in `mcp_server.py` (`served_rules`). That is the version it was evaluated and recorded with. When I adopted v1.2 on 2026-11-25, the server did not change, and the replays above confirm it: every tool result is still identical. Serving v1.2 would be a separate change to the server, and it would need its own evaluation and transcripts.

## 1. My server: `yash-js3-job-filter` 1.0.0

### What it declares

- `initialize`:
  - capabilities `{"tools": {"listChanged": false}}`
  - one of three protocol versions: 2025-06-18, 2025-03-26 or 2024-11-05
  - instructions saying it cannot apply, email, message, log in, write files for the client, or reach the network, and that it keeps a transcript
- `tools/list`: two tools, `score_posting` and `search_saved_postings`. Each declares:
  - `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: false`
  - a closed input schema (`additionalProperties: false`) with length and range limits

### Declared versus what it does

| Declared or implied | What I checked, and how | Result |
|---|---|---|
| Read-only | `test_the_only_file_write_is_the_transcript` reads the source and finds every write-mode `open`, `write_text`, `unlink` or `rename`. `test_a_real_session_changes_nothing_but_its_own_transcript` hashes every file in a copy of the project, runs a full session as a separate process, and hashes again. | The only write is the transcript, inside `mcp/transcripts/`. No other file changed. |
| No network | `test_server_and_the_code_it_runs_import_nothing_that_reaches_out` checks the imports of `mcp_server.py`, `job_filter.py` and `postings.py` against a list that includes `socket`, `urllib`, `http`, `subprocess` and `ssl`. | None imported. This is a static check only. I did not watch the network while the server ran. |
| No paths from the client | `test_no_tool_takes_a_path_url_or_command`. In the scripted session, a call with an extra `"path": "/etc/passwd"` argument was refused (`isError`). | No tool takes a path, URL or command. |
| No apply, email or message | The scripted session called `apply_to_job`, which got `-32602 Unknown tool`. In both Claude sessions, Claude was asked to apply and to save a note, and it said it could do neither. | No such capability exists. |
| `score_posting` is the filter | `test_score_posting_matches_the_filter_exactly` | Same decision, score and points as `job_filter.evaluate`. |
| Limits | Tests and the scripted session: `limit` 500 was refused, a 100,001-character description was refused, and `true` for an integer was refused. | Enforced. |
| Lifecycle | `test_tools_before_initialize_are_refused_but_ping_works` | Tools before `initialize` get `-32002`. **It does not wait for `notifications/initialized`**: `tools/list` works right after `initialize`. The Lesson 8 server is stricter here. |
| Version negotiation | Claude Code session 1, lines 3–4 | Claude Code asked for 2025-11-25. My server answered 2025-06-18, its newest, and Claude Code accepted and carried on. |
| **Found: a crash on one input** | The robustness probe sent one line of 5,000 `[` characters. | Before the fix, `RecursionError` killed the server and later requests went unanswered (before-fix transcript). Fixed by catching it, plus a catch-all so one bad message cannot stop the server. Regression test: `test_deeply_nested_json_is_a_parse_error_not_a_crash`. |
| **Found: the description said "stored nowhere"** | Reading my own transcript code while writing this evaluation | `score_posting` said nothing was "stored", but the transcript stores every message, including the posting text a client sends. Both the description and the instructions now say so. Session 1 shows the old wording; session 2 shows the new. |
| **Found by Claude, not fixed: ties are unexplained** | Claude's answer in session 2: "11 postings are tied at 80 … The tool doesn't say how it orders a tie." | True. The server breaks ties by board, then ID (as FILTER.md section 4 does), but the tool description does not say so. Left unchanged so the final transcript matches the final code. |
| A probe it handled oddly | Claude Code session 1, line 1: before `initialize`, Claude Code sent `server/discover` with `protocolVersion` `2026-07-28` in `_meta`. | My server answered `-32002 not initialized`, which wrongly suggests the method exists. `-32601 method not found` would have been more accurate. Claude Code fell back to `initialize` either way. |

### What a compatible client is not entitled to

- **A decision about the person.** `confirmed` and `review` are FILTER.md v1.1 screening output for a fictional persona. They are not a judgment that a posting is worth applying to. The instructions say so, and Claude repeated it in session 2.
- **Any file, path, URL, command, or the network.** No tool accepts one. The results file and the transcript folder are fixed at start-up by whoever launches the server, and both must be inside this folder.
- **My real résumé or data.** Only the fictional persona's skills are loaded.
- **Fresh data.** The search tool reads a saved run over postings collected on 2026-11-10, and its description says they may no longer be open.
- **Other sessions' transcripts.** No tool reads them.
- **Roots, elicitation or sampling.** Claude Code offered roots and elicitation (session 1, `initialize`). This server never asks for either.
- **Stack traces or internal paths.** Errors are generic. Traces go to stderr, which the client never receives (`test_one_failing_message_does_not_stop_the_server`).
- **Trust in the annotations themselves.** `readOnlyHint` is something the server says about itself. A client should not trust it from a server it has not checked; the tests above are the check.

### Trust decision (mine to make)

**Trust decision:** ______________________ (Yash)

*Claude's recommendation, for me to accept, change or reject:* trust it for local use with Claude Code on this machine, with these limits:
- Launch it myself, with the default results file.
- Do not paste private documents into `score_posting`, because the transcript keeps them.
- Treat every answer as screening, not advice.
- Evaluate it again whenever a tool is added.

## 2. The other server: the Lesson 8 reference server (`info7375-readonly` 1.0.0)

**Source:** course repository, `lessons/08-mcp-from-scratch/code/main.py` (sha256 above). Its own lesson calls it "a deliberately small stdio teaching subset" and "not a production or conformance-certified MCP implementation" (`docs/en.md`). I judged it against that stated scope, by reading its 72 lines and by running the same probe I ran on mine.

### What it declares

- `initialize`: always `protocolVersion` `2025-11-25`, capabilities `{"tools": {}}`. No instructions.
- `tools/list`: one tool, `lookup`, "Read a public course fixture". Its input is `{"key": string}`, required, with `additionalProperties: false`. No annotations.

### Declared versus what it does

| Declared or implied | Evidence | Result |
|---|---|---|
| Reads a public fixture | Source: it imports only `argparse`, `json` and `sys`, and `lookup` returns a value from a dictionary written in the code (`{"office": "505A Dana Hall"}`). | Read-only in fact, with no file or network access. It does not *declare* that with `readOnlyHint`. |
| Lifecycle | Probe: `tools/list` before `initialize` and again after `initialize` but before `notifications/initialized` both got `-32000`. After the notification, it worked. | Stricter than mine. It waits for the initialized notification. |
| Version 2025-11-25 | Probe: I asked for 2025-06-18 and it answered 2025-11-25 anyway (source line 27). | No negotiation. A client that does not support 2025-11-25 must disconnect. |
| A 2025-11-25 server answers `ping` | Probe: `ping` after initialization got `-32601 Method not found`. | Not implemented, although the protocol version it claims includes it. |
| Unknown tool vs unknown record | Probe: `write_file` got `-32602 Unknown tool`. Source: an unknown key returns a tool result with `isError: true`. | As its lesson teaches: a protocol error versus a tool error. |
| Malformed input | Probe: `{this is not json` got `-32700`, and `[]` got `-32600`. | Handled. |
| **One line of 5,000 `[` characters** | Probe | **The server crashed** (`RecursionError`, exit code 1) and the rest of the probe got no reply. It has the same weakness mine had before my fix. |

### What a compatible client is not entitled to

- Anything beyond the one fixture value. There is no other data, and no write or network path.
- **The truth of the value.** A successful JSON-RPC exchange shows the protocol worked, not that "505A Dana Hall" is correct. That is the lesson's own "Conducting AI" point, and the protocol cannot establish it.
- A server that survives malformed input, or that negotiates versions.

### Trust decision (mine to make)

**Trust decision:** ______________________ (Yash)

*Claude's recommendation, for me to accept, change or reject:* safe to connect for teaching, because it can do nothing outside its own process. But don't rely on it as a dependency: it doesn't answer `ping`, doesn't negotiate a version, and can be stopped by one malformed line.

## What these evaluations do not show

- I did not monitor the network or the file system at the operating-system level. The "no network" result rests on reading imports, not on watching traffic.
- Two Claude sessions with one prompt are not a test of how Claude uses the tools in general. They show only what happened on those two runs.
- The probes cover the cases I thought of. Inputs I did not think of are untested, and the deep-nesting crash was found only because I thought to try it.
