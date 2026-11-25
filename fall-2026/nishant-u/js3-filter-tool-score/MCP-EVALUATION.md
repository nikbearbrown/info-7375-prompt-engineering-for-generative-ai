# MCP evaluation — two tool servers, four ledgers

Ledgers drafted by Claude Code on 2026-11-25 from the source code and the real transcripts listed below. The two **Trust decision** sections are Nishant's own words (2026-11-25).

Chapter 8 keeps four ledgers for one connection decision and does not let one stand in for another:

| Ledger | Question |
| --- | --- |
| Protocol | Is the exchange well formed and in order? |
| Capability | Does the code do what the listing says? |
| Permission | Does this task allow that capability? |
| Evidence | Does the returned content support the claim built on it? |

**Evidence types:**
- **advertised:** the server says so (`initialize`, `tools/list`, descriptions);
- **source-inspected:** read in the code;
- **executed on a fixture:** seen in a real call recorded in a transcript;
- **independently sourced:** checked against something the server did not produce;
- **uninspected:** not looked at. Uninspected is not "none".

**Transcripts** (all in `mcp_server/transcripts/`; line numbers below refer to these files):

| ID | File | What |
| --- | --- | --- |
| T1 | `2026-11-25-js3-scripted-client.jsonl` | JS3 server's own log of the scripted client run |
| T2 | `2026-11-25-claude-code.jsonl` | JS3 server's own log of the real Claude Code run (session `ef4e86c3-5a29-4cca-bf3f-bba0d82b71ec`, see `mcp_server/CLAUDE-CODE-RUN.md`) |
| T3 | `2026-11-25-client-side-reference.jsonl` | the scripted client's log of the reference server run. The reference server keeps no log of its own |

---

## Server A: `mcp_server/server.py` (this folder, written for JS3)

**Provenance:** written from scratch in this session by Claude Code at Nishant's direction (commit `b16b973`), Python standard library only. It reads `out3/filter-run-v2/results.json` and `shortlist.json` (FILTER.md v2 run, commits `fb071b5`, `409b995`, `7339062`).

### Declared vs actual

| What it declares | Where | What it actually did | Evidence type |
| --- | --- | --- | --- |
| One tool, `score_posting(posting_id)`, schema: one required string, no other properties | `tools/list` (T1 line 7, T2 line 7) | Calls with exactly `posting_id` returned results (T1 line 9, T2 line 9); `{"wrong": 1}` → `-32602` (T1 line 15) | advertised + executed on a fixture |
| `readOnlyHint: true`, `destructiveHint: false`, `openWorldHint: false` | `tools/list` annotations | The tool loads two JSON files once at start and answers from memory; `posting_id` is a dict key, never a path. `"../../x"` → `isError`, "Refused … Nothing was read" (T1 line 13); a unit test fails if any file is opened during a call (`test_js3_mcp`) | source-inspected + executed on a fixture |
| "Read-only except that the server appends every message to its own transcript log inside its folder." (`initialize` instructions, current) | source; T1 line 4 and T2 line 4 show the earlier wording, "Read-only." | Matches: the server process appends every message to `mcp_server/transcripts/<date>-<client>.jsonl`, and the tool changes nothing. The earlier "Read-only." overstated it. It was changed on 2026-11-25, after T1 and T2 were recorded (commit "JS3: server descriptions match the trust decision") | source-inspected + executed (the log files exist) |
| "Return the SAVED FILTER.md v2 verdict … for one posting collected on 2026-11-10 … not a fresh judgment of fit … cannot fetch new or updated postings" (tool description, current) | source; T1 line 7 and T2 line 7 show the earlier wording, "Reads only the saved v2 run … it cannot fetch new postings" | Matches: it answers from `out3/filter-run-v2/` loaded at start. It imports only `datetime, json, os, re, sys, pathlib`, with no network or subprocess module (AST test). Same change and date as the row above | source-inspected |
| Protocol versions | `initialize` | Echoes a requested version if it is one of `2025-11-25, 2025-06-18, 2025-03-26, 2024-11-05`, else answers `2025-11-25`. Only `2025-11-25` was exercised by a real client (T2 line 3–4). It does not change behavior per version, so the support it claims for older versions is **untested** | executed (2025-11-25) / uninspected (others) |
| Lifecycle: tools refused until `initialize` + `notifications/initialized` | docstring | `tools/list` before initialize → `-32000` (T1 lines 1–2). Claude Code's pre-initialize `server/discover` probe (protocol `2026-07-28`) also got `-32000`, and Claude Code continued to the standard handshake (T2 lines 1–4) | executed on a fixture |
| A missing posting is a tool-level failure, not a protocol error | docstring | `greenhouse:faire:999` → `result.isError: true` (T1 line 11) | executed on a fixture |
| Error codes `-32700/-32600/-32601/-32602` | docstring | `-32700` (T1 line 19), `-32601` (T1 line 17), `-32602` (T1 line 15); `-32600` in unit tests only | executed / unit-tested |

