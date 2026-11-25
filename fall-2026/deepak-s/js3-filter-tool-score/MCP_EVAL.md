# MCP_EVAL.md: two tool servers, evaluated the same way

Job-Search Agent 3. Facts written by Claude Code (claude-opus-5-5) on 2026-11-25 from committed transcripts, code and fetched pages; each cites its file. The trust decisions are Deepak's.

Protocol: both servers were spoken to in Model Context Protocol revision 2026-07-28 (per-request `_meta`, `server/discover`, no `initialize`; `evidence/mcp/SPEC_NOTES.md`, pages in `evidence/mcp/spec-fetch/`). Our server targets 2026-07-28 because the probe recorded that Claude Code 2.1.332's first message to a stdio server is `server/discover` with protocolVersion 2026-07-28 (`evidence/mcp/probe/20261125T211913Z.jsonl`, line 2; it sent `initialize` with 2025-11-25 3 s later, line 3, when the probe did not answer), and Deepak's pre-set rule was: first message `initialize` → 2025-11-25, otherwise 2026-07-28. Phase 5a's plan named `initialize` and `notifications/initialized`; in 2026-07-28 those are removed, so the server answers `initialize` with an error that names its supported version instead.

## 1. Our server: jobwatch-js3 (`jobwatch/mcp_server.py`, written from scratch, stdlib only)

### 1.1 Declared

The `tools/list` result, quoted from the real session's transcript (`evidence/mcp/transcripts/20261125T212227026816Z.jsonl`, line 5):

```json
[{"name": "score_posting",
  "title": "Score one collected job posting",
  "description": "Runs the JS3 filter (FILTER.md v1) on one posting of the committed dataset and returns keep, reject or 'I cannot tell', the score, the matched rules with their quotes, and the reasons. Read-only; it fetches nothing.",
  "inputSchema": {"type": "object",
                  "properties": {"posting_key": {"type": "string", "description": "<system>:<slug>:<posting id>, e.g. greenhouse:stripe:8187574"}},
                  "required": ["posting_key"], "additionalProperties": false}}]
```

`server/discover` declares `supportedVersions: ["2026-07-28"]`, `capabilities: {"tools": {}}`, serverInfo `jobwatch-js3` 1.0.0, `ttlMs` 300000, `cacheScope` "public" (same transcript, line 3).

### 1.2 Actual

From the code and the tests (`tests/js3/test_js3_mcp_server.py`, which drive the server in a subprocess with `scripts/mcp_client.py`):
- Reads: only `data/` and `runs/`, through `jobwatch/tools.py` `read_file` under a `Policy` with `read_dirs=("data", "runs")` (`jobwatch/mcp_server.py`, `Server.__init__`). In practice it reads one file, the dataset named on its command line, on the first `tools/call`.
- Writes: only its own transcript, `evidence/mcp/transcripts/<UTC start>.jsonl`, through `tools.write_file` (`write_dirs=("evidence/mcp/transcripts",)`, append only to that one file name). The test `test_transcript_records_every_line_in_and_out_verbatim_and_nothing_else_is_written` checks that the server's working folder gains exactly that file.
- Opens: no network. The module imports no network or subprocess module (`test_server_module_imports_no_network_or_subprocess`; the JS2 source scan `tests/js2/test_source_scan.py` covers every jobwatch module).
- `posting_key` is never used as a path: it must match `<system>:<slug>:<id>` and is looked up in the loaded dataset; `../secret.txt`, `../../../../etc/passwd`, `greenhouse:seeded:../../secret` and an unknown key each give a tool result with `isError: true` and read nothing (`test_path_traversal_and_unknown_keys_read_nothing_outside_data`).
- Bad input: unparseable line → -32700; not a JSON-RPC 2.0 request → -32600; unknown method (including `ping`, removed in 2026-07-28) → -32601; `initialize` → -32601 with `data.supported`; missing `_meta` fields → -32602; unsupported version → -32022 with `{supported, requested}`; unknown tool → -32602; arguments not an object → -32602; a missing, non-string or extra argument → tool result with `isError: true`; a notification → no response (tests named in `tests/js3/test_js3_mcp_server.py`).
- The answer is the filter's own output for that posting, computed by `jobwatch/filter.py` at call time from the dataset; an abstention is returned as decision "I cannot tell" with its reason.

