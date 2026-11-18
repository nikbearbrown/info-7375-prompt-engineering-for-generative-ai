# The agent as a tool, and two tool servers evaluated

> **Authorship.** Claude wrote the server, the client and this report. Every transcript cited
> was recorded on 2026-11-14 US Eastern time (2026-11-15 in the UTC timestamps inside the
> files). Nothing in this report is a constructed example.

## Executive summary

The agent's scoring step is offered to Claude as a tool, through a small server written from
scratch that speaks the Model Context Protocol (MCP). It has one tool, `score_posting`: give it
a board and a posting id, and it returns the filter's verdict with the posting text it rests
on. Claude Code, used as a real client, called it twice and reported the results without
adding facts. The server was then tested the way you would test a stranger's server, by
sending it requests it does not offer, and it refused every one.

A second, independent server was evaluated the same way: Microsoft Learn's public MCP
server. It does what it declares for documentation search. It also declares capabilities it
does not offer, accepts a search with no query, writes instructions to the model into its
tool descriptions, and gives each anonymous client an identifier inside a readable session
token. **Recommended trust decisions (Smit decides in the sign-off):** my server is fit for this agent's use. Microsoft Learn's is fit
as a read-only documentation source whose output is treated as untrusted text. It does not
belong in this job agent.

## The server

| | |
|---|---|
| Code | `src/mcp_server.py`, Python standard library, about 160 lines, JSON-RPC 2.0 over stdin/stdout |
| Methods | `initialize`, `notifications/initialized`, `ping`, `tools/list`, `tools/call`. Anything else gets `-32601` |
| Tool | `score_posting(board ∈ {airbnb, figma, spotify, linear}, posting_id ~ ^[A-Za-z0-9-]{1,64}$)`, no other arguments |
| Annotations | `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: false` |
| Data | the saved run `runs/live-20261114/` and `persona/`, loaded at start. No network |
| Writes | only `transcripts/<name>.jsonl`, the record of every line in and out |
| Result | JSON text labeled `RECORD (written rule, recomputable) - not a judgment of whether the job is worth applying to` |

Start it by hand: `python3 src/mcp_server.py --transcript-name my-try` (then type JSON-RPC lines).

## Transcripts (both directions, real)

| File | Client → server | What happened |
|---|---|---|
| `transcripts/client-session-20261114.jsonl` (+ `-server-side`) | my client (`src/mcp_client.py stdio-session`) | initialize, list, 2 valid calls, then 7 requests a client is not entitled to: a path as `posting_id`, a path as `board`, an extra `write_to` argument, an undeclared tool `read_file`, `resources/list`, a line that is not JSON, an unknown id. Then `ping` |
| `transcripts/claude-code-client-20261114-server-side.jsonl` + `.answer.json` | **Claude Code 2.1.323**, model `claude-sonnet-5-5` | discovery probe, initialize, list, 2 calls. Claude's answer, cost $0.05, is in `.answer.json` |
| `transcripts/mslearn-list-20261114.jsonl`, `mslearn-session-20261114.jsonl` | my client over HTTPS | Microsoft Learn's server: initialize, list, 1 search, 1 fetch, 1 search with no query, `resources/list`, `prompts/list` |

To rerun: `python3 src/mcp_client.py stdio-session --name <new>`; for Claude Code, see README.

