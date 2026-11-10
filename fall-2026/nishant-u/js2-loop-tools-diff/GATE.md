# GATE — Job-Search Agent 2 (nishant-u)

Written by Nishant U on 2026-11-10, before Claude Code changed any code. Drafted with Claude (claude.ai); reviewed and approved by me. Starts from my JS1 (d63ee48, copied unchanged in ca43940).

## Boards (the plan for one run)
1. Greenhouse `faire` — https://boards-api.greenhouse.io/v1/boards/faire/jobs?content=true
2. Greenhouse `instacart` — https://boards-api.greenhouse.io/v1/boards/instacart/jobs?content=true
3. Ashby `poshmark` — https://api.ashbyhq.com/posting-api/job-board/poshmark
4. Greenhouse `poshmark` — a real board that returned 200 with 0 jobs on 2026-11-10 (used for the finished-wrong-answer demonstration)
5. Greenhouse `no-such-board-js2-test` — fails on purpose (returned 404 on 2026-11-10)

## Exits (controller status; every run ends in exactly one)
- **finished** — every planned board was attempted within budget and each returned a parsed response. It does NOT mean the answer is right; that is judged separately by the outcome check.
- **incomplete** — every planned board was attempted within budget, but at least one failed under the error policy. The report lists each failed board and why.
- **budget-exhausted** — a budget ran out before every board was attempted. The report lists the boards not attempted.
- **error** — bad configuration or an unexpected exception. Nothing is written to state.
Every report includes: exit status, per-board status, requests used, seconds used, new IDs per board, and the trace.

## Outcome check (separate from the controller)
A comparator that reads the saved raw responses, not the agent's parsed report: it flags any board whose raw response has zero postings, and any company whose posting count differs sharply across its two systems. The agent's own "finished" is never taken as proof.

## Budgets (per run)
- Boards: at most 5. Requests: at most 10, retries included. Wall-clock: at most 60 seconds.
- Budgets change only by a new dated entry in this file's Amendments, written by me.

## Repeat rule
The same action is the same (method, host, path and query) within one run. A repeated action is refused and recorded in the trace, except an error-policy retry, which is allowed and counted against the request budget.

## Error policy
- HTTP 404 or 410: no retry (a wrong name won't fix itself). The board is marked failed: not-found, and escalated in the report.
- HTTP 5xx, timeout or connection error: one retry after 2 seconds (a transient failure may pass). If it fails again, the board is marked failed and escalated.
- HTTP 200 that isn't valid JSON, or has the wrong shape: no retry. Marked failed: bad-response.
- No failed board ever gets an invented value: no fake postings and no "0 new" for a board that failed.

## Permission policy (enforced in code, not in a prompt)
- **Hosts (read only, GET):** boards-api.greenhouse.io, api.ashbyhq.com. Anything else is refused before any network call, including after a redirect.
- **Operations:** `fetch` (GET an allowed host), `write_run_file` (inside the output root), `update_state` (merge new IDs into the state file inside the output root), `reset_state` (replace the state file). Anything else is refused.
- **Containment:** writes only inside the output root, judged by the resolved path (resolve() and is_relative_to()), never a string prefix. `..` traversal, a sibling prefix like `out-evil` beside `out`, and a symlink pointing outside are refused.
- **Approval:** `reset_state` needs approval, which means approved is the boolean True; anything else ("yes", 1, missing) is refused. Approval never overrides the host or containment rules.
- **Never:** apply, email, message anyone, log in, POST, or delete anything.

## Boundary cases (prediction written before running)
| # | Case | Predicted |
|---|---|---|
| 1 | fetch https://boards-api.greenhouse.io/... | allowed |
| 2 | fetch https://api.ashbyhq.com/... | allowed |
| 3 | fetch https://api.lever.co/... (not on the list) | refused before any request |
| 4 | fetch an allowed host that redirects to evil.example | refused, no request to evil.example |
| 5 | write out/runs/r1/raw.json | allowed |
| 6 | write out/../escape.txt | refused (traversal) |
| 7 | write out-evil/x.txt (sibling prefix) | refused |
| 8 | write out/link/x.txt where link points outside out | refused (outside-pointing link) |
| 9 | read out/state/seen_ids.json | allowed (read, not write) |
| 10 | operation "delete" | refused (not in the vocabulary) |
| 11 | reset_state with approved=True | allowed |
| 12 | reset_state with approved="yes" | refused |
| 13 | reset_state with approved=True on a path outside out | refused (approval can't override containment) |
| 14 | a POST to an allowed host | refused |

## Wrong versions the tests must catch
1. **String-prefix containment:** checking startswith("out") accepts out-evil.
2. **Uncounted retries:** retries don't count against the request budget, so a failing board can loop past it.
3. **Finished despite a failure:** a run with a 404 board reports finished instead of incomplete.
4. **Truthy approval:** approved="yes" or 1 accepted as approval.
5. **Invented value:** a failed board reported as "0 new".

## What a failure looks like
2026-11-10, written before any run: *Failure is a run whose controller status is finished while a planned board failed, or any write that lands outside the output root.*

## Amendments
2026-11-10, before any code, after Claude Code's review of the gate:
1. Two run profiles. full = boards 1–5 (shows the deliberate failure; ends incomplete). demo = boards 1–4 (no failing board), used for the finished-wrong-answer demonstration. Outcome-check thresholds: flag any board whose raw response has 0 postings; flag a company that has 0 postings on one system and at least 1 on another (Poshmark: Greenhouse vs Ashby).
2. Add operation read_file (inside the output root; containment applies). Boundary case 9 is a read_file, predicted allowed.
3. update_state is a merge: it may only add IDs and must never drop one. Replacing the set is reset_state, which needs approval. Wrong version 6: an update_state that replaces the whole set instead of merging. New boundary case 15: update_state that would drop an existing ID → refused.
