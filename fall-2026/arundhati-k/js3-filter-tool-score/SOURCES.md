# SOURCES

## Data (public endpoints, GET only, fetched 2026-11-25)

| source | URL | used for |
|---|---|---|
| Stripe job board (Greenhouse) | `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | 772 postings |
| Figma job board (Greenhouse) | `https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true` | 142 postings |
| Notion job board (Ashby) | `https://api.ashbyhq.com/posting-api/job-board/notion` | 174 postings |

Raw responses: `data/raw/2026-11-25/*.json.gz`. No login, no applying, no messages.

## Protocol and tools

- Model Context Protocol, JSON-RPC 2.0 message shapes (initialize, tools/list, tools/call). The server was written
  from scratch in `jsagent3/mcp_server.py`. It answers protocol version `2025-06-18`.
- Claude Code CLI 2.1.316 (Anthropic): the MCP client in transcript 02, the other server evaluated (`claude mcp
  serve`, transcript 03), and the live scorer (`claude -p`, model `claude-opus-5-5`, runs dated 2026-11-25 UTC
  2026-11-26T01:3x).

## My own earlier work reused

- `../js2-loop-tools-diff/`: board list, persona file, allow-list approach.
- `../js1-contract-and-watch/prompts/baseline.txt`: copied unchanged as `prompts/judge_v1.txt` (inherited prompt).

## What Claude (Claude Code, Opus 5.5) contributed

| part | Claude | me |
|---|---|---|
| FILTER.md v1 | formatted my chat answers into tables. Filled the gaps marked [Claude, pending]: threshold 2, spelling variants, whole-word matching, "Sr.", the years cutoff, US detection, W3. The "training" false-friend example appeared in Claude's question to me and in the brief | the role words, topic words, reasons, level rule, evidence rules and both wrong versions (Appendix A, verbatim) |
| tests and code | wrote all tests (from FILTER.md, before the code) and all code | (none) |
| audit | drew the seeded samples and wrote the blind sheets; computed agreement and intervals; found the false friends by printing each matched line | all 54 verdicts and the #26 revision |
| rule changes | proposed and measured A–D | decided A rejected, B added, C rejected, D added, with my reasons |
| held-out | drew the set | all 20 labels |
| shortlist | auto labels (code) and the "read" labels, which are Claude's reading | checked the 6 ✎ rows and agreed with each, with my reasons (audit/my-shortlist-checks-2026-11-25.txt) |
| tool server | wrote the server and client, ran the transcripts, drafted TOOL-EVALUATIONS facts | both trust decisions (TOOL-EVALUATIONS.md) |
| score changes | wrote judge_v2 from my rules, ran P1/P2/C2 live, wrote SCORE-CHANGES.md | (none) |
| parser bugs | found and fixed both (curly apostrophe; "four (4) years"), tests first | (none) |

**Lookup I did myself:** [Arundhati: open one posting in your own browser, for example stripe:8128744 or
stripe:6042172, and write what you saw and whether it matches the saved text.]

**Help on my FILTER.md answers:** [Arundhati: say whether your five answers were written by you alone or with
ChatGPT/Claude help.]
