# EVAL-FACTS — JS3 step 2.3 (Chapter 8: my agent as a tool)

Facts gathered 2026-11-24 (US Eastern) for Tushar's two evaluations. This file holds facts only.
Whether to trust either server, and for what, is Tushar's decision and is not written here.
FILTER.md stays frozen at f3edf99 (git blob `aa49e255b311a028bd214ad995cbda99b0cf5f83`, unchanged).

Evidence in this folder:
- `transcript-run-20261125T040140Z-bfa84e.jsonl`: the server's log of the real session with Claude Code as the client.
- `claude-client-reply-2026-11-24.txt`: the exact command, the date, and Claude's reply, verbatim.
- `tests/test_mcp_server.py`: 14 tests, all passing (full suite results in `evidence/test-runs/js3-step2.3-full-suite.txt`).

---

## a. My server (`tools/mcp_server.py`): declared vs actual

### What it declares

`initialize` → `capabilities: {"tools": {}}`, `serverInfo: {"name": "js3-filter", "version": "0.1.0"}`.
`tools/list` → exactly one tool (`tools/mcp_server.py:63`), checked field for field by
`test_tools_list_declares_exactly_one_tool_with_the_stated_schema`:

| Field | Declared |
|---|---|
| name | `score_posting` |
| description | "Score one saved posting against FILTER.md v0.2. Read-only; uses the committed corpus evidence/runs/live-text-1; no network." |
| inputSchema | `board`: string, enum `greenhouse/stripe`, `ashby/notion`, `ashby/linear`; `posting_id`: string; both required; `additionalProperties: false` |
| annotations | none declared |

### What it actually does (from tests and the real transcript)

| Behaviour | Evidence | Observed |
|---|---|---|
| Reads (data) | `test_server_reads_only_the_corpus_filter_md_and_persona_besides_python_code`: a CPython audit hook records every `open` | Data reads are limited to `FILTER.md`, `evidence/runs/live-text-1/summary.json`, `evidence/runs/live-text-1/raw/*/attempt-1.raw`, **and `../js1-contract-and-watch/persona/cole-palmer.example.json`**. Python source files from `agent/` and the standard library are also opened, for imports. |
| Writes | `test_server_writes_only_inside_evidence_mcp`: the project tree is snapshotted before and after, and the audit hook covers the whole filesystem | The only file opened for writing is one `transcript-<run>.jsonl`, opened in `"x"` mode so it is never overwritten (`:249`). `mkdir` runs only on the log folder. No `__pycache__` is written, because `sys.dont_write_bytecode` is set before any import (`:32`). `--log-dir` outside `evidence/mcp/` exits 2 before writing anything (`test_log_dir_outside…`). |
| Network | `test_server_opens_no_socket_and_runs_no_process`: socket constructors are replaced and the audit hook watches `socket.*`, `subprocess.*`, `os.exec*`, `os.posix_spawn`, `os.fork`, `urllib.*`, `http.client.*` | Zero events during a session that ran initialize, list and two calls. A temporary mutation that opened a raw `_socket` was caught by this test, and the mutation was then removed. |
| Matches the filter | `test_valid_calls_match_agent_filter_v02_result_on_every_board` | For one posting on each board, `verdict`, `gates`, the first failing/unknown gate, `score`, `near_threshold`, `text_status`, `text_chars` and `title` equal `agent.filter.run_filter(..., mode="v0.2")`. A temporary mutation to v0.1 was caught by this test, and the mutation was then removed. |
| Tool errors | `test_unknown_id_board_or_bad_arguments_are_tool_errors_not_crashes` | An unknown id, an unknown board, an extra argument, a non-string id or a missing id each returns `isError: true` with a one-line message and no traceback. The server keeps serving afterwards. |
| Protocol errors | `test_unknown_method…`, `test_malformed_lines…`, `test_unknown_tool_name…` | Unknown method → -32601. Malformed JSON or invalid UTF-8 → -32700 with `id: null`. A JSON array (batch) → -32600. Unknown tool name → -32602. Any other exception → -32603 carrying only the exception's type name (`:234`). Notifications never get a reply (`:223`). |
| Rules guard | `test_filter_md_not_matching_the_frozen_blob_is_refused` | Each call hashes FILTER.md as a git blob. If it differs from f3edf99's blob, the call returns `isError` (`:97-110`). |
| Transcript | `test_transcript_logs_every_message…` | Every inbound line (with its raw text) and every outbound message is logged with a UTC timestamp and a direction, plus `meta` start/end records. A sentinel environment variable's name and value never appear in the log. |

