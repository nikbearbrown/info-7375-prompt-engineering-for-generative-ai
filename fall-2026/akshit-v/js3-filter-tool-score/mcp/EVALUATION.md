# Two tool servers, evaluated as if someone else wrote them

> Facts below come from the saved transcripts and the source files they name. Claude Code drafted this file from them. The two **trust decisions** are mine, and are marked where they appear.

Both servers were driven two ways:
- by my **probe client**, `scripts/mcp_probe.py`, which sends a scripted list of messages and records every line in both directions;
- by a **real client**, Claude Code 2.1.316 (`claude -p`) with no built-in tools, `--strict-mcp-config`, and permission for named tools only.

| Transcript | What it is |
|---|---|
| `mcp/transcripts/js3_filter_probe_client.jsonl` | my server **1.0.0**, 18 scripted messages, client side |
| `out/mcp/transcripts/20261125T024203Z_probe.jsonl` | the same session, recorded by the server |
| `out/mcp/transcripts/20261125T024246Z_claude_code_client_1.jsonl` + `mcp/transcripts/claude_code_client_1_claude_stream.jsonl` | Claude Code as the client of my server 1.0.0, server side + Claude's event stream |
| `mcp/transcripts/js3_filter_probe_client_v1.0.1.jsonl`, `mcp/transcripts/claude_code_client_2_v1.0.1_claude_stream.jsonl` | the same probe and a second Claude Code session, after the 1.0.1 fix |
| `mcp/transcripts/fs_default.jsonl`, `fs_read_only.jsonl`, `fs_roots.jsonl`, `fs_roots_confined.jsonl`, `fs_modern_era.jsonl` | the filesystem server under five setups (each with its server stderr beside it) |
| `mcp/transcripts/fs_claude_code_default_claude_stream.jsonl`, `fs_claude_code_confined_claude_stream.jsonl` | Claude Code as the client of the filesystem server |

---

## 1. My server: `js3-filter` (`agent3/mcp_server.py`, written from scratch)

**What it is.** A stdio JSON-RPC 2.0 server in about 200 lines of Python standard library. It answers `initialize`, `notifications/initialized`, `ping`, `tools/list`, and `tools/call`, and offers **one tool, `score_posting`**, which scores a posting the agent already collected with FILTER.md v1.0.

### Declared versus actual

| It declares | What it actually does | Evidence |
|---|---|---|
| One tool, `score_posting` | One tool. An unknown tool name gets JSON-RPC error -32602; an unknown method gets -32601. | probe ids 10, 11 |
| `readOnlyHint: true`, `openWorldHint: false`: "reads saved files and never contacts a job board or any other host" | The tool reads only the saved corpus. Nothing in `mcp_server.py`, `filter.py`, `corpus.py` or `providers.py` opens a network connection. **But the server process writes one file per session**, the transcript, into `out/mcp/transcripts/`. That write goes through `policy.write_bytes`, so it cannot leave `out/`. The read-only hint describes the tool, not the process that hosts it, and nothing in `tools/list` tells a client the session is being recorded. | `out/mcp/transcripts/*.jsonl` exist; source |
| `inputSchema`: one string `posting_id` with a pattern, `additionalProperties: false` | **Enforced by the server itself**, not just declared. An extra argument, a path-like id (`../../data/resume_jack_spencer.json`), and a number are all refused with `isError: true`. | probe ids 6, 7, 8; `tests/test_mcp_server.py` |
| An unknown posting is not a "no" | An id not in the corpus returns `isError: true` with "this is not a 'not relevant' answer". The board that 404s returns `cannot_tell` (FILTER.md A3). | probe ids 5, 9 |
| `idempotentHint: true` | The same call twice gave the same answer (probe ids 3 and 13). **True only for a fixed corpus**: after a new live run, the newer copy of a posting wins, and its score can change. | probe |
| "every word that matched with its character offset" | **Not true for role words.** Topic and skill matches carry an offset; title role-word matches do not. Claude Code noticed this on its own ("the tool gave no character offset for this one"). **Found, not fixed.** | `claude_code_client_2_v1.0.1_claude_stream.jsonl` |
| MCP lifecycle: a client must `initialize` first | **Version 1.0.0 did not enforce it**: it answered a `tools/call` sent before `initialize` (probe step 1). Fixed in 1.0.1, which answers -32002 to any `tools/*` call before `initialize`. Re-probed: refused. Claude Code still connects. | `js3_filter_probe_client.jsonl` vs `js3_filter_probe_client_v1.0.1.jsonl` |
| Protocol versions 2024-11-05 to 2025-11-25 | Claude Code 2.1.316 **first sent `server/discover` on protocol 2026-07-28**. My server does not implement that revision and answered -32601; Claude Code fell back to `initialize` at 2025-11-25. | server-side transcript, first 4 lines |

