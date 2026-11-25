# SOURCES — Job-Search Agent 3

What I used, what Claude contributed, and what I wrote or decided myself. All dates are 2026-11-25.

## What I used

| Source | What I took from it |
|---|---|
| My JS1 folder `../js1-contract-and-watch/` | `rule.py` (byte-identical, SHA-256 `2aa42900…`); `claude_judge.py` (one import line changed); `prompts/baseline-v1.txt` and `revision-v1.txt`; the persona; the rules R1–R5 and their reasons, quoted in FILTER.md; my labeling rule `experiment/LABELING-RULE.md` |
| My JS2 folder `../js2-loop-tools-diff/` | `boards.py` (byte-identical, `f17c20cc…`); the three raw responses of live run `2026-11-10T215306Z`, copied to `data/` and checked against the hashes in that run's record |
| My final-project plan (`../final-project-film/four-part-film/APPENDIX.md`, 2026-11-23) | The reject-audit pass line, "at most 1 of 30" |
| The Model Context Protocol reference server `fetch`, [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers), commit `97ed9ec74f370222d4ceec50380d06dff36ac4e5` | Its `server.py` (SHA-256 `dc6de86f…`), README (`028743a4…`), `pyproject.toml` and LICENSE, downloaded to Claude Code's scratch folder and read for the second evaluation. Not copied here. |

**Network requests** (all on 2026-11-25, by Claude Code): one GitHub API request for the `fetch` server's latest commit, and four downloads of its files from `raw.githubusercontent.com`. The agent and the tests make none.

## What Claude contributed

Claude Code (Opus 5.5, `claude-opus-5-5`) in one Claude Code session in VS Code.

| Part | What Claude Code did | What I did |
|---|---|---|
| Explaining JS3 | Explained it in simple steps; said which parts must be mine (FILTER.md decisions, hand labels) | — |
| `FILTER.md` v1 | Drafted it from my JS1 rules and reasons. Recommended D1–D3. | Chose D1–D3 ("ok as you say"); read the draft and replied "ok" before it was committed (`48488ab3`) |
| Code (`js3/`) | Wrote all of it: loader, filter, evidence rules, sampler, quick view, report, tool server, measurement. `rule.py` and `boards.py` are copies. | — |
| Tests (34) | Wrote all of them, **after** the code | — |
| Labeling sheets | Made the blind sheet and the shorter quick view; explained my rule in simple steps; answered my questions ("3+ years", location, clearance) | — |
| Labeling decisions | Suggested "3+ counts as 3 or fewer" (from my JS1 rule) and the clearance/visa "status unknown" rule. When I said he might be an immigrant, pointed out that his résumé says nothing about citizenship and that it must not be decided from his name. | Decided both ("ok") before any label |
| Labels 1, 4, 8–12, 17, 19 | **Declined** when I asked it to do the corrections. Then suggested a label for each **from my written rules**, naming the rule and the posting's words. | Confirmed all nine ("confirm all") |
| Labels for the other 53 | Saved my lines word for word. Asked how they were made, because batch 2's wording differed from batch 1. | Typed batch 1 myself. For batch 2, answered "I decided each one myself" (wording tidied, with or without help). |
| v1.1 | Found the "D.C." bug and the graduation-date keep in my labels; recommended A–F | Decided A–F ("ok") |
| Claude measurements | Ran 48 fresh `claude -p` judgments (15:53:53–15:54:37 UTC), all valid | — |
| Tool-server session | Ran Claude Code 2.1.283 as the client of my server (15:52 UTC, $0.07). Claude's reply is quoted in TOOL-SERVER.md as received. | — |
| `fetch` server evaluation | Downloaded its source at a pinned commit. Started a separate Claude reviewer, which read it and reported with line numbers. Claude Code checked six of its claims against the file. | Made the trust decision **as drafted**; I did not read the `fetch` source myself |
| Reports | Drafted AUDIT.md, WHAT-MOVES-THE-SCORE.md, TOOL-SERVER.md, the shortlist and its notes, and this README, from the saved results | — |
| Sign-off, driver's seat, FRICTIONAL facts | Drafted them | Check, change, and sign; write the "What I learned" lines |

**Claude responses shown in this folder:**
- Claude Code's reply in the tool-server session (2026-11-25, 15:52 UTC), quoted in full in TOOL-SERVER.md.
- 48 judgments in `measure/replies/`, two of them quoted in WHAT-MOVES-THE-SCORE.md.
- The `fetch` reviewer's report, summarized with line numbers in TOOL-SERVER.md and marked *(reviewer)* where Claude Code did not check a line itself.

**Transcripts:** the Claude Code conversation of my own work stays on my machine.

## What I wrote, ran or decided myself

| Part | What |
|---|---|
| D1–D3 (FILTER.md v1) | v1 counts every years phrase, and must-haves only is tested as M1; "I cannot tell" when C1, C3 or C4 is insufficient; pass line at most 1 of 30 |
| Labeling decisions | "3+ years" counts as 3 or fewer; clearance/visa *status* the résumé does not record is "status unknown", while an *active* clearance required is N |
| 62 hand labels | 53 mine and 9 confirmed suggestions, as above. The raw lines are in `audit/labels-raw.md`. |
| v1.1 decisions A–F | add "D.C." and the graduation-date rule; record "Platform Engineer" as a false friend without a rule; reject M1, M2 and title grouping |
| FRICTIONAL "What I learned" lines | *(to write)* |
| Sign-off | *(to sign or withhold)* |
