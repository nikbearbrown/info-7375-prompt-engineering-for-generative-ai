# Evaluation: the course's teaching server, `info7375-readonly` 1.0.0 (`lookup`)

**The server, and where it comes from:**
- File: `lessons/08-mcp-from-scratch/code/main.py` in the course repository, [nikbearbrown/info-7375-prompt-engineering-for-generative-ai](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/lessons/08-mcp-from-scratch/code/main.py).
- Version: last changed in commit `a8629ce1` (2026-09-06, "feat: publish INFO 7375 Claude and Python course"). This evaluation read it at upstream `e27e91fe`, sha256 `948337afc71b67b659aac44b4a8f3efec5dc699b9bb7c2e683dd6888068b1769`.
- It is 72 lines of standard-library Python. Chapter 8 describes it as a teaching example ("not a conformance implementation").

Claude Code drafted this evaluation on 2026-11-24, judging the server the same way as this folder's own: declared against actual, the four ledgers, and Claude's leads checked. Claude Code first opened this file after `jobwatch/mcp_server.py` was written and tested, at commit `cc80e659`. **The trust decision at the end is the student's.**

**Evidence:**
- The source, read in full.
- [The harness transcript](../transcripts/2026-11-24-course-reference-harness.jsonl): 15 CONSTRUCTED messages, under the same audit hook. It was run by the scripted harness, not by Claude Code as a host.
- [Claude's leads](claude-leads/course-reference-reply.json).

## What it declares, and what it does

| What it declares (where) | What it does | Evidence |
| --- | --- | --- |
| `serverInfo` name `info7375-readonly` | It imports `argparse`, `json` and `sys`. The `lookup` branch reads one literal mapping, `{"office": "505A Dana Hall"}`. Under the audit hook: 17 opens, all reads (the standard library and `main.py`), and no writes, sockets or processes | source-inspected; executed (this version, these inputs) |
| "Read a public course fixture" (tool description) | It reads the mapping. **"public" is a data classification the code can't assert.** Only the data's owner can say it (the chapter makes the same point) | source-inspected |
| Input schema: `key`, a string, required, nothing else | `set(args) != {"key"}` and `isinstance(args["key"], str)`: it matches the schema. But only `office` resolves. Every other string is `Record not found` with `isError: true` (id 7). The description doesn't say that | source-inspected; executed |
| `protocolVersion` 2025-11-25 | It answers 2025-11-25 whatever is asked. With `unsupported-fixture` (id 3) that is allowed, since a server may answer with a version it supports. But it never reads the request | executed; source-inspected |
| (implicit) MCP 2025-11-25 behaviour | **`ping` gets `-32601` "Method not found"** (id 9). The spec says the receiver "MUST respond promptly with an empty response". **A Boolean id is accepted and echoed** (id `true`). The spec says "Requests MUST include a string or integer ID". **`initialize` with no params is accepted** (id 2). The spec puts its fields on the client ("MUST initiate … containing" them), so this is a robustness gap rather than a server violation. **A second `initialize` is accepted** (id 3). For arguments that are an object but fail the schema (`{}`, `{"key": 5}`), the source returns `-32602`, where 2025-11-25 calls input-validation failures tool execution errors. That path is not in the transcript | executed (ids 9, `true`, 2, 3); source-inspected (the `-32602` path); spec read 2026-11-24 |
| Tool requests refused before `initialize` and `notifications/initialized` | Holds: id 1, and id 4 after `initialize` but before the notification, both got `-32000` | executed |

## What a compatible client is not entitled to conclude

- That "505A Dana Hall" is a current, true office. It is a fixture value in source code, and nothing compares it with the world.
- That the fixture is "public". The code can't classify data.
- That a missing record means no such record exists anywhere. The mapping has one key.
- That the server keeps to the session rules. It answers a Boolean id, has no `ping`, and accepts repeated and empty `initialize` requests.
- That it is read-only beyond these inputs and this version. The audit hook covers one run.

## The four ledgers

| Ledger | Line | Evidence | Reopens if |
| --- | --- | --- | --- |
| Protocol | Lifecycle gating holds (ids 1 and 4 get `-32000`). Parse error `-32700`. Unknown method `-32601` (id 10) | executed | a new commit to `main.py` |
| Protocol | `ping` unsupported. Boolean id accepted. Empty `initialize` accepted | executed; spec read 2026-11-24 | a new commit |
| Capability | One literal mapping. No file write, network or process seen | source-inspected; executed (audit hook) | a new commit, or a new tool |
| Permission | Task: answer one classroom question from the declared fixture. Data: a course fixture. Whether it is "public" is the course owner's call. Effects allowed: none | the chapter's own task; **the owner's classification is uninspected** | a different task or data scope |
| Evidence | "505A Dana Hall" equals the mapping in the source | source-inspected; executed (id 6) | a changed fixture |

## Claude's leads, checked

Claude (claude-opus-5-5, 2026-11-24 23:03 UTC) got Chapter 8's instruction with the harness transcript, `main.py` and the advertised tool. It returned 11 leads.

| # | Lead (short) | Checked against | Verdict |
| --- | --- | --- | --- |
| 1 | A Boolean id is accepted and echoed | The transcript (id `true`), the source, and MCP 2025-11-25 "basic" | **Confirmed** |
| 2 | `ping` is not implemented | The transcript (id 9), the source, and the MCP ping page | **Confirmed** |
| 3 | `initialize` is accepted without params | The transcript (id 2) and the source | **Confirmed** as behaviour. The spec text read puts the MUST on the client |
| 4 | The version is ignored, and a repeated `initialize` is accepted | The transcript (ids 2 and 3) and the source | **Confirmed.** Answering with its own version is allowed |
| 5 | Malformed arguments are a protocol error, against 2025-11-25 | The spec: requests that fail the `CallToolRequest` schema *are* protocol errors | **Partly wrong.** The example it cites (id 8, arguments as a list) breaks `CallToolRequest`, so `-32602` is right there. The source's same branch also answers `{}` and `{"key": 5}` with `-32602`, and for those the lead holds |
| 6 | "public" cannot be verified | The source | **Confirmed** |
| 7 | Any string is accepted, but only one key resolves | The source and the transcript (id 7) | **Confirmed** |
| 8 | "readonly" rests on the source, not the transcript | The audit hook | **True of what Claude saw.** The executed evidence now agrees for this run |
| 9 | The companion document is missing | `lessons/08-mcp-from-scratch/docs/en.md` exists in the repository | **Wrong as a finding about the server.** Claude wasn't given that file |
| 10 | A `tools/call` without an id is dropped before dispatch | The source returns before dispatch | **Confirmed** |
| 11 | Some paths are never exercised | The transcript | **Confirmed** (`-32600`, "Unknown tool", missing arguments, demo mode) |

## How it differs from this folder's server (behaviour, not style)

`ping` gets an empty result in ours and `-32601` here. A Boolean id gets `-32600` in ours and is echoed here. An empty `initialize` gets `-32602` in ours and is accepted here. A supported requested version is echoed by ours, while this one always answers 2025-11-25. Schema violations in an object are `isError` in ours (since 0.1.1) and `-32602` here. Both refuse tool requests until both lifecycle steps arrive, and both accept a second `initialize`.

## The trust decision (the student's)

```text
Decision:     allow / deny / pending  ____________
For task:     ____________
Server:       info7375-readonly 1.0.0, main.py at a8629ce1 (sha256 948337af…1769)
Re-review if: ____________
Why, in my words: ____________
```
