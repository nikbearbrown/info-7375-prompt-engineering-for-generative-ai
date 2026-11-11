# Permission policy: boundary tests

The policy is in `GATE.md` and enforced in `agent/policy.py`. Each case below has its prediction written on 2026-11-09, before `agent/policy.py` existed and before any test ran. The "What happened" column was filled in after `python3 -m unittest tests.test_policy -v` ran on 2026-11-09: 18 tests, 18 as predicted. Cases 19 to 23 ran on 2026-11-10 after my predictions were committed (`898afe3`): 5 tests, 5 as predicted.

| # | Case | Kind | Prediction | Test | What happened |
|---|---|---|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/pinterest/jobs?content=true` | request, allowed host | allowed | `test_01_greenhouse_get_allowed` | as predicted: allowed |
| 2 | GET `https://api.lever.co/v0/postings/spotify?mode=json` | request, allowed host | allowed | `test_02_lever_get_allowed` | as predicted: allowed |
| 3 | GET `https://example.com/jobs` | request, host off the allow-list | refused before any connection | `test_03_host_off_allow_list_refused` | as predicted: refused before any connection |
| 4 | GET `https://boards-api.greenhouse.io.evil.com/jobs` | request, look-alike host | refused | `test_04_look_alike_host_refused` | as predicted: refused |
| 5 | GET `http://boards-api.greenhouse.io/...` | request, plain http | refused | `test_05_plain_http_refused` | as predicted: refused |
| 6 | POST to `https://api.lever.co/...` | request, not a GET | refused | `test_06_post_refused` | as predicted: refused |
| 7 | A redirect from an allowed host to `https://example.com/` | request, redirect | refused, nothing fetched from example.com | `test_07_redirect_off_allow_list_refused` | as predicted: refused, nothing fetched from example.com |
| 8 | Write `runs/state/seen_ids.json` | write, allowed folder | allowed | `test_08_write_in_runs_allowed` | as predicted: allowed |
| 9 | Write `evidence/raw/x.json` | write, allowed folder | allowed | `test_09_write_in_evidence_allowed` | as predicted: allowed |
| 10 | Write `runs/../GATE.md` | write, `..` escape | refused | `test_10_dotdot_escape_refused` | as predicted: refused |
| 11 | Write `runs-evil/x.json` | write, prefix trick beside `runs` | refused | `test_11_prefix_trick_refused` | as predicted: refused |
| 12 | Write `runs/link/x.json`, where `runs/link` is a symlink to a folder outside | write, symlink escape | refused | `test_12_symlink_escape_refused` | as predicted: refused |
| 13 | Write an absolute path outside the project, such as `/tmp/x.json` | write, outside | refused | `test_13_absolute_outside_refused` | as predicted: refused |
| 14 | Read `config/boards.json` | read, inside the folder | allowed | `test_14_read_config_allowed` | as predicted: allowed |
| 15 | Read `../js1-contract-and-watch/README.md` | read, outside the folder | refused | `test_15_read_outside_refused` | as predicted: refused |
| 16 | Write `config/budgets.json` without my approval | write that needs approval | refused ("needs my approval") | `test_16_config_write_without_approval_refused` | as predicted: refused ("needs my approval") |
| 17 | Write `config/budgets.json` with my approval | write that needs approval | allowed | `test_17_config_write_with_approval_allowed` | as predicted: allowed |
| 18 | Write `agent/rule.py` (the relevance rule) without my approval | write that needs approval | refused ("needs my approval") | `test_18_rule_write_without_approval_refused` | as predicted: refused ("needs my approval") |
| 19 | GET `https://api.ashbyhq.com/posting-api/job-board/ramp` | request, the third allowed host | allowed | `test_19_ashby_get_allowed` | as predicted: allowed |
| 20 | GET `https://api.lever.co@example.com/v0/postings/x` | request, allowed name before an `@` | refused | `test_20_userinfo_trick_refused` | as predicted: refused |
| 21 | GET `https://api.lever.co:8443/v0/postings/spotify` | request, allowed host on another port | allowed (my note: the GATE allows an HTTPS request to an approved hostname and does not restrict ports) | `test_21_other_port_allowed` | as predicted: allowed |
| 22 | Write `evidence/raw/../../config/hosts.json` | write, reaching `config/` through `..` | refused | `test_22_dotdot_into_config_refused` | as predicted: refused |
| 23 | GET `https://BOARDS-API.GREENHOUSE.IO/v1/boards/pinterest/jobs` | request, allowed host in capitals | allowed | `test_23_capital_letters_host_allowed` | as predicted: allowed |

A refused request must raise before any connection is made, and a refused write must leave no file behind.

Cases 19 to 23 are my own predictions, written on 2026-11-10 before their tests existed.

Claude Code drafted the 18 predictions from `GATE.md`; on 2026-11-10 I read and checked all of them. All 18 tests matched their prediction.
