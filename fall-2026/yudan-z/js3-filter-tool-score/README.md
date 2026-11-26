# Job-Search Agent 3 — The Filter, the Tool, and the Score

Yudan Zhou (@yudanzhou) · INFO 7375 · 2026-11-25

## Executive summary

This builds on my JS2 agent (GitHub commit `47bab91`). It adds three things.

**1. A versioned filter, audited by hand.** I hand-labelled 61 sampled postings without seeing the filter's decisions. The audit showed that v1 rejected postings I would send Mira to (5 of 30 random rejects). I then changed the filter one step at a time, measuring each step on 16 held-out labels. v1 found 0 of the 5 held-out Y postings; v4 finds all 5 and shows 1 of the 11 held-out N.

**2. An MCP tool server written from scratch.** It is read-only, and Claude Code used it in a real session.

**3. An account of where every number comes from.** All of them are hand-set or inherited, and none was fitted.

Under v4, 138 of 1,595 postings reach Mira, and **all 138 are "cannot tell"**: none of the postings states that it sponsors visas.

Mira is a **fictional persona** (`persona/resume.json`). No real résumé, contact or tracker is in this folder.

| Read | For |
|---|---|
| `FILTER.md` | the filter rules, evidence rules, expected sources, wrong versions, version history |
| `AUDIT.md` | the reject audit, my labels, what the sample can show, the false friend |
| `SHORTLIST.md` | the source-grounded shortlist, relevance vs entailment, the abstention rule and its counterexample |
| `TOOL-SERVER.md` | my MCP server and the official filesystem server: declared vs actual, entitlements, trust decisions |
| `SCORE-CHANGES.md` | the origin of every number, one change at a time, and why persistence is not training |
| `FRICTIONAL.md` | what went wrong and what I decided |
| `SOURCES.md` | data, code, and what Claude contributed |

## Language and toolchain

- **Python 3.14**, standard library only (no pip installs). Tested on Windows 11.
- **Claude Code CLI 2.1.314**, only for the one MCP session (`claude -p`), with model `claude-opus-5-5`.
- Git. Set the environment variables `PYTHONUTF8=1` and `PYTHONDONTWRITEBYTECODE=1`.

## Exact commands (run from this folder)

```
python -m unittest discover -s tests                     # 115 tests
python -m agent.run_filter filter/filter-v1.json         # writes runs/filter-v1.jsonl
python -m agent.run_filter filter/filter-v4.json         # writes runs/filter-v4.jsonl
python -m audit.measure filter/filter-v1.json filter/filter-v2a.json filter/filter-v2b.json filter/filter-v2c.json filter/filter-v2d.json filter/filter-v2e.json filter/filter-v2.json filter/filter-v2f.json filter/filter-v2g.json filter/filter-v3.json filter/filter-v4.json
python -m agent.shortlist runs/filter-v4.jsonl           # writes runs/shortlist-v4.md and .csv
python mcp/server.py                                     # the MCP server on stdio (one JSON-RPC message per line)
claude -p "<prompt in mcp/session/TRANSCRIPT.md>" --mcp-config mcp/claude-mcp-config.json --strict-mcp-config --allowedTools "mcp__js3-postings__search_postings,mcp__js3-postings__score_posting" --output-format stream-json --verbose
```

Nothing here touches the network except the `claude` command. The filter and the server read only `data/postings.jsonl`, the JS2 snapshot.

## What ran, and when (2026-11-25, EST)

| Time | What ran | Output |
|---|---|---|
| 16:11 | filter v1 on 1,595 postings; blind label sheet and sample key generated (seed 20261125) | `runs/filter-v1.jsonl`, `audit/LABEL-ME.csv`, `audit/sample-key.json` (commit `4469e7b`) |
| between 16:11 and 20:14 | **I labelled 61 rows by hand** in Excel | `audit/labels-pass1.csv` (commit `2ef8ac2`) |
| 20:14–20:21 | I re-checked 14 rows against the full text, then fixed row 39 | `labels-pass2.csv`, `labels-final.csv` |
| 20:26–20:42 | filters v2a–v4 run and measured against the labels | `runs/measure.txt`, `runs/filter-v2/v3/v4.jsonl` |
| 20:28 | **real Claude Code session** through `mcp/server.py`: 1 search and 3 scoring calls | `mcp/logs/transcript-2026-11-26.jsonl` (UTC date), `mcp/session/` |
| 20:43 | full test suite: **115 tests, OK** | `runs/tests.txt` |

