# SponsorSQL answer for review

**Question:** How many certified H-1B Data Analyst cases have a recorded worksite in Boston, MA?
**Source checksum recorded in this database:** f8ca8448a528671f784d3692923775a13741c99caec2816b2fe30c8885bd28b3
**Full answer SHA-256 (all rows):** 292177ccb01618f1b117a1316484a7f51560e3cafb80c433388ec31ed2b49b0a
**Full evidence SHA-256 (rows kept):** dc44cda11cd74125ea2981487df05ab7052d1a2ce56a37656567613b24d8d678

Model-written interpretation (not checked by SponsorSQL): Counts source rows with CASE_STATUS = 'Certified' exactly and VISA_CLASS = 'H-1B' exactly, whose JOB_TITLE contains the whole phrase 'data analyst' (title_has), and whose recorded worksite pair is Boston, MA (UPPER(TRIM(WORKSITE_CITY)) = 'BOSTON' and UPPER(TRIM(WORKSITE_STATE)) = 'MA'). Only the single worksite city/state pair on each row is checked.
Model-written limits: The table holds one worksite city/state pair per case plus a total worksite count, not every additional worksite location, so a case whose Boston worksite is only an additional location is not counted. This is a count of cases whose recorded worksite is Boston, MA, not of every case with any Boston worksite. Other city spellings (neighborhoods, misspellings) are not merged. Counts LCA cases, not visa approvals or hires.

## Answer
1 row(s)

| cases |
|---|
| 40 |

## SQL that produced the answer
```sql
SELECT COUNT(*) AS cases FROM lca WHERE CASE_STATUS = 'Certified' AND VISA_CLASS = 'H-1B' AND UPPER(TRIM(WORKSITE_STATE)) = 'MA' AND UPPER(TRIM(WORKSITE_CITY)) = 'BOSTON' AND title_has(JOB_TITLE, 'data analyst') = 1
```

## Matching rows (evidence)
40 matching row(s), first 20 shown

| sheet_row | CASE_NUMBER | CASE_STATUS | VISA_CLASS | EMPLOYER_NAME | JOB_TITLE | WORKSITE_CITY | WORKSITE_STATE |
|---|---|---|---|---|---|---|---|
| 8272 | I-200-25306-357292 | Certified | H-1B | Gupta Media Holdings LLC | Marketing Data Analyst II | Boston | MA |
| 24187 | I-200-25307-360814 | Certified | H-1B | CarGurus, Inc. | Senior Product Data Analyst | Boston | MA |
| 43289 | I-200-25322-419286 | Certified | H-1B | Brigham and Women's Hospital | Data Analyst I | Boston | MA |
| 47607 | I-200-25324-425744 | Certified | H-1B | Tufts Medical Center, Inc. | Data Analyst III (Stroke Center Data Analyst) | Boston | MA |
| 76062 | I-200-25350-486041 | Certified | H-1B | Apexsync Technologies LLC | Data Analyst | Boston | MA |
| 82326 | I-200-25356-502465 | Certified | H-1B | Cisco Systems, Inc. | Data Analyst | Boston | MA |
| 83166 | I-200-25360-510905 | Certified | H-1B | Cermax Corp. | Data Analyst | Boston | MA |
| 88831 | I-200-25364-516437 | Certified | H-1B | Brigham and Women's Hospital | Data Analyst II | Boston | MA |
| 110282 | I-200-26016-567907 | Certified | H-1B | Federal Express Corporation | Sr Data Analyst | Boston | MA |
| 128453 | I-200-26028-597827 | Certified | H-1B | Federal Express Corporation | Sr Data Analyst | Boston | MA |
| 144993 | I-200-26041-630477 | Certified | H-1B | Langan Engineering and Environmental Services, LLC | GIS/Environmental Data Analyst | Boston | MA |
| 146472 | I-200-26042-633674 | Certified | H-1B | General Hospital Corporation | Senior Data Analyst | Boston | MA |
| 149851 | I-200-26043-638165 | Certified | H-1B | Beth Israel Deaconess Medical Center,Inc. | Senior Data Analyst | Boston | MA |
| 188214 | I-200-26071-699123 | Certified | H-1B | TRUSTEES OF BOSTON UNIVERSITY | Senior Data Analyst | Boston | MA |
| 193259 | I-200-26076-710016 | Certified | H-1B | SCHNEIDER ELECTRIC USA, INC. | Senior Data Analyst | Boston | MA |
| 196991 | I-200-26077-712461 | Certified | H-1B | General Hospital Corporation | Senior Data Analyst | Boston | MA |
| 199932 | I-200-26079-718102 | Certified | H-1B | Boston Medical Center Corporation | Senior Quality Improvement Data Analyst | Boston | MA |
| 201994 | I-200-26082-721531 | Certified | H-1B | Grantham, Mayo, Van Otterloo & Co. LLC | Research Data Analyst | Boston | MA |
| 204978 | I-200-26083-727151 | Certified | H-1B | PUBLIC PARTNERSHIPS LLC | Sr. Data Analyst | Boston | MA |
| 224163 | I-200-26092-752707 | Certified | H-1B | General Hospital Corporation | Data Analyst, Senior | Boston | MA |

```sql
SELECT sheet_row, CASE_NUMBER, CASE_STATUS, VISA_CLASS, EMPLOYER_NAME, JOB_TITLE, WORKSITE_CITY, WORKSITE_STATE FROM lca WHERE CASE_STATUS = 'Certified' AND VISA_CLASS = 'H-1B' AND UPPER(TRIM(WORKSITE_STATE)) = 'MA' AND UPPER(TRIM(WORKSITE_CITY)) = 'BOSTON' AND title_has(JOB_TITLE, 'data analyst') = 1 ORDER BY sheet_row ASC
```

**SponsorSQL count-versus-rows check:** answer 40 matches 40 matching rows

An LCA filing is not a job offer, a visa approval, or a promise of sponsorship.

---
Approved by: interactive terminal user
Note: (none)
View SHA-256: 713713b8dbd417031d765c6560a04820f14b6b0b6c9532d30bca1459632c47e3
