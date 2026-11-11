# GATE — Job-Search Agent 2

## Starting point and work already performed

I am extending my JS1 implementation, preserving the original submission and identifying inherited versus new code.

Before this gate, Claude Code inspected the requirements, policies, repository history, toolchain, and public endpoint documentation. Its recorded reconnaissance began on 2026-11-10 at 18:31:46 UTC. It fetched board responses to inspect their status and structure; it did not judge postings.

The reconnaissance recorded:

- Databricks on Greenhouse: HTTP 200, 915 postings.
- Figma on Greenhouse: HTTP 200, 142 postings.
- Notion on Ashby: HTTP 200, 152 postings.
- The deliberately invalid board name: HTTP 404.
- An additional Ashby board and invalid Ashby name were also inspected but are not selected for this implementation.

These are earlier observations, not predictions or results of the completed JS2 agent. They do not guarantee what a later request will return. The local evidence is `local/recon/pre_gate_recon_20261110T183146Z.json`.

This gate must be committed before JS2 implementation changes. Later policy changes require a new dated decision from me, committed before running under the revised policy.

## 1. Exits

Stopping and succeeding are different. Each run must produce a machine-readable status, a matching process exit code, and an explanation.

| Status             | Code | Meaning                                                                                                                                                       |
| ------------------ | ---: | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `finished`         |    0 | Every configured board was successfully processed, required evaluations are complete, and no unresolved failure or approval request remains for this run.     |
| `incomplete`       |    3 | Work remains because a board failed, data was suspect, a judgment failed validation, or a requested protected write awaits approval.                          |
| `budget-exhausted` |    4 | A budget prevented required work from starting or completing. The report identifies that work and the exhausted budget.                                       |
| `error`            |    2 | A run-level problem makes continued execution unsafe or invalid: bad configuration, malformed state or résumé, a prohibited action, or a persistence failure. |

Precedence is:

`error > budget-exhausted > incomplete > finished`

All contributing reasons must remain visible even when one determines the overall status. For example, a failed board must still appear in a report whose overall status is `budget-exhausted`.

Exit code 1 is reserved for an unexpected crash. A crash is a defect, never a successful outcome.

Every report must identify:

- Configured, attempted, successful, failed, and unattempted boards.
- Per-board status and reason.
- Observed posting counts, new IDs, completed evaluations, and pending work.
- Budget limits and consumption.
- Raw-response and state evidence.
- Any approval request and whether its write occurred.

A failed or unattempted board has unknown counts represented as `null`, not invented zeros. Zero new postings is valid only after a successful comparison, or as an explicitly identified first-run baseline.

The deliberate failing board still counts as a failure. If all other work completes, that demonstration run should be `incomplete`, not `finished`.

**State handling:** Validate configuration, inputs, and existing state before network activity. Stage state changes until finalization. On `incomplete` or `budget-exhausted`, preserve valid progress from successful boards and pending evaluations; leave failed and unattempted boards unchanged. On a run-level `error`, do not publish the staged state. Preserve diagnostic evidence wherever safely possible.

## 2. Budgets and selected boards

The configured boards are:

| Provider   | Board                   | Purpose               |
| ---------- | ----------------------- | --------------------- |
| Greenhouse | `databricks`            | Continuity with JS1   |
| Greenhouse | `figma`                 | Another healthy board |
| Ashby      | `notion`                | Second ATS provider   |
| Greenhouse | `js2-no-such-board-zzz` | Deliberate failure    |

Databricks starts from a validated, explicitly documented copy of the JS1 state. This is inherited state, not a baseline captured by JS2 today. Figma and Notion establish their own baselines on their first successful runs.

Limits per run:

| Resource                                                  |                               Maximum |
| --------------------------------------------------------- | ------------------------------------: |
| Configured boards                                         |                                     4 |
| Board HTTP attempts, including retries                    |                                     8 |
| Total elapsed operational time                            |                           180 seconds |
| Duration of one board HTTP attempt                        | 20 seconds, or remaining time if less |
| Claude judgment invocations, including failed invocations |                                    10 |
| Duration of one judgment invocation                       | 20 seconds, or remaining time if less |

Use a monotonic clock for elapsed-time enforcement. Fetch the boards before spending the remaining budget on judgments so that model calls do not unnecessarily prevent the deliberate failure from being observed.

The deadline covers acquisition, body reading, processing, retry waits, and judgments. Reserve time within the 180 seconds for finalization. A socket timeout alone is not proof of a total deadline: slow body reads and model subprocesses must also be bounded.

