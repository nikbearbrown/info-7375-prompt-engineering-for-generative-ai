# Sign-off — Job-Search Agent 3

Tushar Patel · INFO 7375 · Fall 2026 · **DRAFT, written by Claude Code on 2026-11-25 for Tushar to review, then sign or withhold**

```text
Sign-off — Job-Search Agent 3
Checked:      the properties below, each with the test or check that shows it
How:          by hand / by a test I wrote before reading Claude's code / by recomputation / with Claude's help
Not checked:  the items listed under "Not checked"
Not claiming: the items listed under "Not claiming"
Signed or withheld: [Tushar: sign or withhold]
```

## Checked

The full suite passed (count in [evidence/test-runs/js3-final.txt](evidence/test-runs/js3-final.txt)).

- **The filter applies FILTER.md v0.1 as written, including the wrong versions it must catch.** [tests/test_filter.py](tests/test_filter.py) has one test per "Wrong versions" row 1–5. No test checks row 6 (a claim labeled supported because its keyword appears): it concerns claim labels, which I judged by hand ([SHORTLIST.md](SHORTLIST.md) section c). G1–G5 each have pass/fail/unknown cases.
- **v0.2 adds C1–C6 as switchable changes, and v0.1 mode still reproduces the original results byte for byte.** [tests/test_filter_v02.py](tests/test_filter_v02.py): a pass case and a fail or unknown case per change, single-change isolation on the saved run, and the sha256 of v0.1's `results.jsonl` from `6cc68807`.
- **The rules stayed frozen.** `git diff f3edf99 -- FILTER.md` is empty. Since `f3edf99` the only change under `agent/` is the new `agent/claims.py`.
- **The fetch stays on the allow-list.** [tests/test_permissions.py](tests/test_permissions.py) carries JS2's permission cases. [tests/test_content_query.py](tests/test_content_query.py) checks that `content=true` is allowed on the Greenhouse listing route only.
- **The live fetch counted what it saved.** [checks/independent_count.py](checks/independent_count.py) imports no agent code. It matched 777 / 170 / 32 on the three boards ([output](evidence/test-runs/live-text-1-independent-count.txt)).
- **The label sheets were blind.**
  - [tests/test_sheets.py](tests/test_sheets.py) checks that no filter output appears on the sheets or in the posting text files, that the draw is deterministic (seed 7375), and that the groups are disjoint.
  - [tests/test_label.py](tests/test_label.py) checks that the labeler writes each label once and never reads `out/`.
  - [tests/test_changed_sheet.py](tests/test_changed_sheet.py) checks that the changed sheet's posting cells equal a fresh build.
- **Every number in the reports comes from the blind labels and the saved data.**
  - [tests/test_audit_v01.py](tests/test_audit_v01.py) reruns `audit/audit_v01.py` and checks that it reproduces [audit/AUDIT-RESULTS.md](audit/AUDIT-RESULTS.md) verbatim from the blind labels, even after the corrections in `9ed99ceb`.
  - [tests/test_score_report.py](tests/test_score_report.py) does the same for [SCORE-REPORT.md](SCORE-REPORT.md) sections 2 and 2b, and checks section 1's values and line references against the code.
  - [tests/test_shortlist_report.py](tests/test_shortlist_report.py) does the same for every generated block of [SHORTLIST.md](SHORTLIST.md).
- **The claim pipeline cannot accept a quote that isn't in the posting, and saves no credentials.** [tests/test_claims.py](tests/test_claims.py) uses an offline fake client.
- **The MCP server does what its tests say, and nothing more.** [tests/test_mcp_server.py](tests/test_mcp_server.py) has 14 subprocess tests. An audit hook shows no socket, data reads limited to the corpus, FILTER.md and the persona, and writes only under `evidence/mcp/`. The results equal `agent.filter` in v0.2 mode. Four temporary mutations (socket, raw socket, a stray write, v0.1 scoring) each made a test fail, and were removed afterwards ([EVAL-FACTS.md](evidence/mcp/EVAL-FACTS.md)).

## How

- **By hand (Tushar):**
  - My blind labels:
    - audit, 48 rows, and held-out, 30 rows (`f97f528a`);
    - post-unblinding corrections on audit rows 19, 29, 40 and 45, recorded separately (`9ed99ceb`);
    - the changed set, 16 rows (`8d8e92f9`);
    - all 96 claims, labeled before I read Claude's proposed labels (`aaf850a0`).
  - My rule decisions: FILTER.md v0.1 (`821ddee3`), v0.2 and its freeze before the held-out comparison (`d74ca782`, `f3edf998`), and the changes I rejected (FILTER.md changelog).
  - The featured shortlist cases (`eaed4d92`).
  - My trust decisions on both MCP servers (`cd745787`, [EVALUATIONS.md](evidence/mcp/EVALUATIONS.md)).
- **By a test I wrote before reading Claude's code:** none. Claude Code wrote every test in `tests/`. The nearest thing is FILTER.md's "Wrong versions my tests must catch" table, committed in `821ddee3` before any JS3 code, which stated what the tests had to catch. [Tushar: confirm or correct]
- **By recomputation:** the report scripts `audit/audit_v01.py`, `audit/audit_v02.py`, `checks/score_report.py` and `checks/shortlist_report.py` recompute every reported number from the committed labels and data, and their tests require the committed reports to match the output exactly. `checks/independent_count.py` recomputes the fetch counts without importing agent code.
- **With Claude's help:**
  - Claude Code wrote the code, tests, report scripts and labelers. It drafted the prose of the audit, score and shortlist reports, EVAL-FACTS.md, this README, SOURCES.md and this sign-off draft.
  - It proposed the C4 heading definition from a survey of the text of all 979 postings (SCORE-REPORT.md section 1).
  - It ran both `claude -p` client sessions.
  - Claude (`claude-sonnet-5-5`, through the API, 2026-11-23) proposed the 96 shortlist claims and a label for each.
  - [Tushar: add any Claude chat contribution]

