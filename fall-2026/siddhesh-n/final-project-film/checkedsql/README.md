# CheckedSQL: first piece (baseline checker)

The first runnable piece of the project pitched in the film: ten test questions, an answer key, baseline SQL queries, and a checker that prints a score table. The code and synthetic data were written with Claude's help (see the film folder's SOURCES.md). **The tool has no Claude step yet.** That comes next, graded by this same checker.

## Run it (Python 3 standard library only, nothing to install)

```bash
python3 checker.py                 # scores queries/ against tests/questions.json
python3 answer_key.py --check      # recomputes the key in plain Python and confirms questions.json matches
```

Result on 2026-10-24 (saved in `results/baseline.md`): **10/10 on the baseline queries, and both deliberately wrong "trap" queries were caught.**

## What's here

| Path | What it is |
|---|---|
| `data/campaigns.csv` | 24 rows of **synthetic** campaign data (3 channels × 2 devices × 4 weeks). Invented for this test, not real company data. The numbers are chosen so the ROAS trap changes the answer. |
| `tests/questions.json` | the 10 questions and their expected answers (Q06 and Q07 are the ratio questions) |
| `answer_key.py` | computes every expected answer from the CSV with no SQL, so the key doesn't share a code path with the queries it grades |
| `HAND-CHECK.md` | the subtotals behind every answer, so each one can be checked with a calculator |
| `queries/q01.sql`–`q10.sql` | baseline SQL, one per question (drafted with Claude) |
| `queries/*_trap_row_average.sql` | deliberately wrong versions of Q06/Q07 that average ROAS row by row; the checker must fail them |
| `checker.py` | runs each query on an in-memory SQLite copy of the CSV, refuses anything but a single `SELECT` (read-only), and prints the score table |
| `results/` | saved score tables |

## The ratio trap, with real numbers

Averaging Email's eight row-level ROAS values gives **9.75** and makes Email look like the best channel. Total revenue ÷ total spend gives Email **2.29** and makes Search (3.98) the best. Both numbers look plausible; only one is right. That's the risk named in the pitch, and Q06/Q07 are there to catch it.
