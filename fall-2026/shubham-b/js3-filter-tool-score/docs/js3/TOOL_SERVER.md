# The agent as a tool (JS3, Chapter 8)

Written by Claude on 2026-11-25 from the transcripts and the code. The two trust decisions
are Claude's recommendations; Shubham confirms or changes them (they are his to make).

## 1. What the server is

[`src/job_search_agent/js3/mcp_server.py`](../../src/job_search_agent/js3/mcp_server.py), written
from scratch with the Python standard library (no MCP SDK). It speaks the Model Context Protocol
over stdio: one JSON-RPC 2.0 message per line. It answers `initialize`, `ping`, `tools/list` and
`tools/call`, accepts the `notifications/initialized` notification, and offers **one tool**:

| | |
|---|---|
| Name | `score_posting` |
| Input | `{"board": one of the four FILTER.md §3 boards, "posting_id": Greenhouse number or Ashby UUID}`, nothing else |
| Output | The FILTER.md score and each rule's points, kept or not, the agent's answer, and the C1–C5 claims with their labels and quoted spans; as text (JSON) and as `structuredContent` |
| Reads | The saved raw responses, `FILTER.md`, the persona (through the pinned-hash gate) |
| Writes | Only the optional transcript, which must be a `.jsonl` under `data/js3/mcp/` |
| Network, processes | None |

```bash
uv run python -m job_search_agent.js3 serve --transcript data/js3/mcp/<name>.jsonl   # the server
scripts/js3_mcp_claude.sh <name> "<prompt>"     # Claude Code as the client (headless)
uv run python scripts/js3_mcp_probe.py <name> [--call TOOL ARGS] -- <server command>   # our probe client
```

## 2. The real transcripts

These are MCP protocol transcripts required by Step 2.3 (client ↔ server messages only); no Claude
conversation or session transcript is included, per the course privacy rule and the JS1 TA note.
Every line in both directions, with a UTC time, exactly as sent.

| File | Client | Server | What happened (2026-11-25 UTC) |
|---|---|---|---|
| [`mcp-wire-claude-code-client-2026-11-25.jsonl`](../../data/js3/mcp/mcp-wire-claude-code-client-2026-11-25.jsonl) | Claude Code 2.1.330, headless, model `claude-sonnet-5-5`, no built-in tools, only `mcp__jsa__score_posting` allowed | ours | 11 lines. Claude Code first sent `server/discover` (protocol `2026-07-28`); our server refused it with error -32600, "send initialize and notifications/initialized first"; Claude Code then sent `initialize` with `2025-11-25`, listed the tools and made two `tools/call`s (Stripe 8128744, Figma 5552549004) |
| [`mcp-wire-claude-code-client-2026-11-25.claude.json`](../../data/js3/mcp/mcp-wire-claude-code-client-2026-11-25.claude.json) | | | Claude's final reply and run facts, trimmed to answer, model, turns and cost (3 turns, $0.037) |
| [`ours-probe-2026-11-25.jsonl`](../../data/js3/mcp/ours-probe-2026-11-25.jsonl) | our probe | ours | A malformed ID, an extra argument, an unknown posting, `resources/list`, and a call to a tool that does not exist (`apply_to_job`) |
| [`playwright-mcp-0.0.86-2026-11-25.jsonl`](../../data/js3/mcp/playwright-mcp-0.0.86-2026-11-25.jsonl) | our probe | Microsoft Playwright MCP 0.0.86 | `initialize` and `tools/list` only: 25 tools |

Claude's reply, as received (quoted from the `.claude.json` `result` field), relayed the tool's
labels faithfully. On the New Grad posting it said "Cannot tell: C4, because the posting gives no
number of years in a sentence about experience". That is exactly the tool's abstention, and it is wrong in the way the tool is
wrong: the posting caps new-grad experience at 18 months, so Kiran's four years are ruled out
([SHORTLIST_NOTES.md](SHORTLIST_NOTES.md) §3). Claude added nothing the tool did not say. That
is what a tool user should expect: the client repeats the server's blind spots.

## 3. Evaluating our server as if someone else wrote it

**Declared versus actual.**

| Declared | Checked how | Actual |
|---|---|---|
| One tool, read-only (`readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: false`) | Read the code; `tests/js3/test_mcp_server.py` | The tool reads files only; no socket or subprocess in the module. True |
| "Never applies, contacts anyone, logs in, or changes any file" | Code reading | The server *does* write a file: the transcript, when started with `--transcript`. The tool itself does not; the server process does. The description is about the tool, but a client cannot tell the two apart |
| Input schema: `board` enum, `posting_id` pattern, no other keys | `test_bad_arguments_are_tool_errors`; probe transcript | Enforced in code, not trusted from the client: a bad ID, a fifth board, an extra key, a non-object all come back as `isError: true` |
| `capabilities: {tools: {listChanged: false}}` | Code | True: the list is a constant |
| Protocol versions | Claude Code transcript | It accepts four revisions and echoes the client's if supported. It does **not** implement `server/discover` (the newer probe Claude Code sent first); a strict client would have to fall back as Claude Code did |
| "Scores; it does not decide" | Output | Every answer is a filter score and claim labels. But the answer text says "Matches the filter", which a careless client could present as "recommended" |
| Results come from "the agent's collected postings" | `source` field in each result | True, and stale by construction: the newest raw is from 2026-11-11. The tool does not say how old its data is unless you read `source` |

