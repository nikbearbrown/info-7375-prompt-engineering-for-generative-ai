# Permission policy and boundary tests — Job-Search Agent 2 (nishant-u)

The policy is enforced in code (`agent2/policy.py`), not in a prompt. Every network call and every file
write the loop makes goes through `Policy`, which raises `PolicyRefused` (a `PermissionError`) for
anything outside it. It is a preflight plus the write itself, not an operating-system sandbox.

## The policy, as written in GATE.md

From `GATE.md`, written before any code (commit `58d6431`):

- **Hosts (read only, GET):** boards-api.greenhouse.io, api.ashbyhq.com. Anything else is refused before any network call, including after a redirect.
- **Operations:** `fetch` (GET an allowed host), `write_run_file` (inside the output root), `update_state` (merge new IDs into the state file inside the output root), `reset_state` (replace the state file). Anything else is refused.
- **Containment:** writes only inside the output root, judged by the resolved path (resolve() and is_relative_to()), never a string prefix. `..` traversal, a sibling prefix like `out-evil` beside `out`, and a symlink pointing outside are refused.
- **Approval:** `reset_state` needs approval, which means approved is the boolean True; anything else ("yes", 1, missing) is refused. Approval never overrides the host or containment rules.
- **Never:** apply, email, message anyone, log in, POST, or delete anything.

### Amendments that change the policy

Before any code (commit `c5ee0fe`):

> 2. Add operation read_file (inside the output root; containment applies). Boundary case 9 is a read_file, predicted allowed.
> 3. update_state is a merge: it may only add IDs and must never drop one. Replacing the set is reset_state, which needs approval. Wrong version 6: an update_state that replaces the whole set instead of merging. New boundary case 15: update_state that would drop an existing ID → refused.

After implementation (commit `d5640de`), decisions Claude Code made while implementing, reviewed and
accepted by me. These are the ones that touch the policy:

> 1. **Request URLs:** only `https` is accepted, and URLs containing a username or password are refused. The gate only names hosts.
> 4. **Refused or repeated boards:** a board refused by the policy or by the repeat rule counts against the board budget and makes the run `incomplete`.
> 6. **Redirects:** a redirect is checked again, up to 3 hops. Each redirect hop does not count as a separate request against the budget.
> 7. **Claude judge (`--claude`):** it runs only on Greenhouse postings. Ashby postings are marked "not run" because the JS1 validator requires integer IDs. JS1's `claude_judge` writes its own files inside a folder the policy approved, but those individual writes don't go through `policy.py`.

So the operation vocabulary in code is exactly `fetch`, `read_file`, `write_run_file`, `update_state` and
`reset_state`, and the allow-list is exactly the two hosts (`PolicyExtras` in `tests/test_js2_policy.py`).

## Boundary tests

Predictions are copied from GATE.md, written before any code: cases 1–14 in `58d6431`, and case 15 plus
case 9's operation in the amendment `c5ee0fe`. The tests are in `tests/test_js2_policy.py`, committed in
`e666f6e` before the implementation (`5e3e3d0`). The results are from the full suite at the final commit,
run on Windows 11 with Python 3.12.10.

| # | Case (GATE.md) | Predicted (GATE.md) | Test | Result | Note |
|---|---|---|---|---|---|
| 1 | fetch https://boards-api.greenhouse.io/... | allowed | `test_case_01_greenhouse_fetch_allowed` | pass | Returns the host. |
| 2 | fetch https://api.ashbyhq.com/... | allowed | `test_case_02_ashby_fetch_allowed` | pass | Returns the host. |
| 3 | fetch https://api.lever.co/... (not on the list) | refused before any request | `test_case_03_lever_refused_before_any_request` | pass | A spy opener received 0 requests. It also checks two lookalike hosts: `boards-api.greenhouse.io.evil.example` and `boards-api.greenhouse.io@evil.example`. |
| 4 | fetch an allowed host that redirects to evil.example | refused, no request to evil.example | `test_case_04_redirect_to_evil_refused_without_requesting_it` | pass | The opener saw only the Greenhouse request. |
| 5 | write out/runs/r1/raw.json | allowed | `test_case_05_write_inside_runs_allowed` | pass | Checks the resolved path and the bytes written. |
| 6 | write out/../escape.txt | refused (traversal) | `test_case_06_traversal_refused` | pass | No file is created outside. |
| 7 | write out-evil/x.txt (sibling prefix) | refused | `test_case_07_sibling_prefix_refused` | pass | Both the absolute path and `../out-evil/x.txt`. |
| 8 | write out/link/x.txt where link points outside out | refused (outside-pointing link) | `test_case_08_outside_pointing_symlink_refused` | **skip** | Windows refused to create the symlink (WinError 1314, privilege not held), so this case has not run on this machine. A one-off directory-junction check, which needs no privilege, refused the write and nothing reached the outside folder, but it is not a committed test. |
| 9 | read out/state/seen_ids.json | allowed (read, not write) | `test_case_09_read_file_inside_allowed` | pass | A `read_file` (amendment `c5ee0fe`). |
| 10 | operation "delete" | refused (not in the vocabulary) | `test_case_10_delete_not_in_vocabulary` | pass | Also refused with `approved=True`. |
| 11 | reset_state with approved=True | allowed | `test_case_11_reset_state_with_true_allowed` | pass | The state is replaced exactly. |
| 12 | reset_state with approved="yes" | refused | `test_case_12_reset_state_with_yes_refused` | pass | Also `1`, `None`, `False` and missing. The state is unchanged. |
| 13 | reset_state with approved=True on a path outside out | refused (approval can't override containment) | `test_case_13_approval_cannot_override_containment` | pass | No file is created outside. |
| 14 | a POST to an allowed host | refused | `test_case_14_post_to_allowed_host_refused` | pass | Both `authorize` and `http_get`. 0 requests. |
| 15 | update_state that would drop an existing ID | refused | `test_case_15_update_that_would_drop_an_id_refused` | pass | Also checks that two updates merge, never replace. |

Wrong versions 1 (string-prefix containment), 4 (truthy approval) and 6 (replacing `update_state`) are
policy mutants in `tests/js2_mutants.py`. Each is caught by `tests/test_js2_mutants.py`.

## What the policy does not cover

- **Writes outside `policy.py`:** JS1's `claude_judge` writes inside a folder the policy approved, but
  its individual writes do not go through `policy.py` (accepted decision 7).
- **Check and use:** the check and the later file operation are not one atomic step, and nothing here
  protects against a concurrent change between them.
- **Case 8:** a real symlink has not been tested on this machine.
- **Terms and rate limits:** each host's terms beyond its API docs, and any rate limit, are not checked.
  The budgets (GATE.md) are my own limits.
