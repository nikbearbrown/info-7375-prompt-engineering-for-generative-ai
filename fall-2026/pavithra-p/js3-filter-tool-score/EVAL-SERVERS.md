# Three tool servers, evaluated the same way

JS3 Step 2 (Chapter 8). My own server first, judged as if someone else had written it. Then two servers I did not write: a classmate's, and a well-known one, Claude Code's own `claude mcp serve` (section 4). All three were driven by the same scripted client (`agent/mcp_client.py`), and every line each way is saved in `transcripts/`. Claude itself was also a client of my server (section 1, "Claude as the client").

| Transcript | Client | Server | When (UTC, 2026-11-25) |
|---|---|---|---|
| `client-own-20261125T205341Z.jsonl` and `server-20261125T205341Z.jsonl` | my scripted client | mine, filter v1.0 | 20:53 (first recording) |
| `claude-client-20261125T210918Z.jsonl` and `server-20261125T210918Z.jsonl` | Claude Code | mine, filter v1.0 | 21:09 |
| `client-own-20261125T210944Z.jsonl` and `server-20261125T210944Z.jsonl` | my scripted client | mine, filter v1.1 (final) | 21:09 |
| `claude-client-20261125T210948Z.jsonl` and `server-20261125T210949Z.jsonl` | Claude Code | mine, filter v1.1 | 21:09 |
| `client-own-20261125T220131Z.jsonl` and `server-20261125T220131Z.jsonl` | my scripted client | mine, v1.1, boards read from config | 22:01 |
| `claude-client-20261125T220131Z.jsonl` and `server-20261125T220132Z.jsonl` | Claude Code | the same | 22:01 |
| `client-own-20261125T223407Z.jsonl` and `server-20261125T223407Z.jsonl` | my scripted client | mine, final (with the review fixes in point 6) | 22:34 |
| `claude-client-20261125T223407Z.jsonl` and `server-20261125T223408Z.jsonl` | Claude Code | mine, final | 22:34 |
| `client-other-lavanya-r-20261125T205405Z.jsonl` | my scripted client | Lavanya Rajesh's `js3-postings` | 20:54 |
| `client-other-lavanya-r-blocked-20261125T215826Z.jsonl` | my scripted client | the same, with the network blocked | 21:58 |

The earlier recordings were made before the fixes below; they are kept as they were. All client-side transcripts were redacted before publishing (`scripts/redact_transcripts.py`). Exactly these changes were made:
* Local paths became `<HOME>`, `<TMP>` or `<SANDBOX>`, wherever they appeared. This includes the start-up lines and the file paths inside the `claude mcp serve` Read and Write messages.
* In Claude Code's first message as a client, the lists that describe my machine and setup were dropped, and its rate-limit lines were removed.
* In the `claude mcp serve` transcript, each of the 28 tool descriptions in its tools/list answer became "<redacted: N characters>". The names, input schemas and other fields stay.

Apart from these, every message, tool call, tool result and Claude reply is as recorded. The server-side files had no paths and are not changed. Two of these files (`client-own-20261125T205341Z.jsonl` and `client-other-lavanya-r-20261125T205405Z.jsonl`) were first committed unredacted in `70ddf4b`. The 22:34 ones are the final server. The 22:01 ones came before the two review fixes in point 6. Each client file is that side's view (what it sent and received); each server file is the server's own log of every line it received and sent.

The questions, for both: what does it declare, what does it actually do, what is a compatible client not entitled to, and do I trust it?

The protocol facts below come from the MCP specification, server tools page, version 2025-06-18 (modelcontextprotocol.io/specification/2025-06-18/server/tools, read 2026-11-25): `tools/list` and `tools/call`, the `tools` capability, unknown tools as a protocol error with code -32602, and "clients MUST consider tool annotations to be untrusted unless they come from trusted servers".

## 1. My server: `js3-jobscore` (`agent/toolserver.py`)

Started with `python3 serve.py`. JSON-RPC 2.0 over stdio, one message per line, Python standard library only.

### What it declares

From the real `initialize` and `tools/list` answers in `transcripts/client-own-20261125T223407Z.jsonl`:

* Protocol version: it repeats the client's version if it supports it (2025-11-25, 2025-06-18, 2025-03-26 or 2024-11-05), or else offers 2025-11-25.
* Capabilities: tools only, `listChanged: false`. No resources, prompts or sampling.
* One tool, `score_posting(board, job_id)`. The board must be one of the five boards in `config/boards.json` (read when the tools are listed), and the job_id must be 1 to 64 characters. No other argument is allowed.
* Annotations: `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: false`.
* Description: it runs FILTER.md version 1.1 on one posting from the latest saved collection, reads only saved files, and makes no network request. The verdict is a filter record, not advice. The version in the description is read from the filter file the server really uses.

### What it actually does (checked)

| Declared | Checked by | Result |
|---|---|---|
| Read-only, writes nothing but its transcript | `test_transcript_has_both_directions_and_nothing_else_is_written`: every file's time is compared before and after a session | only the transcript changed |
| Writes stay inside its folder | `test_transcript_outside_its_folder_is_refused` | refused by the permission policy |
| No network | `test_makes_no_network_connection`: `socket.socket` raises if anything opens a connection | the call still worked |
| Only the declared arguments | transcript call 7 sends `path: ../../.ssh/id_rsa` | error -32602 "unexpected arguments" |
| Only the declared tool | transcript call 8 asks for `apply_to_job` | error -32602 "unknown tool" |
| Same verdict as the filter | transcript call 3 (the HELM posting): reject, score 3 under v1.1, the same as `runs/20261125T204144Z/filter-v1.1/decisions.jsonl` (score 4 under v1.0 in the 20:53 recording) | matches |
| Does not guess | transcript call 6, an id not in the run | `isError: true`, "nothing was guessed" |

Where it does not do what it says, or says too little:

1. Found and fixed: in the first version, the failed board could not be reached. The server had an "I cannot tell: board failed" answer, but `lever:no-such-board` was not in the board list it declared, so call 5 got a schema error (-32602) in the 20:53 and 21:09 recordings. Now the board list includes it, and call 5 answers "I cannot tell: board lever:no-such-board failed" in the 22:01 and 22:34 recordings (`test_declared_boards_come_from_config_and_a_failed_board_says_cannot_tell`).
2. Found and fixed: the board list was written in the code, so it could drift from `config/boards.json`. It is now read from that file each time the tools are listed (same test).
3. "Idempotent" holds only within one collection. The tool reads the latest run, so the same call can give a different answer after the next `watch`.
4. Found and fixed: the first version's description said "version 1.0" as fixed text, so after a filter change it would have claimed the wrong version. It now reads the version from the filter file (`test_tools_list_declares_one_read_only_tool`). The filter file's path is still fixed in the code.
5. It answers `tools/call` before `initialize`. The protocol leaves that to the client, but a stricter server would refuse.
6. Found by a ChatGPT review and fixed: a request whose `params` was a list, not an object, crashed the server (`AttributeError`), ending the session. It now answers -32602 "params must be an object" (the last calls of the 22:34 recording: the list `params`, then a `ping` that is still answered). An unexpected exception raised while a request is being handled is answered -32603 and the session goes on. Errors outside the request handler, such as the process being killed, are not covered (`test_params_that_are_not_an_object_are_refused_not_a_crash`, `test_an_unexpected_error_is_reported_and_the_session_goes_on`). The same review found that the declared version was read fresh while the filter used was loaded once; both now come from the same load (`test_declared_version_is_the_version_used`).

### Claude as the client

`python3 scripts/transcript_claude_client.py` offers the server to Claude Code in print mode:
* the server is the only MCP server (`--strict-mcp-config`);
* every built-in tool is off (`--tools ""`);
* `score_posting` is the one tool allowed (`--allowedTools mcp__jobscore__score_posting`);
* Claude runs from an empty folder.

The CLI's own first message lists the tools Claude had: only `mcp__jobscore__score_posting`. The model was `claude-opus-5-5`.

In the final recording (22:34), Claude called the tool twice, with exactly the two board and job_id pairs I asked for. It reported both verdicts, scores and reasons as the tool gave them (reject 3, keep 5, filter v1.1). Asked whether the tool could apply or show the full posting, it said no: "The tool says it is read-only and "never applies, sends or changes anything."" The 21:09 and 22:01 recordings gave the same calls and the same answer in other words.

Claude believed the server's description and annotations; it had no way to check them. My tests are what check them. A server whose description lied would have been believed just the same, so the declaration is a claim, and only checking the behaviour makes it more than that.

### What a compatible client is not entitled to

* Not the posting's full text, the résumé, or any file path. The server reads the fictional résumé but never returns it.
* Not any action: there is no apply, send, write or fetch tool. A client that asks for one gets an error, as in transcript call 8.
* Not "keep" as a recommendation. It is the filter's record, and whether a posting is worth Rohan's time stays my judgment (`SIGNOFF.md`).
* Not any promise beyond the declared fields: the schema says what may be sent, and anything else is refused.

