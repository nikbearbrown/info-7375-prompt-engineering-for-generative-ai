# SponsorSQL prompt contract — version 2

**Version history:** v2 written 2026-11-21 after development round 1 (contract v1 scored 4/10; see `results/dev-round1-contract-v1.json`). It changes only what round 1 showed was missing; every change is listed in "Changes from v1" at the end. Held-out questions were not looked at when writing it. **Status: awaiting owner review** (gate 2 in `../gates.md`).

## Input

A plain-English question, the fixed FY2026 Q3 LCA schema below, the source SHA-256, and the interpretation rules in the next section. The only table is `lca`, loaded with `load_lca_sqlite.py`. It has one row per populated LCA case. The input workbook is public DOL data; contact, attorney, preparer, address, phone, and email fields are excluded from this table.

Available columns: `sheet_row`, `CASE_NUMBER`, `CASE_STATUS`, `DECISION_DATE` (ISO date), `VISA_CLASS`, `JOB_TITLE`, `SOC_CODE`, `SOC_TITLE`, `TOTAL_WORKER_POSITIONS`, `EMPLOYER_NAME`, `TRADE_NAME_DBA`, `EMPLOYER_FEIN`, `WORKSITE_CITY`, `WORKSITE_STATE`, `WAGE_RATE_OF_PAY_FROM`, `WAGE_RATE_OF_PAY_TO`, `WAGE_UNIT_OF_PAY`, `PW_WAGE_LEVEL`, and `TOTAL_WORKSITE_LOCATIONS`. Except `sheet_row`, these are text fields; numeric wages and counts need explicit casts.

## Interpretation rules (apply unless the question says otherwise)

- **Job titles:** to test whether a title contains a phrase, use the provided function `title_has(JOB_TITLE, 'data analyst') = 1`. It lower-cases the title, turns every run of punctuation or spaces into one space, and matches the phrase as whole words, so `Data-Analyst` and `Senior Data  Analyst` match but `Metadata Analyst` and `Data Analysts` do not. **Never** use `LIKE '%...%'` on `JOB_TITLE`.
- **Title classes:** use only the phrases the question names. "BI Analyst" means the phrase `bi analyst`; do not add `business intelligence analyst` or any other class the question does not name.
- **Statuses and visa class:** `CASE_STATUS = 'Certified'` exactly (`Certified - Withdrawn` is a different status). `VISA_CLASS = 'H-1B'` exactly (excludes H-1B1 and E-3). Apply a status filter only when the question asks for one.
- **Text values:** group and label by `TRIM(EMPLOYER_NAME)`, `TRIM(JOB_TITLE)`, `UPPER(TRIM(WORKSITE_CITY))` and `UPPER(TRIM(WORKSITE_STATE))`. Do not merge different employer spellings.
- **Blank values:** label a NULL or empty grouping value as `'[blank]'`.
- **Wages:** "offered annual base wage" means `CAST(WAGE_RATE_OF_PAY_FROM AS REAL)` on rows where `WAGE_UNIT_OF_PAY = 'Year'`; exclude other units rather than converting them. Use the provided aggregate `median(...)` for medians.
- **Worksite:** the one `WORKSITE_CITY` / `WORKSITE_STATE` pair on the row. Additional worksites are not in this table.
- **Rankings:** order by count descending, then the label ascending, and apply the `LIMIT` only when the question asks for a top N.

## SQLite functions provided by the system

`title_has(text, phrase)` returns 1 or 0 as described above. `norm(text)` returns the normalized text. `median(x)` is an aggregate. Standard SQLite functions are available; recursive queries, `PRAGMA`, `ATTACH` and other tables are not.

## Performance (each statement has a 10-second budget)

The table has 437,496 rows and no indexes. Do not join `lca` to itself or to a derived table on text columns. For `rows_sql` of a ranking, filter the base table with `... AND TRIM(EMPLOYER_NAME) IN (SELECT ... LIMIT 10)` (or the matching grouping expression) instead of a join.

