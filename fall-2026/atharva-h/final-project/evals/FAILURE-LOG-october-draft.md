# October draft SQL: observed evaluation, 2026-11-21

**Result: 3/10 pass against the independent FY2026 Q3 key. This draft is not ready to ship as an answering system.** A success bar for a later revised version is at least 8/10 on these fixed questions, no unsafe or off-schema query, and a separate held-out set that has not been used to tune the prompt. A lower score, or any unsafe query, means revise or narrow the tool.

The key and its definitions were written and checksum-recorded **before** opening `EXAMPLE-QUESTIONS-AND-SQL.md`. `evals/evaluate_draft_sql.py` executes SQLite ports of the ten October Claude-written queries. `ILIKE`, `TRY_CAST`, `MEDIAN`, and `DATE_TRUNC` were translated because DuckDB is not installed; the filters and output limits of the draft were retained. Alphabetical tie breakers were added so top-ten results are deterministic. This checks saved draft SQL; it is **not** a new live Claude Code run or a human Excel review. The full SQL ports, actual values, expected values, and source hashes are in `draft-sql-results.json`.

| Q | Result | Observed reason |
|---|---|---|
| 1 | Pass | The ten leading filed employer names and counts in Massachusetts match. This does not prove every underlying case was selected. |
| 2 | Pass | Boston returns 40 distinct cases; the independently counted 40 source rows have 40 distinct case numbers. It checks only the worksite city recorded on each row. |
| 3 | Fail | Plano is 93 in the draft output versus 92 in the key; Dallas is 59 versus 62. The top-ten city list changes. The draft's substring title match includes near matches and misses punctuation or repeated-space variants. |
| 4 | Fail | The draft returns 28 jurisdictions, while the key covers 48 states plus DC. It silently adds `HAVING COUNT(*) >= 20` and annualizes nonannual wages using assumed hours/weeks. The key uses only filed `Year` wage values. This question needs the wage definition stated to users. |
| 5 | Fail | Level I is 1,026 versus 1,027; Level II is 1,605 versus 1,609. In the full certified H-1B set, the key includes 16 normalized Data Analyst phrase variants the draft misses (for example, `Data  Analyst`) and excludes 9 substring near matches the draft accepts (for example, `Data Analysts` and `Metadata Analyst`). |
| 6 | Fail | The draft returns only 25 names for a question asking which employers filed cases; the key has 1,114 filed names. It also adds `Business Intelligence Analyst` beyond the three phrases named in the question, and its top McKinsey count is 43 rather than 44. The three-role boundary should be clarified before a new model run. |
| 7 | Fail | The key has 51 Capgemini America cases under five exact titles across three verified name spellings. The draft's `data OR analyst` test brings in twelve additional titles such as Business Systems Analyst and Data Engineer; it also splits the company by filed spelling. |
| 8 | Fail | The draft adds `CASE_STATUS = Certified`, although this question asks about H-1B cases across all statuses. Its Data Scientist title count is 2,460 versus 2,636. |
| 9 | Fail | Monthly counts differ; for example April 2026 is 696 in the draft versus 701 in the key. The title substring rule both misses valid phrase variants and accepts near matches. The key's nine months total 3,780 cases. |
| 10 | Pass | The top-ten names and counts match after trimming surrounding whitespace for display. A trailing space on one source employer name is a display difference, not a substantive failure. |

## Limits and next decision

- This is one file and ten questions. It does not estimate accuracy on arbitrary prompts, future DOL releases, second worksites, or different employers.
- The old SQL was ported to SQLite, so this is a **ported-query evaluation**, not proof that the original DuckDB text ran unchanged.
- Question 4's annualization and question 6's BI wording are genuine specification choices; the key states one defensible interpretation, and a revised contract must settle them before further scoring.
- The project owner reported manually reviewing the files on 2026-11-21. No independent recount of the ten answers from the workbook was reported, so this is still an automated key rather than a personal hand count. A final evaluation sign-off remains separate.
- Do not present 3/10 as the score of a finished SponsorSQL agent. No prompt revision, held-out evaluation, human gate, or final system run has occurred in this check.
