# Frictional

<!-- Dated entries, written the same day. Entries marked DRAFT were drafted by Claude from the session and still need rewriting in my own words before submission. -->

## Nov 23, 2026 — Day 1: data, FILTER.md, label sample

- **What happened:** After going over the assignment requirements and the Nov 25 deadline, I started from my JS2 scraping agent. Checking the saved JS2 Greenhouse responses for Robinhood and Affirm showed that they lacked job description bodies because JS2 requested `/jobs` without `?content=true`. Since the JS3 evidence rules require quoting exact spans from the posting text, I re-collected all three boards with `?content=true` in `run-20261123-185425Z` (3 GET requests, 1.8 s, status `finished`), pulling 400 postings total: 162 from Robinhood, 218 from Affirm, and 20 from Wealthfront, all with title, location, and body text.
- **Decisions I made:** I chose to re-collect with `?content=true` rather than limiting the filter to job titles, kept Sam Rivera as a new-grad software engineering persona instead of switching to AI/ML, and dropped JS2's deliberate 404 test board.
- **What the initial survey showed:** Before any filter rules existed, scanning the 400 postings showed four patterns that shaped `FILTER.md` v1.0: 149 of 199 engineering-related titles included a seniority word; title levels did not match stated requirements (the initial survey script reported `Software Engineer II` at Affirm asking for `5+ years`); `Full Stack` appeared inside non-engineering titles like `Analytics Lead, Full Stack`; and Affirm posted separate country copies of the same role (`Remote US` / `Remote Canada`), leaving 91 postings sharing a board and title with another posting.
- **Friction 1 — `FILTER.md` duplication during an edit:** While fixing a one-word typo in wrong version W1, a Python find-and-replace script failed to match because the title was wrapped in backticks (`find()` returned `-1`) and appended a duplicate copy of the file onto itself (230 lines, two changelogs). Claude ran that script and caught the duplicate in its own `grep` output; it restored the original 115-line single-changelog version and re-applied the fix before any commits were made.
- **Friction 2 — Redesigning the label sample:** The initial seeded sample (60 postings: 40 engineering-ish, 20 other) only had about one likely `keep` in its 30-posting held-out split, which would not have given us enough positive cases to measure filter changes. Before labeling anything, we redesigned the sampler (v2, seed `2026`) to draw 90 postings split 45/45 into `dev` and `heldout`: all 50 engineering titles without a seniority or intern word (stratum A1), 20 random seniority titles (stratum A2), and 20 random other titles (stratum B). Because stratum A1 reuses the G1/G2 keyword list, the 90-row set is a stratified benchmark rather than a uniform random sample of the 400 postings.
- **Why I accepted `FILTER.md` v1.0 as written:** I had Claude draft `FILTER.md` v1.0 from the survey summary and committed it untouched (`0041401`) before writing any filter code so the specification stayed strictly separate from implementation. I accepted the core rules because they mapped directly to concrete patterns in our data: G1 filtered out the 149/199 senior titles, R1 required full role phrases to block `Analytics Lead, Full Stack` and `Offensive Security Engineer`, G3 ran before deduplication so `Remote Canada` copies would not mask `Remote US` openings, and R2 penalized `4+ years` in the body instead of trusting title numerals. I took the `Software Engineer II` / `5+ years` example at face value without opening the raw posting myself because it fit what I expected from mid-level fintech listings, and I accepted the unmeasured weights (`0.50` threshold, `+0.30` / `-0.40` R2 points) plus the `R2 + R3 = 0.50` edge case knowing the 90-row audit would test them empirically.
- **Reference commits:** `0041401` (`FILTER.md` v1.0 alone, prior to any filter code), `b19d5ad` (collection run, loader, unlabeled label sheets, and initial logs).

## Nov 23, 2026 (later) — Labels and correcting the survey regex bug

