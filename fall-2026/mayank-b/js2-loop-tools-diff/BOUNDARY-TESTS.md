# Permission boundary tests: predictions first

## Executive summary

**What this is.** Sixteen cases at the edge of what my agent may do: hosts it may call, paths it may read or write, and writes that need my approval. Each case has a **prediction written and committed before any test ran**, then the result actually observed.

**Why it matters.** The permission policy is in code (`src/jsa/policy.py`, `src/jsa/net.py`), not in a prompt. These tests are how I know the code enforces what GATE.md §6 says. A test I can't predict, I don't yet understand.

**What it found.** On the final code (CP6) all 16 cases were allowed or refused as predicted, and the "Observed" column was filled in only after running. **One prediction named the wrong reason:** B7 was refused as predicted, but with `approval-required`, not the `outside-write-root` I wrote. The one prediction the first version broke was **B8**, the review-packet defect: a write through a symlink pointing outside the project was **allowed**. That was reproduced before the patch (CP5) and refused after it (CP6). One gap remains untested: if `runs/` *itself* is a symlink to outside, writes still land outside (`review/04-still-missed-probe.txt`).

## The permission policy (GATE.md §6, enforced in code)

| Rule | Where in the code | What it allows |
|---|---|---|
| Hosts | `policy.check_url` + `policy._host_ok`; `net.fetch` calls it before every request | only `boards-api.greenhouse.io` and `api.ashbyhq.com`, exact match; `https` only; port 443 only; no user-info in the URL |
| Methods | `policy.check_url` | `GET` only |
| Redirects | `net._NoRedirect` | none followed: a 3xx becomes `redirect-refused` |
| Read | `policy.authorize(…, "read")` | inside `config/`, `persona/`, `state/`, `runs/`, judged by where the path resolves |
| Write, no approval | `policy.authorize(…, "write", run_id=…)` | inside `runs/<this-run-id>/` only |
| Write, needs my approval | `policy.authorize(…, approval=…)` + `policy._approval_ok`; used only by `agent.py approve` | `state/seen-ids.json`, only when the approval is a string exactly equal to the run id |
| Never | not representable in the code | apply, email, message, log in, submit a form, send credentials: there is no code path for any of these |

Containment is component-wise (`Path.is_relative_to`), never a string prefix.

## The boundary tests

Predictions committed in JS2-CP2 (before code). Test names refer to `tests/test_policy.py`.

| # | Case | Request | Predicted (correct policy) | Wrong version it catches | Observed |
|---|---|---|---|---|---|
| B1 | host off the allow-list | GET `https://example.com/jobs` | **refused**: `host-not-allowed` | — | refused `host-not-allowed` ✅ (`test_B1_host_off_allowlist`) |
| B2 | allowed host as a substring | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs` | **refused**: `host-not-allowed` | W8 | refused `host-not-allowed` ✅ (`test_B2_…`); planting W8 turns it red |
| B3 | allowed host, plain http | GET `http://boards-api.greenhouse.io/v1/boards/anthropic/jobs` | **refused**: `scheme-not-https` | — | refused `scheme-not-https` ✅ |
| B4 | allowed host, https, GET | GET `https://api.ashbyhq.com/posting-api/job-board/notion` | **allowed** | — | allowed ✅; also exercised live: 3 real board fetches in run `2026-11-11T00-24-30Z-real` |
| B5 | allowed host, non-GET | POST `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs` | **refused**: `method-not-allowed` | — | refused `method-not-allowed` ✅ |
| B6 | redirect from an allowed host | a 301 from an allowed host to `https://evil.example/` | **refused, not followed**: `redirect-refused` | — | refused `redirect-refused` ✅ (handler raises; nothing followed) |
| B7 | `..` escape on write | write `runs/<id>/../../state/seen-ids.json` | **refused**: `outside-write-root` (it resolves to `state/`, which needs approval, and isn't the run folder) | — | refused ✅, **but for a different reason than predicted**: `approval-required`, because the path resolves to `state/seen-ids.json` itself and the approval rule is checked first. My predicted reason (`outside-write-root`) was wrong. The test asserts the observed reason; an extra case `runs/<id>/../../config/x.json` gives `outside-write-root` |
| B8 | symlink escape on write | write `runs/<id>/link/x.json`, where `link` → a folder outside the project | **refused**: `outside-write-root` | W2 (**review-packet defect: the first version is expected to allow it**) | **before the patch (CP5, `review/01-reproduce-before-patch.txt`): ALLOWED, defect reproduced.** After the patch (CP6, `review/03-after-patch.txt`): refused `outside-write-root` ✅; planting W2 turns it red |
| B9 | prefix trick | write `runs-evil/x.json`, a sibling of `runs/` | **refused**: `outside-write-root` | W1 | refused `outside-write-root` ✅ for `runs-evil/` and for `runs/<id>-evil/`; planting W1 turns it red |
| B10 | read inside a read root | read `config/boards.json` | **allowed** | — | allowed ✅ |
| B11 | read outside every read root | read `../js1-contract-and-watch/.env` | **refused**: `outside-read-roots` | — | refused `outside-read-roots` ✅ (also `src/` is not readable) |
| B12 | read allowed but write not | write `config/boards.json` | **refused**: `outside-write-root` | — | refused `outside-write-root` ✅ |
| B13 | approval-needed write, no approval | write `state/seen-ids.json`, approval absent | **refused**: `approval-required` | — | refused `approval-required` ✅ |
| B14 | approval-needed write, truthy approval | write `state/seen-ids.json` with approval `"yes"`, then `True` | **refused** both: `approval-invalid` | W3 | refused `approval-invalid` ✅ for `"yes"`, `True`, `1`, `"true"`; planting W3 turns it red. Also via the CLI (`test_truthy_approval_writes_nothing`) |
| B15 | approval for a different run | write `state/seen-ids.json` with approval = another run's id | **refused**: `approval-invalid` | — | refused `approval-invalid` ✅ |
| B16 | approval exactly matching | write `state/seen-ids.json` with approval == this run id | **allowed** | — | allowed ✅ |
