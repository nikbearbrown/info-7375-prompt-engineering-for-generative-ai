# GATE.md — Job-Search Agent 2

**Decision owner:** Revan C.  
**Written:** November 10, 2026, before the Job-Search Agent 2 implementation  
**Starting point:** My Job-Search Agent 1 in this repository, which watches Klaviyo's Greenhouse board. Its `CONTRACT.md` still governs the fictional résumé and relevance rule. This gate governs the new multi-board loop, its tool permissions, and its exits.

This is a decision document, not a report of completed tests or runs. I will revise it in writing before changing a budget or relaxing a permission. I will keep the earlier version in Git so the decision remains visible.

## Boards and the bounded run

I chose three public boards for the normal watch and one deliberately invalid board for the failure demonstration. The invalid board is a request to an allowed public endpoint; it is not a license to fetch arbitrary Greenhouse slugs.

| Order | ATS | Board | Exact permitted GET URL | Purpose |
|---|---|---|---|---|
| 1 | Greenhouse | Klaviyo | `https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true` | Existing Job-Search Agent 1 board |
| 2 | Greenhouse | Duolingo | `https://boards-api.greenhouse.io/v1/boards/duolingo/jobs?content=true` | Second live board |
| 3 | Lever | Patch My PC | `https://api.lever.co/v0/postings/patchmypc?mode=json` | Second ATS |
| 4 | Greenhouse | `js2-deliberate-missing-board` | `https://boards-api.greenhouse.io/v1/boards/js2-deliberate-missing-board/jobs?content=true` | Intentional HTTP failure, enabled only for the labeled demonstration run |

The normal run selects orders 1–3. The deliberate-failure run selects orders 1–4. If a board disappears or changes its response, I will record that as an observation, not silently substitute another board. A board change requires a new written decision and an allow-list change that I review.

## Exits

One run has exactly one final status. A stopped loop is not automatically a successful loop. The trace must name the selected boards and give an observation or a reason for not observing each one.

| Status | Meaning | Required report |
|---|---|---|
| `finished` | Every selected board was requested once, returned a valid nonempty job list, and its observation and run output were saved. In an approved state-changing run, the state update was also saved. An observation-only run may finish without changing state. | Board names, response counts, new-posting counts, raw-response paths, elapsed time, request count, run mode, and whether state changed. Zero **new** postings is allowed after a valid nonempty response. |
| `incomplete` | At least one selected board failed or returned an invalid or empty response, while the loop recorded the failure and continued through the remaining boards within budget. | Successful observations plus the failed board's actual HTTP status or validation error. The failed board's job count and new-posting count are `unknown`, never zero. Overall success must not be claimed. |
| `budget-exhausted` | The next board request or required processing step would cross a run limit. | Which limit stopped the run, usage so far, completed and unattempted boards, and whether state was changed. Unattempted boards have `unknown` counts. |
| `error` | A local preflight, permission, output, or state-write failure prevents a trustworthy run record. | The actual error, the last completed action, any raw evidence already saved, and whether state was changed. No `finished` claim. |

If two conditions occur, I report the condition that first stopped progress, while retaining earlier board failures in the trace. A failed board does not stop the next board. A local error that makes the trace unreliable stops the run immediately. I will use distinct machine-readable statuses and nonzero process exit codes for every status except `finished`.

I will advance the seen-posting state only in a run with `--approve-state-write`, after all selected boards have valid observations and the run output has been saved. An observation-only run, or any `incomplete`, `budget-exhausted`, or `error` run, leaves the prior state unchanged. This may cause already observed postings to appear again on the next run, so the trace must say whether state advanced.

## Budgets

The production limits are **4 boards, 4 HTTP requests, and 45 seconds of elapsed wall-clock time per run**. Each request has an **8-second timeout**. The three-board normal run therefore uses at most three requests; the four-board demonstration uses at most four. Redirects are refused rather than followed, so they cannot consume uncounted requests.

