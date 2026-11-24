# Fact check — Ground Truth SQL final project film v4

## Executive summary

Every number and claim in the four-part final film, with where it comes from. v4 (2026-11-22) re-cuts
the v3 pitch film (approved by Riya 2026-10-22) into executive summary / introduction / methods /
evaluation. Claims carried over from v3 keep v3's sources and verdicts (items 1-16). New in v4:
the BIRD human-vs-AI line (B06), the Chinook counts (B09), the method steps (B10-B13), what the
project needs (B14) and the pass bar (B19).

Status: checked by Claude (Opus 5.5, Claude Code), 2026-11-22, against the sources named. Riya Kapadnis's sign-off: APPROVED 2026-11-23, after watching the final 4:35 cut with sound (after her two requested changes, B05 and B20).
Rule used: past tense only for what exists and can be shown; everything else is "will" / "planned".

| # | Beat | Claim | Verdict | Source | Fix |
|---|---|---|---|---|---|
| 1 | B02 | Wrong (fan-out) query reports USA revenue 4,667.06; Canada 2,689.96; France 1,722.10; runs with no error | PASS | `evidence/run_slice.py` Q03 wrong variant, output 2026-10-19 | On-screen tag: "example SQL · drafted with Claude, checked by me" |
| 2 | B02 | The real answer is 523.06 | PASS | Q03 gold | — |
| 3 | B03 | People ask in plain English and don't see the SQL; models don't know a schema; wrong SQL doesn't crash; the number ends up in reports and decisions | EXEMPT (general explanation, no figure) | the real cases in B02/B13 show the crash point | Worded as a general reason, no statistic |
| 4 | B04 | Ground Truth SQL: give it your data and questions, it says which answers were wrong and why | EXEMPT (plan, "I'm building") | PROJECT-BRIEF.md §1 | Report-card rows on screen use the real Q03/Q06 causes; Q01 tick |
| 5 | B05 | Where it will be used and who it helps | EXEMPT (intended use) | PROJECT-BRIEF.md §2-3 | No customers or deployments claimed |
| 6 | B06 | BIRD: 12,751 question-SQL pairs, 95 databases, scored by checking results (execution accuracy) | PASS | bird-bench.github.io, "over 12,751 unique question-SQL pairs, 95 big databases"; re-read 2026-11-22 | — |
| 7 | B06 | People score about 93 percent; the best AI still scores lower | PASS | bird-bench.github.io EX leaderboard, read 2026-11-22: "Human Performance Data Engineers + DB Students" test 92.96; highest model row read: AskData (AT&T CDO - DSAIR), test 83.40, Oct 22 2026 | The page was truncated when read, so no system is named as #1; the AI bar is drawn at 83.4% and labelled only "lower" |
| 8 | B06 | BIRD tests AI only on its own databases | PASS | same page; its 95 databases are fixed | — |
| 9 | B07 | Vanna writes SQL on your data and has a built-in answer test that looks for words; on this data it passed the answer nine times too high | PASS | `evidence/vanna_check.py`, Riya's run 2026-10-21, Vanna 2.0.2 `OutputEvaluator` gave PASS to the 4,667.06 rows | Screenshot of her run, labelled |
| 10 | B08 | Benchmarks check numbers but not on your data; tools work on your data but don't check numbers; Ground Truth SQL does both | PASS (as a summary of items 6-9) / EXEMPT for GTSQL (plan) | items 6-9 | "does both" is the design, said in present tense as what it is built to do |
| 11 | B09 | Chinook: free sample music store database, 11 tables, 59 customers, 412 orders, 2009 to 2013, MIT license | PASS | read-only queries on `evidence/data/Chinook_Sqlite.sqlite` 2026-11-22: 11 tables, COUNT(Customer)=59, COUNT(Invoice)=412, InvoiceDate 2009-01-01..2013-12-22; `evidence/data/CHINOOK-LICENSE.md` | — |
| 12 | B10 | About fifty questions (plan), each with a checked answer, each checked a second way in plain Python from raw tables; on screen "today 8 of 8 agree" | PASS (8 of 8) / EXEMPT (50 is the plan) | `evidence/cross_check.py` + `cross_check_output_2026-10-21.txt` (8/8) | — |
| 13 | B11 | Claude answers three times; sees only the table layout and the question; one read-only query; never changes data | PASS | `evidence/claude_runs/2026-10-21/` prompt (schema + questions only, three runs); PROJECT-BRIEF.md §4 prompt contract; read-only connection | — |
| 14 | B12 | Two different queries both return 523.06 | PASS | Q03 equivalent variant, run_slice.py | — |
| 15 | B13 | Causes with wrong/right numbers: revenue 4,667 vs 523 (order counted once per song); long songs 3,503 vs 1,069 (ms as seconds); rock buyers 835 vs 59 (purchases not people); busiest rep empty vs Jane Peacock (wrong columns) | PASS | Q03, Q06, Q04, Q05 in run_slice.py; v3 items 3-8 | — |
| 16 | B14 | Needs: laptop, Python, the free database; no cloud servers, no extra token credits; Claude via Riya's Claude Code plan, same as the first runs | PASS | Riya, 2026-11-22 (chose "Claude Code (my plan)"); 2026-10-21 runs were Claude Code subagents; SQLite runs locally | — |
| 17 | B15 | Scope: one sample database, ~50 questions, Claude; not a chat app; never changes data | EXEMPT (plan) | PROJECT-BRIEF.md §5 | — |
| 18 | B16 | On 9 hand-labelled test queries (3 correct rewrites, 6 with a mistake), comparing wording judged 6 right, comparing results 9 | PASS | last two lines of run_slice.py output | — |
| 19 | B17 | Claude answered the 8 questions three times; 22 of 24 passed; both fails Q02, a France/Brazil tie at 5 | PASS | `evidence/claude_runs/2026-10-21/`, `score_claude_runs.py`; tie checked read-only | Terminal output shortened, tagged |
| 20 | B18 | Answer-key question asked about 2023; data ends 2013; empty gold let a broken query match; runner now rejects empty gold | PASS | `evidence/run_slice_output_v0_first_run.txt`; run_slice.py assert | — |
| 21 | B19 | Pass bar: checker agrees with hand labels every time; every answer key passes the second check; every miss has a named cause; did not work if Claude gets everything right; "today it nearly does" (22 of 24) | EXEMPT (criteria, Riya's choice 2026-11-22) / PASS for 22 of 24 | Riya chose the draft bar 2026-11-22; item 19 | — |
| 22 | B20 | "In conclusion" recap: checker works; Claude 8 questions x3, 22/24, both fails the question's fault; next ~50 harder questions | PASS | items 18-20 | Closing line is a slogan, EXEMPT |
