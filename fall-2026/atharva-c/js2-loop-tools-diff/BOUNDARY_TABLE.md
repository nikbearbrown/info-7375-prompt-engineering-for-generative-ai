# BOUNDARY_TABLE.md

| # | Action / Input Target | Operation | Context / Flags | Predicted Result | Actual Result | Pass/Fail |
|---|---|---|---|---|---|---|
| 1 | `https://api.github.com/repos` | GET | Valid JSON endpoint, unauthorized host | Blocked (host not allowed), run exits error | Blocked (PolicyViolation, `test_b01`); `error` exit checked in loop tests | ✅ |
| 2 | `https://boards-api.greenhouse.io.evil.com/jobs` | GET | Lookalike domain | Blocked (host not allowed), run exits error | Blocked (PolicyViolation, `test_b02`); `error` exit checked in loop tests | ✅ |
| 3 | `https://boards-api.greenhouse.io/v1/boards/github/jobs` | POST | Allowed host, forbidden method | Blocked (method not allowed), run exits error | Blocked (PolicyViolation, `test_b03`); `error` exit checked in loop tests | ✅ |
| 4 | `out/../secret.txt` | Write | Traversal attempting write outside `out/` | Blocked (path traversal), run exits error | Blocked (PolicyViolation, `test_b04`); `error` exit checked in loop tests | ✅ |
| 5 | `out-evil/jobs.json` | Write | Prefix lookalike directory | Blocked (outside `out/`), run exits error | Blocked (PolicyViolation, `test_b05`); `error` exit checked in loop tests | ✅ |
| 6 | `out/symlink_escape` | Write | Symlink pointing to project root | Blocked (resolves outside `out/`), run exits error | Blocked (PolicyViolation, `test_b06`); `error` exit checked in loop tests | ✅ |
| 7 | `/etc/passwd` | Write | Absolute filesystem path | Blocked (outside `out/`), run exits error | Blocked (PolicyViolation, `test_b07`); `error` exit checked in loop tests | ✅ |
| 8 | `boards.json` | Read | Config read during setup | Allowed (permitted read path) | Allowed (`test_b08`) | ✅ |
| 9 | `boards.json` | Write | Modifying board list without `--approve` | Blocked (protected file requires `--approve`), run exits error | Blocked (PolicyViolation, `test_b09`); `error` exit checked in loop tests | ✅ |
| 10 | `boards.json` | Write | Modifying board list with `--approve` | Allowed (explicit operator approval granted) | Allowed (`test_b10`) | ✅ |
| 11 | `https://boards-api.greenhouse.io/v1/boards/robinhood/jobs` | GET | Allowed host and method | Allowed | Allowed (`test_b11`) | ✅ |
| 12 | `out/jobs.json` | Write | Standard output target within allowed directory | Allowed | Allowed (`test_b12`) | ✅ |

*Note: The path validation tests only execute the policy verification functions and operate inside a temporary directory created with Python's `unittest` and `tempfile` (originally written as pytest `tmp_path`; changed because the tests use the standard library, like JS1), ensuring no files outside the test sandbox are ever created or modified.*

Actual results from my own run on Nov 8, 2026: 12 of 12 passed. Command: `python3 -m unittest discover -s tests -t . -v`. Evidence: `evidence/policy-tests-20261108.txt`. Policy code and tests: commit `f357831`.
