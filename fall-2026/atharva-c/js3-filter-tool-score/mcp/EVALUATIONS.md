# MCP server evaluations

DRAFT (Claude, Nov 24, 2026), to be checked and rewritten by me.

The same questions are asked of both servers:

1. What can it read, and what can it change?
2. How is access limited, and does it hold?
3. Do the tools tell a client what they do, including what they cannot do?
4. How are errors reported?
5. Is there a record of what was called?

## 1. My server: `js3-job-filter` (`agent/mcp_server.py`, commit `3ee665a`)

**How I evaluated it:** I ran it, which was more than reading the code.

- `tests/test_mcp_server.py` has 12 tests that pass. They run over stdio against the real server.
- `evidence/mcp/scripted-transcript.jsonl` is a scripted raw-protocol session.
- `evidence/mcp/claude-code-transcript.md` is one real Claude Code session, run Nov 24, 06:03 UTC.
- A probe on Nov 24 sent extra arguments, an unknown board, and 50 repeated calls. Its call log is in `out/`, which is git-ignored.

| Question | Finding | Evidence |
|---|---|---|
| Reads / changes | It has 4 tools, and all of them read the saved Nov 23 run. None changes anything: there is no network, no subprocess, and no write except its own call log. | Source; `test_tools_list_is_read_only` |
| Access limits | The data is fixed at startup. The call log is the only file it writes, and the server refuses to start if the log path is outside `out/`. | `test_log_must_stay_in_folder` (`/etc/js3.log` is refused) |
| Unknown action | `apply_to_job` gets JSON-RPC `-32602 unknown tool`. There is nothing to apply with. | Scripted transcript, id 7 |
| Errors | A bad uid or a bad `limit` comes back as `isError: true` and the server keeps running. Malformed JSON gets `-32700`, and an unknown method gets `-32601`. | Tests; scripted transcript, id 6 |
| Logging | Every call goes to JSONL with a timestamp, the tool, its arguments, an error flag and the time taken. A one-line summary goes to stderr. | `evidence/mcp/claude-code-server-log.jsonl` (13 rows for the real session) |
| Speed | 50 `judge_posting` calls took 26 ms in total. | Probe |

**What is wrong with it** (found by running it, not by reading it):

1. **The schema promises checks the server does not make.** Each tool says `additionalProperties: false`, and `board` is an enum, but the server checks neither.
   - `get_posting` with an extra `"delete": true` succeeded without a word about the unknown argument.
   - `search_postings` with `board: "lever"` returned `total: 0` instead of an error. That is the "no matches on X" answer that FILTER.md §3 forbids: "lever" is not a board here, so the honest answer is "I did not search that".
2. **Search is a substring match.**
   - In the real session, "Software Engineer I" matched 31 titles: the 8 SWE I postings, 22 SWE II, and 1 intern posting.
   - The client had to filter these itself ("I left those out").
   - It also miscounted them: its answer says "23 Software Engineer II postings", but a recount of the same 31 titles by script on Nov 24 gives 22 SWE II, 8 SWE I and 1 intern. A client summarizing a long result list is its own source of error.
   - With the default limit of 10, a client that trusts the first page could miss SWE I roles.
3. **`judge_posting` returns rule codes without their meaning.**
   - It returns `gates: ["G3"]` and `rules: {"R1": 0.5, …}`, but nothing says what G3 or R1 checks.
   - The real client wrote: the tool "only gives the gate's name, not what it checks."
4. **The data is a snapshot, and only one tool description says so.**
   - `search_postings` says "saved Nov 23, 2026 run".
   - `get_posting` and `judge_posting` don't, so a client could present a posting as currently open.
5. **The full text is returned twice.** Each result carries the text once in `content` as a JSON string and once in `structuredContent`. That doubles the tokens a client reads: `get_posting` is about 5,100 characters of text, sent twice.

## 2. Another server: the official Filesystem server (`@modelcontextprotocol/server-filesystem`)

**How I evaluated it:** by reading its README and source on GitHub (`modelcontextprotocol/servers`, `src/filesystem`, package version 2.4.0, read Nov 24, 2026). I did **not** install or run it, because that would mean downloading and executing code I did not write.
- Two caveats on the reading. Several files were only partly read: the tails of `lib.ts` and `server.ts`, plus some helper modules that were not read at all. The README's install section was also only summarized.
- Points that rest on those partial reads are marked *(partly read)*.

| Question | Finding |
|---|---|
| Reads / changes | It has 16 tools. 10 read, and 6 change files: `write_file` (overwrites), `append_file`, `edit_file`, `create_directory`, `move_file` (removes the source), and `copy_file` (which refuses to overwrite). |
| Access limits | Allowed directories come from command-line arguments. A client's MCP Roots replace them unless `--confine-roots` is set. Paths are resolved and normalized, then checked as a prefix on a separator boundary. Symlinks are resolved with `realpath`, and the target must also be inside. Null bytes are rejected, as are some Windows-only tricks (alternate data streams, device names). `--read-only` drops every tool whose `readOnlyHint` is not `true`. |
| Tool annotations | Every tool has them. The read tools have `readOnlyHint: true`, and `write_file`, `edit_file` and `move_file` have `destructiveHint: true`. `openWorldHint` is false throughout *(partly read for two tools)*. |
| Errors | The handlers throw errors with clear messages ("Access denied - path outside allowed directories"). I could not confirm from the reading whether the SDK turns these into `isError: true` results or protocol errors. `read_multiple_files` reports each failed file inline and carries on. |
| Logging | It logs to stderr: startup, allowed directories, read-only notices and changes to Roots. I found **no per-call log** in the parts I read *(partly read)*. |
| Build | TypeScript on Node ≥ 24, using the official SDK packages (`@modelcontextprotocol/server`, `@modelcontextprotocol/node`) with `zod` schemas. Transport is stdio, or streamable HTTP when that option is passed. |

**Compared with mine:**

- **It has to defend what mine avoids.** Its write tools are why it needs path checks, symlink checks and a read-only mode. Mine has no write tool, so the only path it has to guard is its log. "Cannot change anything" is easier to show than "can only change what it should".
- **It validates input and mine does not.** Its tools declare `zod` schemas through the SDK, so I'd expect it to reject an unknown argument before the tool runs (inferred from the SDK, not tested). Mine writes the same kind of schema by hand and then ignores it. This is the cost of writing the protocol from scratch: the schema is only documentation unless I check it myself.
- **Mine keeps a record and it does not.** Mine logs every call with its arguments. The Filesystem server's stderr messages cover setup but, in the code I read, not each call. For an agent that should never act without a trace, mine does better here.
- **Its annotations do work and mine are only labels.** Its `readOnlyHint` drives `--read-only`. Mine sets the same hints on every tool, but nothing in my server reads them.

## Changes this suggests for my server (not made yet)

1. Enforce the input schemas. Reject unknown arguments, and reject a board that is not one of the three, with an "I did not search that board" error.
2. Add `match: "word"` to search (a whole-word or prefix match), or say in the description that the match is a substring.
3. Add a one-line meaning for each gate and rule to `judge_posting` results, taken from FILTER.md.
4. Put "saved run of Nov 23, 2026; not live" in every tool description.
5. Return the text once: keep `structuredContent` and make `content` a short summary.
