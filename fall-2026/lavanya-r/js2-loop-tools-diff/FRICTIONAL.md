# FRICTIONAL — Job-Search Agent 2

An honest, dated log of what happened, including what went wrong and what is unresolved.
Lavanya R. Times are ET.

## 2026-11-09 (evening): starting point

- Claude read my JS1 grading feedback (99/100), which I had saved. It asked for three things: write the rule in my own words, add postings I'd label "fit" so false negatives can be measured, and fix the validator's `.0` path quirk.
- Claude probed boards with one read-only GET each: Greenhouse `databricks` 914 jobs, Ashby `notion` 153 and `openai` 825, Lever `palantir` 304 and `zoox` 234. A made-up Greenhouse name returned 404. Endpoints came from Lectern's `sources.json`.
- I chose the `.0` validator fix as my review-packet change.
- Claude reproduced the defect on the **unchanged JS1 code**, using a real Claude reply from 2026-10-30 that JS1 had marked INVALID only because of `education.0.end_date` (`review/01-reproduce.txt`). It also found a second defect: `education[5].end_date` is accepted even though the persona has one education entry, because bracket indexes are ignored instead of checked.

## 2026-11-10: GATE.md

- **Friction:** I did not write GATE.md from scratch. Claude offered multiple-choice options for each section, and I picked from them.
- **Conflicts I fixed:** three of my first picks conflicted (0 jobs = "no new jobs" while I'd also marked that as a wrong version; hosts "ending in" the ATS names; retry a 404 three times). Claude pointed them out; I changed all three. The table is at the end of GATE.md.
- **My own words.** I wrote the two "In my own words" paragraphs in GATE.md (sections 1 and 4). Claude fixed only grammar and punctuation.
- **Unresolved:** most of GATE.md's reasons are Claude's option text, not mine. GATE.md labels which parts are which.

## 2026-11-10: boundary predictions

- I picked Allow / Refuse / Ask me for all 14 cases from cards, before any policy code existed.
- Four picks disagreed with my own GATE.md: case 3 (plain http) Allow, case 4 (linkedin.com) Allow, case 8 (symlink to /tmp) Allow, case 12 (overwrite state) Allow. Claude asked about each. I changed 4 → Refuse, 8 → Refuse, 12 → Ask me, and **kept case 3 as Allow**. The code follows GATE.md, so case 3 is expected to show up as a wrong prediction.

## 2026-11-10: the bug-test spec

- I started picking expected values for the bug test, then discarded those first answers and handed the remaining design decisions to Claude. **So from here on, Claude made those decisions:** the bug-test expected values (`tests/test_path_index.py`) are Claude's spec, approved by me, not mine. GATE.md and my predictions were done before this point and stay as I picked them.
- Claude then summarised my GATE.md decisions in plain words (incomplete if a board breaks; 10 boards / 20 requests / 120 s; skip repeats; no retry on 404, one retry on timeout; 0 jobs is suspicious; 3 hosts; 2 folders; ask before overwriting state). I read the summary and changed none of them.

## 2026-11-10, 17:22–17:40: the build (Claude Code did this part; logged so it can be traced)

Commits, in order: `77537ea` GATE → `7e1bacb` JS1 copy → `8fc4022` failing bug test → `8defa72` build → `8948aa3` live run 1 → `5bab37a` demo → `7044eaf` patch → `e417ced` review logs → `a6472df` predictions vs actual → `40b55f0` reviewer tests (failing) → `54b5602` revision → `b521ed3` logs.

What went wrong or was surprising, honestly:

- **check.py trusted the report it was checking.** Its first "exit honesty" check used the statuses the report gave itself, so a doctored report (`status: ok`, `exit: finished` on an empty board) passed. `test_check_catches_a_doctored_report` failed and caught it. Fixed before commit `8defa72`: the check now decides from the raw bytes which boards really worked. This was the clearest lesson of the assignment, an independent check that wasn't independent.
- **The finished-wrong demo needed three tries.**
  1. Both JS1 runs started in the same second, so they got the same file names, and run 2 overwrote run 1's report.
  2. The rerun used a zsh variable that didn't split into arguments, so steps 1–3 failed with usage errors. Worse, a hard-coded "a clean finish" note printed after an exit code of 2.
  3. Claude deleted those outputs and moved the demo into `review/finished_wrong_demo.sh` (bash, no hard-coded claims, a 1.2 s gap). Only the third run is committed (`logs/04`).
- **Claude's first patch (`7044eaf`) passed every test and was still wrong.** Reading the diff as behavior, by running old and new on inputs the test didn't have, showed a regression: a digit-only dict key like `by_year.2025` was now rejected. It also showed over-acceptance: `education.00` and a non-ASCII digit counted as index 0. The reviewer tests were committed failing (`40b55f0`), then revised (`54b5602`). A green suite was not the same as a correct change.
- **The re-validation script first missed 2 of the 3 affected replies.** The action-surface files store no posting id, and the script skipped them silently. It found 1 change; my JS1 notes said 3 replies were hurt. After the fix it found exactly those 3.
- **Mistakes in Claude's drafts, caught before commit:**
  - TRACE.md gave the wrong seq numbers (6 and 7 instead of 8 and 9);
  - REVIEW-PACKET's "would still miss" example showed no actual difference;
  - SOURCES.md said Lectern lists the Lever endpoint. It doesn't; the Lever URL came from Claude's own knowledge.
- **Approval in the live run:** run 1 had no terminal and no `--approve-state`, so the imported Databricks memory was **not** overwritten. The run ended `incomplete` for that reason as well as the 404. That was intended: approving is mine.

## Unresolved

- **"Fit" labels:** the JS1 feedback asked me to add postings I'd label "fit", so false negatives could be measured. Not done in JS2. Run 1 had 89 new Databricks postings, including several "Software Engineer - New Grad (2027 Start)" roles, which would be the place to start.
- **Real failures:** the timeout, 5xx and empty-board paths are tested only with constructed responses.
