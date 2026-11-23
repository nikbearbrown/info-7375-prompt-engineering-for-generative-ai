# TOOL-SERVER.md — the MCP-shaped tool server (Chapter 8)

**Server:** `js3/mcp_server.py`, called `js3-score` (version 0.1.0). It is
written from scratch, stdlib only, and offers one tool, `score_posting`.
**Client:** `tools/mcp_client.py`, a minimal test client. It drives the real
server over a real subprocess stdin/stdout pipe.
**Audit:** `tools/mcp_audit.py` runs the server under a Python audit hook
(PEP 578) and reports every file opened for writing, every directory
change, every DNS lookup and socket connection, and every process spawn.
**Tests:** `tests/test_mcp_server.py`, 17 tests. 15 were written first:
log 23 shows them failing before the server existed, log 24 shows them
passing. The other 2 were added test-first for the schema fix (section
4.1).
**Successful scored call:** `logs/30_mcp_client_session_audited_with_key.txt`.

## 1. Wire format, checked against the spec before building

The MCP specification was read on 2026-11-22.

- **Which version this targets.** The newest version, **2026-07-28**, has
  no `initialize` handshake. Every request carries
  `_meta["io.modelcontextprotocol/protocolVersion"]`, and servers must
  implement `server/discover`. That version calls versions with an
  `initialize` handshake (2025-11-25 and earlier) "legacy". The requested
  sequence, initialize → tools/list → tools/call, is the legacy lifecycle,
  so this server targets **2025-06-18**, the version whose pages were read.
- **Transport (2025-06-18).** stdio, carrying JSON-RPC 2.0 encoded as UTF-8.
  "Messages are delimited by newlines, and **MUST NOT** contain embedded
  newlines." "The server **MUST NOT** write anything to its `stdout` that is
  not a valid MCP message." The server MAY log to stderr.
- **Lifecycle.**
  - The server answers `initialize` with `protocolVersion`, `capabilities`
    and `serverInfo`. If it supports the requested version it echoes it;
    otherwise it answers with the latest version it supports.
  - The client then sends `notifications/initialized`.
  - Notifications have no `id` and get no reply.
  - Request ids "MUST NOT be `null`".
- **Errors.** Unknown tools and invalid arguments are JSON-RPC protocol
  errors (`-32602`). Failures while running a tool are results with
  `isError: true`. In 2026-07-28, input-validation errors move to
  `isError`. A 2026-07-28 client that probes `server/discover` gets `-32601`
  here, which that spec treats as "legacy server, fall back to
  `initialize`".
- **Annotations.** "Clients **MUST** consider tool annotations to be
  untrusted unless they come from trusted servers."
- **Structured results.** "Servers **MUST** provide structured results that
  conform to this schema [outputSchema]". A tool returning
  `structuredContent` "SHOULD also return the serialized JSON in a
  TextContent block". The server does both.

## 2. What the server does

- **The one tool.** `score_posting` takes `{board, id}`, a posting in the
  committed evidence of run `20261121T132140Z`, or `{title, content}`, an ad
  hoc posting.
- **Filter first.** The posting goes through filter v1.1.0 (rules 1-4).
- **Claude only for relevant postings.** Only if the bucket is `relevant`
  does it make one real Claude judgment through `js3/shortlist.py`
  (shortlist-v1, `claude-opus-5-5`), with every claim grounded by
  `js3/grounding.py`. Otherwise Claude is not called and `judgment` is
  `null`.
- **Wire log.** Every inbound line and every outbound line is appended
  verbatim to `logs/mcp/server_<stamp>_<pid>.jsonl` before it is processed
  or sent.
- **Client's own record.** The client keeps a separate record
  (`logs/mcp/client_<stamp>.jsonl`) and checks it against the server's wire
  log after the session. In every completed session below the two were
  identical.
- **Error mapping.**

  | Input | Response |
  |---|---|
  | Unknown tool, or arguments that fail `inputSchema` | `-32602` |
  | Posting not in the evidence, missing API key, judgment unavailable | `isError: true` |
  | Unparseable line | `-32700`, id `null` |
  | Batch array, null id, wrong `jsonrpc` version | `-32600` |
  | Unknown method | `-32601` |
  | Any request before `initialize`, except `ping` | `-32600` (this code is my choice; the spec names none) |

## 3. The real transcript: log 30, the successful scored call

`python3 tools/mcp_client.py --audit`, run with the rotated key. Every
`>>>` and `<<<` line below is verbatim from
`logs/30_mcp_client_session_audited_with_key.txt`. The same lines are in the
server's own wire log, `logs/mcp/server_20261123T004720Z_15469.jsonl`, and
the client's own record, `logs/mcp/client_20261123T004720Z.jsonl`:

