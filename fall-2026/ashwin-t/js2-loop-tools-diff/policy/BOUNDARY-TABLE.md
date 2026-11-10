# Permission policy: boundary cases

The policy is `jobloop/policy.py` (rules in GATE.md section 5). The cases below were listed by
Claude Code on 2026-11-09. **The Predicted and Why columns are Ashwin's own, written on 2026-11-09
before `tests/test_boundaries.py` existed or any of these cases was run.** (Claude Code had already
written `jobloop/policy.py` at commit `e270605`; see the note at the end.) The Actual column is
filled only from the output of `tests/test_boundaries.py`.

Outcomes: `allow`, `deny`, `approval-required`, or `run error` (the loop stops before any request).
For path cases, the path is relative to the `js2-loop-tools-diff/` folder.

| ID | What is asked | Exact input | Predicted (Ashwin) | Why (Ashwin) | Actual |
|---|---|---|---|---|---|
| B01 | Network read, configured board | `GET https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | allow | GET uses HTTPS, the exact allowed host, and the configured Klaviyo listing endpoint. | |
| B02 | Host off the allow-list | `GET https://evil.example/v1/boards/klaviyo/jobs?content=true` | deny | The host is not on the exact allow-list. | |
| B03 | Lookalike host (allowed name as a prefix) | `GET https://boards-api.greenhouse.io.evil.example/v1/boards/klaviyo/jobs?content=true` | deny | An allowed name used as a prefix does not make the full hostname allowed. | |
| B04 | Network write to an allowed URL | `POST https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | deny | Remote writes are forbidden even when GET to the same URL is allowed. | |
| B05 | Allowed host, board not in the config | `GET https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | deny | The host is allowed, but this board is not configured for the run. | |
| B06 | Plain http | `GET http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | deny | The gate permits HTTPS only. | |
| B07 | Nonstandard port | `GET https://boards-api.greenhouse.io:8443/v1/boards/klaviyo/jobs?content=true` | deny | Only HTTPS port 443 is permitted; 8443 is outside the policy. | |
| B08 | File write inside the run folder | write `runs/2026-11-09T00-00-00Z-live/report.json` | allow | A new report may be created inside the current unique run directory, assuming no existing file or symlink is overwritten. | |
| B09 | `..` escape | write `runs/../state/seen.json` | deny | The path contains traversal; it cannot use the run directory to reach state or bypass the separate state-write checks. | |
| B10 | Sibling-prefix trick (`runs-evil` beside `runs`) | write `runs-evil/report.json` | deny | runs-evil is a sibling directory, not a descendant of runs. | |
| B11 | Symlink escape | write `runs/link/x.json`, where `runs/link` is a symlink to a folder outside the project | deny | A symlink component would redirect the write outside the permitted directory. | |
| B12 | Read request | read `config/boards.json` | allow | The runtime may read its own board configuration. | |
| B13 | Write request to the same file as B12 | write `config/boards.json` | deny | Permission to read configuration does not permit the runtime to modify it. | |
| B14 | State write, finished run, **no** `--approve-state-write` | write `state/seen.json` (status `finished`, no flag) | approval-required | A finished run still needs the explicit state-write flag; state must remain unchanged without it. | |
| B15 | State write, **with** the flag, finished run | write `state/seen.json` (status `finished`, flag given) | allow | Both required conditions hold: finished status and explicit approval for this run and state path. | |
| B16 | State write, with the flag, but the run was incomplete | write `state/seen.json` (status `incomplete`, flag given) | deny | Approval cannot override the rule that incomplete runs leave persistent state unchanged. | |
| B17 | Read outside the project (absolute path) | read `/etc/passwd` | deny | This absolute path is outside the project and is not an authorized runtime input. | |
| B18 | Config text tries to grant approval | `config/boards.json` with an extra key `"approve_state_write": true`, run without the flag | run error | Configuration cannot grant approval. Reject the attempted permission-setting key during preflight, before any request or state write. | |

Predictions filled on 2026-11-09 from GATE.md section 5, without reading the policy
implementation or running boundary tests. Actual remains blank. Commit the reviewed
predictions before writing or running `tests/test_boundaries.py`.

B08 assumes a fresh current-run directory and a new report file. B15 assumes a live
run, a valid state payload, and a safe destination. B18 predicts strict preflight
rejection: the gate forbids configuration-based approval but does not explicitly
mandate how unknown keys are handled. This row makes that expected behavior explicit;
it is a prediction to check, not an observed result.
