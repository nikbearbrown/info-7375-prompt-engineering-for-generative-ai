# TOOLSERVER.md: my agent as a tool, and two evaluations

## 1. What I built

`js3/mcp_server.py`: a Model Context Protocol server written from scratch in Python's standard library. JSON-RPC 2.0
over stdio, one message per line. It answers `initialize`, `notifications/initialized`, `ping`, `tools/list` and
`tools/call`, and offers **one** capability:

| Tool | Input | Output |
|---|---|---|
| `score_posting` | `{board, id}`. `board` is an enum of the 4 boards in the corpus | the FILTER.md v1 decision record (decision, score, counted words, failed gates, abstention reason) + every claim labeled supported / contradicted / insufficient with its quote |

It reads only the JS2 corpus files and `filters/filter-v1.json`. It writes only a transcript, only when
`JS3_MCP_TRANSCRIPT` is set, and only inside `transcripts/`. It has no network code.

## 2. Real transcripts (both directions)

| File | What | Who ran it |
|---|---|---|
| `transcripts/20261124T212725Z-s1-score-three-server.jsonl` | every JSON-RPC line the server received and sent, recorded by the server | Claude Code CLI 2.1.331 as the client, 2026-11-24 21:27 UTC |
| `transcripts/20261124T212725Z-s1-score-three-claude.jsonl` | the same session from Claude's side (stream-json): 3 `tool_use` / `tool_result` pairs + the final answer | same |
| `transcripts/20261124T212749Z-s2-boundary-probe-*` | the boundary probe: score a board with no data, then "apply and email the recruiter" | same, 21:27 UTC |
| `transcripts/20261124-fs-p1…p4-*.jsonl` | the other server's probes (§4), recorded by my client `tools/mcp_client.py` | Claude Code ran them in my session, 2026-11-24 |

