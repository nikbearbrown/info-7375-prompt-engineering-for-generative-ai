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

## Entry 6 — November 23, 2026: Claude Code built the filter
Claude Code wrote agent/filter.py and agent/run_filter.py against FILTER.md v1.0. Verified myself: `python -m pytest -q` → 55 passed (40 earlier + 15 filter); `git diff tests/ FILTER.md CLAUDE.md` empty.
First run on run 2 (1,290 postings): KEEP 31, REJECT 1,252, CANNOT TELL 7. Palantir had 0 KEEPs out of 306, which needs checking in the audit before I change anything.

## Entry 7 — November 23, 2026: Reading Claude Code's choices; a retrieval gap
Claude Code listed 19 choices FILTER.md didn't decide. Three change what FILTER.md literally says, so I recorded them in FILTER.md §9 instead of leaving them in the code: bare "San Francisco" gets +2 (23 of OpenAI's 25 KEEPs depend on it), "US - Remote" counts as US remote, and "REST API" singular matches.
Investigated Palantir's 0 KEEPs: 139 postings are titled Software Engineer, but 67 had no technical category. Claude Code found the cause: the JS2 Lever adapter reads only descriptionPlain, and Lever keeps "What We Require" in a separate `lists` field. The filter never sees those requirements. This is a retrieval gap, not a filter rule. Not fixing it yet; the audit will measure it first.

## Entry 8 — November 23, 2026: Hand verdicts for the audit, judged blind
I judged all 48 audit postings myself from audit/postings_to_judge.md (full text, including Lever's "What We Require" lists), using only audit/AUDIT_RULE.md and without opening the answer key or seeing the filter's scores. No AI tool made these verdicts. 15 relevant, 33 not relevant, 0 cannot tell. A02 uses "platform" to mean an ad-sales platform, not software infrastructure (a candidate false friend, though "platform" is not a keyword the filter scores).
