# Evaluation: my own MCP server (`mcp/server.mjs`), read as if someone else wrote it

**Drafted by Claude Code on 2026-11-25. For Aravind to edit; the trust decision is Aravind's.**

**Marks:** **[V]** verified, with the evidence named. **[I]** inferred, not tested.

**What it is:** JSON-RPC 2.0 over stdio, one JSON message per line. Written from scratch, with no MCP
SDK; about 120 lines of Node 20 with no dependencies. It handles `initialize`,
`notifications/initialized`, `ping`, `tools/list`, and `tools/call`, and has one tool,
`score_posting`.

## Declared vs actual

| It declares | It actually does | Evidence |
|---|---|---|
| `capabilities: { tools: { listChanged: false } }`, nothing else | Has only tools: no resources, prompts, or sampling. `resources/list` gets -32601. | [V] `test/mcp-server.test.mjs` |
| One tool, `score_posting`, annotated `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: false` | It reads the frozen snapshot and FILTER.md, both loaded once at start. It writes only its own transcript and makes no network call. | [V] the import-graph test: no `child_process`, `node:net` / `http(s)` / `dgram`, `fetch(`, or `judge.mjs`; no file write anywhere in the graph except the server's single `appendFileSync` (the transcript logger) |
| "Read-only scorer … No network, no writes except this server's own transcript" (`instructions`) | Appends to `transcripts/<start>-<pid>.jsonl`. It checks that `transcripts/` resolves, by real path, inside the js3 folder. `JS3_TRANSCRIPT_SUBDIR` must be a plain name, so `../escape` is refused. | [V] tests |
| The input schema: exactly `{posting_id: "board:id"}` | Extra keys, the wrong type, or a bad pattern give `isError: true`. An unknown id gives `isError: true`. | [V] tests (an extra `path` argument is refused) |
| "no posting text returned" | Returns title, location, url (the job page, `absolute_url` / `hostedUrl`), decision, score, components, and the veto quote. A veto quote is up to 300 characters of posting text, so the description slightly overstates this. | [V] the test checks that the first 200 characters of the body are absent. **[V] the mismatch was observed live:** in Claude Desktop call 2 (`transcripts/2026-11-26T004241768Z-70635.jsonl`, 00:45:25 UTC), the tool returned `veto.quote` = "This position needs to be based in the Beijing, China office 5 days a week. No Visa/Relocation Support.". **Fixed after the run** in a separate commit: the description now says it returns no posting body, only the quoted veto sentence. |
| Protocol versions 2025-06-18 / 2025-03-26 / 2024-11-05 | It echoes a supported version. Anything else, including Claude Code's 2025-11-25, gets 2025-06-18. | [V] tests; [V] the real transcript `transcripts/2026-11-26T003743686Z-69681.jsonl` (Claude Code accepted 2025-06-18 and went on to `tools/list`) |
| (nothing about it) | Claude Code first sent `server/discover` (protocol era 2026-07-28). The server answered -32601, and the client fell back to `initialize`. | [V] the real transcript |
| (nothing about it) | It ignores the client's `roots` and `elicitation` capabilities. It never sends a request to the client. | [V] source; [V] the transcripts show both clients declared roots. Claude Desktop also sent 3 × `notifications/roots/list_changed`, and the server sent nothing back. |
| Input refused outside `board:id` (the boundary) | `posting_id: "../../README.md"` gives `isError: true`, "invalid arguments …". The pattern check runs before any lookup, and the server has no file-reading path for ids at all. | [V] Desktop call 3 in the transcript (00:46:01 UTC); [V] `test/mcp-server.test.mjs` (extra `path` argument, unknown id); [V] import-graph test. The model's own explanation in the chat is not evidence. |

## What a compatible client is not entitled to

Speaking MCP correctly does not give a client:
- **Any write, delete, or network action.** None exists in the server; this is not just a hint
  [V].
- **Posting text in bulk, the audit sheet, the hand labels, the held-out ids, or `applyUrl`.** None
  is reachable through the one tool [V].
- **A different filter or persona at call time.** The spec and prefs are fixed at start [V].
- **Trust in the annotations as such.** `readOnlyHint` is a claim a client cannot check. Here the
  claim is backed by the code and the tests, not by the hint.
- **A correct answer.** The output is the filter's RECORD, with all its known limits (FILTER.md §5.3,
  §5.4).
- **Confidentiality of its own calls.** Every message is logged in full to `transcripts/` [V].

## Limits and risks

- [I] **Not hardened against a hostile client:**
  - no request-size limit and no rate limit
  - a very long line is read whole
  - a client could fill the transcript disk by sending many requests

  This is acceptable for a local stdio server started by its own user.
- [V] **The transcript is unbounded and unrotated.**
- [V] **Real clients:** Claude Code 2.1.323 (handshake and `tools/list`; its `tools/call` was blocked
  by the spend limit) and Claude Desktop (two clients; **3 real `tools/call`** in
  `2026-11-26T004241768Z-70635.jsonl`).
- [V] **The evaluation covers exactly the server that ran:** SHA-256 `d5fd7291…` at `461b608d`, checked
  after the run.
- [I] Not tested with any other client.

## Trust decision (draft)

**Trust it for its stated use:** a local stdio server, launched by me, against my own frozen
snapshot. Its write path is one append-only file inside the project folder, it has no network path,
and its one tool is backed by tests, not just annotations.

**Don't trust:**
- the original "no posting text" wording (the veto quote is posting text; fixed after the Desktop run)
- any remote or shared deployment (no limits)
- its answers as judgments of fit (they are the filter's output)
