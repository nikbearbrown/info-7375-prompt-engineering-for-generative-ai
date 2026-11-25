# TOOLSERVER.md — my agent as a tool, and two evaluations (Chapter 8)

## 1. What I offer Claude

**One capability: `search_postings`.** It is a read-only, whole-word search over the postings my agent saved on 2026-11-24 (6 boards, 3,117 postings, `runs/2026-11-24T220432Z-live`).

- **Server:** `mcp/server.py`, written from scratch in standard-library Python, with no MCP SDK.
- **Protocol:** stdio JSON-RPC 2.0, one message per line. It handles `initialize`, `notifications/initialized`, `ping`, `tools/list` and `tools/call`. Every other method gets error -32601.
- **Helpers:** `mcp/tap.py` sits between a real client and the server and records every line in both directions. `mcp/client.py` is my scripted client. Both are from scratch.
- **Tests:** `tests/test_mcp_server.py` (13), offline.

**How to run it:**
```bash
python3 -B mcp/client.py --out transcripts/01-scripted-client-own-server.jsonl
claude -p "Use the search_postings tool to find postings mentioning MLflow on greenhouse/databricks, limit 5, and list their titles." --mcp-config mcp/claude-mcp-config.json --strict-mcp-config --allowedTools mcp__js3-postings__search_postings
```

**The real transcripts** are in `transcripts/`; the README there explains each file.
- `01` is my client against my server.
- `02` is **Claude Code 2.1.312 as the client**, recorded by the tap, plus Claude's answer from 2026-11-24. The answer matched the tool's result: 45 postings in total and the same 5 titles.
- `05` is my own adversarial probes against my server.

**Why "saved" and not "new" postings.** The tool searches only what the collector saved. New postings arrive by running the JS2 collector, which has the host allow-list, the request budget and the approval step. The tool server itself never goes online. This keeps the brief's rule: nothing in a tool server I write can send or change data outside my folder.

## 2. My server, evaluated as if someone else wrote it

### Declared vs actual

| It declares | What it actually does | Evidence |
|---|---|---|
| One tool, `search_postings`, `readOnlyHint: true`, `openWorldHint: false` | Reads the corpus files and nothing else. It writes no file: before and after the calls, the folder's file list and modification times are unchanged. It imports no `socket`, `urllib` or `http`. | `test_server_writes_no_files`, `test_no_network_imports` |
| `inputSchema`: `query` 1–200 characters, optional `board`, `limit` 1–20, `additionalProperties: false` | It enforces all of these. `limit: 99` → -32602. An extra `path` argument → -32602 `unknown argument(s)`. | transcripts `01`, `05` |
| "Matches a whole word or phrase, ignoring case" | Yes. `.*` is searched as plain text (0 results, so it is not a regex). `C++` works. "ML" does not match "HTML". | transcript `05`; `test_whole_word_not_substring` |
| `board` is "ats/board" | `../../etc` → -32602 `no board … in the corpus`. Boards are looked up in the loaded corpus, never used as a path. | transcript `05` |
| Searches "the job postings saved by the JS3 collection run of 2026-11-24" | True. The corpus folder is fixed in code, relative to the server file, and the folder never changes on its own. | `test_corpus_dir_is_inside_js3` |
| Speaks protocol `2025-06-18` | It also accepts `2025-03-26` and `2024-11-05`. For any other version it answers with its own. Claude Code asked for `2025-11-25` and accepted `2025-06-18`. | `test_unknown_protocol_version_gets_servers_own`; transcript `02` |

**Gaps between declared and actual:**
1. **No progress notifications.** The description doesn't promise them, but Claude Code sent a `progressToken` and got nothing back.
2. **No answer to `server/discover`.** Claude Code probes for it first, and my server answers -32601. Claude Code recovered and used `initialize`.
3. **The results are not complete.** It returns at most 20 postings per call (`count_total` says how many matched).

### What a compatible client is not entitled to