## Required output

Return one JSON object with `interpretation`, `sql`, `rows_sql`, `answer_type`, `limits`, and `needs_clarification`. `answer_type` is one of `count`, `ranking`, `table`. If `needs_clarification` is true, leave `sql` and `rows_sql` empty and name the ambiguous choice in `interpretation`. Otherwise produce one SQLite `SELECT` query (or a `WITH` query ending in `SELECT`) in `sql` that computes the answer, and a second one in `rows_sql` that lists the public rows behind it (`sheet_row`, `CASE_NUMBER`, `CASE_STATUS`, `VISA_CLASS`, `EMPLOYER_NAME`, `JOB_TITLE`, `WORKSITE_CITY`, `WORKSITE_STATE`). The system, not the model, executes the query and shows the answer, query text, source checksum, and matching public rows used to calculate it. A count without the matching rows is insufficient for the promised user view.

## Rules for the SQL writer

1. Use only the listed table and fields. Never request or reconstruct omitted contact data.
2. Treat `Certified` and `Certified - Withdrawn` as different statuses. Do not turn an LCA into a visa approval, job offer, actual hire, or promise of future sponsorship.
3. State title matching, employer-name grouping, worksite, and wage-unit choices in `interpretation`. If the question does not settle a choice that changes the answer, ask for clarification or show clearly labeled alternatives. Do not silently add a `LIMIT`, minimum sample size, new status filter, or extra title class.
4. Count source rows when the question asks for cases. Count distinct `CASE_NUMBER` only when the question explicitly asks for distinct case numbers, after checking duplicates.
5. The workbook supplies one worksite city/state pair and a total worksite count, but not every additional worksite location. Say so when the question asks whether a role has *any* worksite in a city.
6. Use `WAGE_RATE_OF_PAY_FROM` as the lower bound of a filed base-wage range. Do not call it total compensation. Do not annualize nonannual units without a stated hours/weeks convention.
7. Include a deterministic order for rankings, with a secondary alphabetical tie breaker. Show the result limit to the user; do not truncate a question asking for all matches.
8. The application must execute SQL through a read-only SQLite connection with an authorizer that denies writes, attachment, and schema changes, plus a time and row budget. Model text is never executed as Python or shell code.

## Refuse or defer

Refuse requests to infer a specific person's visa status, predict approval, guarantee an employer will sponsor, reveal private contact data, or change the source or answer key without a human review. Defer an ambiguous question rather than returning one unmarked assumption as fact.

## Evaluation gate

The October draft SQL scored 3/10 under the fixed independent key after a SQLite syntax port. A later prompt revision is not ready to ship until it gets at least 8/10 on the ten development questions, at least 4/5 on a separately frozen held-out set, and zero unsafe SQL. These thresholds are decisions for the next build; they are not achieved results. Each failure should record the question, model output, executed SQL, expected answer, actual answer, matching row evidence, and cause. The project owner reviews any change to the prompt or key before re-scoring.


## Changes from v1

| Round-1 evidence | Change in v2 |
|---|---|
| D4, D5, D6, D9 failed: `LOWER(JOB_TITLE) LIKE '%data analyst%'` counted near matches and missed punctuation variants (predicted in `../pre-mortem.md`) | `title_has()` is provided and required for titles |
| D6 added `business intelligence analyst` | Use only the title phrases the question names |
| D8 grouped `JOB_TITLE` untrimmed, splitting `"Data Scientist "` from `"Data Scientist"` | Group and label by `TRIM(...)` |
| D5 labelled blanks `(blank)` | Label blanks `[blank]` |
| D3's evidence query joined `lca` to a CTE on text columns and hit the 10-second budget | Performance section: no self-joins; filter with `IN (SELECT ...)` |
| v1 referred to rules in `ANSWER-KEY.md` that the model never received | The rules are now written into the contract |
