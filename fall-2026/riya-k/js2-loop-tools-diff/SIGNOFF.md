# Sign-off — Job-Search Agent 2

**DRAFT by Claude Code, 2026-11-09. Not signed until I have read every line below and signed at the bottom.**

## Checked: which properties, by which of my own tests

| Property | Test(s) | How |
|---|---|---|
| Exits: `finished` only when every board is ok with >0 postings; a failed board → `incomplete`; budget stop → `budget_exhausted`; bad config → `error` | `test_all_good_boards_finish`, `test_wrong_version_2_failed_board_is_null_not_zero`, `test_seventh_board_never_runs`, `test_bad_config_is_error_exit`, `test_config_outside_read_roots_is_refused` | test written before I saw it pass; mutations 3a/3b caught |
| A failed board is `null`, never 0 | `test_wrong_version_2_failed_board_is_null_not_zero`; live day 1 (`notarealco-js2` → `postings: null`) | test + **by hand**, reading the day-1 report |
| Empty board flagged, not reported as "no new jobs", not baselined | `test_wrong_version_1_empty_board_is_flagged_not_success`; live day 1 (hubspot `suspect_empty`) | test + by hand |
| Error policy: 404 never retried; timeout/5xx retried once after a real 2 s wait | `test_wrong_version_4_404_is_never_retried`, `test_timeout_retried_once_after_wait_then_succeeds`, `test_5xx_retried_at_most_once` | test; mutations 4a/4b caught |
| Budgets: never an 11th request, never a 7th board, no request or retry after 60 s | `test_wrong_version_5_never_an_11th_request`, `test_seventh_board_never_runs`, `test_time_budget_stops_before_next_board`, `test_retry_not_started_if_wait_would_break_time_budget`, `test_config_cannot_raise_budget` | test; mutation 5 caught |
| Repeat rule | `test_repeat_rule_blocks_second_identical_request`, `test_duplicate_board_in_config_read_once` | test |
| Permission policy: 17 boundary cases | `tests/test_policy.py` B01–B17 | **predicted before the code** (`2b6071e`), 17/17 as predicted; mutations 6/7/8 caught |
| The write that needs approval | B16, B17, `test_reset_refused_without_approve_then_allowed_with_it` | test + README command 8 |
| Intern exclusion, incl. the real posting 6866538002, and no false hits on Internal/International/Internals | `tests/test_intern.py` | **test written before the patch** (`fdae00e`), I ran it red then green |
| Full-time only | `tests/test_fulltime.py` | test committed red before the change (`2eb2a7c`) |
| A finished wrong answer is caught | `tools/independent_check.py` on the naive run → CONTRADICTED | by recomputation from a second source (live, 2026-11-09) |

**How:** every test above ran offline. Claude Code wrote the code and the tests (see SOURCES.md). I decided what the
boundary cases, the intern test and the full-time test had to show, and I ran the reproduce/red test, the post-patch suite
and the mutation check myself. Claude's help: writing all code and tests; running the seeded run and the build-time test runs.

## Not checked (real items)

1. **A real retry never happened live.** No board timed out or returned 5xx on 2026-11-09, so the retry path has only been
   tested with a fake transport.
2. **Pagination.** SmartRecruiters returns at most 100 postings per page, and the loop reads one page. A SmartRecruiters
   board with more than 100 postings would be undercounted and nothing would flag it. (Greenhouse and Ashby returned all
   postings in one response for my boards, but I did not check a documented limit.)
3. **Greenhouse part-time/contract roles whose title doesn't say so** pass the full-time rule. Greenhouse gives no employment type.
4. **The 23 postings rated relevant on day 1 (after amendments 3–4) were not hand-checked.**
5. **The second-source check covers only HubSpot.** Any other board that returns 0 postings gets `NO_SECOND_SOURCE`, not a verdict.
6. **The 60 s budget** is checked before each request, and each request's timeout is capped at the remaining time. Reading a
   very large body is not time-limited, so a run could go slightly over 60 s. Not tested live.
7. **`--disallowedTools Bash`** (the flag that should really fence a Claude Code patch session) was not tried.
8. **A symlink swapped in between the path check and the write** (a race) is not tested; the check runs once before
   `mkdir` and once after, not at the moment of writing.

## Not claiming

- That the agent finds the jobs I *should* apply to. The rule is a filter I wrote, and its recall was never measured.
- That the three adapters handle every board on those systems. I tested five real boards.
- That the permission policy would stop a *model* that wants to escape. There is no model inside the loop. The policy
  limits this program's own code paths.
- That two runs a day apart are "monitoring". There is no scheduler; I ran it by hand twice.

## Driver's seat

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence |
|---|---|---|---|---|
| **The loop** | Write the loop, the adapters, the budget and exit code, the trace, and the tests; replay seeded runs; point out traps it finds (stale Lectern note, empty-200) | Decide the exits, budgets, retry policy and approval rule **before** code; run the live runs; read the trace | A budget is a promise about how hard I hit someone else's server, and "finished" is a claim about what I'll rely on. Those are my commitments, and Claude would just pick defaults | GATE.md committed alone (`61c093d`) before code (`0cd07c7`); my chat answers 2026-11-09; my day-1 run output in TRACE.md §1 |
| **The review** | Write the patch from a fixed prompt; extract what it actually did (diff, tool calls); explain the diff as behavior | Decide what the fix must and must not do (Intern/Internship only, whole-word); commit the test before the patch; run the tests myself; accept/revise/reject | The model that wrote the patch also read my test (its `grep`), so it cannot be the one that says it passes. And the rule decides which jobs my persona sees | `fdae00e` (test) before `6e69b42` (prompt) before `8449968` (patch); `patch_session_tool_calls.md` rows 2–3, 8; my decision quoted in REVIEW_PACKET.md §5 |

## Signed or withheld

Signed or withheld: ____________ (name, date)