```
>>> {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "js3-test-client", "version": "0.1.0"}}}
<<< {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18","capabilities":{"tools":{"listChanged":false}},"serverInfo":{"name":"js3-score","title":"JS3 posting scorer (filter v1.1.0 + shortlist-v1)","version":"0.1.0"},"instructions":"One tool, score_posting. Judged calls are billed and not idempotent."}}
>>> {"jsonrpc": "2.0", "method": "notifications/initialized"}
>>> {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
<<< {"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"score_posting","title":"Score a job posting for Priya Nair","description":"Runs one posting through filter v1.1.0 (FILTER.md rules 1-4). If the filter bucket is 'relevant', makes ONE real Claude judgment (claude-opus-5-5, prompt shortlist-v1) and returns the verdict with every claim grounded against the posting text (supported / contradicted / insufficient). If the bucket is not 'relevant', Claude is not called and judgment is null. Persona is fixed (JS1 resume.json, fictional). Each judged call is billed, non-deterministic, and writes a transcript under logs/mcp/.","inputSchema":{"type":"object","description":"Either {board, id} for a posting in the committed 2026-11-21 evidence, or {title, content} for an ad hoc posting. Not both.","properties":{"board":{"type":"string","enum":["gitlab","stripe","palantir"]},"id":{"type":["string","integer"]},"title":{"type":"string","minLength":1},"content":{"type":"string"}},"additionalProperties":false,"oneOf":[{"required":["board","id"],"properties":{"board":{},"id":{}},"additionalProperties":false},{"required":["title","content"],"properties":{"title":{},"content":{}},"additionalProperties":false}]},"outputSchema":{"type":"object","required":["posting","filter","judgment"],"properties":{"posting":{"type":"object","required":["source","board","id","title","url"],"properties":{"source":{"type":"string","enum":["committed_evidence","adhoc"]},"board":{"type":"string"},"id":{"type":["string","integer"]},"title":{"type":"string"},"url":{"type":["string","null"]}},"additionalProperties":false},"filter":{"type":"object","required":["version","bucket","reasons","eligibility_flags"],"properties":{"version":{"type":"string"},"bucket":{"type":"string","enum":["relevant","rejected","insufficient_data"]},"reasons":{"type":"array","items":{"type":"string"}},"eligibility_flags":{"type":"array","items":{"type":"object","required":["kind","quote"],"properties":{"kind":{"type":"string","enum":["graduation","clearance"]},"quote":{"type":"string"}},"additionalProperties":false}}},"additionalProperties":false},"judgment":{"type":["object","null"],"description":"null when the filter bucket is not 'relevant' (Claude is not called).","required":["model","prompt_version","verdict","claims","message_id","transcript"],"properties":{"model":{"type":"string"},"prompt_version":{"type":"string"},"verdict":{"type":"string","enum":["relevant","not relevant"]},"claims":{"type":"array","items":{"type":"object","required":["claim","quote","label","field","quote_label","contradicted_by","contradicted_by_field"],"properties":{"claim":{"type":"string"},"quote":{"type":["string","null"]},"label":{"type":"string","enum":["supported","contradicted","insufficient"]},"field":{"type":["string","null"],"enum":["title","content",null]},"quote_label":{"type":"string","enum":["supported","insufficient"]},"contradicted_by":{"type":["string","null"]},"contradicted_by_field":{"type":["string","null"],"enum":["title","content",null]}},"additionalProperties":false}},"message_id":{"type":"string"},"transcript":{"type":"string"}},"additionalProperties":false}},"additionalProperties":false},"annotations":{"readOnlyHint":false,"destructiveHint":false,"idempotentHint":false,"openWorldHint":true}}]}}
>>> {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "score_posting", "arguments": {"board": "gitlab", "id": 8704363002}}}
<<< {"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"{\"posting\": {\"source\": \"committed_evidence\", \"board\": \"gitlab\", \"id\": 8704363002, \"title\": \"Backend Engineer (Python),AI Engineering: Agent Foundations\", \"url\": \"https://job-boards.greenhouse.io/gitlab/jobs/8704363002\"}, \"filter\": {\"version\": \"1.1.0-candidate\", \"bucket\": \"relevant\", \"reasons\": [], \"eligibility_flags\": []}, \"judgment\": {\"model\": \"claude-opus-5-5\", \"prompt_version\": \"shortlist-v1\", \"verdict\": \"relevant\", \"claims\": [{\"claim\": \"The role centers on Python backend work with LangGraph, which matches Python and LangGraph in resume.key_skills.\", \"quote\": \"Most of your work will be backend engineering in Python, using libraries such as LangGraph to build secure, reliable and scalable features in our AI Gateway.\", \"label\": \"supported\", \"field\": \"content\", \"quote_label\": \"supported\", \"contradicted_by\": null, \"contradicted_by_field\": null}, {\"claim\": \"The role requires building agentic flows with LangChain and LangGraph, which matches LangChain and LangGraph in resume.key_skills and the AI Engineer target in resume.target_roles.\", \"quote\": \"Build and improve agentic flows and their reusable parts with LangChain and LangGraph, including the Flow Registry.\", \"label\": \"supported\", \"field\": \"content\", \"quote_label\": \"supported\", \"contradicted_by\": null, \"contradicted_by_field\": null}, {\"claim\": \"The posting asks for LLM application framework experience, which aligns with LLM and LangGraph in resume.key_skills.\", \"quote\": \"Experience with LLM application frameworks such as LangGraph, or designing and shipping AI-powered backend features or harnesses.\", \"label\": \"supported\", \"field\": \"content\", \"quote_label\": \"supported\", \"contradicted_by\": null, \"contradicted_by_field\": null}, {\"claim\": \"This is an Intermediate-level role, which may stretch the candidate's 1 year in resume.years_of_experience. The posting does, however, explicitly welcome varying experience levels.\", \"quote\": \"As an Intermediate Backend Engineer (Python) in GitLab's Agent Foundations stage\", \"label\": \"contradicted\", \"field\": \"content\", \"quote_label\": \"supported\", \"contradicted_by\": \"Please note that we welcome interest from candidates with varying levels of experience; many successful candidates do not meet every single requirement.\", \"contradicted_by_field\": \"content\"}, {\"claim\": \"The role requires production Python backend API experience, a backend emphasis that resume.key_skills does not explicitly show beyond Python and SQL.\", \"quote\": \"Experience building and maintaining production Python backend applications, including APIs, asynchronous or background processing, and data models.\", \"label\": \"supported\", \"field\": \"content\", \"quote_label\": \"supported\", \"contradicted_by\": null, \"contradicted_by_field\": null}, {\"claim\": \"The role is remote, which fits resume.location_preference.open_to_remote, though location-based eligibility may apply.\", \"quote\": \"All of our roles are remote, however some roles may carry specific location-based eligibility requirements.\", \"label\": \"supported\", \"field\": \"content\", \"quote_label\": \"supported\", \"contradicted_by\": null, \"contradicted_by_field\": null}, {\"claim\": \"The posting does not say whether visa sponsorship is offered, which leaves uncertainty given resume.visa_sponsorship_needed is true.\", \"quote\": null, \"label\": \"insufficient\", \"field\": null, \"quote_label\": \"insufficient\", \"contradicted_by\": null, \"contradicted_by_field\": null}], \"message_id\": \"msg_011ChJwN8JnUbvx5LtPpCfSR\", \"transcript\": \"/Users/omraut/Desktop/js3-filter-tool-score/logs/mcp/judge_transcripts/gitlab_8704363002_4.json\"}}"},{"type":"text","text":"gitlab 8704363002 - Backend Engineer (Python),AI Engineering: Agent Foundations\n  JUDGMENT (Claude claude-opus-5-5, shortlist-v1): relevant\n  !! CONTRADICTION (FILTER.md abstention rule): 1 claim(s) conflict with the posting's own text. This verdict is shown only together with them:\n     - claim: This is an Intermediate-level role, which may stretch the candidate's 1 year in resume.years_of_experience. The posting does, however, explicitly welcome varying experience levels.\n       cites [supported]: \"As an Intermediate Backend Engineer (Python) in GitLab's Agent Foundations stage\"\n       but the posting says (content): 'Please note that we welcome interest from candidates with varying levels of experience; many successful candidates do not meet every single requirement.'\n  Claims:\n   [supported] The role centers on Python backend work with LangGraph, which matches Python and LangGraph in resume.key_skills.\n       quote: 'Most of your work will be backend engineering in Python, using libraries such as LangGraph to build secure, reliable and scalable features in our AI Gateway.'  (content)\n   [supported] The role requires building agentic flows with LangChain and LangGraph, which matches LangChain and LangGraph in resume.key_skills and the AI Engineer target in resume.target_roles.\n       quote: 'Build and improve agentic flows and their reusable parts with LangChain and LangGraph, including the Flow Registry.'  (content)\n   [supported] The posting asks for LLM application framework experience, which aligns with LLM and LangGraph in resume.key_skills.\n       quote: 'Experience with LLM application frameworks such as LangGraph, or designing and shipping AI-powered backend features or harnesses.'  (content)\n   [contradicted] This is an Intermediate-level role, which may stretch the candidate's 1 year in resume.years_of_experience. The posting does, however, explicitly welcome varying experience levels.\n       quote: \"As an Intermediate Backend Engineer (Python) in GitLab's Agent Foundations stage\"  (content)\n   [supported] The role requires production Python backend API experience, a backend emphasis that resume.key_skills does not explicitly show beyond Python and SQL.\n       quote: 'Experience building and maintaining production Python backend applications, including APIs, asynchronous or background processing, and data models.'  (content)\n   [supported] The role is remote, which fits resume.location_preference.open_to_remote, though location-based eligibility may apply.\n       quote: 'All of our roles are remote, however some roles may carry specific location-based eligibility requirements.'  (content)\n   [insufficient] The posting does not say whether visa sponsorship is offered, which leaves uncertainty given resume.visa_sponsorship_needed is true.\n       quote: None\n"}],"structuredContent":{"posting":{"source":"committed_evidence","board":"gitlab","id":8704363002,"title":"Backend Engineer (Python),AI Engineering: Agent Foundations","url":"https://job-boards.greenhouse.io/gitlab/jobs/8704363002"},"filter":{"version":"1.1.0-candidate","bucket":"relevant","reasons":[],"eligibility_flags":[]},"judgment":{"model":"claude-opus-5-5","prompt_version":"shortlist-v1","verdict":"relevant","claims":[{"claim":"The role centers on Python backend work with LangGraph, which matches Python and LangGraph in resume.key_skills.","quote":"Most of your work will be backend engineering in Python, using libraries such as LangGraph to build secure, reliable and scalable features in our AI Gateway.","label":"supported","field":"content","quote_label":"supported","contradicted_by":null,"contradicted_by_field":null},{"claim":"The role requires building agentic flows with LangChain and LangGraph, which matches LangChain and LangGraph in resume.key_skills and the AI Engineer target in resume.target_roles.","quote":"Build and improve agentic flows and their reusable parts with LangChain and LangGraph, including the Flow Registry.","label":"supported","field":"content","quote_label":"supported","contradicted_by":null,"contradicted_by_field":null},{"claim":"The posting asks for LLM application framework experience, which aligns with LLM and LangGraph in resume.key_skills.","quote":"Experience with LLM application frameworks such as LangGraph, or designing and shipping AI-powered backend features or harnesses.","label":"supported","field":"content","quote_label":"supported","contradicted_by":null,"contradicted_by_field":null},{"claim":"This is an Intermediate-level role, which may stretch the candidate's 1 year in resume.years_of_experience. The posting does, however, explicitly welcome varying experience levels.","quote":"As an Intermediate Backend Engineer (Python) in GitLab's Agent Foundations stage","label":"contradicted","field":"content","quote_label":"supported","contradicted_by":"Please note that we welcome interest from candidates with varying levels of experience; many successful candidates do not meet every single requirement.","contradicted_by_field":"content"},{"claim":"The role requires production Python backend API experience, a backend emphasis that resume.key_skills does not explicitly show beyond Python and SQL.","quote":"Experience building and maintaining production Python backend applications, including APIs, asynchronous or background processing, and data models.","label":"supported","field":"content","quote_label":"supported","contradicted_by":null,"contradicted_by_field":null},{"claim":"The role is remote, which fits resume.location_preference.open_to_remote, though location-based eligibility may apply.","quote":"All of our roles are remote, however some roles may carry specific location-based eligibility requirements.","label":"supported","field":"content","quote_label":"supported","contradicted_by":null,"contradicted_by_field":null},{"claim":"The posting does not say whether visa sponsorship is offered, which leaves uncertainty given resume.visa_sponsorship_needed is true.","quote":null,"label":"insufficient","field":null,"quote_label":"insufficient","contradicted_by":null,"contradicted_by_field":null}],"message_id":"msg_011ChJwN8JnUbvx5LtPpCfSR","transcript":"/Users/omraut/Desktop/js3-filter-tool-score/logs/mcp/judge_transcripts/gitlab_8704363002_4.json"}},"isError":false}}
>>> {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "score_posting", "arguments": {"board": "gitlab", "id": 8396674002}}}
<<< {"jsonrpc":"2.0","id":4,"result":{"content":[{"type":"text","text":"{\"posting\": {\"source\": \"committed_evidence\", \"board\": \"gitlab\", \"id\": 8396674002, \"title\": \"Manager/Senior Manager, Solution Architects - San Francisco\", \"url\": \"https://job-boards.greenhouse.io/gitlab/jobs/8396674002\"}, \"filter\": {\"version\": \"1.1.0-candidate\", \"bucket\": \"rejected\", \"reasons\": [\"rule 1: 0 of 6 role/skill words (need >= 2)\", \"rule 4: seniority word 'Manager' in title\"], \"eligibility_flags\": []}, \"judgment\": null}"},{"type":"text","text":"filter 1.1.0-candidate: rejected - Claude not called.\n  rule 1: 0 of 6 role/skill words (need >= 2)\n  rule 4: seniority word 'Manager' in title"}],"structuredContent":{"posting":{"source":"committed_evidence","board":"gitlab","id":8396674002,"title":"Manager/Senior Manager, Solution Architects - San Francisco","url":"https://job-boards.greenhouse.io/gitlab/jobs/8396674002"},"filter":{"version":"1.1.0-candidate","bucket":"rejected","reasons":["rule 1: 0 of 6 role/skill words (need >= 2)","rule 4: seniority word 'Manager' in title"],"eligibility_flags":[]},"judgment":null},"isError":false}}
>>> {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "delete_everything", "arguments": {}}}
<<< {"jsonrpc":"2.0","id":5,"error":{"code":-32602,"message":"Unknown tool: 'delete_everything'"}}
>>> {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "score_posting", "arguments": {"board": "gitlab", "id": 1, "title": "x", "content": "y"}}}
<<< {"jsonrpc":"2.0","id":6,"error":{"code":-32602,"message":"Invalid arguments for score_posting","data":{"errors":["arguments: must match exactly one of oneOf, matched 0"]}}}
>>> {this is not json
<<< {"jsonrpc":"2.0","id":null,"error":{"code":-32700,"message":"Parse error: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"}}
>>> [{"jsonrpc": "2.0", "id": 7, "method": "ping"}]
<<< {"jsonrpc":"2.0","id":null,"error":{"code":-32600,"message":"Invalid Request: JSON-RPC batches are not supported"}}
```

