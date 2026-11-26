# SOURCES — Job-Search Agent 3

## What I started from

- **My Job-Search Agent 2** (`../js2-loop-tools-diff/`): `jsagent/policy.py` and `jsagent/fetch.py`
  copied into `js3/` (policy unchanged; fetch changed only in import path and User-Agent); the
  three boards and two hosts.
- **My Job-Search Agent 1** (`../js1-contract-and-watch/`): the fictional persona
  `personas/priya-nair.resume.json`, which JS1 copied from the Reallocation Engine's example
  persona; the title keywords and seniority terms (`CONTRACT.md`); the labeling rule
  (`labels/LABELING-RULE.md`); the `claude -p` call pattern and the 12,000-character cap
  (`agent/claude_judge.py`).
- **Not used:** Reallocation Engine code, Lectern code, classmates' JS3 folders. Other students'
  JS3 commits are in this branch's history (it was cut from `main`). Claude Code did not open
  their folders.

## Public endpoints (no login, GET only)

- Greenhouse Job Board API: `https://boards-api.greenhouse.io/v1/boards/{anthropic,figma}/jobs?content=true`
- Ashby public posting API: `https://api.ashbyhq.com/posting-api/job-board/openai`

One GET per board per collection; one collection ran (2026-11-26 16:27 UTC). The agent never
applies, emails, messages or logs in. I did not read each company's site terms beyond the APIs
being published for job boards.

## Other software evaluated

- **Claude Code's MCP server** (`claude mcp serve`), Anthropic Claude Code CLI 2.0.20, already
  installed. Evaluated in TOOL-SERVER.md §5. Nothing was downloaded.
- **Model Context Protocol message shapes** (initialize / tools/list / tools/call, protocol
  version 2025-06-18) as Claude Code implements them. The server was written from Claude's
  knowledge of the spec and checked against what Claude Code 2.0.20 actually sent (session B).
  The spec text itself was not opened during this session.

## What Claude Code contributed (desktop app, Claude Opus 5.5, 2026-11-26)

| Part | Claude Code | Me (Saloni) |
|---|---|---|
| Setup | found JS1/JS2 in the course repo; asked three questions | chose: commit each milestone, reuse JS2's 3 boards, label in a script |
| FILTER.md v1.0 | drafted all of it from my JS1 choices (rules, weights, threshold, evidence rules, wrong versions) | _confirm or change in the sign-off_ |
| Code (`js3/`, `scripts/`, `tests/`) | wrote all of it and ran every run in README "What ran" | — |
| Prompts (`prompts/`) | wrote `justify_v1`, `judge_v1`; `judge_v2_criteria` inserts my JS1 labeling rule | — |
| AUDIT / SHORTLIST / TOOL-SERVER / SCORE | drafted from the run files; found the `training` boilerplate, the Architect pattern, the checker's kind mismatch, and Claude's false "twice" claim | _hand verdicts, claim review, C1–C3 decisions, held-out labels_ |
| Hand labels | none; the sheets are empty | _all of them_ |
| FRICTIONAL.md | Part B timeline only | Part A |
| SIGNOFF.md | draft, marked withheld | _edit, then sign or withhold_ |

**Claude responses shown in this folder** are real replies from 2026-11-26, saved raw with UTC
start times: `out/shortlist/shortlist.json` (12), `out/experiments/J*.jsonl` (120),
`out/mcp/claude-client-20261126T163148Z.json` (1). None is edited.
