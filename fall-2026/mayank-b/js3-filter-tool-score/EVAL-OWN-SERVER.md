# Evaluation: own tool server `jsa3-score-posting` 

**Drafted by Claude Code; the trust decision at the end is mine (Mayank Bhadrasen, 2026-11-25).**

| | |
|---|---|
| Server | `src/jsa3/mcp_server.py`, serverInfo `jsa3-score-posting` 0.1.0, one tool `score_posting` |
| Version evaluated | SHA-256 `4143fd10c80d48eddcee102e676c34bb1550ebf0fc9ae8546cfa0c8b91fd64ed` (2026-11-26T02:23Z). Transcripts A `02-21-02Z` and B (both runs) were recorded with the revision just before it, which differed only in `main()`'s startup `except` clause (it now refuses to start on *any* corpus load error, including `boards.Malformed`, where before it raised a traceback) |
| Written by | Claude Code, for Mayank, from scratch on the Python standard library (2026-11-25) |
| Evidence | `transcripts/A-scripted-2026-11-26T02-23-11Z.*` (22/22 steps matched `EXPECTED-A.md`), `transcripts/B-claude-code-*` (real client, Claude Code 2.1.323, 2 runs), `tests/test_mcp.py` (21 tests, all passing on Python 3.9.6), `scripts/wrong_versions_mcp.py` |
| Task it is evaluated for | "Score one posting of a saved JS3 corpus run with the JS3 filter so Mayank can review it." Nothing else |

Evidence types (Chapter 8): **advertised** (what the server says about itself) · **source-inspected**
(read in code) · **executed** (ran on a fixture or a real corpus, with a transcript or a test) ·
**independently sourced** · **uninspected** (not looked at; this is not the same as "none").

> **Re-recorded on the JS3 corpus, 2026-11-25 21:26 ET** (corpus run `2026-11-26T02-20-27Z-content`): `transcripts/A-scripted-2026-11-26T02-26-36Z` (22/22 steps as predicted), `transcripts/C-teaching-server-2026-11-26T02-26-45Z` (22/22), and the real client `transcripts/B-claude-code-2026-11-26T02-26-53Z` (Claude Code 2.1.323 sent `server/discover`, then `initialize`, `notifications/initialized`, `tools/list`, `tools/call`; the tool returned `keep` for posting 5183044008, and Claude repeated the verdict and reason verbatim). The observations below were first made on the development recordings against the JS2 corpus (named where cited); the re-recordings reproduced every step.

## 1. Protocol ledger: is the exchange well formed and in order?

| # | Claim | Evidence type | Where | Status | Re-review if |
|---|---|---|---|---|---|
| P1 | `tools/*` before `initialize` gets `-32000`. So does `tools/*` after `initialize` and before `notifications/initialized` | executed | A steps 1, 3; tests T3, T4 | allow | `Server.handle` or `_notification` changes |
| P2 | Only `notifications/initialized` after a successful `initialize` sets ready, never `initialize` itself (WF6) | executed | test W1: the planted `ReadyOnInitialize` fails step 3 and only step 3 | allow | same |
| P3 | Version: the server supports `2025-11-25` only, and answers `2025-11-25` to any request (asked `2024-11-05` → `2025-11-25`). No params → `-32602` | executed | A steps 17–18; T6 | allow | a new MCP protocol version, or a client that disconnects on the mismatch |
| P4 | A second `initialize` → `-32600`, and state is left as it was (no reset). This is our choice: the spec does not define re-initialization | executed | A steps 15–16; T5; planted M3 fails 15–16 | allow | if the spec defines re-initialization |
| P5 | Request error vs task error: an unknown tool or bad arguments → `-32602`. A well-formed call for an unknown or ambiguous id → a **result** with `isError: true` | executed | A steps 7–9, 13; E2, E3; planted M2 fails step 7 | allow | tool schema changes |
| P6 | `-32601` for an unknown method in every state. `-32700` with id null for an unparseable line. `-32600` for `{}`, `[]` (batch) and a null or boolean id | executed | A steps 10, 11, 21, 22; E4 | allow | — |
| P7 | A `tools/call` sent as a notification (no id) gets no reply and is **not executed**. The server says so on stderr | executed | A step 14 + its `.stderr.txt`; E5 counts filter calls (0) | allow | — |
| P8 | `ping` → `{}` in any state | executed | A step 12; T7 | allow | — |
| P9 | Interop with a real client: Claude Code 2.1.323 probed `server/discover` (`2026-07-28`), got `-32601`, then initialized at `2025-11-25` and completed list + call | executed (2 runs) | `transcripts/B-*`, `B-README.md` | allow | a Claude Code upgrade that drops the `initialize` fallback |
| P10 | Conformance beyond this subset: `_meta`/progress, cancellation, `notifications/cancelled`, `resources`, `prompts`, large lines | uninspected / not implemented | — | pending | before any second client is used |

