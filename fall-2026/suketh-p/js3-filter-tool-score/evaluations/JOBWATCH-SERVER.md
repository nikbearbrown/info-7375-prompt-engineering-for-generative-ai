# Evaluation: this folder's tool server, `jobwatch-js3` 0.1.1 (`score_posting`)

Claude Code drafted this evaluation on 2026-11-24 from the source, the tests and the transcripts listed below, and checked it the way the brief asks: as if someone else had written the server. **The trust decision at the end is the student's** (Chapter 8: "the decision is yours: allow, deny, or pending, in your own words").

Evidence types, as Chapter 8 defines them: **advertised** (the server says it), **source-inspected** (the code was read), **executed** (ran on a fixture or a real session), **independently sourced** (checked against a second record), **uninspected**.

**Sources:**
- [jobwatch/mcp_server.py](../jobwatch/mcp_server.py) and the modules it imports: [corpus.py](../jobwatch/corpus.py), [screen.py](../jobwatch/screen.py), [location.py](../jobwatch/location.py), [normalize.py](../jobwatch/normalize.py), [ats.py](../jobwatch/ats.py), [board.py](../jobwatch/board.py).
- Tests: [tests/test_mcp_server.py](../tests/test_mcp_server.py) and [tests/test_mcp_wrong_servers.py](../tests/test_mcp_wrong_servers.py).
- The real Claude Code session, with server 0.1.0: [server side](../transcripts/2026-11-24-claude-code-session.jsonl), [host side](../transcripts/2026-11-24-claude-code-session-host.jsonl), [configuration](../transcripts/2026-11-24-claude-code-session-command.json).
- The harness runs: [0.1.0](../transcripts/2026-11-24-jobwatch-harness.jsonl) and [0.1.1](../transcripts/2026-11-24-jobwatch-harness-0.1.1.jsonl).
- Claude's leads: [the reply](claude-leads/jobwatch-reply.json).

## What it declares, and what it does

| What the server declares (where) | What it does | Evidence |
| --- | --- | --- |
| One tool, `score_posting` (`tools/list`) | One tool. The dispatch branch accepts only that name, and any other name gets `-32602` | source-inspected; executed |
| "Reads only saved files; no network; writes nothing" (tool description). `readOnlyHint: true`, `openWorldHint: false` (annotations) | It reads `runs/2026-11-24-js3-corpus/trace.json` and the three `raw/*.body.gz` once, plus `jobwatch/data/iso3166.tab`. The imports are `gzip`, `hashlib`, `json`, `pathlib`, `html`, `re` and `dataclasses`, with no network or process module and no `print`. Under the audit hook, two harness runs saw 49 file opens, all reads, and no writes, sockets or processes | source-inspected; executed (this version, these inputs) |
| Input schema: `board` from three values, `posting_key` a string of 1–300 characters, both required, nothing else | `_call` checks exactly those conditions | source-inspected; executed (the schema test) |
| "Greenhouse: the numeric id, as text. Ashby: the jobUrl" (schema text) | **Not checked.** Any string of 1–300 characters is looked up, and an unknown key gets a tool error | source-inspected; executed (`does-not-exist`) |
| Returns "the score and its parts, the matched words, the location outcome and the fate" (description) | It returns those, plus fields the description doesn't name: `title`, `captured_at`, `description_blank`, `reasons`, `review_reasons`, and the location text and words. **No `outputSchema` is declared** | executed |
| "the student's FILTER.md v0.1 result" (description) | The value equals `screen.score` recomputed on the saved posting, and `screen.py`'s word lists and numbers equal FILTER.md's | executed (`test_the_value_matches_the_declared_source`, `tests/test_filter_doc.py`); independently sourced (the record served in the real session equals the committed `audit/v0.1` row for key 4020350008) |
| Tool requests refused until `initialize` and `notifications/initialized` (docstring) | Holds. In the harness, `tools/list` was refused before `initialize` (id 1) and again after it but before the notification (id 3) | executed |
| (implicit) MCP 2025-11-25 behaviour | `ping` is answered in any state. Request ids must be strings or integers. **0.1.1:** arguments that break the input schema come back as `isError` results, as the spec's tools page says. 0.1.0 returned `-32602` for them (see the leads below) | executed; spec read 2026-11-24 |
| (not declared) | A second `initialize` is accepted in any state. A repeated request id isn't detected. A notification-shaped line with a bad `jsonrpc` value gets an error response | source-inspected |

