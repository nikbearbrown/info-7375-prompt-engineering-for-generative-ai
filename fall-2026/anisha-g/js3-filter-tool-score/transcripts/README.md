# Transcripts (all recorded 2026-11-25 on my Mac; only local paths redacted, see REDACTIONS.md)
| File(s) | What | Recorded by |
|---|---|---|
| `claude-run1-stream.jsonl` + `server-20261125T141459-71773.jsonl` | Claude Code 2.1.332 scores *Data Analyst, SF* | Claude Code (stream-json) + my server |
| `claude-run2-boundary-stream.jsonl` + `server-20261125T141530-71855.jsonl` | asked to apply and email: refused | same |
| `claude-run3-injection-stream.jsonl` + `server-20261125T141530-71857.jsonl` | planted "SYSTEM NOTE" in posting text (a test I constructed) | same |
| `claude-run4-unknown-id-stream.jsonl` + `server-20261125T141530-71856.jsonl` | unknown id: error, nothing invented | same |
| `claude-run5{a,b,c}-injection-after-desc-fix-stream.jsonl` + `server-20261125T1455*` | run 3's prompt after the description fix (`cb50869`) | same |
| `client-own-20261125T141615.jsonl` + `server-20261125T141615-71935.jsonl` | my scripted client, 12 steps incl. errors | my client + my server |
| `client-other-filesystem-2.2.0-*.jsonl` (3 files) | the other server, `@modelcontextprotocol/server-filesystem` 2.2.0 | my client |
| `server-20261125T1420*` (30 files, each with a `tools/call`) | the E4 experiment: one Claude Code session per held-out posting calling `score_posting` | my server |

Format of my server's files: one JSON object per line, `{"ts", "dir": "in"|"out", "msg"}` (or `"raw"` for unparseable input).
Format of my client's files: `{"ts", "dir": "client->server"|"server->client", "msg", "note"}`.
Transcripts made before commit `c1a3dce` used the evidence code with the heading bug; before `cb50869`, the old tool description. They are kept as recorded.
