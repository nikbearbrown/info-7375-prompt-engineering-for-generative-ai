# Job-Search Agent 3 — Filter, Tool, Score

INFO7375, Pavan Majji. Folder: `fall-2026/pavan-m/js3-filter-tool-score/`

The JS2 agent collects about 1,300 postings per run from three boards. JS3 decides which ones reach Alex Morgan (fictional persona, `data/persona_alex.json`) and why: a written, versioned filter (FILTER.md), a hand audit of what it rejects, a source-grounded shortlist, the filter offered to Claude as an MCP tool written from scratch, and a measurement of what moves the score. My real résumé is not in this repo.

**Started from:** my own JS2 (`../js2-loop-tools-diff`, submitted at `70f8e203`), copied unchanged with its Nov 10 state (`8f821de4`). I did not use the Reallocation Engine, Lectern, or other students' work.

## Language and toolchain
- Python 3.14.3 (Homebrew) in a project venv; httpx 0.28.1; pytest 9.2.0 (`requirements.txt`)
- Claude Code (desktop app; the transcript shows client `claude-code 2.1.330`) wrote the implementation against my FILTER.md and tests
- curl, for my own calls to the Microsoft Learn MCP server
- Timestamps are local time (EST, UTC−5)

## Run it from a fresh clone
```bash
cd fall-2026/pavan-m/js3-filter-tool-score
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -v                     # 69 tests, no network
```
Filter and measurement (no network, reads saved runs):
```bash
python -m agent.run_filter --run out/runs/2026-11-23T153111 --filter-config config/filter_v1_1.json
python -m agent.measure_filter --run out/runs/2026-11-23T153111 \
  --configs config/filter_v1_0.json config/filter_c1_years5.json config/filter_c3_uscity2.json
```
MCP server (stdio) and my own client:
```bash
python -m agent.mcp_client --run out/runs/2026-11-23T153111 \
  --postings ashby:openai:33acf0e2-5c11-46d7-9dc9-417f5537139b greenhouse:gleanwork:4742953005
```
To use it from Claude Code, start Claude Code in this folder; it reads `.mcp.json` and offers `score_posting`.
Live collection (calls the three allowed hosts; updates `out/state/`, restore with `git checkout -- out/state`):
```bash
python -m agent.loop --config config/boards.json; echo "exit code: $?"
```

## What ran (past tense)
| When | What | Result | Evidence |
|---|---|---|---|
| Nov 19 | Live run 1 | 1,284 postings, 134 new since Nov 10 | `out/runs/2026-11-19T190803/` |
| Nov 23 | Live run 2 | 1,290 postings, 40 new | `out/runs/2026-11-23T153111/` |
| Nov 23 | Filter v1.0 on run 2 | KEEP 31, REJECT 1,252, CANNOT TELL 7 | `out/filter/2026-11-23T153111/` |
| Nov 23–24 | Reject audit, 48 postings judged blind | 3 of 30 random rejects wrong (95% interval 3–26%); false friend "Python" | `audit/`, `AUDIT` section of FILTER.md §10 |
| Nov 24 | C1 and C3 measured; held-out set of 32 judged blind | C1 added (v1.1), C3 rejected | `out/measure/`, `heldout/`, FILTER.md §10 |
| Nov 24 | Filter v1.1 on run 2 | KEEP 22 | `out/filter/2026-11-23T153111/filter_v1_1/` |
| Nov 25 | Shortlist: 50 claims labeled | 17 supported, 7 contradicted, 26 insufficient | `SHORTLIST.md`, `shortlist/` |
| Nov 25 | MCP: my client, then Claude Code | handshake, tools/list, score_posting; apply_to_job refused | `out/transcripts/` |
| Nov 25 | Microsoft Learn MCP evaluated with curl | 7 requests and responses saved | `evidence/other_server_mslearn/` |
| Nov 25 | Live run 3 | 1,304 postings, 37 new; v1.1 KEEP 22 | `out/runs/2026-11-25T061851/` |

Agent runs on three real days: Nov 19, 23 and 25.

## Documents
`FILTER.md` (v1.0 written first, §9 implementation clarifications, §10 rules added/cut/rejected) · `audit/` (rule, blind sheet, my verdicts, comparison) · `heldout/` · `SHORTLIST.md` · `TOOL_SERVER.md` · `WHAT_MOVES_THE_SCORE.md` · `SOURCES.md` · `FRICTIONAL.md`

## Sign-off — Job-Search Agent 3

