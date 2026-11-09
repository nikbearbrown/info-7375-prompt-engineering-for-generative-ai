# Boundary cases — my predictions, written BEFORE any test or code existed
Anisha Gaikar · 2026-11-09 ~3:13 pm · My words, copied unchanged from my chat answer. Each case is one test in `tests/test_policy.py`; the test's name is shown.

| # | Case | My prediction (before running) | Test |
|---|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs` | allowed — Public listings on the approved Greenhouse host. | `test_01_greenhouse_get_allowed` |
| 2 | GET `https://api.lever.co/v0/postings/palantir?mode=json` | allowed — Public listings on the approved Lever host. | `test_02_lever_get_allowed` |
| 3 | GET `https://api.ashbyhq.com/posting-api/job-board/acme` | blocked — Ashby is outside my allowlist. | `test_03_ashby_blocked` |
| 4 | GET `https://boards-api.greenhouse.io.evil.com/...` (look-alike host) | blocked — The look-alike hostname fails the exact match. | `test_04_lookalike_host_blocked` |
| 5 | GET `https://boards-api.greenhouse.io@evil.com/...` | blocked — The actual host is evil.com. | `test_05_userinfo_trick_blocked` |
| 6 | POST to `https://boards-api.greenhouse.io/...` | blocked — I only allow GET requests for public listings. | `test_06_post_blocked` |
| 7 | GET `http://boards-api.greenhouse.io/...` | blocked — I require HTTPS for both approved hosts. | `test_07_plain_http_blocked` |
| 8 | Allowed URL redirects to `https://evil.com/` | blocked — The initial request is allowed, but the agent must block and report the redirect to evil.com before following it. | `test_08_redirect_off_allowlist_blocked` |
| 9 | Write new `reports/job-watch/run-1.json` | allowed — It creates a new report inside reports/job-watch/. | `test_09_new_report_allowed` |
| 10 | Write `reports/job-watch/../../agent.py` | blocked — The resolved path escapes the report folder. | `test_10_dotdot_escape_blocked` |
| 11 | Write `reports/job-watch-evil/x.json` | blocked — A similar folder name does not count as being inside reports/job-watch/. | `test_11_prefix_trick_blocked` |
| 12 | Write via symlink `reports/job-watch/link/` → outside | blocked — The symlink resolves to a location outside the report folder. | `test_12_symlink_escape_blocked` |
| 13 | Write `/etc/x.json` | blocked — /etc/x.json is outside the report folder. | `test_13_absolute_path_blocked` |
| 14 | Overwrite existing report, no approval | ask me — The agent needs my approval before overwriting an existing report. | `test_14_overwrite_needs_approval` |
| 15 | Same overwrite, with approval | allowed — I approved this specific overwrite inside the report folder. | `test_15_overwrite_with_approval_allowed` |
| 16 | Read an existing report in `reports/job-watch/` | allowed — The agent can read an existing report in the report folder. | `test_16_read_report_allowed` |
| 17 | Delete a report in `reports/job-watch/` | blocked — The agent must never delete reports. | `test_17_delete_blocked` |

Boards (my choice, live status unverified before the first run): Greenhouse `klaviyo`, Greenhouse `datadog`, Lever `palantir`, and Greenhouse `no-such-board-7375` as the deliberate failure.