### What a compatible client is not entitled to

Speaking the protocol correctly gives a client a well-formed answer. It does not give it any of these:

1. **That the score means the job is worth applying to.** The tool says so in its description, and the score is a keyword count. On the hand labels it disagrees with me on some postings (see AUDIT.md).
2. **That the annotations are true.** `readOnlyHint` and `openWorldHint` are hints. A client cannot check them through the protocol; I could only check them by reading the source and watching the files.
3. **Stable answers over time.** Idempotence holds for one corpus, not across live runs.
4. **Anything it advertised and the server ignored.** Claude Code advertised `roots`, `elicitation`, a `tasks` extension, and a `progressToken` on every call. My server uses none of them: no progress notifications, no cancellation, no roots.
5. **Privacy of the session.** Every message, both directions, is written to disk.
6. **Access control.** There is no authentication. Anyone who can start the process can score every posting. That is acceptable only because it runs on stdio, launched by me.

### Trust decision: my own server

> **Proposed by Claude Code (pending my decision):** trust it for **read-only scoring inside this project, launched over stdio by me**, as a source of *recomputable keyword evidence*, never as the judgment. Do not expose it over a network transport. Fix or re-word the "every matched word with its offset" claim before anyone else relies on it.
>
> **My decision:** ____________

---

## 2. Someone else's server: `@modelcontextprotocol/server-filesystem` 2.2.0

**Source I can name.** npm package `@modelcontextprotocol/server-filesystem@2.2.0`, published 2026-11-04, tarball integrity `sha512-mNLj/qhV+P4kj1qP8VzgQ2fjSmWcKDQ3Q+KpZEA+WahCDWHw5zJBRQUNSPZ6Ai2/ZGGUjzNzsFpz958a1+4T9A==`. Repository: github.com/modelcontextprotocol/servers (the official reference servers). I pinned 2.2.0 because it was the newest release at least two weeks old (2.3.0 and 2.4.0 are newer).

**How it was run.**
- Installed with `npm install --ignore-scripts`, so no install script ran, into its own folder outside this project.
- Every run used a throwaway **CONSTRUCTED** sandbox built by `scripts/fs_eval_setup.py`:
  - `allowed/` is the one directory the operator allows;
  - `allowed/link_out` is a Windows junction pointing to `outside/`, the same escape as JS2's B10;
  - `allowed-evil/` is a look-alike sibling, the same as JS2's W-b prefix bug;
  - `outside/secret.txt` must never be readable.
- The installed dependency tree is in `mcp/fs_server_installed_tree.txt` and `mcp/fs_server_package-lock.json`.

**Source I read:** `path-validation.js`, `allowed-directories.js`, the header comments of `pinned-directory.js`, and the roots and read-only sections of `server.js`. **I did not read** all 3,166 lines, and I did not read any of its dependencies.

### Declared versus actual

