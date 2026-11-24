# MCP server evaluations

Both servers were evaluated against the same five questions:

1. What can it read, and what can it change?
2. How is access limited, and does it hold?
3. Do the tools tell a client what they do, including what they cannot do?
4. How are errors reported?
5. Is there a record of what was called?

---

## 1. My server: `js3-job-filter` (`agent/mcp_server.py`, commit `3ee665a`)

**How I evaluated it:** I tested the server by running it rather than relying on code inspection alone:
- `tests/test_mcp_server.py` runs 12 passing tests against the live server over stdio.
- `evidence/mcp/scripted-transcript.jsonl` captures a scripted raw-protocol session (`tests/mcp_scripted_client.py`).
- `evidence/mcp/claude-code-transcript.md` records a live Claude Code session run on Nov 24 at `06:03 UTC`.
- An adversarial probe on Nov 24 sent undeclared arguments, an unknown board name, and 50 repeated tool calls (its call log is saved in git-ignored `out/`).

| Question | Finding | Evidence |
| :--- | :--- | :--- |
| **Reads / changes** | Exposes 4 read-only tools over the saved Nov 23 collection. It makes no network calls, spawns no subprocesses, and writes nothing except its own call log. | Source; `test_tools_list_is_read_only` |
| **Access limits** | The dataset is fixed at startup. The call log is the only file written, and the server refuses to start if the log path points outside `out/`. | `test_log_must_stay_in_folder` (`/etc/js3.log` refused) |
| **Unknown action** | Calling an undeclared tool (`apply_to_job`) returns JSON-RPC `-32602` (unknown tool); there is no write or apply capability. | Scripted transcript, id `7` |
| **Errors** | A bad `uid` or invalid `limit` returns `isError: true` while keeping the server alive. Malformed JSON returns `-32700`, and an unknown method returns `-32601`. | Tests; scripted transcript, id `6` |
| **Logging** | Every call is appended to JSONL with timestamp, tool name, arguments, error flag, and elapsed time, plus a one-line summary on `stderr`. | `evidence/mcp/claude-code-server-log.jsonl` (13 rows for the live session) |
| **Speed** | 50 sequential `judge_posting` calls completed in 26 ms total. | Nov 24 probe |

### What is wrong with it (found by running it, not by reading it)

1. **Declared schemas were not enforced at runtime (fixed in `e273c8e`):** Every tool declared `additionalProperties: false` and an enum for `board`, yet the server checked neither.
   - `get_posting` accepted an extra `"delete": true` argument without complaint.
   - `search_postings` with `board: "lever"` returned `total: 0` instead of an error, producing the exact `"no matches on X"` response forbidden by `FILTER.md` §3 (`lever` was never searched, so the honest answer is `"I did not search that"`).
2. **Search uses plain substring matching:**
   - In the live Claude Code session, querying `"Software Engineer I"` matched 31 titles: the 8 `Software Engineer I` postings, 22 `Software Engineer II` postings, and 1 intern posting.
   - The client had to filter out the non-SWE-I roles itself (`"I left those out"`) and miscounted them in its final summary (`"23 Software Engineer II postings"` vs. 22 confirmed by a Nov 24 script recount), showing that a client summarizing a long result list becomes its own source of error.
   - With the default page limit of 10, a client that trusts the first page alone can miss genuine `Software Engineer I` matches.
3. **`judge_posting` returns rule codes without explanations:**
   - The tool outputs `gates: ["G3"]` and `rules: {"R1": 0.5, …}` without stating what each code checks, prompting the live client to note that the tool `"only gives the gate's name, not what it checks."`
4. **Only one tool description states that the dataset is a static snapshot:**
   - `search_postings` mentions the `"saved Nov 23, 2026 run"`, whereas `get_posting` and `judge_posting` omit that caveat, risking a client presenting archived listings as live openings.
5. **Full posting text is duplicated in every response:**
   - Each tool result includes the full text once inside `content` as a JSON string and a second time inside `structuredContent`. For `get_posting`, that sends roughly 5,100 characters of posting body twice and doubles client token consumption.

---

## 2. Another server: the official Filesystem server (`@modelcontextprotocol/server-filesystem`)