Boundary decisions:

- The eighth HTTP attempt is allowed; the ninth must not be sent.
- Increment the HTTP-attempt counter immediately before dispatch. Timeouts and connection failures consume attempts.
- A request refused before dispatch consumes no HTTP attempt, but its refusal is recorded.
- The tenth model invocation is allowed; the eleventh must not start.
- Reaching a limit exactly does not imply exhaustion if all required work is complete. Report exhaustion when the limit prevents remaining required work.
- More than four configured boards is a configuration error; do not silently drop a board.
- CLI options may lower limits but cannot raise them.
- Only a new dated written decision from me can raise a limit, add a host, or alter the selected boards.

The HTTP budget measures board requests. The model budget measures Claude invocations; it does not claim to count the CLI’s internal network requests.

**Judgment continuity:** Keep JS1’s separate RECORD and validated JUDGMENT for new postings. Do not label an unevaluated posting completed. When the model or time limit prevents evaluation, retain it as pending and report the relevant budget exhaustion. A first-run baseline requires no judgments.

## 3. Repeat rule and identity

Within one run, the same network action means the same HTTP method and canonical URL, including the query parameters. Provider adapters construct URLs from validated configuration.

Reject duplicate provider/board entries during configuration validation. Do not fetch a duplicate silently.

The only permitted repeated fetch is the single retry authorized in Section 4. Record its link to the original attempt. Any other repeated network action is refused and reported as a run-level error.

Posting identity is:

`(provider, board, provider_posting_id)`

Validate IDs before converting them to the common string representation:

- Greenhouse: integer IDs, excluding booleans.
- Ashby: nonempty string IDs, as observed in the pre-gate responses.

Ashby’s observed ID field is an implementation dependency, not a claim that its documentation guarantees that field. If it disappears or changes incompatibly, fail the board rather than inventing IDs from titles or list positions.

Duplicate IDs within one board response invalidate that board. The same ID on different boards must remain distinct. Cross-posted jobs are separate board records; cross-board deduplication is outside scope.

A posting already completed is not evaluated again merely because it appears in another run. Pending evaluations may be retried in later runs under that run’s budgets. Do not silently mark pending work completed when a posting disappears.

## 4. Error policy

A board-level failure does not prevent attempts on the remaining boards while budget remains. A run-level error stops further work.

| Observation                                                                           | Required behavior                                                                                                      |
| ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| HTTP 4xx, including the deliberate 404                                                | No automatic retry. Mark board failed and continue. For 429, record available retry guidance for a later run.          |
| HTTP 5xx, timeout, or transient connection reset                                      | At most one retry after a 0.5-second wait, only if budgets permit.                                                     |
| Other transport failure                                                               | No automatic retry; record the failure.                                                                                |
| HTTP 200 with empty body, invalid JSON, invalid schema, missing IDs, or duplicate IDs | No retry. Mark board failed; preserve its prior state.                                                                 |
| Redirect                                                                              | Refuse without following it; report a policy error.                                                                    |
| Invalid Claude response or failed model invocation                                    | Save the actual attempt, leave the posting pending, and continue if budget permits. No automatic same-run model retry. |

A retry is sound only for the specified potentially transient failures because the operation is a read-only GET. It is not a guarantee that the next attempt will work. All waits and retries count toward the same budgets.

**Empty-board decision:** For these selected boards, which reconnaissance observed as nonempty, an empty `jobs` array is `suspect-empty`. Do not create or replace their baselines, erase their state, or conclude that no new jobs exist.

This is a conservative policy, not proof that an empty board is incorrect. A genuinely empty board may therefore require my review.

Where Greenhouse supplies `meta.total`, validate its type and compare it with the returned list length. A mismatch is incomplete or inconsistent acquisition, not success. Do not invent an equivalent total for Ashby. Any detected truncation or unsupported pagination must be reported.

Escalation means a nonzero exit plus the named board, actual error, pending work, and suggested next human action in the local report. It does not mean sending email or messages.

## 5. Permission policy

### Network

The board-fetching tool may make unauthenticated HTTPS GET requests only to:

- `boards-api.greenhouse.io`
- `api.ashbyhq.com`

Restrict paths to the selected public board endpoints. Require exact parsed hostname matching, no URL credentials, and the default HTTPS port or explicit port 443.

