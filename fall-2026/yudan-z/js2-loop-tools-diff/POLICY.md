# Permission policy and boundary tests

## Executive summary

This page is GATE §6 turned into code and tests. Every network request, file read and file write the agent makes goes through one module, `agent/policy.py`; no prompt is involved.
- The **Predicted** column was written on 2026-11-09 and committed with the tests (`ff7a40c`) before the policy code existed and before any test ran. Claude drafted each prediction from the GATE §6 rules I approved; B19 was added with its GATE revision, also before its code.
- The **Observed** column is filled in only from the actual test output: the full suite I ran myself on 2026-11-09 (`review/07-yudan-ran-tests.txt`, 86 tests OK). B09 ran with a directory junction, because this Windows account cannot create symlinks (WinError 1314).

## The policy

| | Allowed | Refused |
|---|---|---|
| Network | `GET` over `https` to `boards-api.greenhouse.io`, `api.ashbyhq.com`, `api.lever.co`; a board name may only use `a-z`, `0-9` and `-` | any other host, scheme or method; a board name that could change the URL path |
| Read | any file inside the project folder | anything outside it |
| Write | new files inside `runs/`, judged on the real path after `..` and symbolic links are resolved, comparing whole path parts | anything else |
| Needs my approval (`--approve KEY`) | `reset-state:<ats>/<board>`, `replace-evidence:<path under runs/>` | the same action without that exact key |
| Never | — | `apply`, `send_email`, `send_message`, `login`: no such tool exists, and asking for one is refused |

## Boundary cases (at least 10, predicted first)

| # | Case | Predicted (2026-11-09, before running) | Test | Observed |
|---|---|---|---|---|
| B01 | `GET https://boards-api.greenhouse.io/...` | allowed | `test_b01_allowed_host_get_passes` | as predicted (test ok) |
| B02 | host off the allow-list, `evil.example.com` | refused, no request made | `test_b02_host_off_allowlist_refused`, `test_tool_refused_fetch_makes_no_request` | as predicted (test ok) |
| B03 | allowed host over `http://` | refused | `test_b03_http_not_https_refused` | as predicted (test ok) |
| B04 | look-alike host `boards-api.greenhouse.io.evil.com` | refused | `test_b04_lookalike_host_refused` | as predicted (test ok) |
| B05 | `POST` to an allowed host | refused | `test_b05_post_to_allowed_host_refused` | as predicted (test ok) |
| B06 | write `runs/live/x.json` | allowed | `test_b06_write_inside_runs_allowed` | as predicted (test ok) |
| B07 | write `runs/../GATE.md` | refused | `test_b07_dotdot_escape_refused` | as predicted (test ok) |
| B08 | write `runs-evil/x.json` (prefix trick, W3) | refused | `test_b08_prefix_trick_refused` | as predicted (test ok) |
| B09 | write through a symlink `runs/link` → a folder outside | refused (or the test is skipped if this machine cannot create a symlink; a skip is reported, never counted as a pass) | `test_b09_symlink_escape_refused` | as predicted (test ok) |
| B10 | read `persona/resume.json` | allowed | `test_b10_read_inside_project_allowed` | as predicted (test ok) |
| B11 | read `../elsewhere.txt` outside the project | refused | `test_b11_read_outside_project_refused` | as predicted (test ok) |
| B12 | the same file: read yes, write no (`persona/resume.json`) | read allowed, write refused | `test_b12_same_file_read_yes_write_no` | as predicted (test ok) |
| B13 | reset a board's seen ids without approval | refused: needs approval | `test_b13_reset_state_without_approval_needs_approval` | as predicted (test ok) |
| B14 | the same reset with `--approve reset-state:greenhouse/pinterest` | allowed | `test_b14_reset_state_with_approval_allowed` | as predicted (test ok) |
| B15 | replace a saved evidence file without approval | refused: needs approval | `test_b15_replace_evidence_needs_approval` | as predicted (test ok) |
| B16 | approval for a different board (`ashby/ramp`) | refused: needs approval | `test_b16_approval_for_another_board_does_not_count` | as predicted (test ok) |
| B17 | tools `apply`, `send_email`, `send_message`, `login` | refused | `test_b17_never_tools_refused` | as predicted (test ok) |
| B18 | a board name `x/../../evil` that rewrites the URL path | refused; run ends `error`, no request made | `test_policy_refusal_stops_with_error` | as predicted (test ok) |
| B19 | an allow-listed host answers `302` to another host (GATE revision 2026-11-09) | not followed: the second host receives no request; the board fails, no retry | `test_redirect_is_not_followed`, `test_3xx_is_not_transient` | as predicted (test ok) |