The session summary, verbatim. The 18 identical `os.mkdir` lines are
omitted; each is `logs/mcp` created with `exist_ok`, once per log append:

```
--- server stderr ---
js3-score MCP server 0.1.0 (protocol 2025-06-18); wire log: /Users/omraut/Desktop/js3-filter-tool-score/logs/mcp/server_20261123T004720Z_15469.jsonl
--- cross-check: client record (17 lines) vs server wire log (17 lines) ---
IDENTICAL
client log: logs/mcp/client_20261123T004720Z.jsonl
server log: logs/mcp/server_20261123T004720Z_15469.jsonl
server exit code: 0
--- audit: 42 events ---
  write INSIDE logs/mcp: /Users/omraut/Desktop/js3-filter-tool-score/logs/mcp/judge_transcripts/gitlab_8704363002_4.json
  write INSIDE logs/mcp: /Users/omraut/Desktop/js3-filter-tool-score/logs/mcp/server_20261123T004720Z_15469.jsonl
  write OUTSIDE logs/mcp: /dev/null
  process: subprocess.Popen None
  process: subprocess.Popen None
  network: socket.getaddrinfo ['api.anthropic.com', '443', '0', '1', '0']
  network: socket.connect ["<socket.socket fd=6, family=30, type=1, proto=6, laddr=('::', 0, 0, 0)>", "('2607:6bc0::10', 443, 0, 0)"]
```

