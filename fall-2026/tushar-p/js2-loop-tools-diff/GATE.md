# Job-Search Agent 2 — Gate

Tushar Patel · INFO 7375 · Fall 2026

Version 0.4 · November 9, 2026

## Scope and boards

I'm building on my JS1 Stripe watch in `fall-2026/tushar-p/js1-contract-and-watch/` at commit `cb4333e`. I want to keep the same baseline and new-ID behavior, then see what happens when the watch has several boards and one fails. The watch uses public HTTP reads and deterministic checks, so it can run without model calls, credentials, or personal data.

| Board | API host | Role |
|---|---|---|
| `greenhouse/stripe` | `boards-api.greenhouse.io` | Keep the board from JS1. Terminal preflight returned HTTP 200. |
| `ashby/notion` | `api.ashbyhq.com` | Add an Ashby board. Terminal preflight returned HTTP 200. |
| `ashby/linear` | `api.ashbyhq.com` | Add a second Ashby board. Terminal preflight returned HTTP 200. |
| `greenhouse/info7375-tushar-js2-deliberately-invalid-20261109` | `boards-api.greenhouse.io` | Use this made-up token in the demo config. Terminal preflight returned HTTP 404. I expect zero retries and no job count for this board. |

On November 9, 2026, the sandboxed `curl` checks failed at DNS. The same checks outside the sandbox returned the statuses above. The response bodies collected during preflight are saved in [evidence/preflight/](evidence/preflight/). My Terminal preflight on November 9 also returned HTTP 404 for an invalid Ashby token (evidence/preflight/ashby-invalid.txt), so the same no-retry rule applies to both providers.

In [live run 1](evidence/runs/live-1/summary.json), Stripe succeeded, both Ashby boards returned HTTP 403, and the invalid Greenhouse token returned HTTP 404. The run exited `incomplete`.

## Loop, budgets, and exits

I want the loop to visit boards in config order. For each board, check permission and budget before fetching. Save the raw response, validate the posting list, compare IDs with that board's saved state, and record the result.

Keep Greenhouse IDs as integers and Ashby IDs as strings. Key the seen IDs by provider and board token so one board can't affect another. On a board's first successful fetch, stage a baseline and report zero new IDs. The summary should show the fetched count and the new count separately. Stage seen IDs only after saving and validating the raw response. If the board fails, keep its old state.

- **5 distinct boards.** If the same `(provider, board token)` appears twice, skip the duplicate and log it. A retry still belongs to the same board.
- **12 HTTP attempts.** Count every transport call, including retries and calls that fail before an HTTP response. A policy denial before transport costs zero attempts. I'm keeping the cap at 12. A valid config can use at most 10 attempts across five boards with one retry each, so tests exercise the 12-attempt guard directly. A live run can still exit `budget-exhausted` if the time budget prevents pending work.
- **60 seconds.** Use a monotonic clock for the whole run. Close the network window at 58 seconds and reserve 2 seconds to finalize evidence and state. Give each transport attempt the smaller of 10 seconds and the time left in the network window, subject to the DNS limit in F12.
- **Changing the limits.** Only I can change the budgets or request timeout, through a dated entry in the decision log. The board config can choose which boards to run within those limits. It can't raise them.

If more than one exit applies, use this order: `error` → `budget-exhausted` → `incomplete` → `finished`. For example, if a board fails and the run hits a budget with another board still pending, report `budget-exhausted` and keep the earlier failure in the trace.

| Exit | When it applies | Report |
|---|---|---|
| `finished` | Every distinct scheduled board succeeded within budget. | Fetched and new counts by board, plus any duplicates skipped. |
| `incomplete` | The loop got through the schedule, and at least one board failed. | Counts for successful boards and a reason for each failure. Leave both counts unset for failed boards. |
| `budget-exhausted` | The loop hit a limit with work left to do. | Which limit it hit, the results so far, and the boards or retries still pending. |
| `error` | The run itself can't continue, for example because the config is invalid, the state is unusable, or evidence can't be saved. | What failed, the results so far, and what's pending. Use stderr if the output folder is unavailable. |

## Board failure policy