I treat 45 seconds as a deadline for the whole run, including saving the final trace. The loop checks board and request limits before each request. It reserves 2 seconds to finish the trace, so it starts a request only when **at least 10 seconds remain**: up to 8 seconds for the request and 2 for finalization. A request proposed at second 40 is not sent; the run reports `budget-exhausted` and the unattempted boards. Each blocking operation uses the remaining deadline as its upper bound, and the loop stops further work when the deadline is reached. An unexpected overrun is reported as `budget-exhausted`, with its measured elapsed time, never as `finished`.

These numbers are my policy, not values for the agent to increase when it is close to finishing. I alone may change them, by editing this gate first and then reviewing the code and tests that implement the new numbers. Tests may use an injected smaller budget to exercise an exit, but that is a labeled test configuration, not a production budget change.

## Repeat rule

Within a run, the same action means the same HTTP method and canonical URL, including its exact path and query, even if a different board label points to it. I allow one `GET` per selected board URL. Before a request, the loop checks its action ledger. A repeated action is recorded as suppressed; it is not sent again and does not create a second observation or an invented result. If a duplicate URL was selected in configuration, the run ends with `error` at preflight because the selection itself is wrong. A run on a later date may request the board again; that is the point of the watch.

## Failed-board policy

I chose **zero automatic retries** for this version. An HTTP error, timeout, malformed JSON, wrong provider shape, missing required posting fields, duplicate posting ID, or empty job list makes that board fail. The loop saves response bytes if it received any, records the actual error, and continues to the next selected board if the run remains within budget. It never treats an empty list or failed fetch as “no new jobs.” At the end, any such failure makes the run `incomplete`.

I chose no retry because this assignment needs a legible one-request-per-board trace. A retry policy would require a separate written reason, request budget, and test showing why that failure is transient. A network failure with no response has no raw body to save; the trace says that explicitly.

For the deliberate-failure run, the fourth Greenhouse slug is expected to return an HTTP error. The trace must label it as intentionally selected **before** the request and then record the actual response. I will not write “404” as an observed result unless the saved trace shows 404. If that slug unexpectedly returns a valid board, I will report what happened and choose a new deliberate-failure case through a written decision.

## Permission policy

I will enforce these boundaries in code before calling a network or filesystem tool. A prompt telling the agent to behave is not enforcement.

**Network.** Only `GET` over HTTPS to the four exact URLs above is allowed. The normal mode permits only the first three; the fourth requires an explicit demonstration flag. The only hosts are `boards-api.greenhouse.io` and `api.lever.co`, but host membership alone is insufficient: scheme, method, port, credentials, path, and query must also match. No redirects are followed. No login, search engine, application endpoint, form submission, POST, PUT, PATCH, or DELETE is allowed. Each live request counts toward the request and time budgets.

**Files.** For Job-Search Agent 2, the program may read the fictional `resumes/aarav-patel.json`, its own configuration and prior `state/js2/` data, and explicitly selected seeded fixtures. It may create or update only files within `evidence/js2/`, `runs/js2/`, and `state/js2/` beneath this repository. It saves exact live response bytes under `evidence/js2/` before parsing and records their paths in `runs/js2/`. It may not read, log, upload, or commit my real résumé, contacts, tracker, credentials, or private conversations. A seeded response is labeled `seeded` in every output and is never called live.

The path check uses canonical resolved paths and path-component containment under the designated directory. It rejects `..` escapes, sibling names such as `runs/js2-evil`, and any symlink component that resolves outside the allowed directory. A caller-provided output path does not expand the allowed directories. A read permission never implies write permission.

**Approval.** The default is an observation-only run: it may fetch the selected boards and save raw evidence and a trace, but it does not update `state/js2/`. It reports `state_updated: false`, and its new-posting comparison is relative to the existing saved state; the same postings may appear again next time. Updating `state/js2/` requires my explicit `--approve-state-write` command-line flag for that run. The flag grants only that state write inside `state/js2/`; it cannot override the host, method, or path restrictions. A direct state-write attempt without the flag is denied, but the observation-only run itself is allowed. The program may write raw evidence and run traces to their approved folders without a second approval, because those are the records needed to inspect the run.

The agent never applies for a job, emails or messages anyone, logs in, or submits a form. It does not infer sponsorship or E-Verify facts beyond the limits already stated in `CONTRACT.md`.

## Predicted boundary cases

These are predictions made before running the Job-Search Agent 2 boundary tests. The test report must later identify the actual result for each case and any disagreement.

| ID | Attempt | Predicted result |
|---|---|---|
| B01 | `GET` the exact Klaviyo URL in normal mode | Allow and count one request |
| B02 | `GET` the exact Patch My PC Lever URL in normal mode | Allow and count one request |
| B03 | `GET https://example.com/jobs` | Deny: host off the allow-list |
| B03a | `GET https://boards-api.greenhouse.io.evil.com/v1/boards/klaviyo/jobs?content=true` | Deny: look-alike host is not the exact allowed hostname |
| B04 | `GET` the Greenhouse host with an unlisted slug | Deny: endpoint off the exact allow-list |
| B05 | `POST` to an allowed board URL | Deny: method is not GET |
| B06 | `GET` an allowed path over HTTP or with a nonstandard port | Deny: scheme or port differs |
| B07 | An allowed URL redirects to another host or path | Deny the redirect; make no second request |
| B08 | Write `runs/js2/../outside.json` | Deny: resolved path escapes the output folder |
| B09 | Write to sibling `runs/js2-evil/result.json` | Deny: sibling prefix is not containment |
| B10 | Write through a symlink inside `runs/js2/` pointing outside it | Deny: resolved path escapes the folder |
| B11 | Read an approved seeded fixture | Allow read only; do not grant write |
| B12 | Write to that seeded fixture | Deny: input read permission is not output write permission |
| B13 | Run without `--approve-state-write` | Allow observation and trace writes; deny any state write and report `state_updated: false` |
| B14 | Write `state/js2/seen_ids.json` with the flag | Allow if the resolved path stays in `state/js2/` |
| B15 | Select the deliberate-failure URL without demonstration mode | Deny at preflight |
| B16 | Try to start an 8-second request at second 40 of a run | Do not send it; report `budget-exhausted` because fewer than 10 seconds remain |

## Plausible wrong versions my tests must catch

1. **Clean but wrong empty result.** A parser accepts `[]` or `{"jobs": []}` from a board and reports `finished` with “no new jobs.” The production policy says `incomplete` with unknown counts. For the required finished-wrong-answer demonstration, I will run a clearly labeled wrong or seeded variant and use an independent check of the saved raw response and selected-board list to expose its false claim. The agent's own summary is not that check.
2. **Failure disguised as success.** A 404, timeout, or malformed response becomes a zero count, or the fourth board disappears from the final trace. A test must require the actual failure and overall `incomplete` status.
3. **Budget crossed by one.** The loop starts request five, a fifth board, or an 8-second request with fewer than 10 seconds left because it checks only after acting. Tests must check refusal before the action, including the second-40 case.
4. **Duplicate action.** A retry or duplicate URL makes a second HTTP request without a new written policy. A test must count actual fetch calls.
5. **Permission by string prefix.** `runs/js2-evil` or a symlink is accepted because its text starts with `runs/js2`. Tests must use resolved path containment.
6. **Read becomes write.** A fixture that may be read is overwritten, or a state file is written without the approval flag. Tests must inspect the file; an observation-only run must still be allowed to fetch and save its trace.
7. **State advances after failure.** A failed or observation-only run marks unseen jobs as seen. Tests must compare state bytes before and after the run.
8. **Provider shapes conflated.** Lever's top-level list is treated as Greenhouse's `jobs` object, or malformed data is silently accepted. Tests must use provider-specific saved fixtures and assert observations by board and posting ID.

## Sources for the endpoint choice

- [Greenhouse Job Board API overview](https://support.greenhouse.io/hc/en-us/articles/10568627186203-Greenhouse-API-overview) and [Greenhouse's `content=true` example](https://support.greenhouse.io/hc/en-us/articles/360000468952-FlexJobs-integration).
- [Lever Postings API documentation](https://github.com/lever/postings-api), including the public list endpoint and JSON mode.

