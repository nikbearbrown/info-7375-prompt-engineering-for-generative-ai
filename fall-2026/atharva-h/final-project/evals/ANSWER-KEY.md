# FY2026 Q3 LCA answer key — independent workbook counts

**Status:** computed from the source workbook; the project owner reported manually reviewing the files on 2026-11-21. The count is automated. Independent manual verification of the underlying workbook rows has not been recorded.

**Source:** `LCA_Disclosure_Data_FY2026_Q3.xlsx`, 251,850,891 bytes, SHA-256 `f8ca8448a528671f784d3692923775a13741c99caec2816b2fe30c8885bd28b3`. The workbook has 437,496 populated rows and 595,239 blank sheet rows. One populated row counts as one LCA case, regardless of `TOTAL_WORKER_POSITIONS`. An LCA case is not a visa approval, job opening, or person hired.

**Reproduce:**

```bash
python3 evals/load_lca_sqlite.py /path/to/LCA_Disclosure_Data_FY2026_Q3.xlsx /tmp/sponsorsql.sqlite
python3 evals/build_answer_key.py /tmp/sponsorsql.sqlite evals/answer-key-results.json
```

The loader keeps only 18 public case, role, employer, worksite, and wage fields. It excludes employer contacts, attorneys, preparers, addresses, phones, and emails. The JSON file contains complete answer arrays, plus the 40 public rows behind question 2. Neither script reads the draft Claude SQL.

## Decisions made before comparing SQL

- **Certified** means `CASE_STATUS` is exactly `Certified`. `Certified - Withdrawn` is separate and appears only in question 10.
- **H-1B** means `VISA_CLASS` is exactly `H-1B`; H-1B1 and E-3 are excluded.
- **Data Analyst** means the whole phrase after case and punctuation normalization, so `Data-Analyst` qualifies. Senior titles also qualify; this is a filing-title question, not an entry-level job search.
- **Worksite** is the `WORKSITE_CITY` and `WORKSITE_STATE` recorded on the row. The file says how many worksites a case has, but does not give the city of every additional worksite. The counts below cannot find a Boston location present only as an unlisted second worksite.
- **Employer** means the name as filed, retaining case and punctuation variants, except question 7 where three Capgemini America spellings were checked to share one employer ID. A shared ID is not applied to every company: the profile shows some IDs spanning distinct names.
- **Wage** in question 4 means `WAGE_RATE_OF_PAY_FROM` when `WAGE_UNIT_OF_PAY` is `Year`. Hour, week, month, and bi-weekly figures are excluded instead of converted using an assumed schedule. This is the lower bound of the filed base-wage range, not total compensation.
- Top-ten ties are ordered by case count descending, then the filed name or city alphabetically. Full lists are in `answer-key-results.json` where the output has more than ten values.

## Ten answers

1. **Which employers filed the most certified H-1B Data Analyst cases in Massachusetts?** There are **116** matching cases. The top ten filed names and counts are: General Hospital Corporation 8; Brigham and Women's Hospital 5; Boston Medical Center Corporation 4; SCHNEIDER ELECTRIC USA, INC. 4; Staples, Inc. 4; CarGurus, Inc. 2; Federal Express Corporation 2; Logging-in.com, LLC 2; Massachusetts Mutual Life Insurance Company 2; Olympus Corporation of the Americas 2. **Check:** exact `Certified` and `H-1B`, normalized Data Analyst phrase, `WORKSITE_STATE = MA`, grouped by filed employer name.

2. **How many certified H-1B Data Analyst cases have a recorded worksite in Boston, MA?** **40 cases.** The 40 case numbers, source row numbers, employer names, and titles are in `answer-key-results.json` under `q2_matching_rows`. **Check:** the same filters as question 1, plus `WORKSITE_CITY = BOSTON`. A separate direct scan of the XLSX, without SQLite, found exactly the same 40 case numbers (`boston-source-check.json`). `Certified - Withdrawn` adds two and `Withdrawn` adds two; they are deliberately excluded. The earlier ChatGPT output of 40 agrees with this count under the first-worksite interpretation, but this does not establish its accuracy on other questions.

3. **Which ten cities have the most certified H-1B Data Analyst cases?** McLean, VA 210; New York, NY 179; Chicago, IL 107; Plano, TX 92; Atlanta, GA 79; Richmond, VA 71; Austin, TX 62; Dallas, TX 62; Houston, TX 55; Jersey City, NJ 47. **Check:** the 3,780 matching certified H-1B Data Analyst cases were grouped by the recorded city and state; no city/state was blank in this set.

