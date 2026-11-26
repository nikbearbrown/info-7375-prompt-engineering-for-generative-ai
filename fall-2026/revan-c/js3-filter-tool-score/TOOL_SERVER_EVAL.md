# Tool servers — JS3 (Chapter 8)

**Status: bounded evaluation, November 25, 2026.** The facts below come from the transcripts, source files, and check runs named in each row. The decisions at the end apply only to the stated local tasks; the real Claude client call is recorded below.

Gate: [FILTER.md](FILTER.md) section 7 (v1, committed `0e15e65` before any server code).

## The two servers

| | Ours: `js3-score-posting` 1.0.0 | Other: Chapter 8 teaching server `info7375-readonly` 1.0.0 |
|---|---|---|
| Source | [jsfilter/mcp_server.py](jsfilter/mcp_server.py), written from scratch in this repo | [third_party/ch8_teaching_server/main.py](third_party/ch8_teaching_server/main.py), copied unmodified from the course repo `nikbearbrown/info-7375-prompt-engineering-for-generative-ai`, path `lessons/08-mcp-from-scratch/code/main.py`, last commit `a8629ce` (2026-09-06), sha256 `948337af…8b1769` |
| Tool | `score_posting(board, id)` | `lookup(key)` |
| Transport | newline-delimited JSON-RPC on stdio | same (`--stdio`) |
| Transcripts | [own-scripted](runs/js3/transcripts/2026-11-25T22-06-24Z_own-scripted.jsonl); [Claude session](runs/js3/transcripts/claude_code_session.jsonl) | [teaching-scripted](runs/js3/transcripts/2026-11-25T22-06-51Z_teaching-scripted.jsonl); [checks](runs/js3/transcripts/2026-11-25_teaching_server_checks.txt) |

Every transcript line was written by [tools/mcp_tap.py](tools/mcp_tap.py), which relays bytes unchanged and logs each line with its direction and UTC time. The scripted client ([tools/js3_mcp_client.py](tools/js3_mcp_client.py)) is a constructed client, not Claude.

The Claude session log runs from 2026-11-26 01:08:40 to 01:08:44 UTC (November 25, 8:08 p.m. ET). The client identified itself as Claude Code 2.1.330; the tap does not record the model used by that client session. The log contains `initialize`, `notifications/initialized`, `tools/list`, and a `tools/call` for `score_posting` with `board=klaviyo`, `id=8041054003`. The server replied without a tool error: total 7, threshold 6, fate `kept`. A preceding `server/discover` probe received `-32000` while the server was not initialized; the subsequent standard handshake and tool call succeeded.

## Predicted versus recorded (ours)

FILTER.md section 7's table, against [the own-scripted transcript](runs/js3/transcripts/2026-11-25T22-06-24Z_own-scripted.jsonl):

| # | Message | Predicted (FILTER.md) | Recorded | Match |
|---|---|---|---|---|
| 1 | `tools/list` id 1, before initialize | `-32000`, id 1 | `-32000`, id 1 | yes |
| 2 | `initialize` id 2 | result, (T, F) | result `2025-11-25`, `{"tools": {}}` | yes |
| 3 | `tools/list` id 3, before notification | `-32000`, id 3 | `-32000`, id 3 | yes |
| 4 | `notifications/initialized` | no response, (T, T) | no response | yes |
| 5 | `tools/call`, arguments missing `id` | `-32602`, id 5 | `-32602`, id 5 | yes |
| 6 | `tools/call`, unknown posting `klaviyo/999` | result `isError: true`, id 6 | result `isError: true`, id 6 | yes |

Also recorded: `{` → `-32700` id null; `{"id": 8}` → `-32600` id null; `resources/list` → `-32601`; tool `delete_posting` → `-32602`; a second `initialize` → `-32600 Already initialized`.

## Declared versus actual

