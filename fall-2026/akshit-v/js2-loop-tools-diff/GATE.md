# GATE — Job-Search Agent 2

Written 2026-11-10, before Claude Code wrote any code for this assignment.
**Provenance:** Claude Code proposed every decision below as a numbered suggestion. On 2026-11-10 I accepted all seven unchanged, answering "Okay" to each (see SOURCES.md). These are now my rules. Each one changes only through a new dated entry at the end of this file.

## 1. Starting point and boards

The agent builds on my Job-Search Agent 1 code. The persona is still **Jack Spencer** (fictional).

| Board | Applicant-tracking system | Endpoint | Purpose |
|---|---|---|---|
| `figma` | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true` | real board |
| `spotify` | Lever | `https://api.lever.co/v0/postings/spotify?mode=json` | real board |
| `snowflake` | Ashby | `https://api.ashbyhq.com/posting-api/job-board/snowflake` | real board |
| `no-such-board-js2` | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/no-such-board-js2/jobs?content=true` | **fails on purpose** (HTTP 404) |

## 2. Exits

Every run ends in exactly one of these four statuses. A loop that stops is not a loop that succeeded.

| Exit | When | What it reports |
|---|---|---|
| `finished` | Every planned board was fetched and checked. | New postings per board. |
| `incomplete` | At least one board failed after the error policy, and the others succeeded. | Results for the good boards, plus each failed board and why. **Never** reported as `finished`. |
| `budget_exhausted` | A budget (section 3) was reached before every board was done. | What was done, and which boards were not attempted. |
| `error` | The run could not start or continue at all: a bad résumé, a corrupt state file, a permission violation, or every board failed. | The cause. **No** postings are recorded as new, and the state file is not changed. |

## 3. Budgets (per run)

| Budget | Limit | Counting |
|---|---|---|
| Boards | **5** | boards attempted |
| HTTP requests | **10** | every request, **including retries** |
| Wall-clock seconds | **60** | checked before each request |

When a budget would be exceeded, the loop stops before making that request and exits `budget_exhausted`. A budget changes **only** through a new dated entry in this file, written by me. A command-line flag alone cannot raise a budget.

## 4. Repeat rule

"The same action" means the same HTTP method, host, and normalized URL within one run. A second identical request is **refused** and logged as `repeat_refused`. The only exception is a retry allowed by the error policy (section 5), which is logged as a retry and counts against the request budget.

## 5. Error policy for a failed board

| Failure | Action | Why |
|---|---|---|
| HTTP 404, or a bad board name | **no retry**; the board is marked failed | Retrying cannot change the answer. |
| Timeout, connection error, or HTTP 5xx | retry **once**, after 2 seconds | These are often temporary, so one retry is sound. It is bounded and counted. |
| Empty or malformed response (no job list, or zero jobs where the board previously had jobs) | **no retry**; the board is marked failed as `suspicious_empty` | An empty board is **never** reported as "no new jobs". The agent does not invent a value. |
| Every board failed | exit `error` and **escalate to me** | Nothing trustworthy came back, so the run stops and a person decides. |

## 6. Permission policy (enforced in code, not in a prompt)

- **Hosts:** only `boards-api.greenhouse.io`, `api.lever.co`, and `api.ashbyhq.com`. HTTPS only, GET only. Redirects must also stay on the allow-list.
- **Writes:** only inside the output folder `out/` (evidence, state, run traces). Refused:
  - any path that resolves outside `out/`, including `..` segments;
  - a look-alike sibling folder such as `out-evil/`;
  - a symlink inside `out/` that points outside it.
- **Reads:** allowed anywhere inside the project folder; refused outside it.
- **Needs my approval:** resetting or deleting the state file. This requires an explicit `--approve reset-state` flag. Without it, the request is refused.
- **Never:** apply, email, message, or log in. The program contains no tool for any of these. Any HTTP method other than GET is refused.

## 7. Wrong versions my tests must catch

- **W-a. A finished wrong answer.** An empty response is reported as `finished` with "no new jobs". The independent check must catch it, not the agent's own report.
- **W-b. Prefix path check.** The write check compares string prefixes (`str(path).startswith("out")`), so `out-evil/x` is wrongly accepted as inside `out/`.

## Dated entries

- **2026-11-10, approved by me after the review packet (see REVIEW_PACKET.md).** The 60-second budget is unchanged. How it is enforced is now explicit: before each request, the loop computes the time left. If less than **1 second** is left, it stops with `budget_exhausted` without sending. Otherwise the request's timeout is at most the time left (and never more than 20 seconds).
