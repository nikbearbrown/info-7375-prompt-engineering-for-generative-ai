# SOURCES

## Used 

| What | Where | How it's used |
|---|---|---|
| Greenhouse Job Board API (public, no auth) | `https://boards-api.greenhouse.io/v1/boards/{board}/jobs` (lists) and `…/jobs/{id}` (details) | the one allow-listed host. **The submitted watch uses one board, `samsara` (`config/boards.json`).** A 131-board list (`config/boards_all.json`) was tested as an extension. The experiment set comes from 7 saved boards (`experiments/source_raw/`). Earlier versions watched `samsara` (v2) and `klaviyo` (v1) |
| v1 persona Rohan Desai | The Reallocation Engine, `search/examples/rohan-desai/` | v1 only (files removed before submission) |
| Python 3.11 standard library | — | everything (urllib, json, re, html, unittest, subprocess) |
| Claude Code CLI v2.1.314 (headless `claude -p`) | Anthropic | runs the Claude judge, the sampling and experiment calls, and the action-surface trials. Model `claude-sonnet-5-5` |
| Course materials | INFO 7375 Chapters 1–3, assignment brief | structure of the contract, sampling, experiment, and action-surface work |

## What Claude (Claude Code, Opus 5.5, 2026-10-31 session) contributed



- **CONTRACT.md:** Contract was drafted based on the input given by Ethan
  (data engineer target, data analyst, Tableau and Power BI, US-only and relocation, Boston and 0–4 years preferred, an updated education and
  timeline for a ~4-year data engineer). Claude wrote the text at his direction. Each version was written before the code and runs it governs.
- **Persona Evan Gordon** (created as "Jordan Okafor", renamed by Ethan in v2.4): invented by Claude to match Ethan's target (data engineer, 2–5 years). Fictional employers,
  @example.com, 555 phone.
- **All code in `jsagent/`, `tests/`, `scripts/`, `experiments/*.py`:** written by Claude Code. Tests were written from the
  contract before the matching implementation.
- **Board list (v3):** Claude wrote 338 candidate company board names from memory and kept the 131 that answered (now `config/boards_all.json`, an optional extension). Claude also wrote
  the multi-board fetch, the per-board baseline, and their tests.
- **Market scan:** Claude scanned 49 Greenhouse boards for data engineering roles and extracted stated years of experience
  (scratch script, not part of the agent), which led to choosing Samsara.
- **Experiment set definition** (every data-titled posting on 7 boards, deduplicated) and the seeded split.
- **Drafts** of LABELING_RULE.md, ACTION_SURFACE.md (incl. the autonomy recommendation), the report templates, the README
  sign-off, and the driver's seat table. **The sign-off is not signed by Claude.**
- **Reference drafts** for the sampling conclusion, the prompt-experiment conclusion, and the action-surface choice (Ethan rewrote them in his own words),
  and the factual parts of the reports (results tables, verified posting quotes, limits).
- **The switch back to one board:** config, test, fresh runs, and doc updates.
- **Verification Claude did in the session:** found the 6,000-character truncation bug by checking its own "content shown"
  remark against the raw text, fixed it, added a regression test, and re-judged. Also spot-checked R5 extraction, checked
  that the wrong-version tests fail when the audit is sabotaged, and checked that the replay reproduces Run 2.

## What Ethan wrote / decided


- Switched the search target to data engineering roles asking for 2–5 years.
- Added data analyst roles to the search (2026-10-31, 17:22 ET; CONTRACT v2.1).
- Added Tableau and Power BI to the persona's skills (2026-10-31, 17:32 ET; CONTRACT v2.2).
- Clarified location: remote only in the US, will relocate, Boston preferred (2026-10-31, ~18:05 ET; CONTRACT v2.3).
- Confirmed relocation is within the US, renamed the persona Evan Gordon, and set 0–4 years as preferred, 5 acceptable, >5 invalid (2026-10-31, 18:26 ET; CONTRACT v2.4).
- Edited the final CONTRACT.md (~20:10–20:30 ET): simplified the header, added the fictional-résumé sample and the refusals for real résumés and
  for presenting Claude's judgment as fact, shortened the metro list to examples, dropped the known-weaknesses list, and dated the failure sentences.
- Decided to return to **one board** (Samsara) for the submission, to follow the brief's "one public job board", keeping the 131-board run as a described extension (2026-10-31, ~21:24 ET).
- Earlier decided to watch every known Greenhouse board instead of one company, knowing it departs from the brief's "one public job board" (2026-10-31, 19:20 ET; CONTRACT v3).
- Updated the persona's education and timeline, kept realistic for a ~4-year data engineer (MS Information Systems 2024–2026, BS Computer Engineering, ~4 years of experience). Fictional employers, no real contacts (2026-10-31, 18:45 ET; CONTRACT v2.5).
- Checked two fixture verdicts by hand (1004 relevant + preferred; 1003 fails R3) and ran the test suite.
- Ran `scripts/replay_runs.sh`. Its output exposed the overwritten-raw-file bug (the replay named Run 3's file as Run 2's).
- Wrote LABELING_RULE.md's final version (finalized 19:37 ET, before any label) and hand-labeled all 20 postings in two passes; after a self-check,
  decided to follow my own rule for 4 Staff/Lead postings and 1 intern.
- Chose the one v2 prompt change (the domain-experience sentence) from three candidates.
- Wrote the sampling conclusion, the prompt-experiment conclusion, and the action-surface choice myself, starting from Claude reference drafts.
- Reviewed, edited, and signed the README sign-off.
- Decided to remove the `archive/` folder before submission.
