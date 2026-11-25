# Evaluation of our MCP server: `job_agent/mcp_server.py`

JS3, step 2 item 3: "evaluate it the way you would a server someone else wrote." The server was built by Claude Code
at my request (commit `a54c424`). This evaluation was drafted by Claude Code on 2026-11-21 from the source, the
recorded runs and the tests named below; every claim carries its evidence type. The trust decision at the end is mine
(written on 2026-11-22). On 2026-11-24 Claude Code added runtime traces where this evaluation had said run-time
behavior was uninspected, and, after my decision, a section on what changed since I wrote it.

## What was evaluated, and with what

- **The object.** `job_agent/mcp_server.py` at commit `a54c424` (SHA-256 `e39a82fe67a0...5325c`), server name
  `job-search-agent`, version `1.0.0`, protocol version `2025-11-25`, started as
  `python3 -B -m job_agent.mcp_server [--transcript js3/mcp/transcripts/NAME.jsonl]`. One tool, `score_posting`.
  The current file, changed in `5dff01f` on 2026-11-22, has SHA-256
  `db44168911705a2ee853b999ac1ebac7ddbc10914c293ce418f7478799c5a347`; what changed is in "Changes after the trust
  decision" at the end. [independently sourced: git history]
- **The task it is evaluated for.** Score one posting from the agent's saved board answers with FILTER.md v1.0 for
  the fictional persona Jane Doe, so that Claude can be offered the agent's filter as a tool (the JS3 brief). Nothing
  else.
- **The evidence.**
  1. The source, read line by line on 2026-11-21, with the modules it imports.
  2. Three recorded runs (all in `js3/mcp/transcripts/`):
     our client against it (`2026-11-21T084407Z-own-client.*`, started 2026-11-21 08:44:07 UTC), the server's own
     record of the same run (`2026-11-21T084407Z-own-server.jsonl`), and one live run with Claude Code 2.1.326 as
     the client (`2026-11-21T084542Z-claude-code-*`, started 08:45:42 UTC).
  3. The tests: `tests/test_mcp_server.py` (33) and `tests/test_mcp_client.py` (9), and six planted server mistakes
     in `tools/mutants.py`.
  4. The MCP 2025-11-25 specification pages for the lifecycle, the transports and tools
     (modelcontextprotocol.io/specification/2025-11-25/...), read on 2026-11-21.
  5. Runtime traces, made by Claude Code on 2026-11-24 (`js3/mcp/runtime/2026-11-25T023441Z/`, named in UTC): our
     client's same five sessions, with the server's code unchanged and run under a Python audit hook (PEP 578) by
     `tools/mcp_runtime_trace.py`, on Python 3.12.14 and 3.9.6. Runs: traced without and with `--transcript`, traced
     with the network denied by `sandbox-exec`, traced at `a54c424`, and not traced as a control. The trace's own
     tests are `tests/test_mcp_runtime_trace.py` (17). The folder's README gives the command that re-checks it.
