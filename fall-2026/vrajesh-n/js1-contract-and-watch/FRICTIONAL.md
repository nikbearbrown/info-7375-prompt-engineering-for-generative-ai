# FRICTIONAL — JS1

> The entries are my (Vrajesh's) own words, dictated in chat to Claude Code and placed here verbatim. [Brackets] are Claude's notes, not my words. The traceability table at the end was compiled by Claude from the files and runs.

## 2026-10-24
- Wrote the first CONTRACT.md in my own words (board: Ashby; "Relevant means: Role type: Software Engineer, United States, Entry Level"; the role-word list; the blockers; "Failure would look like no jobs found"). About ten items were still OPEN. [See CONTRACT.md, lines marked "My words, 10-24".]
- My first test expectation: "for each row in the table given resume, I expect a job to apply."

## 2026-10-31

**What surprised me.**
"Well the Job 5 where the job is 2+ years but i guess first it might be in new grad catagory for master student but claude said no that surprised me."
[Job 5 = "Software Engineer, AI Integrations". Claude said not_relevant in all 4 sampling runs, in both prompts on dev, in my claude.ai chat, and in action-surface arms 2 and 3.]

**Why #8 changed from no to yes.**
"For #8 Today i thought that if that job does not have experience mentioned it might not be new grad but then i again went to that job and it was a type of entry level job so that's changed my mind."
[#8 = "Fullstack Engineer, Ambient AI" (dev set). The change came after the first baseline dev run; that run is kept as `experiments/results/baseline-dev-labels-v1.json`.]

**What I accepted, modified or rejected from Claude.**
"I mean yes claude said that the job 5 is irrelevent / not new grad but for a master student i think companies can prefer new grad"
[So I rejected Claude's verdict on job 5 and kept my label `relevant`. For the contract and the one prompt change I picked from options Claude listed; each pick is marked *(chosen 10-31)* in CONTRACT.md and in PROMPT-EXPERIMENT.md.]

**What is unresolved.**
"No i think everything resolved now"
[Claude's note, not mine: the README sign-off "Not checked" list still names limits that were not tested, such as other boards, R4 never firing on a real posting, and the years regex.]

## Traceability (compiled by Claude)

| What | Where |
|---|---|
| Contract written before code | CONTRACT.md (10-24 words plus 10-31 choices); TEST-EXPECTATIONS.md; commit order in git (contract committed first) |
| Wrong versions caught | `tests/wrong_versions.py`; `test_tests_catch_wrong_version_1/2` |
| My test run | README sign-off "How": 21 passed in 0.10s |
| Watch runs | `reports/run1-*`, `run2-*`, `run3-*`; `data/state/seen.json` `runs` list |
| Crash found and fixed | `earlybird/resume.py`: a non-JSON resume crashed instead of being refused (found on run 3's day, 10-31) |
| First label draw discarded | `experiments/make_label_sheet.py` docstring; PROMPT-EXPERIMENT.md "Labels" |
| My hand labels and the #8 change | `experiments/labels.csv` `hand_note` column |
| Prompts | `experiments/prompts/baseline.txt`, `revision.txt` (one added line) |
| Agent arm write denied | `experiments/action-surface/arm3-output.json` `permission_denials` |
