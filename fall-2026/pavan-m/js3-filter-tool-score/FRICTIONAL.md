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

## Entry 9 — November 23, 2026: Audit results
Compared my 48 blind verdicts with the filter (audit/comparison_2026-11-23.txt). Random rejects: the filter disagreed with me on 3 of 30 (10%; 95% Wilson interval 3–26%, so somewhere around 40–330 of the 1,252 rejects could be postings I'd want). Close calls: 3 of 5 wrong just below the threshold and 3 of 5 just above. Kept sample: 2 of 8 not relevant to me.
Patterns: (1) OpenAI postings describe the work, not tool names, so real backend roles score 6 with no skill category (A04, A07); (2) the Lever retrieval gap is confirmed in the sample (A30: Java, Python, Postgres, AWS are in Lever's lists field, which the filter never sees; also "Postgres" doesn't match "PostgreSQL"); (3) all 5 false KEEPs ask for 4+ or 5+ years, which the 8-year cutoff lets through.
Honest note: my written AUDIT_RULE says 8+ years is the hard minimum, but I also judged several 4+/5+ roles not relevant under my "borderline → lean not relevant" rule. My judgment was stricter than my own written rule.

## Entry 10 — November 23, 2026: Fixed the comparison file; false friend found
My first commit of audit/comparison_2026-11-23.txt contained only a placeholder line ("see FRICTIONAL Entry 9") because I ran a placeholder snippet from Claude's instructions instead of the comparison script. Re-ran the real comparison into that file.
False friend: "Python". In 6 audited postings, "Python" matched the Programming category for the wrong reason: data analysis in a Marketing Science Lead role (A26, "SQL and Python or R"), task scripting in AI Support Engineer roles (A36, A40), ML classifiers in a Protection Scientist role (A41). The title rule rejected all of them anyway, so it did no harm here, but if the title rule were widened, this match would start admitting the wrong postings.

## Entry 11 — November 23, 2026: Choosing which rule changes to measure
From the audit's three error patterns I listed four candidate changes: C1 years cutoff 8→5, C2 read Lever's lists field, C3 any US city +2, C4 threshold 8→7. I chose to test C1 and C3, one at a time, on my 48 audited postings. Wrote tests/test_filter_config.py first: defaults must stay v1.0, each change must work when switched on, and neither may overreach (C1 still ignores "preferred" years; C3 gives nothing to non-US locations).

## Entry 12 — November 23, 2026: Measuring C1 and C3 on the audit sample
Claude Code made the filter configurable (defaults = exact v1.0) and wrote agent/measure_filter.py. Verified myself: 61 tests pass; `git diff tests/ FILTER.md audit/` empty; re-scoring with v1.0 reproduces all 48 recorded decisions.
Results on my 48 audited postings: v1.0 37/48 agree; C1 (years cutoff 5) 40/48, fixing A18, A43, A44 for the reason I wrote ("5+ years"); C3 (other US cities +2) 37/48, changing none of the 48 but adding 12 KEEPs elsewhere that I have not judged.
Caution: C1 was suggested by these same 48 postings, so 40/48 is a development result, not proof. Held-out labels are needed. A31 and A16 remain false KEEPs under C1.
Correction to Entry 8: my verdicts are 14 relevant / 34 not relevant, not 15/33. The count in Entry 8 was wrong (drafted with Claude); the CSV itself is unchanged.
Accepted Claude Code's choices, including a separate read check for audit/ rather than adding audit/ to policy.READ_DIRS.

## Entry 13 — November 23, 2026: Held-out labels, judged blind
Drew a held-out sample (seed 7376): 20 random postings with a target engineering title, excluding the 48 audited postings, plus the 12 postings that C3 adds as KEEP, shuffled together. Judged all 32 myself, blind, using audit/AUDIT_RULE.md, before opening the key: 7 relevant, 25 not relevant.
Honest notes: (1) I judged 9 internships not relevant for Alex's level, but neither my AUDIT_RULE nor FILTER.md v1.0 mentions internships; (2) as in the audit, I also judged several 4+/5+ year roles not relevant, which is stricter than my written 8+ rule.

## Entry 14 — November 23, 2026: Held-out results changed my conclusion
On 20 held-out postings, v1.0, C1 and C3 all agree with me on 18/20 (95% interval 70–97%). C1's dev gain (37→40/48) did not show up on postings it wasn't chosen from, so I added it to v1.1 only with that caveat. C3 rejected: of its 12 added KEEPs, I judged 3 relevant (25%); 7 of the 9 bad ones were internships, which exposed that FILTER.md has no internship rule. Both held-out misses (H02, H27) are Palantir, consistent with the Lever retrieval gap. C2, C4 and an internship rule were considered but not tested (time).
v1.1 = v1.0 + years cutoff 5, applied via config/filter_v1_1.json; code defaults unchanged, so no test was modified.

## Entry 15 — November 23, 2026: Source-grounded shortlist
Labeled all 50 claims for FILTER v1.1's top 10 against each posting's text, with evidence quotes (shortlist/claim_labels.csv). 17 supported, 7 contradicted, 26 insufficient. Only 4 of 20 "requires <skill>" claims were supported. Relevance ≠ entailment: S04 matched "Docker" but says "prior expertise in every tool ... is not required". Abstention counterexample: S02, S05, S07, S10 state no years, yet the justification claims Alex's ~3 years fits; the abstention rule only works per posting, not per claim. Also found the years rule misses spelled-out numbers (S09 "at least five years").
My first save of the labels didn't reach the CSV (TextEdit); the count check caught it (all 50 blank), and I re-wrote the file with my labels before committing.

## Entry 16 — November 24, 2026: MCP server tests written before implementation
Wrote 8 tests in tests/test_mcp_server.py before agent/mcp_server.py exists: initialize declares tools, the initialized notification gets no reply, tools/list offers exactly score_posting with required title/location/content, tools/call uses FILTER v1.1 (5+ years rejected), a missing argument is a tool error not a crash, an unknown tool such as apply_to_job is a protocol error (-32602), and an unknown method is -32601.

## Entry 17 — November 25, 2026: MCP server and my own client
Claude Code wrote agent/mcp_server.py (JSON-RPC 2.0 over stdio, from scratch, no SDK), agent/mcp_client.py and a project .mcp.json. Verified myself: 69 tests pass; `git diff tests/ FILTER.md` empty. Ran my client on S04 and S01: initialize (protocol 2025-06-18), tools/list (only score_posting), two tools/call (KEEP 9, KEEP 11, matching the v1.1 decisions file), and apply_to_job refused with -32602. Client- and server-side transcripts saved in out/transcripts/.
Things to evaluate later (declared vs actual): the tool declares readOnlyHint true, but the server writes a transcript file; serverInfo says version 1.1 while each score result says filter_version "1.0" with a years_cutoff override; the server answers tools/call even without a prior initialize; it supports protocol versions only up to 2025-06-18.

## Entry 18 — November 25, 2026: Claude Code used my MCP server
The desktop app's /mcp opened the account-level Connectors list, where my project server isn't shown. Asking in a new Code session started in js3-filter-tool-score worked: Claude Code found js3-job-filter from the project .mcp.json, called score_posting once, and showed the exact result (KEEP, score 11). Server-side transcript: out/transcripts/server-2026-11-25T060303.jsonl.
Claude noticed something I hadn't: the test description I sent (drafted with Claude in chat) was only ~26 real words, padded with 50 repeated "team" words, which pushed it past the 50-word rule. The filter's word count checks length, not meaning, so filler defeats the abstention rule. Another real limit of FILTER.md §2.6/§3.7.

## Entry 19 — November 25, 2026: Evaluating Microsoft Learn's MCP server
Called https://learn.microsoft.com/api/mcp myself with curl (not via my agent): initialize, notifications/initialized, tools/list, then four tools/call tests. All saved in evidence/other_server_mslearn/. Findings: the same search twice gave identical results; a search with no query returned empty results with no error; a non-Microsoft fetch URL was refused only in the text, with isError unset; the session ID is base64 JSON containing my clientInfo and a userIdClaim. Wrote TOOL_SERVER.md with both evaluations and my trust decisions (drafted with Claude from these transcripts; I checked each claim against the saved files).
Small snag: my terminal printed "command not found: #" for comment lines in a pasted block; harmless, the requests still ran.