## 2. Capability ledger: does the code do what the listing says?

| # | Claim | Evidence type | Where | Status | Re-review if |
|---|---|---|---|---|---|
| C1 | Exactly one tool, `score_posting`, and the dispatch accepts only that name | advertised + source-inspected + executed | A step 5; `_call`; A step 9 (`apply_to_job` → `-32602`) | allow | a new tool is added |
| C2 | No network: the server and everything it imports (`jsa3.filter`, `jsa3.corpus`, `jsa.boards`) import no `jsa.net`, `socket`, `ssl`, `http*`, `urllib.request`, `subprocess` or `asyncio`. `jsa.boards` imports `urllib.parse`, which only parses strings | source-inspected (AST scan, N1) + executed (N3: `python3 -X importtime` lists every module the real server process loaded during a session, and none is a network module) | `tests/test_mcp.py` N1–N3 | allow | any import changes in these four files |
| C3 | Writes nothing, except the optional `--log` file, which must resolve inside `transcripts/` (it appends and never truncates) | source-inspected (the only `open(` for writing is `Log`) + executed (B1 refuses `/tmp`, `..` and `src/` paths and creates no file; B2) | tests B1, B2 | allow | a new `open`/`write` |
| C3b | The interpreter writes no bytecode when run as configured: under `python3 -I`, `sys.flags.dont_write_bytecode` was 1 on this Mac. **Without `-I`**, Apple's python3 has `pycache_prefix=~/Library/Caches/com.apple.python`, which is outside this folder | executed (one-line check, 2026-11-26) | — | allow with `-I` only | the launch command changes |
| C3c | OS-level file and network activity of the real process (fs_usage/dtruss, a sandbox profile) | **uninspected** | — | pending | before connecting to anything but a local corpus |
| C4 | Reads: `--corpus <dir>/report.json`, the raw files it names (SHA-256 checked) and `--config` | source-inspected | `jsa3/corpus.py` | allow, with one finding ↓ | corpus.py changes |
| C4-finding | `corpus.load` opens `run_dir / att["raw"]` with no containment check, so a tampered `report.json` (an absolute path or `../`) could make the server **read** a file outside the run folder. The SHA-256 check only shows the bytes match the trace, and the trace is in the same file. The read is never returned unless it parses as a job board | source-inspected, not executed | `src/jsa3/corpus.py` line ~32 | pending (fix: reject a raw path that resolves outside `run_dir`) | when fixed |
| C5 | The returned record is `filter.evaluate(posting, config)` with nothing added or changed, plus a `source` block (corpus run, board, raw file, raw SHA-256, filter version, config SHA-256) | executed | A `.md`: "client-side recomputation: identical"; test E1 | allow | filter.py changes |
| C6 | The corpus and config are loaded once at startup. Edits on disk afterwards are not seen until restart | source-inspected | `main()` | allow | — |
| C7 | Tool annotations `readOnlyHint: true`, `openWorldHint: false`, `destructiveHint: false`, `idempotentHint: true` | advertised (consistent with C2/C3, which are the actual evidence) | `TOOL` | allow | — |

