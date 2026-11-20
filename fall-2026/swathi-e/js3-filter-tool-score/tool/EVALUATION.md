# tool/EVALUATION.md — evaluating the tool servers (Chapter 8)

Dated 2026-11-20. Drafted by Claude Code from committed evidence only; the
trust decision is written by Swathi Baba Eswarappa.

## 1. My own server: `js3-score-posting` (`tool/server.py`)

**Evidence used (all committed)**
- The contract: `tool/TOOL-SERVER.md`, commit `f1c24dd`. Its amendment is in
  `ff32302`, and the confirmation of the rate-limit counting in `9973987`.
- The tests and predictions: `tool/tests/test_server.py` and
  `tool/TEST-PREDICTIONS.md`, in commits `ae93c19` and `bdaf8ac`. They were
  written before the server existed and are unchanged since `bdaf8ac`.
- The server: `tool/server.py`, commit `61b314c`.
- The test runs:
  - `tool/test-runs/before-implementation-2.txt` (`bdaf8ac`): 42 tests, 40
    FAIL and 2 ERROR, because `server.py` was missing.
  - `tool/test-runs/after-implementation.txt` (`de027ed`): "Ran 42 tests …
    OK".
- The transcripts. Each was written by the server itself and committed
  unchanged.
  - **T1:** `tool/transcripts/2026-11-20T18-15-33-952083Z-9193.jsonl`, the
    scripted client's normal session (`7f1e66c`).
  - **T2:** `tool/transcripts/2026-11-20T18-15-34-001432Z-9194.jsonl`, the
    scripted client's adversarial session (`7f1e66c`). The client is
    `tool/client.py`.
  - **T3:** `tool/transcripts/2026-11-20T18-21-07-980276Z-9425.jsonl`, the
    Claude Code v2.1.308 session (`4fd59d6`).
- How lines are cited: "T2:6" means line 6 of T2, one JSON entry per line.
  Test names (P1, B2, …) refer to `tool/tests/test_server.py`.

### 1.1 Declared vs actual

