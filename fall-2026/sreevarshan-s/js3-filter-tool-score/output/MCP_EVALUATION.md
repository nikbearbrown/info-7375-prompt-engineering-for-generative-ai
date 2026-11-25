# MCP EVALUATION — Job-Search Agent 3

Date: 2026-11-24

Each server is judged on four questions: what it declares, what it actually does, what a compatible client is *not* entitled to assume, and whether to trust it.

## Section 1 — My own server: job-search-agent-3 v0.1.0

Source: `js3/mcp_server.py`. Evidence: `tests/test_mcp_server.py` (17 tests) and the real run in `output/mcp_transcript.txt`.

### What it declares
- One tool, `score_posting`, with one required string parameter, `title`.
- Tool description: "Score a job posting title for relevance to an ML/data engineering job search. Returns a score 0-100 and a reason."
- JSON-RPC 2.0 over stdio, one message per line. The initialize reply gives `serverInfo` name `job-search-agent-3`, version `0.1.0`, and empty `capabilities` `{}`.

### What it actually does
- **Lookup:** it searches `output/filter_results.json` for the first posting whose title equals the given title. The match ignores case and extra whitespace but is otherwise exact; it never does substring matching.
- **Score:** it returns **100 for any passed posting and 0 for a rejected or unknown title**. No other score is possible, so the "0-100" in the description is misleading: it is a binary pass/fail. The transcript shows both cases: "Data Engineer" → not found, score 0; "Machine Learning Engineer, Radar" → Stripe 8243617, score 100.
- **Reason:** for a found title, `reason` is the filter's reason (`title_match`, `title_and_topic`, `hard_reject`, `no_match`), not an explanation of relevance.
- **Errors:**
  - -32601 for an unknown method.
  - -32602 when params aren't an object, the tool name isn't `score_posting`, or `title` isn't a string.
  - -32603 for anything else: invalid JSON, a message that isn't an object, or a missing results file. It doesn't crash.
- **Notifications:** messages without an `id` get no reply.
- **Scorer used:** this tool does **not** use the weighted scorer in `js3/scorer.py`. Its score is the pass/fail stand-in only.

### What a compatible client is not entitled to
- **Duplicate titles:** when two postings share a title, it returns the first one in file order and hides the rest. Stripe has two "Machine Learning Engineer, Radar" postings; only 8243617 is returned. File order is an implementation detail, not a promise.
- **Partial titles:** no match on partial titles. "Data Engineer" doesn't find "Senior Data Engineer - Data Platform".
- **Persistence:** none between calls. It rereads `filter_results.json` on every call, so if the file changes, so do the answers. It keeps no session or cache.
- **Graded scores:** none, despite the description.
- **Relevance:** a score of 100 says only that the title passed FILTER.md, not that the posting suits Priya.

### Trust decision
- **Suitable for:** local use in this assignment, driven by my own client on my own machine.
- **Not suitable for production:**
  - no authentication
  - no rate limiting
  - single-threaded, handling one message at a time on one stdio stream
  - input validation limited to JSON parsing and the checks on `name` and `title` above
  - a tool description that overstates what the score means

## Section 2 — External server: the reference MCP filesystem server

Source: https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem

Evidence: `README.md`, `index.ts`, `server.ts`, `lib.ts` and `path-utils.ts` from the `main` branch, read on 2026-11-24. The ends of `server.ts` and `lib.ts` were only summarised, not read in full, and several helper files it imports were not read (`path-validation.ts`, `roots-utils.ts`, `pinned-directory.ts`, `allowed-directories.ts`, `read-only-directories.ts`). Points marked *(README only)* rest on the README, not the code.

### What it declares
- **Tools:** file and directory tools over the MCP protocol: `read_text_file`, `read_media_file`, `read_multiple_files`, `write_file`, `append_file`, `edit_file`, `create_directory`, `list_directory`, `list_directory_with_sizes`, `directory_tree`, `move_file`, `copy_file`, `search_files`, `get_file_info`, `list_allowed_directories`, and a deprecated `read_file` alias.
- **Annotations:** each tool carries read-only and destructive hints. For example, `write_file`, `edit_file` and `move_file` are marked destructive, and the read and list tools are marked read-only.
- **Transport:** stdio by default, with an optional streamable HTTP transport bound to 127.0.0.1 *(README only)*.

### What it actually does
- **Restricts access to allowed directories,** given as command-line arguments at startup. It resolves symlinks and checks the real path against those directories, so a path or symlink that leads outside them is refused. The `lib.ts` error begins: "Access denied - path outside allowed directories".
- **Accepts directories from the client at runtime.** A client that supports MCP Roots can supply them, and per the README, client roots "completely replace" the startup directories, unless the server was started with `--confine-roots`, which only lets roots narrow them.
- **Waits or exits without directories.** If started with none, it waits for the client to provide roots. If the client can't, it reports "Server cannot operate: No allowed directories available." and exits.

### What a compatible client is not entitled to
- **Atomic writes:** writing to an existing file goes through that file in place rather than via a temp file and rename. A `lib.ts` comment names the trade-off as crash-atomicity: a crash mid-write can leave a partly written file.
- **File locking:** none was found in the code or the README.
- **Ordering:** no guarantee across concurrent calls. `read_multiple_files` reads files concurrently, and no serialization of concurrent `write_file` calls was found. The server does order its own roots updates, using a generation counter and a barrier.
- **Cancellation:** a timed-out call can't be cancelled and finishes in the background *(README only)*.

### Trust decision
- **Suitable for:** sandboxed local use with a narrow allowed directory.
- **Main safety boundary:** the allowed-directory restriction. A misconfigured startup path removes that protection entirely; for example, passing a home directory or `/` exposes everything under it.
- **Roots risk:** because client roots can replace the startup directories, the client's roots configuration is part of the same boundary. Starting with `--confine-roots` keeps the startup directories as the upper limit.
- **Not to rely on for:** crash-safe writes or coordinated concurrent edits.
