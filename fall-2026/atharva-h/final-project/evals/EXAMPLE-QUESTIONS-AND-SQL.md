# Ten example questions and Claude-written SQL

**Written by Claude (Claude Code, Opus 5.5) on 2026-10-24. None of these queries has been run.**

These are drafts of the kind of question an international student looking for data work would ask, plus the SQL Claude writes for each. In SponsorSQL this SQL is **the thing under test**. It is **not** the answer key. The answer key has to be my own work, done from the file without this SQL.

## What was checked, and what wasn't
- **Checked:** the column names (from the file's header row) and the literal values used below, from `profile-FY2026-Q3.json`, a standard-library scan of the file made on 2026-10-24:
  - `CASE_STATUS`: `Certified`, `Certified - Withdrawn`, `Withdrawn`, `Denied`
  - `VISA_CLASS`: `H-1B`, `E-3 Australian`, `H-1B1 Chile`, `H-1B1 Singapore`
  - `WAGE_UNIT_OF_PAY`: `Year`, `Hour`, `Month`, `Week`, `Bi-Weekly`
  - `WORKSITE_STATE`: two-letter codes on every data row
- **Not checked yet:** the values of `PW_WAGE_LEVEL` (assumed `I`–`IV`), the format of `SOC_CODE` (assumed to start `15-2051`), and the column types after loading.

## Assumed setup
- A DuckDB table `lca` loaded from `LCA_Disclosure_Data_FY2026_Q3.xlsx` (SHA-256 `f8ca8448…bd28b3`), keeping the original column names.
- The load must drop the sheet's **595,239 blank rows**. The sheet declares 1,032,735 rows after the header, but only 437,496 contain data.
- `TRY_CAST` is used wherever a column's type after loading is unknown.

"Data Analyst" means `JOB_TITLE ILIKE '%data analyst%'` throughout. That's a deliberate, testable choice: it misses `Data-Analyst` and `Data Science Analyst`.

---

### 1. Which employers filed the most certified H-1B cases for Data Analyst jobs in Massachusetts?
*(This is the example shown in the film, B03A.)*
```sql
SELECT EMPLOYER_NAME, COUNT(*) AS cases
FROM lca
WHERE CASE_STATUS = 'Certified'
  AND VISA_CLASS = 'H-1B'
  AND JOB_TITLE ILIKE '%data analyst%'
  AND WORKSITE_STATE = 'MA'
GROUP BY EMPLOYER_NAME
ORDER BY cases DESC
LIMIT 10;
```
Trap to test: grouping by `EMPLOYER_NAME` splits one employer across its spellings (see Amazon Data Services in the profile).

### 2. How many certified H-1B cases are for Data Analyst jobs with a worksite in Boston, MA?
*(The ChatGPT test question.)*
```sql
SELECT COUNT(DISTINCT CASE_NUMBER) AS cases
FROM lca
WHERE CASE_STATUS = 'Certified'
  AND VISA_CLASS = 'H-1B'
  AND JOB_TITLE ILIKE '%data analyst%'
  AND UPPER(TRIM(WORKSITE_CITY)) = 'BOSTON'
  AND WORKSITE_STATE = 'MA';
```
Trap to test: only the first worksite on each filing is in this file. Additional worksites are in the separate `LCA_Worksites` file.

### 3. Which ten cities have the most certified H-1B Data Analyst cases?
```sql
SELECT UPPER(TRIM(WORKSITE_CITY)) AS city, WORKSITE_STATE AS state, COUNT(*) AS cases
FROM lca
WHERE CASE_STATUS = 'Certified'
  AND VISA_CLASS = 'H-1B'
  AND JOB_TITLE ILIKE '%data analyst%'
GROUP BY city, state
ORDER BY cases DESC
LIMIT 10;
```
Trap to test: city spellings (`NEW YORK` vs `NEW YORK CITY`), and suburbs counted separately.

### 4. What is the median offered salary for certified H-1B Data Analyst cases, by state?
```sql
SELECT WORKSITE_STATE AS state,
       COUNT(*) AS cases,
       MEDIAN(
         TRY_CAST(WAGE_RATE_OF_PAY_FROM AS DOUBLE) *
         CASE WAGE_UNIT_OF_PAY
              WHEN 'Year' THEN 1      WHEN 'Month' THEN 12
              WHEN 'Bi-Weekly' THEN 26 WHEN 'Week' THEN 52
              WHEN 'Hour' THEN 2080 END
       ) AS median_annual_offer
FROM lca
WHERE CASE_STATUS = 'Certified'
  AND VISA_CLASS = 'H-1B'
  AND JOB_TITLE ILIKE '%data analyst%'
GROUP BY state
HAVING COUNT(*) >= 20
ORDER BY median_annual_offer DESC;
```
Trap to test: mixed pay units (hourly rows must be annualized), and `WAGE_RATE_OF_PAY_FROM` is the bottom of a range.

### 5. Which prevailing-wage levels do employers use for Data Analyst H-1Bs, and how many are entry level (Level I)?
```sql
SELECT PW_WAGE_LEVEL, COUNT(*) AS cases,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM lca
WHERE CASE_STATUS = 'Certified'
  AND VISA_CLASS = 'H-1B'
  AND JOB_TITLE ILIKE '%data analyst%'
GROUP BY PW_WAGE_LEVEL
ORDER BY PW_WAGE_LEVEL;
```
Trap to test: `PW_WAGE_LEVEL` values aren't profiled yet, and blank levels are possible.

### 6. Which employers filed certified H-1B cases for entry-level (Level I) data roles: Data Analyst, Business Analyst or BI Analyst?
```sql
SELECT EMPLOYER_NAME, COUNT(*) AS level_1_cases
FROM lca
WHERE CASE_STATUS = 'Certified'
  AND VISA_CLASS = 'H-1B'
  AND PW_WAGE_LEVEL = 'I'
  AND (JOB_TITLE ILIKE '%data analyst%'
       OR JOB_TITLE ILIKE '%business analyst%'
       OR JOB_TITLE ILIKE '%bi analyst%'
       OR JOB_TITLE ILIKE '%business intelligence analyst%')
GROUP BY EMPLOYER_NAME
ORDER BY level_1_cases DESC
LIMIT 25;
```
Trap to test: `'%bi analyst%'` matches any title containing those letters in a row, not just "BI Analyst". Check the matching titles.

### 7. Has a specific employer (for example, Capgemini America) filed certified H-1B cases for data roles, and under which job titles?
```sql
SELECT EMPLOYER_NAME, JOB_TITLE, COUNT(*) AS cases
FROM lca
WHERE CASE_STATUS = 'Certified'
  AND VISA_CLASS = 'H-1B'
  AND EMPLOYER_NAME ILIKE '%capgemini america%'
  AND (JOB_TITLE ILIKE '%data%' OR JOB_TITLE ILIKE '%analyst%')
GROUP BY EMPLOYER_NAME, JOB_TITLE
ORDER BY cases DESC;
```
Trap to test: the name match versus the employer ID. The profile shows three spellings of Capgemini America under one ID, and `TRADE_NAME_DBA` may hold yet another name.

### 8. Which job titles do employers use most for H-1B cases coded as Data Scientists (SOC 15-2051)?
```sql
SELECT JOB_TITLE, COUNT(*) AS cases
FROM lca
WHERE CASE_STATUS = 'Certified'
  AND VISA_CLASS = 'H-1B'
  AND SOC_CODE LIKE '15-2051%'
GROUP BY JOB_TITLE
ORDER BY cases DESC
LIMIT 20;
```
Trap to test: the `SOC_CODE` format isn't profiled yet, and many "Data Analyst" titles may sit under other SOC codes.

### 9. How many certified H-1B Data Analyst cases were decided each month?
```sql
SELECT DATE_TRUNC('month', TRY_CAST(DECISION_DATE AS DATE)) AS month, COUNT(*) AS cases
FROM lca
WHERE CASE_STATUS = 'Certified'
  AND VISA_CLASS = 'H-1B'
  AND JOB_TITLE ILIKE '%data analyst%'
GROUP BY month
ORDER BY month;
```
Trap to test: how dates load from Excel (serial numbers or text), and that the file only runs to June 30, 2026.

### 10. Which employers had the most Data Analyst cases certified and then withdrawn?
```sql
SELECT EMPLOYER_NAME, COUNT(*) AS certified_then_withdrawn
FROM lca
WHERE CASE_STATUS = 'Certified - Withdrawn'
  AND VISA_CLASS = 'H-1B'
  AND JOB_TITLE ILIKE '%data analyst%'
GROUP BY EMPLOYER_NAME
ORDER BY certified_then_withdrawn DESC
LIMIT 10;
```
Trap to test: a withdrawal has several possible causes (a filing correction, a role change), so it isn't evidence of anything about the employer by itself.
