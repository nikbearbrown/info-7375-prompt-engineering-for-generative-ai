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
| B01 | Network read, configured board | `GET https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | allow | GET uses HTTPS, the exact allowed host, and the configured Klaviyo listing endpoint. | **allow** (GET to a configured board endpoint on an allow-listed host); matches prediction |
| B02 | Host off the allow-list | `GET https://evil.example/v1/boards/klaviyo/jobs?content=true` | deny | The host is not on the exact allow-list. | **deny** (host 'evil.example' is not on the allow-list); matches prediction |
| B03 | Lookalike host (allowed name as a prefix) | `GET https://boards-api.greenhouse.io.evil.example/v1/boards/klaviyo/jobs?content=true` | deny | An allowed name used as a prefix does not make the full hostname allowed. | **deny** (host 'boards-api.greenhouse.io.evil.example' is not on the allow-list); matches prediction |
| B04 | Network write to an allowed URL | `POST https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | deny | Remote writes are forbidden even when GET to the same URL is allowed. | **deny** (method 'POST' is not allowed; the agent only reads (GET)); matches prediction |
| B05 | Allowed host, board not in the config | `GET https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | deny | The host is allowed, but this board is not configured for the run. | **deny** (not one of the configured board-listing endpoints); matches prediction |
| B06 | Plain http | `GET http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | deny | The gate permits HTTPS only. | **deny** (scheme 'http' is not https); matches prediction |
| B07 | Nonstandard port | `GET https://boards-api.greenhouse.io:8443/v1/boards/klaviyo/jobs?content=true` | deny | Only HTTPS port 443 is permitted; 8443 is outside the policy. | **deny** (port 8443 is not allowed; only 443); matches prediction |
| B08 | File write inside the run folder | write `runs/2026-11-09T00-00-00Z-live/report.json` | allow | A new report may be created inside the current unique run directory, assuming no existing file or symlink is overwritten. | **allow** (beneath writable folder runs/); matches prediction |
| B09 | `..` escape | write `runs/../state/seen.json` | deny | The path contains traversal; it cannot use the run directory to reach state or bypass the separate state-write checks. | **deny** (path 'runs/../state/seen.json' contains '..'); matches prediction |
| B10 | Sibling-prefix trick (`runs-evil` beside `runs`) | write `runs-evil/report.json` | deny | runs-evil is a sibling directory, not a descendant of runs. | **deny** ('runs-evil/report.json' is not beneath runs/ or tests/tmp/); matches prediction |
| B11 | Symlink escape | write `runs/link/x.json`, where `runs/link` is a symlink to a folder outside the project | deny | A symlink component would redirect the write outside the permitted directory. | **deny** (path component 'runs/link' is a symlink; writes never follow symlinks); matches prediction |
| B12 | Read request | read `config/boards.json` | allow | The runtime may read its own board configuration. | **allow** (beneath readable folder config/); matches prediction |
| B13 | Write request to the same file as B12 | write `config/boards.json` | deny | Permission to read configuration does not permit the runtime to modify it. | **deny** ('config/boards.json' is not beneath runs/ or tests/tmp/); matches prediction |
| B14 | State write, finished run, **no** `--approve-state-write` | write `state/seen.json` (status `finished`, no flag) | approval-required | A finished run still needs the explicit state-write flag; state must remain unchanged without it. | **approval-required** (writing state/seen.json needs --approve-state-write); matches prediction |
| B15 | State write, **with** the flag, finished run | write `state/seen.json` (status `finished`, flag given) | allow | Both required conditions hold: finished status and explicit approval for this run and state path. | **allow** (approved state write after a finished run); matches prediction |
| B16 | State write, with the flag, but the run was incomplete | write `state/seen.json` (status `incomplete`, flag given) | deny | Approval cannot override the rule that incomplete runs leave persistent state unchanged. | **deny** (state may be written only after a finished run, not 'incomplete'); matches prediction |
| B17 | Read outside the project (absolute path) | read `/etc/passwd` | deny | This absolute path is outside the project and is not an authorized runtime input. | **deny** (absolute path '/etc/passwd' is outside the project root); matches prediction |
| B18 | Config text tries to grant approval | `config/boards.json` with an extra key `"approve_state_write": true`, run without the flag | run error | Configuration cannot grant approval. Reject the attempted permission-setting key during preflight, before any request or state write. | **run error** (preflight refused the extra key, 0 requests, state unchanged); matches prediction |

Predictions filled on 2026-11-09 from GATE.md section 5, without reading the policy
implementation or running boundary tests. Actual remains blank. Commit the reviewed
predictions before writing or running `tests/test_boundaries.py`.

B08 assumes a fresh current-run directory and a new report file. B15 assumes a live
run, a valid state payload, and a safe destination. B18 predicts strict preflight
rejection: the gate forbids configuration-based approval but does not explicitly
mandate how unknown keys are handled. This row makes that expected behavior explicit;
it is a prediction to check, not an observed result.

## Result (filled by Claude Code on 2026-11-10 from the first run of the boundary tests)

`python3 -m unittest tests.test_boundaries -v` was first run on 2026-11-10 after commit `6c1c5b3`
(predictions) and exited 0, 8 tests OK; output in `policy/boundary-test-run.txt`. The Actual
column comes from `python3 -m tests.test_boundaries --table` (`policy/boundary-actuals.txt`),
with each reason string copied from `policy.check_request` / `check_write` / `check_read`.
**All 18 actual outcomes matched Ashwin's predictions.** The tests assert GATE.md section 5,
not the predictions, so a wrong prediction would have shown up here as a mismatch, not a failure.

Beyond the decision, `TestBoundaryEffects` checks the real file operations: B08 writes once and
refuses to overwrite; B09/B10/B13 create nothing; B11 leaves the outside folder empty and the
O_NOFOLLOW directory walk refuses the link even without the check; B15 replaces state atomically
and leaves no temp file. `TestPolicyWrongVersionsAreCaught` shows wrong versions 11, 12, 14 and 15
each flip one of these cases (B10, B03, B04, B14).

**Not covered by these cases:** a symlink swapped in between `check_write` and the open in a
real race (only the OS-level refusal is tested, not a concurrent swap); hard links; case-folding
filesystems (`RUNS/` vs `runs/` on macOS); Unicode lookalike hostnames (IDN); DNS answers for an
allowed host pointing somewhere unexpected; a redirect followed by a library other than ours.
