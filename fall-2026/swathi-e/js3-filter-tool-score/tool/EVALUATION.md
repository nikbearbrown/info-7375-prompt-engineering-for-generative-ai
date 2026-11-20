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

## 2. External server: `@modelcontextprotocol/server-filesystem` 2.4.0 (code reading only)

Dated 2026-11-20. Drafted by Claude Code. **This is a code-reading
evaluation, not an observation:** the package was downloaded and read, but
never installed, run, connected to a client or given a directory. No
protocol transcript of this server exists. Contract §6 allowed this
fallback, "clearly labeled as code-reading, not observation".

How package files are cited: `dist/server.js:262` means line 262 of that
file in the published 2.4.0 tarball. These are the compiled JavaScript files
that would run. The TypeScript source in the GitHub repository was not read.

### 2.1 Version selection

- **Evaluated: 2.4.0.** The npm registry gives its publish time as
  2026-11-18T09:19:39.880Z, and the `latest` dist-tag pointed to 2.4.0 on
  2026-11-20 (`npm view … time`, `npm view … dist-tags`).
- **How the version was chosen (provenance).**
  1. **Claude Chat** first recommended 2.2.0, based on release age: the
     newest release at least two weeks old. 2.2.0 was published
     2026-11-04T21:36:25.362Z, 16 days before this evaluation. 2.3.0
     (2026-11-11) and 2.4.0 (2026-11-18) were newer than two weeks.
  2. **ChatGPT** identified security advisory GHSA-7m4x-rv66-mxhh, which
     affects 2.2.0.
  3. **Claude Chat** independently checked the advisory and revised its
     recommendation.
  4. **Swathi** approved version 2.4.0 and the code-reading approach.

  These steps took place outside this Claude Code session. Claude Code
  verified the advisory and the release information below on 2026-11-20,
  after the version was chosen.
- **Why the age-based recommendation of 2.2.0 was rejected.**
  - **Advisory GHSA-7m4x-rv66-mxhh** (repository advisory, state
    "published", published 2026-11-11T07:24:37Z, read on 2026-11-20 through
    `https://api.github.com/repos/modelcontextprotocol/servers/security-advisories/GHSA-7m4x-rv66-mxhh`;
    page `https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-7m4x-rv66-mxhh`):
    - Summary: "server-filesystem: `move_file`'s same-device rename leaves
      the source unpinned — a swapped source parent moves an outside file
      into the allowed directories, where it becomes readable".
    - Severity medium, CVSS 3.1 score 5.0
      (`AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N`), CWE-367 (time-of-check
      time-of-use race).
    - Affected: npm `@modelcontextprotocol/server-filesystem` "< 2.3.0",
      patched in "2.3.0". The date-versioned releases ">= 2025.1.14,
      <= 2026.8.31" are also affected, with no patched version.
    - The reporter's "Confirmed version: v2.2.0". The advisory quotes the
      vulnerable 2.2.0 code: `renameIntoDirectory` called
      `fs.renameSync(sourcePath, path.basename(destinationPath))` with the
      source as an absolute path that "the kernel resolves at rename time —
      after validation".
    - The global advisory database (`/advisories/GHSA-7m4x-rv66-mxhh`) and
      OSV returned 404 on 2026-11-20. The npm bulk advisory endpoint
      returned no advisories for 2.2.0, 2.3.0 or 2.4.0. The repository
      advisory above is therefore the source.
  - **So 2.2.0 is affected by a published advisory**, and an age rule alone
    would have chosen a known-vulnerable version.
