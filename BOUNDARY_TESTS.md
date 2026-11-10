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

These were added after the code existed. The predictions above were not edited. Raw outputs are in `evidence/tests/`.

| ID | Predicted | Actual after the build (`6c82b59`) | Actual after the patch (`afb3877`) |
|---|---|---|---|
| B01 | deny | deny | deny |
| B02 | deny | deny | deny |
| **B03** | deny | **allow (mismatch)** | deny |
| **B04** | deny | **allow (mismatch)** | deny |
| B05 | deny | deny | deny |
| B06 | deny | deny | deny |
| B07 | deny | deny | deny |
| B08 | deny | deny | deny |
| B09 | deny | deny | deny |
| B10 | deny | deny | deny |
| B11 | allow | allow | allow |
| B12 | deny | deny | deny |
| B13 | allow | allow | allow |
| B14 | needs approval | needs approval | needs approval |
| B15 | allow | allow | allow |
| B16 | deny | deny | deny |
| B17 | deny | deny | deny |
| B18 | allow | allow | allow |
| | | **16/18** (`02_boundary_after_build.txt`) | **18/18** (`03_boundary_after_patch.txt`) |

The two mismatches were the ones written down in advance: JS1's `check_url` accepted a nonstandard port and user information. They
are the review packet's defect ([REVIEW_PACKET.md](REVIEW_PACKET.md)). No prediction was changed to make a row match.
