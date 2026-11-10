# GATE.md — Job-Search Agent 2: The Loop, the Tools, and the Diff

## Executive summary

This file is written before any code, per the assignment's own rule.
It defines every way the loop can end, its budgets, what counts as a
repeat, how it handles a failed board, what it's allowed to touch, and
two plausible-but-wrong implementations the tests must catch.

## Boards and ATS systems

- `gitlab` — Greenhouse (`boards-api.greenhouse.io/v1/boards/gitlab/jobs`)
- `stripe` — Greenhouse (`boards-api.greenhouse.io/v1/boards/stripe/jobs`)
- `palantir` — Lever (`api.lever.co/v0/postings/palantir`)

One board, `badslug-gitlab-typo`, is used ONLY to exercise the deliberate
failure path (Step 2) — it is not a real target board.

## Exits

Every run ends in exactly one of these, reported explicitly in the run's
final output — a loop that stops silently is a bug, not a success:

- `finished`: every board in the run list was attempted, and the budget
  was not exceeded.
- `incomplete`: one or more boards were not attempted ONLY because they
  were refused for lacking `--approve-new-board` (see Permission policy).
  Reports which boards were refused. A budget hit is never `incomplete`.
- `budget-exhausted`: any budget (requests, seconds, or boards) was hit,
  at any point in the run. Reports which budget, its configured limit,
  and which boards were never attempted.
- `error`: an unrecoverable condition stopped the whole run (e.g. the
  state file is corrupted and unreadable), or every attempted board
  failed (see Error policy). Reports the exception or the reason.

Precedence when more than one applies: `error` > `budget-exhausted` >
`incomplete` > `finished`.

### Per-board status

Every board in the run list ends with exactly one of:

- `ok`: fetched and parsed; state updated (a first run is a baseline).
- `failed`: the error policy gave up on it; carries the real error.
- `refused`: new board without `--approve-new-board`; no request made.
- `interrupted`: a budget was hit after at least one request for this
  board (mid-pagination or mid-retry). Its partial data is discarded and
  its state file is left unchanged.
- never attempted: listed in the run's `not_attempted`, no request made.

A single board failing (Greenhouse 404, timeout, malformed JSON) is NOT
by itself a loop-level `error` — see Error policy below. It only becomes
`error` if the error policy's own retry/escalate logic is itself unable
to proceed.

## Budgets

- `MAX_BOARDS_PER_RUN = 5` (we use 3; headroom for the assignment's
  "at least three" without silently watching an unbounded set)
