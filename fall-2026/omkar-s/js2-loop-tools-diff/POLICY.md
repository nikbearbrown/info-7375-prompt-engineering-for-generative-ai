# Permission policy and boundary tests

The policy is in GATE.md §5. It is enforced in `agent/policy.py`, and the loop cannot reach the network or the disk except through it (see *How the program is forced through the policy*, below).

## Boundary cases: predicted before the policy code existed

**The "Predicted" column was written on 2026-11-09 at 08:01 UTC, before `agent/policy.py` existed.** A frozen copy of this table as first written is `evidence/POLICY-predictions-2026-11-09.md`, and its sha256 and time are in `evidence/TIMELINE.md`. The "Actual" column was filled in later from the test run; that run's output is `evidence/test-runs/2026-11-09T08-29-26Z-FINAL-2.txt`. **All 21 predictions matched; none had to be changed.** Mutants W4 (startswith), W5 (no realpath) and W6 (substring host) are each killed by these boundary tests (`tests/run_mutants.py`).

Paths are relative to the assignment folder. `runs/` is the output folder.

| # | Kind | Request | Predicted (and why) | Test | Actual (final run) |
|---|---|---|---|---|---|
| B1 | network, allowed | `GET https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | **ALLOW**: exact host on the allow-list, https, GET | `test_B01_allowed_host_get` | as predicted ✔ |
| B2 | network, **host off the allow-list** | `GET https://www.linkedin.com/jobs/view/1` | **DENY**: host is not on the list | `test_B02_host_off_allow_list` | as predicted ✔ |
| B3 | network, suffix trick | `GET https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs` | **DENY**: the host *contains* an allowed name but is not equal to it | `test_B03_suffix_trick_host` | as predicted ✔ |
| B4 | network, userinfo trick | `GET https://boards-api.greenhouse.io@evil.example/v1/boards/x/jobs` | **DENY**: the real host is `evil.example`, and the URL carries credentials | `test_B04_userinfo_trick` | as predicted ✔ |
| B5 | network, scheme | `GET http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs` | **DENY**: http, not https | `test_B05_plain_http` | as predicted ✔ |
| B6 | network, port | `GET https://api.ashbyhq.com:8443/posting-api/job-board/linear` | **DENY**: port other than 443 | `test_B06_non_443_port` | as predicted ✔ |
| B7 | network, **write-like method** | `POST https://api.lever.co/v0/postings/spotify/<id>/apply` | **DENY**: only GET is allowed. This is what "apply" would be. | `test_B07_post_is_denied` | as predicted ✔ |
| B8 | network, credentials | `GET` an allowed URL with an `Authorization` header | **DENY**: the agent never sends credentials | `test_B08_auth_header_denied` | as predicted ✔ |
| B9 | network, redirect | allowed URL answers `302 Location: https://evil.example/` | **DENY / refused**: the redirect is not followed | `test_B09_redirect_refused` | as predicted ✔ |
| B10 | **read** request | read `config/watchlist.json` | **ALLOW**: reading inside the assignment folder | `test_B10_read_inside_folder` | as predicted ✔ |
| B11 | **write** request, same file as B10 | write `config/watchlist.json` | **ASK**, and with no approver it is **not written**. The budget and watch list change only by a written decision. | `test_B11_write_config_needs_approval` | as predicted ✔ |
| B12 | write, approval **granted** | same as B11, approver says yes | **ALLOW** (the approval is recorded in the decision) | `test_B12_write_config_approved` | as predicted ✔ |
| B13 | write, allowed | write a new file `runs/r1/raw/greenhouse-klaviyo-a1.json` | **ALLOW** | `test_B13_new_file_in_runs` | as predicted ✔ |
| B14 | write, **`..` escape** | write `runs/../GATE.md` | **DENY**: it resolves outside `runs/` | `test_B14_dotdot_escape` | as predicted ✔ |
| B15 | write, **prefix trick** | write `runs-evil/x.json` (sibling folder whose name starts with `runs`) | **DENY**: `runs-evil` is not inside `runs` (component check, not string prefix) | `test_B15_prefix_trick_sibling` | as predicted ✔ |
| B16 | write, **symlink** | `runs/link` is a symlink to a temp folder outside; write `runs/link/x.json` | **DENY**: the real path is outside `runs/` | `test_B16_symlink_escape` | as predicted ✔ |
| B16b | write, symlink **file** | `runs/evil.json` is a symlink to a file outside | *Added after the predictions (not predicted beforehand):* **DENY**, and the outside file is not created | `test_B16b_symlink_file_planted_at_final_path` | DENY ✔ |
| B17 | write, overwrite evidence | write over an existing `runs/r1/raw/…json` | **ASK**: raw responses are append-only evidence; not written without approval | `test_B17_overwrite_raw_needs_approval` | as predicted ✔ |
| B18 | write, state file | overwrite the existing `runs/state/klaviyo.state.json` | **ALLOW**: the one file the loop must update every run | `test_B18_state_file_overwrite_allowed` | as predicted ✔ |
| B19 | write, absolute path | write `/tmp/x.json` | **DENY** | `test_B19_absolute_outside` | as predicted ✔ |
| B20 | read, outside the folder | read `~/.ssh/id_rsa` | **DENY** | `test_B20_read_outside_folder` | as predicted ✔ |
| B21 | forbidden action | `apply`, `email`, `message`, `login`, **even with an approver that says yes** | **DENY** for all four; approval cannot unlock them | `test_B21_forbidden_actions_never_allowed` | as predicted ✔ |

That is 22 rows: 21 cases predicted before the code, against a minimum of 10, plus B16b, added later and marked as such. Every category the assignment names is covered: off-allow-list host (B2–B4), `..` (B14), prefix trick (B15), symlink (B16), read vs write (B10 vs B11), and a write that needs approval (B11, B12, B17).

## Two honest notes

- **The frozen predictions file already says the "Actual" column would be filled in later.** That sentence was a plan written at 08:01 with the predictions; the column itself did not exist then. The predictions in it are byte-for-byte the "Predicted" column here.
- **`check_action()` (B21) is a guard that nothing calls.** The program contains no apply, email, message or login code at all, so there is nothing for it to stop. The barrier actually enforced on every request is structural: GET only, the exact-host allow-list, and no credential headers (B2–B8). B21 shows that if such an action were ever added and routed through the policy, approval could not unlock it. It does not show more than that.

## How the program is forced through the policy

- `agent/transport.py` is the only module that opens a network connection. Its `get()` calls `policy.check_request()` first and raises `PolicyDenied` on anything but ALLOW. Its opener has a redirect handler that raises instead of following.
- **Reads:** the watch list, budgets and each board's state file are read through `loop._read_json`, which calls `policy.check_read` first. The persona is checked in `main()`. (Until 08:21:36 the state read bypassed the policy; see FRICTIONAL. `test_state_file_symlinked_outside_is_not_read` covers it.)
- **Traced:** since 08:29, every request decision (inside each `observation`), every state-file read and every write appears in `trace.jsonl`, with paths relative to this folder.
- `agent/store.py` is the only module that writes files. Every write calls `policy.check_write()` first. It opens files with `O_NOFOLLOW` (or `O_EXCL` for evidence), so a symlink swapped in after the check is not followed either.
- `tests/test_policy_boundary.py::test_no_other_module_opens_network_or_writes` scans the source and fails if any other module in `agent/` imports `urllib.request`, `socket` or `http.client`, or calls `open(` in write mode.
