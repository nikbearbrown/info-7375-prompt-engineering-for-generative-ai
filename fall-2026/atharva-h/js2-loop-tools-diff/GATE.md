# GATE — Job-Search Agent 2

Written before Claude Code touches the code. Decided on 2026-11-01 in an interview: Claude asked one section at a time, and I chose. Added on 2026-11-09, still before any code: no judging in JS2, closed postings in the report, and the no-overwrite rule. A budget or policy here changes only by a new dated entry in this file.

## Scope
- **Starting point:** my Job-Search Agent 1 code in `../js1-contract-and-watch/` (commit `f0b7a6b`): Python standard library, with its allow-list, path check, state, and tests.
- **No judging in JS2 (2026-11-09).** The loop reports which postings are new and which have closed since the last run. JS1's rule and Claude judges stay in JS1.
- **Real boards the loop watches:**

  | System | Host | Board | Employer I expect |
  |---|---|---|---|
  | Greenhouse | `boards-api.greenhouse.io` | `abacusinsights` | Abacus Insights |
  | Ashby | `api.ashbyhq.com` | `valon` | Valon |
  | Lever | `api.lever.co` | `xsolla` | Xsolla |

- **Board that fails on purpose:** Ashby `valonn`, a misspelled name. It returned a real HTTP 404 with a plain-text body (`Not Found`) when probed on 2026-11-01.
- **Finished wrong answer:**
  - **The run:** a run configured with Greenhouse `abacus` as if it were Abacus Insights. On 2026-11-01 that slug was a different employer ("ABACUS", 45 postings), so the run can end cleanly and still be wrong.
  - **The independent check:** a separate command, run after the loop, that never reads the loop's report. It compares the board's own name (Greenhouse `/v1/boards/{token}`) with the employer I configured.

## Exits
Every run ends with exactly one exit status. It is printed and written to the run's trace, along with what that status reports.

| Exit | When | What it reports |
|---|---|---|
| `finished` | Every configured board was fetched, parsed, and its state saved, within budget. | Per-board posting counts, the new postings, and the postings that closed since the last run. |
| `incomplete` | At least one board did not succeed: it failed after the error policy, or it was never reached because the run was interrupted. | Each such board, its error, and the requests spent on it. A failed board's previous state is left untouched. |
| `budget-exhausted` | The next action would exceed a budget, so the loop stopped before taking it. | Which budget, the boards not visited, and everything done before the stop. |
| `error` | The loop cannot continue safely: a permission violation, an invalid persona or config, or state it can't read or write. | The refused action or the error. The run stops immediately and writes no state afterward. |

If more than one applies, the order is `error`, then `budget-exhausted`, then `incomplete`, then `finished`. Only `finished` means every board succeeded. A loop that stops is not a loop that succeeded.

## Budgets
- **Boards:** at most 5 per run.
- **HTTP requests:** at most 10 per run. Every request counts, including retries.
- **Time:** at most 60 seconds of wall-clock time per run. A request's timeout never reaches past the time left.
- **Checked before every action.** If the next action would go over any budget, the run exits `budget-exhausted` without taking that action.
- **Who may change them:** only a new dated decision in this file. A test fails if the budgets in the code differ from the numbers here.

## Repeat rule
- **Same action:** the same HTTP method and the same URL within one run. Different boards on the same host are different actions.
- **A second identical request** is sent only when the error policy counts it as a retry. Otherwise it is refused, recorded in the trace as `repeat refused` with its URL, and the run continues.

## Error policy
- **HTTP 404 or any other 4xx:** no retry. A wrong name won't fix itself, and asking again would only spend budget. The board is recorded as failed.
- **Timeout, dropped connection, or HTTP 5xx:** retry once after 2 seconds; the retry counts against the request budget. If the retry also fails, the board is recorded as failed.
- **Why one retry is sound:** these failures are often transient and clear within seconds, and one more request fits the budget. Retrying more would keep spending budget on a board that is down.
- **A response that can't be parsed** (for example, Ashby's plain-text `Not Found`) is a failure of that board, not a crash of the loop.
- **Failed boards:**
  - A failed board is never treated as an empty list, and no value is invented for it.
  - Its previous state is kept as it was.
  - The run exits `incomplete`.
  - The failure is listed in the run report for me to look at.

## Permission policy
These rules are enforced in the program, not in a prompt.

- **Network:**
  - Only HTTPS `GET` requests to `boards-api.greenhouse.io`, `api.ashbyhq.com`, and `api.lever.co`. Every redirect is checked against the same list.
  - No other HTTP method. No cookies. No `Authorization` header.
- **Reads:** any file inside this folder (`js2-loop-tools-diff/`), and nothing outside it.
- **Writes:**
  - Only inside this folder's `runs/` and `state/`, judged after resolving `..` and symlinks.
  - A sibling folder that merely shares a prefix, such as `runs-evil/`, is outside.
  - A path that is readable is not, by that fact, writable.
  - **No overwrite (2026-11-09).** A run never overwrites an earlier run's folder or report. Every run gets a new folder, and the loop refuses one that already exists. A normal run only adds seen ids and never drops any.
- **Writes that need my approval first:**
  - resetting or overwriting state so that seen ids are dropped
  - deleting a run folder
  - changing the board list
  - any single write over 5 MB

  The agent asks y/N in the terminal and waits. If no one is at a terminal, the answer is no.
- **Never:** apply, email, message, or log in. GET-only requests with no credentials mean the agent's HTTP tool cannot do any of these.
- **Any action this policy refuses** stops the run with `error`.

## Wrong versions
1. **Prefix path check.** Writes are checked with `path.startswith("runs")`, so `runs-evil/`, and a symlink inside `runs/` that points outside, both get through.
2. **Failed board = no new jobs.** A 404 or timeout is treated as an empty board. The run looks fine, a value is invented, the board's state can be wiped, and the run exits `finished`.
3. **Substring host check.** Hosts are checked with `"greenhouse.io" in url`, so `boards-api.greenhouse.io.evil.example` and `http://` URLs pass.
4. **Retries not counted.** The budget counts boards rather than requests, so retries go uncounted and a run can exceed 10 requests and still report `finished`.

## Decisions after the gate

### 2026-11-10 — Greenhouse board identity (accepted in review)
- **The rule.** Before fetching a Greenhouse board's job list, the loop asks Greenhouse for the board's own name (`/v1/boards/{token}`). If that name does not match the employer in the config (case and punctuation ignored), the board fails: its job list is not fetched, its state is not touched, and the run exits `incomplete`.
- **Error policy and budgets.** The name request follows the same error policy as a job-list request. It costs one request per Greenhouse board, which fits within the budgets above.
- **Why.** The wrong-board run (`runs/2026-11-09T205807Z_WRONG-BOARD-demo`) ended `finished` on another employer's board.
- **Evidence.** My test `tests/test_review_identity.py` was committed before the patch (`a81c572`) and failed on the old code. After the patch, the same real wrong board (`runs/2026-11-10T170122Z_WRONG-BOARD-after-patch`) ended `incomplete` after one request, saved no ids, and gave this reason: `identity mismatch: the board calls itself 'ABACUS', but the config says 'Abacus Insights'`.
- **Limit.** Ashby and Lever have no public name endpoint, so the check covers Greenhouse only. A valid Ashby (or Lever) board for the wrong employer could still finish cleanly.