The two process events, as raw `AUDIT` lines (verbatim):

```
AUDIT {"kind": "process", "event": "subprocess.Popen", "executable": "uname", "argv": "['uname', '-p']", "env": "[not recorded]"}
AUDIT {"kind": "process", "event": "subprocess.Popen", "executable": "file", "argv": "['file', '-b', '/opt/homebrew/opt/python@3.11/Frameworks/Python.framework/Versions/3.11/bin/python3.11']", "env": "[not recorded]"}
```

The judged call (`id: 3`) returned `isError: false`, verdict **relevant**, 7
claims: 5 supported, 1 contradicted, 1 insufficient. The judge transcript is
`logs/mcp/judge_transcripts/gitlab_8704363002_4.json`. The contradicted
claim is again the "Intermediate" level claim, set against the
boilerplate "varying levels of experience" sentence. That is the same
pattern SHORTLIST.md section 5 documents.

### Log 29: a real, correctly handled authentication failure

Log 29 is the first session with the fixed audit wrapper (section 4.4). The
Claude call reached `api.anthropic.com` and was rejected with a 401, because
the copied key was corrupted (section 4.4). The server returned this,
verbatim from line 7 of log 29:

```
<<< {"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"Judgment unavailable (JUDGMENT_ERROR): AuthenticationError: Error code: 401 - {'type': 'error', 'error': {'type': 'authentication_error', 'message': 'invalid x-api-key'}, 'request_id': 'req_011ChJvCSUJFcYStESEQGrSp'}. Transcript: /Users/omraut/Desktop/js3-filter-tool-score/logs/mcp/judge_transcripts/gitlab_8704363002_2.json"}],"isError":true}}
```