## What a compatible client is not entitled to conclude

- **That "kept" means the job is worth applying to.** The description says the result "describes the filter's decision, not whether the job is worth applying to." In the real session Claude declined to infer it: "This result can't answer that." That's one run, so it's not a property of Claude.
- **That the location outcome is right.** The U.S. test counts two-letter codes. `"ca"` can be Canada, a risk named in the option the student chose. The record says *which words* matched, not where the job is.
- **That the data is current.** Every posting was captured at 2026-11-24 22:36 UTC. Postings change, and the tool never fetches.
- **That `isError: false` and a matching id make the content true.** They show which request the answer belongs to and that the lookup ran. They don't show that the filter is any good. That is measured separately, by the reject audit and the held-out labels.
- **That the server is read-only in general.** The audit hook saw no writes on these inputs, in this version. Native code or `ctypes` could avoid the hook.
- **That it conforms to MCP.** It is a subset: tools only, with no resources, prompts, logging, progress or cancellation. It does not detect repeated request ids.

## The four ledgers

| Ledger | Line | Evidence | Reopens if |
| --- | --- | --- | --- |
| Protocol | `initialize` → result (version echoed if supported, else 2025-11-25), then `notifications/initialized` → no response, then `tools/list` and `tools/call` | executed: the Claude Code session (client `claude-code` 2.1.291 asked for 2025-11-25) and the harness | a new protocol version, or a new client |
| Protocol | Requests before readiness get `-32000`. A parse error gets `-32700` with id null. An unknown method gets `-32601`. Bad params shape or an unknown tool get `-32602`. Schema violations get `isError` | executed (harness 0.1.1); source-inspected | any change to `handle` or `_call` |
| Capability | Reads the saved corpus and `iso3166.tab`. No writes, no network, no processes | source-inspected; executed (audit hook) | a new tool, a new import, a new data source |
| Capability | The transcript is written by the tap, a separate process, not by the server | source-inspected (`mcp_tap.py`) | the tap gaining any other write |
| Permission | Task: look up the JS3 filter's decision on one saved public posting. Data: public postings from the allow-listed boards (JS2's permission policy). Effects allowed: none beyond returning text. Results go to the host's context and the transcript | the brief ("must not expose anything that can send or change data outside your own folder"); JS2 GATE.md | a wider task, new boards, or any effect beyond reading |
| Evidence | The returned record equals FILTER.md v0.1 recomputed on the saved posting, and equals the committed audit row | executed; independently sourced | a changed corpus or a new FILTER.md version |
| Evidence | Whether the filter's decision is *right* | **not established by this server**. See the reject audit and the held-out measurement | — |

## The handoff, for the real session

| Handoff | What passes | Trusted to be | How that trust is earned |
| --- | --- | --- | --- |
| Server → host | The record for `greenhouse/anthropic` 4020350008: kept, score 2 (role 1 + description topic 1, `machine learning`), location `us` from `new york`, `ca`, `ny`, `wa` | FILTER.md v0.1's output for that saved posting, from server 0.1.0 | It equals `screen.score` on the saved posting and the committed audit row (checked 2026-11-24) |
| Host → Claude's context | The same JSON, as the `tool_result` content (the host-side stream shows it unchanged) | Data about a filter decision. Not an instruction, and not advice | The recorded host configuration (built-in tools off, only this server, only this tool), plus the tool description and the prompt |
| Claude → answer | "Fate: kept … Score: 2 … Location: outcome `us`", and on applying: "This result can't answer that" | A restatement of the tool's output | Every number and word in Claude's answer was compared with the record, and all match |

