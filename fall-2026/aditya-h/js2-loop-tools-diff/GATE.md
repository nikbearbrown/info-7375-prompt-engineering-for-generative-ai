# GATE — Job-Search Agent 2: exits and policy, written before any code

**Author:** Aditya Hasija
**Written:** 2026-11-09, before Claude Code wrote or changed any JS2 code.
**Gate version:** v1

**Provenance:**
- **Decisions:** Aditya made every decision below in the Claude Code chat on 2026-11-09:
  - the board set (5 real boards + 2 demonstration boards)
  - the budgets (10 boards, 15 requests, 120 s)
  - retrying transient errors once
  - the repeat rule (same URL = same action)
  - the approved write (resetting a board's state)
  - the three wrong versions
- **Wording:** Claude Code drafted this text from those answers.
- **Facts:** the board facts were probed by Claude Code on 2026-11-09:
  - Ramp's Greenhouse board returned HTTP 200 with one posting, while Ramp's Ashby board returned 175.
  - A misspelled Greenhouse slug returned HTTP 404.
- **Approval:** Aditya approved this text in chat ("Approved") on 2026-11-09, before any JS2 code was written.

**Started from:** my own Job-Search Agent 1 (`../js1-contract-and-watch/`): its allow-listed fetch, id-based state, persona guard, and the `title-us-v1` rule. I also used the instructor's Lectern notes (`fall-2026/nik-bear-brown/lectern/ATS.md`) as reference for the Ashby endpoint and the lesson that a wrong slug can return a valid, empty board. No Lectern code is copied.

## The loop

One run is a **bounded loop over the boards in `boards.json`, in file order**. For each board:
1. Check the budgets.
2. Ask the permission policy whether the fetch is allowed.
3. Make one GET request (plus at most the one sanctioned retry).
4. Save the raw response.
5. Parse and normalize the postings.
6. Diff them by id against that board's own state.
7. Judge the new postings with the JS1 rule.
8. Record an observation in the trace.

Every step, including refusals, appends one line to the run's **trace** (`runs/<run-id>/trace.jsonl`).

### Boards (v1)

| key | ATS | slug | purpose |
|---|---|---|---|
| `greenhouse/stripe` | Greenhouse | `stripe` | real |
| `greenhouse/anthropic` | Greenhouse | `anthropic` | real |
| `ashby/openai` | Ashby | `openai` | real |
| `ashby/notion` | Ashby | `notion` | real |
| `lever/palantir` | Lever | `palantir` | real |
| `greenhouse/stripe-js2-bad` | Greenhouse | `stripe-js2-bad` | **deliberate failure**: a bad slug, expected HTTP 404 |
| `greenhouse/ramp` | Greenhouse | `ramp` | **finished-wrong demonstration**: a stale old board (Ramp now posts on Ashby) |

## Exits

Every run ends with **exactly one** exit status. A run that stops is not a run that succeeded.

| exit | when | what it reports |
|---|---|---|
| `finished` | every board was attempted, and every board ended `ok` | per-board counts (fetched / new / relevant), budget used, trace path |
| `incomplete` | every board was attempted or deliberately skipped, but at least one ended `failed` or `skipped-duplicate` | the same, plus **which** boards failed and why. A failed board's counts are reported as `null` (unknown), **never 0**. |
| `budget-exhausted` | a budget would be exceeded before the next request | everything so far, plus the boards **not attempted** and which budget ran out |
| `error` | a permission violation, corrupt state, or an invalid config or persona | stops immediately. It reports the violation; later boards are listed as not attempted. |

**`finished` is not the same as "correct".** The loop's own report can be wrong while it ends cleanly, e.g. a stale board reported as "0 new". Correctness is checked by a **separate program**, `check_run.py`, that doesn't trust the loop's report:
- It **recomputes** every count from the saved raw files.
- It **flags a suspect board** when an `ok` board has fewer than 3 postings, or its newest posting is more than 14 days old.
- For a suspect board, it makes **one read-only cross-check request** to the same company on another allow-listed ATS, taken from `checks.json`.

The check has its own trace and never changes state.

## Budgets (per run)

| budget | limit | what happens at the limit |
|---|---|---|
| boards | **10** | Boards beyond the 10th in `boards.json` are not attempted. Exit is `budget-exhausted`. |
| requests | **15** HTTP requests, counting retries | A request that would be the 16th is not made. Exit is `budget-exhausted`. |
| seconds | **120** s wall clock | Checked before every request. Each request's timeout is the smaller of 20 s and the time remaining. |

**Who may change a budget:** only Aditya, by adding a new dated entry under "Budget changes" below. The loop reads its budgets from one constant in the code, `BUDGETS`, and a test asserts that this constant equals the latest entry in this file. No command-line flag or prompt can raise a budget.

### Budget changes
- 2026-11-09 — v1 — boards 10, requests 15, seconds 120 (Aditya).

## Repeat rule

- **The same action** means the same method + host + path + query string within one run.
- **The only allowed repeat** is the single sanctioned retry after a transient error (see the error policy below).
- **Any other repeat is refused** before it happens. It is recorded in the trace as `repeat-blocked`, costs no request budget, and gets no new data.
- **A board key that appears twice** in `boards.json` is fetched once. The second entry is recorded as `skipped-duplicate`.

## Error policy (per board)

| failure | retry? | why | board result |
|---|---|---|---|
| timeout, connection error, HTTP 5xx, HTTP 429 | **once**, after 2 s | Transient: the same request can succeed a moment later. | `failed` if the retry also fails |
| HTTP 4xx other than 429 (e.g. 404 bad slug) | **never** | Deterministic: retrying returns the same answer and only burns budget. | `failed` |
| HTTP 200 but the body is not JSON, or not the expected shape for that ATS | **never** | A retry would get the same body. This is a problem with the data, not with timing. | `failed` |
| HTTP 200 with zero postings while the state already holds ids | no | Probably a broken board, not a real emptying. | `failed` ("suspect-empty"), and the state is not changed |

**A failed board:**
- keeps its previous state untouched,
- has its raw body saved as evidence if one was received,
- reports `null` counts, never an invented 0, and
- makes the run's exit `incomplete`.

The other boards continue.

**Escalate to Aditya, and stop the run with exit `error`, when:** the permission policy refuses any action except a repeat; a state file is corrupt; or `boards.json` or the persona is invalid. The agent never "fixes" these itself.

## Permission policy (enforced in code: `jobwatch2/policy.py`)

Every network request and every file read or write goes through `policy.py` **before** it happens. The prompt is not the enforcement. There is no Claude call in the JS2 loop at all; the rule judge is code.

**Network**
- **Method:** `GET` only.
- **Scheme:** `https` only.
- **Hosts:** exactly these three, each with the only path shape allowed on it:

  | host | allowed path |
  |---|---|
  | `boards-api.greenhouse.io` | `/v1/boards/<slug>/jobs` |
  | `api.ashbyhq.com` | `/posting-api/job-board/<slug>` |
  | `api.lever.co` | `/v0/postings/<slug>` with `?mode=json` |

- **Slugs:** must match `[a-z0-9-]+`.
- **Headers:** no credential headers (`Authorization`, `Cookie`) are ever sent.

**Files**
- **Write:** only inside `runs/`, judged by the **resolved real path**. That means:
  - no `..` escape,
  - no prefix trick (`runs-evil/` is not inside `runs/`),
  - no symlink that points out of `runs/`,
  - no absolute path elsewhere.
- **Read:** only inside this assignment folder (`js2-loop-tools-diff/`). Reading is a separate permission from writing. For example, `personas/` and `boards.json` are readable but not writable.
- **Needs Aditya's approval:** resetting or deleting a board's saved state (a re-baseline), because it changes what "new" means for that board from then on. It is allowed only when the run is started with `--approve-reset <board-key>` for that exact board. Otherwise it is refused, with the reason `needs-approval`. The agent cannot grant itself this flag.

**Never:** apply to a job, email or message anyone, log in, send a non-GET request, contact a host not listed above, or read my real résumé. The persona guard from JS1 still refuses any résumé that doesn't use `@example.com` emails and 555 phone numbers.

### Boundary cases — predicted before running

Each row is a test in `tests/test_policy.py`. The **Predicted** column was written here first.

| # | request | predicted |
|---|---|---|
| 1 | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs` | allow |
| 2 | GET `https://example.com/jobs` | deny: host not allowed |
| 3 | GET `http://boards-api.greenhouse.io/v1/boards/stripe/jobs` | deny: scheme not https |
| 4 | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs` | deny: host not allowed (suffix trick) |
| 5 | POST `https://api.lever.co/v0/postings/palantir/<id>/apply` | deny: method not GET (never apply) |
| 6 | GET `https://api.lever.co/v0/postings/palantir/<id>/apply` | deny: path not a board listing |
| 7 | GET an allowed URL with an `Authorization` or `Cookie` header | deny: credential header (never log in) |
| 8 | write `runs/state/greenhouse__stripe.json` | allow |
| 9 | write `runs/../GATE.md` | deny: escapes `runs/` |
| 10 | write `runs-evil/x.json` (prefix trick, a sibling of `runs`) | deny: outside `runs/` |
| 11 | write `runs/link/x.json`, where `runs/link` is a symlink to a folder outside | deny: resolved path outside `runs/` |
| 12 | write `/tmp/x.json` (absolute path) | deny: outside `runs/` |
| 13 | read `personas/maya-sehgal.resume.json` | allow (read) |
| 14 | write `personas/maya-sehgal.resume.json` | deny: read allowed, write not |
| 15 | read `~/.ssh/id_rsa` or `../../../../etc/passwd` | deny: outside the assignment folder |
| 16 | reset `greenhouse/stripe` state without `--approve-reset` | deny: needs-approval |
| 17 | reset `greenhouse/stripe` state with `--approve-reset greenhouse/stripe` | allow |
| 18 | reset `ashby/openai` with `--approve-reset greenhouse/stripe` | deny: approval is for a different board |
| 19 | the same GET twice in one run, with no transient error | second one: deny, `repeat-blocked` |

## Relevance (unchanged from JS1, extended to three systems)

New postings are judged by the JS1 rule `title-us-v1`: a product-family title phrase, **and** a US location. Each ATS is first normalized to the same fields:

| normalized | Greenhouse | Ashby | Lever |
|---|---|---|---|
| `id` | `<board-key>:<id>` | `<board-key>:<id>` | `<board-key>:<id>` |
| `title` | `title` | `title` | `text` |
| `location.name` | `location.name` | `location` + `secondaryLocations[].location` | `categories.allLocations` (or `categories.location`) |
| US office/country | `offices[].name` is `US` / `US-…` | `address.postalAddress.addressCountry` = `United States` (incl. secondary) | `country` = `US` |

Ids are namespaced by board key, so two systems can never collide.

## Wrong versions (my tests must catch these)

1. **Stopped = succeeded.**
   - *What it does:* the loop reports `finished` although a board failed or a budget ran out.
   - *Why it looks right:* the run ends cleanly and prints counts.
   - *Test:* a fixture run with one 404 board must exit `incomplete`, and a run with the request budget set to 2 across 5 boards must exit `budget-exhausted` and list the unattempted boards.
2. **Invented value on failure.**
   - *What it does:* a failed board is recorded as "0 postings / 0 new" instead of failed.
   - *Why it looks right:* zero is a plausible count, and the report is tidy.
   - *Test:* a failed board's counts must be `null`, its state file must be byte-for-byte unchanged, and the report must name it as failed.
3. **Retry everything.**
   - *What it does:* retries a 404 or bad JSON, or retries without limit.
   - *Why it looks right:* retrying feels robust.
   - *Test:* with a fake fetcher, a 404 must be requested exactly once, and a timeout exactly twice (the original plus one retry). The request counter must match the trace.
