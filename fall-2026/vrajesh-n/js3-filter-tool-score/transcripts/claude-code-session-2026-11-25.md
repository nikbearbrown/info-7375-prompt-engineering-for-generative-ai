# Claude Code <-> earlybird-score session
Date: 2026-11-25. Raw log kept private (transcripts/private/, git-ignored).
Kept: prompt, tool calls, tool results, replies. Dropped: hook output, plugin paths, session ids, thinking blocks.

## Prompt I gave Claude

> Use the score_posting tool from the earlybird-score server to score two postings: first posting_id 8301253 on board greenhouse_stripe, then posting_id 8760167002 on board greenhouse_databricks. For each, tell me the verdict, the failed check if any, and for every claim its label and one short reason. If a claim is insufficient, say 'I cannot tell'. Do not guess beyond what the tool returned.

Model: `claude-sonnet-5-5`. Claude Code 2.1.332. MCP server `earlybird-score` status: ['connected'].

### Claude calls a tool

`ToolSearch` with

```json
{
 "query": "select:mcp__earlybird-score__score_posting"
}
```

### Tool result

```json

```

### Claude calls a tool

`mcp__earlybird-score__score_posting` with

```json
{
 "posting_id": "8301253",
 "board": "greenhouse_stripe"
}
```

### Claude calls a tool

`mcp__earlybird-score__score_posting` with

```json
{
 "posting_id": "8760167002",
 "board": "greenhouse_databricks"
}
```

### Tool result

```json
{"posting_id": "8301253", "board": "greenhouse_stripe", "title": "Backend / API Engineer, Radar", "location": "San Francisco, Seattle, New York", "url": "https://stripe.com/jobs/search?gh_jid=8301253", "verdict": "relevant", "failed_check": null, "justification": "role title 'Backend / API Engineer, Radar' with no seniority word and no 3+ years asked, US country 'USA', no sponsorship or clearance blocker; fits resume degree 'MS, Computer Software Engineering' and 0 experience entries", "claims": [{"claim": "role", "label": "supported", "quote": "title: \"Backend / API Engineer, Radar\"", "why": ""}, {"claim": "early_career", "label": "supported", "quote": "...ations are a bonus, not a requirement. Minimum requirements 2+ years of industry software engineering experience Strong coding s...", "why": ""}, {"claim": "us_location", "label": "supported", "quote": "location: \"San Francisco, Seattle, New York\"", "why": ""}, {"claim": "sponsorship", "label": "insufficient", "quote": "", "why": "the text says nothing about sponsoring visas"}, {"claim": "no_clearance", "label": "insufficient", "quote": "", "why": "the text does not mention a clearance"}, {"claim": "stack_fit", "label": "insufficient", "quote": "", "why": "no shipped technology appears as a stated need (skills listed on the resume but not shipped do not count)"}], "filter_version": "v2", "persona": "rohan-desai (fictional)", "source": "local snapshot 2026-11-01"}
```

### Tool result

```json
{"posting_id": "8760167002", "board": "greenhouse_databricks", "title": "AI Engineer – Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus)", "location": "Maryland; Virginia; Washington, D.C.", "url": "https://databricks.com/company/careers/open-positions/job?gh_jid=8760167002", "verdict": "not_relevant", "failed_check": "R5", "justification": "description mentions 'secret clearance'; a clearance needs US citizenship and the resume needs sponsorship", "claims": [{"claim": "role", "label": "supported", "quote": "title: \"AI Engineer – Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus)\"", "why": ""}, {"claim": "early_career", "label": "insufficient", "quote": "", "why": "the text states no years of experience"}, {"claim": "us_location", "label": "supported", "quote": "location: \"Maryland; Virginia; Washington, D.C.\"", "why": ""}, {"claim": "sponsorship", "label": "insufficient", "quote": "", "why": "the text says nothing about sponsoring visas"}, {"claim": "no_clearance", "label": "contradicted", "quote": "...ons, U.S. citizenship and eligibility for a U.S. government secret clearance are required to access classified information. The position...", "why": ""}, {"claim": "stack_fit", "label": "insufficient", "quote": "", "why": "no shipped technology appears as a stated need (skills listed on the resume but not shipped do not count)"}, {"claim": "ai_focus", "label": "supported", "quote": "...mmates, and fueling your curiosity for the latest trends in GenAI, LLMOps, and ML more broadly. This role can be remote. The...", "why": ""}], "filter_version": "v2", "persona": "rohan-desai (fictional)", "source": "local snapshot 2026-11-01"}
```