- `MAX_REQUESTS_PER_RUN = 15` (3 boards × up to 5 requests each,
  accounting for Lever's pagination)
- `MAX_SECONDS_PER_RUN = 120`

A budget changes only by editing this file and committing the change —
never silently in code, never via a CLI flag that isn't itself logged.

Every HTTP request counts against `MAX_REQUESTS_PER_RUN`, including each
retry and each Lever page.

## Repeat rule

Two observations are "the same" if they share both: (board, posting id).
A posting id already in that board's seen-state is not re-reported, even
if its title or content text changed since last seen (content *changes*
on an already-seen id are a known, named limitation — see FRICTIONAL.md
candidate list). The loop does not re-fetch a board already successfully
completed earlier in the same run.

## Error policy

On a failed board (bad slug/404, empty response, timeout):

- Retry up to 2 times, with a 1-second backoff, ONLY for a timeout or a
  5xx response (transient conditions). A retry here is sound because
  these are the specific failure classes a public API can recover from
  within seconds; it is not sound for a 404 (bad slug), which will never
  resolve by retrying.
- A 404 or a malformed/unparseable response is NOT retried — it fails
  that board immediately and the run proceeds to the next board.
- An empty response body is malformed: the board is `failed`. A
  well-formed response with no postings (Greenhouse `{"jobs": []}`, Lever
  `[]`) is a valid board with zero postings: `ok`, not `failed`.
- A failed board is recorded explicitly as `board_status: "failed"` with
  the real error, and contributes ZERO postings to the run's new-postings
  list. It is never silently treated as "zero new postings found" — those
  are different, explicitly distinguished states.
- The loop does not escalate a single board failure to a full run
  `error` exit unless ALL boards in the run fail. "All boards" means every
  board that was attempted: refused and never-attempted boards are not
  counted, and at least one board must have been attempted.

## Permission policy

Enforced in code (`agent/permissions.py`), not just described in a prompt:

- **May call**: `boards-api.greenhouse.io` (HTTPS only), `api.lever.co`
  (HTTPS only). `api.anthropic.com` is NOT on the list yet: JS2 has no
  judgment code. It is added back, here and in `agent/permissions.py`,
  in the same change that adds judgment code.
- **May write**: only inside `evidence/`, `state/`, `logs/`, each
  resolved to an absolute real path and checked that the write target is
  actually inside it (no `..`, no symlink escape, no sibling-directory
  prefix trick).
- **Never**: apply to a job, send email, send any message, log in
  anywhere, or write outside the three allowed directories. There is no
  code path for any of these — not a check that refuses them, an absence
  of the capability.
- A write to a NEW board's state file (one not yet in `state/`) requires
  an explicit `--approve-new-board <name>` flag; without it, the loop
  refuses to create state for a board it hasn't seen approved before,
  even if that board is otherwise allow-listed for fetching.

## Wrong versions (tests must catch both)

1. **Budget silently ignored**: an implementation that logs "budget
   exceeded" but keeps making requests anyway. Test: set
   `MAX_REQUESTS_PER_RUN = 2`, run against 3 boards, assert exactly 2
   requests were made and the exit status is `budget-exhausted`.
2. **Failed board reported as "no new jobs"**: an implementation that
   catches the fetch exception but then falls through to the normal
   "0 new postings" code path instead of a distinct `failed` state. Test:
   force a 404 on one board, assert that board's status is literally
   `"failed"` with the real error message, NOT merged into a report that
   says "no new jobs."

## What a failure looks like

*(dated before any code was run)*

**2026-11-09**: a failure is any run where a board that actually failed
(404, timeout, malformed response) is reported in the final output as
having "no new postings," indistinguishable from a board that was
successfully fetched and genuinely had nothing new. These are different
facts and must never collapse into the same sentence.

## Toolchain

- Language: Python 3.x (same as JS1)
- New host: `api.lever.co` added to the allow-list, alongside JS1's
  `boards-api.greenhouse.io`
- No external services beyond the two allow-listed hosts

## Amendments

**2026-11-09** — after the first implementation pass, to settle questions
this file left open. Every change made in this pass:

1. Exits: `incomplete` now means ONLY "boards refused for lacking
   `--approve-new-board`". The old example ("a budget limit hit mid-run")
   was removed; any budget hit is `budget-exhausted`. Added exit
   precedence.
2. Exits / Error policy: the `error` exit for board failures means every
   *attempted* board failed; refused and never-attempted boards don't
   count.
3. Added a "Per-board status" section, including the new `interrupted`
   status (budget hit mid-board: partial data discarded, state unchanged).
4. Budgets: retries and Lever pages count against the request budget.
5. Error policy: an empty body is `failed`; `{"jobs": []}` is a valid board
   with zero postings.
6. Permission policy / Toolchain: removed `api.anthropic.com` from the
   allow-list until judgment code exists; "three allow-listed hosts" is
   now "two".

## Amendment 2026-11-10: removal detection

**Written AFTER the code.** Every earlier section of this file came before
the code it governs; this one does not. Removal detection was built as the
review packet's chosen non-trivial change, from the task request, and the
code (`d3e2e8a`) went in before this file said anything about it. The gap
was caught only during the packet's own scope-review step
(REVIEW-PACKET.md, Step 4). That is a real process finding, recorded here
rather than hidden: the test-first discipline held (`8bb6a17` came before
`d3e2e8a`), but spec-first did not.

- **`removed`** — a per-board report field: a sorted list of posting ids
  that were in the board's previous successful fetch and are absent from
  the current one. It is present, possibly empty, on every board entry
  whatever its status. It is empty for a baseline run and for `failed`,
  `refused` and `interrupted` boards. Boards that were never attempted have
  no entry at all. It is separate from `new` and from `board_status`: a
  removal never changes a board's status or the run's exit.
- **`last_fetch_ids`** — a state-file field: the full id set from the
  board's most recent successful fetch, rewritten on every successful
  fetch. It is used to compute `removed` on the next run. A state file
  written before this amendment has no `last_fetch_ids`. Until that board's
  first successful run after this change, `seen_ids` is used instead.
  Failed runs do not update state, so that fallback lasts until the first
  success, after which `last_fetch_ids` exists.
- **Once-only reporting** — a removed id is reported exactly once, on the
  run where it is first found missing, and never again on later runs. If
  the id comes back, it is not reported as new (the repeat rule still
  holds). If it later goes missing again, that is a new removal and is
  reported again, once.