- **Evidence types**, as chapter 8 names them:
  - **advertised**: what the server says about itself (its tool listing, its initialize answer).
  - **source-inspected**: read in the code.
  - **executed on a fixture**: a run we made and recorded, on constructed postings (the tests) or on the saved board
    answers of run `2026-11-20T114036Z` (the transcripts and the runtime traces). The run is named each time.
  - **independently sourced**: from a source the server did not write (the MCP specification, the committed filter
    run, the course repo's history).
  - **uninspected**: not looked at. Not the same as "none".

## Ledger 1: Protocol. Is the exchange well formed and in order?

| # | Claim | Evidence type | Where |
|---|---|---|---|
| P1 | Every request in the recorded runs got exactly one answer carrying its id; no notification got an answer. | executed on a fixture | own-client run: 31 of 31 expected answers; Claude Code run: 4 requests, 4 answers, 1 notification, no answer |
| P2 | Initialization and readiness are two states: after `initialize` and before `notifications/initialized`, `tools/list` is refused with -32000. | executed on a fixture; source-inspected | own-client session `early`, step 3; `Server.handle`; test `test_tools_wait_for_the_initialized_notification` |
| P3 | Every request before `initialize` gets -32000, whatever its method. | executed on a fixture | session `early`, step 1; Claude Code's `server/discover` probe, answered -32000 |
| P4 | `initialize` checks its params (a string `protocolVersion`, an object `capabilities`, a `clientInfo` with name and version) and answers -32602 if one is missing. | source-inspected; executed on a fixture | `initialize_problems`; test `test_initialize_needs_its_params` |
| P5 | The version answer is always `2025-11-25`: the requested version when it is that one, otherwise the server's only supported version, which is what the lifecycle page asks a server to answer. | source-inspected; independently sourced; executed on a fixture | `Server._initialize`; lifecycle page, "Version Negotiation"; test `test_the_version_answer_is_the_one_supported_version` |
| P6 | Claude Code asked for `2025-11-25` in `initialize` and went on with the session. | executed on a fixture | Claude Code run, server record, the `initialize` line |
| P7 | Error codes: -32700 with id null for a line that is not one JSON value in UTF-8; -32600 with id null for JSON that is not a request; -32601 for an unknown method after readiness; -32602 for an unknown tool or for params or arguments that are not objects; -32603 for an internal error, which does not end the server. | executed on a fixture | own-client session `main`, steps 7, 10, 11, 12; tests in `MessageTest` and `ToolTest` |
| P8 | A tool-level negative is a result with `isError: true`, not a protocol error: an unknown posting, arguments that fail the input schema, a used-up call budget. This follows the tools page's split ("Input validation errors" are tool execution errors; "Unknown tools" are protocol errors). | executed on a fixture; independently sourced | session `main`, steps 6, 8, 9; tools page, "Error Handling" |
| P9 | stdout carries protocol messages only. | source-inspected; executed on a fixture | the only stdout write is in `serve`; test `test_without_transcript_nothing_is_written_and_stdout_carries_protocol_only` (every stdout line parses as one JSON-RPC response); planted mistake "a status line on stdout" |
| P10 | A second `initialize` is refused with -32000 and changes no state; a `tools/call` sent as a notification (no id) is never answered and never run. | executed on a fixture | session `lifecycle`, steps 3 and 4; test `test_notifications_are_never_answered_and_a_tool_call_without_id_never_runs` |
| P11 | A line that is not UTF-8 and a line of 20,000 nested brackets each get -32700, and the server keeps answering. | executed on a fixture | sessions `bytes` and `deep` |
| P12 | How a session ends is recorded: a closed stdin ("stdin closed"), SIGTERM ("SIGTERM"), SIGINT ("interrupted"). Claude Code's session ended with "interrupted": the server got SIGINT while it was waiting for input, so it never read a closed stdin first. | executed on a fixture | own-server record (5 sessions, each "stdin closed"); test `test_sigterm_ends_the_session_and_the_transcript_says_so`; Claude Code run, last line of the server record |
| P13 | Claude Code sent a method the contract never named, `server/discover`, before `initialize`, as a probe for protocol revision `2026-07-28`. The server answered -32000 (not initialized), not -32601. Claude Code then sent `initialize` for `2025-11-25`. | executed on a fixture | Claude Code run, server record, first two exchanges |
| P14 | Not implemented: `ping`, cancellation, progress notifications, pagination (a `cursor` is ignored), `server/discover`, JSON-RPC batches (refused as -32600), and any check that a request id is not reused. This is a subset of MCP, not a conformant implementation. | source-inspected | `Server.handle` dispatches four methods only |

## Ledger 2: Capability. Does the code do what the listing says?

### Declared against actual

| What is declared | Where it is declared | What the code does | Evidence type |
|---|---|---|---|
| One tool, `score_posting` | tools/list | `tools/list` returns the one `TOOL` object; `tools/call` runs nothing else | advertised; source-inspected; executed on a fixture (session `main`, step 3 and 7) |
| "The tool reads saved files only" | tool description | `score_posting` reads `runs/<run>/boards/<board>/attempt-*.meta.json` and the saved body (through `filter_run.newest_answers`), `FILTER.md` (rules and SHA-256) and `persona/jane-doe.json` (through `resume.load`) | source-inspected |
| "it fetches nothing" | tool description | No network call on the tool's code path; the repo's modules import no `socket`, `ssl`, `http` or `subprocess` module (only `urllib.parse`). At run time, in the five traced sessions on Python 3.12.14 and 3.9.6: no socket was created and no network call was made, and with the network denied by `sandbox-exec` every answer was the same. On 3.12.14 no `socket`, `ssl`, `http` or `subprocess` module loaded. On 3.9.6, `subprocess`, `_posixsubprocess`, `select` and `selectors` did load: the server imports `platform` (line 48), and Python 3.9's `platform.py` imports `subprocess` when it loads; no process was started. | source-inspected (code path, the repo's imports); executed on a fixture (runtime trace, 2026-11-24, `js3/mcp/runtime/2026-11-25T023441Z/`) |
| "and changes no file" | tool description | `score_posting` calls only reading functions. A whole session without `--transcript` left a copy of the repo byte for byte unchanged. | source-inspected; executed on a fixture (test above, P9) |
| `readOnlyHint: true`, `openWorldHint: false` | tool annotations | As above. The tools page says clients "MUST consider tool annotations to be untrusted unless they come from trusted servers": these two are the server's own testimony. | advertised; independently sourced (tools page) |
| `board` is one of three boards; `posting_id` is a lowercase UUID or a number; no other argument | inputSchema | `argument_problems` checks the same three things; the `board` value only selects one of three fixed entries in `BOARDS`, and the board key used in a path comes from that entry, never from the client's string | source-inspected; executed on a fixture (session `main`, steps 8 and 9; test `test_arguments_that_fail_the_input_schema_are_tool_errors_that_never_echo_the_value`) |
| The strict id pattern does not lock out real postings | (not declared) | All 1,509 ids in the three newest saved answers match it | executed on a fixture (test `test_every_id_in_the_real_saved_answers_fits_the_pattern`) |
| "the fictional persona Jane Doe" | tool description | The profile is read through `resume.load`, which refuses a file not marked fictional | source-inspected |
| "the version is in the result" | tool description | The result carries `filter.version` and the SHA-256 of FILTER.md | executed on a fixture (session `main`, step 4) |
| Not in the listing: a budget of 50 tool calls per session; hidden characters (Unicode Cc and Cf, except newline and tab) dropped from results; the `--transcript` option | module docstring | All three are in the code. The budget is a per-session cap, not a time-based rate limit. | source-inspected; executed on a fixture (tests `test_a_session_answers_at_most_max_calls_tool_calls`, `test_hidden_characters_are_dropped_from_the_result`) |

