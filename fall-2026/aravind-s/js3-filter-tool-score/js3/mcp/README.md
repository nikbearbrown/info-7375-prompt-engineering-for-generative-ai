# JS3 step 2 item 3: the agent as a tool (MCP)

The agent's filter offered to Claude as one tool, through a Model Context Protocol server written from scratch, with
the real transcripts in both directions and two evaluations: of our server, and of the course's lesson 8 reference
server. Python 3 standard library only; tested on Python 3.12.14 and 3.9.6. The live client run used the Claude Code
CLI 2.1.326 that the Claude desktop app bundles.

Claude Code built the server, the client, the Claude Code run script and the tests, ran them, and drafted the two
evaluations, at my request. The trust decision at the end of each evaluation is mine. On 2026-11-24 Claude Code added
the runtime trace (below) and put its evidence into both evaluations.

## What is here

| Path | What it is |
|---|---|
| `job_agent/mcp_server.py` | The server: stdio, newline-delimited JSON-RPC 2.0, protocol `2025-11-25`, one read-only tool `score_posting(board, posting_id)`. Its docstring holds the lifecycle table every answer follows. |
| `tools/mcp_client.py` | Our own client: the normal requests, then the requests a client is not entitled to, with the expected answer of each written before the run. |
| `tools/mcp_claude_run.py` | The one live run with Claude Code as the client. |
| `js3/mcp/other-server/main.py` | The lesson 8 reference server, copied byte for byte (provenance below). |
| `js3/mcp/transcripts/` | Every transcript (next table). |
| `js3/mcp/EVALUATION-OWN.md` | Our server: the four ledgers, declared against actual, what a client is not entitled to, the findings, and my trust decision. |
| `js3/mcp/EVALUATION-OTHER.md` | The same for the lesson 8 reference server. |
| `tests/test_mcp_server.py`, `tests/test_mcp_client.py` | 33 and 10 tests. |
| `js3/checks/mutants-2026-11-21-mcp.txt` | The full mutants run with six planted server mistakes. |
| `tools/mcp_runtime_trace.py`, `tools/mcp_trace_boot.py` | The runtime trace (2026-11-24): each server, its code unchanged, run under a Python audit hook (PEP 578) through our client's five sessions; what it opens, writes, connects to and starts, and its answers compared across runs. |
| `js3/mcp/runtime/2026-11-25T023441Z/` | The trace's evidence, recorded on 2026-11-24 (the name is UTC), on Python 3.12.14 and 3.9.6: an event summary (JSON and Markdown) and the client's transcript for each run, and the comparisons. Its README says what the runs show and gives the command that re-checks them. |
| `tests/test_mcp_runtime_trace.py` | 17 tests of the trace: a planted write, socket and process are caught, reads and writes are told apart, a planted environment value never comes out, the traced server's stdout is JSON-RPC only, a known small run's summary. |

## How to run

From the repo root:

```bash
# The server (it waits for JSON-RPC lines on stdin; Ctrl-D ends it). -B keeps Python from writing bytecode caches.
python3 -B -m job_agent.mcp_server
python3 -B -m job_agent.mcp_server --transcript js3/mcp/transcripts/NAME.jsonl   # also keep the server's own record

# Our client, against our server or against the lesson 8 reference server (each writes new dated transcripts)
python3 tools/mcp_client.py own
python3 tools/mcp_client.py other

# Claude Code as the client: without --live it only prints the command. The one live call was made on 2026-11-21.
python3 tools/mcp_claude_run.py --board ashby-openai --posting-id f3ddd41c-541f-485e-90d6-86c26e018e9f
python3 tools/mcp_claude_run.py --board ashby-openai --posting-id f3ddd41c-541f-485e-90d6-86c26e018e9f --live

# The runtime trace: every run (both servers: traced, with --transcript, with the network denied, our server at
# a54c424, and not traced), saved in js3/mcp/runtime/<UTC time>/; then the same runs again, compared with that folder
python3 tools/mcp_runtime_trace.py record --python /opt/homebrew/bin/python3.12 --python /usr/bin/python3
python3 tools/mcp_runtime_trace.py check js3/mcp/runtime/2026-11-25T023441Z

# The tests, and the planted mistakes
python3 -m unittest discover -s tests -t .
python3 tools/mutants.py
```

`--transcript` accepts only a `.jsonl` file directly inside `js3/mcp/transcripts/`; any other path is refused with exit
code 3 before the server reads a message. Without it, the server writes nothing.

## What each transcript shows

All times are UTC. In every file the repo folder is written as `<repo>`, the home folder as `~`, and Claude Code's
temporary folder as a placeholder, so no record names this Mac's account.

