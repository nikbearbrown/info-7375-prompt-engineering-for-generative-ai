# GATE — Job-Search Agent 2

Written and committed before Claude Code changed any code for JS2.
Starting point: my JS1 agent (commit aa7c870), copied unchanged in b9ede94.

## Boards for this layer

| Board | ATS | Endpoint | Checked in browser 2026-11-10 |
|---|---|---|---|
| scaleai | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/scaleai/jobs?content=true` | JSON, `meta.total` 169 |
| databricks | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true` | JSON, `meta.total` 916 |
| openai | Ashby | `https://api.ashbyhq.com/posting-api/job-board/openai` | JSON; no `total` field |
| rithika-js2-no-such-board | Greenhouse | `https://boards-api.greenhouse.io/v1/boards/rithika-js2-no-such-board/jobs` | Deliberate failure: `{"status":404,"error":"Job not found"}` |

Two facts from that check shape this gate: the 404 body says "Job not found",
not "board not found", so the agent must go by status code and never read a
failure as "0 jobs"; and Ashby returns no total, so a posting count cannot be
cross-checked against the response itself for that board.

## 1. Exits

A loop that stops is not a loop that succeeded.

| Exit | When | Reports | Code |
|---|---|---|---|
| `finished` | Every planned board fetched and parsed, within budget | Per board: postings seen, new IDs. States that this is the agent's own report, not an independent check | 0 |
| `incomplete` | Loop ended normally but at least one board failed after the error policy | Which boards succeeded and which failed, with HTTP status. New jobs for a failed board: **unknown**, never 0. That board's state file is not updated | 1 |
| `budget_exhausted` | A board, request, or time limit was reached before every board was tried | Which limit, which boards were done, which were never tried | 2 |
| `error` | Run could not proceed safely: invalid résumé or config, unreadable state, or a permission violation | The reason. Nothing written except the trace | 3 |

`finished` means the loop's own criteria were met. It does not mean the answer is correct.

## 2. Budgets

Checked **before** each action. If the next action would exceed a limit, it is not taken; the run stops with `budget_exhausted`.

Budget values (a test checks `config/budgets.json` against these lines):

- max_boards: 4
- max_requests: 8
- max_run_seconds: 90
- max_request_seconds: 20
- max_claude_calls: 0

Reasons: 4 boards is exactly the plan, and a fifth in the config is refused
at startup with `error`. 8 requests is 1 request plus at most 1 retry per
board. 90 seconds covers 4 requests at 20 seconds plus one retry; Databricks
is a large response. 0 Claude calls because this layer is about the loop,
tools, and permissions; first runs on each board are baselines with 0 new
postings to judge.

**Who may change a budget:** only me, by adding a dated entry to the Budget
decisions log below and committing it. The agent and Claude Code never change a budget.

### Budget decisions log

- 2026-11-10: initial values above, set by me.

## 3. Repeat rule

**Same action:** same method + host + full URL (path and query) within one run.

| Situation | What happens |
|---|---|
| Second attempt allowed by the error policy (timeout, connection error, 5xx) | Allowed; traced as `attempt 2 of 2` |
| Any other repeat | Not sent; traced as `repeat_blocked`; board marked failed with that reason |
| Same board twice in config | Refused at startup with `error` |
| Same posting ID twice in one response | Counted once; traced as `duplicate_posting` |
| Same output file written twice | Refused; raw files are named run-id + board + attempt |

## 4. Error policy

Retry only when a second try could honestly give a different answer. Never invent a value for a failed board.

| Failure | Retry | Recorded |
|---|---|---|
| 404 or other 4xx | No: a wrong name returns the same 404 every time | Board failed, status and raw body saved, new jobs unknown, state untouched, escalated |
| 429 rate limited | No: retrying immediately ignores the site's request to slow down | Board failed, `rate_limited`, escalated |
| Timeout, connection error, 5xx | Yes, once, after 2 seconds: usually transient, and a read-only GET cannot change anything on the server | Both attempts traced; if attempt 2 fails, board failed |
| 200 with invalid JSON or missing `jobs` field | No: the server answered and the answer is wrong | Board failed, `malformed_response`, raw saved |
| Permission violation | Never | Whole run stops with `error` |

**Escalate** means a "Needs your attention" section at the top of the report.
The agent never renames a board, changes a URL, or works around a failure.

**Known limit of this first version, stated before building:** a 200 with
zero postings is accepted as a valid empty board. If a board that had
postings suddenly returns none, the run can end `finished` and report
"0 new", which may be wrong. I expect this to be the finished-wrong-answer
case, caught by an independent check rather than by the agent's own report.

## 5. Permission policy

Enforced in Python (`agent/policy.py`), not in a prompt.

**Network**
- Allow-list, exact host match: `boards-api.greenhouse.io`, `api.ashbyhq.com`.
- HTTPS only. GET only. No `Authorization` or `Cookie` headers.
- A redirect to a host off the allow-list is refused.

**Disk**
- Read: `data/`, `config/`, `out/`.
- Write: only `out/` (`out/raw/`, `out/state/`, `out/runs/`).
- Paths are fully resolved (symlinks followed, `..` collapsed) and compared by
  whole path components, never by string prefix (`out-evil/` is not `out/`).
- **Needs my approval:** resetting or deleting a board's state file, because
  that makes every posting look new. Refused unless an approver returns yes;
  with no one to answer, the answer is no.

**Never:** apply, email, message, log in, submit forms, run shell commands, or give Claude tools.

## 6. Wrong versions my tests must catch

Each is built as a mutant in `tests/mutants.py`; `tests/test_mutants.py` must fail on every one.

| # | Wrong version | Breaks |
|---|---|---|
| W1 | Budget checked after a request instead of before | 2 |
| W2 | Retry treated the same as an accidental repeat | 3 |
| W3 | Failed board reported as 0 new jobs | 4 |
| W4 | Failed board's state file still updated | 4 |
| W5 | Exit `finished` although a board failed | 1 |
| W6 | Retries a 404 | 4 |
| W7 | Host check by "ends with" or "contains" | 5 |
| W8 | Path check by string prefix, symlinks not resolved | 5 |
| W9 | Approval defaults to yes when no one answers | 5 |
| W10 | Duplicate posting ID counted twice | 3 |
| W11 | `config/budgets.json` differs from the values in section 2 | 2 |

Decided by: Rithika Sankar Rajeswari 2026-11-10

### Budget decisions log (continued)

- 2026-11-10: max_run_seconds stays 90. Correction to the section 2 reasoning:
  4 requests at the full 20 s plus a 2 s wait and a 20 s retry is 102 s, more
  than 90, so in that worst case the retry is not started and the run ends
  `budget_exhausted`. I accept that. Pointed out by Claude Code in its build
  summary (evidence/2026-11-10_claude_code_build_summary.md).

### Error policy decisions log (continued)

- 2026-11-10: Known limit in section 4 is withdrawn. New rule: if a board's
  saved state has at least one posting and a 200 response now has zero
  postings, the board FAILS with reason `empty_after_nonempty`. New jobs:
  unknown (never 0). State file is not updated. No retry (the response was
  received; retrying would not change it). The run cannot end `finished`.
  A board with no saved state, or whose saved state was already empty, may
  still return zero postings and count as a valid empty board.
  Why: the SEEDED demo (out/runs/20261110T193722Z-SEEDED) ended `finished (0)`
  and reported Scale AI as 0 new when it had 169 the day before; only the
  independent check caught it.
  Decided by: Rithika Sankar Rajeswari 2026-11-10
