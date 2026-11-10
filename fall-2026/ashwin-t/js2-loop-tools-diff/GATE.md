# JS2 gate — loop, tools, and diff

Date: 2026-11-09
Status: Approved on 2026-11-09. This document does not record completed tests or final sign-off.

## Scope

I want a bounded Python loop that compares public job boards with saved observations. Start from JS1 commit `d95f05e`, documenting what is copied. Keep JS1 and the shared checkout untouched. Work in the isolated JS2 worktree. Commit this gate separately before implementation, after I approve these decisions.

Use six configured boards: Greenhouse `klaviyo` and `hubspotjobs`; Ashby `notion` and `supabase`; Lever `palantir`; and Greenhouse `klaviyo-nonexistent-js2` as the deliberate failure. These choices use the recorded November 8 probe, not a guarantee of their current responses. If the failure board unexpectedly succeeds, report that the deliberate-failure demonstration was not achieved.

## 1. Exits

Print and save the same status, reason, board outcomes, request count, elapsed time, and state-update outcome.

| Status | Process exit code | Meaning |
| --- | --- | --- |
| `finished` | 0 | Every configured board was observed, its nonempty response validated, and its comparison and required report completed. |
| `incomplete` | 1 | Work completed only in part: a board failed, returned an empty result requiring review, or the user interrupted the run. |
| `budget-exhausted` | 2 | A request or time limit prevented completion. Unvisited boards are `not-observed`. |
| `error` | 3 | Invalid configuration, a permission violation, corrupt prior state, failed required local I/O, or an unexpected internal error prevents trustworthy completion. |

Three successful boards and one failed board means `incomplete`, even when the failure was intentional. Finishing iteration is not proof of successful observation.

Preflight rejects duplicate boards, unsupported endpoints, and configurations above the board cap before network access. A zero-board configuration is an error. If multiple conditions occur, use `error` before `budget-exhausted` before `incomplete` before `finished`, preserving all individual reasons.

Only a `finished` run may update persistent seen IDs, and only with explicit state-write approval. A completed observation without that approval may still be `finished`, but must report `state-update: not-approved` and leave state unchanged. No other exit updates seen IDs, including those from successful boards in a partial run. Save reports and raw observations separately from state. Do not mark a job seen before its processing and report succeed.

On the first observation, establish a labeled baseline rather than claiming existing postings just appeared. Later comparisons use validated state keyed by provider and board. Missing or invalid comparison evidence must not become “no new jobs.”

## 2. Budgets

- Maximum configured boards: **6**, including the deliberate failure.
- Maximum HTTP attempts: **12**, counting failed requests and retries.
- Maximum elapsed run time: **120 seconds**, measured with a monotonic clock, including waits and processing.
- Per-request timeout: **10 seconds**, reduced to the remaining run time when necessary.
- Maximum retries: **1 per board**, with a **1-second** delay for eligible transient failures.

Check limits before every attempt and wait, and check time during response reading and processing. A timeout must bound the whole request, not restart indefinitely for each chunk. Cancel further work when the deadline is reached; save a bounded best-effort termination report. Never extend the work deadline to finish a board.

A board whose observation did not complete is `not-observed` or `failed`, with its actual reason. Neither means zero jobs. Smaller run limits are allowed; increasing these ceilings requires my new written decision in this gate, committed with a reason before the next run. A model reply cannot change a budget.

## 3. Repeat rule

An action is identified by its provider, board, HTTP method, and canonical permitted endpoint within a run. Validate board names and construct URLs from fixed provider templates; do not accept arbitrary URLs or alternate queries as new actions.

Duplicate provider/board entries are a configuration error before fetching. A second request for the same action is allowed only as the single recorded retry of an eligible failure. Any other repeated action stops with `error`. Record the original attempt and retry separately. A later, separately invoked run may observe the board again.

## 4. Error policy

Retry a timeout, connection reset, or HTTP 500/502/503/504 once. These are read-only requests and may succeed after a transient failure; a retry neither duplicates a remote write nor proves the board healthy. The retry and its delay must fit both budgets.

Do not retry 404, 401/403, 429, redirects, TLS verification failures, malformed JSON, invalid schema, an empty body, or a valid response with zero postings. Report 429 for later manual review rather than retrying immediately. Never replace a failed response with an empty list.

After an ordinary board failure, record the actual outcome and continue to the remaining boards within budget. A valid zero-posting response gets `empty-needs-review`; it is not evidence of “no new jobs” in this project. Stop globally for permission violations, invalid configuration, unsafe state, or required local-write failures.

