# Assisted sign-off checks — 2026-11-23 (America/New_York)

These checks were performed in an AI-assisted session. They are evidence for the owner's review, **not** a claim that Atharva personally ran each command or made a human gate decision.

## Documents and tests

- Read `CONTRACT.md`, `pre-mortem.md`, `evals/PROMPT-CONTRACT-v1.md`, `evals/PROMPT-CONTRACT-v2.md`, `SIGNOFF.md`, and `transfer-reflection.md`. No changes were made to the contract or pre-mortem.
- Ran `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -t .` from the final-project folder: **43 tests passed** in 0.715 s.
- Attempted the course validator command `python3 scripts/validate_course.py` from the worktree root. The command could not run because `scripts/validate_course.py` is absent from this checkout; a file search found no copy in the local INFO-7375 tree. This is a validation gap, not a failed project test.
- Technical review of v2: it adds whole-phrase title matching, explicit wage and title-class rules, trimmed group labels, and a faster ranking evidence query. The saved development score is 9/10 and held-out is 5/5. It is not ready for final owner acceptance without addressing D8's Unicode whitespace, H3's false `MISMATCH` for a median (`answer_type: count`), and the absent `value` and refusal types. The held-out set was scored before owner review of v2.

## Interactive gate attempts

- The checklist's positional command failed at argument parsing (exit 2): this CLI requires `--question`; a live call also needs `--adapter claude-cli`.
- Corrected live attempt: `python3 -m sponsorsql ask --db data/fy2026q3.sqlite --adapter claude-cli --gate interactive --question 'How many certified H-1B Data Analyst cases have a recorded worksite in Boston, MA?'`. The shell had no `claude` command. Run `20261124T024108Z-454e7c` stopped `budget_exhausted` with `model_unavailable`, no answer view and no approval prompt; the shell process still exited 0, so its status must be read from the saved run. The local date was 2026-11-23; the run ID uses UTC. Raw state: [live-cli-unavailable-2026-11-23.json](live-cli-unavailable-2026-11-23.json).
- A **recorded-reply replay** on the real database reached the interactive gate. It showed answer 40, SQL, 40 matching rows, and view SHA-256 `713713b8dbd417031d765c6560a04820f14b6b0b6c9532d30bca1459632c47e3`. The assistant entered `d` and the note `Recorded reply replay; live Claude CLI unavailable. Deferred for owner review.` Run `20261124T024133Z-f17861` stopped `deferred_by_human` and wrote no report. That stop label is the program's wording; the input was **not** Atharva's personal approval, refusal, or deferral. Raw state: [replayed-gate-defer-2026-11-23.json](replayed-gate-defer-2026-11-23.json).

## Result and source checks

- Re-executed D2's saved answer SQL and `rows_sql` against `data/fy2026q3.sqlite` opened read-only. Both returned 40, and all 40 `CASE_NUMBER` values matched the independent answer key's Boston list. The first inspected rows were sheet rows 8272 and 24187, both `Certified`, `H-1B`, Boston, MA, with Data Analyst phrase titles.
- Re-executed H1's saved answer SQL and `rows_sql` against the same database. The answer was 564 and the evidence query returned 564 matching rows. The first two inspected rows had Texas worksites and Business Analyst phrase titles. This checks two saved results against their matching rows, not all 15 questions.
- Opened the original FY2026 Q3 workbook in Microsoft Excel, entered a temporary formula in blank cell `CU1`, and observed **40**: `=COUNTIFS(B:B,"Certified",F:F,"H-1B",G:G,"*Data Analyst*",BR:BR,"Boston",BT:BT,"MA")`. The `*Data Analyst*` substring is narrower than the project's `title_has()` rule for some titles, so this independently corroborates **only this Boston answer**. Closed Excel with **Don't Save**. The original workbook SHA-256 remained `f8ca8448a528671f784d3692923775a13741c99caec2816b2fe30c8885bd28b3`.

## Owner's personal recheck (same evening)

After this assisted pass, Atharva repeated the checks personally on 2026-11-23 (owner's statement): the test suite (43 tests passed), D2 and H1 against their matching rows, and the Boston `COUNTIFS` formula in Excel (40). Atharva also reviewed `evals/PROMPT-CONTRACT-v2.md` personally. Those personal checks are ticked in [../SIGNOFF.md](../SIGNOFF.md). The run IDs, timings and commands above belong to the assisted pass.

## What this does not establish (assisted pass)

No live Claude CLI call reached a gate. No owner decision was entered. The Excel formula was entered in the assisted session rather than by Atharva. No personal recount of all ten development answers, acceptance of contract v2, new held-out score, or stranger run is established by these checks.