## 3. Permission ledger: does this task allow that capability?

| # | Claim | Evidence type | Where | Status | Re-review if |
|---|---|---|---|---|---|
| R1 | Brief: "must not expose anything that can send or change data outside your own folder." Nothing is sent (C2), and the only possible write is inside `transcripts/` (C3) | source-inspected + executed | C2, C3 | allow | — |
| R2 | The agent never applies, emails, messages or logs in. The server has no tool that could, and a call to `apply_to_job` is refused | source-inspected + executed | A step 9 | allow | a new tool |
| R3 | The host grants only `mcp__jsa3__score_posting`. Claude Code's built-in tools were disabled (`--tools ""`, `--strict-mcp-config`), and the client output shows `permission_denials: []` | executed | B command + client output | allow | the host command changes |
| R4 | The data: public job-board postings that the JS2/JS3 loop already saved, plus a fictional persona. Whether Claude may read posting text is a data-owner and course-policy question. It is not something the server can settle | — (a human decision) | — | **pending: Mayank** | a corpus with non-public data |
| R5 | The tool reads whatever `--corpus` and `--config` the host config names. The host config, not the server, bounds the read scope | source-inspected | `main()` | allow, while the config points inside this repo | the config changes |

## 4. Evidence ledger: does the returned content support the claim built on it?

| # | Claim | Evidence type | Where | Status | Re-review if |
|---|---|---|---|---|---|
| E1 | The verdict and reason Claude reported equal the bytes the server returned | compared (mechanical `in` string test) | B run 1 and run 2: True / True | allow | — |
| E2 | Claude's answer also contained sentences **the tool never returned**. Run 1: "Your latest commits mention a filter v1.0 run on the live collection". Run 2: "not your CP3 fetch with `content=true`… due tonight at 11:59 PM". They came from Claude Code's session context (the repo, git), not the server | compared (log vs answer) | `B-*.jsonl` vs `B-*.client-output.json` | **deny** as evidence for anything | — |
| E3 | A record is the filter v0.1 judgment on one saved snapshot. Whether the verdict is *right* about the job is settled by Mayank's audit sheet, not by this server | — | `FILTER.md`, audit | pending (audit) | a new corpus or filter version |
| E4 | Provenance: `source.raw_sha256` matches the trace in `report.json` | executed (fixture: E1; real corpus: the A record is identical to the recomputation) | — | allow | a new corpus |
| E5 | Snippets in `topic_hits` are posting text from public boards: **untrusted data** that goes into Claude's context. The tool description says so. No injection test was run through the real client | advertised + source-inspected; behaviour under injection **uninspected** | `TOOL.description` | pending | before using a corpus from a board not on the allow-list |

## Declared vs actual

| Declared (tools/list, serverInfo, instructions) | Actual (evidence) | Match? |
|---|---|---|
| "Read-only" | writes only the opt-in `--log`, inside `transcripts/` (C3, tests B1/B2). Without `-I`, the interpreter may write `.pyc` outside the folder (C3b) | yes, under the configured command |
| "offline", `openWorldHint: false` | no network module loaded in the real process (N3) or imported in source (N1). OS-level check uninspected (C3c) | yes, as far as was checked |
| "looks up one posting by id in a corpus fetched earlier and saved to disk" | `corpus.load` + `by_id`, SHA-256 checked. Can read outside the run dir if `report.json` is tampered (C4-finding) | yes, with a gap |
| returns "the filter's record: verdict, reason, matched words with snippets, score" | record identical to `filter.evaluate` (C5), plus a `source` block not mentioned in the description | yes (more than declared: `source`) |
| "cannot apply, email, message or log in anywhere" | no such code path (C1, R2) | yes |
| inputSchema `{"posting_id": string}`, `additionalProperties: false` | enforced: a wrong type, an extra key, a missing key or a list → `-32602` (E3 test) | yes |
| protocolVersion `2025-11-25` | the only version it answers. It does not implement `server/discover` (answers `-32601`) | yes |

