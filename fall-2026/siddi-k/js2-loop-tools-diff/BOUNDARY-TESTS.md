# Boundary tests (GATE.md §5)

Run by `python tests/boundary_tests.py` against a throwaway copy of the folder layout. Case 9's link was a **junction** on this machine. Predictions are Siddi's, committed before this ran (`BOUNDARY-PREDICTIONS.md`).

| # | Case | Siddi predicted | Actual (from the code) |
|---|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs` | allowed — GET to an explicitly allowlisted Greenhouse host. | allowed |
| 2 | GET `https://evil.example.com/jobs` (host off the allow-list) | refused — evil.example.com is not allowlisted. | refused ('https://evil.example.com/jobs': host 'evil.example.com' is not on the allow-list) |
| 3 | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs` (allow-listed name used as a prefix of another host) | refused — look-alike hostname; exact host matching is required. | refused ('https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs': host 'boards-api.greenhouse.io.evil.com' is not on the allow-list) |
| 4 | GET `http://boards-api.greenhouse.io/...` (allowed host, but plain http) | refused — plain HTTP is not permitted; use HTTPS only. | refused ('http://boards-api.greenhouse.io/v1/boards/stripe/jobs': only https is allowed) |
| 5 | Allowed host answers with a redirect to `https://stripe.com/jobs` | refused — redirects to unapproved hosts are blocked. | refused (redirect 302 to 'https://stripe.com/jobs' refused: redirects are never followed) |
| 6 | Write a **new** file `evidence/runs/<run_id>/trace.jsonl` | allowed — new run-specific file inside evidence/runs/. | allowed |
| 7 | Write `evidence/runs/../GATE.md` (`..` escapes the output folder) | refused — path traversal escapes the permitted folder. | refused (evidence/runs/../GATE.md: '..' path segments are never allowed) |
| 8 | Write `evidence/runs-evil/x.json` (prefix trick: a sibling folder whose name starts with `runs`) | refused — evidence/runs-evil is outside the permitted folder. | refused (evidence/runs-evil/x.json: writes are allowed only under evidence/runs/) |
| 9 | Write through a link: `evidence/runs/link/x.json`, where `link` points outside the project | refused — symlink points outside the permitted project folder. | refused (evidence/runs/link/x.json: resolves outside this assignment folder (C:\Users\Suhas Kommuri\AppData\Local\Temp\js2outsidest94brj6\x.json)) |
| 10 | Write a file that **already exists** under `evidence/runs/` (an overwrite), no approval given | needs approval — overwriting an existing file requires approval first. | needs approval (evidence/runs/existing.json: overwriting an existing file needs approval) |
| 11 | The same overwrite as #10, **with** your approval given | allowed — explicit approval authorizes this overwrite. | allowed |
| 12 | Write `config/boards.json` (changing configuration) | refused — config/boards.json is outside the permitted write folder. | needs approval (config/boards.json: changing config needs approval) |
| 13 | **Read** `config/boards.json` (a read, not a write) | allowed — reading configuration is not prohibited by the write-folder restriction, assuming no secrets or unrelated personal data. | allowed |
| 14 | **Read** `~/.claude/.credentials.json` (a credentials file) | refused — credentials and secrets are explicitly off-limits. | refused (C:\Users\Suhas Kommuri\.claude\.credentials.json: reads are allowed only inside this assignment folder) |
| 15 | Write an absolute path outside the project, e.g. `C:\Windows\Temp\x.json` | refused — Windows Temp is outside the permitted write folder. | refused (C:\Windows\Temp\x.json: resolves outside this assignment folder (C:\Windows\Temp\x.json)) |

## Findings (added by Claude after the run; the table above is generated)

- **14 of 15 predictions matched the code.**
- **Mismatch, case 12 (write `config/boards.json`):** Siddi predicted *refused*; the code returned *needs approval*. The code follows GATE.md §5 as written ("writes that need my approval first: Changing configuration or budgets…"). So the prediction disagrees with Siddi's own gate, not with the implementation. Neither the code nor the prediction was changed after the run; which one should change is Siddi's decision.
- **Case 9:** Windows refused to create a symlink without the developer privilege, so the test made a directory **junction**, which `Path.resolve()` follows the same way. A true symlink was not exercised on this machine.
- **Case 14:** the credentials path was refused because it lies **outside the assignment folder**. The separate secret-name rule (`.credentials.json`) was not what fired, and is only exercised for secret-named files inside the folder.