| # | Declared (where) | How it was checked | Observed | Status |
|---|---|---|---|---|
| 1 | One read-only tool, `score_posting(board, posting_id)` (§1) | Tests P6, B1, B2; T1:5, T3:7 | `tools/list` returns exactly one tool, `score_posting`, with the declared input schema. B1 and B2 found no write except the transcript (row 18) | matched |
| 2 | Output is the saved v1.1 record, unchanged, plus a source naming the file, its SHA-256 and the run (§1) | Tests N1–N5. N5 compares all 1,832 postings with `results.json`, in 92 sessions; T3:9 | Every record equals `results.json`. In T3:9, `source` gives `runs/filter-v1.1-2026-11-17T21-47-06-167440-0500/results.json`, sha256 `a7f90a74…5edeff`, run `2026-11-17T21-47-06-167440-0500` and filter version `v1.1` | matched |
| 3 | The only data source is that file, SHA-256 pinned, 1,832 postings (§1) | Code scan (`server.py`: one read open, line 85); test B2 (audit hook); test N5; test B6 | B2 saw only reads of `results.json` and stdlib or module loading. N5 found 1,832 postings. B6: a copy of the server with an altered results file exits non-zero, with stderr naming sha256 and nothing on stdout | matched |
| 4 | Retrieves, does not score or fetch (§1) | Code scan (imports, `server.py` lines 20–29); tests B1 and B2 | The server imports no filter module and no network module. No network or subprocess events | matched |
| 5 | A posting changed or removed since 2026-11-17 is still answered from the saved record (§1) | Not compared with live data | — | not checked |
| 6 | A posting not in the run is "unknown" (§1, §2 errors table) | Test A5; T2:8–9 | T2:9: `"isError": true`, "unknown posting: databricks 1234567890 is not in the saved 2026-11-17 results …" | matched |
| 7 | Standard library only, no MCP SDK (§2) | Code scan (imports, `server.py` lines 20–29); test B1 | Imports are only `collections`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `re`, `sys`, `time` and `traceback` | matched |
| 8 | Newline-delimited JSON-RPC; stdout carries only MCP messages; diagnostics on stderr (§2) | Test E9; T1–T3 | E9: every stdout line is a single JSON-RPC 2.0 response. The scripted client found no extra stdout at end of input | matched |
| 9 | Version negotiation: answers `2025-11-25` whatever is requested (§2) | Tests P1, P2; T1:2, T3:4 | T3:4 answers `"protocolVersion": "2025-11-25"` | matched |
| 10 | `initialize` result: capabilities `{"tools": {"listChanged": false}}` and the declared serverInfo (§2) | Test P1; T1:2, T3:4 | Exactly as declared | matched |
| 11 | Ids: never null, repeated in responses; notifications get no response (§2) | Tests E3, P7, P3, P8; T1:3, T3:5 | A null id gets -32600. The `notifications/initialized` lines T1:3 and T3:5 have no response line | matched |
| 12 | `tools/list` and `tools/call` before `initialize` refused with -32600; `ping` answered (§2) | Tests P4, P5 | As declared | matched |
| 13 | Errors table, rows -32700, -32600, -32601 and -32602 (§2) | Tests E1–E7, X3; T2:4–5, T2:10–11, T3:1–2 | T2:5 `-32602 "Unknown tool: read_file"`. T2:11 `-32700`, id null. T3:2 `-32601 "Method not found: server/discover"` | matched |
| 14 | Errors table: argument failures are tool execution errors (`isError: true`) (§2, decision 2) | Tests A1–A4, X1, X2; T2:6–7, T3:10–11 | T2:7 and T3:11: `"isError": true`, "invalid arguments: posting_id for stripe must be a string of 1-20 digits" | matched |
| 15 | Errors table: an unexpected fault gives -32603, with no stack trace on stdout (§2) | No test forces an internal error (`TEST-PREDICTIONS.md`, "What these tests do not cover") | — | not checked |
| 16 | The argument-error design is checked against the exact 2025-11-25 tools-page wording before tests (§2) | Retrospective note, §1.1a: the local Claude Code session log of the original check, and a re-fetch of the page on 2026-11-20 | At the time, the check was made between the contract commit and the tests commit, but was not recorded in a committed file. The page puts "Input validation errors" under tool execution errors with `isError: true`, and "Unknown tools" under protocol errors. It does not say which category applies when arguments fail a tool's `inputSchema` | matched (recorded afterwards) |
| 17 | No network and no subprocesses (§3) | Code scan (imports, test B1); test B2 (audit hook) | No socket, subprocess, exec, spawn, fork or urllib/http events in B2's session | matched |
| 18 | Writes only its transcript: one new file per session, never overwritten, every line both ways with time and direction (§3) | Code scan (`server.py` line 107, mode `"x"`); tests B2, B3, B5 | B2: exactly one exclusive-create open, in `tool/transcripts/`. B3: the incoming and outgoing lines equal what was sent and received. B5: two sessions give two files. T1–T3 each have `t`, `dir` and `line` | matched |
| 19 | A line over 64 KiB refused with -32600, recorded truncated with length, SHA-256 and the first 1,024 characters (§3) | Tests E8, B4 | As declared, and a later `ping` is still answered | matched |
| 20 | Accepts only the declared boards and id formats; path tricks rejected (§3) | Tests A3, A4, X1, X2; T2:6–7, T3:10–11 | X1's 13 path-like ids and X2's 6 path-like boards all give `isError: true`, and no text contains file contents | matched |
| 21 | No sandbox is claimed (§3) | — | Nothing to observe: this is a disclosure, carried into §1.4 | not checked (disclosure) |
| 22 | Protected files unchanged (§5) | `tearDownModule` hash check in every suite run; `git diff --stat f1c24dd HEAD` over the protected paths | The `after-implementation.txt` run passed with the hash check. The git diff over `runs/`, `audit/`, `heldout/`, `shortlist/`, `persona/`, FILTER.md and the filter code shows no change | matched |
| 23 | Rate limit: at most 20 `tools/call` per second per session, then `isError` "rate limit exceeded"; recovery after the window; per session (amendment §1) | Tests R1–R3; T2:14–65 | T2:15–53: calls 1–20 of the burst served. T2:55–63: calls 21–25 get `"isError": true`, "rate limit exceeded: …". T2:65: the call after 1.1 s is served | matched |
| 24 | How the limit counts: argument-error and unknown-posting calls count; rate-limited calls and protocol errors do not (amendment §1, confirmed in `9973987`) | No test pins these details (`TEST-PREDICTIONS.md`, amendment section). The scripted client waits 1.1 s before its burst to avoid them | — | not checked |
| 25 | Served before `notifications/initialized`; a second `initialize` gets -32600 "already initialized" (amendment §2) | Tests P11, P10; T2:12–13 | T2:13: `{"code": -32600, "message": "already initialized"}` | matched |
| 26 | New run outputs and transcripts contain no absolute home-directory paths (searched for the home-directory prefix); raw transcripts preserved unchanged (amendment §3) | A search for the home-directory prefix in the committed files; `tool/privacy_scan.py` (`c4be37b`) on T1–T3; SHA-256 recorded at run time and compared with the committed blob | No match for the home-directory prefix in `before-implementation-2.txt`, `after-implementation.txt`, T1, T2 and T3. `tool/privacy_scan.py` gives 0 blocking hits on T1–T3. The transcripts' committed hashes equal their hashes at run time (reported when they were committed). The scan before each commit used an earlier, uncommitted version of the script (see §1.4) | matched |
| 27 | Claude Code compatibility observed, not assumed (§2, Known limitation) | T3 | See §1.2 | matched |

