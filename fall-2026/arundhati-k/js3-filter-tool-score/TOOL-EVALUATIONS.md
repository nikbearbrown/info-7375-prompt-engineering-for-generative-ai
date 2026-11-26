# Tool-server evaluations (Chapter 8)

Both servers were run on 2026-11-25 and evaluated the same way: what the server **declares** on the wire, what it
**actually does** (from code or observed behaviour), what a compatible client is **not entitled to**, and a trust
decision. Facts below were drafted by Claude Code from the transcripts. The trust decisions are mine, typed in chat.

| transcript | client | server |
|---|---|---|
| [`transcripts/01-own-client.md`](transcripts/01-own-client.md) (+ `.jsonl`) | `mcp_client.py own` (stdlib, written for this) | `python3 -m jsagent3.mcp_server` |
| [`transcripts/02-claude-code-client.jsonl`](transcripts/02-claude-code-client.jsonl) (server-side log) + [`02-claude-code-reply.json`](transcripts/02-claude-code-reply.json) | Claude Code 2.1.316, `claude -p --mcp-config mcp-config.json --strict-mcp-config --allowedTools mcp__js3__score_posting` | same server |
| [`transcripts/03-claude-mcp-serve.md`](transcripts/03-claude-mcp-serve.md) (+ `.jsonl`) | `mcp_client.py claude` | `claude mcp serve` (Anthropic, Claude Code CLI 2.1.316, already installed, nothing downloaded) |

Redaction: in 01 and 03 the local home directory is replaced by `<HOME>` (`mcp_client.py` `redact()`). No other edits.

---

## 1. My server: `js3-posting-scorer` 0.1.0 (`jsagent3/mcp_server.py`)

### What it declares (transcript 01, `initialize` and `tools/list` replies)

- `"protocolVersion": "2025-06-18"`, `"capabilities": {"tools": {"listChanged": false}}`, so it declares no
  resources and no prompts.
- `"instructions": "One read-only tool. It scores postings; it cannot apply, email, or fetch."`
- Exactly one tool, `score_posting`, with `"annotations": {"readOnlyHint": true, "destructiveHint": false,
  "idempotentHint": true, "openWorldHint": false}`. The `inputSchema` has the string properties `posting_id`,
  `title`, `body` and `location`, with `"additionalProperties": false`.

### What it actually does (code + observed)

| probe (transcript 01) | observed reply |
|---|---|
| `tools/call` before `initialize` (fresh process A) | `-32002 "server not initialized ..."` |
| `score_posting` `{"posting_id": "stripe:8128744"}` | rejected, `"topic score 1 < threshold 2"`, `close_call: true`, `claims: []` |
| pasted `Electrical Engineer` + Java/SQL/AWS body | rejected (`no role word in title`), so wrong version W1 did not get through the tool |
| `resources/list` | `-32601 method not found` |
| `tools/call` `apply_to_job` | `-32602 "unknown tool: 'apply_to_job'"` |
| `posting_id: "../../etc/passwd"` | `isError: true`, `"no posting with id ... in the local snapshot"`. The id is a dictionary key, never a path |
| `posting_id: 8128744` (number) | `isError: true`, `"all arguments must be strings"` |
| extra argument `path: "/etc"` | `isError: true`, `"unexpected arguments ..."` |
| line `{not json` | `-32700 parse error` |

- **Reads:** `data/postings.json`, built offline from `data/raw/2026-11-25/*.json.gz` if missing, and `filter/v1.json`.
- **Writes:** `data/postings.json` (only when it is missing), and the transcript log when started with `--log`.
  `main()` refuses a log path outside this folder.
- **Network:** none. `mcp_server.py` imports only `evidence`, `filter`, and `collect` with `offline=True`.
- The declared hint `"idempotentHint": true` holds for calls, but the **first** start can write `data/postings.json`.
  So "read-only" is true of the tool call, not of server start-up.
- With Claude Code as the client (transcript 02), Claude Code first sent a `server/discover` request
  (`protocolVersion` `2026-07-28` in `_meta`). My server answered it with `-32002` because it was not initialized yet.
  Claude Code then sent `initialize` asking for `"protocolVersion": "2025-11-25"`, my server answered `2025-06-18`,
  and Claude Code accepted that and went on to `tools/list` and two `tools/call`s. My server does not negotiate: it
  always answers `2025-06-18`, whatever the client asks for.
