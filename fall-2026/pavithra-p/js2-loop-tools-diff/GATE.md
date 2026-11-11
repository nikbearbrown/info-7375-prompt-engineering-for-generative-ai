# GATE: Job-Search Agent 2

Pavithra Prasad · INFO 7375 · JS2 · 2026-11-09 · written before any code (my draft: commit `034c127`)

One run of the loop checks a fixed list of boards, one request at a time, for a fictional candidate (Rohan Mehta, carried over from JS1).

| # | Board | System | Host |
|---|---|---|---|
| 1 | pinterest | Greenhouse | boards-api.greenhouse.io |
| 2 | figma | Greenhouse | boards-api.greenhouse.io |
| 3 | spotify | Lever | api.lever.co |
| 4 | ramp | Ashby | api.ashbyhq.com |
| 5 | no-such-board | Lever | api.lever.co (fails on purpose: the name does not exist) |

## Exits

Every run ends with exactly one status, written in the run's trace and report. A loop that stops is not a loop that succeeded: only `finished` means every board was checked.

| Status | When | Reports |
|---|---|---|
| `finished` | every board was checked | the jobs found, the new jobs, and the final relevant-job count |
| `incomplete` | at least one board failed after the error policy, the others were checked | which boards failed and why, and the partial results |
| `budget-exhausted` | the next step would break a budget | which limit was reached and the work completed before stopping |
| `error` | the loop itself broke: a repeated action, a policy refusal, or an unexpected exception | the error and the last completed action |

A board whose response is not valid JSON or has the wrong shape is a failed board (`incomplete`), not an `error`. A failed board is reported as failed with its reason, never as "0 jobs" or "no new jobs".

## Budgets

Per run: at most 5 boards, 10 requests and 60 seconds. Each request times out after 10 seconds. The loop checks the budgets before every request; if the next request would break one, it stops with `budget-exhausted`.

Only I can change a budget, the board list or the allowed hosts, by editing the version-controlled `config/` files before a run and committing that change.

## Repeat rule

"The same action" means the same HTTP method, host, path and query parameters. The only allowed repeat is one retry after a transient failure (below). Any other repeat stops the loop with `error` ("repeated action").

## Error policy

When a board fails, the loop retries once and then records the failure and continues with the next board.

* Retry once, after a 2-second wait, only for a timeout, HTTP 429 or HTTP 5xx, because these failures may be temporary.
* Do not retry a wrong board name (HTTP 404), any other HTTP 4xx, or invalid data: asking again will not change the answer.
* Every attempt, including the failed ones, is saved in the trace, and every response body that arrived is saved as raw evidence.

## Permission policy

Enforced in the program (`agent/policy.py`), not in a prompt.

* **Hosts:** only `boards-api.greenhouse.io`, `api.lever.co` and `api.ashbyhq.com`, over https, GET only. A redirect to any other host is refused.
* **Writes:** only inside this folder's `runs/` and `evidence/` folders (the seen-jobs state lives in `runs/state/`). A path is checked after resolving it: `..`, a look-alike folder such as `runs-evil/`, and a symlink that points outside are all refused.
* **Reads:** files inside this folder may be read; reading never needs approval.
* **Needs my approval:** writing to `config/` (board list, budgets, hosts) or to the relevance rule. Without my explicit approval the write is refused. The loop never makes these writes during a run.
* **Never:** submit applications, log in, contact employers or anyone else, call another host, write outside the approved folders, or store credentials.

## Wrong versions my tests must catch

1. A version that repeatedly retries a permanently failing board.
2. A version that goes over the request budget or calls a host outside the allow-list.
3. A version that reports a failed board as "0 new jobs" and ends `finished` (added in review: a finished wrong answer).

## Truth

My written rule (the relevance rule from JS1's `CONTRACT.md`, carried into this folder) decides whether a job is relevant. Claude's verdict is a judgment, labelled as one. Any hand check follows the rule.

## What a failure looks like

2026-11-09: The run fails if it reports a board it could not read as checked, goes over a budget or the allow-list, writes outside `runs/` or `evidence/`, or ends `finished` when a board failed.