Totals: 23 matched (row 16 recorded afterwards), 0 not matched, and 4 not
checked (rows 5, 15, 21 and 24; row 21 is a disclosure, not a behavior).

### 1.1a Retrospective note on row 16 (added 2026-11-20)
- **The original check was not recorded in a committed file at the time.**
  The contract (§2) promised it "before tests are written". No committed
  file recorded that it happened.
- **The evidence that it happened is a local, uncommitted record.**
  - The Claude Code session log for this work holds a sub-agent's fetch of
    `https://modelcontextprotocol.io/specification/2025-11-25/server/tools`.
    The fetch was HTTP 200, and the "Error Handling" section was quoted
    verbatim.
  - The request was sent at 2026-11-20 15:57:14 UTC and the report
    returned at 15:57:25 UTC. That is after the contract commit (`f1c24dd`,
    15:57:10 UTC) and before the tests commit (`ae93c19`, 16:01:50 UTC).
  - The log is not part of this repository, so this row is marked
    "matched (recorded afterwards)", not "matched".
- **Verification performed now (2026-11-20), separate from the original.**
  - The same URL was fetched again (HTTP 200, `text/markdown`, no
    redirect). Its "Error Handling" section reads, verbatim:
    > 1. **Protocol Errors**: Standard JSON-RPC errors for issues like:
    >    * Unknown tools
    >    * Malformed requests (requests that fail to satisfy [CallToolRequest schema](https://modelcontextprotocol.io/specification/2025-11-25/schema.md#calltoolrequest))
    >    * Server errors
    >
    > 2. **Tool Execution Errors**: Reported in tool results with `isError: true`:
    >    * API failures
    >    * Input validation errors (e.g., date in wrong format, value out of range)
    >    * Business logic errors
    >
    > **Tool Execution Errors** contain actionable feedback that language models can use to self-correct and retry with adjusted parameters.
  - The page's example tool execution error is labeled "(input
    validation)" and returns `"isError": true`. Its example protocol error
    is `-32602` with "Unknown tool: invalid_tool_name".
  - The wording matches what was quoted in the original check.
- **What the page does not settle.**
  - It never says which category applies when `tools/call` arguments fail
    the tool's `inputSchema`, for example a missing required property.
  - "Malformed requests" refers to the `CallToolRequest` schema, not to a
    tool's `inputSchema`. "Input validation errors" is illustrated by a
    semantic check, not a schema check.
  - Treating `inputSchema` failures as tool execution errors (decision 2)
    is therefore our design choice, consistent with the "Input validation
    errors" bullet. It is not something the page requires.

### 1.2 Protocol interoperability: Claude Code v2.1.308

Observed in T3, the only server process started for the Claude Code session.

1. **Claude Code first probed with `server/discover`, offering the current
   revision** (T3:1):
   ```json
   {"jsonrpc":"2.0","id":"server-discover-probe-1","method":"server/discover","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"claude-code","title":"Claude Code","version":"2.1.308","description":"Anthropic's agentic coding tool","websiteUrl":"https://claude.com/claude-code"},"io.modelcontextprotocol/clientCapabilities":{"roots":{"listChanged":true},"elicitation":{"form":{},"url":{}},"extensions":{"io.modelcontextprotocol/tasks":{}}}}}}
   ```
2. **The server answered method-not-found** (T3:2):
   ```json
   {"jsonrpc": "2.0", "id": "server-discover-probe-1", "error": {"code": -32601, "message": "Method not found: server/discover"}}
   ```
3. **Claude Code fell back to the `initialize` handshake with `2025-11-25`**
   (T3:3):
   ```json
   {"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{"roots":{"listChanged":true},"elicitation":{"form":{},"url":{}},"extensions":{"io.modelcontextprotocol/tasks":{}}},"clientInfo":{"name":"claude-code","title":"Claude Code","version":"2.1.308","description":"Anthropic's agentic coding tool","websiteUrl":"https://claude.com/claude-code"}},"jsonrpc":"2.0","id":0}
   ```
4. **The server confirmed `2025-11-25`** (T3:4):
   ```json
   {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": "2025-11-25", "capabilities": {"tools": {"listChanged": false}}, "serverInfo": {"name": "js3-score-posting", "version": "1.0.0"}}}
   ```
5. **Then the rest of the session:**
   - `notifications/initialized` (T3:5) and `tools/list` (T3:6–7);
   - the normal call, databricks 6865698002 (T3:8–9);
   - the adversarial call, stripe `../../etc/passwd` (T3:10–11).

   There was no `ping`. Each `tools/call` carried `_meta`
   `claudecode/toolUseId` and a `progressToken`.

This matches the fallback the contract expected (§2, "In 2026-07-28 terms,
it is a 'legacy' server"). **It is one client version (Claude Code
v2.1.308), observed in one session on one day (2026-11-20).** It does not
show how other clients, other Claude Code versions or a client that speaks
only 2026-07-28 would behave. The contract's Known limitation still applies.

### 1.3 What a compatible client is NOT entitled to

- **Unrelated files.**
  - The only file input a client can influence is `board` and
    `posting_id`, and no path is built from them (`server.py` line 83 uses
    the constant `RESULTS_REL`).
  - Path tricks are rejected as argument errors before any lookup: X1 (13
    path-like ids, including `results.json`, `FILTER.md` and
    `~/.ssh/id_rsa`), X2, T2:6–7 and T3:10–11.
  - In T3, Claude Code's `../../etc/passwd` request reached the server
    (T3:10, 18:35:33.956680). The server itself returned the rejection
    (T3:11, 1.3 ms later). No file contents were returned.
  - An unknown tool name such as `read_file` is a protocol error (T2:4–5),
    so no other capability exists to call.
- **External side effects.**
  - B2 ran the server under a Python audit hook for a session of normal,
    path-trick, unknown-tool and malformed requests.
  - The hook recorded no socket, subprocess, exec, spawn, fork, remove,
    rename, chmod or truncate events. The only opens were reads of
    `results.json`, one exclusive-create transcript and module loading.
  - This was observed for B2's session only. The Claude Code session was
    not run under the hook.
- **Persistence.**
  - The server's only write is its transcript (`server.py` lines 107 and
    112; B2). It never opens a transcript for reading: B2 saw exactly one
    transcript open, in mode `"x"`.
  - Each session reloads and re-verifies `results.json` (B6), and the rate
    window is per process (R3). Nothing a client sends affects a later
    session.