### Every call that opens, writes, runs or connects

Read in `job_agent/mcp_server.py` (`open` needs no import, so the search covered `open(`, `.write`, `mkdir`,
`unlink`, `rename`, `os.`, `subprocess`, `socket`, `urllib`, `http`, `signal.` and `print(`, not only the imports):

| Call | What it does | When | Evidence type |
|---|---|---|---|
| `os.open(path, O_WRONLY \| O_APPEND \| O_CREAT \| O_NOFOLLOW)` and `os.fdopen`, then `file.write` | appends the transcript: the server's one write | only with `--transcript`, after `transcript_path` has allowed the path | source-inspected; executed on a fixture |
| `transcript_path` | refuses `..`, a name that is not `.jsonl`, a parent that is not exactly `js3/mcp/transcripts/` (after links are resolved), a link or a folder in the file's place, and a transcripts folder (or `js3/`, `js3/mcp/`) that is a link; refused means exit 3 before any message is read | at start | source-inspected; executed on a fixture (`TranscriptGuardTest`, `test_a_refused_transcript_path_stops_before_anything_is_read_or_written`; planted mistake "the transcript guard compares path strings") |
| `os.getcwd()` | resolves a relative `--transcript` path | at start | source-inspected |
| `stdout.write` in `serve` | the protocol | each answer | source-inspected |
| `print(..., file=sys.stderr)`, `traceback.print_exc(file=sys.stderr)` | a refusal, an internal error | rarely | source-inspected |
| `signal.signal(SIGTERM, ...)` | turns SIGTERM into a recorded end | at start, as a process only | source-inspected |
| `(repo / "FILTER.md").read_bytes()` | the SHA-256 in each result | each call | source-inspected |

