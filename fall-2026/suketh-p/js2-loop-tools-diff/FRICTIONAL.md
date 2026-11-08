# FRICTIONAL — Job-Search Agent 2

Two parts. **The student's entries** are the student's own words, dated and placed verbatim; Claude Code adds only the headings. **Claude Code's timeline** (added in later commits) is a factual record of what Claude Code did, with times the commits or saved files can show. Nothing in it is presented as the student's experience.

## The student's entries

### 2026-11-08, before building

November 8, 2026 - Before building

I expect the hard part to be telling the difference between a board with no new jobs and a board I couldn’t check. With two systems, I also need to make sure a posting from one board doesn’t get counted as already seen because it shares a key with another board. I’ll check the saved responses and compare the posting history before and after a run where one board fails.

### 2026-11-08, after the failure run against the saved state

November 8, 2026 — After the failure run

I compared the state file with the copy I saved before the run, then ran the independent checker against the saved responses and both state files. The bad board returned a 404, its job count showed as unknown, and the run ended incomplete with the state file unchanged, just as I expected. I still need to check whether the loop handles a 200 response with an empty jobs list the same way.
