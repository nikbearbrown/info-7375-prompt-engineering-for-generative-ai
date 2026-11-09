# Job-Search Agent 2 — Gate

Tushar Patel · INFO 7375 · Fall 2026

Version 0.2 · November 9, 2026

## Scope and boards

I'm building on my JS1 Stripe watch in `fall-2026/tushar-p/js1-contract-and-watch/` at commit `cb4333e`. I want to keep the same baseline and new-ID behavior, then see what happens when the watch has several boards and one fails. The watch uses public HTTP reads and deterministic checks, so it can run without model calls, credentials, or personal data.

| Board | API host | Role |
|---|---|---|
| `greenhouse/stripe` | `boards-api.greenhouse.io` | Keep the board from JS1. Terminal preflight returned HTTP 200. |
| `ashby/notion` | `api.ashbyhq.com` | Add an Ashby board. Terminal preflight returned HTTP 200. |
| `ashby/linear` | `api.ashbyhq.com` | Add a second Ashby board. Terminal preflight returned HTTP 200. |
| `greenhouse/info7375-tushar-js2-deliberately-invalid-20261109` | `boards-api.greenhouse.io` | Use this made-up token in the demo config. Terminal preflight returned HTTP 404. I expect zero retries and no job count for this board. |

My prediction for the live demo is three successful boards, one recorded failure, and an `incomplete` exit. On November 9, 2026, the sandboxed `curl` checks failed at DNS. The same checks outside the sandbox returned the statuses above. The checks recorded HTTP status only. The agent's live run is still pending.

## Loop, budgets, and exits

I want the loop to visit boards in config order. For each board, check permission and budget before fetching. Save the raw response, validate the posting list, compare IDs with that board's saved state, and record the result.

Keep Greenhouse IDs as integers and Ashby IDs as strings. Key the seen IDs by provider and board token so one board can't affect another. On a board's first successful fetch, save a baseline and report zero new IDs. The summary should show the fetched count and the new count separately. Update seen IDs only after saving and validating the raw response. If the board fails, keep its old state.

- **5 distinct boards.** If the same `(provider, board token)` appears twice, skip the duplicate and log it. A retry still belongs to the same board.
- **12 HTTP attempts.** Count every outbound request, including retries. A request denied before it goes out costs zero attempts.
- **60 seconds.** Use a monotonic clock for the whole run. Cap each HTTP attempt, including retries, at 10 seconds or the remaining time, whichever is shorter. Leave room to save the final trace and summary. When time runs out, start no new requests or state updates.
- **Changing the limits.** Only I can change the budgets or request timeout, through a dated entry in the decision log. The board config can choose which boards to run within those limits. It can't raise them.

If more than one exit applies, use this order: `error` → `budget-exhausted` → `incomplete` → `finished`. For example, if a board fails and the run hits a budget with another board still pending, report `budget-exhausted` and keep the earlier failure in the trace.

| Exit | When it applies | Report |
|---|---|---|
| `finished` | Every distinct scheduled board succeeded within budget. | Fetched and new counts by board, plus any duplicates skipped. |
| `incomplete` | The loop got through the schedule, and at least one board failed. | Counts for successful boards and a reason for each failure. Leave both counts unset for failed boards. |
| `budget-exhausted` | The loop hit a limit with work left to do. | Which limit it hit, the results so far, and the boards or retries still pending. |
| `error` | The run itself can't continue, for example because the config is invalid, the state is unusable, or evidence can't be saved. | What failed, the results so far, and what's pending. Use stderr if the output folder is unavailable. |

## Board failure policy