### Claude says

## Posting 8301253 (greenhouse_stripe): Backend / API Engineer, Radar

**Verdict:** relevant. **Failed check:** none.

| Claim | Label | Reason |
|---|---|---|
| role | supported | The title is "Backend / API Engineer, Radar". |
| early_career | supported | The tool quotes "Minimum requirements 2+ years of industry software engineering experience". That quote seems to cut against the label, and the tool gave no explanation. The justification says there is no seniority word and no "3+ years" ask. |
| us_location | supported | The location is "San Francisco, Seattle, New York". |
| sponsorship | I cannot tell | The text says nothing about sponsoring visas. |
| no_clearance | I cannot tell | The text does not mention a clearance. |
| stack_fit | I cannot tell | No shipped technology appears as a stated need. |

## Posting 8760167002 (greenhouse_databricks): AI Engineer - Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus)

**Verdict:** not_relevant. **Failed check:** R5. The description mentions "secret clearance", a clearance needs US citizenship, and the resume needs sponsorship.

| Claim | Label | Reason |
|---|---|---|
| role | supported | The title matches the quoted title. |
| early_career | I cannot tell | The text states no years of experience. |
| us_location | supported | The location is "Maryland; Virginia; Washington, D.C.". |
| sponsorship | I cannot tell | The text says nothing about sponsoring visas. |
| no_clearance | contradicted | The posting says "U.S. citizenship and eligibility for a U.S. government secret clearance are required". |
| stack_fit | I cannot tell | No shipped technology appears as a stated need. |
| ai_focus | supported | The posting quotes "GenAI, LLMOps, and ML". |

The tool left the `why` field empty for every supported or contradicted claim. The reasons above come from its quotes and justification text.

### Final result (is_error=False, turns=4, 11368 ms)

## Posting 8301253 (greenhouse_stripe): Backend / API Engineer, Radar

**Verdict:** relevant. **Failed check:** none.

| Claim | Label | Reason |
|---|---|---|
| role | supported | The title is "Backend / API Engineer, Radar". |
| early_career | supported | The tool quotes "Minimum requirements 2+ years of industry software engineering experience". That quote seems to cut against the label, and the tool gave no explanation. The justification says there is no seniority word and no "3+ years" ask. |
| us_location | supported | The location is "San Francisco, Seattle, New York". |
| sponsorship | I cannot tell | The text says nothing about sponsoring visas. |
| no_clearance | I cannot tell | The text does not mention a clearance. |
| stack_fit | I cannot tell | No shipped technology appears as a stated need. |

## Posting 8760167002 (greenhouse_databricks): AI Engineer - Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus)

**Verdict:** not_relevant. **Failed check:** R5. The description mentions "secret clearance", a clearance needs US citizenship, and the resume needs sponsorship.

| Claim | Label | Reason |
|---|---|---|
| role | supported | The title matches the quoted title. |
| early_career | I cannot tell | The text states no years of experience. |
| us_location | supported | The location is "Maryland; Virginia; Washington, D.C.". |
| sponsorship | I cannot tell | The text says nothing about sponsoring visas. |
| no_clearance | contradicted | The posting says "U.S. citizenship and eligibility for a U.S. government secret clearance are required". |
| stack_fit | I cannot tell | No shipped technology appears as a stated need. |
| ai_focus | supported | The posting quotes "GenAI, LLMOps, and ML". |

The tool left the `why` field empty for every supported or contradicted claim. The reasons above come from its quotes and justification text.
