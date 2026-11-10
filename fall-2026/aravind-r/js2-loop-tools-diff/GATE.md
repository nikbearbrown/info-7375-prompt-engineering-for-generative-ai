# GATE.md — DRAFT proposed by Claude Code, 2026-11-10 (not yours until you edit and commit it)

> Claude drafted this. Delete this banner, change anything you disagree with, then save it
> as `js2-loop-tools-diff/GATE.md` and commit it yourself *before* any loop code is written.
> Name this draft in SOURCES.md.

Job-Search Agent 2 watches several public job boards in one bounded run. This file is the
spec. The code enforces it; where the code and this file disagree, this file wins and the
code is wrong.

## Boards (boards.json)

| id | system | token | why |
|---|---|---|---|
| gh-stripe | Greenhouse | `stripe` | JS1's board; 200 on 2026-11-10 |
| gh-airbnb | Greenhouse | `airbnb` | second Greenhouse board; 200 on 2026-11-10 |
| lv-spotify | Lever | `spotify` | second system; 200, 84 postings on 2026-11-10 |
| gh-broken | Greenhouse | `no-such-board-js2` | **deliberate failure**: 404 on 2026-11-10 |

## Exits

A run ends in exactly one status. Precedence when several apply: `error` > `budget-exhausted` > `incomplete` > `finished`.

| status | when | reports | exit code |
|---|---|---|---|
| `finished` | every board in the config was observed successfully, within budget | per-board counts and new postings | 0 |
| `incomplete` | the run reached the end of the board list, but ≥1 board failed | the successful boards' results **and** each failed board's error; a failed board shows `error`, never `0 jobs` | 10 |
| `budget-exhausted` | a budget would be exceeded by the next action, so the loop stopped before it | what was observed so far, the budget that hit, and the boards never attempted | 11 |
| `error` | the run itself can't be trusted: bad config, a policy refusal of the loop's own write, unreadable state | the reason; nothing reported as new | 12 |

"Finished" means the loop stopped normally. It does not mean the answer is right; `src/check.mjs` decides that (see Independent check).

## Budgets (per run)

| budget | limit |
|---|---|
| boards | 5 |
| HTTP requests (retries count) | 8 |
| wall-clock seconds | 60 |
| per-request timeout | 15 s |

The loop checks a budget **before** each action, not after. A config or CLI flag can lower a budget but never raise one. A budget changes only when I add a dated line to "Decisions" below and commit it. The constants in `src/policy.mjs` must match this table; a test checks this.

## Repeat rule

- "The same action" = same method + same normalized URL (lowercased host, sorted query) in one run.
- A repeat is refused by the policy unless the error policy authorized it as a counted retry.
- A board listed twice in boards.json (same system + token) is fetched once; the duplicate is logged as `skipped: duplicate`.
- Across runs, an identical id set is recorded as `unchanged`, not as an error.

## Error policy

| failure | action | why |
|---|---|---|
| network error, timeout, HTTP 5xx, HTTP 429 | retry **once** after 2 s, if the budget allows | transient by nature; one retry is cheap and bounded |
| HTTP 404 / 4xx | no retry; record `error: not found` | a bad board name won't get better on a retry, and a retry only spends budget |
| body not JSON, or no job list where the system promises one | no retry; record `error: malformed` | deterministic; same bytes again |
| empty job list (`[]`) on a board whose last saved state had > 0 ids | record `suspect: empty`; do **not** overwrite state | an empty board is more often an outage or a renamed board than a company with zero jobs |
| same board fails on 2 consecutive runs | mark `escalate` in the report for me to look at | I decide whether the board is gone or the code is wrong |

A failed board never updates its state file and is never reported as `0 jobs` or `no new jobs`.

## Permission policy (enforced in `src/policy.mjs`)

**Network.** HTTPS, GET only, to exactly these hosts and paths:

| host | allowed path |
|---|---|
| `boards-api.greenhouse.io` | `/v1/boards/<token>/jobs` (query `content=true` allowed) |
| `api.lever.co` | `/v0/postings/<site>` (query `mode=json` allowed) |

Host match is exact; no suffix or substring match. Redirects are not followed (`redirect: 'manual'`); any 3xx is refused and recorded. No credentials: no `Authorization` or cookie header, no `user:pass@` in the URL.

Both hosts also serve application endpoints (Greenhouse accepts POSTed applications; Lever has `POST /v0/postings/<site>/<id>/apply`, and every Lever posting carries an `applyUrl`). That is why the allow-list is host **plus method plus path**, not host alone.

**Files.**
- Write: only inside `./out/`, judged by the resolved real path (symlinks resolved, `..` resolved). `out-evil/` beside `out/` is outside.
- Read: anywhere inside this project folder. Reading outside it is refused.
- Needs my approval (the loop has no approval path, so it refuses and records `refused: needs approval`): deleting anything under `out/`, or overwriting a state file with fewer ids than it holds.

**Never.** Apply, email, message, or log in. No code path in this project can send a POST, open a `mailto:`, or submit a form.

## Independent check (`src/check.mjs`)

A separate program that reads only `out/` (raw responses, state, trace) and recomputes each board's count and new set, not reading the loop's report as truth. It flags:
- a board reported `finished`/`0 new` whose raw response had an empty list while its previous state had ids;
- a reported new-count that differs from the recomputed diff;
- a state file whose id count differs from its raw response.

## Wrong versions the tests must catch

1. Host check by `endsWith`/`includes`: `boards-api.greenhouse.io.evil.example` passes.
2. Path check by `startsWith(out)` with no separator: `out-evil/x` passes.
3. Path check without `realpath`: a symlink `out/link → /tmp` escapes.
4. Host allowed but method not checked: `POST …/apply` reaches an allow-listed host.
5. `fetch` left at its default `redirect: 'follow'`.
6. A failed board counted as `0 jobs`, or its state overwritten with an empty list.
7. Retry on 404, or retry with no limit.
8. Budget checked after the request (N + 1 requests sent).
9. Status `finished` when a board failed.
10. Lever's UUID ids cast to `Number` (JS1's `state.mjs` does this: ids save as `[null]` and every run reports every posting as new; reproduced 2026-11-10 against a real Spotify response).
11. Duplicate board fetched twice.

## Decisions

- 2026-11-10: budgets set as above. (Aravind)