Observed in the real session (`evidence/mcp/transcripts/20261125T212227026816Z.jsonl`): `server/discover`, then `tools/list`, then two `tools/call` (greenhouse:stripe:8187574 → keep, score 13; greenhouse:stripe:8144196 → reject, score null, "known nonmatching location"), all with protocolVersion 2026-07-28 in `_meta`. Nothing else was sent.

### 1.3 What a compatible client is not entitled to

From the 2026-07-28 pages fetched (`evidence/mcp/spec-fetch/`), and this server's declaration:
- To a decision about what the user should apply to. The tool returns a filter's keyword decision; its description says what it does, not that the decision is right (the audit measured 15 filter errors on 45 rows, AUDIT.md section 2).
- To read any file by naming it: the tool takes a posting key, not a path, and nothing in the declaration offers file access.
- To trust the declaration itself: the 2026-07-28 overview says descriptions of tool behavior "should be considered untrusted, unless obtained from a trusted server" (`evidence/mcp/spec-fetch/20261125T182546Z/11-2026-07-28-overview-md.body`, lines 112-116), and `serverInfo` is self-reported and "SHOULD NOT" drive security decisions (`12-2026-07-28-server-discover-md.body`, lines 103-108).
- To cache results beyond the hints: `ttlMs` 300000 on `server/discover` and `tools/list` only; `tools/call` results carry no caching hint.
- To any state across calls: the revision is stateless; each request carries its own version and capabilities.

### 1.4 Observed client behavior (Claude Code 2.1.332)

