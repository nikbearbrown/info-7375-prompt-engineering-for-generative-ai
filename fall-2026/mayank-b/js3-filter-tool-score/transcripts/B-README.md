# Transcript B: Claude Code as a real MCP client

Both runs below happened on 2026-11-26 UTC (2026-11-25 evening ET) on Mayank's Mac. The client was
Claude Code `2.1.323 (Claude Code)` (output of `claude --version`, saved for run 1 in
`B-claude-code-2026-11-26T02-20-05Z.claude-version.txt`, and printed into the `.md` for run 2). `modelUsage` in each client
output lists `claude-opus-5-5`, which wrote the answer, and `claude-haiku-5-5`, which made a small side call (24 output tokens in run 1).
The corpus was the JS2 development run `2026-11-11T02-24-39Z-second-check` (the JS3 content fetch did not
exist yet), so the posting picked has no text and the filter answers `cannot_tell`.

No secrets are in any of these files. The host config holds only paths. The client output holds a
session id, token counts, cost and a credential *expiry time*, but no credential.

## Run 1: by hand, 2026-11-26T02:20:05Z

Host config: `mcp-config.json` (this file belongs to run 1 only). Command, cwd = project root:

```bash
claude -p "Use the score_posting tool to score posting id 5456619008 and report the verdict and reason exactly as the tool returned them." --mcp-config transcripts/mcp-config.json --strict-mcp-config --allowedTools mcp__jsa3__score_posting --tools "" --no-session-persistence --output-format json
```

| File | What it is |
|---|---|
| `B-claude-code-2026-11-26T02-20-05Z.jsonl` | the server's `--log`: 10 rows, every raw stdio line both ways |
| `B-claude-code-2026-11-26T02-20-05Z.client-output.json` | Claude Code's stdout, verbatim |
| `B-claude-code-2026-11-26T02-20-05Z.client-stderr.txt` | Claude Code's stderr (empty) + `exit=0` |
| `B-claude-code-2026-11-26T02-20-05Z.claude-version.txt` | `claude --version` |

## Run 2: by script, 2026-11-26T02:21:08Z

`python3 -I scripts/mcp_record_b.py --corpus <run dir>` sends the same prompt and flags, but writes a
per-run host config. It produced `B-claude-code-2026-11-26T02-21-08Z.{mcp-config.json,jsonl,client-output.json,client-stderr.txt,md}`.
The `.md` holds the exact command and the version, plus a mechanical check of whether the tool's verdict
and reason appear verbatim in Claude's answer.

## What both runs showed (recorded in the logs)

1. Claude Code's first line was **not** `initialize`. It was a request
   `{"method":"server/discover", "params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28",...}}}`
   with id `"server-discover-probe-1"`. The server does not know that method, so it answered `-32601`
   (it answers unknown methods with -32601 in every state). Claude Code then sent `initialize` with
   protocolVersion `2025-11-25` and id `0`, followed by `notifications/initialized`, `tools/list` and one
   `tools/call` carrying `_meta.progressToken` (the server ignores `_meta`).
2. In both runs the verdict `cannot_tell` and the reason `cannot tell: no posting text` appear verbatim in
   Claude's answer (run 2's check is in its `.md`; run 1 was checked afterwards with the same `in` string test, run once from the shell: True, True).
3. **Both answers added sentences that the tool never returned.** Run 1: "Your latest commits mention a
   filter v1.0 run on the live collection…". Run 2: "not your CP3 fetch with `content=true`… due tonight at
   11:59 PM." Those came from Claude Code's own session context (this repository's files and git state),
   not from the server. EVAL-OWN-SERVER.md (evidence ledger) explains why they are not evidence.
4. Neither server log ends with the server's `"stdin closed; server exit"` meta row. Claude Code ended
   the server process without closing its stdin first, so the server never reached its exit line. The
   last row is the tool result.

## Not checked

- How Claude Code handles an `isError: true` result, a `-32000`, or a `-32602`. Only the success path ran
  through the real client.
- Claude Code's own network traffic and permission internals. Only the flags it was given and its
  `permission_denials: []` output were recorded.
- Any client other than Claude Code 2.1.323.

## Re-record against another corpus

```bash
cd fall-2026/mayank-b/js3-filter-tool-score
python3 -I scripts/mcp_record_b.py --corpus <path to runs/<id>-content>
```

This makes one Claude Code request on Mayank's account.
