# Evaluation: the reference Filesystem MCP server

**Drafted by Claude Code on 2026-11-25. For Aravind to edit; the trust decision is Aravind's.**

**Source:** `modelcontextprotocol/servers`, `src/filesystem`, npm `@modelcontextprotocol/server-filesystem` v2.4.0.
- Read at commit `c799c8552b0f27b7a33a7b9233773da144dddcf5` (2026-11-18), shallow-cloned into the
  session scratchpad on 2026-11-25 and **read only, never run**.
- About 5,900 lines of TypeScript.
- Dependencies: `@modelcontextprotocol/server` ^2.3.1, `@modelcontextprotocol/node` ^2.1.1, `diff`,
  `minimatch`, `zod`.

**Marks:**
- **[V]** verified by reading the code or the comment at the cited place
- **[R]** taken from its README, not traced in the code
- **[I]** inferred

## Declared vs actual

| It declares | What the source shows | Mark |
|---|---|---|
| 16 tools. Read: `read_file`, `read_text_file`, `read_media_file`, `read_multiple_files`, `list_directory`, `list_directory_with_sizes`, `directory_tree`, `search_files`, `get_file_info`, `list_allowed_directories`. Write: `write_file`, `append_file`, `edit_file`, `create_directory`, `move_file`, `copy_file`. | All 16 are registered in `server.ts` (`server.registerTool`, lines 387–1117). | [V] |
| Annotations: `write_file`, `edit_file`, `move_file` are `destructiveHint: true`; `append_file`, `create_directory`, `copy_file` are `destructiveHint: false`; all are `openWorldHint: false`. | As declared. `append_file` changes a file but is marked non-destructive: true in the narrow sense (no existing content is removed), but it is still a write. | [V] annotations; [I] judgment |
| "may touch only its allowed directories" | Every path goes through `validatePath`. It realpaths the allowed directory and resolves symlinks segment by segment, refusing a symlink whose target leaves the allowed directories. For a path that doesn't exist yet, it resolves the nearest existing parent. A dangling symlink is named as such. (`lib.ts` ~405–475) | [V] the check sites and their comments; the full logic was not traced or tested |
| `--read-only` serves only read tools, "whatever the client is configured to allow" | When `readOnly` is set, `registerTool` is wrapped so that any tool without `readOnlyHint: true` is removed before a client connects. Write tools are then absent from `tools/list`, and calling one gives "unknown tool". (`server.ts` ~340–352) | [V] |
| `--read-only-dir` refuses writes into a given directory, by resolved path | [R] README; not traced in `read-only-directories.ts`. | [R] |
| **Roots (2025-era clients): "Roots notified by Client to Server, completely replace any server-side Allowed directories"** unless started with `--confine-roots` | `ServerOptions`: "On a 2025-era connection the client's Roots, when it supports them, replace the command-line directories after initialize." (`server.ts` ~229). There is a `replacedCommandLine` flag (~1199). | [V] |
| Streamable HTTP transport (`--transport streamable-http`) | Binds `127.0.0.1:3001` by default. The `HOST` environment variable can widen it. Browser requests are allowed only from a localhost Origin. (`http.ts` 13–44) | [V] |
| Writes | Not crash-atomic, by design: "a crash mid-write leaves a partly written file" (`lib.ts` ~694, a trade-off for Windows `EPERM`). `move_file` refuses to overwrite an existing destination (~750). | [V] comments |

## What a compatible client is not entitled to, and what it gets anyway

- **The boundary is the server's, but a 2025-era client can move it.** A client that supports Roots
  replaces the allowed directories unless the server was started with `--confine-roots`. This is
  the most important finding.
  - **Connection to my own transcript:** in `transcripts/2026-11-26T003743686Z-69681.jsonl`, Claude
    Code 2.1.323 declared `roots: {listChanged: true}` in `initialize` and requested 2025-11-25, a
    2025-era version. Against this filesystem server, that client's workspace roots would replace
    whatever directories I passed on the command line. [I] (from the code and README; not run)
- **Annotations are not permission.** A client may auto-approve "read-only" tools. Here
  `readOnlyHint` is enforced server-side only in `--read-only` mode. Without it, write tools are
  listed, and only the client's own approval stands between the model and `write_file`.
- **Not a sandbox.** It runs with the user's OS permissions. Its path checks protect only what's
  outside the allowed directories, which may be replaced by Roots. The README itself recommends
  OS-level read-only permissions or a Docker `ro` mount "for defence in depth". [R]
- **No integrity guarantee on writes** (non-atomic) [V]. **No confidentiality inside the allowed
  directories:** any file there, including `.env` and keys, can be read by `read_file`. [I]

## Not checked

- The full `validatePath` logic, Windows path handling, `search_files` / `minimatch` behaviour on
  hostile patterns, and resource limits on `directory_tree` and `read_multiple_files`.
- The `@modelcontextprotocol/server` SDK it depends on: not read.
- Its tests (`__tests__/`): not run. The server itself was never started.

## Trust decision (draft)

- **Would use:** only with `--read-only` **and** `--confine-roots`, with explicit command-line
  directories that hold no secrets, preferably in Docker with a read-only mount.
- **Would not use:** in its default configuration with Claude Code, because Claude Code advertises
  Roots and those would replace the boundary.
- **Never** with `HOST` widened beyond loopback.
- **Compared with my server:** this one is far more capable and far better engineered for hostile
  paths, but its default trust boundary can be moved by the client. Mine has almost no capability,
  and its boundary is fixed in code.
