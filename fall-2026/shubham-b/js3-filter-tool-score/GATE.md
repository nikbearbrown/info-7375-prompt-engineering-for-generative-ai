# GATE.md — Job-Search Agent 2: the loop, the tools, and the diff

**Version:** v1.0, 2026-11-09, written before any JS2 code.
**Persona:** Kiran Joshi (fictional), the same as in `CONTRACT.md`.

`CONTRACT.md` still governs one board: the rule, the records, the run statuses and the state.
This file governs the loop that runs that one-board pass over several boards.

## 1. What the loop is

`jsa watch` reads a plan, then for each planned board, in order:
checks the budget, fetches the board once through the permission policy (with at most one
retry), and runs the JS1 pass on it (`pipeline.run_once`: rule, records, state). Each board has
its own state folder `data/watch/boards/<provider>-<token>/`. The loop records every
observation in `data/watch/loops/<loop_id>/trace.jsonl` and ends with exactly one exit
status, written to `report.json` and `report.md` beside the trace.

The loop does not call Claude. Its model backend is `none`, so every new posting's judgment is
`UNAVAILABLE` and stays pending. `jsa run` stays the judging path for Stripe.

## 2. Exits

Every run of the loop ends in exactly one of these. A loop that stopped did not
necessarily succeed: only `FINISHED` means every planned board was checked.

| Exit | When | What it reports | Exit code |
|---|---|---|---|
| `FINISHED` | Every planned board was attempted and every one is OK (below) | Per-board status, fetched count, new count, pending count; total requests and seconds used | 0 |
| `INCOMPLETE` | Every planned board was attempted, at least one failed, at least one is OK | The same, plus each failed board with its status, HTTP status and error kind, marked for my attention | 8 |
| `BUDGET_EXHAUSTED` | A budget stopped the loop before every board was attempted | Which budget ran out, the boards done, and the boards **not attempted** (never reported as checked) | 9 |
| `ERROR` | The loop could not do its job: the policy refused the plan before any fetch, a board's state is corrupt or locked, or no attempted board was OK | The reason code; nothing is reported as checked | 10 |

**A board is OK** when its JS1 status is `BASELINE`, `SUCCESS_WITH_NEW` or `SUCCESS_NO_NEW`, or
when it is `PARTIAL_FAILURE` only because judgments were deferred: every judgment is
`UNAVAILABLE`, the backend is `none`, and the notes are only `judgments_not_valid`,
`pending_unresolved` and `judge_unavailable`. Any other `PARTIAL_FAILURE`, and every
`FETCH_FAILED`, `INVALID_RESPONSE` and `EMPTY_RESPONSE`, is a **failed board**.

An empty board is a failed board. "No jobs came back" is not "no new jobs".

**Precedence** when more than one applies: `ERROR`, then `BUDGET_EXHAUSTED`, then
`INCOMPLETE`, then `FINISHED`.

## 3. Budgets

Per loop run, from `config/watch.toml`:

| Budget | Value | Checked |
|---|---:|---|
| `max_boards` (boards attempted) | 6 | Before starting each board |
| `max_requests` (GET attempts sent; see amendment A1) | 10 | Before every attempt |
| `max_seconds` (wall time from loop start) | 180 | Before each board and each retry; each request's timeout is the smaller of 30 s and the time left |

A request already in flight is bounded by its own timeout, so the loop can overrun
`max_seconds` by at most that timeout plus the time to finish the board it is on.

**Who may change a budget:** only me, and only by a new dated entry in section 10 of this file
that gives the new value and the reason, committed before the run that uses it. The agent
cannot change one: `config/` is outside its write folder.

## 4. Repeat rule

- **The same board** is the same provider plus the same token after trimming and lowercasing
  (`Stripe` and ` stripe` are `stripe`). The loop fetches a board at most once per run. A later
  plan entry for a board already in the plan is recorded as `SKIPPED_REPEAT`, is not
  fetched, and does not count against `max_boards`.
