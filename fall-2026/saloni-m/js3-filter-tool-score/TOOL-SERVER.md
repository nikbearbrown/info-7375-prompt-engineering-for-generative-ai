# The agent as a tool (Chapter 8)

## 1. What I built

`js3/mcp_server.py` is a Model Context Protocol server written from scratch: JSON-RPC 2.0 over
stdio, one message per line, standard library only, no MCP SDK. It implements `initialize`
(protocol versions 2025-06-18, 2025-03-26, 2024-11-05), `notifications/initialized`, `ping`,
`tools/list` and `tools/call`. Any other method gets `-32601`.

| Tool | Does | Limits |
|---|---|---|
| `score_posting` | runs FILTER.md on one posting, given by `uid` from the local snapshot or as `title` + `text`, and returns score, decision and every rule that fired | title ≤ 300 chars, text ≤ 50,000; no extra arguments |
| `search_postings` | returns up to 20 snapshot postings whose title has every query word, each with its score | query 1–200 chars; limit 1–20 |

Both tools declare `readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: false`.
Neither fetches anything: `search_postings` searches the 2026-11-26 snapshot on disk.

## 2. Real transcripts, both directions (2026-11-26)

| Session | Client | Files |
|---|---|---|
| A, 16:30:46 UTC | my handwritten client, `scripts/mcp_client.py own`, with the server under the audit wrapper | client side `out/mcp/client-own-20261126T163046Z.jsonl`; server side `out/mcp/transcripts/20261126T163046925729Z-server.jsonl`; audit `out/mcp/audit-own-20261126T163046Z.jsonl` |
| B, 16:31:50 UTC | **Claude Code 2.0.20** (`claude-sonnet-5-5`) as the MCP client, `scripts/claude_uses_tool.py` | server side `out/mcp/transcripts/20261126T163150666071Z-server.jsonl`; Claude's answer `out/mcp/claude-client-20261126T163148Z.json` |
| C, 16:30:59 UTC | my handwritten client against **Claude Code's own server** (`claude mcp serve`), §5 | `out/mcp/client-claude-mcp-serve-20261126T163059Z.jsonl` |
| J3, 16:36:34–16:37:21 UTC | Claude Code as client, one session per held-out posting (SCORE.md); it called a tool in 15 of 30 | the 30 `out/mcp/transcripts/*-server.jsonl` after 16:33 |

Every line is saved with a timestamp and a direction (`client->server` / `server->client`),
byte for byte. The transcripts contain the local folder path (`/Users/…/js3-filter-tool-score`).
JS2's committed traces already contain the same path, so I left them unredacted rather than
edit a real transcript.

**Session A, what my client sent and got back** (from the client transcript):

| Call | Result |
|---|---|
| `score_posting {uid: greenhouse:anthropic:5432575008}` | ok: Applied AI Engineer, Startups, score 5, keep |
| `score_posting {title: "HTML Email Developer", …}` | ok: score 0, reject (no substring match on "ml") |
| `search_postings {query: "data engineer", limit: 5}` | ok: 30 matches, 5 returned |
| `score_posting {uid: …does-not-exist}` | `isError: true`, "no posting … in snapshot" |
| `search_postings {limit: 500}` | `isError: true`, "limit must be an integer from 1 to 20" |
| `score_posting {uid: "x", path: "../../../../etc/passwd"}` | `isError: true`, "unexpected argument(s): ['path']" |
| `tools/call write_file` | JSON-RPC error `-32602`, "unknown tool" |
| `resources/list` | `-32601` method not found |
| a line that is not JSON | `-32700` parse error |

**Session B, Claude Code as the client.** Claude Code sent `initialize` (it declared
`capabilities: {roots: {}}`), `notifications/initialized`, `tools/list`, then **one**
`search_postings {query: "data engineer"}` and **one**
`score_posting {uid: greenhouse:figma:6178851004}`: 9 lines in all. Its final answer reported
the uid, title, score 5, keep, R1 and R3 correctly. It then added:

> "I called `search_postings` twice by mistake. Both calls returned identical results."

**The transcript contradicts this.** There is exactly one `search_postings` request (id 2). The
model's account of its own tool use was wrong, in the cautious direction. Only the wire
transcript can settle what a client did.

## 3. Evaluating my own server as if someone else wrote it

