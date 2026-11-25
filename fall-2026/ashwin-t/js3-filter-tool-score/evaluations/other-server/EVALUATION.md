# Evaluation of another tool server: `claude mcp serve` (Claude Code 2.1.285, Anthropic)

Drafted by Claude Code on 2026-11-25 from `PROBE.md` and `transcript-2026-11-25.jsonl` (9 lines, both directions,
12:38 UTC). The trust decision at the end is Ashwin's to make.

**Source:** Anthropic's Claude Code CLI, version 2.1.285, as installed on this machine. Its `serve` subcommand runs
Claude Code's own tools as an MCP server over stdio. We probed it with this folder's client, `jobfilter/mcp_client.py`,
and called exactly two tools: `Read` and `Write`.

## Declared versus actual

| Declared | Observed | Verdict |
|---|---|---|
| `initialize`: `protocolVersion` `2025-06-18`, `capabilities.tools.listChanged: true`, `serverInfo` `claude/tengu 2.1.285` | As declared | Matches |
| `tools/list`: 28 tools, including Bash, Read, Edit, Write, WebFetch, WebSearch, Agent, Artifact, SendMessage, CronCreate, RemoteTrigger, PushNotification | As listed | Matches |
| Safety annotations | **0 of 28** tools declare MCP `annotations` (no `readOnlyHint`, no `destructiveHint`). The list includes tools that run shell commands, write files, reach the network and send notifications | **Undeclared.** A client cannot tell from the declaration which tools change things |
| Extra keys | 17 kinds of non-spec keys, e.g. `searchHint`, `backgrounding`, `maxResultSizeChars`, `shouldDefer`, `enablesCodeExecution` | Outside the MCP spec; a generic client would ignore them |
| `Read` (no scope declared) | Returned the first 3 lines of a file **outside the server's working directory**, with no prompt, about 7 ms after the request | Reads beyond its cwd |
| `Write` (no scope declared) | **Created a 62-byte file** in the throwaway directory, with no prompt; it was read back from disk | Changes the file system with no approval step |
| Lifecycle (MCP spec: `initialize` comes first) | Sent as the very first message with no `initialize`, `tools/list` got all 28 tools after about 1.5 s (`preinit-probe-2026-11-25.jsonl`, 22:25:32 UTC, run by Claude Code after the trust decision; only `tools/list` was sent, no tool was called). | **Not enforced.** A client cannot rely on the handshake as a gate |
| Shutdown (not declared) | It had not exited 10 s after stdin closed, so our client killed it (exit `-9`) | A client must handle cleanup itself |

**Deliberately not called:** Bash, WebFetch, RemoteTrigger, Artifact, PushNotification, and every other tool with
an outside effect. Only Read and Write were exercised, and Write only inside a new, empty directory.

## What a compatible client is not entitled to

- **To assume any tool is safe.** With no annotations, nothing in the protocol says which of the 28 tools are
  read-only.
- **To assume the working directory is a sandbox.** `Read` reached outside it.
- **To an approval prompt.** Through this interface, calls ran without asking anyone. The interactive Claude Code
  permission system did not intervene here.
- **To a fixed tool list.** `listChanged: true` means the tools may change during a session.
- **To rely on the non-spec keys.** They are Claude Code specific and undocumented by MCP.
- **To clean shutdown on EOF.**

## Trust decision (Ashwin)

**Status: approved by Ashwin on 2026-11-25** (in chat). Ashwin supplied this wording; Codex helped draft it.

> I would not connect claude mcp serve to an unrestricted client that executes tools without approval. For this
> evaluation, I would allow only Read through an enforced restriction to a disposable directory. The working
> directory alone does not enforce that restriction.
>
> I would disable Bash, Write, WebFetch, SendMessage and RemoteTrigger for this read-only evaluation, and leave all
> other untested tools disabled. Tool-list changes would require another review.
