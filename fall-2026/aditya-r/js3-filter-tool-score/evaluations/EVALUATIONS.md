# Two tool servers, evaluated the same way

Both servers are evaluated under the same four headings. Each claim is marked **[exercised]** (a call was actually made, and its transcript is cited) or **[source]** (learned only by reading the code). The trust decisions are **proposed by Claude Code. Aditya confirms or changes them in the sign-off.**

## 1. Our server: `js3-score-posting` 1.0.0 (`js3/mcp_server.py`, this folder)

### Declared capability
- `initialize` declares `capabilities: {tools: {listChanged: false}}` and no resources, prompts or logging.
- There is one tool, `score_posting(posting_id, filter_version?)`.
  - The description says "Read-only", and that the corpus is saved and nothing is fetched.
  - Its annotations are `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: false`.
- Supported protocol versions: 2025-11-25, 2025-06-18, 2025-03-26 and 2024-11-05. If the client requests one of these, it is echoed back. Otherwise the server answers with 2025-11-25.

### Observed behavior and evidence
- **[exercised, Claude]** `transcripts/claude_code_2026-11-25_run1.*`, made with Claude Code 2.1.310 as the client on 2026-11-25 at 21:26 UTC.
  - Claude Code first sent `server/discover` with `_meta` protocol version **2026-07-28**. Our server does not implement that, answered **-32601**, and the client fell back to `initialize` with **2025-11-25**. **Our server works with this client only through that fallback.**
  - Claude then called `tools/list`, followed by two `tools/call` requests:
    - The first was a success: `R 4 + S 0 + T 3 + E 1 + Y 0 = 8; threshold 6 -> keep`.
    - The second used an unknown id, and the result had `isError: true` with "I cannot tell: … not in the saved corpus … Nothing was fetched or guessed."
- **[exercised, test client, not Claude]** `transcripts/selftest_js3_test_client.*` and `tests/test_mcp_server.py` (12 tests) cover:
  - invalid argument types, extra arguments (`path`), an unknown tool name (`write_file`) and a traversal-style `filter_version`: each gives -32602;
  - an unknown method (`resources/list`): -32601;
  - malformed JSON: -32700.
  - The tool result equals direct scoring with `js3.filter`.
- **[source, plus a source-scanning test]** There are no network, subprocess or shutil imports. The only file opened for writing is the optional wire log (`--log`). The corpus is built in memory (`build(write=False)`).
- **Declared vs actual gap found:** the `instructions` string that Claude received said "no writes". With `--log` set, though, the server **does** append to a local file.
  - That log is set by the operator and is outside the tool surface, but the sentence was still inaccurate.
  - It was corrected after the run: "Tools write nothing; the operator may enable a local wire log (--log)." The 2026-11-25 transcript keeps the old wording, because it is the record of what was sent.
- **Not exercised:** the 2026-07-28 protocol, cancellation, concurrent requests, very large inputs, or a client that lies about its capabilities.

### What protocol compatibility does not entitle a client to assume
- **Freshness.** A valid result is not a current posting. The corpus is from 2026-10-30 and 2026-11-10, and the tool cannot tell whether a posting is still open.
- **Judgment.** A `keep` is a filter score, not a judgment that the job is worth applying to. The tool description says so.
- **Features.** Echoing a protocol version is not implementing that version's features. The server has no `outputSchema`/`structuredContent`, no tasks, no elicitation and no `server/discover`.
- **Truthful annotations.** `readOnlyHint` is a claim by the server. Here it is backed by a source-scanning test. A client still cannot verify it over the wire.
- **Safe text.** Tool results contain text copied from job postings. A client must treat that text as data, not instructions.

### Proposed trust decision
**Trust, within a narrow scope:**
- Use it locally, over stdio, attached to Claude as a read-only scorer for this folder's saved corpus, pinned to the commit in the README.
- Don't expose it over a network, and don't use it as a source of truth about whether a job is open or suitable.

Reasons:
1. There is one tool with a closed input schema.
2. No network or exec code exists, and a test checks the source for it.
3. Every failure path seen ends in an explicit error or "I cannot tell".

## 2. Other server: `@modelcontextprotocol/server-filesystem` **2.3.0**

