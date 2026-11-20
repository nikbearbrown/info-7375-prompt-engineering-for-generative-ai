# tool/TEST-PREDICTIONS.md — tests for the tool server, before the server exists

Written 2026-11-20 by Claude Code, before `tool/server.py` exists. The tests
are in `tool/tests/test_server.py`. Each test checks one part of the
committed contract, `tool/TOOL-SERVER.md` (commit `f1c24dd`).

    python3 -m unittest discover -s tool/tests -v

## Prediction for the run before implementation
`tool/server.py` does not exist yet, so every test is predicted to fail or
error. No test should pass.

| Group | Predicted failure | Why |
|---|---|---|
| P, N, E, A, X | FAIL: "the server closed stdout" | `python3 tool/server.py` exits at once, with "can't open file" |
| B1 | ERROR: `FileNotFoundError` | B1 reads `server.py` to inspect its imports |
| B2–B5 | FAIL: the server closed stdout | same reason as P–X |
| B6 | ERROR: `FileNotFoundError` | B6 copies `server.py` |

The protected-file check in `tearDownModule` is predicted to pass: the tests
only read the protected files.

The actual output of this run is in `tool/test-runs/before-implementation.txt`,
unedited.

## Expected outcome once the server is implemented
Every test is expected to pass. These are the behaviors each test asserts.

### P — protocol and initialization (contract §2)
| Test | Request | Expected |
|---|---|---|
| P1 | `initialize` with `protocolVersion` "2025-11-25" | Result `protocolVersion` "2025-11-25", `capabilities` `{"tools": {"listChanged": false}}`, `serverInfo` `{"name": "js3-score-posting", "version": "1.0.0"}`, id 0 |
| P2 | `initialize` with "2024-11-05" | Result `protocolVersion` "2025-11-25" |
| P3 | `notifications/initialized`, then `ping` | No response to the notification; the ping gets `{"result": {}}` |
| P4 | `tools/list` and `tools/call` before `initialize` | Error -32600, with each request's id |
| P5 | `ping` before `initialize`, with a string id | `{"result": {}}`, id echoed |
| P6 | `tools/list` | Exactly one tool, `score_posting`, with a title, a description and an `inputSchema` (object; required `board` and `posting_id`; `additionalProperties` false; `board` enum databricks / plaid / stripe; `posting_id` a string with a pattern). No `outputSchema` or annotations |
| P7 | A request with a string id | Id echoed |
| P8 | An unknown notification (`notifications/cancelled`) | No response |
| P9 | stdin closed | The server exits with code 0 |

### N — normal calls (contract §1)
Each result has `isError` false. `structuredContent.record` equals the
posting's record in `results.json` exactly. `structuredContent.source` gives
the file, its SHA-256, run id `2026-11-17T21-47-06-167440-0500` and filter
version `v1.1`. `content` is one text item whose JSON equals
`structuredContent`.

| Test | Posting | Recorded verdict |
|---|---|---|
| N1 | databricks 6865698002 | shortlisted |
| N2 | stripe 8172508 | rejected |
| N3 | stripe 5601881 | I cannot tell |
| N4 | databricks 8843577002 and plaid 5d8abedc-018a-4b42-ae1f-0e70b34f2007 | not shortlisted; rejected |
| N5 | All 1,832 postings, one session | Each record equals `results.json` |

### E — protocol errors (contract §2 errors table)
| Test | Input | Expected |
|---|---|---|
| E1 | A line that is not valid JSON | -32700, id null |
| E2 | A batch array | -32600, id null |
| E3 | `"id": null` | -32600, id null |
| E4 | No `jsonrpc`; `"jsonrpc": "1.0"` | -32600, with the readable id (4; 5) |
| E5 | `server/discover`, `resources/list`, `prompts/list`, `tools/run` | -32601 |
| E6 | Tool `read_file`; tool `Score_Posting` | -32602; the first message is exactly "Unknown tool: read_file" |
| E7 | params is an array; `name` missing; `arguments` is an array or a string; `name` is a number | -32602 |
| E8 | A line over 64 KiB | -32600, id null; a following `ping` still works |
| E9 | A session of bad lines | Every stdout line is a JSON-RPC 2.0 response with exactly one of `result` / `error`, and there is no other stdout output |

