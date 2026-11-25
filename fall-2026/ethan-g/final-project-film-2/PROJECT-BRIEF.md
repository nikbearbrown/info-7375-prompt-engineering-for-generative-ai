# PROJECT-BRIEF — DataSentry (project film)

**Ethan Gomes · INFO 7375 · project film in four parts · 2026-11-23**
**Target role:** Data Engineer (also Data Analyst / BI) · **Stack:** Python, pandas, pandera, Claude (Opus 5.5) through
Claude Code on my existing subscription; NYC TLC taxi data (public). Detail: `APPENDIX.md`. Sources: `SOURCES.md`.

**1. Executive summary — what and why.** DataSentry is an AI agent that writes data-quality checks for a table, tests
them against bad rows I planted on purpose, and revises them until a person approves the final set. It matters
because checks that quietly let bad rows through put wrong numbers into dashboards and decisions, and as AI writes
more of those checks, someone has to grade them.

**2. Introduction — what others have done.** pandera, dbt and Great Expectations run rules on tables; Amazon's Deequ
suggests them. I ran one rule, fare can't be negative, in all three (2026-10-25): all caught the 25 negative fares;
none caught the 25 trips that end before they start. AI already writes tests: GX Cloud's paid ExpectAI suggests data
checks; at Meta, AI-written unit tests built 75% of the time and passed 57% (TestGen-LLM, 2024), and a later tool
steered by planted bugs had 73% of its tests accepted (ACH, 2025). Mutation testing has graded code tests with
planted bugs since 1978. In what I found, nobody does that for AI-written data checks on real tables: that is the gap.

**3. Methods — how.** Data: NYC yellow taxi trips, January 2025, a clean 10,000-row sample. Step 1 (built): a planter
breaks copies of the table five ways and locks the answer key away. Step 2 (built): Claude sees only the column names
and types and writes pandera checks under a contract; an independent scorer grades them on the clean copy and every
broken copy. Step 3 (built and run, 2026-11-23): the loop feeds only the clean copy's results back, up to three
rounds, every round logged. Claude runs with no built-in tools, in an empty folder, and every checks file must pass a
code policy before it runs. Planned: a tool menu Claude chooses from, with every call checked in code, and a human
gate (scorecard, code and sha256 shown; approve, refuse or defer). Resources: public data, my laptop, my existing
Claude subscription; no API key, no credits.

**4. Evaluation — how I'll know it worked.** I measure defect types caught, false alarms on good trips, and crashing
checks, on held-out data never used for tuning (a second planting, a second clean copy). It passes only with all five
defect types caught, zero good trips flagged and no crashing checks, on both plantings; anything less fails. Results:
by hand nothing passed; the loop flagged 94, then 1, then 0 good trips and met the pass line in round 3, and its
checks flagged 0 good trips on the second clean copy. Planned: at least five deliberate failure cases and one
controlled failure (predicted, triggered, caught by the held-out scorer, refused at the gate). Limits: one table, five
planted defect types; not shown yet for other tables or real, unplanted defects.

---

**Exists today (2026-11-23)**

- This brief, the project film, its beat sheet, appendix and build files.
- `first-run/`: the planter, the scorer, the hand-written baseline, the dbt and GX comparison, two hand-run Claude
  rounds (2026-10-25), and the loop (`loop.py`, `run_loop.sh`, 13 tests written first) with its live run
  (`loop-runs/2026-11-23_182418/`) and the second-clean-copy check (`heldout_clean.py`).

**Will exist**

- The tool menu Claude chooses from, with every call checked in code, and a budget on calls and time.
- The human gate bound to what the approver saw.
- A frozen held-out set from a different month, at least five deliberate failure cases, and the controlled failure.
- The public repository.
