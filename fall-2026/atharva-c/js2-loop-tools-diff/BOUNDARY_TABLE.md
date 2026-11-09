# BOUNDARY_TABLE.md

| # | Action / Input Target | Operation | Context / Flags | Predicted Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|---|
| 1 | `https://api.github.com/repos` | GET | Valid JSON endpoint, unauthorized host | Blocked (host not allowed), run exits error | | |
| 2 | `https://boards-api.greenhouse.io.evil.com/jobs` | GET | Lookalike domain | Blocked (host not allowed), run exits error | | |
| 3 | `https://boards-api.greenhouse.io/v1/boards/github/jobs` | POST | Allowed host, forbidden method | Blocked (method not allowed), run exits error | | |
| 4 | `out/../secret.txt` | Write | Traversal attempting write outside `out/` | Blocked (path traversal), run exits error | | |
| 5 | `out-evil/jobs.json` | Write | Prefix lookalike directory | Blocked (outside `out/`), run exits error | | |
| 6 | `out/symlink_escape` | Write | Symlink pointing to project root | Blocked (resolves outside `out/`), run exits error | | |
| 7 | `/etc/passwd` | Write | Absolute filesystem path | Blocked (outside `out/`), run exits error | | |
| 8 | `boards.json` | Read | Config read during setup | Allowed (permitted read path) | | |
| 9 | `boards.json` | Write | Modifying board list without `--approve` | Blocked (protected file requires `--approve`), run exits error | | |
| 10 | `boards.json` | Write | Modifying board list with `--approve` | Allowed (explicit operator approval granted) | | |
| 11 | `https://boards-api.greenhouse.io/v1/boards/robinhood/jobs` | GET | Allowed host and method | Allowed | | |
| 12 | `out/jobs.json` | Write | Standard output target within allowed directory | Allowed | | |

*Note: The path validation tests only execute the policy verification functions and operate inside a temporary directory created by pytest (`tmp_path`), ensuring no files outside the test sandbox are ever created or modified.*