- **What happened:** I hand-labeled all 90 sampled postings by reading the titles, locations, and full body text (`dev`: 6 keep / 39 reject; `heldout`: 5 keep / 40 reject) and committed the completed CSVs (`215f29a`) before writing any filter code. Afterward, Claude checked the experience requirements cited in my `my_reason` column against the raw posting text: all 29 year counts cited in my dev reasons matched; separately, one held-out reason (`affirm:8032173003`) was a guess that contradicted its posting.
- **The label I changed:** For `affirm:8032173003` (`Software Engineer II, Full Stack (Card Acquisition)`, `Remote US`), I initially guessed `reject` (`likely 2-5+ yrs`) from the title level. Claude pointed out that the body actually asks for `1.5+ years`—identical to the other Affirm `Software Engineer II` roles I had marked `keep`—so I updated it to `keep` (`unsure: SWE II asking 1.5+ yrs, US remote`) prior to committing the label sheets.
- **Fixing the false `5+ years` survey claim:** While cross-checking my labels, Claude found why its Day 1 survey claimed Affirm's `Software Engineer II` asked for `5+ years`: the quick survey regex only matched whole integers, so it stripped the `1.` off `1.5+ years` and reported `5+`. Reviewing all `Engineer II` postings in the dataset showed that most actually ask for `1.5+ years`, with a smaller number asking for `2+ years`, `3+ years`, or no fixed minimum.
- **What I changed:** I added a `v1.1` correction note and changelog entry to `FILTER.md` while leaving the `v1.0` rules untouched so the pre-code baseline remains intact. Wrong version W2 now cites a verified `3+ years` posting (`Software Engineer II, Backend (Test Infra)`, labeled `reject`), and parsing decimal years (`1.5+` as `1.5`, not `5`) is set as the first test case for Day 2.
- **What I learned:** A quick regex used during exploratory data profiling had the exact decimal-truncation bug we need to prevent in `agent/filter.py`. Spot-checking matched sentences against the full text during labeling caught the error before it got baked into the filter logic.
- **Reference commits:** `215f29a` (90 hand-labeled rows in `labels/dev.csv` and `labels/heldout.csv`), `5b192f5` (`FILTER.md` v1.1 correction and the first version of this entry), `6cd481c` (commit hash filled in).

## Nov 24, 2026 — DRAFT (Claude, to rewrite): tests, filter v1.0 run, dev comparison

