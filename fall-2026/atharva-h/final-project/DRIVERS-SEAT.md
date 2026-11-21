# The driver's seat

What Claude did, what the owner did, and why that part stays the owner's. Dated facts only. If the owner disagrees with a row, the owner edits it, and the change shows in the commit history.

| Part | Claude (Claude Code, Opus 5.5) | Owner (Atharva Hambir) | Why this part stays the owner's |
|---|---|---|---|
| Choosing the project, the dataset, and the target role (Oct 2026) | Proposed six topics, and the DOL LCA dataset when asked for job-search data | Chose the topic and the latest DOL release; ran the ChatGPT test himself on 2026-10-24 and pasted the reply | The project has to answer a question the owner actually has |
| Decisions on 2026-11-21 (SQLite, success bar, no downloads, branch separate from JS3, four-minute film) | Proposed options and recorded them in `CLAUDE-HANDOFF-2026-11-21.md` | Gave the deadline, confirmed Claude Code access and the four-minute limit, approved the build | These are scope and risk decisions about the owner's own submission |
| Independent answer key (2026-11-21) | Wrote `build_answer_key.py`, `verify_boston_source.py`, `ANSWER-KEY.md` | Reported manually reviewing the key and the preparation files on 2026-11-21. **No independent hand recount from the workbook was reported.** | The definitions (what "certified", "Data Analyst" and "wage" mean) decide every score; Q4's wage meaning and Q6's BI wording still need an explicit owner choice |
| Pre-mortem and contract (`pre-mortem.md`, `CONTRACT.md`, `evals/PROMPT-CONTRACT-v1.md`) | Drafted them and committed before the code (`da6b416`) | Review pending | Predicting the failure and setting the rules is the supervising part of the work |
| Agent code and tests (`sponsorsql/`, `tests/`) | Wrote all code and the 28 tests (`ed4a2e1`) | Review pending. Must be able to explain any line (course AI policy). | The owner answers for the code at the gate and in front of a TA |
| Held-out set (`evals/heldout-questions.json`, `heldout-key.json`) | Wrote the five questions and the counting script; froze them before any proposal (`dfbbb73`) | Review pending | Choosing what counts as a fair held-out test is a judgment the owner signs |
| SQL proposals (`evals/proposals/`) | A separate Claude Code subagent wrote the SQL from the prompt file only, on 2026-11-21 | — | — |
| Running the evaluation, the failure cases and the controlled failure | Ran the commands and saved the raw outputs in `evidence/` and `evals/results/` | Review pending | — |
| Human gate decisions | None. Claude never approves at the gate. | **Not yet done:** an interactive approve, refuse or defer on the real data | Approval has to come from a person who saw the view |
| Stranger run | Ran a clean-checkout test from the committed files only (`STRANGER-RUN.md`, part B) | **Not yet done:** a person who didn't build it runs it (part A) | — |
| Sign-off, ship decision, Frictional log | Nothing written in the owner's voice | **Not yet done:** `SIGNOFF.md`, the decision in `transfer-reflection.md`, `FRICTIONAL.md` | The course grades these as the owner's own account |
| Film | Not started | — | Narration has to be the owner's |
