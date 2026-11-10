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
