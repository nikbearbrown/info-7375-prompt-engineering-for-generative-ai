# TOOL-SERVER.md — the JS3 score_posting tool server (Chapter 8)

Written 2026-11-20, before any server code or tests. Decisions by Swathi Baba
Eswarappa; drafted by Claude Code from them. This is the contract: tests are
written against it first, and the server is judged against it.

## 1. The capability: `score_posting(board, posting_id)`
One tool, read-only.

- **Input:** `board` is one of `databricks`, `stripe` or `plaid`, and
  `posting_id` is that posting's id as a string.
- **Output:** filter v1.1's saved record for that posting, taken unchanged
  from the results file:
  - the verdict, the score and the reason;
  - the points;
  - the per-rule results R1–R7, each with its result, reason and exact
    recorded quotes;
  - the evidence claims, with their recorded labels and quotes;
  - the posting's title, location and URL, as recorded.

  The response also names its source: the results file's path, its SHA-256,
  and the run it describes.
- **The only data source** is
  `runs/filter-v1.1-2026-11-17T21-47-06-167440-0500/results.json`
  (SHA-256 `a7f90a74cfd3c82324e55502439684f0234599cde74789fd0736808e2e5edeff`;
  1,832 postings: Databricks 901, Stripe 789, Plaid 142).
- **It retrieves, it doesn't score.** The tool returns a judgment the filter
  computed earlier, offline, on the saved 2026-11-17 collection. It does not
  fetch postings, run the filter or rescore anything.
  - A posting that has changed or been removed since 2026-11-17 is still
    answered from the 2026-11-17 record.
  - A posting that was not in that run is "unknown".
  - Every response says so, through its source fields.

## 2. Protocol
- **Implementation:** written from scratch with the Python standard library
  only (`tool/server.py`). It uses no MCP SDK and no third-party package.
- **Messages:** JSON-RPC 2.0 over stdin/stdout, using the MCP message shapes
  `initialize`, `notifications/initialized`, `tools/list` and `tools/call`.
  `ping` is also answered.

### Specification revision used
Checked on 2026-11-20 at modelcontextprotocol.io.

- **The current revision is 2026-07-28.**
  `https://modelcontextprotocol.io/specification/versioning` states: "The
  current protocol version is 2026-07-28". That revision is stateless: its
  changelog says "remove the `initialize`/`notifications/initialized`
  handshake", and adds `server/discover`. Source:
  `https://modelcontextprotocol.io/specification/2026-07-28/changelog`.
- **This server implements the previous revision, 2025-11-25.** That is the
  revision that defines the `initialize` / `notifications/initialized` shape
  named above:
  - `https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle`
  - `https://modelcontextprotocol.io/specification/2025-11-25/basic/transports`
  - `https://modelcontextprotocol.io/specification/2025-11-25/basic/index`
  - `https://modelcontextprotocol.io/specification/2025-11-25/server/tools`
  - `https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/ping`
- **In 2026-07-28 terms, it is a "legacy" server.** The 2026-07-28 stdio page
  says a client that supports both eras "SHOULD probe with `server/discover`",
  and that if "the server returns any other error … the server is legacy.
  Fall back to the `initialize` handshake." This server answers
  `server/discover` with JSON-RPC error -32601 (method not found), so such a
  client falls back.
- **Claude Code compatibility will be observed, not assumed.** Whether Claude
  Code 2.1.308, the local version, connects this way is recorded from the
  real transcript (§5).

### Rules the server follows, from 2025-11-25
- **Framing:** one JSON-RPC message per line, UTF-8, delimited by newlines,
  with no embedded newlines. "The server MUST NOT write anything to its
  `stdout` that is not a valid MCP message". Diagnostics go to stderr only.
