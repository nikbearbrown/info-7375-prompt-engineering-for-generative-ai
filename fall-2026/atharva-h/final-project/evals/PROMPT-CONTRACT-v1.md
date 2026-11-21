# SponsorSQL prompt contract — version 1

**Version history:** drafted by Claude on 2026-11-21 (morning) as a proposal. On 2026-11-21 at 13:15 EST, before any agent code, one change was made: the required output gained a `rows_sql` field, so the system can show the matching rows. Nothing else changed. This is the version the agent sends to the model in development round 1. Later versions are separate files.

## Input

A plain-English question, the fixed FY2026 Q3 LCA schema below, the source SHA-256, and the exact interpretation rules in `ANSWER-KEY.md`. The only table is `lca`, loaded with `load_lca_sqlite.py`. It has one row per populated LCA case. The input workbook is public DOL data; contact, attorney, preparer, address, phone, and email fields are excluded from this table.

Available columns: `sheet_row`, `CASE_NUMBER`, `CASE_STATUS`, `DECISION_DATE` (ISO date), `VISA_CLASS`, `JOB_TITLE`, `SOC_CODE`, `SOC_TITLE`, `TOTAL_WORKER_POSITIONS`, `EMPLOYER_NAME`, `TRADE_NAME_DBA`, `EMPLOYER_FEIN`, `WORKSITE_CITY`, `WORKSITE_STATE`, `WAGE_RATE_OF_PAY_FROM`, `WAGE_RATE_OF_PAY_TO`, `WAGE_UNIT_OF_PAY`, `PW_WAGE_LEVEL`, and `TOTAL_WORKSITE_LOCATIONS`. Except `sheet_row`, these are text fields; numeric wages and counts need explicit casts.

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