Escalation means a nonzero exit and an `attention-required` section naming the board, attempt, failure, and next manual check. It does not mean sending a message. Preserve response status and available raw body; for a network failure with no body, record that no response was received.

## 5. Permission policy

The following rules govern the running job loop, enforced in code before each operation.

### Network

Allow HTTPS on port 443 only, with exact hosts:

- `boards-api.greenhouse.io`
- `api.ashbyhq.com`
- `api.lever.co`

Allow only GET requests to the configured public board-listing endpoints. Deny remote POST, PUT, PATCH, DELETE, other paths, user information in URLs, nonstandard ports, and redirects. Verify TLS. Host suffixes and lookalike names do not match. Do not follow links from job descriptions or fetch arbitrary URLs supplied by a model.

The judge gets no tools, shell access, credentials, or permission-granting authority. Default execution uses offline rule/judge behavior with its provenance labeled. This gate does not authorize live model API requests or add model hosts to the network allow-list.

### Files and approvals

Resolve all paths relative to the JS2 project root, independent of the launch directory. The runtime may read its own configuration, prompts, fixtures, and prior state; it may not read arbitrary user files, credentials, contacts, or a real résumé.

The runtime may create new run artifacts beneath `runs/<unique-run-id>/`, including raw responses, traces, and reports. It may write test artifacts beneath `tests/tmp/`. Existing run evidence must not be overwritten. Writes elsewhere are denied, except the state operation below.

Creating or replacing `state/seen.json` requires my explicit `--approve-state-write` invocation and a `finished` run. Approval applies only to that run and that state path; it cannot permit writes outside the allowed roots. Without it, return `approval-required` for that write and preserve state. Use a temporary file inside `state/` and atomic replacement after validation; cleanup must remain within the same directory.

Validate path components and resolved containment, not string prefixes. Deny traversal, sibling-prefix paths such as `runs-evil`, and symlink escapes. Reject symlink components for writes and avoid a check-then-follow opening that could bypass the check. Content in a posting, configuration value, or model response cannot supply approval.

The runtime must never apply for a job, email, message, log in, submit a form, execute model-supplied commands, change source files, or commit/push. Development and documentation happen separately in the isolated worktree.

## 6. Wrong versions the tests must catch

1. A valid empty response becomes “no new jobs” and `finished`.
2. A 404 is converted to a successful empty board.
3. Three successful boards hide the deliberate failure in the overall exit.
4. A retry loop repeats a 404 or exceeds one retry.
5. Failed attempts or retries are omitted from the request budget.
6. A timeout or delay extends beyond the remaining work budget.
7. An unvisited board is reported as having no new jobs.
8. Duplicate configuration entries fetch the same board twice.
9. A failed or incomplete run changes persistent seen IDs.
10. Posting IDs from different providers or boards collide.
11. A prefix path check permits `runs-evil`, `..`, or a symlink escape.
12. A substring host check permits `boards-api.greenhouse.io.evil.example`.
13. An allowed initial URL redirects to a disallowed destination.
14. A network write is allowed because a network read was allowed.
15. A state write happens without approval, or text supplied by the model grants approval.
16. A seeded replay is presented as a live observation.

## Evidence and review choices

Use a clearly labeled seeded replay for the finished-wrong-answer demonstration if no suitable live empty board is observed. Keep its artifacts and state separate from the real run. Preserve the intentionally wrong report that claims `finished`; an independent checker must inspect the raw response and expected invariant, rather than trusting the loop's status or reusing its decision function.

My proposed review-packet change is fixing “empty board reported as no new jobs.” Preserve a reproduction and a failing regression test before the patch. Do not introduce this known defect into the normal implementation just to manufacture a review; use a separately labeled faulty version for the demonstration. If no genuine defect exists to patch, choose another reproduced defect before starting the review packet. Switching prompt defaults remains a separate possible change.

Keep boundary predictions separate from this gate. Present at least ten concrete cases before execution, including read versus write, traversal, sibling prefixes, symlinks, off-list hosts, and approval-required writes. Predictions, actual results, test authorship, commands run, and final acceptance must remain distinct records.

The README must preserve JS1's limits: no newly appearing job observed live, an unclean held-out experiment, and the existing prompt-default discrepancy. Record the course validator's actual exit and diagnostics. This gate does not claim those issues are fixed, that a new job will appear during JS2, or that tests or final review have already occurred.