### A — argument errors are tool execution errors (contract §2, decision 2)
Each returns a result with `isError` true, a non-empty text reason and no
traceback.

| Test | Input |
|---|---|
| A1 | No arguments; only `board`; only `posting_id`; an extra key `path` |
| A2 | `posting_id` given as a number; `board` given as a list; `board` null; `posting_id` null |
| A3 | Board `deliberate-bad-name`, `Stripe`, `STRIPE`, `greenhouse`, empty, or `" stripe"` |
| A4 | A UUID for Stripe; letters for Databricks; digits for Plaid; an uppercase UUID for Plaid; 21 digits; an empty id |
| A5 | Well-formed but unknown postings, including a real Stripe id asked for under Databricks. Text contains "unknown posting" |

### X — path tricks (contract §3)
| Test | Input | Expected |
|---|---|---|
| X1 | 13 path-like `posting_id`s: `../`, `..%2F`, absolute paths, backslashes, a NUL byte, `results.json`, `FILTER.md`, `~/.ssh/id_rsa`, leading space, newline, `file://`, and the results path itself | `isError` true; the text never contains file contents |
| X2 | Path-like boards: `../stripe`, `stripe/../../`, `/`, `.`, `..`, `runs` | `isError` true |
| X3 | Tool name `../score_posting` | -32602 (unknown tool) |

### B — declared boundaries (contract §3, §5)
| Test | Check | Expected |
|---|---|---|
| B1 | Code inspection, by AST | No imports of network, process, subprocess, `ctypes`, `shutil`, `tempfile`, `importlib`, `pickle` or similar modules. No calls to `eval`, `exec`, `compile` or `__import__`. No attributes `system`, `popen`, `exec*`, `spawnv`, `fork`, `unlink`, `rmtree`, `rename`, `chmod`, `urlopen` or `create_connection` |
| B2 | Runtime audit hook over a session with normal, path-trick, unknown-tool and malformed requests | The only events are: opens of `results.json` (read), exactly one exclusive-create open of a file in `tool/transcripts/`, an optional `mkdir` of `tool/transcripts/`, and interpreter and module loading. No socket, subprocess, exec, spawn, remove or rename events. Exit code 0 |
| B3 | Transcript contents | The server prints `transcript: <path>` on stderr. The file is in `tool/transcripts/`; each entry has `t`, `dir` and `line`; the incoming lines equal exactly what was sent, and the outgoing lines equal exactly what was received, in order |
| B4 | Oversized line in the transcript | One incoming entry with `truncated` true, the full `length` in bytes, its `sha256`, and the first 1,024 characters |
| B5 | Two simultaneous sessions | Two different transcript files |
| B6 | A copy of `server.py` next to an altered results file, in a temp directory | Non-zero exit, nothing on stdout, and stderr mentions sha256 |
| tearDownModule | SHA-256 of `results.json` (v1.1 and v1), the held-out measurement, FILTER.md, the filter code, and `audit/`, `heldout/`, `shortlist/` and `persona/`, before and after | Identical |

## What these tests do not cover
- **Server faults (-32603).** No test forces an internal error.
- **Rate limiting.** The 2025-11-25 tools page says "Servers MUST: … Rate
  limit tool invocations". The contract does not include rate limiting, so
  no test checks it. This is open for Swathi's decision.
- **Requests between `initialize` and `notifications/initialized`, or a
  second `initialize`.** The contract does not say what happens in either
  case, so no test assumes a behavior.
- **Claude Code as a client.** That is observed later, from the real
  transcript, not in this suite.
- **The tests' own transcripts.** Transcripts created by these test
  sessions are deleted by `tearDownModule`. Only files the tests themselves
  created are removed. The preserved transcripts come from the separate
  scripted-client and Claude Code sessions in §5.
