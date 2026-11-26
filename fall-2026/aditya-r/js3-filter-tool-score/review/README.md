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

---

# Second batch: fresh held-out set H2 (FILTER.md amendment A3)

- **What to fill in:** `review/LABEL_SHEET_H2.csv`. It has 24 rows, H01–H24. The full text of each row is in `review/postings_h2/Hxx.md`. The question and the `label`/`reason` columns are the same as in the first batch.
- **Edit the CSV file directly** and save it in place (CSV UTF-8). **Please don't send screenshots or paste the labels into the chat.** Claude must not see these labels until the filter revision is frozen.
- **Stay blind:** the same rule applies as before. Don't open `runs/`, `splits/`, `corpus/`, `shortlist/` or `FILTER.md` while labeling.
- **How to resume:** tell Claude *"H2 labels saved"*. Claude will run `js3.labels seal-h2`. That checks that every row has `yes`, `no` or `unsure`, and records the file's sha256. It prints only row problems: no labels and no counts.

---

# Third batch: fresh blind audit A4 (FILTER.md amendment A4; separate from H2)

- **What to fill in:** `review/LABEL_SHEET_A4.csv`. It has 37 rows, A01–A37, and none of them was on your earlier sheets. The full text of each row is in `review/postings_a4/Axx.md`.
- **Columns:** `verdict` (`yes` = worth Priya's time, `no`, or `unsure`) and `reason`. Use your own judgment, as before. Edit the file directly and save it as CSV UTF-8.
- **Stay blind:** as before, don't open `runs/`, `splits/`, `audit/`, `shortlist/` or `FILTER.md` while labeling.
- **How to resume:** tell Claude *"A4 labels saved"*. Claude will run `js3.labels import-a4` (validate and seal) and then `js3.audit a4`. That gives the errors by group, the interval for the 30 random rejects, and any new false friend.