That is what the server declares: an execution error with `isError: true`,
no `structuredContent`, and **no fabricated verdict**. The failure was
recorded in `logs/mcp/judge_transcripts/gitlab_8704363002_2.json`, with
`response_body: null`. Log 29 also measured the same writes, network
events and process spawns as log 30, so the audit result does not depend on
whether the call succeeds.

### Every session in `logs/mcp/`

Every session is kept; nothing is deleted except the one exposed log in
section 4.3.

| Session (UTC) | Summary log | What it was |
|---|---|---|
| 000255Z | log 25 | no key: judged call correctly `isError` (missing key) |
| 000325Z | log 26a | audited, server crashed at import (section 4.2); 2-line client record |
| 000336Z | log 26 | audited, no key: only the wire log was written; 0 network events, 0 process spawns |
| 002610Z | **none** (deleted, section 4.3) | audited, old key: judge `_1`, relevant. Its wire logs and judge transcript hold no key and are kept |
| 003202Z | log 29 | audited, corrupted new key: 401, `isError` (section 4.4); judge `_2` |
| 003635Z | **none** | a scored session: judge `_3`, relevant, message `msg_011ChJvYbTayVb1ciw3614oU`. **Origin unknown** (see the note below) |
| 004720Z | log 30 | audited, rotated key: the successful scored call; judge `_4`, relevant |

