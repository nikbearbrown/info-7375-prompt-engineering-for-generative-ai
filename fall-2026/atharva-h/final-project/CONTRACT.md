# The gate: SponsorSQL contract and required tests

Written 2026-11-21 13:10 EST and committed **before** the agent code in `sponsorsql/`. Drafted by Claude in Claude Code at the owner's request; owner review is recorded in [SIGNOFF.md](SIGNOFF.md), not assumed here. The model-facing rules are in [evals/PROMPT-CONTRACT-v1.md](evals/PROMPT-CONTRACT-v1.md) (v1; the final version is [evals/PROMPT-CONTRACT-v2.md](evals/PROMPT-CONTRACT-v2.md)).

## What the system is for

SponsorSQL answers a plain-English question about the public U.S. Department of Labor FY2026 Q3 LCA disclosure file. It always returns three things together:
- the answer
- the SQL query that produced it
- the matching public rows

That way the person asking can check the number for themselves. Only a person at the gate can turn an answer into a saved report.

## What it must never do

1. **Never write to the data.** The database is opened read-only, and an SQLite authorizer denies every action except reading the `lca` table and calling allow-listed functions.
2. **Never run model text as code.** Model output is parsed as JSON. Only the `sql` and `rows_sql` strings are used, and only after the policy check. No Python `eval`, no shell.
3. **Never reveal contact data.** Employer contacts, attorneys, preparers, addresses, phones and emails are not loaded. Questions asking for them are refused before the model is called.
4. **Never predict or promise immigration outcomes.** It never says whether a named person will get a visa, whether a petition will be approved, or whether an employer will sponsor someone. An LCA is not a job offer, an approval or a hire.
5. **Never treat "the model said it's done" as a stop.** The loop stops only on:
   - a human decision (approve, refuse, defer)
   - a policy refusal
   - a clarification deferral
   - a spent budget
   - repeated policy denials
   - an error limit
6. **Never save or export an answer without a human approval** bound to the exact view the person saw. An approval for a different view counts as a deferral.

## Budgets

| Budget | Limit |
|---|---|
| Model proposals per question | 2 |
| Policy denials before stopping | 2 |
| Wall-clock time per SQL statement | 10 s (SQLite progress handler interrupts) |
| Rows returned for display | 200 (more are counted, not shown) |
| Total wall-clock time per question | 60 s |

## Tests that must pass before the system counts as working

All use Python's standard library and a small synthetic database built inside the test, so they run from a fresh clone without the 252 MB source file.

1. Non-`SELECT` SQL (`DELETE`, `UPDATE`, `INSERT`, `DROP`, `ATTACH`, `PRAGMA`) is denied before execution.
2. A second statement hidden after a semicolon is denied.
3. Reading any table other than `lca` (including `sqlite_master` and `metadata`) is denied by the authorizer at execution time.
4. A runaway query is interrupted by the time budget, and the loop stops with `budget_exhausted` or a recorded policy stop.
5. Questions asking for contact data or immigration predictions are refused before any model call.
6. An unparseable model reply is recorded and retried within the proposal budget, then the loop stops.
7. A clarification request from the model stops the loop as a deferral and runs no SQL.
8. The gate exports a report only for an approval whose view hash matches. A stale or mismatched approval becomes a deferral and writes nothing.
9. Every run writes a state file and a ledger line, including the stop reason.
10. The evaluator scores a known-wrong answer as a fail and a known-right answer as a pass.
11. For a count answer, a disagreement between the answer and the number of matching rows is flagged.

## Evaluation that can say no

- **Development set:** the ten questions in `evals/ANSWER-KEY.md`, frozen 2026-11-21 before any model SQL was run against them.
- **Held-out set:** five questions frozen in `evals/heldout-questions.json` with their answer key **before** any model proposal for them exists. Scored once, with the final contract.
- **Deliberate failure cases:** at least five, run by `python3 -m sponsorsql failures`.
- **Ship bar:** at least 8/10 on development, at least 4/5 on held-out, and zero unsafe SQL executed. Anything less means narrow or defer.