- **The same action** is a GET of the same URL in the same loop run. The only allowed second
  GET of a URL is the one retry. Any further GET of that URL is refused by the fetcher
  and recorded as `repeat_refused`.
- **Across runs**, running the loop again is a new decision by me, not a repeat. Postings
  are de-duplicated by the per-board seen-ID state.

## 5. Error policy

| Failure on a board | Retry? | Why | Then |
|---|---|---|---|
| Timeout, connection/DNS/TLS error, HTTP 500–599 | **Once**, after a 2 s pause, only if a request and at least 5 s remain | The request is a read-only GET, so repeating it changes nothing on the server; these failures are often momentary; one retry costs one request and stays polite | If the retry also fails: the board is `FETCH_FAILED`, the loop moves on |
| HTTP 404 or any other 4xx (bad board name) | No | Asking again for a board that does not exist gives the same answer | `FETCH_FAILED` with the HTTP status; the loop moves on |
| HTTP 429 | No | The site asked us to slow down; respecting rate limits is a refusal | `FETCH_FAILED`; moves on |
| Host or redirect refused by the policy, size cap, too many redirects | No | A policy refusal is not a transient fault | `FETCH_FAILED`; moves on |
| Response not JSON or wrong shape | No | The bytes will not change by asking again within seconds | `INVALID_RESPONSE`; moves on |
| Empty `jobs` array | No | Same | `EMPTY_RESPONSE` (a failed board); moves on |
| A board's state file is corrupt, or its lock is held | No | Continuing would risk the saved state | The loop stops: `ERROR` |

The loop never invents a value for a failed board: no posting count, no "0 new". A failed
board's state is never written, and its saved response (if any bytes came back)
is kept as evidence.

**Escalation:** every failed board is listed under "Needs your attention" in
`report.md`, and the exit code is non-zero. The loop never repairs a plan or a state file on its
own.

## 6. Permission policy

Enforced in the program and the fetcher and writer that call
it, not in a prompt. The loop has no model in it, so no instruction can talk it out of these.

**Hosts.** The loop's requests may reach only `boards-api.greenhouse.io` and
`api.ashbyhq.com`: exact host match, HTTPS, port 443, no user name or password in the URL, GET
only. Every redirect hop is checked again. Links inside job descriptions are never followed.

**Reads.** Inside the project folder only. Never `private/`, `.env` files, or anything outside
the project (resolved through symlinks).

**Writes.** Inside `data/watch/` only, resolved through symlinks, so `..`, a sibling with the
same prefix (`data/watch-evil/`) and a symlink that points out are all refused. Everything else
is refused, including `config/` (budgets and the plan), `GATE.md`, the source code and JS1's
`data/live/` state.

**Needs my approval.** Deleting anything under `data/watch/`. The only delete is
`jsa watch reset <provider>/<token>`, which clears one board's saved state so its next run is a
fresh baseline. It asks on a terminal and proceeds only if I types the board key; with
no terminal it is refused.

**Never**, with or without approval: apply for a job, email, message, log in, send any
request other than GET, follow a link from a posting, or change a budget or the plan.

## 7. Boundary cases and predictions (written before the tests run)