### Trust decision

Allowed, with limits. Claude may call `score_posting` only, through `--allowedTools mcp__jobscore__score_posting`, with no other tools in that session. I trust it to be read-only and offline because tests check both, not because its annotations say so: annotations are claims the server makes about itself, and the specification says a client must treat them as untrusted unless the server is trusted. I do not trust its verdicts as advice. Problems 1, 2, 4 and 6 are fixed; problems 3 and 5 are listed in `SIGNOFF.md`.

## 2. The other server: `js3-postings` by Lavanya Rajesh

Source: `fall-2026/lavanya-r/js3-filter-tool-score/mcp/server.py` in the course repository, Lavanya's folder at commit `d32b8bc` (2026-11-25). The file is unchanged since `309c996`.

I read `mcp/server.py` and `agent/corpus.py` before running anything:
* they import only `json`, `os`, `pathlib`, `re`, `sys`, `gzip`, `hashlib` and `html`, so no network module;
* they never open a file for writing.

I ran it from a `git archive` copy outside my folder, unchanged, with `python3 -B mcp/server.py`. My scripted client sent the same kinds of requests as to my own server. Transcript: `transcripts/client-other-lavanya-r-20261125T205405Z.jsonl`.

### What it declares

* Protocol versions 2025-06-18, 2025-03-26 and 2024-11-05. Capabilities: `tools: {}`.
* One tool, `search_postings(query, board?, limit?)`. The query is 1 to 200 characters, limit is 1 to 20 (default 10), and no other argument is allowed.
* Annotations: `readOnlyHint: true`, `openWorldHint: false`. It declares nothing about destructive or idempotent.
* Description: "Read-only search over the job postings saved by the JS3 collection run of 2026-11-24 (6 public boards, 3,117 postings)… Fetches nothing live."

### What it actually does (checked)

| Declared | What I did | Result |
|---|---|---|
| 3,117 postings on 6 boards | ran Lavanya's own `python3 -B -m agent.corpus runs/2026-11-24T220432Z-live` | 3,117 on 6 boards: matches |
| Whole-word search, ignoring case | "Helm" (call 4, limit 5) | `count_total` 6, 5 returned; all 5 returned are the Kubernetes tool (Terraform, Helm), so in Lavanya's data this word does not look like a false friend. The sixth was not returned and not read |
| The query is text, not a pattern | ".*" (call 5) | 0 results: the query is escaped |
| Only declared arguments | `path: ../../.ssh/id_rsa` (call 6) | -32602 "unknown argument(s)" |
| Limit at most 20 | limit 1000 (call 7) | -32602 |
| Board names from its corpus only | board `../../etc` (call 8) | -32602 "no board" |
| Writes nothing | a marker file, the same 13 messages, then `find <copy> -newer <marker>` | no file changed; the commands and output are saved in `evidence/other-server-write-check.txt` (23:02 UTC), with that run's transcript `client-other-lavanya-r-20261125T230240Z.jsonl` |
| Fetches nothing live | read the imports (above), then ran it again through `scripts/run_blocked.py`, which makes every socket raise before the server starts | the same 13 answers with the network blocked (`client-other-lavanya-r-blocked-20261125T215826Z.jsonl`); `tests/test_run_blocked.py` checks that the blocker really blocks |

Where it differs from what a client might expect:

1. An unknown tool (call 9, `apply_to_job`) comes back as a normal result with `isError: true`, not as a protocol error. The specification lists unknown tools under protocol errors (its example is code -32602, "Unknown tool"), and keeps `isError` for a tool that ran and failed. A client may then pass "unknown tool" to the model as if a tool had run and failed.
2. The results are not ranked. They come in key order (`ats/board/id`, alphabetical), and `limit` cuts that list. Searching "backend engineer" with limit 3 (call 3) gave the first three OpenAI keys out of 4 matches. A client is not entitled to read the first results as the best ones; the tool only promises that the word is there. This is the same "relevance is not entailment" point as my shortlist.
3. Asked for protocol 2025-11-25 (call 12), it answered 2025-06-18. That is allowed by the protocol, but a client that only speaks the newest version would have to stop.
4. It accepts `initialize` twice and tool calls without it, like mine.

### What a compatible client is not entitled to

* Not the full posting text. It returns key, title, locations, URL and the field that matched.
* Not more than 20 results per call, not any file outside its run folder, not a live fetch, not any write.
* Not completeness or ranking (point 2): `count_total` says how many matched, and the client has to page or narrow the query.

