# Permission policy and boundary tests
The policy is **enforced in code**, not in a prompt: `watcher/policy.py`.
- **Network:** every request goes through `check_request` first.
- **Redirects:** every redirect goes through `PolicyRedirectHandler`.
- **Files:** every write goes through `check_write`, inside `Store.write`.

My rules for it are in GATE.md section 5.

| Rule (GATE 5) | Where it's enforced |
|---|---|
| GET only, HTTPS only, exact host `boards-api.greenhouse.io` or `api.lever.co`, no `user@host` trick | `Policy.check_request` |
| Only public job-list paths; apply, login and message paths are refused even with GET (never-list 5b) | `ALLOWED_PATHS` + `check_request` |
| A redirect is checked **before** it's followed; allowed redirects return to the loop and count as requests (my 15-cap decision) | `PolicyRedirectHandler`, `loop.run` |
| Writes only inside `reports/job-watch/`, resolved through `..` and symlinks (the folder itself mustn't be a symlink) | `Policy.check_write` / `_inside` / `_root_ok` |
| Overwriting needs approval, for that one file | `check_write(path, approved=<that path>)`, plus the prompt in `watch.py` |
| Never delete | `Policy.check_delete` always refuses |

## Boundary cases: predicted before any test or code existed, then run
Predictions are from `PREDICTIONS.md`. The cases were chosen and the predictions written on 2026-11-09 at ~3:13 pm; ChatGPT helped word them (see the note in that file). Row 18 is a test that was kept by my decision at ~3:23 pm. "Actual" is the result of running the named test on my Mac on 2026-11-10 (`logs/23_all_tests_after_patch.txt`: 66 tests, OK).

| # | Case | Predicted | Actual | Test (`tests/test_policy.py`) |
|---|---|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs` | allowed | allowed ✔ | `test_01_greenhouse_get_allowed` |
| 2 | GET `https://api.lever.co/v0/postings/palantir?mode=json` | allowed | allowed ✔ | `test_02_lever_get_allowed` |
| 3 | GET `https://api.ashbyhq.com/posting-api/job-board/acme` | blocked | blocked ✔ | `test_03_ashby_blocked` |
| 4 | GET `https://boards-api.greenhouse.io.evil.com/...` (look-alike host) | blocked | blocked ✔ | `test_04_lookalike_host_blocked` |
| 5 | GET `https://boards-api.greenhouse.io@evil.com/...` | blocked | blocked ✔ | `test_05_userinfo_trick_blocked` |
| 6 | POST to `https://boards-api.greenhouse.io/...` | blocked | blocked ✔ | `test_06_post_blocked` |
| 7 | GET `http://boards-api.greenhouse.io/...` | blocked | blocked ✔ | `test_07_plain_http_blocked` |
| 8 | Allowed URL redirects to `https://evil.com/` | blocked | blocked ✔ | `test_08_redirect_off_allowlist_blocked` |
| 9 | Write new `reports/job-watch/run-1.json` | allowed | allowed ✔ | `test_09_new_report_allowed` |
| 10 | Write `reports/job-watch/../../agent.py` | blocked | blocked ✔ | `test_10_dotdot_escape_blocked` |
| 11 | Write `reports/job-watch-evil/x.json` | blocked | blocked ✔ | `test_11_prefix_trick_blocked` |
| 12 | Write via symlink `reports/job-watch/link/` → outside | blocked | blocked ✔ | `test_12_symlink_escape_blocked` |
| 13 | Write `/etc/x.json` | blocked | blocked ✔ | `test_13_absolute_path_blocked` |
| 14 | Overwrite existing report, no approval | ask me | ask ✔ | `test_14_overwrite_needs_approval` |
| 15 | Same overwrite, with approval | allowed | allowed ✔ | `test_15_overwrite_with_approval_allowed` |
| 16 | Read an existing report in `reports/job-watch/` | allowed | allowed ✔ | `test_16_read_report_allowed` |
| 17 | Delete a report in `reports/job-watch/` | blocked | blocked ✔ | `test_17_delete_blocked` |
| 18 | GET an *application* URL on an allowed host (`.../jobs/1/applications`) — added after the freeze | blocked | blocked ✔ | `test_never_apply_path_blocked_even_with_get` |

**18 of 18 matched my prediction.**

Extra edge cases came from the two reviewers (`tests/test_review_fixes.py`):
- a bad port;
- approval being for one specific file;
- the report folder itself as a target;
- the **report folder itself symlinked outside** (checked through the real writer, and no outside file is created);
- board names with capitals or `_`.

All of them failed before the fixes (`logs/04`) and pass after (`logs/03`, `logs/23`).
