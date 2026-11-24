# EVAL-OTHER-SERVER.md: evaluating someone else's tool server

## The server and its source

- **What:** the official MCP reference **filesystem server**, `@modelcontextprotocol/server-filesystem`, **version 2.2.0**.
- **Source:** repository `github.com/modelcontextprotocol/servers` (`src/filesystem`), from the npm registry.
- **Why that version:** it was published Nov 4, 2026. The newest release (2.4.0, Nov 18) was only 4 days old when we ran this, so we picked one that had been public for more than two weeks.
- **Integrity:** npm `dist.integrity` `sha512-mNLj/qhV+P4kj1qP8VzgQ2fjSmWcKDQ3Q+KpZEA+WahCDWHw5zJBRQUNSPZ6Ai2/ZGGUjzNzsFpz958a1+4T9A==`, shasum `57838ee5aad32519fb3e7236e1ed17ff43421d84`. `npx` verifies the downloaded tarball against the registry's integrity.
- **How it was run:**
  - command: `npx -y @modelcontextprotocol/server-filesystem@2.2.0 <sandbox>/allowed`, through the same logging tap as our own server (`scripts/mcp_tap.py`);
  - driver: `scripts/probe_other_server.py`, which builds a fresh constructed sandbox in a temporary folder outside this repo for every run.
- **The runtime is unsupported.** npm warned `EBADENGINE`: version 2.2.0 requires **Node ≥ 24**, and this machine ran **Node 23.11.0**. The server started and answered anyway, but the results below are for a runtime its authors don't support.
- **Published history:** two advisories in this package's past:
  - **CVE-2025-53110** (GHSA-hc55-p739-j48w): directory containment bypassed by naive **prefix matching**;
  - **CVE-2025-53109:** a **symlink** bypass, where the path was checked as a string without resolving links.

  Both were reported by Elad Beber (Cymulate) and fixed in 2025.7.1. Sources: [GitLab advisory 53110](https://advisories.gitlab.com/pkg/npm/@modelcontextprotocol/server-filesystem/CVE-2025-53110/), [GitLab advisory 53109](https://advisories.gitlab.com/pkg/npm/@modelcontextprotocol/server-filesystem/CVE-2025-53109/), [Snyk: directory traversal < 2025.7.1](https://security.snyk.io/vuln/SNYK-JS-MODELCONTEXTPROTOCOLSERVERFILESYSTEM-10734144), [Snyk: symlink < 2025.7.1](https://security.snyk.io/vuln/SNYK-JS-MODELCONTEXTPROTOCOLSERVERFILESYSTEM-10734143). They are the same two escapes JS2's boundary tests tried on our own policy (the `jobs-evil` prefix trick and the symlink case).

## 1. What it declares (phase 1, `declare`, Nov 22, 2026, 4:19 PM EST)

**The handshake:** `serverInfo` `{"name": "secure-filesystem-server", "version": "2.2.0"}`, protocol `2025-11-25`, capabilities `tools` (listChanged) **and `resources`** (listChanged). The full reply is in `evals/filesystem-declared.json`; the transcript is `transcripts/other-filesystem-declare-*.jsonl`.

**16 tools.** Six of them change files: `write_file`, `append_file`, `edit_file`, `create_directory`, `move_file`, `copy_file`. The other ten only read: `read_file`, `read_text_file`, `read_media_file`, `read_multiple_files`, `list_directory`, `list_directory_with_sizes`, `directory_tree`, `search_files`, `get_file_info`, `list_allowed_directories`.

**What the descriptions promise:**
- every file tool says **"Only works within allowed directories"**;
- `move_file` and `copy_file` say **"Both source and destination must be within allowed directories"**;
- `list_allowed_directories` says **"Subdirectories within these allowed directories are also accessible"**.

**Its own annotations, as declared:**
- `write_file` and `edit_file` are `destructiveHint: true`.
- `append_file`, `copy_file` and `create_directory` are `destructiveHint: false`.
- `write_file` is `idempotentHint: true`.
- No tool is `openWorldHint: true`.

## 2. Predictions, written and committed before the probe (phase 2)

The sandbox: `allowed/note.txt`; `allowed-evil/secret.txt` (prefix trick); `outside/secret.txt`; and `allowed/link → ../outside` (a symlink). The server's only allowed folder is `allowed/`.

| # | Request | Predicted (if the declarations hold) | Why |
|---|---|---|---|
| 1 | `list_allowed_directories` | `<sandbox>/allowed` only | the command line names only that folder |
| 2 | `read_text_file allowed/note.txt` | **allowed**: content returned | inside |
| 3 | `read_text_file allowed/../outside/secret.txt` | **refused** | `..` leaves the allowed folder |
| 4 | `read_text_file allowed-evil/secret.txt` | **refused** | the prefix trick; CVE-2025-53110 was fixed in 2025.7.1 |
| 5 | `read_text_file allowed/link/secret.txt` | **refused** | a symlink out; CVE-2025-53109 was fixed in 2025.7.1 |
| 6 | `write_file allowed/written.txt` | **allowed**, and the file exists afterwards | a declared write tool, inside: the server is **not** read-only |
| 7 | `write_file allowed/link/pwned.txt` | **refused**, and `outside/pwned.txt` does not exist | a symlink write out |
| 8 | `list_directory <sandbox>` (the parent) | **refused** | outside |
| 9 | `read_text_file note.txt` (relative path) | **refused** (uncertain) | we expect a relative path to resolve against the server's working directory, which isn't allowed |
| 10 | `tools/call delete_everything` | **an error** | not a declared tool |
| R | **Roots:** a client that declares the `roots` capability and answers `roots/list` with `<sandbox>/outside` | **the allowed folder becomes `outside/`**: `outside/secret.txt` readable, `allowed/note.txt` refused (uncertain) | the server's earlier documentation said client roots **replace** the folders given on the command line. If that still holds, a client widens or moves the sandbox just by being "compatible" |

The results are added below the predictions after the probe runs, and the predictions are not edited.

## 3. What it actually did (phase 2, Nov 22, 2026, 4:20–4:21 PM EST)

Sources: `evals/filesystem-probe.json` and `evals/filesystem-roots.json` (with paths shortened to `<sandbox>`), and the full transcripts `transcripts/other-filesystem-probe-*.jsonl` and `…-roots-*.jsonl`.

| # | Predicted | Actual reply | As predicted? |
|---|---|---|---|
| 1 | `allowed` only | "Allowed directories: <sandbox>/allowed" | yes |
| 2 | allowed | the note's text | yes |
| 3 | refused | "Access denied - path outside allowed directories: <sandbox>/outside/secret.txt not in <sandbox>/allowed" | yes |
| 4 | refused | "Access denied - path outside allowed directories: <sandbox>/allowed-evil/secret.txt not in <sandbox>/allowed" | yes. The prefix-trick fix holds in 2.2.0 |
| 5 | refused | "Access denied - symlink target outside allowed directories: <sandbox>/outside/secret.txt …" | yes. The symlink fix holds for reads |
| 6 | allowed; the file exists | "Successfully wrote to <sandbox>/allowed/written.txt"; on disk afterwards, `allowed/written.txt` exists | yes |
| 7 | refused; nothing outside | "Access denied - symlink target outside allowed directories: <sandbox>/outside …"; `outside/pwned.txt` does **not** exist | yes. The fix holds for writes |
| 8 | refused | "Access denied - path outside allowed directories: <sandbox> not in <sandbox>/allowed" | yes |
| 9 | refused (uncertain) | **allowed**: the note's text | **no.** A relative path resolves against the allowed folder, not the server's working directory. This is harmless here, but our prediction was wrong |
| 10 | an error | JSON-RPC error −32602 "Tool delete_everything not found" | yes |
| R | the sandbox moves to `outside/` (uncertain) | When the client declared `roots`, the server sent **`roots/list`** to the client right after initialization, before it answered the first tool call. Our client answered `<sandbox>/outside`. Then `list_allowed_directories` returned "<sandbox>/outside", `outside/secret.txt` **was readable**, and `allowed/note.txt` was **refused**. The server's own stderr said: "Effective allowed directories (from the client's Roots, which replaced the command-line directories)" | **yes, and this is the main finding** |

