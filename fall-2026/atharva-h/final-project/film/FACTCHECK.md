# FACTCHECK — atharva-sponsorsql-final

Every number or factual claim on screen or in the narration, with its source in the project folder `fall-2026/atharva-h/final-project/` (branch `atharva-h/final-project`, commit `c314f474`).

| # | Claim | Beat | Source |
|---|---|---|---|
| F1 | The DOL disclosure file has 437,496 filings; 595,239 blank sheet rows (1,032,735 sheet rows after the header) | B00, B03 | `evals/profile-FY2026-Q3.json`; `evidence/load.log` |
| F2 | The workbook is 252 MB, SHA-256 starting f8ca8448, and the loader checks it | B03 | `sponsorsql/config.py`; `sponsorsql/load.py`; `evidence/load.log` |
| F3 | 18 of 98 columns are loaded; contact, attorney and preparer fields are never loaded | B03 | `sponsorsql/config.py` (`FIELDS`); header row (98 columns) in `evals/FREEZE.md` and FACTCHECK of the pitch |
| F4 | An H-1B is a U.S. work visa for specialty (skilled) jobs; an LCA is the employer's filing with DOL before hiring on an H-1B; an LCA is not a visa approval | B00, B03 | DOL record layout; project brief (`brief.md`) |
| F5 | MyVisaJobs search fields (company, title, city, state); H-1B salary explorer filters (employer, title, worksite, fiscal year, status) | B02 | Earlier session's review on 2026-11-21 (`final-project-film/APPENDIX.md`, section 2); not re-checked for the film |
| F6 | ChatGPT wrote a query and, on follow-up, said 40; nothing checked it | B02 | `evals/chatgpt-test-2026-10-24.md` |
| F7 | The loop: observe, decide, act, record, stop; budget 2 proposals, 10 s per statement | B04 | `sponsorsql/agent.py`, `sponsorsql/config.py`, `sponsorsql/state.py` |
| F8 | Read-only database; SQLite rule allows reading only table lca | B05 | `sponsorsql/policy.py` |
| F9 | F1/F2/F3 output lines and rows before/after 437,496 | B05 | `evidence/rescore-after-review.log`; `evals/results/failures-after-review.json` |
| F10 | Boston run: answer 40, SQL, three of the 40 matching rows, view SHA-256 713713b8…9632c47e3 | B06 | `evidence/gate-view-D2-2026-11-23.txt` (real run, 2026-11-23, recorded Claude reply) |
| F11 | Gate prompt text "Approve, refuse, or defer this answer? [a/r/d]:" | B06 | `sponsorsql/gate.py` (`decide`, interactive mode). No owner decision is shown or claimed. |
| F12 | Python standard library + SQLite, nothing installed; Claude Code account; no API key or paid credits; loads in about 70 s | B07 | `artifact.md`; `evidence/load.log` (1:10 total) |
| F13 | The Claude CLI said "Not logged in"; the tested SQL came from separate Claude sessions, saved word for word, replayed | B07 | `artifact.md`; `evals/proposals/*-responses.json` provenance |
| F14 | 10 development and 5 held-out questions locked before any test; keys counted by separate code from the data (the SQLite database the loader builds from the checksum-verified workbook) | B08 | `evals/FREEZE.md` (commit `dfbbb73` before `b65b725`); `evals/build_answer_key.py`, `evals/build_heldout_key.py` |
| F15 | Bar: at least 8/10, at least 4/5, 0 unsafe queries | B08 | `CONTRACT.md` |
| F16 | 4/10 (loose title match; "Metadata Analyst" counted), 9/10 (the miss: a few source titles end in tabs or non-breaking spaces; the key strips them and the query's `TRIM()` doesn't, so four counts are off by one or two), held-out 5/5 run once | B09 | `evals/FAILURE-LOG.md`; `evals/results/*-rescored-after-review.json` |
| F17 | Ten deliberate failures stopped as predicted; the title bug triggered on purpose was caught by the key | B10 | `evals/results/failures-after-review.json` |
| F18 | An independent reviewer found 18 findings; code fixed where it could be; three limits remain | B11 | `audit-note.md`; `evidence/independent-review-2026-11-21.md` |
| F19 | Ship / narrow / defer is the owner's sign-off, still open | B11 | `SIGNOFF.md` (not signed), `transfer-reflection.md` |
| F20 | Permission policy: a list, in code, of what the tool may do (read one table); anything else is blocked before it runs | B05 | `sponsorsql/policy.py` (`authorizer`, `check_text`, `open_readonly`) |
| F21 | "The final version of Claude's instructions was tested before I reviewed it" | B11 | `gates.md`; `evals/PROMPT-CONTRACT-v2.md` (scored before owner review) |
| F22 | "I've reviewed it since" | B11 | **The owner's own statement, given in chat on 2026-11-23 when choosing this wording. Not yet recorded in the project's documents; the owner records it.** |
| F23 | Credit: "Written by Atharva Hambir with Claude" (wording chosen by the owner, 2026-11-23). The synthetic voice is disclosed in the project's `film/README.md`, not in the narration | B12 | owner's instruction, 2026-11-23 |
