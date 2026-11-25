## Exits

I’m building on JS1’s Anthropic watch for ML, AI systems, and data infrastructure roles. A normal run checks Anthropic (`anthropic`) and Databricks (`databricks`) on Greenhouse, and Linear (`linear`) on Ashby. A separate failure run adds the bad Greenhouse slug `jobwatch-no-such-board-js2`. I expect a 404 from that board.

| The run ends when | Status | What it reports |
| --- | --- | --- |
| A normal run gets usable data from all three boards, saves the results, and completes the approved state update. | `finished` | Per-board counts and whether the board was baselined or checked for new postings. |
| At least one normal board is usable but another board fails, including the intentional 404, or approval for the state update is missing. | `incomplete` | The usable results as provisional, plus the failed boards and reasons or the missing approval. |
| A budget prevents the run from finishing required work. | `budget-exhausted` | Which limit was reached, how much was used, and what was left unfinished. |
| No normal board is usable, the failure control behaves unexpectedly, or the run hits a policy denial, corrupt state, or a required write failure. | `error` | The specific fault and where the run stopped. |

The trace records each request with its board, timestamp, elapsed time, and HTTP status or failure reason. It points to the raw response when one was received and lists any boards that were skipped. Failed boards have an unknown count. Only a `finished` run advances the saved watch state.

## Budgets

At most four distinct boards, four HTTP requests, and 30 seconds of elapsed time per run. The deliberate failure counts toward both the board and request limits. Each request gets at most five seconds to receive the full response, or less if the run has less time left. The clock starts before the first operation and covers fetching, processing, and saving. I can change these limits by writing a dated change to this gate before the next run.

## Repeat rule

The same fetch means the same ATS and board slug in one run. Trim whitespace and lowercase those two values before looking up the approved endpoint. If a board appears twice, log the duplicate and fetch it once. A failed request still uses that board’s one attempt.

Keep posting history by ATS, board slug, and posting key. Use Greenhouse’s `id` and Ashby’s `jobUrl` as keys. Use the Ashby URL as a string without opening it. Collapse identical duplicates and reject conflicting records with the same key. The first usable snapshot of each board is a baseline with zero new postings. Later snapshots count only keys that have never been saved for that board, even if a title changed or a posting disappeared and came back. Apply the JS1 screening rule to new postings using the fictional persona. [Greenhouse Job Board API](https://docs.greenhouse.io/job-board.html#list-jobs) · [Ashby Job Postings API](https://developers.ashbyhq.com/docs/public-job-posting-api)

## Error policy

Save the raw response before interpreting it. A failed request, non-200 response, malformed payload, or empty jobs list means the board could not be verified. Record the reason, continue with the other boards within budget, and show the failed board in the summary so I can decide whether to check it manually. Make zero automatic retries. If the bad slug does anything other than return the expected 404, record the outcome and report that the failure control broke. A policy denial, corrupt state, or required write failure stops the run. Save the evidence and results before atomically updating state.

## Permission policy

Allow HTTPS GET only on the configured list endpoints at `boards-api.greenhouse.io` and `api.ashbyhq.com`. For Greenhouse, use `/v1/boards/{slug}/jobs?content=true`. For Ashby, use `/posting-api/job-board/{slug}`. Check the exact host, path, query, and method before sending. Refuse redirects and links found in postings. Use the local screening rule for this version and make no model calls.

Read only the fictional persona, the watch state, and saved run evidence when needed. Write new evidence and results only under the current run’s folder in `runs/`. Creating or replacing `state/state.json` requires my explicit approval for that file and that run, supplied locally before the run starts. That approval also covers the temporary file in `state/` needed to make the update atomic. Check containment against the fixed project paths, refuse parent traversal and symlink paths, and check approval separately from read access. Never apply, submit forms, email, message, log in, or access my real résumé or contacts.

## Wrong versions

- A 404 or empty jobs list becomes “no new postings” and the loop reports `finished`. Use a labeled empty-response fixture and check the saved body and before-and-after state separately from the loop’s report.
- A partial run advances state. Use one failed board and compare the entire state file before and after the run.
- A duplicate board sends a second request, the request cap is exceeded, or work continues after the deadline. Check the requests and timestamps recorded by the test harness.
- A key from one board suppresses a posting from another, or a returning posting is marked new. Use fixtures with overlapping keys and a posting that disappears and returns.
- A write is allowed because a read of the same file was allowed. Test contained reads, new run evidence, and state writes with no approval, the wrong approval, and approval for the correct run and file.
- An off-list host, a POST to an allowed host, a redirect, or a path through `..`, `runs-evil/`, or a symlink gets through. Check that the forbidden request or file operation never happens.
