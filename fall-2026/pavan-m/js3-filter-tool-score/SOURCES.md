# SOURCES — Job-Search Agent 3

## What I used
- Public job-board APIs: Greenhouse (Glean), Lever (Palantir), Ashby (OpenAI), through my JS2 loop
- Microsoft Learn MCP Server (https://learn.microsoft.com/api/mcp), evaluated with curl on Nov 25, 2026
- Model Context Protocol message shapes (initialize, tools/list, tools/call; protocol 2025-06-18)
- Python 3.14.3, httpx 0.28.1, pytest 9.2.0
- Claude Code (desktop app, claude-code 2.1.330) and Claude (claude.ai chat)
- Starting point: my own JS2 (`../js2-loop-tools-diff` at `70f8e203`). I did not use the Reallocation Engine, Lectern, or other students' work.

## What I wrote or did myself
- FILTER.md v1.0: every rule, weight, threshold and wrong version (`5639e4c8`), and the decisions in §9 and §10
- Every assert in tests/test_filter.py, tests/test_filter_config.py and tests/test_mcp_server.py, before the code each tests
- audit/AUDIT_RULE.md, and all 48 audit verdicts and 32 held-out verdicts, judged blind
- The choice of which rule changes to test (C1, C3), and accepting C1 and rejecting C3 on the evidence
- All 50 shortlist claim labels with evidence quotes
- Every live run, filter run, measurement, client run and curl call, and reading their output
- The trust decisions in TOOL_SERVER.md, the "Not checked" list and the sign-off

## What Claude Code contributed
- `agent/filter.py` and `agent/run_filter.py` (`c7574898`), including choices FILTER.md didn't decide (recorded in FILTER.md §9)
- Found the Lever retrieval gap (the adapter drops Lever's `lists` field)
- The configurable filter and `agent/measure_filter.py` (`ed5b94b2`)
- `agent/mcp_server.py`, `agent/mcp_client.py` and `.mcp.json` (`32353bfa`)
- In the Claude Code session using my server: noticed that padded filler words pass the 50-word rule

## What Claude (chat) contributed (claude.ai, Nov 19–25, 2026)
- A step-by-step plan and a plain-language breakdown of the assignment
- Review of my FILTER.md drafts (mismatches with Alex's résumé, rules that weren't hand-checkable, an abstention counterexample that didn't expose a limit)
- Test skeletons with TODOs (I wrote the asserts) and the sampling, comparison and labeling-sheet scripts
- The Claude Code prompts I used
- Drafts of SHORTLIST.md, TOOL_SERVER.md, WHAT_MOVES_THE_SCORE.md, FILTER.md §9–§10, this README and wording for many FRICTIONAL entries, all from my results; I checked the numbers against the committed files
- Mistakes it made that I caught or fixed: a placeholder that overwrote the audit comparison file, a wrong verdict count (15/33 instead of 14/34), a wrong Palantir-miss count, a wrong README reference, and FRICTIONAL entry dates that didn't match the commits