The modules it imports (`job_agent.filter`, `filter_run`, `providers`, `resume`, `rule`, `evidence`, `errors`)
contain three functions that write: `filter_run.run` (a filter run's folder), `evidence.new_run_dir` and
`evidence.save_response`. The server calls none of them; its only calls into these modules are
`filter_run.newest_answers`, `providers.read`, `filter.load_rules`, `filter.load_profile`, `filter.check_profile` and
`filter.judge`, which read. [source-inspected]

**The interpreter writes too.** Run without `-B`, the same server left nine new bytecode files in
`job_agent/__pycache__/` (`__init__`, `errors`, `evidence`, `filter`, `filter_run`, `mcp_server`, `providers`,
`resume`, `rule`; gitignored). That is Python's import system, not the server's code, and it is why every documented
command, the client and the Claude Code configuration use `-B`. [executed on a fixture, 2026-11-21, in a copy of the
repo; with `-B` the tests find no new file]

**Who maintains it.** This repo; the code was written by Claude Code at my request; no other maintainer.
[independently sourced: git history]

## Ledger 3: Permission. Does this task allow that capability?

| # | Claim | Evidence type | Where |
|---|---|---|---|
| M1 | The task allows offering one capability to Claude through a tool server, and forbids exposing "anything that can send or change data outside your own folder". | independently sourced | the JS3 brief, step 2 item 3 and "Privacy and boundaries" |
| M2 | The data behind the tool: postings saved from three public board APIs on GATE.md's allow-list, and the fictional persona. No résumé, contact or tracker of mine is read. | source-inspected | `BOARDS`, `PROFILE`; `resume.load` refuses a persona not marked fictional |
| M3 | The effects: text returned to the client. The one write (the transcript) is chosen by whoever starts the process, lands only in this repo's `js3/mcp/transcripts/`, and no protocol message can start, stop or redirect it. | source-inspected; executed on a fixture | `main`, `transcript_path`; the process tests |
| M4 | In the Claude Code run, the host exposed exactly this one tool to the model and nothing else: no built-in tool, no other MCP server, no skill or slash command, dontAsk permissions, the seat's own login. Claude Code's four built-in plugins were loaded (`cc-plugin-sec-default`, `cc-plugin-agents-md`, `cc-plugin-privacy`, `cc-plugin-plugin-authoring`); they added no tool, and what they do inside a call is **uninspected**. | executed on a fixture | `2026-11-21T084542Z-claude-code-init.json` (`tools`, `mcp_servers`, `skills`, `slash_commands`, `plugins`, `permissionMode`, `apiKeySource`); command in `-run.json` |
| M5 | Where results may go: into Claude's context, as third-party text (each quote is the employer's posting) inside a result that says so (`data_note`) and says what it does not claim (`scope`). | source-inspected | `score_posting` |
| M6 | Discovery is not consent to call: `tools/list` only says the tool exists. In the Claude Code run the consent was the host configuration written before the call (`--allowedTools mcp__job-search-agent__score_posting` with `--permission-mode dontAsk`, which refuses anything not allowed). | source-inspected (the command); executed on a fixture | `2026-11-21T084542Z-claude-code-run.json`, `command`; `permission_denials` empty |
| M7 | Whether this scope is right for the task (the data, the effects, where the text may go) is not something the transcript can show. It is my decision. | (decision input) | below |

