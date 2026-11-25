# Probe of another tool server: `claude mcp serve` (Claude Code 2.1.285, Anthropic)

Run by Claude Code on 2026-11-25 at 12:38 UTC, using this folder's own client (`jobfilter/mcp_client.py`).
The transcript is `transcript-2026-11-25.jsonl`: 9 lines, both directions, with UTC times.

## Commands

The server ran in a new, empty throwaway directory outside the repo. The calls file
(`probe-calls.json`, with paths redacted) asked for exactly two tool calls:

1. `Read` with `limit: 3` on `drafting/FILTER-QUESTIONS.md` in this folder. That file is **outside** the server's working directory.
2. `Write` of a new one-line file **inside** the throwaway directory.

No other tool was called (no Bash, WebFetch, Artifact, RemoteTrigger or PushNotification).

```bash
python3 -m jobfilter.mcp_client RAW.jsonl probe-calls.json --cwd <THROWAWAY_PROBE_DIR> -- claude mcp serve
python3 -m jobfilter.redact RAW.jsonl evaluations/other-server/transcript-2026-11-25.jsonl
```

## Redaction, the only edit

`jobfilter/redact.py` replaced absolute local paths:

| Placeholder | Stands for |
|---|---|
| `<THROWAWAY_PROBE_DIR>` | the empty directory the server ran in |
| `<JS3_FOLDER>` | this folder's absolute path |
| `~` | the home directory |

The unredacted raw transcript was 218,940 characters (sha256 prefix `b8e4818dd45c80f1`). It was not committed.

## Observed facts (from the transcript, no judgment)

- **initialize:** `protocolVersion` `2025-06-18`; `capabilities.tools.listChanged: true`; `serverInfo` `claude/tengu` `2.1.285`.
- **tools/list:** 28 tools, among them Agent, Bash, Read, Edit, Write, NotebookEdit, WebFetch, WebSearch, Artifact, ArtifactData,
  SendMessage, CronCreate, RemoteTrigger, Monitor and PushNotification.
  - **0 of 28** declare MCP `annotations` (no `readOnlyHint` or `destructiveHint`).
  - 17 kinds of non-spec keys appear, for example `searchHint` (27 tools), `backgrounding` (28),
    `maxResultSizeChars` (28), `shouldDefer` (18) and `enablesCodeExecution` (4).
- **tools/call Read:** returned the first 3 lines of a file outside the server's working directory, with no prompt.
  Reply about 7 ms after the request.
- **tools/call Write:** created `written-by-js3-probe.txt` (62 bytes) in the throwaway directory, with no prompt.
  The file was then read back from disk: `JS3 probe: written through claude mcp serve tools/call Write.`
- **Shutdown:** the server had not exited 10 s after stdin was closed. The client killed it (exit `-9`).
