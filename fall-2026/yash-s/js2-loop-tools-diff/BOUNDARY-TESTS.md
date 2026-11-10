# Job-Search Agent 2 — Boundary Test Predictions

**Date:** 2026-11-09  
**Status:** Predictions before implementation and testing

## Purpose

I want to test whether my agent follows its permission policy.

The permission checks must happen in Python code, not just in Claude's prompt.

I am writing these expected results before Claude Code implements the permission checker.

The actual results will be recorded after I run the tests.

## My Predicted Results

| # | Test case | My expected result | Why |
|---|---|---|---|
| 1 | HTTPS request to `boards-api.greenhouse.io` | Allow | This is an approved host using HTTPS. |
| 2 | HTTPS request to `api.ashbyhq.com` | Allow | This is the second approved ATS host. |
| 3 | Request to `example.com` | Refuse | The host is not on my allow-list. |
| 4 | Request to `boards-api.greenhouse.io.evil.com` | Refuse | The hostname only looks similar to an approved host. |
| 5 | HTTP request to `boards-api.greenhouse.io` | Refuse | My policy allows HTTPS only. |
| 6 | Write a new evidence file inside the approved `runs/` folder | Allow | This is a normal evidence write in the correct folder. |
| 7 | Write to `runs/../outside.json` where the resolved path escapes `runs/` | Refuse | The path uses `..` to reach outside the approved folder. |
| 8 | Write to `runs-evil/output.json` beside `runs/` | Refuse | A folder with a similar prefix is not the same approved folder. |
| 9 | Write through a symlink in `runs/` that points outside | Refuse | The resolved destination is outside the permitted directory. |
| 10 | Read the fictional resume from `persona/` | Allow | The agent needs to read the fictional resume for matching. |
| 11 | Write to the resume file in `persona/` | Refuse | Reading a file does not mean the program can modify it. |
| 12 | Reset an existing state file without my approval | Refuse | State resets require explicit approval. |
| 13 | Reset an existing state file with my explicit approval and within the approved state folder | Allow | The policy permits this specific action after approval and validation. |
| 14 | Follow an HTTPS redirect to an unapproved host | Refuse | An allowed starting URL must not bypass the host restrictions. |
| 15 | Write to an absolute path outside the approved output folder | Refuse | An absolute path outside the permitted directory must not bypass the path policy. |

These predictions apply to the permission checker. An "Allow" result means the action is permitted by the policy, not that a live network request is guaranteed to succeed.

## How I Will Test Them

I will ask Claude Code to implement these checks as automated tests.

For network permissions, the tests should use constructed URLs and mocked requests so I can check host restrictions without contacting external websites.

For filesystem permissions, the tests should create temporary folders and files.

The tests should use actual paths, including a sibling folder and a symbolic link, to verify that the program checks the resolved destination.

For approval tests, the tests should verify that an explicit approval is required for a restricted state operation.

I will run the tests myself and compare the results with this prediction table.

## What I Will Record After Testing

After I run the tests, I will add a results section with:

- The actual result for each case
- Whether it matched my prediction
- The test name
- Any failure or unexpected behavior
- What Claude changed after the tests
- The commit containing the tested implementation

I will not change the original predictions after seeing the results.

## Wrong Versions

I also want the tests to catch at least two intentionally incorrect implementations.

My planned wrong versions are:

1. A failed board is treated as a successful board with zero new postings.
2. A path checker uses string prefixes and incorrectly permits `runs-evil/`.
3. A repeated request does not count toward the request budget.

I want to save a reproducible check for these wrong versions and rerun it after code changes.

This addresses the feedback I received on Job-Search Agent 1 about rerunning planted-bug checks.

## Results After Testing (added 2026-11-10)

My predictions above are unchanged. These results come from my own test runs: all 63 tests passed before the live run, and all 65 passed after the review patch, saved in `review/tests-after-patch.txt` at 2026-11-10T03:49Z. I ran them with Python 3.13.5; Claude also ran the suite with Python 3.9.6. The tested permission code is `policy.py` from commit `841dbce`, and it has not changed since.

