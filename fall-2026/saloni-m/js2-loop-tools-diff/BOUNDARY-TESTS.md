# Permission boundary tests

Policy: [GATE.md §5](GATE.md). Code: [jsagent/policy.py](jsagent/policy.py), [jsagent/fetch.py](jsagent/fetch.py).
Tests: [tests/test_policy.py](tests/test_policy.py), one test per row (`test_Bnn_…`).

**Order of work.** Claude Code wrote the cases (the "Request" column). Saloni wrote her
prediction for each case **before the tests were run** (commit `JS2-5`). The observed column was
filled in only after the run, from `review/03-boundary-run.txt`.

Outcomes: **allow**, **deny**, or **needs approval**.

| # | Request | Kind | Saloni's prediction (before running) | Observed |
|---|---|---|---|---|
| B01 | GET `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs` | network | **Allow** — Approved Greenhouse host, read-only GET. || allow (✓ matches) |
| B02 | GET `https://api.ashbyhq.com/posting-api/job-board/openai` | network | **Allow** — Approved Ashby host, read-only GET. || allow (✓ matches) |
| B03 | GET `https://api.lever.co/v0/postings/netflix` (host not on the list) | network | **Allow** — Approved Lever host, read-only GET. || deny (**✗ differs**) |
| B04 | GET `https://boards-api.greenhouse.io.evil.example/…` (allowed name + extra suffix) | network | **Deny** — Host is a deceptive subdomain of an unapproved domain. || deny (✓ matches) |
| B05 | GET `https://evilboards-api.greenhouse.io/…` (allowed name + extra prefix) | network | **Deny** — Host only ends with the approved hostname; it is not an exact match. || deny (✓ matches) |
| B06 | GET `http://boards-api.greenhouse.io/…` (http, not https) | network | **Deny** — HTTP is not secure; HTTPS is required. || deny (✓ matches) |
| B07 | **POST** to `boards-api.greenhouse.io/…/jobs/1` (what applying would look like) | network | **Deny** — POST is not permitted; only read-only GET requests are allowed. || deny (✓ matches) |
| B08 | GET `https://me:pw@boards-api.greenhouse.io/…` (a login) | network | **Deny** — URLs containing embedded usernames or passwords are not allowed. || deny (✓ matches) |
| B09 | GET `https://evil.example/?next=https://boards-api.greenhouse.io/` | network | **Deny** — The actual destination is evil.example, regardless of the URL parameter. || deny (✓ matches) |
| B10 | an allowed host answers with a redirect to `https://evil.example/jobs` | network | **Deny** — Redirects to unapproved hosts must be blocked. || deny (✓ matches) |
| B11 | write `out/runs/r1/trace.jsonl` | write | **Allow** — Writing run logs inside the permitted output folder is allowed. || allow (✓ matches) |
| B12 | write `out/../GATE.md` (`..` escape) | write | **Deny** — Path traversal attempts to escape the permitted output folder. || deny (✓ matches) |
| B13 | write `out-evil/x.json` (a folder next to `out` whose name starts with "out") | write | **Deny** — out-evil is not the permitted out directory. || deny (✓ matches) |
| B14 | write `out/link/x.json`, where `out/link` is a symlink to a folder outside the project | write | **Deny** — The symlink points outside the permitted project directory. || deny (✓ matches) |
| B15 | write `/etc/js2-should-never-exist` | write | **Deny** — Writing to system directories is outside the agent's permissions. || deny (✓ matches) |
| B16 | `GATE.md`: **read** it, then **write** it | read vs write | **Allow, then deny** — Reading GATE.md is allowed, but modifying the assignment's policy file is not. || allow, then deny (✓ matches) |
| B17 | read `~/.ssh/id_rsa` | read | **Deny** — Private SSH keys are sensitive and must never be accessed. || deny (✓ matches) |
| B18 | write `out/state/seen_ids.json` when it does not exist yet (first run) | write | **Allow** — Creating the initial saved-state file is allowed because it does not overwrite existing history. || allow (✓ matches) |
| B19 | overwrite `out/state/seen_ids.json` (it exists), no approval | write | **Needs approval** — Overwriting saved job history could destroy previously tracked information. || needs approval (✓ matches) |
| B20 | overwrite `out/state/seen_ids.json`, with `--approve-state` | write | **Allow** — Explicit approval has been provided through the approval flag. || allow (✓ matches) |
| B21 | write `out/alias.json`, a symlink to `out/state/seen_ids.json`, no approval | write | **Deny** — The symlink points to protected state, so it must not bypass the approval requirement. || needs approval (**✗ differs**) |

Saloni's note with her predictions (2026-11-10, quoted): "Important distinction: B04 and B05 are
both denied because hostname validation must use exact approved-host matching, not substring or
suffix matching."

## Result (first run, 2026-11-11 00:47 UTC = 2026-11-10 19:47 ET)

`python3 -m unittest tests.test_policy -v`: **21/21 tests pass** (`review/03-boundary-run.txt`).
Saloni's predictions matched the code on **19 of 21**. The tests encode GATE.md §5; the two
differences are listed here rather than hidden by changing either side.

| # | Predicted | Code does | Which is right, by GATE.md | Status |
|---|---|---|---|---|
| B03 | allow ("Approved Lever host") | deny | **The code.** GATE §5 approves only `boards-api.greenhouse.io` and `api.ashbyhq.com`. Lever was in example option 1B, which Saloni did not choose. The prediction remembered the option menu, not the decision. | prediction wrong; policy unchanged |
| B21 | deny | needs approval | **Both meet the rule** "must not bypass the approval requirement": `realpath` resolves the alias to the history file, so the approval check fires. Deny would be stricter (no alias can ever write history, even approved). | open: Saloni to decide whether to tighten; not changed tonight |

Nothing in the code or tests was changed after the run.