## What a compatible client is NOT entitled to

- **"Read-only" and "offline" are the server's testimony.** A client sees only the tool description and the annotations. C2 and C3 come from source and tests in *this* folder, at *this* SHA-256, so any other copy or revision has to be checked again.
- **A result is not a fact about the job.** `keep` / `reject` / `cannot_tell` is filter v0.1 applied to one snapshot. `cannot_tell` here means the saved snapshot had no text. It says nothing about whether the job has a description.
- **`isError: false` means the lookup ran, not that the verdict is correct.** `isError: true` means the id was not in this corpus run, not that the posting does not exist.
- **Protocol compliance is not safety.** 22/22 matched steps say the exchange is well formed. They say nothing about data scope (R4) or about the content (E3, E5).
- **A matching id associates a reply with a request. It does not make the reply trustworthy.**
- **Posting snippets are not instructions.** They are third-party text.
- **Claude's fluent restatement adds no evidence** (E2). Anything in Claude's answer that is not in the server log has no provenance from this tool.
- **One host, two runs.** Interop with other clients, and Claude Code's handling of error replies, was not checked.

## Handoff analysis (Chapter 8)

| Server output | Host inference | Evidence for the inference | Next component's allowed use |
|---|---|---|---|
| `verdict: cannot_tell, reason: cannot tell: no posting text` for 5456619008 | "the filter could not judge this posting from the saved corpus" | the record equals the recomputation from the raw file at the logged SHA-256 (A step 6) | quote it as the filter's output for that run. It must not be stated as a fact about the job |
| (none: Claude's extra sentences about commits / CP3 / the deadline) | — | none from this server | must stop before use. Check against the repo itself if needed |

## Recommendation (Claude Code's, not a decision)

**Allow, bounded**: for the task above, server SHA-256 `4143fd10…64ed`, launched as
`python3 -I src/jsa3/mcp_server.py --corpus <a run dir in this repo>`, with Claude Code limited to
`mcp__jsa3__score_posting` and built-in tools off. Two conditions: (1) the C4 finding (a raw path in `report.json` could point outside the run folder) was **fixed on 2026-11-25 in JS3-CP10**: `corpus.load()` now refuses it, tested by `tests/test_sheets.py` `CorpusPaths`; (2) R4 is Mayank's call.
Re-review if a tool is added, any of the four imported files changes, the launch command loses `-I`,
the corpus or filter version changes, or the client changes.

## Sign-off

```text
Sign-off — MCP evaluation packet, own server
Checked:      P1–P9 executed; C1–C3, C5 source-inspected + executed; C4 source-inspected; E1, E2 compared
How:          tests written before the recordings (EXPECTED-A.md first), scripted client, real client (Claude Code),
              source comparison; drafted with Claude Code (which also wrote the server)
Not checked:  OS-level file/network activity (C3c); prompt injection through posting text (E5); client handling of
              error replies; other clients; whether any verdict is true about the job (E3)
Not claiming: that the server is secure, MCP-conformant, or fit beyond this task and this version
Decision:     allow for task "score one saved posting for Mayank's review", server SHA-256 4143fd10…64ed
Re-review if: new tool / import change / launch command change / new corpus or filter version / new client
```

**Decision (Mayank): allow, bounded (2026-11-25).**

Allow, 2026-11-25, for one task only: scoring a saved posting for my review, with the server launched with `-I` and Claude Code limited to `score_posting`. I checked what it does by running it (transcripts A and B), not by trusting its description. If anything in the re-review list changes, it goes back to pending.

Signed: Mayank Bhadrasen, 2026-11-25