**About the 00:36Z session (003635Z).** Its origin is unknown. It was not
directed by either party in the conversation that built this server, and no
numbered summary log was saved for it. It is included only because its
content can be checked independently: the server's wire log
`logs/mcp/server_20261123T003635Z_8723.jsonl`, the client record
`logs/mcp/client_20261123T003635Z.jsonl`, and the judge transcript
`logs/mcp/judge_transcripts/gitlab_8704363002_3.json`, with message id
`msg_011ChJvYbTayVb1ciw3614oU`, served by `claude-opus-5-5` at
2026-11-23T00:36:36Z. Those files are its evidence for the non-idempotence
finding in section 5. Nothing here speculates about how the session came to
be run.

## 4. Found, then fixed — and found, then left

### 4.1 The `oneOf` input-schema gap (found by self-evaluation, fixed)

- **Found:** while probing my own server for the evaluation in section 5. The
  tool description says "{board, id} ... or {title, content} ... Not both".
- **The gap:** `INPUT_SCHEMA`'s `oneOf` branches listed only *required* keys.
  So `{board, id, title}` and `{board, id, content}` validated, and the extra
  key was silently ignored.
- **Test first:** a test probing exactly those two inputs failed against the
  old schema. Log `27_mcp_schema_gap_test_before_fix.txt` shows 2 failures
  and 2 errors: the server returned a result instead of `-32602`.
- **Fix:** each branch is now closed, with its own `properties` and
  `additionalProperties: false`. Log 28 shows the test passing and the full
  suite passing (91 tests).