- Give a timeout or HTTP `5xx` one retry after a 1-second wait. Start the wait only if there's a request left and enough time for the wait and another attempt. Count the wait against the 60-second budget and check the budget again before retrying. If the budget prevents the retry, keep the original failure in the trace and report the retry as pending. Log the first failure and retry separately.
- For a `404`, another `4xx`, a permission denial, or a malformed response, record the failure and move to the next board. A bad token or a denied operation needs a config or policy change before another try makes sense.
- Count zero only when a valid response contains an empty `jobs` list. Treat a transport error, an empty body, or an invalid schema as a failure. Save the response bytes if there are any and log the error even if no bytes came back.
- In the trace I want to see the board, operation, attempt number where applicable, elapsed time, response status or error, raw file path if there is one, and what the loop did next. Save the trace for partial runs too if the output folder is available.

## Permission policy

- **Network reads.** Allow unauthenticated HTTPS `GET` only on the two exact API hosts above, on the default HTTPS port and the configured board's listing route. Refuse URL user info, off-list hosts, other paths, and all redirects. Treat links and text from postings as data.
- **Local reads.** Read the selected board config, `out/state.json` under the default output folder, and the selected fixture if I explicitly choose an offline demo. If I choose a different output folder, use its `state.json`. Deny other local reads before opening a file. A board response can't choose a file or supply a path.
- **Local writes.** Put the trace, summary, raw responses, and state inside the local output folder, which defaults to `out/`. Check that the real path stays inside that folder, including for temporary files. Refuse any symlink in the path that can redirect the write. I choose the output folder locally. Board input can't change it.
- **Protected write.** The regular run writes the summary. Writing `out/protected/shortlist.json` needs my explicit approval for that destination, those exact bytes, and that run. If I choose a different output folder, the same rule applies to `protected/shortlist.json` inside it. My approval can't extend beyond the output folder.
- **Forbidden actions.** Block applications, emails, messages, logins, and ATS write requests before they can happen.

## Wrong versions the tests must catch

| What could go wrong | What I expect the check to show |
|---|---|
| The loop turns a failed fetch into an empty list and exits `finished`. | The failed board has no counts and the completed schedule exits `incomplete`. |
| A prefix check lets a write through to `out-evil/` or through a symlink outside `out/`. | The write is refused and the outside file is untouched. |
| The loop retries a 404 or forgets to count a timeout retry. | The 404 gets one attempt. A transient failure gets at most one retry, and both attempts count. |
| A slow request gets the whole run budget, or the retry skips the wait. | The attempt is capped at the smaller of 10 seconds and the time left. The retry waits 1 second and rechecks the budget. |
| A board failure hides a later budget limit or fatal error. | The final exit follows the precedence above, and the earlier board failure stays in the trace. |
| Two boards share the same ID, or a failed fetch clears the board's state. | Each board keeps its own seen IDs. A failed fetch leaves its state alone. |
| The code drops postings and still reports `finished`. | An independent count from the saved response catches the difference. |

The [permission boundary table](evidence/PERMISSION-BOUNDARIES.md) lists the expected results before any tests run.

## Finished with the wrong answer

I'll use a labeled offline demo, `--seed-wrong-empty`, with a saved board response and a separate copy of that board's existing seen IDs. The fixture will have at least one ID absent from the seen list, so the board already has a baseline and the correct new count is greater than zero.

The demo will save the original response and then deliberately feed an empty `jobs` list to the normal counting step. I expect the loop to report zero new jobs and exit `finished`. A separate check will read the original JSON and the pre-run seen IDs directly, compute the set of new IDs, and compare it with the agent's report. I'll save the fixture, starting state, report, and check output together. The demo will use its own output folder and state.

## Decision log

| Date | Owner | Entry |
|---|---|---|
| 2026-11-09 | Tushar Patel | Initial draft v0.1. |
| 2026-11-09 | Tushar Patel | Draft v0.2 incorporates review feedback: exit precedence, a 10-second request cap, a 1-second retry wait, and a seeded wrong-answer demo. It clarifies who can change budgets and which path needs approval, and adds predictions for local reads and approval reuse across runs. |
| 2026-11-09 | Tushar Patel | I approved v0.2 and its permission predictions for the pre-code commit. |
