# Permission policy and boundary tests

The policy itself is in `GATE.md` and is enforced by `agent/policy.py`. Every network request
goes through `check_request()`, every file read through `check_read()`, and every write
through `check_write()`. The loop has no other way to reach the network or the disk.

## Predictions (written before the tests or the policy code existed)

Committed in a separate commit before `agent/policy.py` and `tests/test_policy.py`, so the
predictions cannot have been fitted to the results. Paths are relative to this assignment
folder. "Approval" means an explicit approval passed in by Smit, never one the agent grants itself.

| # | Kind | Input | Predicted result | Why |
|---|---|---|---|---|
| P1 | request | `GET https://boards-api.greenhouse.io/v1/boards/figma/jobs` | allow | Allow-listed host, HTTPS, GET. |
| P2 | request | `GET https://evil.example.com/jobs` | deny: host not allowed | Host off the allow-list. |
| P3 | request | `GET https://boards-api.greenhouse.io.evil.com/v1/boards/figma/jobs` | deny: host not allowed | Look-alike: the allowed name is only a prefix of this host. |
| P4 | request | `GET https://evilgreenhouse.io/v1/boards/figma/jobs` | deny: host not allowed | Catches a suffix check (`endswith("greenhouse.io")`). |
| P5 | request | `GET http://boards-api.greenhouse.io/v1/boards/figma/jobs` | deny: scheme | Plain HTTP is not allowed. |
| P6 | request | `GET https://user:pw@api.lever.co/v0/postings/spotify` | deny: credentials | Credentials in a URL mean logging in. |
| P7 | request | `GET https://api.lever.co:8443/v0/postings/spotify` | deny: port | Only the default HTTPS port. |
| P8 | request | `POST https://api.lever.co/v0/postings/spotify/abc/apply` | deny: method | Only GET; this is also an apply. |
| P9 | request | `GET https://api.lever.co/v0/postings/spotify/abc/apply` | deny: apply path | The agent never applies, even with GET. |
| P10 | request | `GET https://127.0.0.1/` | deny: host not allowed | IP literals are not on the list. |
| P11 | request | `GET https://API.LEVER.CO/v0/postings/spotify` | allow | Hostnames are case-insensitive; normalized before the check. |
| P12 | request | GET to an allowed host with an `Authorization` header | deny: credentials | Logging in is never allowed. |
| P13 | write | `jobs/state/figma.state.json` | allow | Inside the write root. |
| P14 | write | `jobs/../GATE.md` | deny: outside write root | `..` escapes `jobs/`. |
| P15 | write | `jobs-evil/x.json` | deny: outside write root | Prefix trick: starts with the text `jobs` but is a sibling folder. |
| P16 | write | `jobs/escape/x.json` where `jobs/escape` is a symlink to a folder outside | deny: outside write root | Resolved with symlinks followed before the check. |
| P17 | write | `/tmp/x.json` (absolute) | deny: outside write root | Absolute path outside the assignment. |
| P18 | read | `config/boards.json` | allow | Readable root. |
| P19 | write | `config/boards.json`, no approval | needs approval | Config writes need Smit's approval. |
| P20 | write | `config/budgets.json`, with Smit's approval | allow | Approved config write. |
| P21 | read | `/etc/passwd` | deny: outside read roots | Reads are limited too. |
| P22 | read | `GATE.md` | deny: outside read roots | Readable roots are `config/`, `fixtures/`, `jobs/` only; the agent has no reason to read its own policy documents. |
| P23 | delete | `jobs/state/figma.state.json`, no approval | needs approval | Resetting a baseline needs approval. |
| P24 | action | `apply`, `email`, `message`, `login` | deny: forbidden action | Never, whatever a config says. |
| P25 | write | `jobs/runs/x.json\0.sh` (NUL byte) | deny: invalid path | A NUL byte makes the path ambiguous. |

## Results

Filled in after running `python3 -m unittest tests.test_policy -v`; see the section below the
table once it exists.
