# Evaluation of another MCP server: the course's lesson 8 reference server

JS3, step 2 item 3: "Evaluate one other tool server from a source you can name the same way." The other server is the
reference implementation of the course's lesson 8, written by the instructor. This evaluation was drafted by Claude
Code on 2026-11-21 from the source, one recorded run of our client against it, and the course repo's history; every
claim carries its evidence type. The trust decision at the end is mine (written on 2026-11-22).

## What was evaluated, and with what

- **The source, named.** `lessons/08-mcp-from-scratch/code/main.py` in the course repository
  `github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai`, at `upstream/main` commit `5639e4c8`
  (fetched into my local clone; nothing was downloaded for this). The file was last changed in commit `a8629ce1`
  (2026-09-06, Nik Bear Brown, "feat: publish INFO 7375 Claude and Python course"). The repository's LICENSE is the MIT
  License.
- **The copy.** `js3/mcp/other-server/main.py`, made with `git show`, byte for byte: its git blob hash is the upstream
  blob's, `f33ea9de`, and its SHA-256 is `948337af...8b1769`. 72 lines; it imports `argparse`, `json` and `sys`.
- **What it says it is.** Server name `info7375-readonly`, version `1.0.0`, protocol version `2025-11-25`; one tool,
  `lookup`, "Read a public course fixture". Run as a stdio server with `python3 main.py --stdio`.
- **The task it is evaluated for.** A classroom comparison: answer the lookup for key `office` from the declared course
  fixture, driven only by our own client. It was never connected to Claude Code.
- **The evidence.**
  1. The source, all 72 lines, read on 2026-11-21.
  2. One recorded run of our client against the copy: `js3/mcp/transcripts/2026-11-21T084408Z-other-client.*`
     (started 2026-11-21 08:44:08 UTC), command `python3 -B -I js3/mcp/other-server/main.py --stdio`, environment
     `PATH=/usr/bin:/bin`, `LANG` and `LC_ALL` `en_US.UTF-8`, nothing else. Each expected answer in that run was
     written in `tools/mcp_client.py` from this source before the run, with the line it relies on.
  3. The test `test_the_reference_server_does_what_its_source_says` (`tests/test_mcp_client.py`), which repeats the
     run on every test run.
  4. Chapter 8 of the course book, which describes this server, and the MCP 2025-11-25 specification pages for the
     lifecycle, the transports and tools, read on 2026-11-21.
- **Evidence types**: advertised, source-inspected, executed on a fixture (here: the recorded run and the test),
  independently sourced, uninspected, as in `EVALUATION-OWN.md`.

## Ledger 1: Protocol. Is the exchange well formed and in order?