| # | Test case | My prediction | Actual result | Matched? | Test in `tests/test_policy.py` |
|---|---|---|---|---|---|
| 1 | HTTPS request to `boards-api.greenhouse.io` | Allow | Allow | yes | `Network.test_01_https_greenhouse_allowed` |
| 2 | HTTPS request to `api.ashbyhq.com` | Allow | Allow | yes | `Network.test_02_https_ashby_allowed` |
| 3 | Request to `example.com` | Refuse | Refuse | yes | `Network.test_03_host_off_the_allow_list_refused` |
| 4 | Request to `boards-api.greenhouse.io.evil.com` | Refuse | Refuse | yes | `Network.test_04_look_alike_host_refused` |
| 5 | HTTP request to `boards-api.greenhouse.io` | Refuse | Refuse | yes | `Network.test_05_plain_http_refused` |
| 6 | Write a new evidence file inside `runs/` | Allow | Allow | yes | `Files.test_06_write_inside_runs_allowed` |
| 7 | Write to `runs/../outside.json` | Refuse | Refuse, and no file was created | yes | `Files.test_07_dot_dot_escape_refused` |
| 8 | Write to `runs-evil/output.json` | Refuse | Refuse, and no file was created | yes | `Files.test_08_look_alike_folder_prefix_refused` |
| 9 | Write through a symlink in `runs/` that points outside | Refuse | Refuse, for both a symlinked folder and a symlinked file; nothing was written outside | yes | `Files.test_09_symlink_pointing_outside_refused` |
| 10 | Read the fictional résumé from `persona/` | Allow | Allow | yes | `Files.test_10_read_the_persona_allowed` |
| 11 | Write to the résumé file in `persona/` | Refuse | Refuse, as both an evidence write and a state write; the file is unchanged | yes | `Files.test_11_write_the_persona_refused` |
| 12 | Reset a state file without my approval | Refuse | Refuse; the state file still exists | yes | `Files.test_12_reset_state_without_approval_refused` |
| 13 | Reset a state file with my approval, inside `state/` | Allow | Allow; the state file was removed | yes | `Files.test_13_reset_state_with_approval_allowed` |
| 14 | Follow an HTTPS redirect to an unapproved host | Refuse | Refuse | yes | `Network.test_14_redirect_refused` and `Network.test_14_http_get_installs_the_redirect_refusal` |
| 15 | Write to an absolute path outside the output folder | Refuse | Refuse, and no file was created | yes | `Files.test_15_absolute_path_outside_refused` |

**All 15 matched my predictions.** None of them failed or behaved unexpectedly.

**What these tests do not show:**
- **#14** is tested at the redirect handler: the handler refuses, and the real `http_get` installs it. No real server sent a redirect during my tests or my live run.
- The network tests check URLs **without making requests**. The live run is the only real network evidence, and it contacted only the two allowed hosts.
- The folder checks run on macOS with real temporary folders and symlinks. A race, where a symlink appears between the check and the write, was not tested.

**Extra tests I did not predict in advance.** Claude added these beyond my 15 cases; they also pass:
- `test_extra_user_part_trick_refused`
- `test_extra_other_port_refused`
- `test_extra_post_refused`
- `test_off_list_url_refused_before_any_network`
- `test_extra_approval_never_allows_a_path_outside_the_state_folder`
- `test_extra_approval_must_be_exactly_true`
- `test_extra_evidence_is_create_only`
- `test_extra_read_outside_allowed_folders_refused`
- `test_extra_state_only_inside_the_state_folder`
- `test_extra_run_folders_are_never_reused`

**What Claude changed after the tests:** nothing in the permission code. The only change after testing was the review patch to `agent.py`, which changes how counts are reported, not the policy (see `review/REVIEW-PACKET.md`).

**Wrong versions.** `wrong_versions.py` plants each of my three wrong versions. After the patch it reported all three caught (`review/wrong-versions-after-patch.txt`). The permission-related one, WV2 (a string-prefix folder check), is caught by `test_08_look_alike_folder_prefix_refused`.
