# Tool server and two evaluations (Chapter 8)

## My server: js3-job-filter
`agent/mcp_server.py`, written from scratch (no MCP SDK): JSON-RPC 2.0 over stdio, one JSON message per line. One capability: `score_posting` (FILTER v1.1). Config for Claude Code: `.mcp.json`.

### Real transcripts (both directions)
| Session | Client | Files |
|---|---|---|
| My own client | `agent/mcp_client.py` | `out/transcripts/client-2026-11-25T053730.jsonl` and the matching `server-...` file |
| Claude Code | claude-code 2.1.330, desktop app | `out/transcripts/server-2026-11-25T060303.jsonl` |

What Claude Code actually sent (server-side transcript): first a `server/discover` probe (not in the version my server implements; it got an error and Claude Code continued), then `initialize` asking for protocol `2025-11-25`. My server supports up to `2025-06-18`, replied with that, and Claude Code accepted the downgrade. Then `notifications/initialized` (no reply, correctly), `tools/list`, and one `tools/call` to `score_posting` (KEEP, score 11).

### Declared vs actual
| Declared | Actual |
|---|---|
| `readOnlyHint: true` | Mostly read-only, but every message, including every tool argument, is written to a transcript file in `out/transcripts/`. That is a side effect the hint does not mention. |
| `openWorldHint: false` | No network code in the server (checked by reading the code and running it with no network access needed). Not tested under a network monitor. |
| `serverInfo.version: "1.1"` | Each result reports `filter_version: "1.0"` with overrides `{"years_cutoff": 5}`. Same behavior, inconsistent labels. |
| Clients must `initialize` first (MCP spec) | My server answers `tools/list` and `tools/call` without it. More lenient than the spec. |
| One tool only | True: `apply_to_job` is refused with -32602 (my client checks this every run). |
| "Scores relevance" | It returns a keyword score. The shortlist audit showed only 4 of 20 "requires <skill>" claims are supported by the text, and Claude noticed padded filler words pass the 50-word rule. |

### What a compatible client is not entitled to
- To trust the hints: `readOnlyHint` and `openWorldHint` are claims made by the server, not guarantees.
- To read KEEP as "worth applying": KEEP means the posting matched keywords and rules, not that its claims are true or that Alex should spend a day on it.
- To privacy for what it sends: everything in a call is written to disk in the transcript.
- To tools that are not listed, or to protocol versions newer than 2025-06-18.

### My trust decision
I trust it for one narrow job: scoring postings locally from saved runs, as a first pass. I do not trust its output as the decision. Whether a posting is worth Alex's time stays mine.

## Other server: Microsoft Learn MCP Server
Source: `https://learn.microsoft.com/api/mcp` (Microsoft; also listed in Claude's connector directory). I called it myself with curl on November 25, 2026, not through my agent, so my agent's allow-list did not change. Every request and response is saved in `evidence/other_server_mslearn/` (request bodies, response bodies, headers).

### What it declares
Protocol `2025-06-18`; server "Microsoft Learn MCP Server" 1.0.0; capabilities logging, prompts, resources, tools. Three tools, all marked `readOnlyHint: true`, `idempotentHint: true`, `destructiveHint: false`: `microsoft_docs_search` (input `query`, but no required list), `microsoft_code_sample_search` (requires `query`), `microsoft_docs_fetch` (requires `url`, described as fetching Microsoft Learn pages).

### Declared vs actual (my four calls)
| Test | Result |
|---|---|
| Same search twice ("Java Kafka trigger Azure Functions") | Identical results (24,026 characters both times). Consistent with `idempotentHint`, but two calls minutes apart cannot show it holds as documentation changes. |
| Search with no `query` | No error: `{"results":[]}`, `isError` unset. An invalid call returns an empty answer that looks like success, the same failure shape as an empty job board reported as "no new jobs". |
| Fetch `https://example.com/` | Refused in the text ("The provided URL is not a valid Microsoft documentation webpage link"), but `isError` was unset. A client checking `isError` would treat the refusal as a successful result. |
| Session ID | Not random: base64 JSON containing my `clientInfo` and a `userIdClaim`. The server identifies the client and session. |

Not tested: the declared `prompts`, `resources` and `logging` capabilities; behavior under load; whether read-only holds for every input.

### What a compatible client is not entitled to
- To rely on `isError` to detect refusals or bad input; it must read the text.
- To treat an empty result as "nothing exists"; it can mean "the request was invalid".
- To anonymity: the session ID carries client details and a user-ID claim.
- To idempotence over time: identical results within minutes show repeatability, not stability.

### My trust decision
Trusted for read-only documentation lookups where a person reads the result. Not trusted as an unattended step in an automated loop, because its errors don't use the error flag and invalid input returns empty success. I would send it no personal data.