- Tests were committed alone (`3beb6f0`) and failed (no `agent/filter.py`). Then the filter was written to FILTER.md v1.1; all 26 tests passed. `tests/wrong_versions.py` patches each of W1–W5 into the filter: every one makes its test class fail.
- The "`&amp;` left in URLs" bug planned for today does not exist: 0 of 400 URLs contain `&amp;`. Robinhood URLs contain a plain `&` (`?t=gh_src=&gh_jid=…`), which is correct. No test or fix was written for it.
- Run on all 400 (`evidence/filter-v1.0/`): kept 22. On dev labels only: tp 6, fp 6, fn 0, tn 33. **All 6 false positives ask for exactly 3 years** (R2 gives 0 at N = 3, so R1 + R4 = 0.60 passes). Held-out has not been run.
- `affirm:7727320003` (W2's real example, 3+ years) is one of them: the W2 test passes only because its fixture says 5+ years. The real filter still keeps the real example.

## Nov 24, 2026 (later) — DRAFT (Claude, to rewrite): audit of v1.0, rule change v1.2

- I hand-judged the v1.0 audit (`c87c9b6`, `cd6bfe8`): 0 of 30 random rejects should have been kept (95% Wilson 0–11.4%, a sample estimate for this run's 378 rejects); 11 of the 22 kept postings should be kept (all kept, so measured for this run); 1 of 9 close calls (`affirm:7815952003`, Quantitative Analyst II, score 0.40) I judged keep. TODO: my reason for that one, and whether it means Sam's target is wider than SWE.
- 7 of the 11 wrong keeps asked for exactly 3 years; 3 were Robinhood backend roles asking 2+ years but written as mid-level; 1 was a Wealthfront iOS role.
- Changed one rule (FILTER.md v1.2): N ≥ 3 years scores −0.40. Tests for it were added and seen failing first. Dev: fp 6 → 0, tp still 6. On all 400, exactly the 7 three-year keeps flipped to reject.
- Leakage: the kept audit sheet included held-out rows, so I saw some held-out postings' decisions before choosing the rule. Held-out is not fully untouched for v1.2; the README must say so.

## Nov 24, 2026 (later still) — DRAFT (Claude, to rewrite): the one held-out run

- Ran held-out once (`evidence/heldout/v1.0-vs-v1.2.txt`, via `agent/evaluate.py`, which only reads saved decisions): v1.0 fp 5 → v1.2 fp 4; tp 5 and fn 0 both times.
- Dev had promised more: 6 false positives fixed on dev, 1 on held-out. Held-out's errors are mostly a different kind (2+ years written as mid-level; mobile stack) that the 3-year rule does not touch.
- With 5 true keeps and a 1-posting difference, held-out cannot show that v1.2 is better in general, only that it did not hurt recall here.

## Nov 24, 2026 (evening) — DRAFT (Claude, to rewrite): source-grounded shortlist

- Tests committed alone first (`f89aef7`), then `agent/shortlist.py`; 13 shortlist tests pass, including one that checks every quote on the real shortlist is a substring of its posting.
- v1.2's 15 kept postings → 10 ranked, 1 "I cannot tell", 4 contradicted. Cases are in `shortlist/CASES.md`: relevance ≠ entailment (`robinhood:7263592`, "2+ years" vs "Strong track record…") and the abstention counterexample (`affirm:7749755003`, abstained only because its skills sit in a "is a plus" sentence; I judged it keep).
- The `track record` / `proven ability` contradiction cue was chosen after I had judged those exact postings, and all 4 contradicted entries are held-out rows. The shortlist agreeing with me there is not a measurement.
- My audit reasons for the three SWE I roles say "early career"; the postings never say that. The supporting span is "previous work or internship experience".

## Nov 24, 2026 (night) — DRAFT (Claude, to rewrite): MCP server from scratch

- Tests first (`8458710`, 12 tests, all failing), then `agent/mcp_server.py`: stdio, one JSON-RPC 2.0 message per line, `initialize` / `notifications/initialized` / `ping` / `tools/list` / `tools/call`, stdlib only, no MCP SDK.
- Four read-only tools over the saved Nov 23 run: `search_postings`, `get_posting`, `judge_posting` (v1.2), `shortlist_entry`. No network, no subprocess; the only file it writes is its call log, and it refuses a log path outside `out/`.
- `evidence/mcp/scripted-transcript.jsonl` is a **scripted** client (`tests/mcp_scripted_client.py`), not a model; it includes a bad uid (tool error, server stays up) and a call to a tool that does not exist (`apply_to_job` → JSON-RPC error -32602).
- Not done yet: a transcript with a real client (Claude Code), and the two server evaluations (mine and one other named server).

## Nov 24, 2026 (night, later) — DRAFT (Claude, to rewrite): real client transcript

- With my yes, Claude registered the server in Claude Code at **local scope** (`claude mcp add --scope local js3-job-filter …`; remove with `claude mcp remove js3-job-filter -s local`). It first made the server find its own folder so it runs from any directory.
- Recorded one real `claude -p` session at 2026-11-24T06:03Z (`evidence/mcp/claude-code-transcript.md` / `.jsonl`, trimmed of local paths; server log alongside). 12 turns, 10 tool calls, reported cost $0.33.
- What the client found about my server: `search_postings` is a substring search, so "Software Engineer I" also matched 23 SWE II postings and an intern posting (it filtered them out itself); `judge_posting` names a gate ("G3") without saying what it checks. Both go into my server evaluation.
- The client also called out that the `entry` quote ("internship experience") fits entry level without stating it, which is the same weakness I noted in CASES.md.

## Nov 24, 2026 (night, last) — DRAFT (Claude, to rewrite): two server evaluations

- `mcp/EVALUATIONS.md`: my server (run: tests, two transcripts, a probe) and the official Filesystem server (read from GitHub source and README, version 2.4.0, **not run**: installing it means downloading and executing code I did not write).
- The probe found my schemas are not enforced: an extra `"delete": true` argument is silently accepted, and `board: "lever"` returns 0 results instead of an error, which is the "no matches on X" answer FILTER.md §3 forbids.
- The real Claude Code answer said "23 Software Engineer II postings"; a script recount says 22. The transcript stays as it was; the error is noted in the evaluation.
- Five fixes are listed but not made.
