# Facts for the JS2 sign-off (collected by Claude)

Shubham writes and signs the sign-off in `README.md`. This file only lists facts and
candidates. Everything below was run by Claude on 2026-11-09 unless it says otherwise; none of it
is yet "checked by Shubham".

## Properties and the tests that check them

| Property (GATE) | Tests | Last result |
|---|---|---|
| Exits and their precedence (§2) | `test_decide_exit` (8 cases), `test_finished_when_every_board_is_ok`, `test_bad_board_name_is_not_retried_and_loop_is_incomplete`, `test_every_board_failed_is_error`, `test_corrupt_state_stops_the_loop_with_error` | pass |
| An empty board is not "no new jobs" (§2) | `test_empty_board_is_failed_not_no_new_jobs`, `test_board_ok_rules` | pass |
| Budgets, checked before spending (§3) | `test_request_budget_stops_before_the_next_board`, `test_request_budget_also_bounds_a_retry`, `test_board_budget`, `test_time_budget`, `test_no_retry_when_time_is_nearly_up` | pass |
| Repeat rule (§4) | `test_same_board_in_other_case_is_fetched_once`, `test_b20_third_get_of_one_url_is_refused` | pass |
| Error policy (§5) | `test_timeout_is_retried_once_then_ok`, `test_5xx_twice_fails_after_one_retry`, `test_4xx_is_never_retried` (404, 429, 400), `test_failed_board_leaves_saved_state_untouched` | pass |
| Permission policy (§6, §7) | `tests/watch/test_policy.py` B01–B19, `test_b07_redirect_off_the_allow_list_fails_the_board`, `test_b20_…`, `test_plan_refused_by_policy_is_error_before_any_fetch` | 38 boundary cases pass (`docs/js2/evidence/boundary-tests.txt`) |
| Wrong versions W1–W9 are caught (§8) | `tests/meta/test_js2_wrong_versions_caught.py` | each killed by its named test |
| Ashby mapping and UUID IDs (§9) | `tests/providers/test_ashby.py` (20 cases), `test_second_run_new_postings_with_deferred_judgments_is_ok` | pass |
| Floor (A2) | `tests/watch/test_floor.py` (7 cases; red on `affcbdd`, green on `8259d8b`) | pass |
| Independent check works on the real runs, and fails an agent that wrongly fails a good board | `tests/test_check_watch.py` | pass |
| Plan ceilings, résumé read, reset token (A3) | `tests/watch/test_plan_policy.py` B21–B27 | 8 cases pass (`docs/js2/evidence/boundary-tests-a3.txt`) |
| Whole suite | `uv run pytest -q` | 1083 passed after the patch; 1093 after the review fixes; 1096 after the second audit (GATE A4); 1099 after the revision (review packet §8) |

Candidates for "Checked … by a test I wrote before reading Claude's code": none yet. Every test
above was written by Claude. If Shubham writes or rewrites a test himself before reading the
code it tests, that is the one to name.

Candidates for "by hand": reading `trace.jsonl` of run 1 against `docs/js2/TRACE.md`; opening
`ramp.com/careers` and the Greenhouse `ramp` response to confirm the wrong board; reading the
patch diff; running `jsa watch reset greenhouse/ramp` and answering the prompt.

Candidates for "by recomputation": `checks/check_watch.py` recomputes counts, new IDs and
sha256 from the raw bytes; `sha256sum` on any raw file against its `.meta.json`.

## Candidate "Not checked" items (real ones)

1. **No live retry.** No board timed out or returned 5xx in any live run; the retry path is
   shown only with constructed responses.
2. **No live budget stop.** Every live run stayed far inside its budget (at most 5 of 10
   requests, under 2 of 180 seconds).
3. **Ashby secondary locations.** The Ashby mapping reads `location` only, not
   `secondaryLocations`. A posting listed in San Francisco *and* Toronto is treated as US-only.
   Not measured on the real boards.
4. **The rule on Ashby text.** No new Ashby posting has been judged by the rule on live data yet
   (run 1 was a baseline). The rule ran on Ashby postings only in constructed tests.
5. **Floors and careers-page facts.** The numbers in `config/watch.toml` and
   `checks/expectations.toml` were recorded by Claude from one morning's counts and page
   fetches.
6. **"First parse only".** Mutation m2 (flooring every parse) passes every test
   (`docs/js2/review/mutations.txt`).
7. **Redirect hops are not budgeted** (amendment A1); none of the planned boards redirects.
8. **Terms of use.** The Greenhouse and Ashby public APIs were used at a few requests per run;
   their terms were not read line by line for this assignment.

## Candidate "Not claiming" items

- That a `FINISHED` loop means the boards are the companies' real boards: only the independent
  check, with hand knowledge, says that, and only for the companies in `expectations.toml`.
- That the floor catches stale boards in general: it catches only a board that falls below a
  number a person wrote down.
- That the policy limits anything outside this program: JS1's `jsa run` launches the `claude`
  executable, whose own network use is not controlled here (the watch loop does not launch it).
- That any posting suits Kiran Joshi: the loop made no model judgments; new postings stay
  `UNAVAILABLE` and pending.
- Anything about Lever or a third job system: not built.