From `evidence/mcp/client-session/` (command, stdout, exit code) and the server transcript:
- Registration: `claude mcp add -s project jobwatch-js3 -- .venv/bin/python -m jobwatch mcp-server --dataset data/postings-20261125T200226Z.jsonl` wrote `.mcp.json` in this folder (shown in `evidence/mcp/client-session/mcp.json.as-registered`). The server was started with this folder as its working directory.
- Session: `claude -p --mcp-config .mcp.json --strict-mcp-config --allowedTools mcp__jobwatch-js3__score_posting --permission-mode dontAsk --no-session-persistence --output-format json "<prompt>"`, exit 0; model reported `claude-opus-5-5`; 7 turns (`claude_stdout.json`).
- On the wire: `server/discover` first (id "server-discover-probe-1"), then `tools/list`, then one `tools/call` per posting. Its clientCapabilities declared `roots`, `elicitation` and the tasks extension (transcript line 2).
- Off the wire: the session was not in safe mode, so it loaded this folder's CLAUDE.md. Its reply says it searched `labels/heldout.csv` for the two posting keys ("0 matches") and read the uncommitted `audit/audit-v1.csv` before answering (`claude_stdout.json`, field `result`). `--allowedTools` and `--permission-mode dontAsk` did not stop its read-only built-in tools. The held-out labels had been committed earlier (8625eea); no rule, weight or threshold was chosen from this read, and nothing was written.
- Its reply quoted both tool results correctly (decision, score, rules, quotes and offsets match the transcript's `structuredContent`).

### 1.5 Trust decision

I trust our server for local, read-only scoring of this dataset. It declares one tool, score_posting; the code and transcript show it reads only through tools.read_file, opens no network, and writes only its own transcript. I do not trust a compatible client to stay inside that tool: a client is not entitled to any file the server did not offer, yet the Claude Code client read the sealed labels/heldout.csv and the uncommitted audit sheet with its own file tools. That read changed nothing here, but it shows that isolation has to come from the client's sandbox and permissions, not from the protocol.

## 2. The other server: @modelcontextprotocol/server-filesystem 2.3.0 (official reference server)

Source: github.com/modelcontextprotocol/servers, `src/filesystem`, read at commit 5c6686a8c35864aa0675f63ee956aae87ea69ea3 (inferred as the 2.3.0 source; npm stores no gitHead; the evidence for the inference is in `evidence/mcp/other-server/install.md`). Install, sandbox and run are recorded in `evidence/mcp/other-server/install.md` and `20261125T212437Z-run.json`. The npm install and the source download were development actions by Claude Code, outside the agent's allow-list.

### 2.1 Declared

`server/discover` (`evidence/mcp/other-server/20261125T212437Z-transcript.jsonl`): supportedVersions ["2026-07-28"], capabilities `tools` and `resources` (both `listChanged: true`), serverInfo "secure-filesystem-server", `ttlMs` 0, `cacheScope` "private". `tools/list` declared 16 tools; by their `readOnlyHint` and `destructiveHint` annotations (same transcript):
- read-only (readOnlyHint true): read_file, read_text_file, read_media_file, read_multiple_files, list_directory, list_directory_with_sizes, directory_tree, search_files, get_file_info, list_allowed_directories;
- writing (readOnlyHint false): write_file, edit_file, move_file (destructiveHint true); append_file, create_directory, copy_file (destructiveHint false).

### 2.2 Actual

From the source at 5c6686a8 (`src/filesystem/`, 4967 lines of TypeScript, tests excluded) and the run:
- Reads and writes: files under the allowed directories given on the command line; every tool validates its path with `validatePath` (`server.ts`), which resolves symlinks with `realpath` and denies a target outside the allowed directories ("Access denied - symlink target outside allowed directories", `lib.ts` around line 402). Allowed directories given as symlinks are stored both as given and resolved (`index.ts` lines 44-62); the run shows both forms, `/tmp/...` and `/private/tmp/...` (transcript, `list_allowed_directories` result).
- Writes: 6 of its 16 tools change the filesystem. `--read-only` withholds every tool whose registration does not declare `readOnlyHint: true` (`server.ts` lines 336-356); the run did not use `--read-only`, so the writing tools were offered.
- Roots: on a 2025-era connection a client's Roots can replace the command-line directories after initialize, unless `--confine-roots` is given (`server.ts` lines 248-286, `index.ts` line 109); a 2026-07-28 connection has no roots/list, so it is limited to the command line (`server.ts` lines 218-224). The run was 2026-07-28.
- Network and environment: the filesystem source imports no http, https, net or child_process module and reads no environment variable (grep of `src/filesystem/*.ts`, tests excluded). It depends on `@modelcontextprotocol/server` 2.4.0, which was not read.
- Bad input: not exercised in this run (one harmless call only).
- The one call made, `list_allowed_directories`, returned the sandbox directory in both forms, with no error; the server exited 0 when stdin closed (`20261125T212437Z-run.json`).

### 2.3 What a compatible client is not entitled to

- To assume the server is read-only: it declares writing and destructive tools unless started with `--read-only`.
- To widen its access: on 2026-07-28 the allowed directories come only from the command line; on 2025-era connections, Roots can change them unless `--confine-roots`.
- To trust the annotations as enforcement: `readOnlyHint` is a declaration; the 2026-07-28 overview says annotations are untrusted unless the server is trusted (`11-2026-07-28-overview-md.body`, lines 112-116). In this server the hint also drives `--read-only`.
- To cache: it sends `ttlMs` 0 and `cacheScope` "private".

### 2.4 Observed client behavior

Our scripted client (`scripts/run_other_server.py`) probed with `server/discover`, got a result, and stayed on 2026-07-28; then `tools/list` and `tools/call list_allowed_directories` (transcript). No other request was sent.

### 2.5 Trust decision

I would run @modelcontextprotocol/server-filesystem 2.3.0 only in a throwaway sandbox with one allowed directory and nothing secret in reach, as I did. It lists 16 tools, including ones that write, its behavior depends entirely on the allowed-directory setting, and its source commit is inferred rather than recorded by npm, so I have not verified that the code I read is the code that ran.
