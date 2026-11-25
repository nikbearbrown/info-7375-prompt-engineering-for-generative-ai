# SOURCES — Job-Search Agent 3 (nishant-u)

## Sources used
- My JS2 (branch nishant-u-js2, f956e22), which contains my JS1; the 182 postings come from its saved Greenhouse and Ashby responses (2026-11-10).
- Course chapters 7–9 and the JS3 brief in this repository.
- The course reference MCP server: lessons/08-mcp-from-scratch/code/main.py.
- The fictional persona Priya Nair (data/resume.example.json), from the Reallocation Engine.

## What I did
- Approved FILTER.md v1 before any code, and the audit rule before sampling.
- Judged the 45 reject-audit postings (audit/audit.csv).
- Decided which rule changes to accept or reject (FILTER.md v2), and approved both MCP trust decisions.
- Reviewed the reports and signed the sign-off.

## What Claude contributed
- Claude (claude.ai): drafted FILTER.md, the audit rule, the prompts I gave Claude Code, suggested decisions on the rule changes, and drafts of the trust decisions and sign-off, which I edited and approved.
- Claude Code: wrote agent3/, audit/make_kit.py, mcp_server/ and all JS3 tests; ran the filter, the comparisons, the MCP transcripts and the Claude Code MCP run; drafted AUDIT-REPORT.md, SHORTLIST.md, SCORE.md, MCP-EVALUATION.md (ledgers), README.md and FRICTIONAL.md; found the C2 "MySQL" quote bug, the held-out exposure and the overstated server descriptions.
- Claude Code also drafted audit verdicts at one point; that draft was discarded.
