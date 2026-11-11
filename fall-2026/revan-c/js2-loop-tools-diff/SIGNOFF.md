# Sign-off — Job-Search Agent 2

**Checked**

- **Network allow-list:** exact host, exact URL, GET only, no redirects followed. `test_B01`–`test_B07`, including the look-alike host (`test_B03a`).
- **Write containment:** `..`, the `runs/js2-evil` prefix trick, and symlinks. `test_B08_dotdot_escape_denied`, `test_B09_sibling_prefix_denied`, `test_B10_symlink_escape_denied`.
- **Read versus write, and approval:** `test_B11`–`test_B14`.
- **Exits:**
  - `finished`: `test_finished_run_reports_what_the_gate_requires`
  - `incomplete`: `test_deliberate_404_is_labeled_first_recorded_and_kept`, `test_failed_board_records_actual_error_never_zero`
  - `budget-exhausted`: `test_B16`, `test_request_budget_refused_before_sending`, `test_overrun_during_a_request_is_budget_exhausted_not_finished`
  - `error`: `test_B15`, `test_duplicate_url_in_selection_is_preflight_error_with_no_request`, `test_state_write_failure_is_error_and_trace_says_so`
- **Empty board never "no new jobs":** `test_empty_board_is_incomplete_never_no_new_jobs`.
- **State never advances after failure or without approval:** `test_state_bytes_unchanged_after_incomplete_run_even_with_approval`, `test_state_bytes_unchanged_after_observation_only_run`.
- **Each GATE.md wrong version is caught:** `tools/check_wrong_versions_js2.py`, 17 of 17.
- **The finished-wrong answer is caught by an independent check:** `test_js1_style_empty_board_reported_as_no_new_is_caught`, and my run of README steps 1–3.
- **The review-packet change:** `test_lever_workplace_type_controls_remote_location`.

**How**

- **By tests written before the JS2 implementation:** Claude wrote the tests from my GATE.md (`e7493d7`, before `ac2827a`). I ran the full suite and compared the named boundary results with my predictions, but did not read every assertion closely.
- **By a test committed before Claude's patch:** `test_lever_workplace_type_controls_remote_location` was committed before `06e9257` and failed on the remote case before the patch.
- **By hand:** I read the eight-line Lever parser diff, inspected the saved Patch My PC fields with `jq`, and read the traces for the DNS failure and Patch My PC timeout.
- **By recomputation:** I ran the independent checker against saved raw responses; it recounted each selected board and caught JS1's finished-wrong empty-board result.
- **With Claude's help:** Claude wrote the JS2 tests and implementation, pointed out the Lever remote-location defect, wrote the narrow parser patch, and checked my documents for inaccurate wording.

**Not checked** (at least three real items)

- **Slow responses and the full 45-second deadline.** One live Patch My PC request did time out after 8 seconds, but the deadline and slow-stream cases were tested only with a fake clock. `http.client`'s timeout applies to each socket operation, so a server that trickles bytes could hold one request past 8 seconds. A live redirect or 5xx was never observed.
- **A race between the path check and the write.** `O_EXCL | O_NOFOLLOW` guards the final path component, but a parent directory swapped for a symlink between check and open was not tested.
- **Whether an empty board is really empty.** The independent check works only from saved bytes. It cannot tell an empty board from a moved one (Webflow), and it was never run against a second source.
- **The relevance verdicts.** They come from JS1's rule. The Lever remote case shows the rule input can be wrong per provider, and the other provider mappings were not reviewed posting by posting.
- **Terms of use** for each board, beyond reading the public API documentation.

**Not claiming**

- **That this is an LLM agent.** The loop is deterministic; no model chooses actions.
- That the three boards represent the job market, or that any posting is a match.
- That a `finished` run means no new jobs exist anywhere.
- That the policy is safe against an attacker with write access to this repository.

**Signed :** Revan C. November 10, 2026.

## Driver's seat

| Part of the task | What Claude did | What I did | Why that part stays mine | Evidence |
|---|---|---|---|---|
| The gate | Reviewed my draft and pointed out gaps | Wrote GATE.md and made every decision in it | Budgets, permissions, and exits are policy; an agent must not set its own limits | `f3072e5` |
| The loop and the policy code | Wrote the tests from the gate, then the code | I checked it by running the traces, the independent check, all the tests, and the 17 broken copies. I did not read every line. | I answer for how it behaves | `e7493d7`, `ac2827a` |
| Runs | Ran scratch checks outside the repository | Ran the submitted normal run, deliberate-failure run, and finished-wrong demo in my terminal | The trace is my record | `d7f1508`, `runs/js2/`, `review_evidence/post_patch_commands.txt` |
| The review | Pointed out the defect and wrote patch `06e9257` | Reproduced it with pre-patch code, committed the failing test before the patch, read the diff, and accepted the change | Accepting a change is a judgment under my name | REVIEW_PACKET.md |
| Sign-off | Drafted this page | I checked every line and fixed or removed anything untrue. | The signature is mine alone | this file |
