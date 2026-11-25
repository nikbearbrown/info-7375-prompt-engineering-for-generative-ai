# Evaluation of our own tool server, `js3-posting-scorer`, as if someone else wrote it

Drafted by Claude Code on 2026-11-25 from the saved transcripts and the source. The trust decision at the end is
Ashwin's to make.

**What was evaluated:** `serve.py`, which runs `jobfilter/serve_tool.py` on `jobfilter/mcp_server.py`. It speaks
MCP over stdio as newline-delimited JSON-RPC 2.0. It was written from scratch with the Python standard library.

**Evidence, both directions, with UTC times:**

| File | Run | Calls |
|---|---|---|
| `client-probe-2026-11-25.jsonl` | Our own client, `jobfilter/mcp_client.py`, at 13:21:09 UTC | `probe-calls.json` |
| `client-probe-2026-11-25-server-1.1.0.jsonl` | Our own client, re-run on the corrected server 1.1.0 at 20:32:11 UTC | `probe-calls.json` (same calls; same results) |
| `../../transcripts/own-probe-server-side-2026-11-25.jsonl` | The same run, written by the server | same |
| `../../transcripts/claude-client-2026-11-25.jsonl` | **Claude Code 2.1.285 as the client**, at 13:21:23 UTC | `claude-client-2026-11-25/` (`prompt.txt`, `command.txt`, `mcp-config.json`), with Claude's reply in `claude-reply.json` |

## Declared versus actual

| Declared | Observed | Verdict |
|---|---|---|
| One tool, `score_posting`, with input `{key: string}`, `required: [key]`, `additionalProperties: false` | `tools/list` returned exactly that. An extra `path` argument got JSON-RPC error `-32602` "unexpected argument(s) ['path']" | Matches |
| Unknown tools do not exist | `apply_to_job` got `-32602` "unknown tool 'apply_to_job'" | Matches |
| Refuses held-out postings | The probe and Claude both got `isError: true` "this posting is in the sealed held-out set". The test `test_refuses_every_held_out_posting` covers all 30 keys | Matches |
| Unknown keys are refused | `../../etc/passwd` got `isError: true` "no posting with key …". The key is a dictionary lookup, never a file path | Matches |
| Scores with "filter v1.0" | Returns `filter_version: v1.0`. Filter v1.1 exists (`78adf4b9`). Server 1.0.0 did not say so; server 1.1.0 says "This is filter v1.0, kept to reproduce the v1.0 results; it is not filter v1.1" | Matches. Since 1.1.0 it is labeled as v1.0, not offered as a substitute for v1.1 |
| "Read-only … cannot … write anything" (server 1.0.0 description and `instructions`, in the 13:21 UTC transcripts) | **Was not literally true.** When started with `--transcript`, the server appends every message to a JSONL file; paths outside this folder are refused (`Transcript`). **Fixed in server 1.1.0:** both texts now say the tool changes nothing and that the server writes only its own transcript, inside the JS3 folder, when started with `--transcript`. `test_declarations_disclose_transcript_and_filter_version` checks this | Mismatch in 1.0.0; corrected in 1.1.0 |
| `readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: false` | No network or subprocess code in `mcp_server.py` or `serve_tool.py` (checked by reading the imports, and by `test_server_modules_import_no_network_or_process_code`). It reads only the committed corpus | Matches, apart from the transcript write above |
| `capabilities.tools.listChanged: false` | The tool list is fixed at start-up | Matches |
| Protocol versions | Our client asked for `2025-06-18` and got it. Claude Code asked for `2025-11-25` and got it | Matches |

**Not in the declaration:**
- Claude Code first sent `server/discover` with `_meta` protocol version `2026-07-28`. Our server answered `-32601`
  (not implemented), and Claude then fell back to `initialize`.
- Claude offered `roots` and `elicitation` capabilities. Our server ignores both.

## What a compatible client is not entitled to

- **To trust the annotations.** `readOnlyHint` and the instructions are claims by the server, and the transcript
  write already shows that a claim can be looser than the code. A client should rely on what it can observe or
  sandbox.
- **To current job data.** Every answer comes from the 2026-11-09 snapshot, and the tool says the job may not still
  be open.
- **To a judgment of fit.** A KEEP means "worth reading". It does not mean qualified, eligible (clearance, work
  authorization) or likely to be hired. A REVIEW means "I cannot tell".
- **To held-out decisions,** or to any posting outside the 805.
- **To the current filter version.** It serves v1.0 until it is changed and redeployed.
- **To protection of the sealed files.** The refusal is a key list inside the tool. Any client that can read this
  folder's files can open `runs/*/heldout-decisions.sealed.json` directly. The server is not an access-control
  boundary.
- **To a stable server.** `serverInfo.version` changed from `1.0.0` to `1.1.0` on 2026-11-25, and nothing promises compatibility with later
  protocol versions such as `2026-07-28`.

## What it exposes outside the folder

It exposes nothing that sends or changes data outside this folder. There is no network, no subprocess and no write
outside the folder; the transcript path outside the folder is refused, and `tests/test_mcp_server.py` checks this.

## Trust decision (Ashwin)

**Status: proposed, pending Ashwin's explicit confirmation.** Ashwin supplied this wording in chat on 2026-11-25; Codex helped draft it.

> I would allow score_posting calls without individual approval for this local coursework dataset, after
> correcting the description to disclose transcript writes. The tool must clearly identify which filter version
> it uses; serving v1.0 is acceptable for reproducing v1.0, but not as an unlabeled substitute for v1.1.
>
> I treat the held-out refusal as a workflow safeguard, not a security boundary. A client with filesystem access
> can bypass it.

The condition in the first sentence was met on 2026-11-25. Server 1.1.0 discloses its transcript writes and labels
itself filter v1.0, not v1.1 (re-probed at 20:32 UTC). The decision itself is still pending Ashwin's confirmation.