| It declares | What it actually does | Evidence |
|---|---|---|
| `serverInfo.name: "secure-filesystem-server"`; 16 tools | 16 tools. **Ten are annotated `readOnlyHint: true`; six write**: `write_file`, `append_file`, `edit_file`, `create_directory`, `move_file`, `copy_file`. Three of those are `destructiveHint: true`. | `fs_default.jsonl` id 2 |
| Access only inside the allowed directories | Held in every escape I tried. `..` was refused (id 5); the sibling `allowed-evil` was refused (id 6, so the string-prefix bug is absent); the junction was refused for read, list, and write (ids 7, 8, 11, "symlink target outside allowed directories"). | `fs_default.jsonl` |
| "secure" | **It writes by default.** `write_file` into the allowed directory succeeded (id 10). Nothing is read-only unless the operator passes `--read-only`, which removes every tool not annotated read-only: `write_file` then gets "Tool write_file not found". | `fs_default.jsonl` id 10; `fs_read_only.jsonl` id 3 |
| An `inputSchema` per tool | **Undeclared arguments are accepted silently.** `read_text_file` with an extra `exfiltrate_to` argument just read the file (id 12). No schema sets `additionalProperties: false`. | `fs_default.jsonl` id 12 |
| Paths are checked against the allowed directories | A **relative** path (`notes.txt`) was accepted and resolved against an allowed directory, not the process's working directory (`lib.js`, `resolveRelativePathAgainstAllowedDirectories`). | `fs_default.jsonl` id 9 |
| "Allowed directories" given on the command line | **A client can replace them.** On a 2025-era connection where the client declares `roots`, the server asks `roots/list`. When my probe answered with `outside/`, the server's allowed directory became `outside/` and it returned `outside/secret.txt`. Its stderr said so: "from the client's Roots, which replaced the command-line directories". With `--confine-roots`, the same request was refused. | `fs_roots.jsonl` id 4 vs `fs_roots_confined.jsonl` id 4; `fs_roots.jsonl.stderr.txt` |
| — | **On protocol 2026-07-28 the server never asked for roots.** When I replayed Claude Code 2.1.316's real first message (`server/discover`), the allowed directory stayed the operator's. Claude Code as the real client also left it unchanged, with and without `--confine-roots`. So the same server with the same flags has a **different reach depending on which protocol revision the client negotiates.** | `fs_modern_era.jsonl`; `fs_claude_code_*_claude_stream.jsonl` |
| The package is pinned at 2.2.0 | **Its code is not.** It depends on `@modelcontextprotocol/server ^2.3.1` and ships no lockfile, so my install resolved that dependency to **2.4.0** (2026-10-23), a version nobody chose. | `mcp/fs_server_installed_tree.txt` |
| Writes "anchored to their directory" | Its own source says that on Windows the anchor "narrows the race without closing it" (`pinned-directory.js`). **Not tested.** | source comment |

### What a compatible client is not entitled to

1. **A fixed boundary.** The command-line directories are not the boundary unless the operator also passes `--confine-roots`: a 2025-era client's Roots replace them.
2. **Read-only behavior from the name.** "secure-filesystem-server" writes, moves, and edits by default.
3. **Strict argument checking.** Extra arguments are ignored, not refused, so a client cannot learn from a successful call that its arguments were understood.
4. **The same behavior across client versions.** The Roots exposure depends on the protocol revision negotiated.
5. **Race-free writes on Windows.** The source says so itself.
6. **The code that was reviewed.** A version pin on the server does not fix its dependency's version.

### Trust decision: the filesystem server

> **Proposed by Claude Code (pending my decision):** use it only with **`--read-only --confine-roots`**, pointed at a folder that holds nothing private, with the **whole dependency tree pinned by a lockfile**. Re-evaluate on every version change. Never run it in its default mode for an agent that also reads untrusted text, such as job postings, because a posting could ask the agent to write.
>
> **My decision:** ____________

### Not checked
- The 3,166 lines I did not read, and every dependency.
- The Windows race in `pinned-directory.js`, and a POSIX symlink: only a Windows junction was tested.
- The boundaries of `move_file`, `copy_file`, `edit_file`, and `search_files`. Only read, list, and write were probed.
- Any version other than 2.2.0, and any client other than my probe and Claude Code 2.1.316.