- **To treat `readOnlyHint` as a guarantee.** It is a hint the server gives about itself. A client should trust it only as far as it trusts the server, and that trust is decided in section 4, not by the hint.
- **To any file other than the frozen corpus.** That includes Priya's résumé, `state/`, my hand verdicts, or anything given as a path. The tool takes no path at all.
- **To fresh results.** A search is about 2026-11-24, not "now". Running the collector is a separate, human-approved step.
- **To any judgement of fit.** The tool says where a word appears. It does not say a posting is worth Priya's time. In transcript 02, its first MLflow hits were a "Senior Data Scientist" and a "Solutions Architect", relevant to the word and wrong for Priya.
- **To quotas or behaviour it never declared:** progress notifications, `server/discover`, roots, elicitation or tasks. Claude Code declared all of these as client capabilities, and my server uses none of them.

### My trust decision (T1)

**Trust, within its read-only scope.** Claude may call it. Re-check before adding a second tool (for example `filter_posting`) or any argument that names a file. (Decided by me, 2026-11-24.)

## 3. Another server: Claude Code's own MCP server

**Source:** Anthropic's Claude Code CLI, version 2.1.312, installed on my machine. It is started with `claude mcp serve`, and its `serverInfo` is `{"name": "claude/tengu", "version": "2.1.312"}`. I chose it because it was already installed, so I didn't download anything new to evaluate a server.

**What I did:** I ran my own scripted client against it (transcripts `03`, `04`). I listed its tools and pressed only **Read**: once on a file in this folder, and once on `/etc/shells`, a standard system file outside the project. I deliberately did **not** call Bash, Write, Edit, NotebookEdit, WebFetch, Artifact, RemoteTrigger, PublishPlugin, PushNotification or any other tool that can run commands, change files or send data.

### Declared vs actual

| It declares | What it actually does | Evidence |
|---|---|---|
| `capabilities: {"tools": {"listChanged": true}}` | It answered `tools/list` with **29 tools**. It sent no `list_changed` notification during the run. | `03`, `04` |
| 29 tools, including Bash, Write, Edit, NotebookEdit, WebFetch, WebSearch, Artifact (publishes web pages), RemoteTrigger, PublishPlugin, PushNotification, CronCreate | — (not pressed) | `03` tools/list |
| **No `annotations` on any tool**: no `readOnlyHint`, no `destructiveHint` | Under the MCP spec, a tool with no annotations must be assumed possibly destructive and open-world. Even **Read** carries no read-only hint. | `03` |
| Extra, non-standard fields on each tool (`aliases`, `searchHint`, `backgrounding`, `maxResultSizeChars`, …) | A strict client might reject these. Mine ignores them. | `03` |
| Read's description: reads "a file from the local filesystem" | Read returned `/etc/shells`, **outside the project folder, with no permission prompt and no error**. Nothing in the protocol limited it to a folder, and my client declared no `roots`. | `04` |
| JSON-RPC errors | An unknown tool got `-32603` (internal error), where `-32602` (invalid params) is what the spec says. An unknown method correctly got `-32601`. | `03`, `04` |
| stdio server lifecycle | It **did not exit** when the client closed stdin. The first run hung until I stopped it, and the second was terminated after 10 s (the note in `04`). | `03`, `04` |

### What a compatible client is not entitled to

Being able to talk to this server does not entitle a client to the user's machine.
- A client that connects gets command execution and file writes **as me**. The protocol doesn't stop that; only the client's own allow-list or the user's settings would.
- Under the spec, the client is not entitled to assume any of these tools is safe, since none is annotated.
- It is not entitled to assume Read stays inside a project. It didn't.

### My trust decision (T2)

**Don't connect it to my job-search agent.** It offers far more than a job-search agent needs: running commands, writing files, publishing. Connecting it would break my own rule that the agent must not change or send data outside its folder. (Decided by me, 2026-11-24.)

## 4. What this part does not show

- I didn't press any of Claude Code's dangerous tools. So I can't say whether `mcp serve` asks for permission before running Bash or writing a file. I only know that Read did not ask.
- I didn't test my server against a hostile client sending huge or malformed messages beyond the parse-error test, and I didn't test concurrent calls.
- Claude Code is one client. Another MCP client may negotiate differently.