- Give a timeout or HTTP `5xx` one retry after a 1-second wait. Apply the retry budget in F11. If the budget prevents the retry, keep the original failure in the trace and report the retry as pending. Log the first failure and retry separately.
- For other failures, record the reason and move to the next board. A request denied by policy or a board that returns `404` needs a config or policy decision before another try makes sense.
- A valid empty `jobs` list means zero fetched. Treat a transport error, an empty body, or an invalid schema as a failure. Save the response bytes if there are any and log the error even if no bytes came back.
- In the trace I want to see the board, operation, attempt number where applicable, elapsed time, response status or error, raw file path if there is one, and what the loop did next. Save the trace for partial runs too if the output folder is available.

## Permission policy

- **Network reads.** Allow unauthenticated HTTPS `GET` only on the two exact API hosts above, on the default HTTPS port and the configured board's listing route. Refuse URL user info, off-list hosts, other paths, and all redirects. Treat links and text from postings as data. Every outgoing request identifies the watch with `User-Agent: info7375-js2-watch/0.1 (student project; tushar-js2@example.com)`. The watch never impersonates a browser.
- **Local reads.** Read the selected board config, `out/state.json` under the default output folder, and the selected fixture if I explicitly choose an offline demo. If I choose a different output folder, use its `state.json`. Deny other local reads before opening a file. A board response can't choose a file or supply a path.
- **Local writes.** Put the trace, summary, raw responses, pre-run state snapshot, and shared state inside the local output folder, which defaults to `out/`. Check that each path stays inside the resolved root, including for temporary files. Apply the symlink rule in F19. I choose the output folder locally. Board input can't change it.
- **Protected write.** Writing `out/protected/shortlist.json` through the tested write gate needs my explicit approval for that destination, those exact bytes, and that run. If I choose a different output folder, the same rule applies to `protected/shortlist.json` inside it. My approval can't extend beyond the output folder. Normal runs only use the regular output paths.
- **Forbidden actions.** Block applications, emails, messages, logins, and ATS write requests before they can happen.

## Contract decisions (v0.3)

