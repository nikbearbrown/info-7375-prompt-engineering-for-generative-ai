# CLAUDE.md — Job-Search Agent 2 (Pavan Majji, INFO7375)

## What this is
Assignment brief: ASSIGNMENT.md in this folder. This builds on my JS1 agent in
../js1-contract-and-watch/ (Python 3.14, httpx; Glean on Greenhouse; fictional persona
Alex Morgan; rule verdict = "record", Claude verdict = "judgment"). Read its CONTRACT.md,
README.md and FRICTIONAL.md for context.

## Hard rules
- Never modify anything in ../js1-contract-and-watch/ (submitted and awaiting grading).
- Do not write or edit GATE.md. I write it. You may review it and suggest changes.
- Do not write code until I say GATE.md is committed.
- I write the tests' asserts before implementation. Never modify files in tests/. If a
  test looks wrong, stop and tell me.
- Make no network requests unless I ask, and only to hosts I have approved.
- Only write inside this folder. Never run git commit or git push; I do that.
- No real résumé, ever. Persona files use @example.com and 555 phone numbers.
- Label anything seeded, simulated, or constructed, in file names and in reports.

## How I work
- Python venv in .venv; run tests with `python -m pytest -v`.
- I log decisions and mistakes in FRICTIONAL.md. When you make a choice my instructions
  didn't cover, list it clearly at the end of your reply so I can accept or reject it.
- When you finish a task, tell me the exact commands to verify it myself.