**Checked**
- The five wrong versions in FILTER.md §5 are caught: `test_wv1_java_does_not_match_javascript`, `test_wv2_title_alone_does_not_qualify`, `test_wv3_repetition_does_not_raise_score`, `test_wv4_missing_description_is_cannot_tell_not_reject`, `test_wv5_matching_is_case_insensitive`
- Key rules: score math (`test_strong_match_is_kept_with_the_expected_score`), years rule (`test_eight_plus_years_is_rejected`, `test_five_years_is_not_rejected_by_the_years_rule`), Manager/Senior, plain Remote, non-US, 50 words, "Spring", HTML decoding (tests/test_filter.py)
- Config defaults stay v1.0 and each change works without overreaching: tests/test_filter_config.py (6 tests)
- MCP protocol behavior: tests/test_mcp_server.py (8 tests), including `test_unknown_tool_is_a_protocol_error` (apply_to_job refused) and `test_tools_call_uses_v1_1_years_cutoff`
- The filter against my judgment: 48 blind audit verdicts and 20 blind held-out verdicts
- The shortlist's claims against the posting text: 50 hand labels with evidence quotes

**How**
- Tests written by me before Claude Code's code: filter tests (`f0af2ebd`) before the filter (`c7574898`); config tests (`20ed62d2`) before `ed5b94b2`; MCP tests (`dd355c44`) before the server (`32353bfa`). `git diff tests/` was empty after every build.
- By hand: every audit, held-out and shortlist label, judged blind where possible (rule → sample → verdicts committed before opening each key)
- By recomputation: measure_filter re-scores all postings and reproduced all 48 recorded audit decisions; Wilson intervals for every rate
- With Claude's help: Claude Code wrote all of `agent/filter.py`, `run_filter.py`, `measure_filter.py`, `mcp_server.py`, `mcp_client.py` and `.mcp.json`. Claude (chat) helped me plan, reviewed FILTER.md, wrote test skeletons and sampling scripts (I wrote every assert and every label), and drafted SHORTLIST.md, TOOL_SERVER.md, WHAT_MOVES_THE_SCORE.md and this README from my results.

**Not checked** **Signed** Pavan Jayant Majji 25/11/2026
1. The Lever retrieval gap is not fixed: the adapter never reads Lever's `lists` field, so Palantir's requirements are invisible to the filter (A30 confirmed; H02, H27 likely).
2. Abstention works only per posting: claims like "Alex's ~3 years fits" are made even when the posting states no years (S02, S05, S07, S10).
3. The 50-word rule counts words, not meaning: filler passes it (shown in the Claude Code session).
4. The years rule misses spelled-out numbers ("at least five years", S09) and ranges ("8–10 years").
5. No internship rule: 7 of C3's 9 bad additions were internships.
6. C1 is unproven beyond development data: held-out showed no difference in 20 postings.
7. My MCP server declares `readOnlyHint: true` but writes every call to a transcript file; I did not test it under a network monitor.
8. Microsoft Learn's prompts, resources and logging capabilities were not tested.

**Not claiming**
- That a KEEP is worth Alex's time: only 17 of 50 shortlist claims (34%) are supported by the posting text.
- That the filter's error rate is known: 3/30 random rejects gives 3–26%.
- That anything was trained: v1.1 is a config file, and Claude Code's tool knowledge comes from `.mcp.json`.
- That results generalize beyond 3 boards, one persona, and my own labels.

**Signed** Pavan Jayant Majji 25/11/2026

## Driver's seat
| Part | Claude should do | I should do | Why it stays mine | Evidence |
|---|---|---|---|---|
| The filter rules | Review for gaps and contradictions | Write FILTER.md and decide every rule and number | It encodes what is worth Alex's time | `5639e4c8` before any build; FRICTIONAL Entry 3 |
| Tests | Suggest structure | Write every assert before the code | Tests must not come from the code they test | `f0af2ebd`, `20ed62d2`, `dd355c44` |
| Implementation | Write the filter, measurement, MCP server and client | Run the tests, read its choices, record the ones that change FILTER.md | Writing code is where Claude is strong | `c7574898`, `3ee6855c` (FILTER.md §9) |
| The audit | Draw the random sample; compute intervals | Judge all 48 and 32 postings blind | The audit checks the filter against my judgment, so the judgment can't come from a tool | `6f3d549d` → `0801bc2c` → `a978db3f`; `8bdc8a9e` → `bc6d587c` |
| Rule changes | Measure each change | Choose which to test, and accept or reject on evidence | A rule is a decision about Alex's time | `69c8c51b`; FILTER.md §10 |
| The shortlist | Generate the claims | Label every claim against the text | Whether a claim is true needs reading, not matching | `8b0c791c` |
| Trust in a tool server | Report what each server does | Decide what I trust it for | Trust is a decision about my risk | TOOL_SERVER.md, `2f1a024c` |
| Whether a posting is worth my time | Score it | Decide | The score is keyword evidence; the decision costs a day of my life | SHORTLIST.md (34% supported) |