- **Version negotiation:** the server supports exactly `2025-11-25`. If
  `initialize` requests it, the response repeats it. Otherwise the response
  offers `2025-11-25`, and the client decides whether to continue ("If the
  client does not support the version in the server's response, it SHOULD
  disconnect").
- **`initialize` result:** `protocolVersion`, `capabilities` set to
  `{"tools": {"listChanged": false}}`, and `serverInfo` set to
  `{"name": "js3-score-posting", "version": "1.0.0"}`.
- **Ids:** requests must have a string or integer id, never null
  ("Unlike base JSON-RPC, the ID MUST NOT be `null`"). A response repeats the
  request's id.
- **Notifications** get no response. `notifications/initialized` marks the
  session ready, and any other notification is ignored.
- **Before initialization:** `tools/list` and `tools/call` sent before
  `initialize` are refused with error -32600, and `ping` is answered. This
  is our choice: the spec says what the client SHOULD NOT do, not what the
  server must answer.
- **`tools/list`** returns one tool: `name`, `title`, `description`, and an
  `inputSchema` with `board` (enum), `posting_id` (string with a pattern),
  both required, and `additionalProperties: false`. It has no `outputSchema`
  and no annotations. Hints are not relied on; the spec says clients "MUST
  consider tool annotations to be untrusted unless they come from trusted
  servers".
- **`tools/call` result:** `content` holds one `{"type": "text"}` item with
  the record serialized as JSON, `structuredContent` holds the same record
  as an object, and `isError` is `false`.

### Errors
The spec separates protocol errors (a JSON-RPC `error`) from tool execution
errors (a result with `isError: true`).

| Case | Response |
|---|---|
| Line is not valid JSON | error -32700, id null |
| Valid JSON but not a single request or notification object (including a batch array, a missing or invalid `jsonrpc`, or a null id) | error -32600 |
| Unknown method (including `server/discover`, `resources/*` and `prompts/*`) | error -32601 |
| `tools/call` for an unknown tool | error -32602 `Unknown tool: <name>` (the spec's example) |
| `tools/call` params not an object, `name` missing, or `arguments` not an object | error -32602 |
| Arguments fail the input schema (unknown board, wrong id format for that board, extra or missing keys, path-like text) | result with `isError: true` and a short reason |
| Valid arguments, but the posting is not in the results file | result with `isError: true`, "unknown posting" |
| Unexpected server fault | error -32603, with no stack trace on stdout |

- **Error codes:** -32700 and -32600 to -32603 are the standard JSON-RPC 2.0
  codes. The 2025-11-25 base page does not list them, so they are taken from
  JSON-RPC 2.0 itself.
- **Our design choice for argument errors.** Treating argument-validation
  failures as tool execution errors follows the spec's description of
  execution errors as "actionable feedback that language models can use to
  self-correct". Before tests are written, it will be checked against the
  exact 2025-11-25 tools-page wording.

## 3. Declared boundaries
- **Reads one data file.** The server reads only the results file named in
  §1. Its path is a constant, resolved from the server file's own location.
  No path is ever built from client input.
  - At startup the server checks the file's SHA-256 against the value in §1,
    and refuses to start if it differs.
  - It also reads its own Python standard-library modules, as any Python
    program does.
- **No network and no subprocesses.** The server imports no networking,
  subprocess or process-execution modules, and does not call them.
- **Writes only its transcript.**
  - **Where:** one raw protocol transcript per session, under
    `tool/transcripts/`. Each file is created new and never overwritten.
  - **What it records:** each line received and each line sent, with a
    timestamp and direction, exactly as read and written.
  - **Oversized lines:** a line over 64 KiB is refused with error -32600.
    For such a line the transcript records its length, its SHA-256 and its
    first 1,024 characters, marked as truncated.
- **Accepts only valid inputs.**
  - `board` must be exactly `databricks`, `stripe` or `plaid`.
  - `posting_id` must be 1–20 digits for Databricks and Stripe, or a
    lowercase UUID for Plaid.
  - Anything else is rejected: other boards (including the failed
    `deliberate-bad-name` board), `../`, slashes, backslashes, NUL bytes,
    whitespace, URL-encoded text, absolute paths, non-strings and extra
    arguments.
- **Rejects unknown tools, unknown methods and unknown postings,** as set
  out in §2.
- **No sandbox is claimed.**
  - The server runs as an ordinary process with the user's permissions. It
    is not sandboxed by the operating system.
  - The boundaries above are properties of the code, checked by reading it
    and by observing it (§5). They are not enforced by the OS.
  - A modified `server.py` could do anything the user can do.

## 4. What a compatible client is NOT entitled to
- **Unrelated files.** Connecting gives a client one lookup into one saved
  results file. It gives no other file, directory listing or path access.
- **External side effects.** The server makes no network requests, starts
  no processes, sends no messages and changes no files except its own
  transcript.
- **Persistent state or memory.** Nothing a client sends is stored for later
  use, beyond the declared transcript. The next session starts from the same
  file. The transcript is a log, not memory the server reads back.
- **Treating a verdict as truth.** A verdict is the filter's recorded rule
  output, not a fact about the job or the candidate.
  - `audit/AUDIT-REPORT.md` measured where v1 disagreed with my labels.
  - `shortlist/SHORTLIST.md` shows that even the four shortlisted postings
    need a human check. None of them establishes visa sponsorship or F-1 OPT
    eligibility, and requirements outside R1–R7 (graduation windows,
    start-by dates) are not checked.
- **Treating a verdict as confirmed eligibility.** A "shortlisted" verdict
  is not confirmed employment eligibility, sponsorship or OPT eligibility.
- **Reading the record as current.** It describes the posting as collected
  on 2026-11-17.

## 5. Evaluation plan: this server
- **Declared vs observed.** Each boundary in §3 and each row of the errors
  table in §2 is a test, with its expected result written down before the
  server exists.
- **Code inspection.** Read `tool/server.py` for every file open, network
  use, subprocess or process execution, environment access and write. Also
  list its imports mechanically.
- **Runtime observation, not a sandbox.** A test wrapper runs the server
  with a Python audit hook (`sys.addaudithook`) that records `open`, socket,
  `subprocess.Popen`, `os.system`, `os.exec*` and `os.spawn*` events. For a
  full adversarial session, the expected record is:
  - opens of the results file (read) and of the transcript file (write);
  - standard-library imports;
  - nothing else.

  This observes the run; it does not confine it.
- **Protected files.** Record the SHA-256 of the results file and of the
  filter, audit, held-out, shortlist and persona files before and after the
  tests. They must be identical.
- **Normal requests** cover:
  - initialize;
  - notifications/initialized;
  - tools/list;
  - one known posting per board, including a shortlisted posting, a
    rejected posting and an "I cannot tell" posting, each compared field by
    field with `results.json`;
  - ping;
  - end of input, which must end the server cleanly.
- **Adversarial requests** cover:
  - malformed JSON;
  - a batch array, a null id and a missing `jsonrpc`;
  - an unknown method, `server/discover`, an unknown tool and calls before
    initialize;
  - missing, extra and wrongly typed arguments;
  - unknown boards and unknown postings;
  - path tricks (`../`, `..%2F`, absolute paths, backslashes, NUL bytes);
  - an oversized line;
  - a `posting_id` that names a real file.
- **Real transcripts from two clients.**
  - **A scripted client:** a Python test driver.
  - **Claude Code** connected as an actual MCP client. That needs a Claude
    Code MCP configuration entry, which I will approve when we get there.
  - Both transcripts are written by the server itself, from the bytes it
    actually read and wrote.
- **Transcript privacy and integrity.**
  - Before committing, I check the transcripts for personal data, tokens,
    paths under my home directory and anything else private.
  - If something must be removed, the transcript is not edited silently.
    Either it is not committed, or a disclosed redaction is recorded next to
    the original's SHA-256.
  - No transcript message is fabricated or altered.
- **Trust decision.** I write the final trust decision for this server
  myself.

## 6. Evaluation plan: another named server
- **Proposed server:** the official Filesystem reference server,
  `src/filesystem` in `github.com/modelcontextprotocol/servers`, published
  as `@modelcontextprotocol/server-filesystem`.
- **Version pin, not yet recorded.** An exact npm version and its source
  commit will be pinned before any evaluation. On 2026-11-20 Claude Code
  could not read the npm registry or the GitHub README (WebFetch was not
  permitted for those hosts), so no version is claimed here.
- **Not installed or run yet.** Nothing is installed or executed at this
  stage.
- **Safety precautions, if it is run later:**
  - A throwaway directory outside this repository, containing only dummy
    files I create for the test.
  - It is the only allowed directory passed to the server.
  - A symlink inside it, pointing to another dummy file outside it, is used
    to test containment.
  - Nothing in my home directory, this repository or any credential is
    reachable through its arguments.
  - It is run with the pinned version only, by a scripted client that
    records the real protocol transcript.
  - The throwaway directory is deleted afterwards.
  - The server is not vendored into this repository, and no Node code is
    added to the course.
- **What is evaluated:**
  - its declared tools and boundaries (read vs write tools, allowed
    directories, roots, symlink handling) against observed behavior on the
    dummy directory;
  - what a client is and is not entitled to;
  - its trust.
- **Fallback: a disclosed code-reading evaluation.** If it cannot be run
  safely (for example, no Node runtime, or I decline the install), the
  evaluation reads the pinned source, and is clearly labeled as code-reading,
  not observation.
- **Trust decision.** I write the trust decision for that server myself.

## Known limitation: a legacy-era server
- **The current revision is 2026-07-28.** It is stateless and uses
  `server/discover`.
- **This server is legacy-era.** It implements 2025-11-25 because that is
  the message shape the assignment names.
- **Clients that speak only 2026-07-28 will fail.** The 2026-07-28
  compatibility matrix says a modern-only client and a legacy server
  "Fails".
- **Claude Code is to be observed, not assumed.** Whether Claude Code
  connects to this server will be observed in the real transcript.

## Decisions (decided 2026-11-20, Swathi)
1. **Protocol: 2025-11-25, as drafted.** It is the message shape the
   assignment names. The limitation is recorded in "Known limitation: a
   legacy-era server" above.
2. **Argument errors: as drafted.**
   - Validation failures are tool execution errors, with `isError: true`.
   - An unknown tool or malformed params are protocol errors, -32602.
3. **Filesystem server version: deferred to the evaluation step.** I will
   provide or approve a verifiable source for the pin then. Until then,
   nothing is installed or run.

## Amendment (2026-11-20, Swathi): rate limit, handshake cases, privacy
Added after the tests were committed (`ae93c19`) and before any server code.
The sections above are unchanged; where this amendment differs from them,
it takes precedence.

### 1. Rate limit
- **Why:** the 2025-11-25 tools page says "Servers MUST: … Rate limit tool
  invocations".
- **The limit:** at most 20 `tools/call` requests per second per session.
  A call beyond that is a tool execution error: a result with
  `isError: true` and the text "rate limit exceeded".
- **Recovery:** once the one-second window has passed, calls succeed again.
- **How it is applied (Claude Code's reading, for me to confirm):**
  - It is a sliding one-second window over the calls the server accepted.
  - A call is counted when it passes the protocol checks, that is
    initialization, the params shape and the tool name. This includes calls
    that then fail argument validation or name an unknown posting.
  - Calls refused for the rate limit are not counted.
  - Protocol errors such as an unknown tool are returned before the limit is
    applied.
  - Each session (each server process) has its own window.

### 2. Handshake cases
- **Requests after `initialize` but before `notifications/initialized`** are
  served normally. This is lenient, because the spec constrains the client.
- **A second `initialize`** in the same session gets error -32600, with the
  message "already initialized".

### 3. Privacy of run outputs and transcripts
- **The existing run.** `tool/test-runs/before-implementation.txt` (commit
  `ae93c19`) contains absolute home-directory paths in its tracebacks. It
  stays as committed, with no history rewrite. This is a disclosed privacy
  note.
- **New run outputs must not contain absolute home-directory paths.** They
  are checked for "/Users/" before they are committed.
- **Transcripts get the same check.** The transcript privacy check (§5)
  searches for "/Users/".
- **Raw protocol transcripts are preserved unchanged.**
- **If a redaction is ever necessary:**
  - the original is kept locally and not committed;
  - the original's SHA-256 is recorded;
  - every redaction is disclosed in the committed copy.

**Confirmed (2026-11-20, Swathi):** the rate-limit counting reading in §1 above is approved as written.