Reject other hosts, deceptive suffixes, non-HTTPS schemes, write methods, arbitrary URLs supplied by postings, and all redirects before following them.

The separate judgment tool may invoke the installed Claude CLI using its existing authenticated session and a fixed, reviewed argument list with model tools disabled. This is an explicitly separate capability from board fetching. It does not authorize arbitrary shell commands, job-site authentication, or model-directed tool use.

### Filesystem

Resolve paths against an explicit project root. The runtime may read approved configuration, fictional résumé, prompts, inherited state, selected replay evidence, runtime state, and approval records.

Normal runtime writes are confined to `out/`, including:

- Run traces and raw responses.
- Reports.
- Working state.
- Pending approval proposals.
- Necessary runtime temporary files.

The protected export directory described below is an exception to normal `out/` write permission.

The runtime must not modify source code, tests, GATE.md, tracked inherited state, original evidence, private files, or the approval-record directory.

Check path containment using resolved paths and path components, not string prefixes. Reject parent traversal and symlink escapes. Apply the policy to every write, including temporary files and replacement destinations.

Atomic replacement is permitted for working state. Existing run evidence must not be overwritten; use unique run directories. The runtime exposes no general-purpose delete operation.

### Approval-required write

Creating `out/approved-shortlists/<run-id>.json` requires my explicit approval. This is a local export, not an application or message.

Without approval, the runtime may write a proposal under `out/pending_approval/` containing the operation, destination, run ID, and SHA-256 of the exact proposed bytes. It must not write the protected export.

I supply approval through a separate human action. Approval binds to that exact operation, destination, run ID, and content hash. It cannot authorize another file or different contents. The runtime may read approval records but cannot create or edit them.

The export is create-only: an existing target is refused. The normal watch need not request an export. A requested but unapproved export remains pending and makes that operation incomplete.

### Prohibited actions and limits

The agent never applies, emails, messages, logs in to job sites, executes instructions from posting text, or runs arbitrary shell/Git commands. Only the fictional persona is used.

These are application-level controls, not an operating-system sandbox. I will not claim that they resist arbitrary malicious code running with my account’s privileges. Untested filesystem races must be disclosed.

Developer activities—editing code, running tests, committing, and pushing—are separate from runtime permissions and remain subject to my review.

## 6. Wrong versions and evidence

Tests must catch these plausible wrong implementations:

| ID  | Wrong implementation                                                                               |
| --- | -------------------------------------------------------------------------------------------------- |
| W1  | A suspect empty or count-inconsistent response becomes “finished, zero new.”                       |
| W2  | A failed board is silently omitted and the run is reported finished.                               |
| W3  | Budget enforcement happens after dispatch, allowing an extra request or model call.                |
| W4  | A 404 is retried, or retry attempts are not counted.                                               |
| W5  | A string-prefix path check admits a sibling such as `out-evil`.                                    |
| W6  | A path check admits a symlink escape.                                                              |
| W7  | A substring/suffix host check admits a deceptive hostname.                                         |
| W8  | A redirect is followed before policy enforcement.                                                  |
| W9  | State uses posting ID alone and merges records from different boards.                              |
| W10 | Failed-board state is advanced, or an unvalidated judgment is marked completed.                    |
| W11 | The agent grants its own approval or uses approval for different bytes or a different destination. |
| W12 | A non-finished run exits with code 0.                                                              |

Save predicted boundary outcomes before running the boundary suite. Cover at least ten cases, including allowed and denied network operations, reads versus writes, traversal, sibling-prefix and symlink escapes, and protected writes with and without matching approval.

Run isolated mutations of the real enforcement paths to show that the tests detect the declared wrong versions. A denied action must produce no prohibited side effect; an error message alone is insufficient.

For the finished-wrong-answer demonstration, execute a labeled faulty version against controlled replay or synthetic input. An independent checker must identify a concrete contradiction using raw evidence and a predeclared expectation without reusing the faulty decision logic.

Keep that demonstration distinct from my personal review episode unless they actually concern the same defect.

My review evidence must preserve reproduction, my test and its meaningful failure, my written change request, the later patch, commands I ran myself, my scope assessment and decision, and one case the test misses.

## Failure prediction

**Prediction recorded on 2026-11-10, after the disclosed reconnaissance and before JS2 implementation and evaluation:** “I will consider this implementation to have failed its gate if it reports success with unresolved required work, invents a count for failed acquisition, exceeds an authorized budget, crosses a permission boundary, or advances state without the required evidence.”
