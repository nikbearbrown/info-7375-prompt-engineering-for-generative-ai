# Finished-wrong-answer demonstration

**This run is CONSTRUCTED.** One input file was made by me from a real capture; the other two inputs are real captures.

## Setup
- `evidence/CONSTRUCTED_2026-11-09_greenhouse_gleanwork_EMPTY.json`: my real Nov 9 Glean capture (123 postings) with `jobs` set to `[]` and `meta.total` set to 0, imitating a board that suddenly returns an empty list.
- `config/demo_boards.json`: three boards, all replayed from saved files, no network. Glean uses the CONSTRUCTED empty file; Palantir and OpenAI use my real Nov 9 captures. The deliberate bad board is left out, so the run can end `finished` (GATE.md §5).

## The loop's own report: clean, and wrong
`python -m agent.loop --config config/demo_boards.json` → status **finished**, agent exit code **0** (evidence/demo_finished_wrong/1_loop_output.txt; run folder out/runs/2026-11-10T131828/).
The loop reported Glean as `ok` with 0 postings and no new jobs. That's wrong: Glean had 123 postings on Nov 9 and 125 on Nov 10 (run 2). This is the weakness GATE.md §5 accepts on purpose: the loop takes an empty list at face value.

## The independent check: catches it
`python check_run.py out/runs/2026-11-10T131828` → **1 problem**, checker exit code **1** (evidence/demo_finished_wrong/2_checker_output.txt):
> greenhouse:gleanwork: SUSPICIOUS empty board: raw response raw/greenhouse_gleanwork.json has 0 postings, but the loop marked the board ok (run status: finished)

Why it's independent: check_run.py is a separate program. It uses summary.json only to find which raw file belongs to which board, then counts the postings itself from the saved raw response. It doesn't trust the loop's count or status.

## The checker doesn't flag healthy runs
`python check_run.py out/runs/2026-11-10T131257` (real run 2) → **0 problems**, exit code **0** (evidence/demo_finished_wrong/3_checker_on_real_run2.txt).

## Limits
- The checker flags *any* empty board. A board that is genuinely empty would also be flagged, so a flag means "look at this," not "this is wrong."
- It doesn't compare against earlier runs, so a board that silently drops from 125 to 3 postings would not be flagged.