| # | Claim | Evidence type | Where |
|---|---|---|---|
| P1 | Every request with an id got exactly one answer carrying its id, until the process ended; no notification got an answer. | executed on a fixture | run: 30 of 30 answers as predicted |
| P2 | Two lifecycle flags: every request but `initialize` is refused with -32000 until `initialize` and then `notifications/initialized` have arrived, including `tools/list` after `initialize` and before the notification. | source-inspected; executed on a fixture | lines 25 to 30; session `early`, steps 1 and 3 |
| P3 | `initialize` reads no params: it sets `initialized` and answers `2025-11-25` whatever the client asked. Our client's valid params got that answer; the code cannot tell a supported request from a malformed one. | source-inspected; executed on a fixture | lines 25 to 28; every `initialize` in the run; chapter 8 says the same |
| P4 | A second `initialize` is answered with a result again, and `ready` stays true. | executed on a fixture | session `lifecycle`, step 3 |
| P5 | A `tools/call` sent as a notification is dropped: no answer, and the lookup does not run. | source-inspected; executed on a fixture | lines 18 to 21; session `lifecycle`, step 4 |
| P6 | -32700 with id null for a line `json.loads` rejects with a `ValueError`; -32601 for an unknown method once ready; -32602 for an unknown tool and for arguments other than exactly one string `key`. -32600 with id null for a message that is not a JSON object with `"jsonrpc": "2.0"` is in the code, but no such message was sent. | source-inspected; executed on a fixture (-32600: source-inspected only) | lines 64 to 67, 45 to 46, 37 to 41, 15 to 16; session `main`, steps 6, 7, 9, 10, 11 |
| P7 | An extra argument and arguments that are not an object both get -32602 ("Expected a string key"). The MCP 2025-11-25 tools page puts a request that fails the CallToolRequest schema (arguments that are not an object) under protocol errors, and "Input validation errors" (an extra key against the tool's own schema) under tool execution errors, returned as a result with `isError: true`. The server declares `2025-11-25`. | executed on a fixture; independently sourced | session `main`, steps 7 and 9; tools page, "Error Handling" |
| P8 | An unknown key is a tool result with `isError: true`, not a protocol error. | source-inspected; executed on a fixture | lines 42 to 44; session `main`, step 5 |
| P9 | A line that is not UTF-8 ends the process: `for line in sys.stdin` decodes outside the `try`, and the `UnicodeDecodeError` is not caught (exit 1, traceback on stderr). Under a locale where Python reads stdin with `surrogateescape` (its UTF-8 mode, or the C locale), the same line would likely reach `json.loads` and get -32700; that was not run. | source-inspected; executed on a fixture (in the environment named above) | line 63; session `bytes`, step 4, stderr recorded |
| P10 | A line of 20,000 nested brackets ends the process: `json.loads` raises `RecursionError`, and line 66 catches `ValueError` only (exit 1, traceback on stderr). | source-inspected; executed on a fixture | lines 64 to 67; session `deep`, step 4, stderr recorded |
| P11 | In `--stdio` mode stdout carries one JSON answer per line and nothing else. Without `--stdio`, the default mode prints the demo's `tools/list` answer as indented JSON over many lines and exits: a client that starts it without the flag reads a broken multi-line answer to a request it never sent. | source-inspected | lines 59 to 61 and 68 to 69 |
| P12 | Not implemented: params checking on `initialize`, version negotiation, `ping`, cancellation, progress, pagination, and any check that a request id is not reused. A subset of MCP, not a conformant implementation; chapter 8 calls it a teaching subset. | source-inspected; independently sourced | the whole file; chapter 8 |
| P13 | The server keeps no record of what it received or sent. The only transcript of this run is our client's. | source-inspected | the whole file |

## Ledger 2: Capability. Does the code do what the listing says?

### Declared against actual

| What is declared | Where it is declared | What the code does | Evidence type |
|---|---|---|---|
| One tool, `lookup` | tools/list | the listing (lines 32 to 34) and the dispatch (line 37) name the same one tool | advertised; source-inspected; executed on a fixture (session `main`, steps 3 and 6) |
| "Read a public course fixture" | tool description | the lookup consults one literal mapping in the code, `{"office": "505A Dana Hall"}` (line 42). Nothing is read from a file. | source-inspected |
| "public" | tool description | nothing in the code classifies data; "public" is a claim about the data that only its owner (the course) can make, as chapter 8 itself says | source-inspected; independently sourced (chapter 8) |
| `key` is a string; no other argument | inputSchema | line 40 checks exactly the key `key` and a string value | source-inspected; executed on a fixture (session `main`, steps 7 and 9) |
| (not declared) a path-like key | | any string is a key into the mapping; `../../../../etc/passwd` is looked up, not opened, and gets "Record not found" with `isError: true` | source-inspected; executed on a fixture (session `main`, step 8) |

### Every call that opens, writes, runs or connects

The file imports `argparse`, `json` and `sys`. Because `open` needs no import, the search covered the whole file,
not only the imports: there is no `open(`, no other way of opening a file, no `os`, `subprocess`, `socket`, `urllib` or `http`, and
no write except `print(...)` to stdout (lines 60 and 69). [source-inspected]

- **Reads:** `sys.stdin` (line 63). No file, no network, no environment variable. [source-inspected]
- **Writes:** stdout only. [source-inspected]
- **At run time:** file and network behavior were not traced; the claim above rests on reading all 72 lines.
  [runtime: **uninspected**]
- **Who maintains it:** the course instructor, in the course repository; one commit touched the file, on 2026-09-06.
  [independently sourced: the course repo's git history]

## Ledger 3: Permission. Does this task allow that capability?

| # | Claim | Evidence type | Where |
|---|---|---|---|
| M1 | The task here is a local comparison, driven only by our client; the server was never offered to Claude Code. | executed on a fixture | the run's command; no Claude Code run names this server |
| M2 | The data behind the tool: one literal key and value, written in the source. The effects: text on stdout. | source-inspected | line 42 |
| M3 | Discovery is not consent to call: our client called `lookup` because its plan said to, for this comparison. The listing gives no permission for any other task. | source-inspected (`tools/mcp_client.py`, `other_plan`) | |
| M4 | Whether the fixture is public, and whether this server belongs in any other task, are not facts the transcript holds. They are the data owner's and my decisions. | (decision input) | below |

## Ledger 4: Evidence. Does the returned content support the claim built on it?

| # | Claim | Evidence type | Where |
|---|---|---|---|
| E1 | The value returned for `office`, "505A Dana Hall", is the value in the source's mapping. | executed on a fixture; source-inspected | session `main`, step 4; line 42 |
| E2 | "Record not found" for `missing` (and for the path-like key) is an absence in the fixture, not a fact about the world. | source-inspected | lines 42 to 44 |
| E3 | Whether the course office is in 505A Dana Hall today was not checked. The claim the evidence earns is "the course fixture lists the office as 505A Dana Hall". | **uninspected** | |

## What a compatible client is not entitled to

| The client tries to | The server's answer | Evidence type |
|---|---|---|
| call a tool before the handshake is done | -32000 | executed on a fixture (session `early`, steps 1 and 3) |
| call a tool that is not listed (`update_state`) | -32602 "Unknown tool" | executed on a fixture (session `main`, step 6) |
| add an argument (`"profile": "private/real-resume.json"`) | -32602 "Expected a string key": refused, at the protocol layer (P7) | executed on a fixture (step 7) |
| name a file through the key (`../../../../etc/passwd`) | looked up as a string: "Record not found", `isError: true`; nothing is opened | executed on a fixture (step 8); source-inspected |
| send arguments that are not an object | -32602 | executed on a fixture (step 9) |
| read resources (`resources/read` of `file:///etc/passwd`) | -32601 | executed on a fixture (step 10) |
| send a malformed line | -32700, id null; the server keeps answering | executed on a fixture (step 11 and 12) |
| send a line that is not UTF-8 | **the process ends** (exit 1); every later request goes unanswered | executed on a fixture (session `bytes`) |
| send a line nested 20,000 deep | **the process ends** (exit 1) | executed on a fixture (session `deep`) |
| initialize a second time | accepted: a second result | executed on a fixture (session `lifecycle`, step 3) |
| run a tool through a notification | nothing: dropped, not run | executed on a fixture (session `lifecycle`, step 4) |
| change any data, or reach a file or the network through the server | no code that could | source-inspected; runtime: **uninspected** |

## Findings

1. All 30 answers in our client's run were the ones its source predicts, line by line. [executed on a fixture]
2. Two inputs a compatible client must not send end the server instead of being refused: a line that is not UTF-8
   (in the recorded environment) and a line nested 20,000 deep. Both leave a traceback on stderr and exit code 1.
   [executed on a fixture]
3. An extra argument is answered with the protocol error -32602, where the MCP 2025-11-25 tools page lists input
   validation as a tool execution error (`isError: true`). The server declares that version. [executed on a fixture;
   independently sourced]
4. `initialize` reads no params and is accepted any number of times. [source-inspected; executed on a fixture]
5. The tool reads one literal mapping and writes nothing but stdout; "public" in its description is a claim about the
   data that the code cannot make. [source-inspected]
6. The server keeps no record of its own; a review depends on the client's transcript. [source-inspected]
7. A subset of MCP 2025-11-25, not conformant, and not shown to be secure; the course presents it as a teaching
   subset. [source-inspected; independently sourced]

## Not checked

- File and network behavior at run time (no trace, no sandbox). **uninspected**
- Any other version of the file, and the course repo after `5639e4c8`. **uninspected**
- The bytes and deep cases under another locale or another Python than 3.12.14. **uninspected**
- Whether the fixture value is true in the world (E3). **uninspected**
- Anything outside the recorded transcript and the test named above.

## Facts the trust decision should rest on

- Source and provenance: the course instructor's file, MIT-licensed repository, blob `f33ea9de`, last changed
  2026-09-06; copied byte for byte, not downloaded.
- Capability: one literal mapping; no file, network or process code in the 72 lines (source-inspected); runtime
  behavior not traced.
- Protocol: a correct two-flag lifecycle for the cases run; no params checking on `initialize`; input validation
  answered as a protocol error.
- Robustness: two malformed inputs end the process (executed).
- Record keeping: none on the server side.
- Data and task: a course fixture, used here only for a local comparison through our client; never connected to Claude.
- What would reopen the decision: a new commit to the file, a second tool, a fixture that is read from a file or the
  network, connecting it to Claude Code or another host, or a task that relies on the fixture's value as a fact.

## Trust decision (Aravind's)

**Allow.** I trust commit `5639e4c8` for local comparison using its fixed course data and the existing read-only tool. I would reconsider if the code changes, another tool is added, it reads external files or network data, or it is connected to Claude Code.

*Aravind, 2026-11-22. In my own words; Claude Code only turned the dash into a full stop and marked the commit as code.*