**How I evaluated it:** By reading its README and TypeScript source on GitHub (`modelcontextprotocol/servers`, `src/filesystem`, package version `2.4.0`, reviewed Nov 24, 2026). I did not install or execute it locally, since doing so would require downloading and running third-party code I did not write.
- **Reading caveats:** Several files were only partially inspected—specifically the tails of `lib.ts` and `server.ts`, plus several helper modules—and the README installation section was only summarized. Points relying on incomplete sections are marked `(partly read)`.

| Question | Finding | Evidence |
| :--- | :--- | :--- |
| **Reads / changes** | Exposes 16 tools: 10 read-only tools and 6 file-mutating tools (`write_file` overwrites, `append_file`, `edit_file`, `create_directory`, `move_file` removes the source, and `copy_file` refuses to overwrite). | GitHub source (`src/filesystem`) |
| **Access limits** | Allowed directories are passed via CLI flags, though a client's MCP Roots replace them unless `--confine-roots` is set. Paths are normalized and prefix-checked on separator boundaries; symlinks are resolved via `realpath` and re-checked; null bytes and Windows device/ADS paths are rejected; and `--read-only` drops any tool without `readOnlyHint: true`. | GitHub source (`lib.ts`, `server.ts`) |
| **Tool annotations** | Every tool declares annotations: read tools set `readOnlyHint: true`, destructive mutators (`write_file`, `edit_file`, `move_file`) set `destructiveHint: true`, and `openWorldHint` is `false` across the server `(partly read for two tools)`. | GitHub source `(partly read)` |
| **Errors** | Handlers throw descriptive error messages (such as `"Access denied - path outside allowed directories"`), though I did not verify from the source read whether the SDK wraps those exceptions into `isError: true` tool results or protocol-level errors. `read_multiple_files` reports per-file errors inline and continues. | GitHub source `(partly read)` |
| **Logging** | Logs startup configuration, allowed directories, read-only notices, and Roots updates to `stderr`, with no per-call audit log visible in the files I inspected `(partly read)`. | GitHub source `(partly read)` |
| **Build** | TypeScript on Node ≥ 24 built on `@modelcontextprotocol/server`, `@modelcontextprotocol/node`, and `zod` schemas, supporting stdio and streamable HTTP transports. | README & `package.json` |

### Comparison with my server

- **Attack surface vs. read-only design:** Because the Filesystem server mutates files on disk, it requires path normalization, symlink traversal checks, Roots confinement, and a `--read-only` flag. Because `js3-job-filter` has zero write tools, the only filesystem path it needs to guard is its own log file—proving a server cannot modify anything is far simpler than proving it only modifies what it should.
- **Schema enforcement:** The Filesystem server declares `zod` schemas through the official MCP SDK, which validates incoming arguments before handler execution (inferred from SDK usage, not executed). Writing JSON-RPC from scratch meant my JSON Schema definitions acted purely as documentation until I wrote explicit validation code.
- **Audit trail:** My server records every tool call, its arguments, its error status, and its latency to a JSONL log. The Filesystem server logs lifecycle and directory changes to `stderr` but showed no per-call trace in the source I read, making `js3-job-filter` stronger on call traceability.
- **Executable vs. passive annotations:** In the Filesystem server, `readOnlyHint` directly controls behavior via `--read-only`. In my server, tool annotations are static metadata that nothing on the server inspects.

---

## 3. Changes suggested for my server

1. **Enforce input schemas at runtime (completed in `e273c8e`, Nov 24):** Incoming arguments are now validated against each tool's declared `inputSchema`. Undeclared keys, wrong types (including boolean `true` passed as an integer `limit`), and unknown board names return tool errors. Passing an unqueried board now returns: `"I did not search board 'lever'. This run searched only: robinhood, affirm, wealthfront."` Verified with 3 new tests that failed prior to the fix.
2. **Add whole-word or prefix matching (`match: "word"`) to `search_postings`**, or state explicitly in its description that search performs substring matching.
3. **Include a one-line explanation for each gate and scoring rule** in `judge_posting` output, pulled directly from `FILTER.md`.
4. **State `"saved run of Nov 23, 2026; not live"` in every tool description**, not just `search_postings`.
5. **Eliminate duplicate payload text** by keeping the full posting object in `structuredContent` and returning a concise summary string in `content`.
