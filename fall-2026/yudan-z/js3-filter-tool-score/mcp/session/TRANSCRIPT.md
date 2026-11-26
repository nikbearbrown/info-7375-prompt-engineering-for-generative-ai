# Real session: Claude Code ↔ js3-postings (2026-11-25, 20:28 EST)

Command (run from the repo root, see README):

```
claude -p "<prompt below>" --mcp-config mcp/claude-mcp-config.json --strict-mcp-config \
  --allowedTools "mcp__js3-postings__search_postings,mcp__js3-postings__score_posting" --output-format stream-json --verbose
```

Prompt: *Use only the js3-postings tools. Search the saved postings for 'new grad' titles. Then score up to three of them with filter version v2. For each, report the decision and every claim with its label (supported / contradicted / insufficient) and the quoted evidence. Do not add anything the tool did not return; if the tool says 'cannot tell', say that.*

## 1. The wire, both directions (from the server's own log, `mcp/logs/transcript-2026-11-26.jsonl`, UTC)

| time (UTC) | direction | message |
|---|---|---|
| 01:28:30 | client->server | `server/discover (client protocolVersion 2026-07-28)` |
| 01:28:30 | server->client | `error {"code": -32601, "message": "method not found: server/discover"}` |
| 01:28:30 | client->server | `initialize (client protocolVersion 2025-11-25)` |
| 01:28:30 | server->client | `result: protocolVersion 2025-06-18, serverInfo {'name': 'js3-postings', 'version': '1.0.0'}` |
| 01:28:30 | client->server | `notifications/initialized` |
| 01:28:30 | client->server | `tools/list` |
| 01:28:30 | server->client | `result: tools ['search_postings', 'score_posting']` |
| 01:28:38 | client->server | `tools/call "search_postings" {"query": "new grad"}` |
| 01:28:38 | server->client | `result: 49 matches, 10 returned` |
| 01:28:43 | client->server | `tools/call "score_posting" {"key": "greenhouse/databricks/7586263002", "version": "v2"}` |
| 01:28:43 | server->client | `result: Associate Product Manager, New Grad (2027 Start) → cannot tell (score 0)` |
| 01:28:43 | client->server | `tools/call "score_posting" {"key": "greenhouse/databricks/8843577002", "version": "v2"}` |
| 01:28:43 | server->client | `result: Product Design New Grad (2027 Start) → cannot tell (score 3)` |
| 01:28:44 | client->server | `tools/call "score_posting" {"key": "greenhouse/databricks/8133727002", "version": "v2"}` |
| 01:28:44 | server->client | `result: Product Manager, New Grad (2027) - Amsterdam → reject (score -5)` |

## 2. What Claude answered (verbatim, from `claude-session.jsonl`)

The search found 49 postings with "new grad" in the title and returned 10. I scored the first three with filter v2. Two came back **cannot tell** and one came back **reject**.

### 1. Associate Product Manager, New Grad (2027 Start), Databricks
`greenhouse/databricks/7586263002`, Bellevue, WA; Mountain View, CA; San Francisco, CA

**Decision: cannot tell** (score 0). Why it couldn't decide: "sponsorship: I cannot tell"

| Claim | Label | Evidence |
|---|---|---|
| the title names a target role | insufficient | title 'Associate Product Manager, New Grad (2027 Start)' contains no target role word |
| the job is in the US | supported | location 'Bellevue, Washington; Mountain View, California; San Francisco, California' |
| the posting asks for skills the persona has | supported | topic words found: ['Excel', 'Python', 'SQL'] |
| the title is not senior | contradicted | title 'Associate Product Manager, New Grad (2027 Start)' senior words: ['Manager'] |
| the stated experience fits a new graduate | insufficient | no stated minimum found |
| the posting does not rule out sponsorship | insufficient | the posting never mentions sponsorship, visas or work authorization |

### 2. Product Design New Grad (2027 Start), Databricks
`greenhouse/databricks/8843577002`, San Francisco, CA; Seattle, WA

**Decision: cannot tell** (score 3). Why it couldn't decide: "sponsorship: I cannot tell"

| Claim | Label | Evidence |
|---|---|---|
| the title names a target role | insufficient | title 'Product Design New Grad (2027 Start)' contains no target role word |
| the job is in the US | supported | location 'San Francisco, California; Seattle, Washington' |
| the posting asks for skills the persona has | supported | topic words found: ['Excel', 'Python', 'SQL'] |
| the title is not senior | supported | title 'Product Design New Grad (2027 Start)' senior words: none |
| the stated experience fits a new graduate | insufficient | no stated minimum found |
| the posting does not rule out sponsorship | insufficient | the posting never mentions sponsorship, visas or work authorization |

### 3. Product Manager, New Grad (2027) – Amsterdam, Databricks
`greenhouse/databricks/8133727002`, Amsterdam, Netherlands

**Decision: reject** (score −5). The tool gave no reasons for being unable to decide.

| Claim | Label | Evidence |
|---|---|---|
| the title names a target role | insufficient | title 'Product Manager, New Grad (2027) - Amsterdam' contains no target role word |
| the job is in the US | contradicted | location 'Amsterdam, Netherlands' |
| the posting asks for skills the persona has | supported | topic words found: ['Excel', 'Python', 'SQL'] |
| the title is not senior | contradicted | title 'Product Manager, New Grad (2027) - Amsterdam' senior words: ['Manager'] |
| the stated experience fits a new graduate | insufficient | no stated minimum found |
| the posting does not rule out sponsorship | insufficient | the posting never mentions sponsorship, visas or work authorization |

Session result: `success`, 6 turns, reported cost $0.3908004. Model: claude-opus-5-5 (from the removed init line).
