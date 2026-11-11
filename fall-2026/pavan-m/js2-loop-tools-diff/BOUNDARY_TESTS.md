# Boundary tests — predictions written before running
Written November 9, 2026, before any test or implementation exists. Each prediction follows GATE.md §6.

| # | Case | Kind | Predicted result |
|---|---|---|---|
| B1 | GET `https://example.org/` | host off allow-list | Refused (`PolicyError`); no request sent |
| B2 | GET `https://boards-api.greenhouse.io.evil.com/` | lookalike host | Refused; hostnames are compared exactly, not by substring |
| B3 | GET an allowed host that redirects to `https://evil.example.org/` | redirect off allow-list | Refused before the redirected request is sent |
| B4 | POST to `https://boards-api.greenhouse.io/` | non-GET method | Refused; no request sent |
| B5 | GET `https://api.lever.co/v0/postings/palantir?mode=json` | allowed host, GET | Allowed |
| B6 | Write `out/runs/test/summary.json` | write inside out/ | Allowed |
| B7 | Write `out/../GATE.md` | `..` traversal | Refused; GATE.md unchanged |
| B8 | Write `/tmp/js2_escape.txt` | absolute path outside | Refused |
| B9 | Write `out-evil/x.json` | prefix trick | Refused; `out-evil` is not inside `out` |
| B10 | Write `out/link/x.json`, where `out/link` is a symlink to a folder outside out/ | symlink escape | Refused; nothing written outside out/ |
| B11 | Read `evidence/2026-11-09_manual-capture_lever_palantir.json` | read, approved folder | Allowed |
| B12 | Write `evidence/new.json` | write to a read-only folder | Refused; evidence/ is read-only for the agent |
| B13 | Read `../js1-contract-and-watch/README.md` | read outside the project | Refused |
| B14 | Reset state of `lever:palantir` with no approval | needs approval | Refused; existing state unchanged |
| B15 | Reset `lever:palantir` with `--approve reset:ashby:openai` | wrong approval | Refused; approval for one board doesn't cover another |
| B16 | Reset `lever:palantir` with `--approve reset:lever:palantir` | matching approval | Allowed |

Results are recorded after running, in the "Actual" column added later. They are never edited into the "Predicted" column.

## Actual results (added November 10, 2026, after running; predictions above unchanged)
Command: `python -m pytest tests/test_policy.py -v` → 16 passed (evidence/boundary_tests_run_2026-11-10.txt).

| # | Test | Actual | Matches prediction? |
|---|---|---|---|
| B1 | test_B1_host_off_allow_list_refused | PolicyError; no request sent | Yes |
| B2 | test_B2_lookalike_host_refused | PolicyError; no request sent | Yes |
| B3 | test_B3_redirect_off_allow_list_refused | PolicyError; evil.example.org never contacted | Yes |
| B4 | test_B4_post_refused | PolicyError; no request sent | Yes |
| B5 | test_B5_allowed_host_get_allowed | 200; exactly 1 request sent | Yes |
| B6 | test_B6_write_inside_out_allowed | Allowed; resolved path inside out/ | Yes |
| B7 | test_B7_dotdot_traversal_refused | PolicyError; GATE.md unchanged | Yes |
| B8 | test_B8_absolute_path_outside_refused | PolicyError | Yes |
| B9 | test_B9_prefix_trick_refused | PolicyError | Yes |
| B10 | test_B10_symlink_escape_refused | PolicyError; outside folder still empty | Yes |
| B11 | test_B11_read_evidence_allowed | Allowed | Yes |
| B12 | test_B12_write_to_read_only_evidence_refused | PolicyError | Yes |
| B13 | test_B13_read_outside_project_refused | PolicyError | Yes |
| B14 | test_B14_reset_without_approval_refused | PolicyError; state unchanged | Yes |
| B15 | test_B15_reset_with_wrong_approval_refused | PolicyError; state unchanged | Yes |
| B16 | test_B16_reset_with_matching_approval_allowed | Reset; seen_ids == [] | Yes |

All 16 matched. Caveat: these run against a fake network (httpx MockTransport) and temporary folders; the live runs only exercised B5-style allowed GETs and a real 404, not a real redirect or a real symlink attack.
