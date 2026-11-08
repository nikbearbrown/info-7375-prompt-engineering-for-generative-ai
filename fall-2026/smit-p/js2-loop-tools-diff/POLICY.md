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

Ran `python3 -m unittest tests.test_policy -v` on 2026-11-08 (raw output in
`evidence/policy-tests.txt`). **25 of 25 predictions matched; no prediction was edited after
the run.** One extra case (`jobsx`, a file named like the root) was added while writing the
tests and also passed.

| # | Predicted | Observed | Match |
|---|---|---|---|
| P1 | allow | allow | yes |
| P2 | deny: host | deny: host 'evil.example.com' not allowed | yes |
| P3 | deny: host | deny: host 'boards-api.greenhouse.io.evil.com' not allowed | yes |
| P4 | deny: host | deny: host 'evilgreenhouse.io' not allowed | yes |
| P5 | deny: scheme | deny: scheme 'http' not allowed | yes |
| P6 | deny: credentials | deny: credentials in URL | yes |
| P7 | deny: port | deny: port 8443 not allowed | yes |
| P8 | deny: method | deny: method POST not allowed | yes |
| P9 | deny: apply path | deny: apply path | yes |
| P10 | deny: host | deny: host '127.0.0.1' not allowed | yes |
| P11 | allow | allow | yes |
| P12 | deny: credentials | deny: credential header Authorization | yes |
| P13 | allow | allow | yes |
| P14 | deny | deny: outside write root | yes |
| P15 | deny | deny: outside write root | yes |
| P16 | deny | deny: outside write root, and nothing landed in the symlink target | yes |
| P17 | deny | deny: outside write root | yes |
| P18 | allow | allow | yes |
| P19 | needs approval | needs approval, and the guarded write left no file | yes |
| P20 | allow | allow (approved config write) | yes |
| P21 | deny | deny: outside read roots | yes |
| P22 | deny | deny: outside read roots | yes |
| P23 | needs approval | needs approval; allow with approval | yes |
| P24 | deny | deny for apply, email, message, login, Apply | yes |
| P25 | deny: invalid path | deny: invalid path | yes |

**Do these tests catch a wrong policy?** A suite that passes proves little unless it fails on
wrong code. `tests/mutation_check.py` plants each wrong version from GATE.md into a scratch
copy and runs the suite. On 2026-11-08 it caught all three policy mutants (prefix path check,
path check without resolving symlinks, suffix host check), the redirect mutant, and all six
loop mutants (10 of 10):
`evidence/mutation-check.txt`.

**Policy in the loop, not only in the unit tests.** `GuardedFetcher.get` calls
`check_request` before the transport is touched, and the loop writes only through
`guarded_write`. `tests/test_loop.py::PolicyInTheLoop` shows that an off-list URL ends the run
as `error` with zero requests sent, and that a whole run leaves nothing outside `jobs/`.

**A gap found while writing this page.** The first draft of this paragraph listed "a redirect
to another host" as untested, because Python's `urlopen` follows 3xx responses on its own and
the policy only sees the first URL. Rather than leave it listed, `tests/test_redirect.py` was
written first and failed (`evidence/redirect-test-before-fix.txt`: the transport returned the
redirected page's 200), then `LiveTransport` was changed to an opener that refuses redirects.
A 3xx now ends that board as `failed:http_3xx` with `count: null`. Mutant W9 confirms the test
catches the old behavior.

**What these tests still do not show.** DNS rebinding (an allowed name resolving to an
unexpected address); a symlink created between the check and the write (a time-of-check
race); and anything about Windows paths. These are listed under "Not checked" in SIGNOFF.md.