| # | Request | Predicted result |
|---|---|---|
| B01 | GET `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | ALLOW |
| B02 | GET `https://api.ashbyhq.com/posting-api/job-board/ramp` | ALLOW |
| B03 | GET `https://jobs.lever.co/palantir` (host off the allow-list) | DENY `host` |
| B04 | GET `https://boards-api.greenhouse.io.evil.example/` (allowed name as a prefix) | DENY `host` |
| B05 | GET `http://boards-api.greenhouse.io/...` (plain HTTP) | DENY `scheme` |
| B06 | POST `https://boards-api.greenhouse.io/v1/boards/stripe/jobs/1` (the apply endpoint, allowed host) | DENY `method` |
| B07 | An allowed host answers with a redirect to `https://evil.example/` | Request refused at the hop, board `FETCH_FAILED` (`REDIRECT_REJECTED`) |
| B08 | Write `data/watch/loops/x/trace.jsonl` | ALLOW |
| B09 | Write `data/watch/../live/state.json` (`..`) | DENY `outside_write_root` |
| B10 | Write `data/watch-evil/x.json` (prefix trick) | DENY `outside_write_root` |
| B11 | Write `data/watch/link/x.json` where `link` is a symlink to a folder outside the project | DENY `outside_write_root` |
| B12 | Read `config/watch.toml` | ALLOW |
| B13 | Write `config/watch.toml` (same file as B12) | DENY `outside_write_root` |
| B14 | Read `private/real.resume.json` | DENY `private` |
| B15 | Read `/etc/hosts` (outside the project) | DENY `outside_project` |
| B16 | Delete `data/watch/boards/greenhouse-ramp/live/state.json` | NEEDS_APPROVAL |
| B17 | B16 with approval refused, or with no terminal | Nothing deleted; DENY `not_approved` |
| B18 | B16 with me typing the board key | ALLOW; the file is deleted |
| B19 | Action `apply` (likewise `email`, `message`, `login`) | DENY `never`, even with approval |
| B20 | A third GET of the same URL in one loop run | DENY `repeat` |

## 8. Wrong versions the tests must catch

Each is plausible and wrong. `tests/meta/test_js2_wrong_versions_caught.py` swaps each one in
and requires the JS2 tests to fail.

| # | Wrong version | Why it is wrong |
|---|---|---|
| W1 | Reports `FINISHED` when a board failed | A loop that stopped is reported as a loop that succeeded |
| W2 | Treats an `EMPTY_RESPONSE` board as OK | An empty board becomes "no new jobs" |
| W3 | Retries every failure (a 404, a 429) | Retries a permanent answer and ignores the site's rate limit |
| W4 | Checks the request budget after sending | Sends one request more than `max_requests` |
| W5 | Write check by string prefix (`str(path).startswith(str(root))`) | `data/watch-evil/` passes |
| W6 | Write check without resolving symlinks | A symlink inside `data/watch/` that points out passes |
| W7 | Host check by suffix or substring | `boards-api.greenhouse.io.evil.example` or `evilgreenhouse.io` passes |
| W8 | Case-sensitive repeat key | `Stripe` and `stripe` are fetched twice |
| W9 | Delete without asking when there is no terminal | An unapproved delete happens in a script |

## 9. The second job-board system

Ashby's public posting API (`https://api.ashbyhq.com/posting-api/job-board/<name>`) returns
`{"jobs": [...], "apiVersion": ...}`. Its IDs are UUIDs, so `PostingId` accepts a lowercase UUID
as well as a positive decimal. Each Ashby job is mapped onto the field names the CONTRACT
rule reads, so the rule and its evidence validator do not change:

| Rule path | Ashby field |
|---|---|
| `$.title` | `title` |
| `$.content` | `descriptionHtml` (plain HTML, not entity-escaped; the same cleanup is safe on it) |
| `$.location.name` | `location` |
| `$.departments[0].name`, `$.departments[1].name` | `department`, `team` |
| `$.updated_at` | `publishedAt` |

A record's posting paths therefore name the mapped view, not Ashby's own field names. The saved
raw bytes keep Ashby's names; this table is the key between them.

## 10. Amendments

Each amendment is dated, says what changed and why, and is committed before the code or run
that depends on it.

**A1 (2026-11-09, written while designing the fetcher; committed with the loop code in 0afcf05).** A request is one GET attempt. Redirect hops inside
one attempt are recorded in the trace but are bounded by `http.max_redirects` (3), not by
`max_requests`. Reason: the JS1 fetcher follows redirects inside one call, so counting hops
against the budget would mean putting the budget inside the transport. None of the planned
boards redirects. 

