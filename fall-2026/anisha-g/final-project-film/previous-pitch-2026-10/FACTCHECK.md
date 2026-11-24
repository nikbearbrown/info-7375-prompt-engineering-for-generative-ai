# Fact check

Status: claims listed by Claude, 2026-10-14; each row checked against its source by Anisha Gaikar, 2026-10-14. Nothing in the project is built yet, so every statement about the tool is a plan, marked EXEMPT, and said with "will" in the film.

| # | Beat | Claim (as spoken / shown) | Verdict | Source / derivation | Fix |
|---|---|---|---|---|---|
| 1 | B00 | Project is JobPost Contracts, a Python tool that summarizes job postings and catches when the AI makes things up | EXEMPT | Proposal, defined in `PROJECT-BRIEF.md` §1 | Film says "nothing is built yet"; every drawing labelled CONSTRUCTED |
| 2 | B00 | Nothing is built yet | PASS | This folder: no code, contracts, test postings or results exist | none |
| 3 | B01 | Definitions of prompt contract, synthetic posting, grounded field | EXEMPT | Working definitions for this film; course vocabulary from the assignment text | none |
| 4 | B02 | When done it will be a GitHub repo with contracts, twenty synthetic postings, a test script and an evaluation log | EXEMPT | Plan, `PROJECT-BRIEF.md` §1 and "Will exist" | Said with "will" |
| 5 | B03 | On October 13 ChatGPT could not open the LinkedIn posting link | PASS | `evidence/chatgpt-link-2026-10-13.png` (my own run) | none |
| 6 | B03 | With the text pasted, ChatGPT summarised the posting but showed no line each fact came from | PASS | `evidence/chatgpt-pasted-2026-10-13.png`: no quotes or sources in any field | none |
| 7 | B03 | Under location ChatGPT added a detail not in the posting | PASS | `evidence/chatgpt-pasted-2026-10-13.png`: "Staples is headquartered near Boston, Massachusetts", while it also says location is not specified in the posting | none |
| 8 | B03 | Copying fields into a spreadsheet by hand is accurate but slow | EXEMPT | Description of the manual process, not a measured result | No timing figure claimed |
| 9 | B04 | Reader opens the README, runs one command, sees a pass/fail table in the first sixty seconds | EXEMPT | Planned reader experience, `PROJECT-BRIEF.md` §3 | Said with "will" |
| 10 | B05 | The four skills (prompt contracts, source grounding, verification, evaluation) are taught in this course | PASS | Assignment text, question 4: "prompt contracts, verification, agent loops, evaluation, source grounding" | none |
| 11 | B05 | It will not prove the tool works on real postings at scale | PASS | Scope: test set is synthetic only (`PROJECT-BRIEF.md` §4) | none |
| 12 | B06 | Five fields in scope; scraping, real postings and career advice out of scope | EXEMPT | Scope decision, `PROJECT-BRIEF.md` §5 | none |
| 13 | B07 | Plan to write at least five deliberately tricky postings | EXEMPT | Risk plan, `PROJECT-BRIEF.md` §6 | Said with "will" |
| 14 | B08 | I already have Python, including tests and data-quality checks; evidence is my MBTA transit reliability pipeline | PASS | github.com/anishagaikar0420/mbta-reliability-pipeline: Python package in `src/`, a `tests/` suite, and a quality gate (row counts, coverage, duplicates) described in its README | none |
| 15 | B09 | Exists today: this brief, this beat sheet and this film; no code or results yet | PASS | This folder's contents | none |