**Real session with Claude Code 2.1.332 as the client** (`transcript-run-20261125T040140Z-bfa84e.jsonl`, 13 records):

| Direction | Count | Messages |
|---|---|---|
| client→server | 6 | `server/discover` (probe, protocol `2026-07-28`), `initialize` (protocol `2025-11-25`), `notifications/initialized`, `tools/list`, `tools/call` ×2 |
| server→client | 5 | -32601 to `server/discover`, initialize result (echoed `2025-11-25`), tools/list result, 2 tool results (`isError: false`) |
| meta | 2 | start; end with reason `KeyboardInterrupt` (Claude Code stopped the server with SIGINT rather than by closing stdin) |

The two calls returned ashby/notion `85947779-…` **keep**: all gates pass, G4 matched only the maximum "less than two years", score 4 (distributed systems, infrastructure, TypeScript, React). They returned greenhouse/stripe `8144196` **reject**: G4 fail on "4+ years", no score computed. Every factual claim in Claude's reply matches these tool results. The reply's closing caveat ("aren't facts about the jobs… no one has checked them") repeats the `note` field the tool returns. Claude did not reach that caveat on its own.

### Every mismatch between declared and actual

1. **Reads more than the description says.** The description names only `evidence/runs/live-text-1`. The server also reads `FILTER.md` (to hash it) and the persona file in a sibling folder, `../js1-contract-and-watch/persona/cole-palmer.example.json`. The step brief said "reads only evidence/runs/live-text-1 and FILTER.md". The persona read goes beyond that brief. It is there because `agent.filter.evaluate` needs the persona's skills and sponsorship fields to give the same result as `agent.filter`.
2. **"Read-only" describes the tool's effect on the corpus, not the process.** Every session writes a transcript file that holds every argument the client sends and every result. So the process writes on every session, including when only `initialize` runs.
3. **"against FILTER.md v0.2"**: the scoring is `agent/filter.py`'s v0.2 code path. FILTER.md is hashed, not interpreted. The blob check detects a changed FILTER.md, but it would not detect a changed `agent/filter.py`. Agreement between code and spec rests on `tests/test_filter_v02.py`, not on this server.
4. **Input handling is looser than the schema in one place.** `posting_id` is stripped of surrounding whitespace before lookup (`:165`), so `" 8144196 "` is accepted.
5. **Undeclared behaviour.** The server answers `ping` with `{}`, which is MCP base protocol but was not in the brief. It does not require `initialize` before `tools/call`: `handle` keeps no session state (`:209-236`). It echoes protocol `2025-11-25`, `2025-06-18`, `2025-03-26` or `2024-11-05`, but implements only the tools subset of any of them. There is no `structuredContent`, no `outputSchema`, and nothing from the capabilities Claude Code offered (`roots`, `elicitation`, `tasks`).
6. **No annotations.** The spec's defaults for a missing hint are `readOnlyHint: false`, `destructiveHint: true`, `idempotentHint: false`, `openWorldHint: true` (schema `2025-11-25/schema.ts:1168-1222`, fetched 2026-11-25). A client that reads only annotations therefore sees a possibly destructive, open-world tool, which is the opposite of the description.

### What a compatible client is NOT entitled to assume