**A2 (2026-11-09, after the finished-wrong-answer runs `2026-11-09T08-16-13Z` and
`2026-11-09T08-16-16Z`, before the test and the patch).** A planned board may carry
`min_postings`, from the company's careers page (the same numbers
as `checks/expectations.toml`). When a board's response parses but lists fewer postings than
its floor, the board is a **failed board**: its JS1 run is `INVALID_RESPONSE` with the code
`below_floor`, its state is not written, its saved response is kept, and the loop cannot end
`FINISHED`. An empty board stays `EMPTY_RESPONSE`. A board with no `min_postings` has no floor.
A floor changes only by a new amendment. Floors for the current plans: `greenhouse/stripe`
100, `greenhouse/figma` 20, `ashby/ramp` 20, `ashby/linear` 5, and `greenhouse/ramp` 20 (it is
Ramp). The deliberately bad `ashby/linearapp` keeps no floor: it must fail by its 404 alone.

Reason: `greenhouse/ramp` ended `FINISHED` and `SUCCESS_NO_NEW` with one stale posting
("Copy of Chief Legal Officer", location "dublin") while Ramp's careers page lists 169 jobs on
Ashby. Only the independent check caught it. The loop cannot see which system a careers page
links to (that host is off the allow-list, on purpose), so the floor is the part of that
check the loop can enforce itself.

**A3 (2026-11-09, after the independent review in `docs/js2/REVIEW_BY_AGENT.md`; predictions
written before the new tests ran).** Corrections:

1. **The plan cannot widen the policy.** The hosts and the write folder are ceilings in code
   (`policy.HOST_CEILING`, `policy.WRITE_CEILING = "data/watch"`). A plan may narrow them, never
   widen them. The plan file must pass the read check *before* it is parsed, and must not lie
   anywhere the agent can write. Before this, a plan passed with `--plan` could allow any host or
   set `write_root = "data"`.
2. **The résumé read is checked.** At loop start the résumé path must pass the read check
   (never `private/`), or the loop ends `ERROR` before any request.
3. **Never-actions, stated precisely.** They are enforced by the agent having no tool that could
   apply, email, message or log in, and by GET-only requests (B06). `check_action` is the
   name-level list (B19); no current tool calls it.
4. **A retry the budget forbids** leaves the board with its real failure and saved body,
   not a synthetic budget error. **The repeat counter** spans the whole loop run, not
   one board.
5. **`jsa watch reset` validates the board token** with the provider, as the plan check does,
   before it asks anything.

New boundary cases and their predictions:

| # | Request | Predicted result |
|---|---|---|
| B21 | A plan allowing `jobs.lever.co` | Refused before any request (`ConfigError`: hosts outside GATE) |
| B22 | A plan with `write_root = "data"` | Refused (`ConfigError`: write_root must be inside `data/watch`) |
| B23 | A plan file inside `data/watch/` | Refused before parsing (`ConfigError`: the agent could write it) |
| B24 | A plan file in `private/` | Refused before parsing (read: `private`) |
| B25 | A plan with `write_root = "data/watch/sub"` and only the Greenhouse host | Allowed (narrowing is fine) |
| B26 | `config/agent.toml` points the résumé at `private/` | Loop `ERROR`, `resume_read_refused:private`, 0 requests |
| B27 | `jsa watch reset greenhouse/x/../ashby-ramp` | Refused as an invalid token, nothing asked, nothing deleted |

**A4 (2026-11-09, after a second audit of the whole repo).** Three corrections, each with its test written and seen failing first:

1. **An I/O error on a board** (for example a full disk while its raw response is saved) ends the
   loop `ERROR` like any other board error, with its trace and report written. Before A4 it
   left no report and the command exited 5. Test: `test_disk_error_still_ends_with_one_exit_and_a_report`.
2. **The board that stops the loop** is reported `FAILED`, with the error's type as its note and
   the requests it used, not `NOT_ATTEMPTED`. Test: `test_corrupt_state_stops_the_loop_with_error`.
3. **The independent check counts every listed job**, as the agent does, so a job without an ID
   no longer makes a correct agent fail the check. Only jobs with an ID can be new. Test:
   `test_count_includes_a_job_without_an_id`. The check's output on every committed loop run is
   unchanged.

Also: Ctrl-D at the `jsa watch reset` question is a no (nothing deleted), not a crash.
