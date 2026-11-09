# GATE: Job-Search Agent 2

Pavithra Prasad · INFO 7375 · JS2 · 2026-11-09 · my draft, written before any code

1. Exits: my loop ends in one of 4 ways:
   finished (all boards checked) -> reports the jobs found and the final relevant-job count.
   incomplete (some boards failed) -> reports which boards failed, why, and the partial results.
   budget-exhausted (hit a limit) -> reports which limit was reached and the work completed before stopping.
   error (something broke, e.g. an invalid response format) -> reports the error and the last completed action.

2. Budgets per run: max 5 boards, 10 requests, 60 seconds.
   Only I can change them, by editing the version-controlled configuration before the run.

3. Repeat rule: "the same action" means the same HTTP method, host, board, endpoint, and parameters, except for one allowed retry after a transient failure.
   If it happens, the loop stops and reports a repeated-action error.

4. Error policy: when a board fails, the loop retries once and then records the failure and continues.
   Retry only for a timeout, HTTP 429, or HTTP 5xx response, because these failures may be temporary.
   It does not retry a wrong board name, HTTP 4xx response other than 429, or invalid data.

5. Permissions: it may call only boards-api.greenhouse.io, api.lever.co, and api.ashbyhq.com.
   It may write only inside the repository's runs and evidence folders.
   It needs my approval before changing the board list, budgets, allowed hosts, or relevance rules.
   It must never submit applications, log into accounts, contact employers, call another host, or write outside the approved folders.

6. Wrong versions my tests must catch:
   (a) a version that repeatedly retries a permanently failing board
   (b) a version that exceeds the request budget or calls a host outside the allowlist

7. Truth (TA's tip): my written rule decides whether a job is relevant,
   and any hand check follows it.
