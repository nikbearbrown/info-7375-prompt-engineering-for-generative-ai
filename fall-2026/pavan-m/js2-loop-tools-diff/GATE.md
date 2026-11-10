# GATE — Job-Search Agent 2

**Written:** November 9, 2026  
**Author:** Pavan Majji  
**Purpose:** Define the loop's exits, budgets, repeat behavior, error handling, and permissions before making code changes.

**Starting point:** Job-Search Agent 1 (commit `9b66b8d`, a copy of JS1 at `9b381ec`).

## 1. Boards

This run is configured for four boards: three intended valid boards across three applicant-tracking systems, plus one deliberately invalid board to exercise the failure policy.

| Key | ATS | URL / purpose |
|---|---|---|
| `greenhouse:gleanwork` | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/gleanwork/jobs?content=true` |
| `lever:palantir` | Lever | `https://api.lever.co/v0/postings/palantir?mode=json` |
| `ashby:openai` | Ashby | `https://api.ashbyhq.com/posting-api/job-board/openai` |
| `greenhouse:pavan-js2-no-such-board` | Greenhouse | Deliberately invalid board name; intended to exercise the 4xx failure path. When I checked it by hand on November 9 it returned 404 (`evidence/2026-11-09_manual-capture_greenhouse_no-such-board.json`), but the actual response must be recorded during each run, not assumed. |

Every posting is identified by the composite key `<system>:<board>:<id>`. Posting IDs may be strings or integers. Including the ATS and board in the key prevents identical IDs from different boards from colliding.

## 2. Exits

| Status | Condition | Exit code |
|---|---|---:|
| `finished` | Every configured board was attempted and every board succeeded. | 0 |
| `incomplete` | The loop reached the end of the board list, but at least one board failed. | 1 |
| `budget-exhausted` | The loop stopped because the next board or request would exceed a configured budget. | 2 |
| `error` | The run could not proceed safely, such as with invalid configuration, unreadable required state, or a policy violation attempted by the agent's own code. | 3 |

Every run must write a summary containing:
- Final status and reason.
- Boards attempted, succeeded, failed, and not attempted.
- HTTP requests used, including retries.
- Elapsed runtime.
- New-posting counts for successfully processed boards.
- Failure details for unsuccessful boards.
- The path to the run trace and saved raw responses.

A failed board must not be represented as a successful board with zero postings. A run that stops is not automatically a successful run. Since the deliberately invalid board is included in this configuration, a run that reaches it and records its failure should end as `incomplete`, not `finished`.

## 3. Budgets

- Maximum **4 configured boards** per run.
- Maximum **10 HTTP requests** per run, including retries.
- Maximum **60 seconds** total runtime per run.
- Maximum **10 seconds** per HTTP request.
- Check the request and time budgets before starting each request.
- If the next request would exceed a budget, do not send it. Save the trace and summary, identify boards not attempted, and exit with `budget-exhausted`.

Budgets are fixed for this version. They may be changed only through a new, dated written decision in this file, committed before the corresponding code change. They must not be silently increased by the implementation or by Claude Code.

## 4. Repeat Rule

- Within one run, an action is considered the same when its HTTP method and URL string are identical.
- An identical request is blocked unless it is the one explicitly permitted retry for a timeout, connection error, or HTTP 5xx response.
- A board appearing more than once in the configuration is attempted only once. The duplicate is recorded as `repeat_blocked`.
- The same posting ID on different ATS boards is treated as a different posting because the ATS and board are part of the composite key.
- A blocked repeat does not consume an HTTP request because no request is sent.

## 5. Error Policy

| Failure | Retry? | Handling |
|---|---|---|
| HTTP 429 (rate limited) | No | Mark the board failed as `rate_limited`. Retrying immediately would add load and is unlikely to succeed within this run's budget. |
| Other HTTP 4xx, including 404 | No | Mark the board failed with an appropriate client-error reason, such as `bad_board`. |
| Timeout | Once, after 2 seconds | Retry the GET request if the request and runtime budgets permit. |
| Connection error | Once, after 2 seconds | Retry the GET request if the request and runtime budgets permit. |
| HTTP 5xx | Once, after 2 seconds | Retry the GET request if the request and runtime budgets permit. |
| Invalid JSON | No | Mark the board failed as `bad_response`. |
| Unexpected response structure | No | Mark the board failed as `bad_response`. |
| Empty posting list | No | The main loop accepts the empty list as zero postings; the independent checker must flag it. |

A GET is safe to repeat (it changes nothing on the server), and timeouts, connection errors, and 5xx responses are often temporary, so one retry is sound for those. A 4xx means the request itself is wrong, so repeating it will not help.

