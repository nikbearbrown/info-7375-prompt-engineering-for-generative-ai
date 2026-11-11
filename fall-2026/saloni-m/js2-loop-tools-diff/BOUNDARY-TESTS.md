# Permission boundary tests

Policy: [GATE.md §5](GATE.md). Code: [jsagent/policy.py](jsagent/policy.py), [jsagent/fetch.py](jsagent/fetch.py).
Tests: [tests/test_policy.py](tests/test_policy.py), one test per row (`test_Bnn_…`).

**Order of work.** Claude Code wrote the cases (the "Request" column). Saloni wrote her
prediction for each case **before the tests were run** (commit `JS2-5`). The observed column was
filled in only after the run, from `review/03-boundary-run.txt`.

Outcomes: **allow**, **deny**, or **needs approval**.

| # | Request | Kind | Saloni's prediction (before running) | Observed |
|---|---|---|---|---|
| B01 | GET `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs` | network | **Allow** — Approved Greenhouse host, read-only GET. | |
| B02 | GET `https://api.ashbyhq.com/posting-api/job-board/openai` | network | **Allow** — Approved Ashby host, read-only GET. | |
| B03 | GET `https://api.lever.co/v0/postings/netflix` (host not on the list) | network | **Allow** — Approved Lever host, read-only GET. | |
| B04 | GET `https://boards-api.greenhouse.io.evil.example/…` (allowed name + extra suffix) | network | **Deny** — Host is a deceptive subdomain of an unapproved domain. | |
| B05 | GET `https://evilboards-api.greenhouse.io/…` (allowed name + extra prefix) | network | **Deny** — Host only ends with the approved hostname; it is not an exact match. | |
| B06 | GET `http://boards-api.greenhouse.io/…` (http, not https) | network | **Deny** — HTTP is not secure; HTTPS is required. | |
| B07 | **POST** to `boards-api.greenhouse.io/…/jobs/1` (what applying would look like) | network | **Deny** — POST is not permitted; only read-only GET requests are allowed. | |
| B08 | GET `https://me:pw@boards-api.greenhouse.io/…` (a login) | network | **Deny** — URLs containing embedded usernames or passwords are not allowed. | |
| B09 | GET `https://evil.example/?next=https://boards-api.greenhouse.io/` | network | **Deny** — The actual destination is evil.example, regardless of the URL parameter. | |
| B10 | an allowed host answers with a redirect to `https://evil.example/jobs` | network | **Deny** — Redirects to unapproved hosts must be blocked. | |
| B11 | write `out/runs/r1/trace.jsonl` | write | **Allow** — Writing run logs inside the permitted output folder is allowed. | |
| B12 | write `out/../GATE.md` (`..` escape) | write | **Deny** — Path traversal attempts to escape the permitted output folder. | |
| B13 | write `out-evil/x.json` (a folder next to `out` whose name starts with "out") | write | **Deny** — out-evil is not the permitted out directory. | |
| B14 | write `out/link/x.json`, where `out/link` is a symlink to a folder outside the project | write | **Deny** — The symlink points outside the permitted project directory. | |
| B15 | write `/etc/js2-should-never-exist` | write | **Deny** — Writing to system directories is outside the agent's permissions. | |
| B16 | `GATE.md`: **read** it, then **write** it | read vs write | **Allow, then deny** — Reading GATE.md is allowed, but modifying the assignment's policy file is not. | |
| B17 | read `~/.ssh/id_rsa` | read | **Deny** — Private SSH keys are sensitive and must never be accessed. | |
| B18 | write `out/state/seen_ids.json` when it does not exist yet (first run) | write | **Allow** — Creating the initial saved-state file is allowed because it does not overwrite existing history. | |
| B19 | overwrite `out/state/seen_ids.json` (it exists), no approval | write | **Needs approval** — Overwriting saved job history could destroy previously tracked information. | |
| B20 | overwrite `out/state/seen_ids.json`, with `--approve-state` | write | **Allow** — Explicit approval has been provided through the approval flag. | |
| B21 | write `out/alias.json`, a symlink to `out/state/seen_ids.json`, no approval | write | **Deny** — The symlink points to protected state, so it must not bypass the approval requirement. | |

Saloni's note with her predictions (2026-11-10, quoted): "Important distinction: B04 and B05 are
both denied because hostname validation must use exact approved-host matching, not substring or
suffix matching."