### Four ledgers

**Protocol.**
- **Well formed and in order** with both clients: every response carries its request's id, and the notification got no response (T1 lines 5–6, T2 lines 5–6).
- **Gap:** unknown methods sent before `initialize` get `-32000`, not `-32601` (T2 line 2). That's a choice, not a spec requirement. Claude Code tolerated it, but another client might not.
- **Untested:** the older protocol versions it claims to support; batching (not supported, answered `-32600`); concurrent clients.

**Capability.**
- **Source-inspected and executed:** one in-memory read of two files at start; no network; no subprocess; the only write is its own transcript.
- **What `score_posting` really returns:** a *saved* verdict, not a fresh score. The verdicts come from FILTER.md v2 run on postings collected 2026-11-10. A posting changed or removed since then is still reported as it was.
- **Uninspected:**
  - behavior when two clients run at once (both would append to the same transcript file);
  - behavior if `out3/filter-run-v2/` is missing or edited (the server would fail at start);
  - the Python interpreter and standard library themselves.

**Permission.**
- **What the task allows (from the JS3 brief):** reading this folder's saved, public-board postings and the fictional persona's derived labels. The tool may return text only.
- **What the brief forbids:** the agent never applies, emails, messages or logs in. A tool server must not expose anything that can send or change data outside this folder.
- **Where it stands:** Server A sends nothing and changes nothing outside the folder. Its one write is inside it, and the task allows that.
- **Where results go:** into the client's context. In T2, into Claude's context and then Claude's reply.
- **Who decides whether that is acceptable:** Nishant (see Trust decision).

**Evidence.**
- **The returned claims match the run's computed labels.**
  - In T2, Claude's reply matched the tool output on all 8 claims and all 7 quotes, checked by script (CLAUDE-CODE-RUN.md).
  - The tool output matches `shortlist.json`, and every quote is a substring of the posting text.
  - Evidence type: executed on a fixture, independently sourced against the saved posting text.
- **They are computed, not hand-verified.** A supported label can still overstate the text. SHORTLIST.md shows "Uses Python" resting on "Python, Java, or equivalent", and on a nice-to-have list.
- **The C4 quote in T2 is truncated mid-word** ("…Wednesday, or Fr") by the 150-character window. Claude noticed and said so.

### What a compatible client is not entitled to

- **Discovery is not consent.** Seeing `score_posting` in `tools/list` does not authorize calling it for any purpose other than the JS3 task.
- **Compatibility is not authorization.** A clean handshake shows the client can talk to the server, not that this server, its data or its outputs are appropriate for a given use.
- **`readOnlyHint` is advertised, not guaranteed.** A client may not rely on it without source inspection, as was done here. It also does not cover the server's transcript write.
- **A matching id and `isError: false` show association and success, not truth.** The labels are computed by `agent3/shortlist.py` and not checked by a person.
- **"accept" is not "apply".** A client is not entitled to treat a verdict as a recommendation to act. The judgment that a posting is worth Priya's time stays with Nishant.
- **A client is not entitled to fresher data than the saved run.** Nor to sponsorship information: C3 is "insufficient" for every accepted posting.

### Trust decision

Trust: yes, narrowly. I'll let Claude Code call it, but only through my own config with only score_posting allowed. Its tool changed nothing in any call (tested; transcripts), it refuses path-like IDs without reading anything, and it imports nothing that can use the network. But I don't trust its description as written: "Read-only" is only true apart from its own transcript log, and "score" is really a saved verdict from postings collected on 2026-11-10, not a fresh judgment of fit. I'll fix both descriptions before anyone else uses it. A compatible client is still not entitled to treat a verdict as advice to apply.

---

## Server B: `lessons/08-mcp-from-scratch/code/main.py` (course reference server)

