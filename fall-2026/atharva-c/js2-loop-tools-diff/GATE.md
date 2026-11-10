# GATE.md

## Exits

1. **finished:** every board succeeded and returned at least one job, nothing was flagged, and the run stayed within budget.
2. **incomplete:** at least one board came back empty (flagged) or failed (see Error Policy).
3. **budget-exhausted:** the loop hit 5 boards, 15 requests, or 60 seconds before it finished every board.
4. **error:** the code tried to do something the permission policy forbids (calling a host that isn't boards-api.greenhouse.io or api.lever.co, writing outside out/ without an approved exception, or sending a POST / applying) or the program crashed. The loop stops right away.

Every exit writes the status, the reason, and a list of which boards succeeded, were flagged, failed, or were skipped.

## Budgets

The run limits are 5 boards, 15 requests, and 60 seconds.

The 15-request cap allocates 1 primary request per board (5 total) plus at most 1 retry per board for timeouts or 5xx responses (5 total), leaving 5 spare requests. Spares cannot be used for a second retry on any board, because the retry policy allows only one attempt per board.

Only I change these numbers, by editing GATE.md with the date and a reason and committing that change before modifying the code.

**Added Nov 9, 2026:** each request times out after 10 seconds (or less, if fewer seconds remain in the 60-second budget). A timeout counts as a timeout under the Error Policy (one retry). This number was in `budget.json` from the first loop commit (`4369abf`, Nov 8) before it was written here; I decided on Nov 9 to keep it, so one slow board cannot use most of the run's 60 seconds.

## Repeat Rule

Two actions are the same if they target the same normalized URL with the same HTTP method. URLs are normalized by converting the hostname and path to lowercase and stripping any trailing slash, making `.../boards/Acme/jobs` and `.../boards/acme/jobs/` identical.

The loop never executes the same request more than once per run, except for a single retry on a timed-out or 5xx response. Any other duplicate request is skipped immediately, noted in the exit report, and does not consume any of the 15-request budget.

## Error Policy

* **Timeout or 5xx response:** Wait 2 seconds and retry once; a single retry is reasonable because a transient network drop or temporary server blip may clear, whereas a persistent outage will not and would quickly exhaust our 60-second budget.
* **404 or bad board name:** Mark as failed with no retry. A 404 is deterministic; querying the exact same missing path a second time will yield the same error.
* **Any other 4xx (for example 403 or 429):** Mark as failed with no retry. Only timeouts and 5xx responses are retried.
* **200 OK with zero jobs:** Flag as empty-response with no retry. The empty list could be caused by a mistyped board name, a changed API endpoint, an archived board, or genuinely no open roles, and the response alone cannot tell you which one it is.
* **Non-JSON response:** Mark as failed with no retry. An unparseable body indicates an unexpected gateway page or HTML error, neither of which the parser can salvage.
* **Data integrity:** The agent never invents, synthesizes, or fills in placeholder data for a board that failed, was flagged, or was skipped.

## Permission Policy

* **Allowed hosts:** `boards-api.greenhouse.io` and `api.lever.co` only.
* **Allowed HTTP methods:** `GET` only.
* **Filesystem access:** The code may read configuration files and the target board list from the `js2-loop-tools-diff/` folder; all file writes are strictly confined to `out/`. The only exception is a write to `boards.json`, the budget config, or `GATE.md`, which is allowed only when the run is started with `--approve`. The seen-jobs record lives at `out/seen.json` and is written by normal runs.
* **Approvals required:** Changing the target board list, modifying budget caps, or altering rules in this document requires my prior written edit and commit. In the program, a write to `boards.json`, the budget config, or `GATE.md` is blocked and logged unless the run is started with `--approve`.
* **Forbidden actions:** The agent must never send a POST request, submit a job application, fill out web forms, authenticate, log in, send emails, or send messages.

## Wrong versions

See WRONG_VERSIONS.md