- Claude Code also sent `_meta.progressToken` on each call. My server ignored it and sent no progress notifications.

### What a compatible client is not entitled to

- **The annotations are claims I make, not guarantees.** `readOnlyHint: true` is only a string in a JSON reply.
  Nothing in the protocol checks it, and the only evidence for it is the code and the probes above.
- **A client is not entitled to anything outside the one tool.** `resources/list`, unknown tools and extra
  arguments are refused (transcript 01).
- **There is no authentication on stdio.** Any process that can start the server can call the tool. The server
  can't tell Claude Code from my test client, and the `clientInfo` it receives is self-reported.
- **Once a result is returned, the server has no control over it.** A client may show it to a model, log it, or
  send it elsewhere.
- **The labels are not entailment.** A client is not entitled to treat `"supported"` as the posting's true meaning,
  only as "matched my rule". Transcript 02 shows Claude itself flagging this: the tool labeled "early-career level"
  `supported` from a quote asking for "2–12+ years", and Claude replied that this "doesn't clearly mean early
  career" and that the tool's own output disagrees on level.

**Trust decision (Arundhati's own words, 2026-11-25):** I would allow Claude to use my server only with restricted permissions. I would first verify that the server enforces the access boundaries I intended and that its tools cannot perform actions outside those boundaries.

---

## 2. Someone else's server: `claude mcp serve` (Claude Code 2.1.316, Anthropic)

### What it declares (transcript 03)

- `"serverInfo": {"name": "claude/tengu", "version": "2.1.316"}`, `"protocolVersion": "2025-06-18"`,
  `"capabilities": {"tools": {"listChanged": true}}`.
- **29 tools:** Agent, Bash, Read, Edit, Write, NotebookEdit, WebFetch, ReportFindings, WebSearch, TaskStop, Skill,
  DesignSync, Artifact, ArtifactComments, ArtifactData, EnterWorktree, ExitWorktree, SendMessage, ListAgents,
  ShareOnboardingGuide, CronCreate, CronDelete, CronList, ScheduleWakeup, RemoteTrigger, Monitor, PublishPlugin,
  PushNotification, ToolSearch.
- **None of the 29 tools carries `annotations`.** There is no `readOnlyHint` or `destructiveHint` even on Bash, Write
  or Edit. The `Bash` input schema includes a `dangerouslyDisableSandbox` property.
- The descriptions are long: Artifact's alone is about 21,800 characters, and the whole `tools/list` reply is about
  180 KB.

### What it actually does (observed)

- I sent `initialize`, `notifications/initialized`, `tools/list`, and **one** read-only call:
  `Read {"file_path": "<HOME>/.../js3-filter-tool-score/FILTER.md", "limit": 5}`.
- `Read` returned the first five lines of FILTER.md. No permission prompt appeared and no approval was asked for.
  The client never declared roots, and the server did not ask for any.
- **Not run:** Bash, Write, Edit, Agent, WebFetch, Cron*, PublishPlugin, PushNotification or anything else that
  could change state or send data. So for those tools, "what it does" is unverified. I only know what they declare.

### What a compatible client is not entitled to

- **Listing a tool is not permission to call it.** The server lists `Bash`, `Write` and `PublishPlugin`, but a
  client that only needs to read a file has no business calling them, and nothing on the wire stops it.
- **Missing annotations are not "safe".** With no hints at all, a client can't learn which tools are destructive
  from the protocol. It has to rely on the tool names and descriptions, which the server wrote itself.
- **There is no authentication or scoping on stdio.** The `Read` call above read a file without any check. A client
  is not entitled to assume the server limits itself to the current folder.
- **`listChanged: true` means the list can change mid-session.** A trust decision made on this `tools/list` reply
  covers that reply only.
- **Long descriptions are input to the model.** A client is not entitled to treat ~180 KB of tool descriptions as
  neutral. They are instructions written by the server's author, and they go into the model's context.

**Trust decision (Arundhati's own words, 2026-11-25):** I would not connect it to anything yet. It lists 29 tools without safety annotations, and its Read tool returns file contents without asking permission. I would inspect the tools and test their permissions in an isolated environment before considering access.
