# Permission policy: boundary cases

The policy is `jobloop/policy.py` (rules in GATE.md section 5). The cases below were listed by
Claude Code on 2026-11-09. **The Predicted column is Ashwin's, written before any of these cases
was run.** The Actual column is filled only from the output of `tests/test_boundaries.py`.

Outcomes: `allow`, `deny`, `approval-required`, or `run error` (the loop stops before any request).
For path cases, the path is relative to the `js2-loop-tools-diff/` folder.

| ID | What is asked | Exact input | Predicted (Ashwin) | Why (Ashwin) | Actual |
|---|---|---|---|---|---|
| B01 | Network read, configured board | `GET https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | | | |
| B02 | Host off the allow-list | `GET https://evil.example/v1/boards/klaviyo/jobs?content=true` | | | |
| B03 | Lookalike host (allowed name as a prefix) | `GET https://boards-api.greenhouse.io.evil.example/v1/boards/klaviyo/jobs?content=true` | | | |
| B04 | Network write to an allowed URL | `POST https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | | | |
| B05 | Allowed host, board not in the config | `GET https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | | | |
| B06 | Plain http | `GET http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | | | |
| B07 | Nonstandard port | `GET https://boards-api.greenhouse.io:8443/v1/boards/klaviyo/jobs?content=true` | | | |
| B08 | File write inside the run folder | write `runs/2026-11-09T00-00-00Z-live/report.json` | | | |
| B09 | `..` escape | write `runs/../state/seen.json` | | | |
| B10 | Sibling-prefix trick (`runs-evil` beside `runs`) | write `runs-evil/report.json` | | | |
| B11 | Symlink escape | write `runs/link/x.json`, where `runs/link` is a symlink to a folder outside the project | | | |
| B12 | Read request | read `config/boards.json` | | | |
| B13 | Write request to the same file as B12 | write `config/boards.json` | | | |
| B14 | State write, finished run, **no** `--approve-state-write` | write `state/seen.json` (status `finished`, no flag) | | | |
| B15 | State write, **with** the flag, finished run | write `state/seen.json` (status `finished`, flag given) | | | |
| B16 | State write, with the flag, but the run was incomplete | write `state/seen.json` (status `incomplete`, flag given) | | | |
| B17 | Read outside the project (absolute path) | read `/etc/passwd` | | | |
| B18 | Config text tries to grant approval | `config/boards.json` with an extra key `"approve_state_write": true`, run without the flag | | | |

To fill in: for each row, write your predicted outcome and one short reason. Then tell Claude
Code; it commits the table before writing or running `tests/test_boundaries.py`.
