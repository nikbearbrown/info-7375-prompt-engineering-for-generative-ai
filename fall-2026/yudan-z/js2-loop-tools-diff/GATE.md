# GATE — Job-Search Agent 2: exits, budgets and policy, written before the code

## Executive summary

This page fixes, before Claude Code changes any code, how my agent's loop may end, how much one run may spend, what counts as repeating itself, what it does when a board fails, and what it may touch.
- The starting point is my own Job-Search Agent 1 code, copied unchanged (commit `317d931`).
- Each decision below is mine. Claude Code drafted the wording, and I chose the options and approved the text on 2026-11-09.
- A budget or policy changes only by a new dated entry under **Revisions**, never by editing a line above it.

## 1. What one run does

One run walks a fixed list of boards in order: fetch, save the raw response, compare ids with the seen list, then judge new postings with my JS1 rule.

| Board | System (ATS) | Endpoint host | Why it is here |
|---|---|---|---|
| `pinterest` | Greenhouse | `boards-api.greenhouse.io` | carried over from JS1 |
| `databricks` | Greenhouse | `boards-api.greenhouse.io` | many postings, so a real change between days is likely |
| `ramp` | Ashby | `api.ashbyhq.com` | second system |
| `palantir` | Lever | `api.lever.co` | third system |
| `no-such-board-js2` | Greenhouse | `boards-api.greenhouse.io` | **fails on purpose** (the board does not exist, HTTP 404) |

## 2. Exits

Every run ends with exactly one exit status, printed and written to the trace. **A loop that stops is not a loop that succeeded.**

| Exit | When | What it reports |
|---|---|---|
| `finished` | every listed board was fetched, saved and compared | per board: postings, new ids, rule verdicts |
| `incomplete` | at least one board failed after the error policy, and the others finished | the same for the boards that finished, plus each failed board, its last error and the attempts made. **A failed board reports no posting count and no "0 new"**; its seen ids are kept unchanged |
| `budget-exhausted` | a budget below would be exceeded by the next action | everything finished so far, and the boards not reached |
| `error` | a permission refusal, a corrupt state file, or a response that is not the expected shape | the refusal or error, and the action that caused it; nothing after it runs |

Only `finished` may be described as success. The process exit code differs per status (0, 3, 4, 2), so a script cannot mistake one for another.

## 3. Budgets

| Budget | Maximum per run | Counted how |
|---|---|---|
| Boards | **6** | each board attempted counts once, including the failing one |
| Requests | **12** | every network request counts, **including retries** |
| Seconds | **120** | wall-clock time from the start of the run, checked before each request |

These are enough for five boards with one retry each (10 requests). Only I may change a budget, and only by a new dated entry under Revisions. A command-line flag may lower a budget for a test; nothing may raise it.

## 4. Repeat rule

- **The same action** means the same tool with the same target: the same `GET` URL after normalisation (lower-case host, no trailing slash), or a write to the same resolved path.
- A second identical fetch in one run is **refused and recorded as a repeat**, except the single retry the error policy allows.
- A board listed twice is fetched once; the second entry is recorded as a repeat.
- Writing the same evidence path twice is refused (evidence is never overwritten).

## 5. Error policy

| Failure | What the loop does | Why |
|---|---|---|
| Timeout, connection error, HTTP 5xx or 429 | **retry once**, then mark the board failed | these can be temporary, so one retry is reasonable. A second retry would mostly spend budget on a board that is down |
| HTTP 404 or other 4xx | **no retry**; mark the board failed | "does not exist" will not change in a second |
| 200 with a body that is not the expected shape | no retry; stop the run with `error` | the data cannot be trusted, and guessing would invent values |
| Any failed board | continue with the next board; exit `incomplete`; list it for me | one bad board should not hide the others, but I must see it |

A failed board never gets a value invented for it: no "0 postings", no "0 new", and no change to its seen ids.

## 6. Permission policy, enforced in code

| | Allowed | Everything else |
|---|---|---|
| **Hosts** (network) | `boards-api.greenhouse.io`, `api.ashbyhq.com`, `api.lever.co`, `GET` only, `https` only | refused before any request is made |
| **Read** | files inside this project folder | refused |
| **Write** | files inside `runs/` only, after resolving `..` and symbolic links; the check compares whole path parts, so `runs-evil/` is not inside `runs/` | refused |
| **Writes that need my approval** | (a) resetting a board's seen-id list; (b) deleting or overwriting any saved evidence file | refused unless the run was started with my explicit `--approve` for that exact action |
| **Never** | applying to a job, sending email or any message, logging in anywhere, sending credentials | there is no tool for these; a request for one is refused |

The policy lives in one module that every tool call passes through. It is not in a prompt.

## 7. Wrong versions my tests must catch

| | Plausible but wrong | What would go wrong |
|---|---|---|
| W1 | a failed or empty board is reported as "0 new" and the run as `finished` | a dead board looks like a quiet board |
| W2 | retries on 404, or retries without limit | wasted budget, and the loop never ends on a dead board |
| W3 | the write check uses a string prefix (`startswith("runs")`) | `runs-evil/x` and `runs/../x` pass |
| W4 | retries are not counted against the request budget | the budget can be exceeded |
| W5 | a failed board's seen ids are cleared or overwritten | next run reports old postings as new |

## 8. Failure sentence (2026-11-09, before any run)

This agent has failed if a run reports `finished` while any board failed or was not reached, reports a number for a board it could not read, makes a request or write the policy forbids, or spends more than its budget.

## Revisions

### 2026-11-09, after reading Lectern: redirects

- **What happened.** Reading the instructor's Lectern collector (`collect.py` refuses redirects), I saw that my fetch followed HTTP redirects. An allow-listed host answering `302 Location: https://elsewhere/` would make the agent request a host the policy never checked.
- **Decision (mine).** The fetch tool never follows a redirect. A 3xx answer is recorded in the trace and treated like a 4xx under §5: no retry, the board is marked failed, the run ends `incomplete`.
- **Test, written before the change:** `RedirectTests.test_redirect_is_not_followed` (two local servers; the second must receive no request).
