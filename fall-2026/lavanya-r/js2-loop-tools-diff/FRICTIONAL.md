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