| # | Decision |
|---|---|
| F1 | JS2 fetches public postings, validates the response, and compares posting IDs. Persona data, relevance rules, and Claude calls are out of scope for the runtime. |
| F2 | The exact Greenhouse route is `/v1/boards/<token>/jobs`. The exact Ashby route is `/posting-api/job-board/<token>`. The path must match the configured board. Deny every other path and any query string, including JS1's `?content=true` (P09). |
| F3 | A response is malformed if it isn't valid JSON, its top level isn't an object, `jobs` is missing or isn't a list, or any job lacks a valid `id`. Greenhouse IDs are integers excluding booleans. Ashby IDs are non-empty strings. Count and compare unique IDs, and log how many duplicates were removed from the response. |
| F4 | Start with a fresh JS2 baseline in `out/state.json`. A board with no state entry reports zero new IDs on its first successful fetch. Reuse JS1's baseline logic with fresh data. The JS2 agent never reads JS1 state. |
| F5 | Stage successful board updates in memory. After writing run evidence, replace the shared state file atomically once at the end of a `finished`, `incomplete`, or `budget-exhausted` run. Keep the prior entries for failed or unattempted boards. On `error`, leave the existing state file alone. |
| F6 | A sixth distinct board makes the config invalid. Exit `error` before transport. Duplicate `(provider, token)` pairs are skipped and logged and count once toward the limit of five. |
| F7 | An unknown provider or a token that fails a full match of `[a-z0-9-]+` makes the config invalid. Exit `error` before transport. A denial when checking a request during the run is a board failure. |
| F8 | An attempt is one call into the transport, including a DNS or connect failure. A redirect response counts as one attempt. The agent refuses the next hop. |
| F9 | Retry only timeouts and HTTP `5xx`. DNS errors, connection resets, `429`, other `4xx`, and `3xx` are board failures with no retry. |
| F10 | Set the network deadline at 58 seconds from run start and reserve the last 2 seconds for local finalization. Each attempt gets the smaller of 10 seconds and the remaining network time, subject to F12. |
| F11 | Retry only if a request remains and at least 2 seconds of network time remain for the 1-second wait and at least 1 second of attempt time. After the wait, check the request budget and the 1-second minimum again before starting the retry. |
| F12 | Use one monotonic attempt deadline for the phases the standard-library client can time out. Use the remaining time for connection and header timeouts and a deadline-bounded chunked body read. A blocking system DNS lookup through `getaddrinfo` can outlast that deadline. Its elapsed time still counts, so recheck the deadline when it returns and do not continue an expired attempt. List DNS timing under “Not checked” at sign-off. |
| F13 | If budget blocks an otherwise eligible retry, record it as pending and exit `budget-exhausted`. Keep the original failure in the trace. |
| F14 | Zero configured boards makes the config invalid. Exit `error` before transport. |
| F15 | CLI exit codes are `finished` = 0, `error` = 2, `incomplete` = 3, and `budget-exhausted` = 4. Use JSON `null` for unset counts. |
| F16 | The shortlist path is a tested permission boundary. Use an in-code `Approval(dest, sha256, run_id)` bound to the destination, exact bytes, and run. JS2 has no CLI approval option and normal runs never write the shortlist. Include this limit under “Not claiming” at sign-off. |
| F17 | Before staging any updates, the agent writes `out/runs/<run_id>/pre-run-state.json` from the state it loaded. Write JSON `null` if there was no state file. I'll run `checks/independent_count.py` separately after live runs and in the seeded demo. It reads the raw response and the snapshot directly, compares the result with the report, and never changes the agent's exit or state. It's a separate read-only program outside the agent's file policy. |
| F18 | In offline mode, `--fixture <path>` grants a read to that fixture's exact resolved path only. For the seeded demo, copy JS1's `raw/greenhouse-stripe-2026-10-28T141616.json` into `fixtures/` and build isolated pre-run seen IDs from JS1's `raw/greenhouse-stripe-2026-10-27T203128.json`. Label the replay seeded. The saved October 28 response has 16 IDs absent from October 27. |
| F19 | Reject a symlink at the selected output root itself, then resolve the root's real path once at startup so aliases in its ancestors, such as `/var` → `/private/var`, work. Reject symlinks in managed paths below that root, even when the target stays inside it. |
| F20 | Give each run its own `out/runs/<run_id>/` folder for raw responses, trace, summary, and the pre-run state snapshot. Use `out/state.json` across runs and run one agent at a time per output root. Use standard-library Python at runtime and pin the test dependency to `pytest==9.2.0` as in JS1. |

## Wrong versions the tests must catch

| What could go wrong | What I expect the check to show |
|---|---|
| The loop turns a failed fetch into an empty list and exits `finished`. | The failed board has no counts and the completed schedule exits `incomplete`. |
| An outgoing request uses urllib's default User-Agent. | The test inspects the outgoing request and requires the exact User-Agent value from the network policy. |
| A prefix check lets a write through to `out-evil/` or through a symlink outside `out/`. | The write is refused and the outside file is untouched. |
| The loop retries a 404 or forgets to count a timeout retry. | The 404 gets one attempt. A transient failure gets at most one retry, and both attempts count. |
| A slow response read gets the whole run budget, or the retry skips the wait. | The read respects the time left in the attempt. The retry waits 1 second and rechecks the budget. This check covers response timing. |
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
| 2026-11-09 | Tushar Patel | Started from Claude chat's suggested answers to F1–F20. For v0.3, I added unique-ID counts in F3, a second budget check after the retry wait in F11, the standard-library DNS limit in F12, an agent-written starting state snapshot in F17, the measured 16-ID fixture difference in F18, an explicit root symlink check in F19, and one active run per output root in F20. I also updated the preflight record to point to the saved bodies and include Ashby's invalid-token result. |
| 2026-11-09 | Tushar Patel | v0.4. Both Ashby boards returned HTTP 403 in live run 1, with Cloudflare error 1010 in the saved response bodies. I reproduced the difference with [curl](evidence/review-packet-ua-repro.txt). The Python User-Agent got 403 and the student-project User-Agent got 200. I added the explicit header and regression test requirement to the gate and kept the 12-attempt cap. For live run 2, I predict three successful boards, one deliberate 404, and an `incomplete` exit. |
