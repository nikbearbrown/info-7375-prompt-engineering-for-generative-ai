# Labeling batch: instructions for Aditya

**What to fill in:** `review/LABEL_SHEET.csv`. It has 63 rows, and each row is one real posting from the corpus.

**The question for each row:** acting for **Priya Nair**, is this posting **worth her time to read in full**?
- Priya is the fictional persona in `resume/priya-nair.resume.example.json`.
- She finished an MS in Information Systems in December 2025 and did one 8-month AI Engineer co-op.
- Her co-op covered an LLM agent, Databricks, LangGraph, MLflow and LLM evaluation.
- She knows Python and SQL, and she lives in Boston.

Use **your own judgment**, not the FILTER.md rules. If location, level or anything else drives your answer, say so in the reason.

| Column | Write |
|---|---|
| `label` | `yes` (worth her time), `no`, or `unsure` |
| `reason` | A few words, for example "senior: 8+ yrs", "sales role", "good fit but Berlin only" |

- **Full text:** each row's `full_text` column names a file in `review/postings/` (for example `review/postings/S01.md`). It holds the title, location, department, URL and the complete description as captured.
- **Stay blind:** please **don't open** `runs/`, `splits/`, `corpus/` or `FILTER.md` while labeling, and don't run the code. They show scores, verdicts and which rows belong to which sampling group. The sheet and the posting files show none of these.
- **Editing:** edit only the `label` and `reason` columns. Keep the row order and the other columns. In Excel or Numbers, save as **CSV UTF-8**.
- **Order:** the rows are in a shuffled order (seed 7377). Some are obvious from the title, and that's fine.

**How to resume:** save the file in place and tell Claude in this same session: *"labels done"*. Claude will then:
1. validate the sheet (`js3.labels import`);
2. seal it by recording its sha256;
3. open **only** the dev rows for the audit.

The held-out rows stay unread until the revisions are frozen.