## Not checked

- **C1–C6 were measured only on 8 changed postings; the held-out set couldn't separate the modes.** No held-out row was one any change could move, so every mode scored 24/30. The changed set is selected, not random, and n = 8. ([SCORE-REPORT.md](SCORE-REPORT.md) sections 2 and 2b)
- **4 held-out labels look like slips and were left uncorrected to keep the set blind.** Rows 7, 24, 25 and 27 are non-engineering titles labeled keep. Held-out agreement therefore measures label quality as well as the filter. ([SCORE-REPORT.md](SCORE-REPORT.md) section 3)
- **The changed-sheet test now skips the label columns.** `test_committed_sheet_matches_a_fresh_build` leaves out `my_verdict`, `note` and `labeled_at` (`tests/test_changed_sheet.py:115-119`, since `2e4ee3ae`). No test protects those labels; only the git history from `8d8e92f9` does.
- **The evidence rule's treatment of silence conflicts with G5 and C1.** The gates count silence about experience or sponsorship as a pass. The evidence rule counts the same silence as insufficient, so the rule abstained on all 17 shortlisted postings. ([SHORTLIST.md](SHORTLIST.md) featured case 2 and "Open limits")
- **FILTER.md doesn't define what a contradicted critical claim does.** Five Stripe postings have a contradicted experience claim (`6042172`, `7476555`, `7292520`, `8131144`, `8243617`). ([SHORTLIST.md](SHORTLIST.md) "Open limits")
- **"infrastructure" still counts from Stripe boilerplate.** It comes from the same sentence that got "platform" removed, and in 421 postings that sentence is its only occurrence. It was counted separately, without a rule change. ([FILTER.md](FILTER.md) "False friend")
- **The MCP server checks "v0.2" against FILTER.md's bytes, not against `agent/filter.py`.** A change to the filter code would not be detected by the server. ([EVAL-FACTS.md](evidence/mcp/EVAL-FACTS.md), mismatch 3)
- **The `claude -p` client ran authenticated with the API key, not my claude.ai login.** Both runs printed that `ANTHROPIC_API_KEY` or another auth source took precedence. ([pre-fix reply](evidence/mcp/claude-client-reply-2026-11-24.txt), [post-fix reply](evidence/mcp/claude-client-reply-2026-11-24-postfix.txt))
- **Ashby's `isRemote` and `workplaceType` aren't used.** FILTER.md lists them as location fields, but the normalized posting leaves them out (`agent/postings.py:12-14`), so G3 never reads them.
- **No client run was made after `idempotentHint` was removed** on 2026-11-25. The post-fix transcript still shows `idempotentHint: true`. Only `tests/test_mcp_server.py` checks the current declaration.

## Not claiming

- That any verdict is a fact about a job. Verdicts are filter output on text saved 2026-11-22.
- That the sample miss estimates are rates for all postings. They are estimates from random samples of 30 rows.
- That Claude learned anything. Every behavior change was a change to a file; nothing was trained.
- That the MCP server is safe for auto-approval elsewhere. My trust covers local use with Claude Code and the tool allow-listed per run ([EVALUATIONS.md](evidence/mcp/EVALUATIONS.md)).

## Signed or withheld

[Tushar: sign or withhold]

## Driver's seat

| Part | What Claude did | What I did | Why it stays mine | Evidence |
|---|---|---|---|---|
| Filter rules | Claude Code implemented FILTER.md in `agent/filter.py`, and proposed the C4 heading definition. | I decided the gates, word lists, thresholds and C1–C6, rejected three variants, and froze v0.2 before the held-out comparison. | The rules encode what Cole wants. A rule changed after seeing results would measure nothing. | `821ddee3`, `d74ca782`, `f3edf998` |
| Reject audit | Claude Code built the blind sheets, the labeler and the audit script. | I labeled 48 audit and 30 held-out rows blind, and recorded post-unblinding corrections separately. | Only an independent judgment can show what the filter misses. | `f97f528a`, `0df210f7`, `9ed99ceb` |
| What moves the score | Claude Code ran each change alone and in combination, and wrote the report script. | I labeled the changed set blind before the group key was read. | Whether a change moves a posting the right way is decided by my label, not by the change. | `4c6754dc`, `8d8e92f9`, `2e4ee3ae` |
| Shortlist claims | Claude (`claude-sonnet-5-5`) proposed 96 claims and labels; Claude Code built the claim sheet and the report. | I labeled all 96 claims blind and chose the featured cases. | A claim is supported only if the posting's text supports it, and I made that call before reading Claude's labels. | `65c97a2e`, `aaf850a0`, `eaed4d92` |
| MCP server | Claude Code wrote the server and tests, ran both client sessions, and drafted EVAL-FACTS.md. | I made the trust decisions on my server and on the reference filesystem server, and required the declaration fixes. | Trusting a tool server is a decision about what may run on my machine. | `47282e94`, `cd745787` |
| **Is this posting worth Cole's time?** | The filter proposes a verdict, and Claude proposes claims and labels. Neither is the reference. | My blind labels are the reference that the filter and Claude are measured against: audit, held-out, changed set and claims. | Worth is a judgment about a person's time and goals. The filter only applies words I chose, and Claude disagreed with me on 11 of 96 claims. Both only propose. | `f97f528a`, `8d8e92f9`, `aaf850a0` |