**Not run:**
- the official filesystem MCP server: evaluated from its source only (`TOOL-SERVER.md` §2);
- the JS2 live fetcher: no new postings were fetched for JS3.

**Edited after the session, before submission:**
- **Session log.** The Claude session log's first line (the `system/init` record, which lists local paths and connectors) was removed. The session itself ran with that line present.
- **Config file.** In `mcp/claude-mcp-config.json`, the `command` was the full path to my Python interpreter when the session ran. The submitted copy says `python`.

## Privacy and safety

- **Persona.** The persona is fictional: an @example.com address and a 555 number.
- **Never sent.** No real résumé, contact list, tracker or credentials are here.
- **Read-only.** The agent never applies, emails, messages or logs in. The MCP server has no tool that writes, sends or fetches. Its only write is its own log under `mcp/logs/`.
- **Logs.** My Windows username has been replaced with `<user>` in every log.

## Sign-off

*The checks below were run by Claude on 2026-11-25. I re-ran the test suite myself in PowerShell (115 tests, OK), read each item, and agree with it.*

| | |
|---|---|
| **Checked** | (1) All 115 tests pass (`runs/tests.txt`). (2) Every number in AUDIT.md and SCORE-CHANGES.md matches `runs/measure.txt`. (3) The three v3 "keeps" really were supported by relocation and executive sentences (SHORTLIST §2). (4) The Claude session's tables match the tool results it received. (5) The submitted files contain no username, real résumé or credentials. |
| **How** | (1) Ran the test command above. (2) Re-ran `audit.measure` and compared the tables. (3) Read the three sentences in `runs/filter-v3.jsonl`. (4) Compared `mcp/session/claude-session.jsonl` with `mcp/logs/`. (5) Ran `grep` for the username over the folder. |
| **Not checked** | (1) Whether any of the 1,457 v4 rejects that nobody labelled is a posting I would want: 30 random rejects is a sample, not a census. (2) My N labels against the full posting text: only Y rows were re-checked. (3) The official filesystem server's runtime behaviour: I read its source and did not run it. (4) Whether any posting is still open today: the data is from 2026-11-09/10. |
| **Not claiming** | That the filter's error rate on all postings is known. That v4 is better than v3 on anything my labels measure: v3 and v4 differ in no labelled row. That "cannot tell" means Mira is eligible. That the agent learned anything: every change is a file I wrote. |
| **Signed or withheld** | **Signed: Yudan Zhou, 2026-11-25** |

## Driver's seat — who decided what

| Decision | Who decided | What the other side did |
|---|---|---|
| Start from JS2; the five role words; label ~60 postings | **me** (asked by Claude, 2026-11-25) | Claude proposed the options |
| FILTER.md v1 rules, weights and threshold | Claude drafted | I reviewed and agreed (2026-11-25) |
| Sample design (30 / 14 / 1 / 16, seed) and the blind sheet | Claude | Claude committed the sheet before I labelled, so the sample could not be chosen after seeing labels |
| **Every Y / N label** | **me** | Claude wrote the excerpts; they were incomplete (AUDIT §2) |
| Changing 8 labels after reading the hidden sentences; keeping the 6 with year minimums as Y | **me** | Claude showed me the 14 sentences |
| Row 39 → N | **me** | Claude pointed out the inconsistency |
| My Y rule: "any entry-level US job Mira can apply to" | **me** | Claude asked which rule my labels followed |
| Steps v2a–v2e, and rejecting v2e | Claude proposed and measured | I can explain each from `runs/measure.txt` |
| Adopting v2f (Excel) and v2g (senior), which cannot be measured | **me** | Claude found both and said they could not be measured |
| v4 evidence fix | Claude, as enforcement of my FILTER.md §2 | Claude told me before building it; I agreed (2026-11-25) |
| MCP server code; the filesystem-server evaluation | Claude wrote them | I can explain the trust decisions |
| Submitting | **me** | — |