- **Release information** (GitHub releases API, read on 2026-11-20). The
  repository's release tags are monorepo versions, not package versions.
  - Release `v2.4.0` (2026-11-11T07:07:16Z) ships filesystem **2.3.0**. It
    lists the GHSA-7m4x-rv66-mxhh fix ("`move_file` moves only the source it
    checked") and GHSA-p9cv-8g75-4xcg (reads anchored to the checked
    directory).
  - Release `v2.5.0` (2026-11-18T09:13:14Z) ships filesystem **2.4.0**. Its
    table says filesystem is affected in "all versions before 2.4.0, and
    date versions 2025.1.14 through 2026.8.31", fixed in 2.4.0. The fix is
    GHSA-rq2p-q7c4-6g27: directory listings stay with the checked
    directory. It adds: "**On Windows a listing is not yet anchored**
    (#5600)".
  - So 2.3.0 also had a fix that only 2.4.0 includes. This evaluation did
    not read GHSA-p9cv-8g75-4xcg or GHSA-rq2p-q7c4-6g27 themselves, only the
    release notes that cite them.
- **Node.js requirement.** 2.4.0 declares `"engines": {"node": ">=24"}`
  (`package.json`; README "Requirements": "Node.js 24 or later"). The
  installed Node.js here is v23.4.0, with npm 10.9.2.
- **No `gitHead`.** `npm view @modelcontextprotocol/server-filesystem@2.4.0
  gitHead` returned nothing. The registry metadata does not name the source
  commit (see row S2 below for the provenance attestation).
- **Why code reading, not a downgrade or a new environment.**
  - Running 2.4.0 needs Node.js 24 or later. Swathi chose not to upgrade
    Node.js or otherwise change the local environment for this evaluation.
    Running it would also mean installing the package's dependencies and
    executing package code, which this code-reading approach avoids.
  - Downgrading to a version that runs on Node 23 would mean evaluating an
    older release than the patched one. 2.2.0 is known-vulnerable
    (GHSA-7m4x-rv66-mxhh), and older 2.x releases precede further fixes.
  - Code reading evaluates the exact published 2.4.0 files, with no change
    to the machine. Its limits are stated in §2.5.

### 2.2 Obtaining the exact published package

All commands were run on 2026-11-20 from a throwaway directory outside the
repository, `/tmp/fs-eval.7UEKGk`. It was created with `mktemp -d
/tmp/fs-eval.XXXXXX`, and its path holds no username.

```bash
npm view @modelcontextprotocol/server-filesystem@2.4.0 name version time dist engines dependencies gitHead repository bin --json
cd /tmp/fs-eval.7UEKGk
npm pack --ignore-scripts --cache /tmp/fs-eval.7UEKGk/npm-cache @modelcontextprotocol/server-filesystem@2.4.0
echo "sha512-$(openssl dgst -sha512 -binary modelcontextprotocol-server-filesystem-2.4.0.tgz | base64)"
```

- **The npm cache was kept inside the throwaway directory** (`--cache`), so
  nothing was written to the home-directory npm cache.
- **The registry metadata:**
  - `dist.integrity`
    `sha512-BoT8Gws5MsetfAey4vDyuzy8WYQES6mGYLSShuqSNGAC0X0NBV4p78/R78KfW4RkxtWz+zxhS9jwhzJrQUTt2Q==`;
  - `dist.shasum` `172f7d8fcd0d85205db041291a47f05bb2042d92`;
  - `fileCount` 14 and `unpackedSize` 227330;
  - `repository` `git+https://github.com/modelcontextprotocol/servers.git`;
  - `bin` `mcp-server-filesystem` → `dist/index.js`.
- **Integrity verification: passed.**
  - The computed SHA-512 of the tarball is
    `sha512-BoT8Gws5MsetfAey4vDyuzy8WYQES6mGYLSShuqSNGAC0X0NBV4p78/R78KfW4RkxtWz+zxhS9jwhzJrQUTt2Q==`,
    identical to the registry value and to the value Swathi gave.
  - The SHA-1 is `172f7d8f…2d92`, equal to `dist.shasum`. The SHA-256 is
    `a785e3dadbf58a5fce6fbb006b883c925772c254e880da4866a4c418fc746e3f`.
- **The archive was inspected before extraction.** Python's `tarfile` was
  run with `-I` from a script outside the archive.
  - It has 14 members, all regular files under `package/`: `package.json`,
    `README.md` and 12 files in `dist/`.
  - There are no symlinks, hard links or device entries, no absolute paths
    and no `..` components.
  - It was then extracted with `tar -xzf … --no-same-owner` into a
    subdirectory, and `find -type l` found 0 links.
- **Inspected files (SHA-256 of each extracted file):**

  | File | Lines | SHA-256 |
  |---|---:|---|
  | `package.json` | — | `4d524b3d5ba59990c1396cdbcea5e54b10aceacb6e8bebe886bd45f27831d43f` |
  | `README.md` | — | `7314bb305332a61ae6b2fe997cec775d5cc1daf6456e62d63e27a0d975293e81` |
  | `dist/index.js` | 268 | `4e7e0c6e39fa416d9368ff0d0a4b9c2d5351be30c76e6e45eced03394b6ede31` |
  | `dist/server.js` | 916 | `531a121b9c3eef3d0651cb71d3447b3b42ccd928450095637dfa0ad99a042807` |
  | `dist/lib.js` | 1006 | `986bd4ecc96be578102ae5ce4ec695e6a5a99dfa1e347ae2dda58f7b1bc8191c` |
  | `dist/pinned-directory.js` | 856 | `b98cd3a2fc747616608eb396437e4727119904d99ed00991a467dfaf22c5ecff` |
  | `dist/path-validation.js` | 181 | `8526d7e173165c71503cd3c533c8ef1ed97ec01ce8589a61e6c8f25ed87de537` |
  | `dist/path-utils.js` | 150 | `d7effde9b096a332dd1e531a8dc47e65117cf5bf387ee937aaba71b5f649b2d2` |
  | `dist/allowed-directories.js` | 61 | `aba75864d20452b0f08e63e1a3e193eecd814bc66a3ddfffef9e756ec3f6e8a0` |
  | `dist/roots-utils.js` | 83 | `47a44576958fbfba80419e3dffd5db1d6e48d85ad0cd810f060fbcf932a28124` |
  | `dist/read-only-directories.js` | 109 | `86298eafe35cc6e21e6ae82259512c0d228043c934a08963f8561dc4119a57df` |
  | `dist/file-resources.js` | 189 | `60e2787929d8c67ebd5e849be7bc0f8e31bdaa536df66202f2d0620b3f6672b7` |
  | `dist/http.js` | 86 | `f4b5488baa8bb049e56bddee3fefc9af02d7f2552ffc2e0b6379df8ab19d2719` |
  | `dist/version.js` | 35 | `044a3819acfb25e8038eb742845502eb255fa719aaa158b4befad5a58a44854d` |

  Not every line of every file was read. The cited lines and the functions
  they belong to were read. Elsewhere the reading was targeted searches
  (for example, every `validatePath` call site, and imports of `http`,
  `child_process` and `process.env`).
- **Not done:** no `npm install`, no dependency download, no Node.js
  upgrade, no execution of package code, and no Claude Code registration.

### 2.3 Declared vs actual (by code inspection)

Statuses: **matched by code inspection** (the code does what is declared, as
far as reading shows), **not matched by code inspection**, and **not
verifiable by code reading**. A "matched" row is a statement about the code
as read, not proof of runtime behavior.

**Tools, schemas and annotations**

| # | Declared | Code evidence | Finding | Status |
|---|---|---|---|---|
| T1 | 16 tools (README "Tools", lines 151–350, and the annotations table, lines 385–402) | `dist/server.js:262–790`: `read_file` (deprecated alias), `read_text_file`, `read_media_file`, `read_multiple_files`, `write_file`, `append_file`, `edit_file`, `create_directory`, `list_directory`, `list_directory_with_sizes`, `directory_tree`, `move_file`, `copy_file`, `search_files`, `get_file_info`, `list_allowed_directories` | The same 16 tools are registered. There is also one resource template, `file://{+path}` (`dist/file-resources.js:124–189`) | matched by code inspection |
| T2 | Annotations: 10 read tools `readOnlyHint: true`; write tools as in the README table (lines 385–402) | Annotation blocks at `dist/server.js:267–272, 285–290, 316–321, 371–376, 402–407, 425–430, 454–459, 476–481, 500–505, 526–531, 607–612, 659–664, 684–689, 709–714, 748–753, 773–778` | Every value matches the table. For example, `move_file` has `readOnlyHint: false`, `destructiveHint: true` (`:659–664`), and `write_file` has `destructiveHint: true` (`:402–407`) | matched by code inspection |
| T3 | Input schemas: path arguments are strings, described as "Absolute, or relative to an allowed directory; it must resolve inside the allowed directories" | `dist/server.js:33–147` (zod schemas); `PATH_RULE` at `:33` | Most path arguments carry the rule. `copy_file`'s `source` and `destination` (`:125–130`) and `read_multiple_files`' `paths` (`:57–62`) do not, though their handlers validate them the same way (`:691–692`, `:380`). The JSON Schema sent to clients is produced by the SDK from these zod objects, so its exact form (for example, whether extra properties are refused) cannot be read here | not verifiable by code reading (the rendering is in the SDK) |
| T4 | `--read-only` serves only tools annotated `readOnlyHint: true` (README line 41) | `dist/server.js:229–237`: a tool without `readOnlyHint === true` is removed after registration | As declared. The annotation is used here as an enforcement key inside the server, not as a promise to the client | matched by code inspection |

**Read, write and move capabilities**

| # | Declared | Code evidence | Finding | Status |
|---|---|---|---|---|
| C1 | Reads: content, media, several files, listings, tree, name search, metadata, allowed-directory list, file resources | `validatePath(…, "read")` at `dist/server.js:241, 323, 380, 507, 533, 542, 619, 716, 755`; `dist/lib.js:987`; `dist/file-resources.js:154` | Every read path goes through `validatePath`. `list_allowed_directories` (`dist/server.js:779–789`) returns the allowed and read-only directory paths themselves | matched by code inspection |
| C2 | Writes: create or overwrite (`write_file`), append, edit, `create_directory`, `copy_file` (never overwrites) | `validatePath(…, "write", readOnlyDirectories)` at `dist/server.js:409, 432, 461, 483, 692`; `dist/lib.js:417–432` (exclusive create, then overwrite in place); `dist/lib.js:534–546` (copy refuses an existing destination) | `write_file` overwrites an existing file without confirmation, as its description says ("overwrite existing files without warning", `dist/server.js:397–399`) | matched by code inspection |
| C3 | Move: "Both source and destination must be within allowed directories"; fails if the destination exists | `dist/server.js:665–668` (both validated in "move" mode); `dist/lib.js:499–526` (`lstat` the destination, refuse if anything is there) | As declared. A move removes the source from its original place | matched by code inspection |
| C4 | Read-only directories (`--read-only-dir`) refuse writes and moves, even through a symlink, and Roots never lift them (README lines 47–59) | `dist/lib.js:331–337` (`assertWritable` on the resolved path for every non-read access); `dist/read-only-directories.js:90–102` (write and move checks); `:38–54` (startup refuses an unresolvable marking) | As declared | matched by code inspection |

**Allowed directories, Roots and path validation**

| # | Declared | Code evidence | Finding | Status |
|---|---|---|---|---|
| A1 | The server may touch only its allowed directories, given on the command line (README lines 17–19) | `dist/index.js:29–84` (each directory resolved, both spellings kept, missing ones dropped with a warning); `dist/index.js:187–203` | As declared for the command line | matched by code inspection |
| A2 | Containment check on a separator boundary, null bytes refused | `dist/path-validation.js:94–181`; null byte `:104`; boundary `:171–179`; Windows-only refusals `:116–124` | A sibling such as `/allowed-evil` does not match `/allowed`. The check compares strings after `path.resolve`, and symlinks are handled separately (A4) | matched by code inspection |
| A3 | Relative paths resolve against an allowed directory | `dist/lib.js:128–145`; with no allowed directories, the fallback is `process.cwd()` (`:129–132`) | The fallback result is still checked against the allow-list (`dist/lib.js:352–365`), so with none it is refused | matched by code inspection |
| A4 | Symlinks: a path is resolved to its real location and checked; a symlink leaving the allowed directories is refused (README lines 86, 128) | `dist/lib.js:366–375` (`realpath`, then re-check); `:376–391` and `:266–330` (for a path that does not exist yet, each existing component is realpath'd and checked) | As declared, at check time. Use-time protection is A6 | matched by code inspection |
| A5 | **Client-provided Roots replace the command-line directories** on a 2025-era connection unless `--confine-roots` is given (README lines 64–84: "Roots notified by Client to Server, completely replace any server-side Allowed directories when provided") | `dist/server.js:802–822` (`allowedDirectories = [...validatedRootDirs]`); `:835–848` and `dist/allowed-directories.js:47–61` (`--confine-roots` keeps only the overlap); `dist/roots-utils.js:59–83` (any existing directory named by a root is accepted) | As declared. **Without `--confine-roots`, a 2025-era client can widen access to any directory it names as a Root**, not only narrow it | matched by code inspection |
| A6 | Use-time anchoring on Linux and macOS: every write, every content or metadata read and every listing acts from inside the checked directory (README line 128) | `dist/pinned-directory.js:1–45` (design), `:166–207` (`chdir`, then `getcwd` check), `:214–233` (open relative to the anchor, identity check), `:840–856` (listing reads `.` inside the anchor); `dist/lib.js:88–93` | The mechanism is present as described. Whether it closes every race at run time cannot be shown by reading | matched by code inspection (runtime not verified) |
| A7 | Windows limit: a parent directory swapped during an operation is not protected (README lines 131–134); listings not anchored there (release v2.5.0, #5600) | `dist/pinned-directory.js:38–45`; `:144–148` (the `getcwd` check is skipped on Windows) | A disclosed gap, present as disclosed | matched by code inspection (disclosed limitation) |
| A8 | Hard links: checks are path-based, so editing a file hard-linked from outside changes it there too (README lines 190–197) | `dist/lib.js:459–465` (`overwriteInPlace` checks the type and identity of the file, not its link count); `dist/lib.js:409–411` (`hardLinks` reported by `get_file_info`) | A disclosed gap, present as disclosed: content outside the allowed directories can change through a hard link inside them | matched by code inspection (disclosed limitation) |

**The advisory fix, network and dependencies**

| # | Declared | Code evidence | Finding | Status |
|---|---|---|---|---|
| G1 | GHSA-7m4x-rv66-mxhh fixed in 2.3.0 and later: "A move within one device first takes the source out of its own checked directory under a fresh name" (release `v2.4.0` notes) | `dist/pinned-directory.js:338–442` (`renameIntoDirectory`). Step 1, anchored in the source's directory, renames the source to a random name (`:363–371`, `stagingName` at `:304–306`). Step 2, anchored in the destination's directory, moves it and checks it by inode and device (`:375–393`). On failure it puts the source back (`:398–441`). `dist/lib.js:499–520` calls it | **The fix is present in the published 2.4.0 code.** The source is no longer passed to `fs.renameSync` as an absolute path from the destination's anchor, as in the 2.2.0 code quoted by the advisory. The cross-device path pins the source through `openSourceInDirectory` (`dist/pinned-directory.js:516–546`, `:650–671`) | matched by code inspection (no race was run) |
| G2 | GHSA-rq2p-q7c4-6g27 (2.4.0): listings stay with the checked directory on Linux and macOS | `dist/lib.js:88–93` (`listValidatedDirectory` returns `readDirectoryInPlace`); `dist/pinned-directory.js:840–856` | Present as described. The advisory itself was not read, only the release note | matched by code inspection |
| N1 | No network over stdio; Streamable HTTP only when chosen, bound to loopback by default (README lines 410–435) | `dist/index.js:156–179` (HTTP only with `--transport streamable-http`); `dist/http.js:17, 21, 27–36, 47–72` (`node:http`, default host `127.0.0.1`, widened by the `HOST` environment variable); no `child_process`, `net` or `fetch` in the 12 `dist/` files (search) | Within the package files, as declared. The SDK dependencies that handle the protocol and stdio were not read | matched by code inspection (package files only) |
| S1 | Dependencies (`package.json`) | `@modelcontextprotocol/server` ^2.3.1, `@modelcontextprotocol/node` ^2.1.1, `zod` ^4.2.0, `diff` ^8.0.3, `minimatch` ^11.0.4. The devDependencies are not shipped | **None of these was downloaded or read.** They include the code that parses JSON-RPC, applies the input schemas, chooses the protocol era (`serveStdio`) and sends `roots/list`. Version ranges (`^`) mean an install could resolve different versions over time. Node.js built-ins used (`fs`, `path`, `crypto`, `node:http` and others) were not audited either | not verifiable by code reading |
| S2 | Source of the published files | `gitHead` absent. The npm provenance attestation (`https://registry.npmjs.org/-/npm/v1/attestations/@modelcontextprotocol%2fserver-filesystem@2.4.0`) has a subject SHA-512 equal to the tarball's, and names workflow `.github/workflows/release.yml` at `refs/tags/v2.5.0`, commit `c799c8552b0f27b7a33a7b9233773da144dddcf5` | The attestation's signature was not verified, and the GitHub source at that commit was not compared with `dist/` | not verifiable by code reading |
| P1 | Protocol: both eras on stdio (2026-07-28 `server/discover`, and 2025-era `initialize` then Roots) | `dist/index.js:5–8, 195–213` (`serveStdio` from the SDK); `dist/server.js:868–914` (Roots only after a 2025-era `initialize`) | The era choice and message handling are in the SDK (S1) | not verifiable by code reading |

Totals: 22 rows. 18 matched by code inspection, 0 not matched by code
inspection, and 4 not verifiable by code reading (T3, S1, S2 and P1).
- A7 and A8 are disclosed limitations, present as disclosed.
- A6, G1 and N1 carry the qualifiers shown in their rows. Their runtime
  side is a limit of this evaluation (§2.5).

### 2.4 What a compatible client is NOT entitled to

- **Access outside the authorized directories.**
  - Every tool and the file resource validate their paths against the
    allowed directories, with symlinks resolved (C1–C3, A2–A4).
  - **But the authorized set is not fixed by the operator alone.** On a
    2025-era connection, without `--confine-roots`, the client's Roots
    replace the command-line directories (A5). Connecting does not entitle
    a client to choose its own scope; the operator should start the server
    with `--confine-roots`, or treat Roots as client-controlled.
  - **Hard links reach outside by design** (A8): content outside the
    allowed directories can change through a hard-linked name inside them.
- **Unrestricted write or move operations.**
  - The write tools overwrite (`write_file`), edit, append, create
    directories, copy, and move (which deletes the source), all inside the
    allowed directories (C2, C3).
  - `--read-only` and `--read-only-dir` narrow this (T4, C4), but only if
    the operator starts the server with them. A default start allows every
    write tool everywhere in the allowed directories.
  - Nothing in the code asks for confirmation. The MCP tools page leaves
    that to the client ("Clients **SHOULD**: Prompt for user confirmation
    on sensitive operations"), and in my own session that was Claude Code's
    permission prompt (§1.4).
- **Assuming tool declarations or annotations guarantee safe behavior.**
  - The annotations in 2.4.0 match the README table (T2). They are still
    hints: the 2025-11-25 tools page says clients "MUST consider tool
    annotations to be untrusted unless they come from trusted servers"
    (contract §2).
  - The match was established here by reading one published version. A
    different version, or a modified copy, could declare one thing and do
    another. This server uses `readOnlyHint` itself for `--read-only`
    (T4), so a wrong annotation there would also weaken that mode.
- **Assuming the allowed-directory restriction is OS-level sandboxing.**
  - The restriction is the server's own code checking paths (A2–A6). The
    process runs with the permissions of whoever starts it.
  - The README's "sandboxed directories" wording (lines 441, 528) refers to
    Docker mounts, which this evaluation did not use.
  - On Windows, the use-time anchoring is explicitly not in place (A7).

### 2.5 Limits of this evaluation

- **No runtime execution and no protocol transcript.** The server was never
  started. Nothing in §2.3 was observed, and there is no counterpart to the
  T1–T3 transcripts of Section 1.
- **Code inspection only, and partial.** The compiled `dist/` files of one
  published version were read, at the cited lines and through targeted
  searches, not exhaustively. Reading is not proof of runtime security. In
  particular, the anchoring (A6) and the advisory fix (G1) were not tested
  against a real race.
- **Dependencies not independently audited** (S1). The SDK packages that
  parse messages, enforce schemas and run the stdio transport were not
  downloaded or read. Neither were `zod`, `diff`, `minimatch` or the
  Node.js built-ins.
- **No proof of security under concurrent filesystem changes.** The
  advisories fixed in 2.3.0 and 2.4.0 were all time-of-check/time-of-use
  races. The code's own comments (`dist/pinned-directory.js:1–45`) and the
  README (lines 128–134) describe the remaining Windows gap. Reading cannot
  show that no other race remains on Linux or macOS.
- **Integrity verification is not trustworthiness.** The SHA-512 match shows
  that the downloaded tarball is the one the registry describes. It does
  not show that the code is safe, that it matches the GitHub source (S2),
  or that the publisher is trustworthy.
- **The advisory database was only partly reachable.** The global advisory
  and OSV lookups returned 404, and the npm bulk endpoint returned nothing,
  so GHSA-7m4x-rv66-mxhh was read from the repository advisory only. The
  two other GHSAs (p9cv, rq2p) were seen only through release notes.
- **Platform.** The code paths differ by platform (darwin, win32, others).
  Nothing was run on any platform, including this macOS machine.

### 2.6 Trust decision

> **TRUST DECISION (written by Swathi)**
>
> I would be much more cautious about trusting this Filesystem server since it has broader filesystem capabilities and can read, overwrite, and move files. Confirming the package integrity and locating the security fix in version 2.4.0 gave me some reassurance, but I haven't tested its runtime behavior or audited its dependencies. If I were to use it, I would limit it to a dedicated directory, enable the --confine-roots option, and manually approve all write or move requests. I would definitely want to test it in an isolated environment before trusting it with important or personal files.