- **Treating a verdict as truth.**
  - Every successful result says so in `source.note` (T3:9): "Retrieved
    from filter v1.1's saved results for the LIVE collection of 2026-11-17;
    not rescored and not current. Not confirmed fit, employment
    eligibility, sponsorship or OPT eligibility …".
  - `audit/AUDIT-REPORT.md` (`815064e`, section A) records where filter v1
    disagreed with my judgment. One of the two "not shortlisted" close calls
    was relevant (row 35).
  - `shortlist/SHORTLIST.md` (`bf15eaf`) gives all four shortlisted
    postings "needs human check" (R6 insufficient). For databricks
    6865698002, the posting returned in T3:9, that is the recommendation
    behind its "shortlisted" verdict.
- **Treating the returned claim labels as human-reviewed labels.**
  - The `claims` in a returned record are produced automatically by
    `job_filter.py`. There are four fixed claims ("role match", "asks 0-1
    years", "no sponsorship restriction", "in the US").
  - My labels in `shortlist/CLAIMS.csv` (`f4dadb2`) are a different claim
    set, one claim per rule. Their provenance is in `shortlist/SHORTLIST.md`,
    "Labeling provenance": I entered them, and the R6 and R3 changes
    followed feedback from Claude Chat and ChatGPT. So they are reviewed by
    me, not independent of AI feedback.
  - For databricks 6865698002 (T3:9):

    | Returned claim (automatic label) | My claim in CLAIMS.csv (my label) | Wording | Label |
    |---|---|---|---|
    | "role match" (supported) | R1 "Role match: title names Software Engineer, New Grad (a target role)" (supported) | differs | same; same quote |
    | "in the US" (supported) | R4 "The job is in the US: location names California, Washington" (supported) | differs | same; same quote |
    | "no sponsorship restriction" (insufficient) | R6 "The posting states no U.S. citizenship, security clearance or 'will not sponsor' requirement" (insufficient) | differs | same |
    | "asks 0-1 years" (insufficient) | — | no matching claim | not comparable |
    | — | R3 no seniority term; R5 early-career evidence; R7 Python (all supported) | not among the returned claims | not comparable |

  - Where the claims match, no label disagrees. The claim sets differ, the
    wording differs, and my R5 quote ("You will graduate in fall 2026 or
    spring 2027 …") is not the filter's R5 quote.
  - The returned record also shows rule R6 as "pass" while its own claim
    "no sponsorship restriction" is "insufficient". A rule result is not a
    claim label.
  - A client reading the tool output gets the automatic labels only. My
    labels are not served by this tool.

### 1.4 Limits of this evaluation

- **No OS sandbox.** The server runs as an ordinary process with my
  permissions (contract §3). Every boundary above is a property of the
  committed code, checked by reading and observing it. None is enforced. A
  modified `server.py` could do anything I can do.
- **The audit hook observes; it does not confine.**
  - It records only the audit events Python raises inside the server's
    process. Work done outside those events, for example by native code,
    would not be seen.
  - It covered the B2 test session only, not the scripted-client or Claude
    Code sessions.
  - The hook's watch list is fixed (`AUDIT_WRAPPER` in
    `tool/tests/test_server.py`). Events outside it are not seen.
- **Permission prompts are not in the MCP transcript.**
  - T3 contains only JSON-RPC lines. It has no record of auto mode, manual
    mode, a permission prompt or an approval.
  - What happened is my own testimony. The first call (T3:8, 18:24:11) ran
    in auto mode without a prompt. I then switched to manual mode, saw the
    permission prompt for the second call (T3:10, 18:35:33) and chose
    option 1 (Yes) for that call only.
  - The 11-minute gap between the calls fits this account but does not
    prove it.
- **One client version.** Interoperability was observed with Claude Code
  v2.1.308 in one session on 2026-11-20 (§1.2), and with my own scripted
  client.
- **Rows not checked:** 5, 15, 21 and 24 in §1.1. In particular, no
  internal fault (-32603) was forced, and the rate-limit counting details
  are not tested.
- **Privacy evidence.**
  - `tool/test-runs/before-implementation.txt` (`ae93c19`) contains
    absolute home-directory paths: 142 lines contain the home-directory
    prefix. It stays as committed, with no history rewrite, as disclosed in
    the amendment §3.
  - A first attempt at the second before-implementation run also contained
    home paths. It was not committed; its SHA-256 is recorded in
    `tool/TEST-PREDICTIONS.md`.
  - **The scans before each transcript commit** (for home paths, emails,
    phone numbers, credentials, tokens and personal data) used an
    uncommitted scratch script plus separate searches for the persona's
    name, URLs and tool-use ids. Neither that script nor its output was
    committed.
  - **The committed script** is `tool/privacy_scan.py` (`c4be37b`). It is
    a modified version of the original, not a copy:
    - identity terms are read at run time (account name, git identity,
      remote owners, persona fields, `--term`) instead of being written
      into the file;
    - the separate persona, URL and tool-use-id searches are folded in;
    - JSON validity and an exit code are added;
    - the home-directory prefix is assembled in two parts, so the file
      does not match its own check.
  - **It reproduces the earlier result.** Run on T1–T3 with
    `--term swathi`, it gives 0 blocking hits. Its informational list of
    long unbroken strings is the same as the original's.
  - **It also detects what it should.** A control file containing a
    home-directory path, an email, a phone number, a token-like string and
    identity terms gave 7 blocking hits and exit code 1.

### 1.5 Trust decision

> **TRUST DECISION (written by Swathi)**
>
> I trust this server to pull my saved job scores and filter results, though I wouldn’t rely on it on its own to decide if a job is actually right for me. Seeing all 42 tests pass—and personally testing both a valid and an invalid request in Claude Code—gave me solid confidence that it works as expected. That said, it doesn't run inside an OS-level sandbox, and I've only tested it on one version of Claude Code so far. If anything changed to let it access other files, make network calls, or perform additional write operations, I’d definitely re-evaluate it before trusting it again.
