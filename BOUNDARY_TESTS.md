# Boundary tests: permission policy (GATE.md section 5)

Each row's prediction was written on 2026-11-10, **before** `jsagent/policy.py` or `jsagent/net.py` existed. That commit is the first
one that contains this file. The actual results are filled in from `scripts/boundary_report.py` output in later commits, and kept apart
from the predictions.

The file cases run inside a throwaway project folder made by the test (`proj/` with `config/`, `out/`, and so on), so a wrong
implementation can never touch the real repository.

**Who wrote what:** Claude Code drafted these cases and their predictions from GATE.md. Ethan reviews them.
**Code:** `tests/js2_boundary_cases.py` holds the cases. `tests/test_js2_boundary.py` asserts actual equals predicted.

| ID | Operation | Input | Predicted | Rule in GATE.md |
|---|---|---|---|---|
| B01 | GET | `https://api.ashbyhq.com/posting-api/job-board/kraken.com` (host off the list) | **deny** | Network: exact hosts |
| B02 | GET | `https://boards-api.greenhouse.io.evil.com/v1/boards/samsara/jobs` (lookalike) | **deny** | Network: suffixes and lookalikes do not match |
| B03 | GET | `https://boards-api.greenhouse.io:8443/v1/boards/samsara/jobs` (nonstandard port) | **deny** | Network: port 443 only |
| B04 | GET | `https://user:pw@boards-api.greenhouse.io/v1/boards/samsara/jobs` (user information) | **deny** | Network: no user information |
| B05 | GET | `http://boards-api.greenhouse.io/v1/boards/samsara/jobs` (plain HTTP) | **deny** | Network: HTTPS only |
| B06 | POST | `https://boards-api.greenhouse.io/v1/boards/samsara/jobs` (write on an allowed host) | **deny** | Network: GET only |
| B07 | redirect | allowed URL redirected to `https://evil.example.com/` | **deny** | Network: every hop checked before following |
| B08 | write | `out/../config/allowlist.json` (traversal) | **deny** | Files: resolve first, then compare |
| B09 | write | `out-evil/x.json` (sibling prefix) | **deny** | Files: no string-prefix check |
| B10 | write | `out/link/x.json`, where `out/link` is a symlink to a folder outside the project | **deny** | Files: symlink escapes denied |
| B11 | read | `config/allowlist.json` | **allow** | Files: config is readable |
| B12 | write | `config/allowlist.json` | **deny** | Files: config is not writable |
| B13 | write (new file) | `out/runs/r1/raw/x.json` | **allow** | Files: create inside the output root |
| B14 | write (existing file) | `out/runs/r1/raw/x.json` again, no approval | **needs approval** | Files: overwriting evidence needs approval |
| B15 | write (existing file) | the same path with `--approve out/runs/r1/raw/x.json` | **allow** | Files: one named approval |
| B16 | choose output root | `--out config/` | **deny** | Files: output root may not be a protected folder |
| B17 | read | `~/.ssh/id_rsa` | **deny** | Files: no reads outside the listed folders |
| B18 | GET | `https://BOARDS-API.greenhouse.io/v1/boards/samsara/jobs` (uppercase host) | **allow** | Network: hosts compared in lowercase |

**What I expect to see before the patch:** the JS2 network check reuses JS1's `fetch.check_url`. JS1 already allowed a nonstandard port and
user information (checked offline on 2026-11-10, with Claude's help), so I expect **B03 and B04 to come out "allow" until the
review-packet patch lands.** The predictions above stay "deny" because that is what the gate requires.

## Actual results

*(Filled in from `scripts/boundary_report.py` after the code exists. See the sections below for each run.)*
