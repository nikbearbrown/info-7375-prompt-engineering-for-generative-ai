# Tool-server transcripts

Every `.jsonl` here is one row per raw stdio line: `{"ts": <UTC>, "dir": "client->server" | "server->client" | "meta", "raw": <the exact line>}`.
Scripted rows also carry `session` and `step`. A `meta` row is a note written by the recorder or the server
(start, exit). It is never a protocol line. Nothing here was edited after recording.

## Predictions (written before the first run)

| File | What it is |
|---|---|
| `EXPECTED-A.md` | predicted reply for each of the 22 steps, own server (written 2026-11-25T20:30Z, before any run) |
| `EXPECTED-C.md` | the same 22 steps, predicted for the teaching server from source alone |

## Recordings

| File(s) | Produced by | Server | Notes |
|---|---|---|---|
| `A-scripted-2026-11-26T02-23-11Z.*` | `scripts/mcp_record.py` | own (`src/jsa3/mcp_server.py`, SHA-256 in the .md) | **current A**: 22/22 steps matched the prediction |
| `A-scripted-2026-11-26T02-21-02Z.*` | same | own, the earlier revision (before the startup-error clause changed) | 22/22 |
| `A-scripted-2026-11-25T20-30-51Z.*` | same | own | first run ever, 22/22. The client put `id` last in its tools/call lines, so its bytes differ from the later runs |
| `C-teaching-server-2026-11-26T02-23-17Z.*` | `scripts/mcp_record.py --expect teaching` | `other-server/main.py --stdio` | **current C**: 22/22 matched EXPECTED-C |
| `C-teaching-server-2026-11-25T20-31-04Z.*` | same | same | first run, 22/22 |
| `C2-teaching-server-replay-of-B-2026-11-26T02-21-54Z.*` | `scripts/mcp_replay.py` | teaching server | Claude Code's 5 recorded client lines from B run 2, re-sent by a script. A replay, not a live client |
| `B-claude-code-2026-11-26T02-20-05Z.*`, `mcp-config.json` | `claude -p` by hand | own | real client, run 1. See `B-README.md` |
| `B-claude-code-2026-11-26T02-21-08Z.*` | `scripts/mcp_record_b.py` | own | real client, run 2. See `B-README.md` |

Every A, B and C run above used the JS2 development corpus
`../js2-loop-tools-diff/runs/2026-11-11T02-24-39Z-second-check`. It has no Greenhouse posting text, and no
posting is kept by filter v0.1, so the recorder fell back to the first posting (`5456619008`).

## Re-record (from the project folder `fall-2026/mayank-b/js3-filter-tool-score`)

```bash
CORPUS=runs/<id>-content          # the JS3 fetch run directory (report.json + raw/)
python3 -I scripts/mcp_record.py   --corpus "$CORPUS"                                   # A
python3 -I scripts/mcp_record_b.py --corpus "$CORPUS"                                   # B (one Claude Code request)
python3 -I scripts/mcp_record.py   --corpus "$CORPUS" --expect teaching \
    --server-cmd "python3 -I other-server/main.py --stdio"                              # C
python3 -I scripts/mcp_replay.py --from transcripts/B-claude-code-<UTC>.jsonl \
    --server-cmd "python3 -I other-server/main.py --stdio" --name C2-teaching-server-replay-of-B   # optional
python3 -I scripts/wrong_versions_mcp.py      # WF6 / M2 / M3 each fail the table; exit 0 = all caught
```

Each command writes new timestamped files and never overwrites old ones (the `.jsonl` is opened with
mode `x`). `mcp_record.py` exits 1 if any step differs from the prediction. The C run's posting id comes
from the corpus, but the teaching server answers every `score_posting` call with `-32602` whatever the id,
so its expected column does not depend on the corpus.


## Current recordings (JS3 corpus, 2026-11-25 21:26 ET)

| File | What | Result |
|---|---|---|
| `A-scripted-2026-11-26T02-26-36Z.*` | my server, scripted client | 22/22 steps as predicted in `EXPECTED-A.md` |
| `B-claude-code-2026-11-26T02-26-53Z.*` | my server, Claude Code 2.1.323 as the real client | tool called; verdict and reason repeated verbatim |
| `C-teaching-server-2026-11-26T02-26-45Z.*` | Chapter 8 teaching server, same scripted client | 22/22 steps as predicted in `EXPECTED-C.md` |

Earlier recordings in this folder were made against the JS2 corpus while the server was being built; they are kept as development history.