**Containment held** for every escape we tried (`..`, prefix trick, symlink read, symlink write, parent folder). The two published bugs are fixed in this version, as far as these five cases can show.

**What the folder can't contain is who decides the folder.**
- A client that speaks MCP correctly and declares `roots` **replaced** the operator's command-line choice with its own folder.
- No tool call and no error was involved, and the user was told nothing: the notice went only to the server's stderr.
- The declarations don't reveal this. `list_allowed_directories` describes the folders as "the list of directories that this server is allowed to access", and nothing in `tools/list` says a client can change that list.

## 4. Declared versus actual

| Declared | Actual |
|---|---|
| "Only works within allowed directories" (every file tool) | **Held** for `..`, the prefix trick, symlink reads and writes, and the parent folder |
| The allowed directories are the ones it was started with (the command line, and `list_allowed_directories`) | **Not fixed.** The client's roots replace them silently |
| Annotations: `readOnlyHint` false on 6 tools | **True.** It writes (case 6). Its `destructiveHint: false` on `append_file` and `copy_file` is the server's own opinion; we didn't test overwrite or append on important files |
| Capabilities include `resources` | **Not probed** |
| Requires Node ≥ 24 (`package.json` engines) | It **ran on Node 23.11.0** with only a warning; behavior on a supported runtime wasn't checked |

## 5. What a compatible client is not entitled to

- **To have its requests honored outside the allowed folders.** Our five escapes were refused, which is correct.
- **To assume the server is read-only.** Six tools change files. A client should allow-list only the read tools if reading is all it needs. In Claude Code that's `--allowedTools` naming only the read tools.
- **To treat annotations as guarantees.** `readOnlyHint`, `destructiveHint` and `idempotentHint` are the server's claims about itself.
- **To decide the sandbox.** Our probe shows the server lets it anyway. That's the gap: an MCP-compatible client *can* move the sandbox through `roots`, whether or not the operator meant to allow that. Claude Code declares `roots` (see our own server's transcript, `capabilities: {"roots": {"listChanged": true}}`), so in practice the folder may be whatever the client's roots are, not the folder typed on the command line.

## 6. Trust decision

**Trusted only under conditions.** Hemanth chose this ("T2 a") on Nov 22, 2026, at 5:36 PM EST, from Claude's recommended option. The conditions:
1. Point it at a **throwaway folder**, never this repo or anything personal.
2. The client **allows only the read tools**: in Claude Code, `--allowedTools` naming only the read tools.
3. Use a client whose **roots are fixed to that same folder**, or one that **doesn't declare roots**. Otherwise the client, not the operator, decides what the server can reach (section 3, case R).
4. **Re-check on a supported runtime** (Node ≥ 24) before relying on it. These results come from Node 23.11.0.
