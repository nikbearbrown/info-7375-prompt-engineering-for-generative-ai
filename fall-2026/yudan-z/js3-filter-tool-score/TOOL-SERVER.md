# TOOL-SERVER — my MCP server, and one I did not write

## Executive summary

`mcp/server.py` is an MCP tool server written from scratch. It uses the Python standard library and no MCP SDK. It serves two read-only tools over stdio: `search_postings` and `score_posting`.

On 2026-11-25 at 20:28 EST, Claude Code (claude-opus-5-5) connected to it and made four tool calls. Both directions are logged in `mcp/logs/` and shown in `mcp/session/TRANSCRIPT.md`. The transcript file is named by its UTC date (`transcript-2026-11-26.jsonl`); the session ran on the evening of 2026-11-25 EST, and every timestamp inside carries `+00:00`.

My trust decision:
- **My server:** trust it for this folder.
- **The official filesystem server:** trust it only with `--read-only` and one allowed directory. Its default configuration exposes write tools, which this assignment's rules forbid.

## 1. My server: `js3-postings`

### Declared vs actual

| Declared (`initialize`, `tools/list`) | Actual, and how I know |
|---|---|
| protocol `2025-06-18`, capability `tools` only | **Actual:** Claude Code first sent `server/discover` (protocol 2026-07-28). The server answered `-32601 method not found`, and the client fell back to `initialize` with protocol `2025-11-25`. The server replied with its own `2025-06-18`, and the session worked (TRANSCRIPT §1). I did not plan for the newer handshake; the fallback is the client's doing, not my server's. |
| two tools, both `readOnlyHint: true`, `openWorldHint: false` | **Mostly true.** Neither tool changes `data/`, `filter/` or anything outside the folder (tested by `test_source_has_no_network_process_or_delete_calls`). But the **server** appends every message to `mcp/logs/transcript-<UTC date>.jsonl`. So "read-only" is true of the tools' effect on the data, and **false** of the server as a whole, which writes its own log. A client is not told this. |
| `search_postings`: "words that must all appear in the title" | **True, but by substring, each word separately.** "new" would also match "renewal", and "grad" would match "graduate". This is wrong version W1, which my filter tests forbid, here in my own tool. It did not change this session: I checked, and all 49 matches contain "new grad" as a phrase. Not fixed. |
| `limit` 1–20 | enforced (`test_limit_is_bounded`) |
| `version` names a filter file | Enforced by the pattern `^v[0-9][a-z0-9]{0,3}$`. A path such as `../../persona/resume` is refused (`test_path_outside_filter_folder_is_refused`). |
| `score_posting` returns the claims with evidence | **True.** In the session, Claude's three tables match the tool results line for line. Claude added one sentence the tool never returned ("The tool gave no reasons for being unable to decide"); it is accurate, but it is Claude's wording, not the tool's. |

### What a client is not entitled to

- **The persona file, the label sheets, or any path the client names.** No tool takes a path. `version` is a short pattern, and `key` is a dictionary lookup, never a file name.
- **Full posting text.** Only the title, location, URL and evidence snippets of at most 220 characters are returned.
- **The network.** The server makes no requests. Its data is a snapshot from 2026-11-09/10, and a client must not read a result as a statement about today's job board.
- **A decision to apply.** The tool returns `cannot tell` for all 138 postings that reach Mira under v4. A client is not entitled to turn that into "eligible".

### Trust decision

I trust it for this folder. It is small enough to read in full (160 lines), and it has 7 tests. In the session, Claude was limited to exactly these two tools (`--strict-mcp-config`, `--allowedTools`).

What I would fix before anyone else used it:
- declare the log file in the server instructions;
- make the search match whole words.

## 2. Another server: the official `filesystem` server

**What I evaluated:**
- the package `@modelcontextprotocol/server-filesystem` v2.4.0;
- at commit `a13c39e647d8c553501ffe4d3f5d9db9dcc534f7` (2026-11-18) of github.com/modelcontextprotocol/servers, `src/filesystem/`;
- specifically `server.ts`, `lib.ts`, `index.ts`, `path-validation.ts` and `README.md`, read on 2026-11-25.

**I did not install or run it.** Everything below comes from reading the source. Nothing here was observed at runtime.

### Declared vs actual (from the source)

| Declared (README) | What the code does |
|---|---|
| 16 tools; 10 annotated `readOnlyHint: true`, 6 write tools (`write_file`, `edit_file`, `move_file`, `append_file`, `create_directory`, `copy_file`) | Each `server.registerTool(...)` in `server.ts` (lines 387–1140) carries those annotations. The two lists match. |
| `--read-only` serves only the read tools, "whatever the client is configured to allow" | `server.ts` 343–353: in read-only mode every tool is registered and then **removed** unless `annotations.readOnlyHint === true`. This fails closed: a new tool without the hint is withheld. |
| access only inside allowed directories, with symlinks resolved | `lib.ts` 405–490: the path is resolved with `realpath`, symlinks are followed step by step, and the result is checked against the allowed directories. A broken symlink is refused by name. |
| a 2025-era client's **Roots replace** the command-line directories | README line 68. `--confine-roots` (lines 72–84) narrows them instead. **Without that flag, a client can widen what the server may touch.** |
| `openWorldHint: false` on every tool | No network code in the files I read. **Not checked:** `http.ts`, the Streamable HTTP transport, which I did not open. |

### What a client is not entitled to

- **Trusting the hints on their own.** Annotations are claims the server makes about itself. Here the code backs them, but a client cannot know that without reading the code.
- **Assuming read-only.** By default, all six write tools are listed. `--read-only` is the operator's choice, made on the command line, not the client's.
- **Choosing its own scope.** Unless the operator passes `--confine-roots`, a 2025-era client's Roots replace the allowed directories. A careful operator should not let the client decide what it can reach.

### Trust decision

**Not with its default arguments.** This assignment says a tool server must not expose anything that can change data outside my folder. The default listing includes `write_file` and `move_file`.

**Yes, with** `--read-only --confine-roots "<this folder>/data"`:
- read-only enforcement is applied at registration and fails closed;
- path checks resolve symlinks;
- one directory and confined roots leave the client no way to widen its scope.

This decision rests on reading the source, **not on running it**. Before using it, I would run it once with a symlink pointing outside the directory and confirm that it refuses.