## Claude's leads, checked

Claude (claude-opus-5-5, 2026-11-24 23:03 UTC) got [Chapter 8's instruction](ask_for_discrepancies.py) with the session transcript, `mcp_server.py` and the advertised tool. It got none of the modules the server imports. It returned 13 leads. Claude Code checked each against the source and the spec.

| # | Lead (short) | Checked against | Verdict |
| --- | --- | --- | --- |
| 1 | "Reads only … no network; writes nothing" rests on modules not shown | The imports and source of `corpus`, `screen`, `location`, `normalize`, `ats` and `board`, plus the audit hook | **True of what Claude saw.** Resolved by source inspection and execution |
| 2 | Imported modules could print to stdout | `grep print(` in those modules | **Checked: none** |
| 3 | "FILTER.md v0.1" is not shown in `mcp_server.py` | `tests/test_filter_doc.py` and the value test | **True of what Claude saw.** Resolved by tests |
| 4 | "saved on 2026-11-24" is only a folder name | `captured_at` comes from `trace.json` request times, all 2026-11-24 22:36 UTC | **Resolved** |
| 5 | The transcript rests on `mcp_tap.py` | The host-side stream independently shows the same `tool_use` and `tool_result` | **Resolved** by a second record |
| 6 | The output has undescribed fields, and no `outputSchema` | The returned record | **Confirmed. Not changed** (an open item) |
| 7 | Only `kept` appears in the transcript | The tests cover `review` and `rejected` | **Confirmed** as a transcript limit |
| 8 | The `posting_key` format is not enforced | `_call` | **Confirmed.** By design: an unknown key is a tool error |
| 9 | "Once" holds only if the first load succeeds | `_lookup` | **Confirmed** (minor) |
| 10 | Some id-less lines get an error response | `handle` | **Confirmed.** They are not valid notifications. The docstring could be narrower |
| 11 | The gate also covers `tools/list`; a second `initialize` is accepted | `handle` | **Confirmed.** The first is intended. The second is an open item |
| 12 | Invalid arguments get a protocol error, not a tool error, under 2025-11-25 | [MCP 2025-11-25, server/tools, "Error Handling"](https://modelcontextprotocol.io/specification/2025-11-25/server/tools), read 2026-11-24: "Input validation errors" are "Tool Execution Errors … isError: true" | **Confirmed. Fixed test-first in 0.1.1** (RED `ebb30cd9`, GREEN `459cf329`) |
| 13 | "San Francisco" and "Seattle" aren't matched, and "ca" may be Canada | `location.py` and the student's chosen option | **Confirmed.** It's the chosen rule. Measured in the audit |

A missing lead proves nothing: Claude's list is a list of places to look.

## The trust decision (the student's)

The student's decision, pasted in chat on 2026-11-25 (arrived by 08:41 EST), in their words:

```text
Decision:     allow
For task:     Look up the v0.1 filter result for one saved public posting at a time in a controlled local session.
Server:       jobwatch-js3 0.1.1, commit 459cf329
Re-review if: The server, client, corpus, or tool scope changes, or I need it to handle retries or overlapping requests.
Why, in my words: The score matched a recomputation from the saved posting. The 0.1.1 harness recorded 49 file reads and zero writes, network calls, or process launches on the tested inputs. The server accepts a second initialize and misses repeated request IDs, so I’d use one initialization and a unique ID for each request.
```

Claude Code checked the facts in it against this evaluation, and each one is in the record:
- the recomputation (the "Evidence" ledger row);
- 49 reads and no writes, sockets or processes in the 0.1.1 harness run;
- the second `initialize` and the repeated request ids ("What it declares").

Claude Code supplied the commit, `459cf329`, for the blank in the form.
