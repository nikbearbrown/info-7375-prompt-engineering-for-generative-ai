# Fact check: every claim in the narration
Checked 2026-11-23 against my GitHub folders and the sources named. **Verdicts:**
- **REAL:** it ran, and the evidence is in my folder.
- **SOURCED:** stated by the named source.
- **PLANNED:** said with "will".
- **ILLUSTRATION:** labelled on screen.

| Beat | Claim | Verdict | Evidence / source |
|---|---|---|---|
| B02 | Only 6 of Klaviyo's 156 postings had an analyst title | REAL | JS1 `runs/2026-10-31T173836-live-raw.json` (156 postings); JS1 FRICTIONAL ~5:39 pm (6 analyst/analytics titles) |
| B03 | The example short list | ILLUSTRATION | Labelled on screen. Row 2's quote ("3-5 years of experience in compensation") is from the real posting 7989990003; rows 1 and 3 are examples |
| B04 | LinkedIn lets you set job alerts | SOURCED | LinkedIn Help, "Job alerts on LinkedIn", https://www.linkedin.com/help/linkedin/answer/a511279 (the page title; the body couldn't be fetched automatically, so no further claim is made) |
| B05 | ChatGPT, 2026-10-13: a good summary, no source lines, an added location detail | REAL | `evidence/chatgpt-pasted-2026-10-13.png` (from my October pitch) |
| B05 | Claude, 2026-10-31: "Mostly not relevant", hedged prose | REAL | `evidence/claude-way1-2026-10-31.png` (JS1 `reports/action-surfaces/way1-ANISHA-screenshot.png`) |
| B06 | Lectern collects from 18 boards across three applicant-tracking systems | SOURCED | The JS2 assignment text: "the instructor's collector, Lectern …, which reads 18 boards across three applicant-tracking systems" |
| B06 | The Reallocation Engine has a role scorer | SOURCED | The JS3 assignment text: "the Reallocation Engine (its role scorer and recipes)" |
| B08 | The Greenhouse and Lever public APIs need no account or login | REAL | JS2 live runs with no credentials (`logs/10`, `logs/12`); allow-list in JS2 `watcher/policy.py` |
| B08 | The persona is fictional (Nadia Okafor) | REAL | JS1 `persona/resume.json` (`@example.com`, 555 phone); JS2 `load_resume` refuses anything else |
| B09 | Layer 1: contract committed before any run; two judges; the validator rejects quotes not in the posting | REAL | JS1 commit `509e6ca`; JS1 `agent.py` `validate()`; JS1 tests. (The contract was drafted together with the code, so the film says "before any run", not "before any code".) |
| B09 | Layer 2: 3 boards, 2 systems, budgets 5/15/60, permission policy in code | REAL | JS2 GATE.md, `watcher/loop.py` `Budget`, `watcher/policy.py`, `logs/10` |
| B10 | Layer 3 and the final project | PLANNED | JS3 assignment; spoken with "will" |
| B11 | No accounts needed; only two public APIs; my laptop + Python; my own Claude account for the Claude steps | REAL | JS2 live runs with no credentials, `watcher/policy.py` allow-list; JS1/JS2 READMEs (Python 3 standard library) |
| B12 | 20 labels (10 dev / 10 held-out); 10/10 and 9/10 with my rule in the prompt; 19 of 20 "not relevant" | REAL | JS1 `labels/labels.csv`, `reports/first-run-1800-verdicts-only/EXPERIMENT-*.md` (the 6:00 pm run; the 6:17 pm rerun matched on the revised prompt) |
| B13 | 18 of 18 boundary predictions matched | REAL | JS2 PERMISSIONS.md; `logs/23` |
| B13 | Two wrong versions ended "finished", and the independent check caught both | REAL | JS2 `logs/14`–`17`, TRACE.md §2 |
| B14 | My pass mark | PLANNED | My decision, 2026-11-23 (APPENDIX.md) |
| B15 | Layers 1–2 exist and ran; the rest will exist | REAL / PLANNED | My JS1 and JS2 folders |
