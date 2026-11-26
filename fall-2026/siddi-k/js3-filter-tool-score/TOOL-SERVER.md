# The tool, its transcripts, and two evaluations (brief Step 2.3)

Facts and tables by Claude, each pointing to its evidence file. The two **trust decisions** are Siddi's, saved verbatim.

## 1. What the agent offers Claude

- **One capability:** `score_posting(board, posting_id)`. It runs FILTER.md's filter on one posting already saved in this folder, and returns the verdict, the failed gates, the score, and every matched word with the sentence it came from.
- **Code:** [js3/mcp_server.py](js3/mcp_server.py). Written from scratch, Python standard library only. stdio transport, one JSON-RPC 2.0 message per line.
- **Lifecycle:** the 2025-11-25 one the brief names: `initialize` → `notifications/initialized` → `tools/list` → `tools/call`.
- **Run it:** `python -m js3.mcp_server --transcript evidence/mcp/<name>.jsonl`. The `--transcript` file records every line in both directions, written by the server itself.

## 2. Real transcripts, both directions

| Session (UTC, 2026-11-26) | Client → server | Files |
|---|---|---|
| `03-06-55Z`, my server | Claude Code 2.1.325, `claude-sonnet-5-5`. `server/discover` (2026-07-28 probe) → my `-32000` → `initialize` asking `2025-11-25` → `notifications/initialized` → `tools/list` → 2 × `tools/call` | [evidence/mcp/2026-11-26T03-06-55Z/](evidence/mcp/2026-11-26T03-06-55Z/): `server-transcript.jsonl` (server side), `claude-stream.jsonl` (the CLI's own `tool_use` / `tool_result` messages), `argv.json`, `prompt.txt` |
| `03-17-39Z`, course server | **Failed.** My stdio tap could not create its log folder and exited, so Claude Code marked the server `failed`. Claude answered that it had no lookup tool and would not guess the record. | [evidence/other-server/2026-11-26T03-17-39Z/](evidence/other-server/2026-11-26T03-17-39Z/) |
| `03-18-29Z`, course server | Same sequence as `03-06-55Z`. `lookup {"key":"office"}` → "505A Dana Hall" | [evidence/other-server/2026-11-26T03-18-29Z/](evidence/other-server/2026-11-26T03-18-29Z/): `tap-transcript.jsonl` (logged by [tools/stdio_tap.py](tools/stdio_tap.py), a pass-through) |
| Experiment T, 30 calls | Claude may call `score_posting` while judging a held-out posting | `evidence/experiments/T/*-server.jsonl` |
| Scripted probe, both servers | The same 14 messages to each server, P1–P14 | [evidence/mcp/probe.txt](evidence/mcp/probe.txt), [evidence/other-server/probe.txt](evidence/other-server/probe.txt) |

**Claude's answer in `03-06-55Z` (claude-stream.jsonl):** it reported both verdicts and their matched words. Asked whether the result shows either posting is worth applying to, it said no, quoting the result's own label ("not a judgment"). It also relayed "ai" as a matched topic for the Notion posting without noticing that the matched sentence is Notion's company blurb, even though the tool result shows that sentence.

## 3. My server, evaluated as if someone else wrote it

| Declared | Where | What it does | Evidence |
|---|---|---|---|
| `readOnlyHint: true`, `destructiveHint: false` | `tools/list` annotations | A call ran with every write-mode `open` and every socket blocked, and still succeeded. **But the process is not read-only:** with `--transcript` it appends to one log file, which can only be inside `evidence/` (`policy.check_write`). | `tests/test_mcp_server.py::test_call_is_actually_read_only_and_offline`, `::test_transcript_can_only_be_written_inside_the_folder`; mutant "readOnlyHint but it writes" caught |
| `openWorldHint: false` | annotations | No socket is opened during a call. | same test |
| `idempotentHint: true` | annotations | Holds inside one process: the same call gave the same answer. **Across restarts it can change**, because without `--collection` the server serves the newest collection. | `::test_same_call_same_answer`; `latest_collection()` in the code |
| `inputSchema`: board enum, id pattern, no extra keys | `tools/list` | Enforced by hand, not just declared. Violations come back as tool errors (`isError: true`), as the 2025-11-25 schema advises for errors from the tool. | probe P8, P9, P11; `::test_schema_is_enforced_not_just_declared`; mutant "schema not enforced" caught |
| "a recomputable record of keyword rules, not a judgment" | tool description | Every result carries `"label": "record: … not a judgment"` and its `filter_version`. | probe P7; Claude repeated the label in `03-06-55Z` |
| supports `2025-11-25` | `initialize` result | Answers `initialize` with the client's version if it knows it, otherwise `2025-11-25`. It has no 2026-07-28 support: `server/discover` gets `-32000`, which a dual-era client reads as "legacy, fall back". | probe P2, P3; `03-06-55Z` lines 1–4 |
| (not declared) | | Answers `ping` at any time. Refuses tools before `initialize` (`-32000`). An unknown method gets `-32601`, an unknown tool `-32602`, bad JSON `-32700`, and a batch `-32600`. | probe P1, P4, P10, P12–P14 |
| (a bug I found) | | Before `eb13b533`, a `--transcript` path in a missing folder made the server die at startup. A client then sees the server as "failed". | the course-server tap had the same bug: session `03-17-39Z` |

**What a compatible client is *not* entitled to.** Speaking the protocol correctly is compatibility, not permission. A client that does everything right still cannot:
- call a tool that was not listed (`write_file` → `-32602`, probe P10);
- pass arguments outside the schema, or a path of any kind (there is no path argument, and ids must match `^[A-Za-z0-9-]{1,64}$`);
- reach the network, the persona file, or any file other than the saved postings;
- assume a newer protocol than the server advertises;
- treat a verdict as a judgment that a posting is worth Siddi's time;
- take the annotations as guarantees. The 2025-11-25 schema calls every `ToolAnnotations` property a **hint**, and says clients should never make tool-use decisions based on annotations received from untrusted servers. (Copy saved 2026-11-18 in Make-up 1's `evidence/sources/2025-11-25_schema.md`.) This server's annotations are checked by the tests above, not by the protocol.

**Siddi's trust decision about this server** (written by Siddi, pasted in chat 2026-11-25 about 22:38 ET, saved verbatim):

### js3.mcp_server

I would allow Claude to call this server unattended, but only for its current read-oriented tools and within the existing filesystem and network restrictions. I relied on the sandbox test, input-validation tests, and reading the implementation, rather than its self-description or the word “idempotent.” I would not assume repeated calls return the same data across restarts, because the server serves the newest collection and can change its answer. I would reconsider unattended use if it gained write tools, accessed files outside `evidence/`, or silently changed what collection it reads.

## 4. The other server: the course's Chapter 8 lesson server

- **Source:** `lessons/08-mcp-from-scratch/code/main.py` in the course repository (github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai), last changed in commit `a8629ce1`, sha256 `948337af…1769`.
- **How it ran:** [tools/other_server_session.py](tools/other_server_session.py) takes the file from git, checks the sha256 and only then runs it. It was read in full first: 72 lines, imports only `argparse`, `json` and `sys`.

| Declared | Where | What it does | Evidence |
|---|---|---|---|
| name `info7375-readonly` | `serverInfo` in `initialize` | No file or network calls in the code. The only data is an in-memory dict `{"office": "505A Dana Hall"}`. **Read-only by reading the code, not by a sandboxed test.** Claude never saw this name, because Claude Code does not pass `serverInfo` to the model. | code; probe P3; `03-18-29Z` Claude: the description's "Read" is "the tool's own wording, not a guarantee" |
| no annotations | `tools/list` | Nothing tells a client it is read-only except the word "Read" in the description. | probe P6 |
| "Read a public course fixture" | description | Returns "505A Dana Hall" for `office`; anything else gives "Record not found" with `isError: true`. | probe P7, P9, P11 |
| `inputSchema` with `additionalProperties: false` | `tools/list` | Enforced, but as a **protocol error** (`-32602 "Expected a string key"`), not a tool result with `isError`. The 2025-11-25 schema says errors from the tool should be reported inside the result. Whether argument validation counts as "from the tool" is open to reading. | probe P8 |
| `protocolVersion: 2025-11-25` | `initialize` result | Always that version, whatever the client asks. | probe P3 |
| (not declared) | | Requires `notifications/initialized` before any tool use: stricter than the spec, which only restricts the client. It also refuses `ping` before then (`-32000`), though the spec lets pings through. `server/discover` gets `-32000`, and Claude Code fell back to `initialize` cleanly. | probe P1, P2, P4; `03-18-29Z` lines 1–4 |

**What a compatible client is not entitled to here:** the same list as in §3. In addition, the name "readonly" entitles a client to nothing: it is self-reported. The 2026-07-28 discovery page says the same of `serverInfo`, that it is self-reported and a client should not rely on it for security decisions. (Make-up 1 `evidence/sources/2026-07-28_server_discover.md`.)

**Siddi's trust decision about the course server** (written by Siddi, pasted in chat 2026-11-25 about 22:38 ET, saved verbatim):

### Chapter 8 server

I would allow Claude to call this server unattended for its limited read-only task because the code is small and contains only one in-memory record, but I would keep its scope narrow. I relied on reading the 72 lines of source code, not testing it in a sandbox, and I would not rely on the word “readonly” in its name or any unverified self-description. I know it is currently simple, but I have less test evidence for it than for my own server. I would reconsider if it gained access to external data, additional tools, or write capabilities, or if its code changed without review.

## 5. The two servers side by side

| Question | Mine | Course Ch 8 |
|---|---|---|
| Read-only shown how | Tests that block writes and sockets during a call | Reading 72 lines of code |
| Says it is read-only how | `readOnlyHint` and other annotations | Only its `serverInfo` name and the word "Read" |
| Bad arguments | `isError: true` result | `-32602` protocol error |
| `ping` before ready | Answered | Refused |
| Works with Claude Code 2.1.325 | Yes, after the discover fallback | Yes, after the discover fallback |
| Two-way transcript | Written by the server | Needed my pass-through tap |