- **Source:** npm package `@modelcontextprotocol/server-filesystem` from the `modelcontextprotocol/servers` repository, published 2026-11-11. The newer 2.4.0 (2026-11-18) was deliberately not used, because it was one week old.
- **Install:** `npm install --ignore-scripts` into a directory outside the repo. The `package.json` and `dist/*.js` hashes are in `evaluations/fs_server_2.3.0_dist.sha256`.
- **Run:** with Node **v22.14.0**, although the package declares `engines: node >=24`. It ran for these sessions. That is not support.
- **Client:** the js3 test client (not Claude), against a throwaway sandbox. The four sessions are in `transcripts/fs_*` and their summary is `evaluations/fs_server_observed.json`, produced by `evaluations/exercise_fs_server.py`.

### Declared capability
**[exercised]**
- `initialize` declares `tools` (`listChanged: true`) **and** `resources` (`listChanged: true`).
- There are **16 tools**. Six are annotated `readOnlyHint: false`: `write_file`, `append_file`, `edit_file`, `create_directory`, `move_file` and `copy_file`. `write_file`, `edit_file` and `move_file` are also annotated `destructiveHint: true`.
- **[source]** It also has a `file://{+path}` resource template with an empty `resources/list`, and options for `--read-only`, `--read-only-dir` and `--confine-roots`.

### Observed behavior and evidence
| Session | Setting | What happened [exercised] |
|---|---|---|
| A | default, `allowed/` | Reading `allowed/note.txt` works. `outside/secret.txt`, `allowed/../outside/…` and the **symlink** `allowed/link_out/secret.txt` are all denied ("symlink target outside allowed directories"). **`write_file` succeeds, and the file exists afterwards.** |
| B | `--read-only` | 10 tools are listed. `write_file` gets JSON-RPC -32602, "Tool write_file not found". The reads behave as in A. |
| C | default, and the client advertises Roots = `other_root/` | **The client's root replaced the operator's directory.** `list_allowed_directories` returns only `other_root`. `other_root/root_file.txt` becomes readable, and `allowed/note.txt` is now denied. Writes into `allowed/` are denied. |
| D | `--confine-roots`, with the same Roots | The roots outside the command-line directory are ignored. Access stays on `allowed/`, and `other_root/` is denied. |

- **[source]** The read-only mode keys on `annotations.readOnlyHint === true`, so it fails closed: a new tool is withheld unless it declares itself read-only.
- **[source]** Every read and write goes through `validatePath`, which compares realpaths with the allowed directories. Resources use the same check.
- **[source]** On a 2026-07-28 connection, Roots are deprecated and only the command line sets the directories.
- **[source]** Not exercised: the 2026-07-28 era, `move_file`/`edit_file`, resources, TOCTOU races, and very large files.
- **Information exposure [exercised]:** a denial message names the allowed directory's absolute path ("… not in <SANDBOX>/allowed"). That reveals local paths to the model.

### What protocol compatibility does not entitle a client to assume
- **The operator's boundary.** A compatible client is **not entitled to assume** the directory the operator configured is the one in force. On a 2025-era connection, the client's own Roots redefine it (session C). A client is also not entitled to *widen* access just by speaking the protocol: the operator can pin it with `--confine-roots` (session D).
- **Read-only behavior.** Speaking MCP doesn't make a server read-only. The default tool list can create, overwrite and move files (session A).
- **Truthful hints.** Annotations are self-reported. This server's `--read-only` trusts its own annotations, and a client can only check them by testing, as here.
- **A fixed version.** The version and the code can change underneath a client. Running `npx` without a pin would have fetched 2.4.0, published a week after the version evaluated here.
- **Engine support.** The engine requirement (Node ≥ 24) was not met. Running on Node 22 is untested territory for its authors.

### Proposed trust decision
**Do not attach it to the job-search agent in its default mode.**
- The six file-changing tools contradict this agent's rule that its tools may not change data, and a client's Roots can move its boundary.
- **Conditionally acceptable** for read-only browsing of this folder only, with all of these:
  1. `@2.3.0`, pinned;
  2. `--read-only --confine-roots <js3 folder>`;
  3. installed with `--ignore-scripts`;
  4. on a supported Node (≥ 24).
- Even then, `score_posting` already gives Claude what the agent needs. Broad file reads add exposure, such as the transcripts and labels, without adding capability. **Recommendation: not needed, so not attached.**
