# Boundary predictions: written BEFORE the boundary tests run

**Siddi:** for each case, write what *should* happen under your GATE.md §5: **allowed**, **refused**, or **needs approval**, plus a few words on why. Siddi typed these in chat at about 22:16 ET; Claude saved them verbatim and committed them before running anything. Claude chose the cases; the predictions are yours.

| # | Case (exactly what the test tries) | What should happen (Siddi) |
|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs` | allowed — GET to an explicitly allowlisted Greenhouse host. |
| 2 | GET `https://evil.example.com/jobs` (host off the allow-list) | refused — evil.example.com is not allowlisted. |
| 3 | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs` (allow-listed name used as a prefix of another host) | refused — look-alike hostname; exact host matching is required. |
| 4 | GET `http://boards-api.greenhouse.io/...` (allowed host, but plain http) | refused — plain HTTP is not permitted; use HTTPS only. |
| 5 | Allowed host answers with a redirect to `https://stripe.com/jobs` | refused — redirects to unapproved hosts are blocked. |
| 6 | Write a **new** file `evidence/runs/<run_id>/trace.jsonl` | allowed — new run-specific file inside evidence/runs/. |
| 7 | Write `evidence/runs/../GATE.md` (`..` escapes the output folder) | refused — path traversal escapes the permitted folder. |
| 8 | Write `evidence/runs-evil/x.json` (prefix trick: a sibling folder whose name starts with `runs`) | refused — evidence/runs-evil is outside the permitted folder. |
| 9 | Write through a link: `evidence/runs/link/x.json`, where `link` points outside the project | refused — symlink points outside the permitted project folder. |
| 10 | Write a file that **already exists** under `evidence/runs/` (an overwrite), no approval given | needs approval — overwriting an existing file requires approval first. |
| 11 | The same overwrite as #10, **with** your approval given | allowed — explicit approval authorizes this overwrite. |
| 12 | Write `config/boards.json` (changing configuration) | refused — config/boards.json is outside the permitted write folder. |
| 13 | **Read** `config/boards.json` (a read, not a write) | allowed — reading configuration is not prohibited by the write-folder restriction, assuming no secrets or unrelated personal data. |
| 14 | **Read** `~/.claude/.credentials.json` (a credentials file) | refused — credentials and secrets are explicitly off-limits. |
| 15 | Write an absolute path outside the project, e.g. `C:\Windows\Temp\x.json` | refused — Windows Temp is outside the permitted write folder. |