- **That the description is enforced.** "Read-only" and "no network" are text in `tools/list`. Nothing in MCP verifies them. The only evidence is this repo's tests, run against this commit, on this machine. The process runs with the user's full OS permissions. Whoever can edit `tools/mcp_server.py`, `agent/`, or `.venv/` controls what `mcp-config.json` launches.
- **That results are true rather than filter output.** A verdict is what the v0.2 rules produce from text saved on 2026-11-22 (run `run-20261122T042828Z-07c6f0`). It is not a fact about the job. The posting may have changed or closed since then, and no person has checked a given result. The filter's measured agreement with hand labels is in `SCORE-REPORT.md`; nothing in a tool result reports it.
- **That `isError: false` means "correct".** It means the posting was found and the rules ran.
- **That it is safe to auto-approve calls.** In the recorded run, auto-approval came from `--allowedTools`, which Tushar's command granted, not from anything the server declared. The spec says clients MUST treat annotations as untrusted unless they come from trusted servers, and that there SHOULD always be a human in the loop with the ability to deny tool invocations (`modelcontextprotocol.io/specification/2025-11-25/server/tools`, fetched 2026-11-25).
- **That what it sends is private.** Every `posting_id` the model sends is logged verbatim to `evidence/mcp/`, a committed folder. If a model put other text into that argument, it would be logged too.
- **That `rules.mode: "v0.2"` pins the code.** It pins FILTER.md's bytes only (see mismatch 3).
- **That the server will negotiate a protocol it implements in full.** It echoes the version a client asks for when that version is on its list (see mismatch 5).

---

## b. Third-party server: MCP reference "filesystem" server

**Source.** `github.com/modelcontextprotocol/servers`, commit **`c799c8552b0f27b7a33a7b9233773da144dddcf5`**
(committed 2026-11-18, "Merge pull request #5592 … release-v2.5.0"). Package `@modelcontextprotocol/server-filesystem`
version 2.4.0 (`src/filesystem/package.json:3`). Cloned with `--depth 1` into `/tmp/mcp-servers-ref/servers`, then made read-only
(`chmod -R a-w`). It was not built, not installed and not run, and not pointed at any of Tushar's files.
All citations are `src/filesystem/<file>:<line>` at that commit and come from reading the source.
"Code reading" marks a consequence derived from the code that was not executed.

### Tools it declares (16) and what each actually does

The annotations are as declared in `server.ts`; the README's table at `README.md:385-402` matches them.

| Tool | Declared at | readOnly / idempotent / destructive / openWorld | Actual effect |
|---|---|---|---|
| `read_file` (deprecated) | `server.ts:387-403` | true / true / false / false | Reads file text. Same handler as `read_text_file` (`:359-385`). |
| `read_text_file` | `server.ts:405-427` | true / true / false / false | Reads text, optionally `head`/`tail` N lines (`:362-379`). |
| `read_media_file` | `server.ts:429-510` | true / true / false / false | Reads any file as base64. Non-image/audio files come back as an embedded resource with a `file://` URI (`:493-504`). |
| `read_multiple_files` | `server.ts:512-555` | true / true / false / false | Reads many files. A failure on one file is reported inline rather than failing the call (`:542-546`). |
| `write_file` | `server.ts:557-588` | **false / true / true** / false | Creates the file, or **overwrites it in place** (`lib.ts:653-669`, `697-706`). Not crash-atomic (`lib.ts:694-695`). |
| `append_file` | `server.ts:590-622` | false / false / **false** / false | Appends to the file, **creating it if missing** (`lib.ts:719-738`). |
| `edit_file` | `server.ts:624-661` | false / false / true / false | Replaces text. **`dryRun` defaults to false** (`server.ts:126-129`), so a call writes unless the client asks for a dry run (`lib.ts:1169-1170`). |
| `create_directory` | `server.ts:663-695` | false / true / false / false | Creates the directory and any missing parents (`lib.ts:741-743`). |
| `list_directory` | `server.ts:697-734` | true / true / false / false | Lists the entries in a directory. |
| `list_directory_with_sizes` | `server.ts:736-853` | true / true / false / false | Lists entries with sizes. A symlink pointing outside is listed with size unknown (`:774-799`). |
| `directory_tree` | `server.ts:855-944` | true / true / false / false | Recursive JSON tree, capped at 100,000 entries (`lib.ts:71`). |
| `move_file` | `server.ts:946-985` | false / false / true / false | Renames a file or directory. **Refuses if the destination exists** (`lib.ts:745-773`). Across devices it **copies, then removes the source** (`lib.ts:762-766`, `pinned-directory.ts:806-835`). |
| `copy_file` | `server.ts:987-1024` | false / true / **false** / false | Copies one regular file and never overwrites (`lib.ts:782-796`). |
| `search_files` | `server.ts:1026-1079` | true / true / false / false | Matches a glob against path names only, never content. Reports directories it could not read (`:1067-1073`). |
| `get_file_info` | `server.ts:1081-1114` | true / true / false / false | Returns stat metadata, including the `hardLinks` count (`lib.ts:628-642`). |
| `list_allowed_directories` | `server.ts:1116-1147` | true / true / false / false | Returns the allowed and read-only directory lists. |

