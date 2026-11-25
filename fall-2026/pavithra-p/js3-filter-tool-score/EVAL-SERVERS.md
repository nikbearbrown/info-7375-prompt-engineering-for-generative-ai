# Two tool servers, evaluated the same way

JS3 Step 2 (Chapter 8). My own server first, judged as if someone else had written it. Then one server I did not write. Both were driven by the same scripted client (`agent/mcp_client.py`), and every line each way is saved in `transcripts/`.

The questions, for both: what does it declare, what does it actually do, what is a compatible client not entitled to, and do I trust it?

## 1. My server: `js3-jobscore` (`agent/toolserver.py`)

Started with `python3 serve.py`. JSON-RPC 2.0 over stdio, one message per line, Python standard library only.

### What it declares

From the real `initialize` and `tools/list` answers in `transcripts/client-own-20261125T205341Z.jsonl`:

* Protocol version: it repeats the client's version if it supports it (2025-11-25, 2025-06-18, 2025-03-26 or 2024-11-05), or else offers 2025-11-25.
* Capabilities: tools only, `listChanged: false`. No resources, prompts or sampling.
* One tool, `score_posting(board, job_id)`. The board must be one of the four boards that answered, and the job_id must be 1 to 64 characters. No other argument is allowed.
* Annotations: `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`, `openWorldHint: false`.
* Description: it runs FILTER.md version 1.0 on one posting from the latest saved collection, reads only saved files, and makes no network request. The verdict is a filter record, not advice.

### What it actually does (checked)

| Declared | Checked by | Result |
|---|---|---|
| Read-only, writes nothing but its transcript | `test_transcript_has_both_directions_and_nothing_else_is_written`: every file's time is compared before and after a session | only the transcript changed |
| Writes stay inside its folder | `test_transcript_outside_its_folder_is_refused` | refused by the permission policy |
| No network | `test_makes_no_network_connection`: `socket.socket` raises if anything opens a connection | the call still worked |
| Only the declared arguments | transcript call 7 sends `path: ../../.ssh/id_rsa` | error -32602 "unexpected arguments" |
| Only the declared tool | transcript call 8 asks for `apply_to_job` | error -32602 "unknown tool" |
| Same verdict as the filter | transcript call 3 (the HELM posting): reject, score 4, the same as `runs/20261125T204144Z/filter-v1.0/decisions.jsonl` | matches |
| Does not guess | transcript call 6, an id not in the run | `isError: true`, "nothing was guessed" |

Where it does not do what it says, or says too little:

1. The failed board is unreachable. The server has an "I cannot tell: board failed" answer, but `lever:no-such-board` is not in the board list it declares, so transcript call 5 gets a schema error (-32602) instead. A client cannot learn from this tool that a board failed.
2. The board list is written in the code. If `config/boards.json` changes, the declared list does not, so the two can drift apart.
3. "Idempotent" holds only within one collection. The tool reads the latest run, so the same call can give a different answer after the next `watch`.
4. The description names version 1.0 because the filter file path is fixed in the code. If I change the filter, I have to change the description too, or it will claim the wrong version.
5. It answers `tools/call` before `initialize`. The protocol leaves that to the client, but a stricter server would refuse.

### What a compatible client is not entitled to

* Not the posting's full text, the résumé, or any file path. The server reads the fictional résumé but never returns it.
* Not any action: there is no apply, send, write or fetch tool. A client that asks for one gets an error, as in transcript call 8.
* Not "keep" as a recommendation. It is the filter's record, and whether a posting is worth Rohan's time stays my judgment (`SIGNOFF.md`).
* Not any promise beyond the declared fields: the schema says what may be sent, and anything else is refused.

### Trust decision

Allowed, with limits. Claude may call `score_posting` only, through `--allowedTools mcp__jobscore__score_posting`, with no other tools in that session. I trust it to be read-only and offline because tests check both, not because its annotations say so: annotations are claims the server makes about itself. I do not trust its verdicts as advice. Problems 1 to 4 above are listed in `SIGNOFF.md` under "Not checked" or fixed there.

## 2. The other server: `js3-postings` by Lavanya Rajesh

Source: `fall-2026/lavanya-r/js3-filter-tool-score/mcp/server.py` in the course repository, her folder at commit `d32b8bc` (2026-11-25). The file is unchanged since `309c996`.

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
| 3,117 postings on 6 boards | ran her own `python3 -B -m agent.corpus runs/2026-11-24T220432Z-live` | 3,117 on 6 boards: matches |
| Whole-word search, ignoring case | "Helm" (call 4) | 6 matches; all 6 that I read are the Kubernetes tool (Terraform, Helm), so in her data this word is not a false friend |
| The query is text, not a pattern | ".*" (call 5) | 0 results: the query is escaped |
| Only declared arguments | `path: ../../.ssh/id_rsa` (call 6) | -32602 "unknown argument(s)" |
| Limit at most 20 | limit 1000 (call 7) | -32602 |
| Board names from its corpus only | board `../../etc` (call 8) | -32602 "no board" |
| Writes nothing | `find -newer` over its folder after the run | no file changed |
| Fetches nothing live | read the imports (above) | no network module; I did not block the network while it ran, so this is from reading the code, not a test |

Where it differs from what a client might expect:

1. An unknown tool (call 9, `apply_to_job`) comes back as a normal result with `isError: true`, not as a protocol error. The MCP specification treats an unknown tool as a protocol error (-32602). A client may then pass "unknown tool" to the model as if a tool had run and failed.
2. The results are not ranked. They come in key order (`ats/board/id`, alphabetical), and `limit` cuts that list. Searching "backend engineer" with limit 3 (call 3) gave the first three OpenAI keys out of 4 matches. A client is not entitled to read the first results as the best ones; the tool only promises that the word is there. This is the same "relevance is not entailment" point as my shortlist.
3. Asked for protocol 2025-11-25 (call 12), it answered 2025-06-18. That is allowed by the protocol, but a client that only speaks the newest version would have to stop.
4. It accepts `initialize` twice and tool calls without it, like mine.

### What a compatible client is not entitled to

* Not the full posting text. It returns key, title, locations, URL and the field that matched.
* Not more than 20 results per call, not any file outside its run folder, not a live fetch, not any write.
* Not completeness or ranking (point 2): `count_total` says how many matched, and the client has to page or narrow the query.

### Trust decision

Allowed for read-only search, with the same limit as mine: only that one tool, in a session with no other tools. My reasons:
* I read the code, and it cannot write or fetch;
* it refused every out-of-bounds request I sent;
* its declared count was true.

I would not let an agent treat its first results as the best matches, or treat a match as evidence that the posting fits (point 2).

## 3. The same checks, side by side

| Check | Mine | Hers |
|---|---|---|
| Undeclared argument | refused (-32602) | refused (-32602) |
| Undeclared tool | protocol error (-32602) | `isError` result |
| Writes | transcript only, tested | none, checked once with `find` |
| Network | none, tested with a blocked socket | none, from reading the imports |
| A claim in its description that I could check | verdict equals the filter's record | 3,117 postings, true |
| Weak spot I found | failed board unreachable; the board list and version are written in the code | unranked results cut by `limit` |