## Ledger 4: Evidence. Does the returned content support the claim built on it?

| # | Claim | Evidence type | Where |
|---|---|---|---|
| E1 | The record for the kept posting (`ashby-openai f3ddd41c...`) and for the rejected posting (`greenhouse-verkada 5283655007`) are equal to the records the committed filter run `2026-11-21T044414Z` made of the same postings, from the same saved answer (same SHA-256) and the same FILTER.md (same SHA-256). | executed on a fixture; independently sourced (the committed filter run) | own-client run, "Evidence checks" table |
| E2 | E1 shows that the server passes the filter's record through unchanged. It does not show that the filter's verdict is right about the posting: both records come from the same `job_agent/filter.py`. | (limit of E1) | |
| E3 | Whether the quotes and the fate are right about these two postings was not checked by a person. That is the reject audit's and the claims kit's job, not this evaluation's. | **uninspected** (for these two postings) | |
| E4 | Two of the three topic groups that earned the kept posting its 65 were earned by sentences about the candidate's required experience ("Strong software engineering experience building distributed systems, ...", "Experience designing and operating APIs, ... or large-scale backend services."), one by a duty sentence ("Design, build, and operate APIs and control-plane services ..."). FILTER.md's rule counts all three. Whether the first two support a claim that the job's work is in those groups is a label for me (FILTER.md Section 2), not decided here. | source-inspected (the record's `topics`) | Claude Code run, the `tools/call` answer |
| E5 | Currency: every result is from the saved answer of run `2026-11-20T114036Z` and says `"live": false`. Whether a posting is still open is not claimed. | source-inspected; executed on a fixture | `score_posting`; any result |
| E6 | Claude's answer restated the record correctly on the fate (kept), the deciding rule (none: all eight rules passed), the score (65 = 50 + 15 for three topic groups) and the FILTER.md version (1.0). It dropped the provenance the result carried: no run date, no "saved, not live", no "Jane Doe's written rules". It used four sentences where the prompt asked for at most three. | executed on a fixture | `2026-11-21T084542Z-claude-code-answer.md` against the server record |

### The handoffs in the Claude Code run (chapter 8, "Laundering")

| Handoff | What passes | Trusted to be | How that trust is earned here |
|---|---|---|---|
| Server to host | the `tools/call` answer, id 2, `isError: false`, the record of `f3ddd41c...` | FILTER.md v1.0's record of that posting in the saved answer `d595afc0...` of run `2026-11-20T114036Z`, from server `a54c424` | E1: the same record as the committed filter run's; the server record and the source |
| Host to Claude's context | that text, byte for byte | data from a saved posting, not instructions and not a current fact | the run's check "the tool result Claude Code passed on is the text the server sent" (passed; recomputed by `test_the_committed_claude_code_run`); the system prompt said to treat tool output as data |
| Claude to answer | four sentences (E6) | "FILTER.md v1.0 kept this saved posting for Jane Doe with score 65" | the values trace to the record (E6); the provenance did not survive the restatement |

## What a compatible client is not entitled to