The tools that write or move files are `write_file`, `append_file`, `edit_file`, `create_directory`, `move_file` and `copy_file`.
`move_file` can delete the source path, and `write_file` and `edit_file` replace existing content.

Beyond tools, the server also registers a **resource template `file://{+path}`** (`server.ts:1151-1158`, `file-resources.ts:155-172`),
so `resources/read` can read any allowed file. `resources/list` stays empty because the template has no list callback (`file-resources.ts:8-13`).

### How it restricts paths

- **Allowed directories from the command line** (`index.ts:47-108`). `~` is expanded and each path resolved. Both the given form and the realpath are kept (`:54-84`). Directories that are missing or not directories are dropped with a warning, and startup exits if none is usable (`:86-105`). Note: the comment at `:78-80` says a missing directory "will be created later", but the filter at `:88-99` drops it.
- **Containment check** (`path-validation.ts:109-222`). The path is normalized and resolved, and must equal an allowed directory or start with that directory plus a separator, so a sibling like `dir-evil` doesn't match (`:212-220`). Null bytes are refused (`:123-126`). On Windows, alternate data streams, device names and trailing dots/spaces are refused (`:137-153`).
- **`validatePath`** (`lib.ts:508-620`):
  - Windows drive paths are refused on POSIX (`:542-549`).
  - Relative paths are resolved against the allowed directories, falling back to the **first allowed directory** (`:210-235`), or to **`process.cwd()` when there are none** (`:214-216`).
  - The existing path is **realpath'd and must stay inside** (`:591-601`). A non-existent path is checked through its nearest existing parent (`:603-617`, `:398-490`).
- **Symlinks.**
  - A symlink whose real target is outside is refused (`lib.ts:596-599`).
  - New files are created with `O_EXCL`, so an existing symlink is never followed (`pinned-directory.ts:299-304`).
  - Overwrites use `O_NOFOLLOW` plus a device/inode identity check (`pinned-directory.ts:320-326`, `lib.ts:680-706`).
  - Directories on the path are "pinned" against swaps after validation on Linux/macOS. **On Windows that protection is absent**, by the README's own statement (`README.md:131-132`).
- **Optional narrowing.**
  - `--read-only` removes every tool not annotated `readOnlyHint: true` (`server.ts:343-354`).
  - `--read-only-dir` refuses writes into, and moves of anything containing, the marked directories, judged on the resolved path (`read-only-directories.ts:110-137`, `lib.ts:519-530`).
  - `--confine-roots` keeps client Roots inside the command-line directories (`server.ts:1209-1228`).

### What the declarations don't tell a client

The `tools/list` entries say only "Only works within allowed directories". They do not say:

1. **Who sets the allowed directories, and that they can change mid-session.** Without `--confine-roots`, a 2025-era client's Roots **replace** the command-line directories (`server.ts:1173-1176`, `README.md:68`), which can widen access beyond what the operator passed. A later Roots update can revoke or replace them again (`server.ts:1180-1183`, `1231-1252`).
2. **Hard links escape the containment check.** The checks are path-based. Writing a file inside an allowed directory that is hard-linked from elsewhere changes it at every name (`lib.ts:638-640`, `README.md:190-197`). Only `get_file_info` exposes this, as `hardLinks`.
3. **Symlinks inside the allowed area are followed to their target.** `validatePath` returns the realpath (`lib.ts:594-601`), and every write tool acts on what it returns. Code reading: `write_file` or `edit_file` on a symlink whose target is also inside overwrites the target. `move_file` with a symlink as `source` renames the target, not the link (`server.ts:965-977` → `lib.ts:745-760`). Grepping the repo found no test of moving a symlink source.
4. **Relative-path fallback** to the first allowed directory, or to the server's working directory when none is set (`lib.ts:210-235`).
5. **The annotations are hints the server itself relies on.** `--read-only` decides what to remove by trusting `readOnlyHint` (`server.ts:336-354`). Some values are judgment calls: `append_file` declares `destructiveHint: false` although it changes file content (`server.ts:601-606`), and `write_file` declares `idempotentHint: true` (`server.ts:567-572`). The spec says annotations "are not guaranteed to provide a faithful description of tool behavior" and that clients "should never make tool use decisions based on ToolAnnotations received from untrusted servers" (`schema/2025-11-25/schema.ts:1168-1179`, fetched 2026-11-25).
6. **`copy_file`'s path arguments lack the path rule** that every other path argument's description carries (`server.ts:180-185` vs `57-63`).
7. **Error text discloses absolute paths and the full allowed-directory list** to the model (`lib.ts:584-588`, `597-599`).
8. **A network listener exists.** `--transport streamable-http` serves `/mcp` on `127.0.0.1:3001` by default. The `HOST` and `PORT` environment variables can change that (`http.ts:30-51`, `index.ts:213-243`). `http.ts` adds a localhost-Origin check (`:82`, `:92`) but no authentication of its own.
9. **What actually runs is not pinned by this commit.** Dependencies are caret ranges (`package.json:36-42`), and an `npx` install fetches the published package, not this source.
10. **The resource template** gives a second read path (`resources/read`) that is not in `tools/list` (see above).

### Sources (checked 2026-11-24/25)

- `github.com/modelcontextprotocol/servers` at `c799c8552b0f27b7a33a7b9233773da144dddcf5`, `src/filesystem/` (read locally from the `/tmp` clone).
- MCP schema `schema/2025-11-25/schema.ts` lines 1168-1222 (ToolAnnotations), from `raw.githubusercontent.com/modelcontextprotocol/modelcontextprotocol/main/…`. `main` was at `2bbace557bbf2cb5d03d6f9b48905415cd7607b0` when it was fetched on 2026-11-25.
- MCP spec `modelcontextprotocol.io/specification/2025-11-25/server/tools`, fetched 2026-11-25: "clients **MUST** consider tool annotations to be untrusted unless they come from trusted servers"; "there **SHOULD** always be a human in the loop with the ability to deny tool invocations."

---

## Addendum, 2026-11-24 23:41 EST: my server's declaration after the fix

Lines 1-148 above are unchanged and describe the **pre-fix** declaration, the one the first transcript shows.
The fix follows Tushar's trust decisions in `EVALUATIONS.md`.

- **Description now:** "Score one saved posting against FILTER.md v0.2. Read-only; uses the committed corpus evidence/runs/live-text-1; no network. Also reads the fictional persona file ../js1-contract-and-watch/persona/cole-palmer.example.json. Every call's arguments and results are logged to evidence/mcp/."
- **Annotations now:** `{"readOnlyHint": true, "destructiveHint": false, "idempotentHint": true, "openWorldHint": false}`.
- **Effect on the mismatches above:** mismatch 1 (the persona read) and mismatch 6 (no annotations) are now declared. Mismatch 2 (the transcript write) is now stated in the description. Mismatches 3-5 are unchanged.
- **How the annotations read the transcript.** The hints describe the tool's effect on the corpus and on the user's files: a call changes neither. The server process still appends every message to a transcript in `evidence/mcp/`. If that log counts as "its environment" (the spec's wording), `readOnlyHint` and `idempotentHint` would be false. `destructiveHint` holds either way, because the log is append-only and opened in `"x"` mode. Per the schema, `destructiveHint` and `idempotentHint` carry meaning only when `readOnlyHint` is false.
- **Annotations are still hints.** Nothing in MCP enforces them (see line 63).
- **Second real client run** (same command, Claude Code 2.1.332): `transcript-run-20261125T044128Z-5fd246.jsonl` and `claude-client-reply-2026-11-24-postfix.txt`.
  - 6 client→server, 5 server→client, 2 meta: the same message sequence as the first run.
  - Its `tools/list` result equals the new declaration field for field, including the annotations.
  - Verdicts are unchanged: notion `85947779-…` keep, score 4; stripe `8144196` reject at G4 on "4+ years".
