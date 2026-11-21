# Brief

Packet document 1 of 10. Next: [data-boundary.md](data-boundary.md) · All documents: [README.md](README.md)

## The need

International students looking for data jobs in the U.S. want to know which employers have filed H-1B paperwork for the kind of role they want, where, and at what filed wage. That information is public: the U.S. Department of Labor (DOL) publishes every **Labor Condition Application (LCA)**, the form an employer files before hiring someone on an H-1B. But the latest file is a 252 MB spreadsheet with 98 columns and 437,496 filled rows, plus 595,239 blank rows. Most students can't query it, and a chatbot's single number can't be checked.

**SponsorSQL** answers a plain-English question about that file, and always shows three things together:
- the answer
- the SQL query that produced it
- the matching public rows

That way the person asking can see how the number was produced, and check it for themselves.

## Who owns it, who is affected

- **Owner:** Atharva Hambir (INFO 7375, Fall 2026). The owner decides what the agent may do, freezes the evaluation, and is the person at the gate.
- **Affected:**
  - students who ask questions
  - employers whose public filings are counted and named
  - reviewers who rely on the evaluation

  [data-boundary.md](data-boundary.md) says how each could contest a result.

## What success looks like

Set before evaluation ([CONTRACT.md](CONTRACT.md), [evals/FREEZE.md](evals/FREEZE.md)):
- at least **8/10** on the development questions
- at least **4/5** on the held-out questions, scored once
- **zero** unsafe SQL executed
- every answer shown with its SQL and matching rows

Anything less means narrow or defer. The actual result and the decision are in [evidence.md](evidence.md) and [transfer-reflection.md](transfer-reflection.md).

## What it is not for

- Not a visa, immigration or legal tool. An LCA filing is not a job opening, a job offer, a visa approval, or a promise to sponsor anyone.
- Not a prediction tool. It doesn't estimate anyone's chances.
- Not a source of contact details. Contact, attorney and preparer data are never loaded.
- Not a general text-to-SQL product. It covers one table, one fiscal-year release, and questions answerable from 18 public fields.

## What would make it inappropriate

- Using an answer as proof that a specific employer will sponsor a specific person.
- Answering from a different or newer DOL file without re-checking the checksum and re-freezing the evaluation. The DOL says Q3 records can still change.
- Removing the human gate, or exporting answers without the matching rows.
- Questions about individual workers, or anything needing data beyond the public file.

## What changed since the October pitch

The pitch planned DuckDB, a hand-checked answer key, and "verified answers". What exists now:
- **SQLite instead of DuckDB:** DuckDB wasn't installed, and no new packages were downloaded.
- **An independent, automated answer key** instead of a hand count. The owner reviewed the files on 2026-11-21 but didn't recount the rows by hand.
- **A narrower claim:** "the answer plus its SQL and rows, so you can check it."
- **A working agent loop** with a coded permission policy and a human gate, which the pitch didn't have.
