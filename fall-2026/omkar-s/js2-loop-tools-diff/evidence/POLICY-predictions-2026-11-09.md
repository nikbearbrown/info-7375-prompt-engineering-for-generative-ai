# Permission policy and boundary tests

The policy is in GATE.md §5. It is enforced in `agent/policy.py`, and the loop cannot reach the network or the disk except through it (see *How the program is forced through the policy*, below).

## Boundary cases: predicted before the policy code existed

**The "Predicted" column was written on 2026-11-09, before `agent/policy.py` existed.** A frozen copy of this table as first written is `evidence/POLICY-predictions-2026-11-09.md`, and its sha256 and time are in `evidence/TIMELINE.md`. The "Actual" column was filled in later from the test run; that run's output is saved in `evidence/test-runs/`.

Paths are relative to the assignment folder. `runs/` is the output folder.

| # | Kind | Request | Predicted (and why) | Test |
|---|---|---|---|---|
| B1 | network, allowed | `GET https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | **ALLOW**: exact host on the allow-list, https, GET | `test_B01_allowed_host_get` |
| B2 | network, **host off the allow-list** | `GET https://www.linkedin.com/jobs/view/1` | **DENY**: host is not on the list | `test_B02_host_off_allow_list` |
| B3 | network, suffix trick | `GET https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs` | **DENY**: the host *contains* an allowed name but is not equal to it | `test_B03_suffix_trick_host` |
| B4 | network, userinfo trick | `GET https://boards-api.greenhouse.io@evil.example/v1/boards/x/jobs` | **DENY**: the real host is `evil.example`, and the URL carries credentials | `test_B04_userinfo_trick` |
| B5 | network, scheme | `GET http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs` | **DENY**: http, not https | `test_B05_plain_http` |
| B6 | network, port | `GET https://api.ashbyhq.com:8443/posting-api/job-board/linear` | **DENY**: port other than 443 | `test_B06_non_443_port` |
| B7 | network, **write-like method** | `POST https://api.lever.co/v0/postings/spotify/<id>/apply` | **DENY**: only GET is allowed. This is what "apply" would be. | `test_B07_post_is_denied` |
| B8 | network, credentials | `GET` an allowed URL with an `Authorization` header | **DENY**: the agent never sends credentials | `test_B08_auth_header_denied` |
| B9 | network, redirect | allowed URL answers `302 Location: https://evil.example/` | **DENY / refused**: the redirect is not followed | `test_B09_redirect_refused` |
| B10 | **read** request | read `config/watchlist.json` | **ALLOW**: reading inside the assignment folder | `test_B10_read_inside_folder` |
| B11 | **write** request, same file as B10 | write `config/watchlist.json` | **ASK**, and with no approver it is **not written**. The budget and watch list change only by a written decision. | `test_B11_write_config_needs_approval` |
| B12 | write, approval **granted** | same as B11, approver says yes | **ALLOW** (the approval is recorded in the decision) | `test_B12_write_config_approved` |
| B13 | write, allowed | write a new file `runs/r1/raw/greenhouse-klaviyo-a1.json` | **ALLOW** | `test_B13_new_file_in_runs` |
| B14 | write, **`..` escape** | write `runs/../GATE.md` | **DENY**: it resolves outside `runs/` | `test_B14_dotdot_escape` |
| B15 | write, **prefix trick** | write `runs-evil/x.json` (sibling folder whose name starts with `runs`) | **DENY**: `runs-evil` is not inside `runs` (component check, not string prefix) | `test_B15_prefix_trick_sibling` |
| B16 | write, **symlink** | `runs/link` is a symlink to a temp folder outside; write `runs/link/x.json` | **DENY**: the real path is outside `runs/` | `test_B16_symlink_escape` |
| B17 | write, overwrite evidence | write over an existing `runs/r1/raw/…json` | **ASK**: raw responses are append-only evidence; not written without approval | `test_B17_overwrite_raw_needs_approval` |
| B18 | write, state file | overwrite the existing `runs/state/klaviyo.state.json` | **ALLOW**: the one file the loop must update every run | `test_B18_state_file_overwrite_allowed` |
| B19 | write, absolute path | write `/tmp/x.json` | **DENY** | `test_B19_absolute_outside` |
| B20 | read, outside the folder | read `~/.ssh/id_rsa` | **DENY** | `test_B20_read_outside_folder` |
| B21 | forbidden action | `apply`, `email`, `message`, `login`, **even with an approver that says yes** | **DENY** for all four; approval cannot unlock them | `test_B21_forbidden_actions_never_allowed` |

That is 21 cases, against a minimum of 10. Every category the assignment names is covered: off-allow-list host (B2–B4), `..` (B14), prefix trick (B15), symlink (B16), read vs write (B10 vs B11), and a write that needs approval (B11, B12, B17).

## How the program is forced through the policy

- `agent/transport.py` is the only module that opens a network connection. Its `get()` calls `policy.check_request()` first and raises `PolicyDenied` on anything but ALLOW. Its opener has a redirect handler that raises instead of following.
- `agent/store.py` is the only module that writes files. Every write calls `policy.check_write()` first. It opens files with `O_NOFOLLOW` (or `O_EXCL` for evidence), so a symlink swapped in after the check is not followed either.
- `tests/test_policy_boundary.py::test_no_other_module_opens_network_or_writes` scans the source and fails if any other module in `agent/` imports `urllib.request`, `socket` or `http.client`, or calls `open(` in write mode.