**Provenance:** the course repository's Chapter 8 teaching server (last changed in commit `a8629ce1`, 2026-09-06), maintained by the instructor. It is a third-party server from a source I can name. Run unmodified with `--stdio` by the scripted client. I read the full source (70 lines; imports `argparse`, `json`, `sys`).

My first run attempt sent nothing: a path bug in my client pointed at a non-existent file, so the process exited and no transcript was written. The client was fixed and the run repeated; T3 is that second run.

### Declared vs actual

| What it declares | Where | What it actually did | Evidence type |
| --- | --- | --- | --- |
| One tool, `lookup(key)`: "Read a public course fixture"; schema: one required string | `tools/list` (T3 line 8) | Source: a one-entry in-memory dict `{"office": "505A Dana Hall"}`. `office` → "505A Dana Hall" (T3 line 10) | advertised + source-inspected + executed |
| "public" | tool description | **The server cannot know this.** Nothing in the code classifies data; "public" belongs in the permission ledger, filled by the data owner (Chapter 8) | source-inspected |
| A missing key is a tool-level failure | source | `missing` → "Record not found", `isError: true` (T3 line 12) | executed on a fixture |
| Path-like key | (not declared) | `"../../x"` → "Record not found", `isError: true` (T3 line 14). Source: a dict lookup, so no file is touched | source-inspected + executed |
| Bad arguments | source | `{"wrong": 1}` → `-32602` "Expected a string key" (T3 line 16) | executed |
| Unknown method / parse error | source | `-32601` (T3 line 18), `-32700` with null id (T3 line 20) | executed |
| Lifecycle | source | `tools/list` before initialize → `-32000` "Initialize and notify before using tools" (T3 line 3) | executed |
| `protocolVersion: "2025-11-25"`, `capabilities: {"tools": {}}` | `initialize` (T3 line 5) | Source: always answers `2025-11-25` and does not read `params`. Not exercised here, because the client also asked for `2025-11-25` | advertised + source-inspected |

### Four ledgers

**Protocol.**
- **Well formed and in order** for this sequence (T3), and matches Chapter 8's transition table.
- **Gaps known from source and the chapter:**
  - it does not evaluate the requested protocol version or validate `initialize` params;
  - a second `initialize` leaves `ready` true;
  - a `tools/call` without an id is dropped silently.
- **Untested here:** those three behaviors; parse errors spanning lines.

**Capability.**
- **Source-inspected:** one in-memory mapping; no file access, no network, no writes, no logging.
- **Executed:** the returned value and `isError` match the source.
- **Lack of logging:** the server keeps no record of what it was asked. The only record is the client's (T3).

**Permission.**
- **Effects:** for a classroom question ("where is the office for key `office`"), the only effect is returning one fixed string, which any task would allow.
- **Whether the fixture is public:** only the course owner can say, and the server's own description is not evidence of it.
- **Use in JS3:** this server has no role in the job-search task. It was evaluated as a named third-party server, not connected to the agent.

**Evidence.**
- **"505A Dana Hall" matches the mapping in the source (source-inspected).** That shows what the server returned, not that 505A Dana Hall is the current office. That would need an independent source, which I did not check (uninspected).

### What a compatible client is not entitled to

- **Not entitled to treat "public" as established.** It is the server's own wording.
- **Not entitled to treat "505A Dana Hall" as a current fact about the world.** It is the fixture's value under this server version.
- **Not entitled to read a successful handshake as version negotiation.** The server returns `2025-11-25` regardless of what was asked.
- **Discovery is not consent, and compatibility is not authorization.** These hold here exactly as for Server A.

### Trust decision

Trust: only as a teaching fixture. Reading the source shows it returns fixed in-memory records, with no network and no writes, and it behaved as its code says. But it calls its data "public", which the code can't know; it always answers protocol version 2025-11-25 whatever the client asks for; and it keeps no log, so there's no evidence trail. I'd run it locally to learn the protocol, but I wouldn't connect it to a real assistant for any decision.

---

## Not checked (both servers)

- **A second client implementation:** Server A was driven by the scripted client and Claude Code; Server B only by the scripted client.
- **Older protocol versions** that Server A claims to support.
- **Concurrent sessions,** and Server A's transcript file under concurrent writes.
- **Hostile inputs beyond those listed:** very long lines, non-UTF-8 bytes, deeply nested JSON.
- **Whether either server's content is correct beyond its own data source** (Server A's labels are computed; Server B's office value is unverified).
