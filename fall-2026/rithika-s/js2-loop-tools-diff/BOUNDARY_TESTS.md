# Boundary tests — permission policy (GATE.md section 5)

Predictions written and committed before any policy code existed.
"Actual" is filled in only from a test run I performed myself.

| ID | Request | Kind | Predicted | Reason (GATE §5) | Test name | Actual |
|---|---|---|---|---|---|---|
| B01 | GET `https://boards-api.greenhouse.io/v1/boards/scaleai/jobs` | network | ALLOW | On allow-list, HTTPS, GET | | not yet run |
| B02 | GET `https://api.ashbyhq.com/posting-api/job-board/openai` | network | ALLOW | On allow-list, HTTPS, GET | | not yet run |
| B03 | GET `https://example.com/jobs` | network | REFUSE `host_not_allowed` | Host off the allow-list | | not yet run |
| B04 | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs` | network | REFUSE `host_not_allowed` | Exact host match, not "ends with" (W7) | | not yet run |
| B05 | GET `http://boards-api.greenhouse.io/v1/boards/scaleai/jobs` | network | REFUSE `not_https` | HTTPS only | | not yet run |
| B06 | POST to `https://boards-api.greenhouse.io/v1/boards/scaleai/jobs` | network | REFUSE `method_not_allowed` | GET only; no submitting or applying | | not yet run |
| B07 | GET allowed URL with an `Authorization` header | network | REFUSE `credentials_not_allowed` | Never log in | | not yet run |
| B08 | Allowed host redirects to `https://example.com/` | network | REFUSE `redirect_off_allowlist` | Redirect off the allow-list | | not yet run |
| B09 | Write `out/raw/<run>_scaleai_a1.json` | write | ALLOW | Inside `out/` | | not yet run |
| B10 | Write `out/../data/resume.example.json` | write | REFUSE `path_outside_write_area` | `..` resolves outside `out/` | | not yet run |
| B11 | Write `out-evil/x.json` | write | REFUSE `path_outside_write_area` | Prefix trick: compared by path components (W8) | | not yet run |
| B12 | Write `out/link/x.json`, where `out/link` is a symlink to a folder outside the project | write | REFUSE `path_outside_write_area` | Symlink resolved before checking (W8) | | not yet run |
| B13 | Read `data/resume.example.json` | read | ALLOW | `data/` is readable | | not yet run |
| B14 | Write `data/resume.example.json` | write | REFUSE `path_outside_write_area` | Same file as B13: readable is not writable | | not yet run |
| B15 | Read `/etc/passwd` | read | REFUSE `path_outside_read_area` | Outside every read folder | | not yet run |
| B16 | Write `out/raw/<run>_scaleai_a1.json` when it already exists | write | REFUSE `would_overwrite` | Evidence is never overwritten | | not yet run |
| B17 | Reset `out/state/scaleai.json`, approver answers yes | approval | ALLOW | My approval given for this action | | not yet run |
| B18 | Reset `out/state/scaleai.json`, approver answers no | approval | REFUSE `approval_denied` | I said no | | not yet run |
| B19 | Reset `out/state/scaleai.json`, no one to answer | approval | REFUSE `approval_denied` | Default is no (W9) | | not yet run |
