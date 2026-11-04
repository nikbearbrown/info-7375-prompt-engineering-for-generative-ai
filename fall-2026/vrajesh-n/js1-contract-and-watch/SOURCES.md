# SOURCES — JS1

## What I used
- Ashby public posting API: `https://api.ashbyhq.com/posting-api/job-board/commure` (read-only, no login).
- Fictional persona: `data/resume/rohan-desai.example.json`, from the Reallocation Engine examples. I added `work_authorization.needs_sponsorship: true` on 2026-10-31 (CONTRACT.md R4).
- Python 3.13 standard library; Claude Code CLI 2.1.314 (`claude -p`, model claude-sonnet-5-5); claude.ai chat (action-surface arm 1).
- My own earlier work: `data/raw/probe.py` and the 10-14 and 10-23 snapshots from my pitch film (`final-project-film/evidence/`).

## What I wrote (Vrajesh)
- The CONTRACT.md words dated 2026-10-24, and every *(chosen 10-31)* decision (picked from options Claude listed).
- The first TEST-EXPECTATIONS.md line, and the decisions the rows encode.
- All 20 hand labels in `experiments/labels.csv`, including the change to #8.
- The choice of the one prompt change.
- The claude.ai chat-paste run (arm 1) and its answer.
- FRICTIONAL.md, in my own words.
- My edits to, and the signature on, the README sign-off.

## What Claude (Claude Code, Opus 5.5, 2026-10-31 session) contributed
- Turned my OPEN contract items into multiple-choice questions, wrote the chosen options into CONTRACT.md and filled the TEST-EXPECTATIONS.md rows from them.
- Wrote all code: `earlybird/`, `tests/`, `experiments/*.py`, `experiments/prompts/baseline.txt` (my 10-24 words plus the JSON format) and `revision.txt` (my chosen sentence).
- Ran the watch runs, the sampling, the prompt experiment and action-surface arms 2 and 3.
- Found and fixed a crash (a non-JSON resume file was not refused).
- Noticed that the first random label draw had no plausible-relevant posting, and redrew it stratified before I labeled.
- Drafted SAMPLING-REPORT.md, PROMPT-EXPERIMENT.md, ACTION-SURFACE.md, README.md (including the sign-off draft and driver's-seat table) and this file.

The claude-sonnet-5-5 answers in `reports/` and `experiments/results/` are Claude's judgments, kept verbatim with dates and session ids.
