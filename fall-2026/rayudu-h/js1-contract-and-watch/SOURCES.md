# SOURCES.md

## What I used

- **The assignment:** INFO 7375 "Job-Search Agent 1 — The Contract and the Watch", from the course repo, `assignments/assignment-js1-the-contract-and-the-watch.md`.
- **Anthropic's public job board:** Greenhouse Job Board API, `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true`. It's read-only, needs no login, and was fetched a handful of times on Oct 31, 2026. The posting text belongs to Anthropic; it's kept here only as raw evidence for the runs.
- **The persona résumé:** **Priya Nair**, a fictional example persona, from The Reallocation Engine, `search/examples/priya-nair/resume.example.json` (https://github.com/nikbearbrown/the-reallocation-engine). It was copied unchanged to `persona/priya-nair.resume.json`.
- **Claude Code** 2.1.316, model `claude-sonnet-5-5`. All judge, sampling, experiment and action-surface calls went through it.
- **Python** 3.9.10 and **pytest** 8.3.3.

## What I wrote

- **The decisions in `CONTRACT.md`:** the board, persona, rule, edge cases, extra refusals, the choice of wrong versions and the failure sentence. I gave them as answers to Claude's questions, and Claude wrote them in. The authorship note at the top of the contract says so.
- **The hand-worked example** in the contract, which led me to add the management test.
- **All 20 hand labels** in `experiment/labels.csv`. For the 10 held-out labels I used the skill-evidence sheet that Claude's script produced.
- **The decision** to stay with one board, and the least-autonomy choice in `ACTION-SURFACE.md`. Hemanth confirmed both.

## What Claude contributed (Claude Code, Opus 5.5, Oct 31, 2026)

- **The contract:** the boilerplate, the question sequence, and the fact checks behind each option (field names, how many postings each option would pass).
- **All code** in `jsagent/`, `scripts/` and `tests/`, written against the contract. That includes the wrong-version implementations the tests catch.
- **Running everything:** the live and seeded runs, the 20 sampling calls, the 40 experiment calls and the three action-surface runs.
- **Drafts:** `README.md`, `SAMPLING-REPORT.md`, `PROMPT-EXPERIMENT.md`, `ACTION-SURFACE.md`, this file and `FRICTIONAL.md`. Every number in them comes from saved files, and `scripts/analyze.py` recomputes them.
- **Two corrections to my own work:**
  - On #8, the skills I listed (Azure, Go, Rust, Kubernetes) aren't on Priya's list. Only Python counts.
  - On #2, "AWS" appears only inside "Laws".

Claude's verdicts on postings appear in the reports as **judgments, with the date and model**. They're never facts.