### Trust decision

Allowed for read-only search, with the same limit as mine: only that one tool, in a session with no other tools. My reasons:
* I read the code, and it cannot write; with the network blocked it gave the same answers;
* it refused every out-of-bounds request I sent;
* its declared count was true.

I would not let an agent treat its first results as the best matches, or treat a match as evidence that the posting fits (point 2).

## 3. The same checks, side by side

| Check | Mine | Lavanya's `js3-postings` | `claude mcp serve` (section 4) |
|---|---|---|---|
| Tools declared | 1, read-only, annotated | 1, read-only, annotated | 28, none annotated |
| Undeclared argument or malformed request | refused (-32602) | refused (-32602) | a list as `params` got no answer at all |
| Undeclared tool | protocol error (-32602) | `isError` result | internal error (-32603) |
| Writes | transcript only, tested | none, checked with a saved `find` | wrote a file inside and outside its start folder, no prompt |
| Reads | its own saved files only | its own corpus only | read a file outside its start folder |
| Network | none, tested with a blocked socket | none, tested with the network blocked | declares WebFetch and WebSearch (not called) |
| Weak spot I found | failed board unreachable and board list written in the code (both fixed); the filter file's path is still fixed in the code | unranked results cut by `limit`; unknown tool as a result, not an error | no confinement and no annotations |

## 4. A well-known server: Claude Code's own `claude mcp serve`

Source: Claude Code 2.1.294, already installed on my machine (`claude mcp serve` makes Claude Code itself an MCP server). Nothing was downloaded. Probe: `python3 scripts/probe_claude_mcp_serve.py`, run twice. The first run, at 23:09 UTC, hung on the last request until I stopped the server; I added a timeout to my client and ran it again at 23:16 UTC, with the same answers. The 23:16 output is in `evidence/claude-mcp-serve-check.txt` and its transcript in `transcripts/client-claude-mcp-serve-20261125T231622Z.jsonl`. The first run's transcript was replaced by the second.

How I kept it safe:
* the server was started in a new temporary folder, `<SANDBOX>/allowed/`, with a sibling `<SANDBOX>/outside/`, both holding only CONSTRUCTED files, deleted afterwards;
* I called only Read and Write, and only on those files;
* I called none of the tools that can run commands, reach the network, publish or message.

### What it declares

* Protocol 2025-06-18, `tools` with `listChanged: true`, server `claude/tengu` 2.1.294.
* 28 tools, and none has annotations: no `readOnlyHint`, no `destructiveHint`. They include:
  * Bash (any shell command);
  * Edit and Write;
  * WebFetch and WebSearch (network);
  * Artifact and ArtifactData (publishing to claude.ai);
  * SendMessage and PushNotification;
  * CronCreate and RemoteTrigger (scheduled and remote jobs).
* Some of these appear because of my own Claude Code setup. So the tool list depends on the machine, not only on the server.

### What it actually does (checked)

| What I sent | Result |
|---|---|
| Read a file inside its start folder | returned the file |
| Read a file in the sibling folder, outside its start folder | returned the "secret" file's content |
| Write a new file inside its start folder | created it, with no prompt |
| Write a new file in the sibling folder | created it, with no prompt (the sandbox afterwards held `outside/new.txt`) |
| An undeclared tool | error -32603 "Tool apply_to_job not found" (the specification's example for an unknown tool is -32602) |
| `params` as a list | no answer at all. In the first run my client waited until I stopped the server by hand; in the second it recorded "no answer within 20 s" (`agent/mcp_client.py`, `tests/test_mcp_client.py`) |

### What a compatible client is not entitled to

* To assume the start folder confines it. Read and Write reached outside it.
* To assume a person is asked before a write. Neither write was stopped or asked about in this mode.
* To tell safe tools from dangerous ones from the declaration. With no annotations, Read and Bash look the same to a client.
* To a stable tool list. It changes with the host's setup.

### Trust decision

Not trusted as a tool server for any client I do not control, and not for my agent.
* It exposes Claude Code's whole set of tools, not one task.
* Nothing in its declaration separates read-only tools from tools that run commands, write, publish or message.
* In my probe, its file tools were not limited to the folder it was started in.

I would run it only inside a throwaway folder with no secrets, and I would not let another model call Bash, Write, Edit, WebFetch, Artifact, SendMessage or the scheduling tools through it. My own server, by contrast, has one declared read-only tool, checked by tests.

Not checked: whether any Claude Code setting confines these tools when it runs as a server. I ran it as installed, with my normal settings.
