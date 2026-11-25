# Sources

## What I used

| Source | Used for |
|---|---|
| Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/<board>/jobs?content=true` | Boards `stripe`, `cloudflare`, `striqe` (misspelled on purpose: 404). Saved responses in `evidence/raw/` (JS1/JS2 runs; JS3 fetched nothing new) |
| Ashby Posting API, `https://api.ashbyhq.com/posting-api/job-board/openai` | Board `openai`. Saved responses in `evidence/raw/` |
| My Job-Search Agent 2, course folder `fall-2026/hsuan-t/js2-loop-tools-diff/` | The starting point for JS3: loop, boards, permission policy, rule judge, Claude judge, persona, tests |
| Model Context Protocol (versions 2024-11-05 to 2025-11-25) | The message shapes the server answers (initialize, tools/list, tools/call, JSON-RPC errors). Written by Claude from its knowledge of the protocol, not checked line by line against the specification; what a real client sent is in the transcript. No MCP SDK is used |
| `modelcontextprotocol/servers`, `src/fetch` at commit `97ed9ec74f370222d4ceec50380d06dff36ac4e5`, https://github.com/modelcontextprotocol/servers/tree/97ed9ec74f370222d4ceec50380d06dff36ac4e5/src/fetch | The other tool server evaluated in `MCP_EVAL.md` (read, not run) |
| Claude Code 2.1.332 | The client in the real tool-server session (`transcripts/mcp-2026-11-25.jsonl`) |
| Clopper–Pearson exact binomial interval | The 95% intervals in `audit/AUDIT.md`, computed in `reports/audit_report.py` without a statistics library |
| JSON Resume schema, https://jsonresume.org/schema/ | Format of the fictional résumé (JS1) |
| Fictional persona Aarav Patel, from the course's Reallocation Engine examples | The résumé and profile every judgment uses (`@example.com`) |
| Claude Code CLI (`claude -p`), model `claude-sonnet-5-5` | The Claude judge in F5 E2 (40 calls, 2026-11-25) |
| pytest 8.4.2; Python 3.11 standard library | Tests; everything else |

## What I wrote

**Job-Search Agent 3**
- The decisions in `FILTER.md`: I read and corrected every rule's reason and signed v1 (2026-11-24) before any JS3 code; missing information passes and the claim is labeled `insufficient`, and the agent abstains only when there is no text (§2); the wrong versions W1 and W2 (§4); v2: add A and B2, reject B1, C and L1, and judge years by a ratio, the way I actually decide; v2.1: replace the rule-5 phrase "without sponsorship"; sign-off of v2.
- The 50 hand verdicts in `audit/hand_verdicts.csv` and the 20 in `heldout/hand_verdicts.csv`, each with my reason, judged blind to the filter's verdict. The choice of S20 as the false friend.
- The shortlist review in `shortlist/review.csv`: the Privy AWS claim is `insufficient`, and the stack match counts as a plus for fit.
- The trust decisions in `MCP_EVAL.md`: our server trusted as is; `fetch` not connected.
- In F5: fresh held-out labels only; adopting prompt v3 for consistency, not for its score.
- The sign-off and the driver's seat in `README.md`.

**Earlier layers** (unchanged): JS2's `GATE.md`, the review in `REVIEW_PACKET.md` §4–7 and its sign-off; JS1's contract, labeling rule, hand labels, prompt revision choice and action-surface decision.

## What Claude contributed

Claude (Claude Code, Claude Opus) contributed, at my request and checked by me:

**Job-Search Agent 3**
- **FILTER.md:** the first draft of every reason tagged `[AI]`, §2–§4, and the measurements it quotes (`reports/filter_v1_measure.py`, `filter_v2_measure.py`).
- **Code:** `reports/audit_run.py`, `audit_sample.py`, `audit_report.py`, `shortlist.py`, `heldout_sample.py`, `f5_experiment.py`, `job_agent/mcp_server.py`, and the FILTER v2 / v2.1 changes in `job_agent/judges/`. The first batch was built through agent-loop (an autonomous coding loop) against tests I approved; `docs/adr/` are that agent's design notes.
- **Tests:** all JS3 test code (`tests/test_js3_*.py`), and the red runs against the wrong versions.
- **Analysis:** drawing the audit and held-out samples; the k/n counts and intervals; checking every shortlist quote against the raw files; proposing S20 and the v2 candidates; running E1 and E2.
- **Documents:** drafts of `audit/AUDIT.md`, `shortlist/REVIEW.md`, `MCP.md`, the evidence sections of `MCP_EVAL.md`, `reports/what_moves_the_score.md`, this README and this file.

**Earlier layers:** GATE's skeleton and review, all JS2 code and tests, the JS2 documents (JS2's `SOURCES.md` in the course folder lists them).