**Declared vs actual.** I ran the server under `scripts/audited.py`. That wrapper installs
Python audit hooks (PEP 578) before the server's code loads and logs every file open, socket
connect, subprocess and exec. Session A logged **91 file-open events, 0 socket events, 0
subprocess or exec events**. The only files opened for writing were its own transcript file
(`out/mcp/transcripts/…-server.jsonl`). The only data files read were `FILTER.md` and the
snapshot `postings.jsonl.gz`.

| Declared | Actual (measured) | Gap? |
|---|---|---|
| "Reads local files only; sends nothing anywhere" | 0 network events | none found |
| `readOnlyHint: true` on both tools | the **server process** writes a transcript of every message, including any text a client passes to `score_posting` | **yes**. The tools change nothing, but the server keeps a copy of what it is sent, and the annotations do not say so. A client that pastes a real résumé into `text` leaves that résumé on disk in `out/mcp/transcripts/`. |
| `inputSchema` for `score_posting` | the "uid **or** title+text" rule is in the description and the code, not the schema (no `oneOf`) | **yes**. A schema-only client cannot know that `{uid, title}` is an error until it tries. |
| `search_postings` "title contains every word in query" | word-set match, so "engineer data" also matches "Data Engineer" | the description does not say word order is ignored |
| `openWorldHint: false` | true for this server; the data it serves came from the open web on 2026-11-26 | the results are as stale as the snapshot |

**What a compatible client is not entitled to:** that the annotations are true (they are hints
the server writes about itself); that the score means a posting is worth anyone's time (it is
FILTER.md v1.0, whose audit is pending); that the snapshot is current; that the transcript is
private (anyone with the folder can read it); and that a successful `tools/call` means the
result is right. `isError: false` means only that the server did not fail.

**Trust decision (mine, pending Saloni's sign-off):** trusted for read-only scoring of the local
snapshot, by Claude Code on this machine, **only with titles and posting text**, never with
résumé text, because of the transcript. The audit covers only the 9 calls in session A. A
different input could open a different path, and the hooks log Python-level events, not
everything the OS does.

## 4. How I'd test someone else's server the same way

1. Read the declared surface: `initialize` result, `tools/list` schemas and annotations.
2. Call each tool with valid input, then with input it should refuse (unknown tool, extra
   argument, out-of-range value, path-like strings).
3. Observe actual behaviour from outside the server: audit hooks for Python, or OS-level
   tracing (`fs_usage`, `dtruss`) for anything else.
4. Compare declared vs actual, line by line.
5. Decide what it may see and do.

## 5. Evaluating another server: Claude Code's built-in MCP server (`claude mcp serve`)

**Source:** Anthropic's Claude Code CLI, version **2.0.20**, already installed on this machine
(`claude --version`). Nothing was downloaded. Session C, 2026-11-26 16:30:59 UTC, my
handwritten client: `initialize`, `tools/list`, one `tools/call Read` on this folder's
FILTER.md (first 5 lines), `ping`.

**Declared.** `serverInfo: {name: "claude/tengu", version: "2.0.20"}`, `capabilities: {tools: {}}`,
**16 tools**: Task, Bash, Glob, Grep, ExitPlanMode, Read, Edit, Write, NotebookEdit, WebFetch,
TodoWrite, WebSearch, BashOutput, KillShell, Skill, SlashCommand. **None declares any
annotations** (`annotations: null` for all 16): no `readOnlyHint` on Read, no
`destructiveHint` on Write or Bash, no `openWorldHint` on WebFetch. Read's description says
"You can access any file directly by using this tool."

**Actual (what I observed).** The `Read` call returned the 5 lines with no approval prompt and
no permission step visible to the client. The text content came back as a JSON string with the
file inside it (`{"type":"text","file":{"filePath":…,"content":…}}`), not as plain text, so a
client must parse twice. I did **not** call Bash, Write, Edit, WebFetch or Task. Their behaviour
is declared, not observed.

**What a compatible client is not entitled to:** that a server this capable will ask before
acting (nothing in the protocol shown here does); that missing annotations mean "safe"; that
paths are limited to a folder (Read's description says the opposite).

**Trust decision: not trusted for this agent.** It exposes `Bash`, `Write`, `Edit`, `WebFetch`
and `Task`: it can run commands, change files anywhere the user can, and reach any host. The
JS3 boundary is "a tool server must not expose anything that can send or change data outside
your own folder". This server violates that by design, so it is never connected to the job
agent. It is the right tool for a developer driving Claude Code, which is a different trust
setting. **Not checked:** whether `claude mcp serve` applies permission settings when Bash or
Write is called. I chose not to find out by calling them.