4. **What is the median offered annual base wage for those cases, by state?** The full result for **48 states and DC** is under `q4_median_annual_base_wage_by_state` in `answer-key-results.json`, with each jurisdiction's sample size. There are **3,284** matching `Year` wage rows. **Check:** take the median `WAGE_RATE_OF_PAY_FROM` separately within each recorded worksite state or DC after the common status, visa, and title filters; exclude nonannual units rather than treating hourly figures as annual salaries.

5. **Which prevailing-wage levels do those cases use, and how many are Level I?** Level I **1,027**; Level II **1,609**; Level III **516**; Level IV **226**; blank **402**; total **3,780**. **Check:** group the same certified H-1B Data Analyst cases by `PW_WAGE_LEVEL`. A blank is reported, not treated as Level I.

6. **Which employers filed certified H-1B Level I cases with Data Analyst, Business Analyst, or BI Analyst titles?** **1,659 cases under 1,114 filed employer names.** The top ten filed names are McKinsey & Company, Inc. United States 44; MCKINSEY & COMPANY, INC. UNITED STATES 30; Amazon.com Services LLC 29; WAL-MART ASSOCIATES, INC. 23; ARTIFINT TECHNOLOGIES LLC 14; AUGMENTED REALITY TECHNOLOGIES LLC 13; ROBOTICS TECHNOLOGIES LLC 11; ARTIFICIAL INTELLIGENCE LLC 9; CLOUD SOCIAL TECHNOLOGIES LLC 9; Insight Global, LLC 9. The complete 1,114-name answer is in `q6_level_i_data_role_all_employers`. **Check:** exact status, visa, and Level I, then any one of the three normalized whole title phrases. The two McKinsey spellings remain separate under the filed-name rule.

7. **Has Capgemini America filed certified H-1B cases for those three data roles, and under which titles?** **Yes: 51 cases.** Titles: Data Analyst 3 (16), Business Analyst 3 (14), Data Analyst 2 (11), Business Analyst 2 (8), Business Analyst 4 (2). The three confirmed spellings contribute 43, 7, and 1 cases. **Check:** the three `Capgemini America Inc` spelling variants share one employer ID in the source; apply the common status, visa, and three-title-phrase filters, then group by exact job title.

8. **Which titles are most used for H-1B cases coded as Data Scientists (SOC 15-2051)?** Of **28,646** H-1B cases across all statuses, the top ten exact titles are Data Scientist 2,636; Data Engineer 1,321; Data Analyst 1,053; Business Intelligence Analyst 647; Senior Data Scientist 603; Business Analyst 493; Senior Data Analyst 397; Data Engineer II 345; Machine Learning Engineer 320; Data Scientist II 294. **Check:** `VISA_CLASS = H-1B`, `SOC_CODE` starts `15-2051`, all case statuses, grouped by title exactly as filed. This question does not say “certified,” so that filter is not added.

9. **How many certified H-1B Data Analyst cases were decided each month?** 2025-10: 6; 2025-11: 276; 2025-12: 244; 2026-01: 261; 2026-02: 221; 2026-03: 258; 2026-04: 701; 2026-05: 879; 2026-06: 934. Total: **3,780**. **Check:** apply the common status, visa, and title filters, then group `DECISION_DATE` by its year-month. The unusually small October count reflects this exact source file and should not be generalized to every DOL release.

10. **Which employers had the most Data Analyst cases certified and then withdrawn?** **223** H-1B cases have `CASE_STATUS = Certified - Withdrawn` and a normalized Data Analyst title. The top ten filed names are Johns Hopkins University 6; CAPGEMINI AMERICA INC 5; TRUSTEES OF THE UNIVERSITY OF PENNSYLVANIA 5; Northwestern University 4; Stier Solutions Inc 4; Brightside Benefit, Inc. 3; Mail Media, Inc. 3; UNIVERSITY OF CALIFORNIA, SAN DIEGO 3; VIRTUSA CORPORATION 3; ACE American Insurance Company 2. **Check:** use the exact `Certified - Withdrawn` status, not `Certified` and not any value merely containing the word “certified.”

## Name-spelling diagnostic

Across **all** statuses and visa classes, the source has 1,203 rows under four `Amazon Data Services, Inc` spellings: 849 without the final period, 315 with it, 32 in uppercase, and 7 with a stray backtick. The profile ties these four spellings to one employer ID. This is a data-quality stress case, not proof that every employer-ID group can be merged safely.

## Review boundary

The answers above are supported by the checked workbook, a reproducible SQLite import, full machine-readable outputs, and control totals that agree with the earlier file profile. The project owner reported reviewing the files manually, but did not report independently recounting each answer from the workbook in Excel. SQLite ports of the saved October Claude SQL were run and scored **3/10** against this key; see `FAILURE-LOG.md`. This is a score for the saved draft SQL, not a finished agent.
