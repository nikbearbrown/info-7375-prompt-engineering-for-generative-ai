# GATE.md: Job-Search Agent 2 — The Loop, the Tools, and the Diff

Written by Sreevarshan Sathiyamurthy, 2026-11-06, before any code.

## 1. Exits

The agent has four possible exit statuses: finished, incomplete, budget-exhausted, and error.

Finished means all the planned boards were checked successfully. Incomplete means at least one board failed, returned an invalid response, or had missing information, but the agent could continue with other boards. Budget-exhausted means the agent reached its request, board, or time limit. Error means something unexpected prevented the run from continuing safely.

Every run should report its final status, how many boards were checked, how many succeeded or failed, and the reason it stopped. An empty or invalid board should not automatically be treated as a successful result with zero jobs.

## 2. Budgets

Maximum four boards per run, including the deliberately failing board. Maximum eight HTTP requests in total. Maximum 90 seconds of execution time.

The agent should not increase these limits automatically. Only I should approve changes to the budget, and any change should be written in GATE.md and recorded in Git before it takes effect.

## 3. Repeat Rule

The agent identifies the same action using the request method, ATS provider, board name, URL, and query parameters.

If the same request has already succeeded during the current run, the agent should reuse that result instead of fetching it again. If a board fails because of a timeout or temporary server error, the agent can retry it once. That retry counts as a new HTTP request toward the budget, but not as an unauthorized duplicate. No retries for permanent errors or invalid responses. Every attempt should be logged with its reason.

## 4. Error Policy

If a board times out or returns a temporary server error, the agent retries once, provided it still has enough time and requests remaining in the budget.

For invalid board names, permanent errors, empty responses, or invalid JSON, the agent records the failure and continues with the remaining boards without inventing job results.

If a board fails twice, the agent stops trying that board. The overall run is marked incomplete unless the error prevents the entire program from continuing safely.

## 5. Boards

Three real boards across two ATS systems, plus one deliberately invalid board:

- Databricks — Greenhouse (boards-api.greenhouse.io)
- Stripe — Greenhouse (boards-api.greenhouse.io)
- Spotify — Lever (api.lever.co)
- invalid-board-xyz — Greenhouse (deliberately invalid, to test error policy)

The agent fetches public job listings only, using official read-only endpoints. It never submits applications.

## 6. Permission Policy

Allowed hosts: boards-api.greenhouse.io and api.lever.co only.

Allowed writes: creating output files and updating normal state files inside the approved output directory. Overwriting or deleting previously saved raw evidence or trace files requires my explicit approval. Any write outside the approved directory is always blocked, even with approval.

The agent may never submit applications, email or message anyone, log in to accounts, access private information, or modify the JS1 project.

## 7. Wrong Versions

Bug 1: the agent reports an invalid or empty board as a successful check with zero new jobs. Test: a board returning empty JSON must produce exit status incomplete, not finished.

Bug 2: the agent allows file writes outside the approved output directory, for example using ../, a similarly named directory, or a symlink. Test: any such write attempt must be blocked and logged.

## 8. Finished but Wrong Answer

A finished-but-wrong run is one where the agent exits with status finished even though one board returned an empty or invalid response.

To catch it: an independent check reads the saved raw response and evidence, verifies the response structure and posting IDs, and compares them against the agent's reported status. If the evidence shows a board failed but the agent reports finished, the independent check fails. That incorrect run is kept as evidence and explained in the trace.
