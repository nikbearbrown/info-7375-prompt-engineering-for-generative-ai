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
