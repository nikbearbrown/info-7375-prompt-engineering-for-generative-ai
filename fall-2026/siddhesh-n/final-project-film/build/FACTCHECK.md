# FACTCHECK — checkedsql-pitch (v2, 2026-10-24)

Every claim in the narration, checked against its source. "Will" claims are plans and are marked PLAN.
Numbers come from `checkedsql/` and were re-run with `python3 checker.py` and `python3 answer_key.py --check`.

| # | Beat | Claim | Verdict | Source |
|---|---|---|---|---|
| 1 | BIDEA | I'm Siddhesh Nikam; this is my final-project pitch | PASS | the student |
| 2 | BDEFS | ROAS = revenue ÷ ad spend | PASS | standard definition; `tests/questions.json` Q03 note |
| 3 | B00 | CheckedSQL will take a plain-English question, have Claude write SQL, run it, show the answer with the query, scored against a key | PLAN | PROJECT-BRIEF §1 |
| 4 | B00 | the question shown, "Which channel had the highest ROAS?", and its answer "Search" | PASS | `tests/questions.json` Q06; `results/baseline.md` |
| 5 | B01 | on Oct 24, with Claude's help, I built the synthetic dataset, ten test questions with an answer key, and the checker | PASS | `checkedsql/` files; SOURCES (Claude wrote the code and data to my spec) |
| 6 | B01 | still to come: prompt contract, Claude step, evaluation log | PLAN | PROJECT-BRIEF "Will exist" |
| 7 | B02 | my marketing campaign project has a Tableau dashboard, made with AI help | CORRECTED → PASS | v1 said "one I built"; the student confirmed on 2026-10-24 that AI made it. The README links the dashboard. |
| 8 | B03 | the chat-assistant test: tool, date, and its answer | PASS | `build/chat_test_full.png` (2026-10-24): "Search had the highest ROAS at 3.98×"; Email 2.29×, Social 1.05×, matching the key |
| 9 | B04 | `python3 checker.py` already works and prints a score table | PASS | ran 2026-10-24: `Score: 10/10 · traps caught: 2/2` |
| 10 | B05 | "get marketing metrics right, checked against an answer key"; verification and evaluation have real evidence (checker, score table); the contract is next | PASS / PLAN | `checker.py`, `results/baseline.md` |
| 11 | B06 | the checker refuses anything but a single read-only SELECT | PASS | `checker.py` `run_query()` |
| 12 | B06 | twenty-four rows, synthetic | PASS | `data/campaigns.csv` (24 data rows), README "synthetic" |
| 13 | B07 | baseline SQL drafted with Claude scored 10/10 before any Claude step in the tool; two deliberately wrong row-average queries both failed | PASS | `results/baseline.md` |
| 14 | B07 | answer key worked out from the totals | PASS | `answer_key.py` (no SQL), `HAND-CHECK.md` |
| 15 | B08 | Email has eight rows; four spend almost nothing (20–30) and return 14–20× | CORRECTED → PASS | `campaigns.csv`: Mobile rows spend 20/25/20/30, ratios 20.0/18.0/19.0/14.0. First draft said "fifteen to twenty"; narration fixed to "fourteen to twenty" |
| 16 | B08 | row-average Email ROAS = 9.75 | PASS | (20+2+18+1.69+19+1.5+14+1.8)/8 = 9.749 |
| 17 | B09 | total ÷ total Email ROAS = 2.29; best channel Search | PASS | 6150/2685 = 2.290; Search 28000/7030 = 3.983; Social 4710/4470 = 1.054 |
| 18 | B09 | the test set has ratio questions; the mistake "gets caught, as it just was" | PASS | Q06, Q07; trap queries failed in `results/baseline.md` |
| 19 | B10 | my earlier repo was built with a lot of AI help; it shows the domain (CTR, ROAS) more than coding skill | CORRECTED → PASS | v1 claimed SQL/PostgreSQL/pandas as existing skills with that repo as evidence; the student confirmed on 2026-10-24 that AI wrote most of it |
| 20 | B11 | exists today: two earlier repos, this film, dataset, questions, key, checker | PASS | GitHub + `checkedsql/` |
