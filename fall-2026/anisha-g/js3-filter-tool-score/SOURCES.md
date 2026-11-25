# SOURCES.md
**Anisha Gaikar · JS3 · 2026-11-25**

## What Claude contributed
| Part | Claude's contribution | Mine |
|---|---|---|
| FILTER.md v1.0 | In a claude.ai chat (2026-11-25, ~1:58–2:02 pm), Claude offered options and wrote the wording, the one-line reasons and the score numbers (§1.4, to reproduce my rule) | I made all 8 choices: title words, seniority, the text rule, the boards, the evidence rule, abstention, missing fields, the wrong versions |
| FILTER.md §5 (v1.1, v1.2) | Claude (Claude Code) measured each candidate rule on the corpus and proposed it | I decided: accept both v1.1 rules, add R5 US-only, reject FP&A and "specialist" |
| All code and tests | Claude Code (Opus 5.5) wrote `js3/`, `toolserver/`, `tools/`, `tests/` and `wrong_versions/`; the tests were written from FILTER.md before the code | I ran them on my Mac |
| H2 hand verdicts (24) | none | **decided and typed entirely by me** |
| Hand verdicts (76 + 5 re-judged) | Claude Code did not see the sheet and gave no verdicts. I used **another Claude chat to help word the reasons** for most postings | **every y/n decision is mine** |
| The blind judging tool, the draw and the seed | Claude wrote them | — |
| Claude judge experiments | real `claude -p` calls (sonnet / haiku): 180 on H at 14:18–14:21 ($2.51) and 120 on H2 at ~16:10 ($1.85), all 2026-11-25; the plan was written by Claude and committed before the calls | — |
| Tool server transcripts | real Claude Code 2.1.332 sessions (Opus 5.5), 2026-11-25 14:14–14:55 | I chose to keep them unedited, apart from path redaction |
| Write-ups (README, AUDIT, SHORTLIST, TOOLSERVER, WHAT_MOVES_THE_SCORE) | Claude drafted the text from the logs and results | I read them; my own words are in the sign-off, the driver's seat and FRICTIONAL.md |
| Label check (49 shortlist claims) | Claude re-read every label against the posting text and found the heading bug and 4 wrong labels | the labels I checked myself (SHORTLIST.md) |
| Survey of classmates' JS3 folders | A Claude sub-agent read lavanya-r, pavan-m, rayudu-h and riya-k for **structure only**: blind sheet, Wilson intervals, `claude -p --strict-mcp-config`, evaluating server-filesystem. **No code or text was copied** | — |

## Code and data I reused
- **My JS2** (`../js2-loop-tools-diff/watcher/policy.py`, `fetch.py`): the allow-list policy and fetch pattern, adapted in `js3/policy.py` and `js3/fetch.py`.
- **My JS1** (`../js1-contract-and-watch/`): `persona/resume.json` (fictional persona) and `prompts/baseline.txt` and `revised.txt`, unchanged.
- **Job postings:** public Greenhouse Job Board API (`boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true`) for klaviyo, datadog, stripe and lyft; public Lever Postings API (`api.lever.co/v0/postings/palantir?mode=json`). Read-only GET, no login.

## External tools and documents
- **Model Context Protocol** message shape (JSON-RPC 2.0; `initialize`, `tools/list`, `tools/call`; tool annotations): modelcontextprotocol.io specification, 2025-11-25 revision. My server is written from scratch without the SDK.
- **`@modelcontextprotocol/server-filesystem` 2.2.0**, from github.com/modelcontextprotocol/servers (npm, integrity `sha512-mNLj/qhV…T9A==`, published 2026-11-04). This is the other server I evaluated; it is not part of my agent.
- **Claude Code 2.1.332** (`claude` CLI): MCP client and `claude -p`.
- **Wilson score interval** (E. B. Wilson, 1927): the standard formula, implemented in `js3/report.py`.

## Claude responses shown in this folder
Every Claude response quoted here is one I actually got on **2026-11-25**, saved raw:
- `transcripts/claude-*-stream.jsonl` (tool server sessions);
- `runs/<exp>/*.json` (judge experiments, each with its own timestamp).
