# FRICTIONAL — what actually happened

## Executive summary

This is an honest log of what went wrong, what was tried, what was accepted or rejected, and
what is still unresolved while building Job-Search Agent 3 on 2026-11-14. Each entry traces
to a commit, a file or a test. **The section "In my own words" is for me (Smit) to write.**
A log drafted by Claude is not my account.

## Log of events (drafted by Claude from the session; each item is traceable)

| # | What happened | What was done | Accepted / modified / rejected | Trace |
|---|---|---|---|---|
| F1 | Job-Search Agent 2's saved Figma responses have no job descriptions (fetched without `content=true`), and this layer needs text to check claims against | a fresh live collection with descriptions, from the same boards plus Airbnb | Claude's decision | `runs/live-20261114/manifest.json`, `ace3d80c` |
| F2 | All 27 filter tests passed on the first run, the same warning sign as in Job-Search Agent 1 | a deliberate-bug check: 11 of 12 caught. The survivor (M7) is a second guard on the tool server and is explained in the log | accepted: reported, not hidden | `tests/mutation-log.md` |
| F3 | The first fact cards for hand judging showed only the years sentence the filter had used. For "5+ years …, including 3+ years with Ruby" that was the 3-year sentence, which would have hidden the filter's error from the judge | fixed before any judging: cards show every years sentence. Sample membership unchanged (checked) | — | `de37311d` |
| F4 | The audit found that rule R5's "smallest number of years" definition, written by Claude to make the rule testable, caused 3 of 6 keeps to be wrong | change A (largest number) measured alone, then adopted by Smit | modified: Claude's definition cut | FILTER.md v1.1, `02b326be` |
| F5 | Two hand verdicts called Engineering Manager roles relevant, against Smit's own written yardstick | asked once; Smit kept them; recorded as given | — | `audit/hand-verdicts.json` `checks_asked` |
| F6 | Three hand verdicts called two Stockholm jobs and a 5-year job relevant | asked once; Smit changed all three to not relevant; a fourth (Stockholm, Backstage) stayed relevant and was not asked again | modified by Smit | same file, `not_asked_again` |
| F7 | One answer ticked both a posting and "None of these 3" | asked; Smit chose "Relevant" | — | same file |
| F8 | Change C (1 skill is enough) made held-out worse on its own (3 → 4 errors) | Smit chose it anyway: "Missing good jobs worse". In combination with A, held-out stayed at 3 | Smit's decision against the held-out signal | FILTER.md v1.1 table |
| F9 | Held-out results for each candidate were shown before Smit chose, so held-out is no longer untouched for v1.1 | disclosed in FILTER.md and WHAT-MOVES-THE-SCORE.md | unresolved | FILTER.md caveat |
| F10 | The filter answered "I cannot tell" 0 times in 473 postings | kept as a finding; counterexample in SHORTLIST.md (no years and "varying seniority levels", yet ranked first) | unresolved: the abstention rule is not changed | SHORTLIST.md |
| F11 | Claude Code's first message to the tool server was `server/discover` at protocol `2026-07-28`, which the server does not know | the server answered `-32601`; the client fell back to `initialize` at `2025-11-25`, and the session worked | no change | `transcripts/claude-code-client-20261114-server-side.jsonl` line 1 |
| F12 | The same transcript showed evidence quotes cut at "e.g." (", React/TypeScript) and back-end technologies (e."), which Claude Code repeated faithfully | display fix in `sentence_around`. All verdicts, rules and scores checked unchanged before and after. The old transcript is kept as recorded | — | `28019a49`, `tests/test_filter.py` `test_context_is_the_whole_sentence` |
| F13 | The claim checker first labeled "(e.g., Ruby, Python, …)" as supported: `\be\.g\.\b` never matches "e.g.," | fixed before the checker labels were committed; a test for it was added later | — | `src/shortlist.py` comment, `e45695e4`; `tests/test_parts.py` `ClaimChecker` (`cb9ec66d`) |
| F14 | Smit labeled all 18 shortlist claims supported; the checker labeled 8 insufficient | asked once about the 5 claims whose quotes state no years or say the level is decided later; Smit answered "Keep as Supported" | Smit's labels kept; the checker's kept beside them | `audit/shortlist-hand-labels.json` |
| F15 | Microsoft Learn's session id decoded to readable JSON with a `userIdClaim`; its declared `prompts` and `resources` were empty | recorded in the evaluation. Testing `microsoft_docs_fetch` on a non-Microsoft URL was deliberately **not** done, because it would probe someone else's server beyond normal use | — | `transcripts/mslearn-session-20261114.jsonl` |
| F16 | The same Claude configuration, run twice, answered differently on 1 of 33 postings | used as the evidence for "persistence is not proof" | — | `experiments/results/SCORES.md` |
| F17 | Given the tool's output instead of the posting, Claude abstained 6 times | explained: a title reject's tool output carries no description | — | WHAT-MOVES-THE-SCORE.md |
| — | **Not done:** the tool-list change measured on held-out; Claude judge on dev; a second collection day; any test written by Smit before reading Claude's code | stated in README "Not checked" | — | README |

## In my own words (Smit — to write)

- What surprised me:
- What I checked myself, and how:
- What I would not have caught without the audit or the claim labels:
- What I accepted, changed or rejected from Claude, and why:
- What is still unresolved:
