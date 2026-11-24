# APPENDIX: Ground Truth SQL

Riya Kapadnis · INFO 7375 · Final Project Film (four-part cut, v4) · 2026-11-22

The film follows the four parts the brief asks for. This appendix holds the detail that does not
belong on screen. Every figure here comes from a file in `evidence/` or a source named next to it;
see `reel/FACTCHECK.md` for the beat-by-beat check.

| Part | Beats | Question it answers |
|---|---|---|
| 1. Executive summary | B01-B05 | What am I building, and why would anybody care? |
| 2. Introduction | B06-B08 | What have other people done, and what did they get? |
| 3. Methods | B09-B15 | How will I build it: data, steps, resources, scope |
| 4. Evaluation | B16-B20 | How will I know it worked, or that it didn't? |

## 1. Executive summary

AI tools can turn a plain-English question into SQL, run it, and return a number with no error,
and the number can still be wrong. In my first test, a common join mistake reported USA revenue
as 4,667.06 instead of 523.06, about nine times too high (`evidence/run_slice.py`, Q03).

Ground Truth SQL is a test for AI data assistants. You give it your own database and questions
with checked answers, and it tells you which answers the AI got wrong and why. It is for
analysts deciding whether to trust an AI SQL assistant, teams testing a tool before buying it,
and engineers deciding what to fix.

## 2. Introduction: what already exists

| Work | What it does | What it got | What it leaves out |
|---|---|---|---|
| **BIRD** (bird-bench.github.io, read 2026-10-09, 2026-10-21, 2026-11-22) | Public text-to-SQL benchmark: "over 12,751 unique question-SQL pairs, 95 big databases", scored by execution accuracy (results, not wording) | Human performance (data engineers + DB students): **92.96** test EX. Highest model row I read on 2026-11-22: AskData (AT&T CDO - DSAIR), **83.40** test EX, Oct 22 2026. The page was cut off when read, so I do not claim that row is #1 | Tests models only on its own 95 databases, not your schema or your questions |
| **Vanna 2.0.2** (github.com/vanna-ai/vanna, MIT; I ran it on Chinook 2026-10-21) | Writes SQL on your own database and ships an evaluation module | Its `OutputEvaluator` gave **PASS** to the 4,667.06 answer because the expected words "USA", "Canada", "France" were present (`evidence/vanna_check.py`). Its other evaluators check tool calls, time/tokens, or ask an LLM judge. I did not run the LLM judge (needs a paid key) | Does not compare result rows against a checked answer |

**The gap:** benchmarks check the numbers but not on your data; tools work on your data but
do not check the numbers. Ground Truth SQL checks the actual rows on your own data, and explains
each miss by its cause.

## 3. Methods

### 3.1 Data
Chinook v1.4.5 (`evidence/data/Chinook_Sqlite.sqlite`, MIT, Luis Rocha): a free sample music
store database. Read-only queries on 2026-11-22: 11 tables, 59 customers, 412 invoices dated
2009-01-01 to 2013-12-22, 3,503 tracks.

### 3.2 Steps
1. **Answer key.** About 50 plain-English questions, each with checked ("gold") SQL and its
   result. Every gold result is recomputed a second way in plain Python from the raw tables
   (`evidence/cross_check.py`; today 8 of 8 agree, Q02 and Q04 flagged). Empty gold answers are
   rejected (the Q08 lesson, B18). Ambiguous questions are fixed or marked.
2. **Claude answers.** Claude sees only the table layout and the question, and must return
   exactly one read-only `SELECT`. Anything else is logged as a contract violation, not fixed.
   Each question is answered three times, to show variance.
3. **Judge by results.** Both queries run on a read-only connection and the result rows are
   compared (order-insensitive unless the question asks for an order), not the SQL text.
4. **Report card.** A Markdown scorecard: pass rate, and every miss with its cause from a
   failure taxonomy (join fan-out, wrong key, unit error, COUNT vs COUNT DISTINCT, date
   handling, ambiguous question), with Claude's SQL beside the gold SQL and both result sets.
5. **Replay.** One command replays saved model answers offline, so anyone can re-run the
   report card without a key.
6. **(Stretch)** A capped repair loop (generate, run, read error, repair), measured for whether
   it fixes answers or only hides errors.

### 3.3 Resources
| Need | Status |
|---|---|
| Compute | My laptop. SQLite runs locally; no cloud servers |
| Model access / token credits | Claude through my Claude Code plan, the same way as the 2026-10-21 runs. No separate API key or extra token credits needed |
| Accounts | GitHub (riyask29) for the public repo |
| Data access | Chinook is public (MIT), already in `evidence/data/` |
| Software | Python 3 standard library + `sqlite3`; Vanna 2.0.2 only for the comparison in §2 |

### 3.4 Scope
- **In:** one database (Chinook), about 50 questions, Claude as the model under test, an
  execution checker, a failure analysis.
- **Out:** no chat app or UI, no write queries, no claims about production warehouses or other
  models. Chinook is 11 tables and 50 questions is small; results say nothing about scale.

### 3.5 Risks
I write both the questions and the answers, so the test may be too easy or the answers wrong.
Both have happened: Q08's first gold asked about 2023 when the data ends in 2013 (an empty gold
"matched" a broken query), and Q02's unstated tie order failed two correct Claude answers.
Mitigations: the second check in plain Python, the empty-answer rule, three runs per question,
harder questions next, and a second person checking a sample once the full set exists.

## 4. Evaluation

### 4.1 Does the checker judge correctly?
Nine test queries labelled by hand (3 correct rewrites, 6 with a mistake). Comparing SQL text
judged 6 right; comparing results judged 9 of 9 (`evidence/run_slice.py`).

### 4.2 First run on Claude (2026-10-21)
Three blind runs of Claude Opus 5.5 on the 8 questions (`evidence/claude_runs/2026-10-21/`,
replayed by `evidence/score_claude_runs.py`): **22/24 pass by rows, 0/24 by SQL text.** Both fails
are Q02, where France and Brazil tie at 5 customers and the question sets no tie order: the
question's fault, not Claude's.

### 4.3 What would tell me it worked
- The checker agrees with my hand labels on every labelled test query.
- Every gold answer passes the plain-Python second check.
- Every miss on the report card has a named cause from the taxonomy.

### 4.4 What would tell me it did not work
- Claude gets everything right: the questions are too easy to tell anything apart. Today it
  nearly does (22/24), so the next ~50 questions must be harder.
- The checker and my hand labels disagree, or a gold answer fails the second check.

## 5. Exists today vs. will exist

| Exists (2026-11-22) | Will exist |
|---|---|
| 8 gold questions + 9 labelled variants (`evidence/gold_set.json`) | ~50 harder questions, some marked ambiguous |
| Execution comparator, 9/9 (`run_slice.py`) | Report card in the README, built from the replay |
| Plain-Python second check, 8/8 (`cross_check.py`) | Failure taxonomy with counts, three-run variance per question |
| Three saved Claude runs, 22/24 (`claude_runs/`, `score_claude_runs.py`) | (Stretch) a measured repair loop |
| Vanna comparison (`vanna_check.py`) | A second person's check of a sample of gold answers |
