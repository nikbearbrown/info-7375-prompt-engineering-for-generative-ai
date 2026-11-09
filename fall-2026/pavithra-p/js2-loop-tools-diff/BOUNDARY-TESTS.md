# Permission policy: boundary tests

The policy is in `GATE.md` and enforced in `agent/policy.py`. Each case below has its prediction written on 2026-11-09, before `agent/policy.py` existed and before any test ran. The "What happened" column is filled in only after the run.

| # | Case | Kind | Prediction | Test | What happened |
|---|---|---|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/pinterest/jobs?content=true` | request, allowed host | allowed | `test_01_greenhouse_get_allowed` | |
| 2 | GET `https://api.lever.co/v0/postings/spotify?mode=json` | request, allowed host | allowed | `test_02_lever_get_allowed` | |
| 3 | GET `https://example.com/jobs` | request, host off the allow-list | refused before any connection | `test_03_host_off_allow_list_refused` | |
| 4 | GET `https://boards-api.greenhouse.io.evil.com/jobs` | request, look-alike host | refused | `test_04_look_alike_host_refused` | |
| 5 | GET `http://boards-api.greenhouse.io/...` | request, plain http | refused | `test_05_plain_http_refused` | |
| 6 | POST to `https://api.lever.co/...` | request, not a GET | refused | `test_06_post_refused` | |
| 7 | A redirect from an allowed host to `https://example.com/` | request, redirect | refused, nothing fetched from example.com | `test_07_redirect_off_allow_list_refused` | |
| 8 | Write `runs/state/seen_ids.json` | write, allowed folder | allowed | `test_08_write_in_runs_allowed` | |
| 9 | Write `evidence/raw/x.json` | write, allowed folder | allowed | `test_09_write_in_evidence_allowed` | |
| 10 | Write `runs/../GATE.md` | write, `..` escape | refused | `test_10_dotdot_escape_refused` | |
| 11 | Write `runs-evil/x.json` | write, prefix trick beside `runs` | refused | `test_11_prefix_trick_refused` | |
| 12 | Write `runs/link/x.json`, where `runs/link` is a symlink to a folder outside | write, symlink escape | refused | `test_12_symlink_escape_refused` | |
| 13 | Write an absolute path outside the project, such as `/tmp/x.json` | write, outside | refused | `test_13_absolute_outside_refused` | |
| 14 | Read `config/boards.json` | read, inside the folder | allowed | `test_14_read_config_allowed` | |
| 15 | Read `../js1-contract-and-watch/README.md` | read, outside the folder | refused | `test_15_read_outside_refused` | |
| 16 | Write `config/budgets.json` without my approval | write that needs approval | refused ("needs my approval") | `test_16_config_write_without_approval_refused` | |
| 17 | Write `config/budgets.json` with my approval | write that needs approval | allowed | `test_17_config_write_with_approval_allowed` | |
| 18 | Write `agent/rule.py` (the relevance rule) without my approval | write that needs approval | refused ("needs my approval") | `test_18_rule_write_without_approval_refused` | |

A refused request must raise before any connection is made, and a refused write must leave no file behind.
