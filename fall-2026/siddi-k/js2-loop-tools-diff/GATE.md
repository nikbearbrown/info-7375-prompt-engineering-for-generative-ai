# GATE.md

Written by Siddi Kommuri on 2026-11-10 (about 22:04 ET), before any JS2 code existed. Siddi typed it in chat and Claude saved it verbatim; only Markdown formatting was added. The template headings were Claude's.

## BOARDS (pick at least 3, at least 2 systems, plus 1 that fails on purpose)

* Greenhouse: Stripe
* Ashby: Notion
* SmartRecruiters: Canva
* Deliberate failure: Greenhouse slug `stripee` (intentional 404)

## 1. EXITS — every way a run can end, and what the run reports for each

* finished: when? Every configured board has been attempted and its response successfully fetched and parsed, including a valid empty result.
  reports: `finished`, run ID, timestamps, per-board status, posting counts, total postings, and output paths.
* incomplete: when? At least one board could not be processed successfully, but the run can safely finish reporting the other boards.
  reports: `incomplete`, run ID, successful and failed boards, error details, partial counts, and output paths. Never report failed boards as zero postings.
* budget-exhausted: when? Any hard run budget is reached before all required work is complete.
  reports: `budget-exhausted`, which budget was reached, completed work, remaining work, partial counts, and output paths.
* error: when? A fatal internal error, invalid configuration, or unsafe condition prevents the run from continuing or reporting reliably.
  reports: `error`, run ID if available, error details, last completed action, and any safely persisted output paths.

## 2. BUDGETS — the most a single run may use

* boards per run: 4
* requests per run: 12
* seconds per run: 120
* who may change a budget, and how: Only I may change a budget, through an explicit written decision recorded in GATE.md and committed before the next run. The agent cannot change its own limits.

## 3. REPEAT RULE

* "the same action" means: The same HTTP method, normalized host, path, query parameters, and pagination cursor.
* when the loop sees the same action again, it: Skips the repeated request, records the repeat-guard event, and ends the run as `incomplete` if that action was required to finish a board. It must not silently treat the skipped request as success.

## 4. ERROR POLICY — what the loop does when a board

* returns 404 / a bad name: Mark that board as `failed` with `not_found`; do not retry and do not report zero postings. Continue with other boards.
* times out: Retry at most twice after the initial attempt, with bounded backoff. A GET request is safe to retry because it does not create or modify postings. If all attempts time out, mark the board `failed` with `timeout`; continue with other boards.
* returns 200 with 0 postings: Treat it as a valid empty result only after confirming the response is structurally valid and the board identity matches the configured board. Record `success` and zero postings.
* when do you (the human) get told: At the end of every run, report its named exit status and per-board outcomes. Report failures immediately in the run output; never wait until a later run or silently convert an error into zero postings.

## 5. PERMISSION POLICY

* hosts it may call: Only the documented, explicitly allowlisted job-board endpoints for Greenhouse, Ashby, and SmartRecruiters. No redirects to unapproved hosts.
* folders it may write: Only new run-specific files under `evidence/runs/`.
* writes that need my approval first: Changing configuration or budgets, changing the host allowlist, overwriting or deleting files, modifying source code outside the approved implementation task, and committing or pushing changes.
* never allowed: Writing outside the approved folder; reading or writing secrets, credentials, or unrelated personal files; making authenticated requests; submitting forms; modifying or deleting remote data; installing software; or executing commands outside the approved task.

## 6. WRONG VERSIONS — 3 to 6 believable but wrong implementations your tests must catch

* Treating every non-success response, timeout, or malformed response as zero new postings.
* Retrying 404s or retrying indefinitely after timeouts, without respecting the request and time budgets.
* Treating a repeated request as new work, causing duplicate requests or an infinite pagination loop.
* Treating any HTTP 200 response as a valid empty board, without validating the response structure and board identity.
* Reporting `finished` when one or more boards failed or when the run stopped because a budget was exhausted.

## Starting point

JS1 reuse: Yes. Build on my JS1 code, taking only the Ashby and SmartRecruiters field names from the instructor's Lectern collector. Do not copy its implementation or assume its behavior is correct.