| File | Written by | What it shows |
|---|---|---|
| `2026-11-21T084407Z-own-client.jsonl` | `tools/mcp_client.py own` | Every line our client sent to our server and every line it got back, with times, in five sessions (each on a fresh process): `early`, `main`, `lifecycle`, `bytes`, `deep`. Also each step's expected and actual answer, the comparison with the server's own record, and the evidence checks against the committed filter run. 31 of 31 answers as expected. |
| `2026-11-21T084407Z-own-client.md` | the same | The same run, readable: a summary table, then each message laid out, with tool results' JSON text parsed. |
| `2026-11-21T084407Z-own-server.jsonl` | our server (`--transcript`) | The server's own record of the same five sessions: a start event, every line in (`in`) and out (`out`), an end event with the reason. It matches the client's record line for line (57 lines). |
| `2026-11-21T084408Z-other-client.jsonl` and `.md` | `tools/mcp_client.py other` | Our client against the lesson 8 reference server, the same five sessions with the reference's tool (`lookup`). 30 of 30 answers as its source predicts, including the two sessions where the reference process ends (a line that is not UTF-8, a line nested 20,000 deep); its tracebacks are recorded. The reference keeps no record of its own. |
| `2026-11-21T084542Z-claude-code-server.jsonl` and `.md` | our server (`--transcript`), started by Claude Code | The one live Claude Code session, as the server saw it: Claude Code's `server/discover` probe (refused with -32000), `initialize`, `notifications/initialized`, `tools/list`, one `tools/call` and its answer, and the end ("interrupted": SIGINT from Claude Code). |
| `2026-11-21T084542Z-claude-code-init.json` | `tools/mcp_claude_run.py` | Claude Code's init event: what it loaded (our one server, our one tool, no skill, no slash command, the seat's login, dontAsk). Its `cwd` shows `/private` before the placeholder: the script replaced the shorter spelling of the macOS temporary folder first (fixed in the script afterwards; the saved file is left as written). |
| `2026-11-21T084542Z-claude-code-events.jsonl` | the same | Every event Claude Code printed, in order, except `rate_limit_event`: the init event, the tool call, the tool result as passed to the model, Claude's answer, and the result event (model `claude-sonnet-5-5`, 2 turns, 4.1 s). |
| `2026-11-21T084542Z-claude-code-answer.md` | the same | Claude's final answer word for word, with the date, the model, the prompt and the system prompt, and the run's nine checks. |
| `2026-11-21T084542Z-claude-code-run.json` | the same | The command (all flags), the prompts, the environment's variable names, the exit code and the checks with what each one saw. Seven passed; two failed on client behavior the script did not expect (`EVALUATION-OWN.md`, finding 5). |

## The runtime trace (2026-11-24)

The evaluations first said that run-time file and network behavior was uninspected. On 2026-11-24 Claude Code ran
each server, its code unchanged, under a Python audit hook (`tools/mcp_trace_boot.py` installs it, then runs the
server with `runpy`) through our client's five sessions, on Python 3.12.14 and 3.9.6: traced, traced with
`--transcript` (ours), traced with the network denied by `sandbox-exec`, our server at `a54c424`, and not traced. The
hook keeps arguments only for an allowlist of events (file paths, modes and flags, socket addresses, a started
program's file name, module names) and never an environment value. Everything is in
`js3/mcp/runtime/2026-11-25T023441Z/`, whose README says what the runs show; in short, for these sessions on these
inputs: neither server wrote a file (ours only the transcript it was asked for), created a socket or started a
process; with the network denied every answer was the same; on Python 3.9.6 the standard library's `platform`, which
our server imports, loads `subprocess` without starting anything; and our server at `a54c424` gives the same answers as
today's except FILTER.md's SHA-256. Evidence type: executed on a fixture. It is not proof for every input.

## The other server's provenance

`js3/mcp/other-server/main.py` is `lessons/08-mcp-from-scratch/code/main.py` from the course repository
(github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai), taken with `git show` from my local clone's
`upstream/main` at commit `5639e4c8`; nothing was downloaded. Git blob `f33ea9de` (the same as upstream), SHA-256
`948337af...8b1769`. The file was last changed in commit `a8629ce1` (2026-09-06, Nik Bear Brown). The repository's
LICENSE is the MIT License. The copy is unchanged (checked again on 2026-11-24 against the clone's blob at `5639e4c8`);
the evaluation's line numbers refer to it.

## Notes

- `.gitignore` ignores every `transcripts/` folder as a privacy fence, with one exception, `js3/mcp/transcripts/`:
  these are protocol transcripts about the fictional persona and public postings, not conversations.
- The client deliberately sends lines a client must not send (MCP's transports page: "The client MUST NOT write
  anything to the server's stdin that is not a valid MCP message") to see what each server does with them.
- The postings in the transcripts were chosen outside the reject audit's cards, the held-out set's cards and the
  shortlist, so no blind card's verdict appears here.
