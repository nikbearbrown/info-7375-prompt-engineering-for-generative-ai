# SOURCES.md

## What I started from

- **My own Job-Search Agent 2:** `../js2-loop-tools-diff/`, submitted at commit `9061037`. It was copied unchanged as this folder's first commit (`cf6b64d`): the loop, the permission policy, the providers, the Claude judge, the tests and the two live runs.
- **The Reallocation Engine** (`github.com/nikbearbrown/the-reallocation-engine`):
  - **The greenhouse-watch scorer.** `.claude/skills/greenhouse-watch/scheme.default.json` (`default-0.1`) and its `judge()` in `scripts/greenhouse_watch.py`. The weights, the threshold, the skill cap, and the rule that a posting with no skill is never relevant are **inherited** from it. The scoring was re-written in Python in `js3/score.py`; no code was copied. FILTER.md names every inherited number.
  - **The fictional persona Priya Nair:** `search/examples/priya-nair/resume.example.json` (as in JS1) and `profile.yml`, copied to `persona/`. Both are marked as fictional and safe to commit.
- **The instructor's Lectern** (`fall-2026/nik-bear-brown/lectern/` in the course repo). I borrowed formats, not code:
  - **The filter log.** `keywords.json` records every word added, cut or rejected, with hits and examples. FILTER.md section 6 follows that format.
  - **The audit design.** `audit_rejects.py` uses MISS / ok / ? verdicts and states that only a uniform random sample of rejects supports a rate.
  - **The "false friend" idea.** `title_families.json` names one: "training" meaning model training.

  Lectern has no tool server, so the MCP server is written from scratch.

## Data

- **Public job boards,** read-only and without logging in:
  - Greenhouse Job Board API: `boards-api.greenhouse.io/v1/boards/anthropic/jobs`;
  - Ashby Posting API: `api.ashbyhq.com/posting-api/job-board/{notion, perplexity}`.

  There were three live snapshots: Oct 31 and Nov 7, 2026 (from JS2), and Nov 20, 2026 (this assignment). Their files are frozen in `CORPUS.sha256`. The posting text belongs to each company and is kept only as raw evidence.
- **Hand verdicts:** Hemanth's 95 blind labels (`audit/labels.csv`) and 69 claim checks (`shortlist/hand-check.csv`), all given in chat on Nov 22, 2026.

## Tool-server sources

- **The Model Context Protocol.** JSON-RPC 2.0 over stdio, with `initialize`, `tools/list` and `tools/call`, the standard error codes, and tool annotations. The server was written from Claude's knowledge of the published MCP specification (modelcontextprotocol.io); **the specification was not re-read during this assignment**. The protocol versions actually used come from the real transcripts:
  - Claude Code asked for `2025-11-25` after first probing `server/discover` with `2026-07-28`.
- **The other server evaluated:** `@modelcontextprotocol/server-filesystem` **2.2.0** from npm (`github.com/modelcontextprotocol/servers`, `src/filesystem`). Its integrity is `sha512-mNLj/qhV+P4kj1qP8VzgQ2fjSmWcKDQ3Q+KpZEA+WahCDWHw5zJBRQUNSPZ6Ai2/ZGGUjzNzsFpz958a1+4T9A==`.
- **Its advisories:**
  - [GitLab: CVE-2025-53110](https://advisories.gitlab.com/pkg/npm/@modelcontextprotocol/server-filesystem/CVE-2025-53110/)
  - [GitLab: CVE-2025-53109](https://advisories.gitlab.com/pkg/npm/@modelcontextprotocol/server-filesystem/CVE-2025-53109/)
  - [Snyk: directory traversal](https://security.snyk.io/vuln/SNYK-JS-MODELCONTEXTPROTOCOLSERVERFILESYSTEM-10734144)
  - [Snyk: symlink](https://security.snyk.io/vuln/SNYK-JS-MODELCONTEXTPROTOCOLSERVERFILESYSTEM-10734143)

  These were found by a web search on Nov 22, 2026.

## Software

- Python 3.12.9 in a virtualenv, plus pytest 8.3.3. The code uses only the standard library.
- Claude Code 2.1.330: `claude -p` for the Claude judge, the claim labeler, and as the MCP client. The models it reported are `claude-sonnet-5-5` and `claude-haiku-5-5`. No API key was used.
- Node 23.11.0 and npm/npx 10.9.2, only to run the other server. That server requires Node ≥ 24 (see `EVAL-OTHER-SERVER.md`).

## What Hemanth decided

- **The filter:** the answers to Q1–Q7 (role words, exclusions, seniority, location, sponsorship, threshold, shortlist size), and "c without phrases" for "Account" (FILTER.md section 7).
- **Claude's proposed parts of the filter:** "accept" for the evidence rules, the expected sources and the wrong versions.
- **Every hand verdict:** 95 postings, plus 20 for the X1 test, plus 90 in the second pass, all judged blind.
- **The rule changes after the audit:** "X1 accept, X2 reject, X3 reject, X4 Reject".
- **The claim labels:** "all ok" twice, then "a" (correct the three labels that broke the rule).
- **The trust decisions:** "T1 a, T2 a".
- **The follow-up tests:** "1 and 2 plus 3".
- **The second labeling pass:** "a" (all 90). The reason for it came from Hemanth: "I did not see the experience in job description".
- **v1.2 (delegated, not Hemanth's own choice):** "Do whatever you recommend and complete the project, I need to submit this today". Z5 was accepted; Y1, Y2, Y3 and Y5 were rejected.
- **The sign-off** (see `README.md`).

## What Claude contributed (Claude Code, Opus 5.5, Nov 20–22, 2026)

- **Proposals:** the plan, the gate questions and their recommended defaults, and the parts of FILTER.md marked "proposed by Claude" (the evidence rules, the expected sources, the wrong versions, R13, and the tie-break).
- **Code:** all of it, and all the tests: `js3/`, `scripts/`, `tests/test_js3_*`.
- **Runs:** the Nov 20 collection run, every filter run, the sampling, the audit computation, and the measurements of X1–X4.
- **Claude-produced data:** the claim labels (one fresh `claude -p` per posting), the rule re-check that found 3 labels breaking the rule, and every Claude-judge experiment.
- **Tool servers:** both transcripts and both evaluations, including finding the roots behavior and the `boards_with_result` gap.
- **Nov 22–24:**
  - the X1 out-of-sample test, E5, and the SEEDED injection test;
  - both labeling views. The first view's blind spot was Claude's choice, and Hemanth's remark exposed it;
  - the second-pass tooling (`js3/relabel.py`), including a view defect Claude found and fixed before any label;
  - the corrected-label reports;
  - the experience rule R17, with its cut-off measured among 3–6 and the range false friend.
- **Drafts:** `AUDIT.md`, `SHORTLIST.md`, `EVAL-OWN-SERVER.md`, `EVAL-OTHER-SERVER.md`, `SCORE.md`, `README.md`, this file and `FRICTIONAL.md`.
