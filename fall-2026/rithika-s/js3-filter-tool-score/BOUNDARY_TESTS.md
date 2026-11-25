# Boundary tests — permission policy (GATE.md section 5)

Predictions written and committed before any policy code existed.
"Actual" is filled in only from a test run I performed myself.

| ID | Request | Kind | Predicted | Reason (GATE §5) | Test name | Actual |
|---|---|---|---|---|---|---|
| B01 | GET `https://boards-api.greenhouse.io/v1/boards/scaleai/jobs` | network | ALLOW | On allow-list, HTTPS, GET | test_B01_greenhouse_get_allowed | PASS, as predicted (run by me, 2026-11-10) |
| B02 | GET `https://api.ashbyhq.com/posting-api/job-board/openai` | network | ALLOW | On allow-list, HTTPS, GET | test_B02_ashby_get_allowed | PASS, as predicted (run by me, 2026-11-10) |
| B03 | GET `https://example.com/jobs` | network | REFUSE `host_not_allowed` | Host off the allow-list | test_B03_host_off_allowlist_refused | PASS, as predicted (run by me, 2026-11-10) |
| B04 | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs` | network | REFUSE `host_not_allowed` | Exact host match, not "ends with" (W7) | test_B04_lookalike_host_refused_exact_match | PASS, as predicted (run by me, 2026-11-10) |
| B05 | GET `http://boards-api.greenhouse.io/v1/boards/scaleai/jobs` | network | REFUSE `not_https` | HTTPS only | test_B05_http_refused | PASS, as predicted (run by me, 2026-11-10) |
| B06 | POST to `https://boards-api.greenhouse.io/v1/boards/scaleai/jobs` | network | REFUSE `method_not_allowed` | GET only; no submitting or applying | test_B06_post_refused | PASS, as predicted (run by me, 2026-11-10) |
| B07 | GET allowed URL with an `Authorization` header | network | REFUSE `credentials_not_allowed` | Never log in | test_B07_authorization_header_refused | PASS, as predicted (run by me, 2026-11-10) |
| B08 | Allowed host redirects to `https://example.com/` | network | REFUSE `redirect_off_allowlist` | Redirect off the allow-list | test_B08_redirect_off_allowlist_refused | PASS, as predicted (run by me, 2026-11-10) |
| B09 | Write `out/raw/<run>_scaleai_a1.json` | write | ALLOW | Inside `out/` | test_B09_write_raw_inside_out_allowed | PASS, as predicted (run by me, 2026-11-10) |
| B10 | Write `out/../data/resume.example.json` | write | REFUSE `path_outside_write_area` | `..` resolves outside `out/` | test_B10_dotdot_out_of_out_refused | PASS, as predicted (run by me, 2026-11-10) |
| B11 | Write `out-evil/x.json` | write | REFUSE `path_outside_write_area` | Prefix trick: compared by path components (W8) | test_B11_prefix_trick_out_evil_refused | PASS, as predicted (run by me, 2026-11-10) |
| B12 | Write `out/link/x.json`, where `out/link` is a symlink to a folder outside the project | write | REFUSE `path_outside_write_area` | Symlink resolved before checking (W8) | test_B12_symlink_out_of_project_refused | PASS, as predicted (run by me, 2026-11-10) |
| B13 | Read `data/resume.example.json` | read | ALLOW | `data/` is readable | test_B13_read_data_allowed | PASS, as predicted (run by me, 2026-11-10) |
| B14 | Write `data/resume.example.json` | write | REFUSE `path_outside_write_area` | Same file as B13: readable is not writable | test_B14_write_data_refused | PASS, as predicted (run by me, 2026-11-10) |
| B15 | Read `/etc/passwd` | read | REFUSE `path_outside_read_area` | Outside every read folder | test_B15_read_etc_passwd_refused | PASS, as predicted (run by me, 2026-11-10) |
| B16 | Write `out/raw/<run>_scaleai_a1.json` when it already exists | write | REFUSE `would_overwrite` | Evidence is never overwritten | test_B16_existing_raw_never_overwritten | PASS, as predicted (run by me, 2026-11-10) |
| B17 | Reset `out/state/scaleai.json`, approver answers yes | approval | ALLOW | My approval given for this action | test_B17_reset_with_yes_allowed | PASS, as predicted (run by me, 2026-11-10) |
| B18 | Reset `out/state/scaleai.json`, approver answers no | approval | REFUSE `approval_denied` | I said no | test_B18_reset_with_no_refused | PASS, as predicted (run by me, 2026-11-10) |
| B19 | Reset `out/state/scaleai.json`, no one to answer | approval | REFUSE `approval_denied` | Default is no (W9) | test_B19_reset_with_no_one_to_answer_refused | PASS, as predicted (run by me, 2026-11-10) |

## Added after the build

B20 was added on 2026-11-10 after Claude Code's build summary showed that B04
does not catch an "ends with" host check. Prediction written before I ran it.

| ID | Request | Kind | Predicted | Reason (GATE §5) | Test name | Actual |
|---|---|---|---|---|---|---|
| B20 | GET `https://evilboards-api.greenhouse.io/v1/boards/x/jobs` | network | REFUSE `host_not_allowed` | Exact host match; "ends with" would let this through (W7) | test_extra_host_suffix_trick_refused | PASS, as predicted (run by me, 2026-11-10) |