**What a compatible client is not entitled to.** Speaking MCP correctly does not entitle a client to:
any file outside what the tool returns (there is no path argument); any write, fetch, or other
board (the board is an enum, the ID a pattern); the persona's contact details (the résumé is
read but only roles, skills and the fixed four-year figure reach the output); a decision ("apply",
"worth your time"): the server never gives one. It is also not entitled to trust the labels as
facts about the job: they are facts about the posting's text, under rules with known limits.

**Trust decision (recommended): trusted for one use, local only.** Let Claude call it on this
machine to explain a posting: it can do nothing but read three kinds of local files and return
text. Do not expose it beyond stdio, and do not let its "Matches the filter" stand in for
Shubham's judgement.

**Shubham's decision:** Trust only for local use - I would allow Claude to call this server on my machine because its capabilities are restricted to evaluating saved job postings, with no network access or ability to apply for jobs. However, the transcript-writing behavior and the possibility of its scoring output being mistaken for a recommendation concern me, so I would not expose it over a network or allow others to access it.

## 4. Evaluating someone else's server: Playwright MCP

**Source:** Microsoft, `@playwright/mcp` (github.com/microsoft/playwright-mcp), version **0.0.86**,
already in this machine's npx cache (`npx @playwright/mcp@latest` is how this machine's Claude Code
configuration starts it). Nothing was installed for this. Evaluated from its `tools/list` (the
transcript above) and by reading its bundled source (`playwright-core/lib/coreBundle.js`). No tool
was called, so no browser was opened.

**Declared versus actual.**

| Declared | Actual (from the source) |
|---|---|
| `serverInfo.version` `1.66.0-alpha-2026-11-18` | The npm package is 0.0.86; the server reports the version of the Playwright core it bundles, an alpha build. The name a client sees is not the package it installed |
| `browser_take_screenshot`: `readOnlyHint: true`, `destructiveHint: false` | It writes an image file (`resolveClientOutputFile`, default folder `.playwright-mcp/` in the working directory, or the temp folder). "Read-only" means read-only toward the web page, not toward the local disk |
| `browser_network_request`: read-only | Returns full request and response headers and bodies. Read-only, but it can hand cookies or authorization headers of a signed-in site to the model; only values configured as `secrets` are redacted |
| Annotations on all 25 tools | Generated from a two-value `type` (`readOnly` / `action`): every action, even `browser_hover` and `browser_resize`, is marked `destructiveHint: true`; every tool is `openWorldHint: true`. Coarse, so a client cannot use them to tell a hover from a form submission |
| `browser_run_code_unsafe`: "executes arbitrary JavaScript in the Playwright server process and is RCE-equivalent" | Honest. It runs code on the host machine, not just in the page |
| `--allowed-origins` | The CLI help says it "*does not* serve as a security boundary and *does not* affect redirects" |
| File access | Limited by default to the workspace roots or the working directory; `--allow-unrestricted-file-access` lifts it. `browser_file_upload` takes absolute paths |
| `capabilities.tools.listChanged: true` | The tool list can change during a session. The source also contains code that turns tools registered by a web page (WebMCP) into callable tools; in this version the listing tools are marked skill-only, and Claude did not test whether a page can add tools in MCP mode |

**What a compatible client is not entitled to.** A client that speaks the protocol is not
entitled to the user's signed-in browser sessions, to submitting forms or clicking "Apply", or to files
outside the workspace. The server does not enforce the first two at all: whatever the client asks,
the browser does.

**Trust decision (recommended): not for this agent.** It is honest about its dangers, and it is fine for
driving a test browser by hand. But one `browser_fill_form` and one `browser_click` would let a
model apply for a job or send a message, which this agent must never do (course brief; CONTRACT
§3). Run as `@latest`, the code that runs can change on every start without review. If a browser
were ever needed for discovery: a pinned version, headless and isolated, with no saved login.

**Shubham's decision:** Don't trust for this agent - Playwright MCP provides browser capabilities that could allow Claude to submit applications, send messages, or interact with authenticated accounts, which violates this agent's boundaries. Running it through @latest also introduces risks because its code can change without review. I would consider using a pinned version in an isolated environment for manual browser testing, but not for autonomous job-search operations.

## 5. What this section does not show

The server was exercised by one client (Claude Code 2.1.330) and our own probe; no other MCP
client. The Playwright evaluation is from declared metadata and source reading; no Playwright tool
was run. The Streamable HTTP transport was not implemented.

`uv run jsa audit-privacy data/js3` reports two findings, both the persona's name "Kiran Joshi"
in the tool description that the transcripts record. The persona is fictional (CONTRACT §4), so
this is expected; it does show that a tool description is data that travels to the client.
