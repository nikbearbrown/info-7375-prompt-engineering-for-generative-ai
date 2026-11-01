# SOURCES — what I used, what I wrote, what Claude contributed

| Item | Source | Who |
|---|---|---|
| Assignment text | `assignments/assignment-js1-the-contract-and-the-watch.md` in the course repo | Instructor |
| Shape of the watch (baseline, seen-id state, raw saved, record vs judgment) | Professor Bear's `fall-2026/nik-bear-brown/greenhouse-watch-demo/` and the Reallocation Engine `greenhouse-watch` skill (`015843d`). They were read as reference; **no code was copied**. | Instructor |
| `persona/aarav-patel.example.json` | Copied unchanged from the-reallocation-engine `search/examples/aarav-patel/resume.example.json` (last changed in `d08afdd`). Fictional: `@example.com` addresses, 555 phone numbers. | Course repo |
| Klaviyo postings | Public Greenhouse endpoint `boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | Klaviyo |
| Contract decisions (board, persona, rule clauses A/B/C, the two wrong versions) | Chosen in chat on 2026-10-25 from options Claude Code offered | **Omkar** chose; Claude wrote the options and typed the choices |
| Contract interpretation details (whole-word matching, how to read "US remote", several locations, HTML cleaning) | CONTRACT.md "Details his choices did not settle" | **Claude** proposed; **Omkar** confirmed ("nothing" to change 10-26 01:51; "confirm" on the DE detail 10-26 16:39) |
| `jsagent/` (fetch, persona, rule, claude_judge, watch) | written 2026-10-25 | **Claude Code** (Opus 5.5) |
| `tests/test_rule.py`, `test_watch.py`, `test_refusals.py`, fixtures, mutants, `run_mutants.py` | written 2026-10-25. The fixtures are **constructed**, not real postings. | **Claude Code** |
| `tests/omkar_hand_cases.csv` rows | hand-computed verdicts on real postings (jobs 2, 14, 16; skills counted with his own `grep`, 2026-10-30) | **Omkar** |
| `prompts/baseline.txt` | prompt contract draft | **Claude Code** |
| `prompts/revision.txt` (the one change) | baseline + a block restating `LABELING-RULE.md` | **Omkar** chose the change (2026-10-27); Claude wrote the block |
| Experiment runners (`experiments/`) | written 2026-10-25 | **Claude Code** |
| Labeling rule and 20 hand labels (the 5 sampling postings are among them) | `experiments/prompt/LABELING-RULE.md`, `labels.csv` | **Omkar**: the rule from options Claude offered (2026-10-26); each label clicked by him in chat (2026-10-27) |
| Action-surface analysis table | `action-surface/ACTION-SURFACE.md` | Claude ran the three ways and drafted the table; **Omkar** made the choice (2026-10-30 20:06 UTC, his words) |
| Sign-off (Checked / How / Not checked / Not claiming), FRICTIONAL Part 1 | README, FRICTIONAL.md | **Omkar** picked or typed each line (2026-10-27, 2026-10-30); the "Not checked" list he picked from was written by Claude |
| Signature | README | **Omkar** ("Sign - Omkar Salian", typed in chat 2026-10-30 23:54 ET) |
| "Why" column of the driver's seat | README | **Omkar**: contract and autonomy rows reuse lines he typed earlier (his choice, 2026-10-31); tests row typed by him 2026-10-31 22:35 UTC; labels row not filled |
| Judge model | Claude via `claude -p` (Claude Code CLI 2.1.292, `--model sonnet`; each run records the exact model id it reports) | Anthropic |
| Sampling report, prompt-experiment report (tables + "what it shows" drafts) | `experiments/sampling/SAMPLING-REPORT.md`, `experiments/prompt/PROMPT-EXPERIMENT.md` | **Claude Code** drafted from the run files |
