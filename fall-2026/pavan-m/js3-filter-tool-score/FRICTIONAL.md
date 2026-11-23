# FRICTIONAL — Job-Search Agent 3

## Entry 1 — November 19, 2026: Starting point
Started from my own JS2 (../js2-loop-tools-diff, submitted at 70f8e203), copied unchanged: agent/, tests/, config/, data/, prompts/, check_run.py. Also copied JS2's out/state/ (ids seen as of the Nov 10 runs), so JS3's first live run compares against Nov 10 and reports postings added since then. 40 tests pass in the new folder. JS2 not yet graded.

## Entry 2 — November 19, 2026: Live run 1 (day 1 of 3)
Ran the JS2 loop live at 7:08 PM EST (out/runs/2026-11-19T190803/). Status incomplete, exit 1 (deliberate bad board). Compared with the Nov 10 state: Glean 128 postings, 14 new; Palantir 307, 11 new; OpenAI 849, 109 new. 1,284 postings collected in total; this is the set the filter will run on.

## Entry 3 — November 19, 2026: FILTER.md v1.0 written before the build
Wrote FILTER.md v1.0: weighted score (title 4 + skill categories up to 8 + location 2, threshold 8), hard rejections, evidence rules, abstention rule, expected sources and fields, five wrong versions, and a table of where every number came from (all hand-set).
Review with Claude found mismatches I fixed before committing: my first draft listed GCP and MySQL, which aren't in Alex's résumé, and left out Python, which is; the starting-point paragraph wrongly said v1.0 adds Lever/Ashby support (JS2 already had it); "nearly empty", the years rule and location aliases weren't hand-checkable (now: <50 words; "N+ years" with N ≥ 8; explicit location aliases); and my first abstention counterexample showed the rule working, not its limit. Final fixes: a wrong Kafka example, the "SF" alias, REVIEW clarified as a flag, and one rule that couldn't be applied mechanically.

## Entry 4 — November 23, 2026: Live run 2 (day 2)
Ran the loop live at 3:31 PM EST (out/runs/2026-11-23T153111/). Status incomplete, exit 1 (deliberate bad board). Compared with the Nov 19 state: Glean 129 postings, 3 new; Palantir 306, 3 new; OpenAI 855, 34 new. Agent runs now exist on two real days (Nov 19 and Nov 23). I was away Nov 20–22, so no runs those days; the deadline moved to Wednesday, Nov 25.
## Entry 5 — November 23, 2026: Filter tests written before implementation
Wrote the asserts for 15 tests in tests/test_filter.py before agent/filter.py exists: one per wrong version in FILTER.md §5 (substring, title-only, raw counting, missing description, case), plus key rules (score math = 10, 8+ years rejected but 5+ not, Manager rejected, Senior flagged not rejected, plain "Remote" is CANNOT TELL, non-US rejected, <50 words is CANNOT TELL, "Spring" alone is not Spring Boot, HTML decoded before matching). First run: ModuleNotFoundError for agent.filter (expected).