| The client tries to | The server's answer | Evidence type |
|---|---|---|
| call a tool before the handshake is done | -32000 | executed on a fixture (session `early`, steps 1 and 3) |
| call a tool that is not listed (`update_state`) | -32602 "Unknown tool: update_state" | executed on a fixture (session `main`, step 7) |
| add an argument, such as another profile (`"profile": "private/real-resume.json"`) | `isError: true`, "not allowed: profile"; nothing is read | executed on a fixture (step 8); source-inspected |
| name a file through the id (`../../../../etc/passwd`) | `isError: true`; the id fails the pattern, and an id is only ever compared with posting ids, never used as a path | executed on a fixture (step 9); source-inspected |
| send arguments that are not an object | -32602 | executed on a fixture (step 10) |
| read resources (`resources/read` of `file:///etc/passwd`) | -32601: no resources are declared | executed on a fixture (step 11) |
| send a malformed line, a line that is not UTF-8, or a line nested 20,000 deep | -32700, id null; the server keeps answering | executed on a fixture (step 12; sessions `bytes`, `deep`) |
| run a tool through a notification | nothing: never answered, never run | executed on a fixture (session `lifecycle`, step 4) |
| initialize a second time | -32000 | executed on a fixture (session `lifecycle`, step 3) |
| call more than 50 times in one session | `isError: true`, budget used up | executed on a fixture (test) |
| start, stop or move the transcript | no message can; only the command line | source-inspected |
| change any data | no method writes | source-inspected; executed on a fixture (the unchanged copy of the repo) |
| reach the network through the server | no network code on any path the server runs; in the traced sessions no socket was created, no network call was made and no process was started, and with the network denied every answer was the same | source-inspected; executed on a fixture (runtime trace, 2026-11-24, `js3/mcp/runtime/2026-11-25T023441Z/`) |

## Findings

1. All 31 steps of our client's run (requests, notifications and broken lines) got the answer the contract predicts,
   silence for the notifications included, and the server's own record of the run matches the client's record line for
   line (5 sessions, 57 lines). [executed on a fixture]
2. Claude Code 2.1.326, run headless once on 2026-11-21 at 08:45:42 UTC with only this server and only this tool,
   called `score_posting` once with the requested arguments; the text it passed to the model is the server's text,
   byte for byte. [executed on a fixture]
3. A real client sent a request the contract had not named: `server/discover`, before `initialize`. The server's
   answer was the lifecycle error -32000. The session went on. [executed on a fixture]
4. Claude Code ended the server with SIGINT while the server was waiting for input; the server's record says
   "interrupted". The stdio section of the lifecycle page says a client should first close the server's input; the
   server never saw its input close. [executed on a fixture; independently sourced]
5. Two of the nine checks the run script wrote before the call failed, and both on client behavior the script did not
   expect: the init event's server entry has an extra field (`"source": "dynamic"`), and `server/discover` came before
   `initialize`. The other seven passed. [executed on a fixture: `-run.json`]
6. The kept and the rejected records are equal to the committed filter run's records of the same postings. [executed
   on a fixture; independently sourced]
7. Without `--transcript`, a full session changes no file; with it, only the named transcript file changes; any other
   path is refused before a message is read. [executed on a fixture]
8. Without `-B`, the Python interpreter writes nine bytecode files into `job_agent/__pycache__/`. [executed on a
   fixture]
9. The six planted server mistakes (ready set on initialize, a tool error sent with `isError` false, an extra argument
   accepted, the transcript guard comparing strings, a status line on stdout, a transcript written without being asked
   for) are each caught by at least one test: the full run of 2026-11-21 (08:49 to 09:08 UTC) caught 82 of 82 planted
   mistakes, these six included (`js3/checks/mutants-2026-11-21-mcp.txt`). [executed on a fixture]
10. The server is a subset of MCP 2025-11-25 (Ledger 1, P14): not conformant, and not shown to be secure.
11. (Added 2026-11-24.) In the five traced sessions, on Python 3.12.14 and 3.9.6, the server opened no file to write
    and changed no file, except the transcript when it was started with `--transcript` (per session, one `os.open`
    with `O_WRONLY`, `O_APPEND`, `O_CREAT` and `O_NOFOLLOW`, then that descriptor opened in mode `a`). It created no
    socket, made no network call and started no process. It read its own nine modules, FILTER.md, the persona, files
    under `runs/` and Python's own files, and nothing else. With the network denied by `sandbox-exec` every answer was
    the same, and every traced answer was the same as the untraced one. This is what happened in these runs on these
    inputs, not proof for every input; the source reading above covers the code paths. [executed on a fixture:
    runtime trace, 2026-11-24, `js3/mcp/runtime/2026-11-25T023441Z/`]