| Claim | Ours: declared | Ours: what the evidence shows | Evidence type | Teaching: declared | Teaching: what the evidence shows | Evidence type |
|---|---|---|---|---|---|---|
| Lifecycle | (docstring) tools refused until initialize + notification | Rows 1–4 above; test rows 1–4; mutant S1 (ready inside initialize) caught by `test_row3…` | executed | (chapter) same | Same order recorded (ids 1–4). **Its own 6 tests pass with ready set inside initialize** — the mutant answered `tools/list` with no notification | executed |
| Version negotiation | echoes a supported version, else offers `2025-11-25` | `2025-11-25` requested → echoed. Other versions not exercised | source-inspected; executed for one value | none declared | Requested `unsupported-fixture` → answered `2025-11-25`. It does not read `params` | executed |
| Tool description | "Read-only: it fetches nothing and changes nothing" | Source imports `argparse, json, pathlib, sys, jsfilter.filter`; no `open(`, write, socket, http, subprocess (`test_server_source…`, which also covers `jsfilter/filter.py`); a stdio session in a temp dir created no file (`test_stdio_session_writes_no_files`); mutant S2 (log write) caught | source-inspected; executed | "Read a public course fixture" | Imports `argparse, json, sys`; data is one literal dict; a stdio session created no file in its folder. **"public" is the server's word: nothing in the code classifies data** | source-inspected; executed |
| What it reads | the persona and three snapshot bodies | `jsfilter.filter.load_snapshot` reads `resumes/aarav-patel.json` and the 3 `evidence/js2/2026-11-10T06-33-08Z_*.body` files, once at start-up, relative to `--root` | source-inspected | one fixture | literal mapping `{"office": "505A Dana Hall"}` | source-inspected |
| Schema matches validation | `board` enum, `id` string, no extra keys | 5 bad-argument shapes → `-32602` (test row 5) | executed | `key` string, no extra keys | list arguments → `-32602`; extra key → `-32602` | executed |
| Returned value matches source | score is FILTER.md v1's score | `test_returned_score_recomputes…` compares with `score_posting` run directly; mutant S3 (total + 1) caught | executed (on a constructed fixture) | value from the fixture | `505A Dana Hall` = the mapping in source | source-inspected |
| A call without an id | not declared | dropped, no response (source) | source-inspected | not declared | dropped, no response (recorded, last line) | executed |
| A second `initialize` | refused, state unchanged | `-32600`, id 14 | executed | not declared | accepted again, same result (id 13) | executed |
| Network | none | no network module imported; not observed at the OS level | source-inspected; **network uninspected at runtime** | none | same | source-inspected; network uninspected at runtime |

## What a compatible client is not entitled to

A client that completed the handshake and got a well-formed result from `score_posting` may conclude only that *this server version returned this text for this request*. It is **not** entitled to:

1. Treat a score or `fate: kept` as a judgment that the posting is worth applying to. The score is a review order under hand-set weights (FILTER.md 1).
2. Treat a matched word as a requirement. `evidence` quotes show where a word occurs, e.g. "TypeScript" under a "Frontend:" list of technologies the company uses (shortlist claim `klaviyo:7855793003:8`).
3. Treat the posting as open or current. The snapshot is from 2026-11-10.
4. Trust "read-only" because the description says so. That is testimony. The evidence is the source and test rows above, for this version only.
5. Call anything else. The server lists one tool; a client that invents `delete_posting` gets `-32602`, and nothing in the protocol grants it more.
6. Infer the persona is a real person, or send the result anywhere outside this folder.

The same applies to `lookup`. "505A Dana Hall" is the fixture's value, not a verified office.

## Handoff (laundering) table — ours

| Handoff | What passes | Trusted to be | How that trust is earned |
|---|---|---|---|
| Server → host | JSON text: rules, components, total, fate, evidence quotes | FILTER.md v1's output for `(board, id)` on the 2026-11-10 snapshot, from server 1.0.0 | `test_returned_score_recomputes…`; the tap transcript; the source |
| Host → Claude's context | that text, plus the `caution` field | data to cite with its role, not instructions or current facts | `.mcp.json` (command, args, working folder); the tool description says what the score is not |
| Claude → shortlist | a sentence using the score or a quote | a draft claim until it receives a source label | Revan confirmed the 50 atomic labels in `runs/js3/shortlist/CLAIMS.csv`; any new Claude claim needs its own review. |

## Claude Code's discrepancy leads (not a verdict)

Places where transcript, source and description disagree or one claims more than another supports. Each is a lead to check, not a finding:

- Ours: the description says "fetches nothing". Only the source and an AST check support that; no runtime network monitor ran.
- Ours: the tap writes `runs/js3/transcripts/claude_code_session.jsonl`. The server itself writes nothing, but **the configured host command does write**, inside this repo. A reviewer reading only `.mcp.json` sees the tap first.
- Ours: `ping` is answered before initialize. FILTER.md's table did not decide this.
- Teaching: the description says "public"; the code cannot establish that.
- Teaching: answers any requested protocol version with `2025-11-25`.
- Teaching: its tests do not pin the order rule (the mutant above).
- Both: a `tools/call` with no id is silently dropped.

## Bounded trust decisions

**Ours, for the task "score one posting from the 2026-11-10 snapshot for the fictional persona": allow for this local scoring task.** The scripted lifecycle, source inspection, no-file-write test, recomputed fixture score, and real Claude client call support this bounded use. The configured `.mcp.json` host path writes the local transcript through the tap. The returned score is a filter output from the saved snapshot, not an application decision or evidence that the posting remains open. Re-review if server code, source bodies, tool list, host configuration, or task scope changes.

**Teaching server, for the task "look up the course fixture key `office`": allow in the isolated course-fixture test.** The inspected source contains one literal mapping and no file or network action, the controlled run produced the expected value, and the task authorizes reading that fixture. This does not establish a real-world office location or full MCP conformance. Re-review if the source, fixture, protocol version, task scope, or permissions change.