- **After:** mixed inputs get `-32602`, as line 13 of log 30 shows ("matched
  0"). That message is accurate but doesn't name the offending key; it was
  left as is.

### 4.2 The audit wrapper's import path (found by a crash, fixed)

- **What broke:** the first audited session crashed before answering
  `initialize`. Running `tools/mcp_audit.py` as a script puts `tools/`, not
  the project root, at `sys.path[0]`, so `js3` could not be imported.
- **Evidence:** log `26a_mcp_client_session_audited_crashed_import_path.txt`,
  kept as is.
- **Fix:** the wrapper sets `sys.path[0]` to the project root. Log 26 is the
  rerun.

### 4.3 The environment-leak bug (found before any commit, fixed; key rotated, log deleted)

- **What leaked:** the full environment of two child processes, including
  `ANTHROPIC_API_KEY` in plain text. The children were `uname -p` and
  `file -b <python3.11 binary>`, started by Python's `platform` module during
  the Claude call. That the Anthropic SDK triggers this while gathering
  platform information is an inference; the call stack was not traced.
- **Why:** the first version of the audit hook recorded every argument of
  the `subprocess.Popen` audit event. Those arguments are
  `(executable, args, cwd, env)`, and `env` is the child's full environment,
  which the server inherits from the shell. The hook wrote that to stderr.
  The client printed the server's stderr. The user's `tee` saved it to the
  first with-key log, `27_mcp_client_session_audited_with_key.txt`.
- **How it was found:** while summarizing that log's audit events for this
  evaluation, before anything was staged. The key was visible in the
  summary. That also means it appeared in the Claude Code session's tool
  output.
- **Resolution: deleted and rotated, not redacted.**
  - The exposed log was **deleted**. It was never staged or committed:
    `git diff --cached`, `git ls-files` and a history search were all empty.
  - The key was **rotated**.
  - Redacting the line in place was considered and rejected. It would have
    left a doctored log describing a run made with a key being withdrawn,
    under a known-buggy wrapper.
- **Fix:** the hook now records only `executable` and `argv` for
  `subprocess.Popen`, with `env: "[not recorded]"`. It was checked offline
  before reuse: a child process given a fake secret in its environment, and
  the secret was absent from the audit output. Logs 29 and 30 were checked
  for key material before this document was written: 0 matches for the
  Anthropic key prefix, 0 for `ANTHROPIC_API_KEY`, and no environment-dump markers.
- **Files from that session that remain:** the wire logs and judge
  transcript of session 002610Z. They hold only MCP messages and the judge
  transcript, contain no key, and are kept.

### 4.4 The key-rotation hiccup (found by the 401, caught before retry)

- **What happened:** the first copy of the rotated key was corrupted by a
  stray bracket character. This is user-reported. The first clean-wrapper
  session (log 29) therefore failed with `401 invalid x-api-key`.
- **How it was caught:** checking the key's prefix in the shell
  (`echo ${ANTHROPIC_API_KEY:0:10}`, which never shows the whole key) before
  retrying.
- **What it showed anyway:** log 29 is a real, correctly handled
  authentication failure (section 3).

### 4.5 Found, then left: the client's audit summary shows `None` for spawns

The wrapper fix in 4.3 renamed the fields of the process event. They are
now `executable`, `argv` and `env` instead of `args`. The client's printed
summary still reads `args`, so logs 29 and 30 show
`process: subprocess.Popen None`. The raw `AUDIT` lines in the same logs
carry the full detail (section 3). This is cosmetic and was left as it was,
so the client code matches the logs it produced.

### 4.6 Log numbering clash: two different logs numbered 27

`logs/27_mcp_schema_gap_test_before_fix.txt` (section 4.1) and the exposed,
since-deleted `logs/27_mcp_client_session_audited_with_key.txt` (section
4.3) were both numbered 27. They were created independently, a few minutes
apart. The schema log keeps its number. Later logs use 29 and 30, and 28 is
the schema fix's after-log, to avoid a third collision.

## 5. Evaluation 1: my own server (`js3-score`)

### What it declares vs what it actually does (measured in logs 26, 29, 30)

**Writes.**
- **Logged:** all writes in the audited sessions are inside `logs/mcp/`.
  - Without a Claude call (log 26), the only write is the wire log.
  - With a call (logs 29, 30), the judge transcript lands in
    `logs/mcp/judge_transcripts/`, as designed.
- **The only write outside `logs/mcp/` is `/dev/null`,** opened by the two
  child processes' output redirection.
- **The transcript write isn't guarded.** It happens inside
  `shortlist.judge` and does not go through the server's `_append` guard. It
  lands inside `logs/mcp/` only because of the directory the server passes
  in.
- **Paths are never client-controlled.** Board and id are only used to
  look a posting up, and ad hoc ids are a hash of the text.
- **The operator can move the log folder.** `JS3_MCP_LOG_DIR` moves it, and
  the write boundary moves with it.
- **Bytecode cache.** First-time imports can write `__pycache__` inside the
  project. That was not observed, because the cache already existed.

**Network.**
- **Without a call:** 0 events (log 26).
- **With a call:** exactly one DNS lookup of `api.anthropic.com:443` and one
  connection to `2607:6bc0::10:443` (logs 29 and 30). Nothing else.
  FILTER.md's toolchain allows that host.
- **Not enforced by my code.** Unlike JS2's permission layer, nothing in my
  code restricts hosts. It relies on the SDK's default, and
  `ANTHROPIC_BASE_URL` in the server's environment would send requests
  elsewhere.

**Process spawns.**
- **Not declared and not expected:** two per judged call, `uname -p` and
  `file -b <python binary>`, measured in logs 29 and 30. They are local and
  read-only, but "the server spawns no processes" is false.
- **They inherit the server's full environment, including the API key.**
  That is normal process behaviour; section 4.3 is what happened when a
  tool recorded it.

**Schema conformance.**
- **Output:** every `structuredContent` is checked against the declared
  `outputSchema` before sending. A mismatch is a `-32603`, never a bad
  result. But the same small checker (`js3/minischema.py`) both declares and
  checks, so a bug in that checker would hide on both sides. The checker
  raises on any keyword it doesn't implement, so a schema can't claim more
  than is checked.
- **Input:** the description and the schema disagreed until fixed (section
  4.1).

**Version label.** The description says "filter v1.1.0", while results
report `"1.1.0-candidate"`. That is the version string decided in
EXPERIMENT.md section 8.

### What a compatible client is not entitled to assume

- **Idempotence.** The annotation says `idempotentHint: false`, and the
  measurements agree. The same call (`gitlab 8704363002`) was judged
  successfully three times through MCP:

  | Judge transcript | Supported | Contradicted | Insufficient |
  |---|---|---|---|
  | `_1` | 5 | 1 | 1 |
  | `_3` (origin unknown; section 3) | 7 | 0 | 1 |
  | `_4` | 5 | 1 | 1 |

  The verdict was "relevant" every time, but whether a CONTRADICTION is
  shown differed between calls. Each call is a new billed judgment with a
  new transcript.
- **No side effects.** Every call is written to disk, judged calls are
  billed to the key holder, and this repo's convention commits `logs/`.
- **One error convention.** It uses 2025-06-18 error shapes. A 2026-07-28
  client expects invalid arguments as `isError`, not `-32602`. Error results
  carry text only, with no `structuredContent`: a missing key, a 401 (log
  29) and an invalid judgment can be told apart only by reading the text.
- **Live data, or any other persona.** Lookups use the frozen 2026-11-21
  snapshot. The persona is fixed. Palantir content is `descriptionPlain`
  only.
- **Concurrency or a prompt `ping`.** One request at a time. A judged call
  blocks the pipe for its duration, and a `ping` waits behind it.
- **That "supported" means true.** It means the quote is in the posting. In
  ad hoc mode the caller writes the posting, so the caller can make any
  claim "supported".

### Trust decision: not for an arbitrary client unsupervised

- **No spending limit.** There is no per-session call budget, so a looping
  client can spend without limit on the key holder's account.
- **Ad hoc mode.** It sends arbitrary text to Anthropic under that key and
  stores it verbatim, with no size cap, in a folder this repo commits.
- **What I would allow:** a supervised local client using `{board, id}`
  mode only.
- **What it would take to allow unsupervised use:**
  - a call budget, like JS2's `MAX_REQUESTS`;
  - a size cap on ad hoc text, or ad hoc mode turned off by default;
  - keeping `logs/mcp/` out of commits.

## 6. Evaluation 2: the reference filesystem server (`@modelcontextprotocol/server-filesystem`)

**Source.** The README and TypeScript source on `main` of
[modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem):
- read: `server.ts`, `lib.ts`, `path-validation.ts`, `roots-utils.ts`,
  `pinned-directory.ts`, `path-utils.ts`, `package.json` (version 2.4.0),
  and the repo's security advisories page (page 1 of 3);
- not read: the read-only and allowed-directories modules, `http.ts`, the
  tests, and advisory pages 2–3.

It was read on 2026-11-22 by a fetch subagent, and nothing was executed.
Claims marked *(reading)* come from reading the code, not from running it.

### Declared vs actual

- **What it declares:** "Secure file operations with configurable access
  controls". The repo's own README says the servers are "intended as
  **reference implementations** … not as production-ready solutions".
- **Tools:** 16. The annotations match the README table wherever they were
  checked. For example, `edit_file` and `move_file` are destructive, and
  `append_file` is not idempotent. `--read-only` removes every tool not
  annotated `readOnlyHint: true`.
- **Validation:**
  - every path is resolved through symlinks to its real location and
    checked against the allowed directories;
  - writes refuse to follow a symlink and create new files with
    exclusive-create flags;
  - on POSIX, each operation is pinned to its directory.
- **Code behaviour the README doesn't mention:**
  - `~` expansion and relative paths are accepted;
  - allowed directories that don't exist at startup are silently dropped,
    despite a code comment saying they're kept for later;
  - error messages reveal the full list of allowed directories;
  - Unicode and space-folding name matching could make a write land on an
    existing, differently spelled file *(reading)*.
- **Documented limits:**
  - overwrites are not crash-atomic;
  - Windows gets no directory pinning;
  - there are no size limits on reads, writes or `read_multiple_files`.
- **Network:** no outbound calls. There is an optional HTTP listener mode.
- **History:** two race-condition (TOCTOU) advisories in November 2026:
  - GHSA-7m4x-rv66-mxhh: `move_file`, fixed in 2.3.0;
  - GHSA-rq2p-q7c4-6g27: directory listings could return names from
    outside the allowed directories, fixed in 2.4.0.

  Three more advisories are referenced but were not read.

### What a client is not entitled to assume

- **A fixed access boundary.** By default, the roots a client sends
  *replace* the directories the operator configured. `--confine-roots` makes
  roots narrow them instead.
- **Trustworthy annotations,** unless the client trusts the server.
- **Atomic writes or bounded reads.**
- **Equal protection on Windows.**
- **Error messages that don't reveal paths.**

### Trust decision

- **Read-only: yes,** under all of these conditions:
  - version 2.4.0 or later, on POSIX;
  - started with `--read-only` and `--confine-roots`;
  - pointed at a dedicated directory holding nothing sensitive.
- **Read-write, for an arbitrary client unsupervised: no.** The reasons:
  - the destructive tools;
  - overwrites that aren't crash-atomic;
  - no size limits;
  - a default that lets the client widen the operator's boundary through
    roots;
  - a recent run of race-condition fixes;
  - the repo's own "not production-ready" statement.
