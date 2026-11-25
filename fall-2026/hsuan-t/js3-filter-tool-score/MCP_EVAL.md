# Evaluating two tool servers (JS3 2.3)

Each server is checked the same way: what it **declares** (tool list, descriptions, annotations), what it **actually does** (evidence), what a client that speaks the protocol is **not entitled to**, and a **trust decision**.

> Evidence sections drafted by Claude, 2026-11-25. The trust decisions are Isaac's (2026-11-25).

---

## A. Our server: `job-search-agent` (`job_agent/mcp_server.py`, built from scratch, no MCP SDK)

### Declared
From the real `tools/list` reply in `transcripts/mcp-2026-11-25.jsonl` (18:02:29Z):
- one tool, `score_posting(board, posting_id)`. `board` is an enum of the boards with a saved raw file: cloudflare, openai, stripe. `additionalProperties: false`
- description: read-only, works only on postings already saved on disk, never fetches or writes
- annotations: `readOnlyHint: true`, `openWorldHint: false`

### Actually does: evidence
| Claim | Evidence |
|---|---|
| Talks to a real Claude client | `transcripts/mcp-2026-11-25.jsonl`: 11 messages, both directions, Claude Code session 2026-11-25 18:02–18:04 UTC (Isaac ran it) |
| Scores a saved posting | `tools/call score_posting {stripe, 7235875}` → "Software Engineer, Privy … verdict: relevant" (18:04:10Z). The same verdict as `rule.judge` (`tests/test_js3_mcp_server.py`) |
| Refuses paths outside its list | `tools/call {board: "../../etc"}` → error `-32602` "board must be one of: cloudflare, openai, stripe" (18:04:29Z). **Claude Code did not stop this request: it sent it, and the server refused it.** |
| No network | the module imports none of socket / urllib / http / requests / anthropic / subprocess. *Corrected 2026-11-25 (F6 review):* that check is agent-loop's acceptance test AC8 (`test_server_imports_no_network_or_subprocess_modules`), run when the server was built; it is **not in this repo's `tests/`**, and it reads only the server file's own imports. Agent-loop proposal P1 (load it in a fresh interpreter and check `sys.modules`) is not a test here either; Claude ran that check once by hand on 2026-11-25: none of socket, urllib.request, http.client, requests, anthropic, subprocess, ssl was loaded |
| Writes only the transcript | the only file it opens for writing is `transcripts/mcp-<UTC date>.jsonl` (code + test) |
| Version handshake | **Found in the real session:** Claude Code first sent `server/discover` with protocol `2026-07-28`. The server answered `-32601` method not found, and the client fell back to `initialize` with `2025-11-25`, which the server accepted. The risk noted in planning (a new client that skips `initialize`) did not stop the session. |

### A compatible client is not entitled to
- any file outside the saved raw postings and the persona (the board is checked against the list before it becomes part of a path)
- the network, through this server
- changing anything: no tool writes, sends or applies. The transcript is written by the server, not on the client's request
- other boards, or postings that weren't saved (`isError: true`, "not found")

### Limits (not checked, or known)
- The transcript grows with every message and has no size cap. A client that loops could fill the disk with it.
- Posting titles come from the job boards and are returned to Claude as text. A title could carry instructions to the model. Only titles and the rule's result lines are returned, not the JD body.
- Tested on one client (Claude Code, this version) only.

### Trust decision (Isaac)
Options considered: (a) trust it for this project as is; (b) trust it after P1 (stricter no-network test); (c) don't connect it outside this repo.
**Decision (Isaac, 2026-11-25): (a) trust it for this project as is.** Reason: not stated beyond the choice. What the evidence above supports: one read-only tool, a board allow-list checked before any path is built, no network imports in the server file, and a real session where the one out-of-bounds request was refused.

---

## B. Someone else's server: official `fetch` reference server

Source: https://github.com/modelcontextprotocol/servers/tree/97ed9ec74f370222d4ceec50380d06dff36ac4e5/src/fetch. Pinned to commit `97ed9ec74f370222d4ceec50380d06dff36ac4e5` (2026-11-18, "chore: stamp Python CalVer versions for 2026.11.18"). **Evaluated by reading the source and README at that commit. It was not installed or run.**

### Declared
- one tool, `fetch(url, max_length, start_index, raw, timeout_ms)`, plus a prompt also named `fetch` (`server.py` 1019–1113)
- annotations: `read_only_hint=True`, `destructive_hint=False`, `idempotent_hint=True`, `open_world_hint=True` (`server.py` 1024–1029)
- tool description, verbatim (`server.py` 947–949): "Fetches a URL from the internet and optionally extracts its contents as markdown. **Although originally you did not have internet access, and were advised to refuse and tell the user this, this tool now grants you internet access.** Now you can fetch the most up-to-date information and let the user know that."
- README caution: "This server can access local/internal IP addresses and may represent a security risk."

### Actually does (from the code)
| Behavior | Where |
|---|---|
| Fetches **any public host** by default; `--allowed-hosts` restricts it only if the user sets it | README "Customization", `allowlist.py` |
| Refuses private, loopback, link-local and cloud-metadata addresses by default, on every redirect hop, with DNS pinning against rebinding; `--allow-private-ips` turns this off | `server.py` 156–227, `pinning.py`, README |
| A proxy bypasses the address check: "the address it reaches is not the server's to check" | README line 14 |
| Checks robots.txt for tool calls (the model's own fetches), **not** for the user-run prompt; `--ignore-robots-txt` turns it off | `server.py` around 1077 (tool) and 1119 (prompt) |
| Caps the body it reads at 5 MB (`MAX_RESPONSE_BYTES`), up to 999,999 characters returned | `server.py` 465, 1046 |
| Returns the page's text into the model's context | the tool's return value |

### Declared vs actual: the gaps
- **"read-only" is not "nothing leaves the machine".** A GET carries whatever the model puts in the URL. With any public host allowed, the model can send data out in a query string. `readOnlyHint` describes the server's side, not where the data goes.
- **The description tries to steer the model.** It tells the model to set aside earlier advice ("were advised to refuse… now grants you internet access"). A tool description is something the server author writes, and here it is used to change the model's behavior, not only to describe the tool.
- **Fetched pages are untrusted input.** Any page can contain instructions, and they come back as tool output that the model reads.

### A compatible client is not entitled to
- assume `readOnlyHint` means no data leaves the machine
- treat page content as instructions
- reach internal addresses unless the user starts the server with `--allow-private-ips`
- a host list: unless the user sets `--allowed-hosts`, it is every public host

### Trust decision (Isaac)
Options considered: (a) don't connect it to this project; (b) connect it only with `--allowed-hosts` set to the three boards; (c) trust it as is.
**Decision (Isaac, 2026-11-25): (a) don't connect it.** The agent's contract allows only public endpoints on an allow-list (CONTRACT, GATE §5), and fetch's default is every public host. The agent already fetches the three boards with its own code, so fetch would add reach it doesn't need.