12. (Added 2026-11-24.) On Python 3.9.6 the modules `subprocess`, `_posixsubprocess`, `select` and `selectors` load
    when the server starts, because the standard library's `platform`, which the server imports, imports `subprocess`
    when it loads (Python 3.9.6's `platform.py`, line 119); on 3.12.14 they do not. The reading of the import graph on
    2026-11-21 covered the repo's own imports, not the standard library's. No process was started in any traced
    session. [executed on a fixture: the same trace; source-inspected: `platform.py`]

## Not checked

- Run-time behavior outside the traced sessions: any other input or client, and anything done in C below the audit
  hook (the system loader opening a C extension module, a C library opening a file or a socket by itself, such as the
  OpenSSL library behind `hashlib`). **uninspected**
- Any version of the server other than `a54c424` and the current file (`db441689...a347`), both traced on 2026-11-24
  and compared in "Changes after the trust decision". **uninspected**
- How Claude Code handles a server that answers a different protocol version. **uninspected**
- Whether the two postings' records are right about the postings (E3). **uninspected**
- Anything outside the recorded transcripts, the runtime traces and the tests named above.

## Facts the trust decision should rest on

- Scope of the task: score one saved posting for the fictional persona, read-only, for JS3; results go into Claude's
  context as data.
- What it reads: saved board answers, FILTER.md, the fictional persona (source-inspected); never my résumé or
  contacts.
- What it writes: nothing, except the transcript an operator asks for, inside `js3/mcp/transcripts/` only (source and
  tests); Python's bytecode caches if `-B` is left out (executed). In the traced sessions, no write but that
  transcript (executed on a fixture: runtime trace, 2026-11-24).
- What it reaches: no network code on its path (source-inspected); in the traced sessions no socket, no network call
  and no process, and the same answers with the network denied (executed on a fixture: runtime trace, 2026-11-24). On
  Python 3.9.6 the standard library's `platform` loads `subprocess` when the server starts, without starting a process.
- How it behaved with a real client: one live Claude Code call, the expected tool call and the exact text handed on;
  one unexpected probe (`server/discover`) refused with -32000; shut down by SIGINT.
- What its results claim and do not claim: the record of FILTER.md v1.0 over a saved answer, marked not live; Claude's
  restatement kept the values and dropped that provenance.
- Version and provenance: commit `a54c424`, server `1.0.0`, protocol `2025-11-25`, maintained in this repo, written by
  Claude Code at my request; six planted mistakes caught. (The file has changed since: see "Changes after the trust
  decision".)
- What would reopen the decision: a new tool or argument, a change to `job_agent/mcp_server.py` or to the modules it
  calls, a new FILTER.md version, a change to what the boards or the persona hold, a new Claude Code version or host
  configuration, or a task that sends results anywhere but Claude's context.

## Trust decision (Aravind's)

**Pending.** I would use `score_posting` for local, read-only scoring of saved postings with server version 1.0.0 at commit `a54c424`, but I would not approve it for broader use yet. I would reconsider after MCP conformance and security testing, or if the server, its arguments, the filter, or the Claude Code version changes.

*Aravind, 2026-11-22. In my own words; Claude Code only turned the dash into a full stop and marked the names as code.*

## Changes after the trust decision (added 2026-11-24)

Written by Claude Code on 2026-11-24. The decision above was committed in `d4c9eb0` on 2026-11-22 at 03:26 ET, for
the server at `a54c424`. Two commits made later that night changed the server or the modules it calls.
[independently sourced: git history; source-inspected: the diffs]

| Commit | When (ET) | What changed | Why FILTER.md v1.0's scoring stays the same |
|---|---|---|---|
| `b8e3a25`, "Two optional switches for v1.1 candidates, both absent in FILTER.md v1.0" | 2026-11-22 03:32 | `job_agent/filter.py` (13 lines added, 3 removed): `split_sentences` can keep listed abbreviations such as "U.S." inside a sentence (Section 7's optional `splitter_keeps`), and `score` adds a term only when `ranking.caution_penalty` is set. | v1.0's Section 7 has neither key, so neither switch acts. Tests in `tests/test_filter_switches.py`: `test_v1_0_has_neither_switch`, `test_splitter_keeps_us_inside_a_sentence_only_when_asked`, `test_caution_penalty_only_when_set`, `test_v1_0_judgments_unchanged_by_the_new_code`. |
| `5dff01f`, "FILTER.md v1.1 (2026-11-22), added below v1.0, which is unchanged" | 2026-11-22 03:47 | `FILTER.md`: v1.1 added below v1.0, with its own Section 7 (293 lines added, none removed). `job_agent/filter.py` (20 added, 6 removed): `load_rules` reads every Section 7 and returns the newest unless a version is named. `job_agent/filter_run.py` (3 added, 2 removed): `run` takes `rules_version` and passes it on; `newest_answers`, the one function of that module the server calls, is unchanged. `job_agent/mcp_server.py` (6 added, 1 removed): a constant `SERVED_FILTER_VERSION = "1.0"` with a three-line comment, and `score_posting` calls `flt.load_rules(repo / "FILTER.md", version=SERVED_FILTER_VERSION)` where it called `flt.load_rules(repo / "FILTER.md")`. (`job_agent/__main__.py` gained `--filter-version`; the server does not use it.) | The server names v1.0, and v1.0's text is unchanged. Tests in `tests/test_filter_v1_1.py`: `test_version_1_0_text_is_unchanged`, `test_the_newest_is_1_1_and_1_0_can_still_be_named`, `test_1_1_differs_from_1_0_only_where_the_document_says`, `test_the_mcp_server_stays_on_the_version_it_was_evaluated_with`. |

The server still answers `initialize` with version `1.0.0`, as at `a54c424`: the version a client sees did not move
with the code. [source-inspected; executed on a fixture]

What the runtime comparison showed [executed on a fixture: runtime trace, 2026-11-24,
`js3/mcp/runtime/2026-11-25T023441Z/`, `compare-d.md` in each Python's folder]:

- The server at `a54c424` (a `git archive` of that commit) and the current server answered all five sessions the same,
  on Python 3.12.14 and on 3.9.6, except one field in two messages: `filter.sha256` inside the text of the
  `score_posting` results for the kept posting (main session, step 4, id 3) and the rejected posting (step 5, id 4).
  That field is FILTER.md's SHA-256: `f1edbf0b5319d0c42645e892d6ef39f738f964128f3146fb82abea06438ba6f1` at `a54c424`
  (v1.0 only), `4d79d279f5b5157e8905cb0e2109e4c50b1b983d410d8bff2a0614077e32a572` now (v1.0, then v1.1).
  `filter.version` is "1.0" in both, and the records (fate, rules, score, topics) are equal.
- The `a54c424` run's answers are the same as the ones our client recorded from that commit on 2026-11-21
  (`js3/mcp/transcripts/2026-11-21T084407Z-own-client.jsonl`).
- The two traces list the same files read and the same modules loaded, and no write, socket or process in either.
  They differ only in the server's SHA-256 and FILTER.md's.

What this means for the decision: "What would reopen the decision", above, names "a change to `job_agent/mcp_server.py`
or to the modules it calls, a new FILTER.md version". Both happened after the decision was written, so by this
evaluation's own terms the decision is reopened. The decision itself says it would be reconsidered "if the server, its
arguments, the filter, or the Claude Code version changes". The comparison shows that the scoring served in these
sessions did not change; it does not make the call.

**Aravind's call after these changes:** **Still pending.** Same scope as before: fine for local, read-only scoring
of saved postings, not approved for broader use until conformance and security testing.

*Aravind, 2026-11-24. He chose this from the two options Claude Code laid out with the evidence above (still pending,
or allow for local read-only use); the words are the option's, which he picked.*

