# GATE — Job-Search Agent 2

Written before any agent code exists in this folder (see the commit that adds this file alone).
Drafted with Claude Code on 2026-11-08 at Smit's request and committed by itself, so the
history shows the gate came before the code. Smit owns every decision below; a change to any
number here needs a new dated entry in the "Decisions" log at the bottom.

## What the loop does

One run visits a fixed list of public job boards (`config/boards.json`), fetches each board's
public JSON once, saves the raw response, parses the postings, compares their ids with the ids
seen last time, and reports the postings that are new. It reads; it never acts on a posting.

## Exits

A run ends in exactly one of four statuses, written to `summary.json` and printed last.
A run that stops is not a run that succeeded: only `finished` means "every board was read and
every count can be trusted".

| Exit | When | What it reports |
|---|---|---|
| `finished` | Every configured board was attempted within budget, every board returned a valid response, and no board was flagged suspect. | Per-board count, new posting ids, and the raw-response path behind each count. Exit code 0. |
| `incomplete` | Every board was attempted, but at least one failed (bad name, timeout, bad response) or was flagged suspect (an empty response after a non-empty baseline), and at least one board succeeded. | The same as `finished` for the good boards; for each failed or suspect board the reason, the HTTP status, and `count: null`. A failed board never reports 0. Its baseline is not overwritten. A `NEEDS HUMAN` line names each one. Exit code 2. |
| `budget_exhausted` | A budget (boards, requests, or seconds) ran out before every board was attempted. | Which budget, its limit, the boards not attempted (listed by name), and the results for the boards that were. Exit code 3. |
| `error` | The run could not do its job at all: invalid config, an attempted call or write that the permission policy denied, a state write that failed, or every board failed. | The error and the step where it happened. No state is updated. Exit code 1. |

## Budgets

| Budget | Limit per run | Why |
|---|---|---|
| Boards | 5 | Three real boards plus one deliberate failure fit, with one spare. |
| Requests | 12 | One request per board, plus one retry each, plus margin. Retries count. |
| Wall-clock seconds | 60 | A healthy run takes under 10 s; 60 s means something is wrong. |
| Retries per board | 1 | See error policy. |
| Minimum gap per host | 1.0 s | Lever's robots.txt asks for `Crawl-delay: 1`; the same gap is applied to every host. |

Budgets live in `config/budgets.json`. The program treats any write to `config/` as a write that
needs approval (see the permission policy), so the agent cannot raise its own budget. A budget
changes only when Smit adds a dated entry to the Decisions log below and either edits the file
directly or approves the write.

## Repeat rule

"The same action" means the same `(method, normalized URL)` pair, where normalization lowercases
the scheme and host and drops a default port. The loop:

1. Removes duplicate boards from the config before starting and records each removal in the trace.
2. Allows an identical request a second time only as the single retry the error policy permits.
3. Refuses a third identical request, records `repeat_blocked` in the trace, and does not count it
   as an observation.

A posting id that appears twice in one board's response is counted once and the duplicate is
recorded.

## Error policy

| What happened to a board | Retry? | Why | Result |
|---|---|---|---|
| HTTP 404 (bad board name) | No | The name is wrong; asking again returns the same answer. | `failed:not_found`, `count: null` |
| Other HTTP 4xx (403, 429, …) | No | The server refused us; retrying would ignore the refusal. | `failed:http_<code>`, `count: null` |
| Timeout, connection error, or HTTP 5xx | Once, after a 2 s wait | The request is a read-only GET, so repeating it cannot change anything on the server, and these failures are often transient. One retry fits the request budget. | Success on retry: normal result, with both attempts in the trace. Second failure: `failed:unreachable`, `count: null` |
| 200 but the body is not valid JSON or lacks the expected shape | No | A broken body is not transient in a way a retry would fix. | `failed:bad_response`, `count: null` |
| 200 with zero postings when the previous baseline had postings | No | It might be real (hiring paused) or a fault (outage, migration). The agent cannot tell which. | `suspect:empty_after_nonempty`, `count: 0` recorded as observed but not trusted, baseline kept, escalated to Smit |

Escalation means a `NEEDS HUMAN:` line in the run output and in `summary.json`. The agent never
fills in a missing value: no previous count, no guessed count, no zero for a failed board.

## Permission policy

Enforced in code (`agent/policy.py`), not in a prompt. Every network call and every file write
goes through it; the boundary tests in `tests/test_policy.py` and the table in `POLICY.md` check it.

**Hosts (allow-list, HTTPS only, default port, GET only, no credentials in the URL):**
`boards-api.greenhouse.io`, `api.lever.co`, `api.ashbyhq.com`. Everything else is denied,
including look-alikes such as `boards-api.greenhouse.io.evil.com` and IP literals.

**Read:** `config/`, `fixtures/`, and `jobs/` inside this assignment folder.

**Write:** `jobs/` only (state, runs, raw responses). Paths are resolved with symlinks followed
before the check, so `..`, a sibling folder like `jobs-evil/`, and a symlink pointing out of
`jobs/` are all denied.

**Writes that need Smit's approval:** anything in `config/` (boards, budgets, policy), and
deleting or resetting a board's baseline in `jobs/state/`. Without an explicit approval the
write is refused and recorded.

**Never:** apply to a job, send email, send a message, log in, send cookies or an Authorization
header, use any HTTP method other than GET, or call an `/apply` path. These are refused even if a
config file asks for them.

## Wrong versions the tests must catch

1. **Empty means "no news."** A board that returns `200` with zero postings after a non-empty
   baseline is reported as "no new jobs" and the run says `finished`.
2. **Failure becomes zero.** A board that 404s or times out is reported with `count: 0` instead of
   `null`, which reads as "checked, nothing there."
3. **Prefix check for paths.** `path.startswith("jobs")` accepts `jobs-evil/`; a check on the
   unresolved path accepts a symlink that leaves `jobs/`.
4. **Suffix check for hosts.** `host.endswith("greenhouse.io")` accepts `evilgreenhouse.io`;
   a substring check accepts `boards-api.greenhouse.io.evil.com`.
5. **Retry everything.** Retrying a 404 burns budget and pretends a bad name is transient.
6. **Stop means success.** Running out of budget ends the loop and still prints `finished`.
7. **Baseline overwritten by a failure.** A failed or suspect board replaces the good baseline,
   so the next run reports every old posting as new.
8. **Ashby unlisted postings counted.** Counting Ashby jobs without checking `isListed`.

## Decisions

| Date | Decision | By |
|---|---|---|
| 2026-11-08 | Initial budgets and policy as above. | Smit (drafted with Claude Code) |
