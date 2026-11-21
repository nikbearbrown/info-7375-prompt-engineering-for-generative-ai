# Pre-mortem — written 2026-11-21 13:07 EST, before any agent code existed

Packet document 6 of 10. Previous: [gates.md](gates.md) · Next: [evidence.md](evidence.md)

This file was written and committed before `sponsorsql/` (the agent) was implemented. It is kept unedited after that point, so it can be compared with what actually happened. Drafted by Claude in Claude Code at the owner's request; see [SOURCES.md](SOURCES.md).

## The failure I predict

**SQL that runs, looks right, and returns the wrong number.**

When the model writes SQL for a job-title question such as "How many certified H-1B Data Analyst cases are in Boston?", it will match titles with a plain substring test such as `JOB_TITLE LIKE '%data analyst%'`. This is what the October draft SQL did. That test:

- **counts near matches it shouldn't:** titles like `Metadata Analyst` contain the letters "data analyst"; `Data Analysts` contains them too.
- **misses titles it should count:** `Data-Analyst` and `Data  Analyst` (two spaces) don't contain the exact substring.

The query raises no error. A person reading it would probably accept it. The count will still disagree with the independent answer key on every title-based question where those variants occur.

Two more predicted failures of the same kind ("runs fine, wrong number"):

1. **Employer spellings split one company.** Grouping by `EMPLOYER_NAME` treats `Amazon Data Services, Inc` and `Amazon Data Services, Inc.` as different employers. An exact-name filter on one spelling finds 315 of that employer's 1,203 rows.
2. **Mixed wage units.** A wage question will be answered by mixing yearly and hourly figures, or by converting hourly pay using an assumed 2,080-hour year, unless the rule is stated.

## How I will trigger it on purpose

- Run the agent on the ten development questions with the **first** version of the prompt contract (`evals/PROMPT-CONTRACT.md`, v1), which does not give the model any title-matching helper. Then run the October draft question-5 query through the same executor with a scripted adapter.

## The independent check that should catch it

- The **answer key** (`evals/answer-key-results.json`). It was computed by a separate Python script that never reads model SQL, and its Boston count was confirmed by a second, direct scan of the workbook that doesn't use SQLite.
- The comparison is done by `sponsorsql/evaluate.py`, not by the model.

## The recovery I plan, and who reviews it

- A second contract version that gives the model a deterministic `title_has(title, phrase)` SQL function and states the wage and employer rules explicitly. Then re-run the development set.
- The held-out set is frozen before either run and is scored once, with the final contract only.
- **Review:** the owner (Atharva Hambir) reviews the contract change and the before/after results before the recovery counts as accepted. Until then it is marked *awaiting owner review*.

## What would make me wrong

If version 1 already scores at least 8/10 on the development set and never uses a substring title test, this prediction failed, and the audit note says so.