Additional rules:
- A failed board does not stop processing of the remaining boards.
- A failed board's saved state must not be updated.
- Do not invent a posting count or result for a board that was not successfully read.
- If a needed retry is not sent because of the budget, the board is marked failed (`retry_not_sent_budget`) and the run exits `budget-exhausted`, listing the boards not attempted.
- A refusal caused by a remote board (for example, a redirect to an unapproved host) marks that board failed (`policy_refused`) and the loop continues. A policy violation attempted by the agent's own code ends the run with `error`.
- Escalation means recording the failure in the trace and summary and returning a non-zero exit code. The agent does not contact anyone.

### Intentional empty-board weakness

For the assignment's finished-but-wrong demonstration, the main loop intentionally accepts a syntactically valid empty posting list and may report zero new postings. This is a known weakness, not evidence that the board is genuinely empty.

A separate `check_run.py` script must independently inspect the saved raw response for each successfully fetched board and flag an empty posting list as suspicious. The checker must not rely only on the main loop's summary or reported count. The demonstration must preserve the raw response and show the checker's finding.

The demonstration uses a separate demo configuration (`config/demo_boards.json`) that does not include the deliberately invalid board, so the run can end `finished` while one board's saved response is an empty list. That empty response is constructed from a real capture and labeled CONSTRUCTED in its file name. The live configuration is not changed.

## 6. Permission Policy

The permission policy must be enforced in program code. A prompt or written instruction alone is not enforcement.

### Allowed network hosts

Only these exact hosts are allowed:
- `boards-api.greenhouse.io`
- `api.lever.co`
- `api.ashbyhq.com`

All other hosts are refused. Redirects must also be checked: a redirect to a host outside this allow-list is blocked before the redirected request is sent. Host matching must use parsed hostnames, not substring matching.

### HTTP methods

Only `GET` is allowed. `POST`, `PUT`, `PATCH`, `DELETE`, and any other method must be rejected before a network request is sent.

### File writes

The agent may write only inside the project's `out/` directory.

Layout: board state in `out/state/`, each run's trace and summary in `out/runs/<timestamp>/`, and that run's raw responses in `out/runs/<timestamp>/raw/`. The `evidence/` folder holds my manual captures and is read-only for the agent.

Before writing, the program must resolve and validate the destination path. It must reject:
- Parent-directory traversal such as `..`.
- Absolute paths outside `out/`.
- Sibling or prefix-confusion paths such as `out-evil/`.
- Symlinks inside `out/` that resolve outside `out/`.

The check must compare resolved path ancestry, not string prefixes.

Known limit: the check runs just before each write. It does not protect against a symlink being swapped in between the check and the write itself (a time-of-check/time-of-use race). This version does not claim to handle that case.

### File reads

Reads are restricted to this project and the approved project folders: `config/`, `data/`, `out/`, and `evidence/`. The implementation must not read arbitrary paths supplied by a posting or remote response.

### State-reset approval

Resetting a board's saved state, including replacing it with a fresh baseline, requires explicit approval through the command-line flag:

`--approve reset:<board-key>`

Without the matching approval flag, the reset is refused and the existing state is left unchanged. Approval for one board does not authorize resetting another board.

### Prohibited actions

The agent must never:
- Apply for jobs.
- Send emails or messages.
- Log in to external accounts.
- Submit application forms.
- Follow links contained inside job postings.
- Execute arbitrary shell commands.
- Delete project files.
- Write outside the approved `out/` directory.

## 7. Wrong Implementations the Tests Must Catch

1. A run with a failed board is incorrectly reported as `finished`.
2. A failed or unreadable board is assigned an invented zero-posting result.
3. Retries continue beyond the request or runtime budget, or retry indefinitely.
4. String posting IDs are discarded because the implementation expects integers only.
5. A prefix-based path check incorrectly permits `out-evil/`.
6. A symlink inside `out/` permits a write outside the approved directory.
7. A non-GET request, such as POST, is sent.
8. Saved state advances after a board fails.
9. Identical posting IDs from different boards collide.
10. An empty posting list is treated as a trustworthy zero-job result and is not flagged by the independent checker.
11. A redirect causes a request to an unapproved host.
12. A duplicate board or repeated URL is fetched again without an allowed retry.

## 8. Failure Definition

A run violates this gate if it:
- Reports `finished` while any configured board failed.
- Sends a request to a host outside the allow-list, including by following an unapproved redirect.
- Sends a disallowed HTTP method.
- Exceeds a request, per-request timeout, or total-runtime budget.
- Writes outside `out/`.
- Resets state without the matching explicit approval.
- Advances saved state for a failed board.
- Invents a result for a board it did not successfully read.
- Fails to record its observations, failures, and final exit status.

This gate is the written contract for implementation and testing. Any change to these rules requires a dated revision before the code implementing that change is made.