**One edit to a transcript, disclosed.** In `mslearn-session-20261114.jsonl` the two
documentation bodies Microsoft returned (41 KB and 53 KB of Microsoft's text) are cut to their
first 600 characters, marked `"redacted": true`, with the byte count and SHA-256 of the full
message. That keeps a public repository from republishing Microsoft's pages. Every other line,
and every line of every other transcript, is as recorded. The unedited file is in
`transcripts/full/` on Smit's machine (git-ignored) and can be checked against the hashes.

## Evaluation 1: my server, as if someone else wrote it

**Declared vs actual**

| Declared | What it actually did (evidence) |
|---|---|
| one tool, read-only, closed world | `tools/list` returned exactly one tool. A test checks the server writes only its transcript (`ToolServer.test_a_real_session_writes_only_its_transcript` runs the server as a process and hashes every file in the folder before and after). It has no network code |
| arguments: exactly `board`, `posting_id` | `write_to` was refused with `isError: true` (transcript id 7) |
| `posting_id` is an id, not a path | `../../persona/aarav-patel.resume` was refused (id 5). Deleting the pattern check does not change this, because ids are only looked up in memory. That is why mutant M7 survives (`tests/mutation-log.md`) |
| tools only | `resources/list` → `-32601` (id 9). Undeclared `read_file` → `-32602` (id 8) |
| result is a record | every result carries the RECORD label. Claude Code repeated it ("records of the written filter (version 1.1), not a judgment") |

**What the real client did that the server never asked for.** Claude Code first sent
`server/discover` at protocol `2026-07-28`, which the server refused, and then fell back to
`initialize` at `2025-11-25`. It advertised `roots` and `elicitation`, which this server never
uses, and it attached `_meta` with a `progressToken` to each call, which this server ignores.
The server answered every message it understood and refused the rest. The client coped.

**What a compatible client is not entitled to**, even if it speaks perfect MCP:

- reading any file: the résumé, the transcripts, the code;
- choosing the run or the data directory (fixed at start, not an argument);
- the network, through this server;
- writes of any kind;
- a judgment of fit. The tool returns what a written rule decided and the text it quoted.
  Whether a job is worth Aarav's time is not on offer.

**Weaknesses found.** The evidence quotes once cut sentences at "e.g.", which Claude Code
then repeated faithfully (`", React/TypeScript) and back-end technologies (e."`). That display
bug was fixed after this transcript and changed no verdict. The server also trusts its own
saved data: if `runs/` were edited, it would serve the edited verdicts, labeled as records.

**Trust decision (recommended by Claude; Smit decides in the sign-off):** **trust for this agent**, local use only, over
stdio, with the data folder fixed at start. Not for exposing over a network: it has no
authentication, because it was never meant to have any.

## Evaluation 2: Microsoft Learn MCP server (`https://learn.microsoft.com/api/mcp`)

The source is Microsoft, a public server with no sign-in. It was reached with my own client
over Streamable HTTP, with the allow-list set to `learn.microsoft.com` only.

**Declared vs actual**

| Declared | What it actually did (evidence: `transcripts/mslearn-session-20261114.jsonl`) |
|---|---|
| capabilities `tools`, `prompts`, `resources`, `logging` (each `listChanged: true`) | `prompts/list` → empty; `resources/list` → empty. Only tools exist |
| 3 tools, all `readOnlyHint: true`, `destructiveHint: false` | search and fetch returned documentation. Nothing observable was changed, though a client can't verify that |
| `microsoft_docs_search(query)`, with `query` not marked required (default null) | called with `{}`: returned `{"results": []}`, not an error. The declared schema matches the behavior, but a missing query passes silently |
| `microsoft_docs_fetch(url)`: "Fetch … Microsoft documentation webpages" | fetched a learn.microsoft.com page as Markdown (53 KB). **Not tested:** what it does with a non-Microsoft URL. Probing someone else's server for that would go beyond normal use |
| session | the `Mcp-Session-Id` is base64 of readable JSON: my client's name and version plus a `userIdClaim` UUID the server assigned. It is not an opaque random token; it carries an identifier for an anonymous client |
| tool descriptions | contain instructions aimed at the model: "Always use this tool…", "This is a required step for comprehensive results", "LATEST OFFICIAL". This is text written to steer whichever model reads it |

**What a compatible client is not entitled to assume:**

- that the returned documentation is free of instructions: it is web content, so treat it as data;
- that `readOnlyHint` is enforced: it is a hint the server makes about itself;
- that "required step" in a description binds the client: it does not.

**Trust decision (recommended by Claude; Smit decides in the sign-off):** **trust as a read-only documentation source,
with outputs treated as untrusted text. Not added to this job agent**, which has no need for it.
Do not connect it in a session that holds private files.