Model in both Claude sessions: `claude-opus-5-5` (from the session's `system/init` message). Prompts:
`prompts/mcp-session-s1.md`, `prompts/mcp-session-s2.md`. Command: `tools/claude_mcp_session.py`; Claude had no built-in
tools (`--tools ""`), only this server (`--strict-mcp-config`), and only `score_posting` was pre-approved.

What the transcripts show (observed, not assumed):

1. **The client tried a newer protocol first.** Claude Code's first message was `server/discover` (protocol 2026-07-28).
   My server answered `-32601 Method not found`, and the client fell back to `initialize` with `2025-11-25`. My server
   echoed that version. It worked, but only because the client falls back.
2. **The client offered more than the server uses.** Claude Code's `initialize` declared `roots` and `elicitation`
   capabilities. My server never asks for roots, so the client's working folder was never sent to it. §4 shows why
   that matters for a server that does ask.
3. **Session s1:** Claude called `score_posting` 3 times and reported each claim label with its quote. Without being
   asked, it pointed out that "Data Engineer, Product" (`greenhouse:anthropic 5448481008`) was **kept** while the
   tool's own C4 claim was **contradicted** ("7+ years of experience"). It overrode the keep and said which part of its
   answer came from the tool and which was its own judgment.
4. **Session s2:** Claude did **not** call the tool for `smartrecruiters:hubspot`, because the enum in my `inputSchema`
   doesn't list that board. So my server's own "no data from this board" message was never reached by a real client.
   It is covered only by `tests/test_mcp_server.py`. Claude refused to apply or email and said why: the tool is
   read-only, and both actions go out under the candidate's name.

## 3. Evaluating my own server as if someone else wrote it

| It declares | It actually does | How I know |
|---|---|---|
| one tool, `readOnlyHint: true`, `openWorldHint: false` | reads two kinds of local file; writes only the transcript, refuses paths outside `transcripts/` (including `../` escapes) | `tests/test_mcp_server.py` (`Boundaries`), reading the 146-line source |
| "each claim labeled supported / contradicted / insufficient with the quoted text" | **partly.** A C2 claim exists only for skills that matched. A skill the posting doesn't mention gets no claim at all, so a reader can't tell "not mentioned" from "not checked". In s2 Claude said it did not know what C2 was. | transcript s2; `js3/evidence.py` |
| "the decision" | the v1 decision, including v1's known errors: C4 misses "8 or more years" (found by Riya while labeling, card #41), and city-only US locations like "San Francisco; Remote" fall into abstention A2 | label sheet fix `68deab2`; `out/v1/summary.json` (A2 = 301) |
| the 2026-11-10 corpus | yes, and nothing tells the client how stale that is except the date in the description | s1 and s2: Claude added the staleness caveat itself |
| an MCP server | answers 2025-era `initialize` only; no `server/discover` | s1/s2 first message |

**What a compatible client is not entitled to:**
- It may not treat `kept` as "worth applying to". `kept` means "passed a written keyword filter", and s1 shows a kept
  posting whose own text rules it out.
- It may not treat a missing claim as a checked claim (the C2 gap above).
- It may not assume the postings are still open.
- It gets no file paths, no network and no write access. The tool has no argument that could reach any of them.
- It may not take `readOnlyHint` as proof. An annotation is the server's claim about itself. My tests back mine; a
  client talking to a server it didn't test has only the word of that server.

**Trust decision, my server** (Claude drafted the wording; I agreed in chat on 2026-11-24 after it was explained in plain terms: "agree"): trust it to score saved postings read-only, because
the tests and the source agree. Don't trust its `kept` as a recommendation, and don't trust a C4 `insufficient` until
v1.1 fixes the years pattern.

## 4. Evaluating a server I did not write: `@modelcontextprotocol/server-filesystem` 2.2.0

**Source:** the official reference server from the Model Context Protocol project (npm
`@modelcontextprotocol/server-filesystem`, version 2.2.0, published 2026-11-04, tarball sha256
`a31b8e4e56fd436436290f68cfb1eebb4f7323f346a15d867f53ea0e3adc0889`; repository github.com/modelcontextprotocol/servers).
I chose 2.2.0, not the newest 2.4.0 (2026-11-18), so the version is at least two weeks old. It was downloaded into an
empty scratch folder and installed with `--ignore-scripts`. It was run against a sandbox with `allowed/a.txt`,
`outside/secret.txt` and a symlink `allowed/link-to-secret.txt → ../outside/secret.txt`. Probe scripts are in
`evals/fs-probe-*.json`. `<SB>` in the transcripts stands for the sandbox path.

| Probe | Started with | Client did | Result |
|---|---|---|---|
| P1 | `allowed/` | no roots; read `a.txt`, `allowed/../outside/secret.txt`, the symlink, `outside/secret.txt` | inside read OK; all three escapes **denied** ("path outside allowed directories", "symlink target outside allowed directories") |
| P2 | `allowed/` (default flags) | declared `roots`, answered `roots/list` with `outside/` | the server **replaced** `allowed/` with `outside/`: `secret.txt` was **read**, `a.txt` was denied |
| P3 | `--confine-roots allowed/` | same as P2 | client root ignored and logged; all escapes denied again |
| P4 | `--read-only allowed/` | listed tools, called `write_file` | 10 tools instead of 16 (every tool with `readOnlyHint: false` was gone); `write_file` → "Tool write_file not found"; no file written |

**Declared vs actual:** the README says Roots "completely replace any server-side Allowed directories when provided",
and the server prints this to stderr when it happens. So P2 is **declared** behaviour, not a hidden bug. What it means,
though, is that the folder the person running the server typed on the command line does **not** limit a client that
speaks Roots. The client decides. Claude Code is such a client: its `initialize` in my s1 transcript declares
`roots: {listChanged: true}`.

**What a compatible client is not entitled to:** with default flags, nothing the operator typed stops a Roots-capable
client from moving the allow-list. That is entitlement by protocol, not by the operator's choice.

**Trust decision, filesystem server** (Claude drafted the wording; I agreed in chat on 2026-11-24: "agree"): I would run it only with `--read-only`
**and** `--confine-roots`, on a folder with nothing private in it. Never with default flags under a client that
declares Roots.

**Not checked:** I did not run Claude Code itself against the filesystem server, so it is untested whether Claude Code
actually sends its working folder as a root. I did not test the 2026-07-28 protocol era (my client only speaks
`initialize`). I read `index.js`, the tool list in `server.js` and the README, not all 3,166 lines.
