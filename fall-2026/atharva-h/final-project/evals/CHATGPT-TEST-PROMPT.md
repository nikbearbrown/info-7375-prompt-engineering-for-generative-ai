# ChatGPT test — one question against the FY2026 Q3 record layout

## Steps
1. Download the record layout PDF (it's small) from the DOL page:
   https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/FY26Q3/LCA_Record_Layout_FY2026_Q3.pdf
2. Open a **new** ChatGPT chat, attach that PDF, and paste the prompt below exactly as written.
3. Copy ChatGPT's **whole reply** and send it back to me, together with:
   - today's date
   - the model name ChatGPT shows (for example, the one in the model picker)

Don't edit or re-ask. The first reply is the test.

## Prompt to paste

```
I have a DuckDB table named lca, loaded from the U.S. Department of Labor file
LCA_Disclosure_Data_FY2026_Q3.xlsx. Its record layout is attached.

Write one SQL query that answers this question:
How many certified H-1B cases in this file are for Data Analyst jobs with a
worksite in Boston, Massachusetts?

Then list every assumption your query makes.
```

## Why this question
It's an ordinary analyst question, but it has several traps built into the data. Whatever ChatGPT does with them is the concrete difference to point to. I won't compute the answer myself, so the hand-checked number stays yours.
