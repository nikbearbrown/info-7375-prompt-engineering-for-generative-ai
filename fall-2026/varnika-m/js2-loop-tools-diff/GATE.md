# GATE.md — Job-Search Agent 2

**Written:** 2026-11-10, before any JS2 code or tests existed.
**Drafted by:** Claude Code (Opus 5.5), at my request. I replied "ok" to keep the draft as it was, with no changes, before it was committed. `SOURCES.md` records who wrote what.

This file is the gate. The loop, its tests and its permission checks are written from it. If the code and this file disagree, the code is wrong. If this file is wrong, I change it here first, with a dated entry under **Decisions**, and only then change the code.

## 0. What the loop does

One run walks a fixed list of boards from `config/boards.json`, one board at a time, in order. For each board it:

1. asks the permission policy whether it may fetch the board's URL;
2. fetches it once (with retries only where section 4 allows them);
3. saves the raw response, byte for byte, before parsing it;
4. classifies the response (`ok`, `failed` or `suspect`);
5. for an `ok` board only, compares posting ids with that board's state file and reports the new ones, each with the JS1 rule's verdict (R1–R5 of JS1's `CONTRACT.md`);
6. writes one trace line for every step: what it asked for, what the policy decided, what came back, and how much budget is left.

The boards for this assignment:

| # | System | Board | URL |
|---|---|---|---|
| 1 | Greenhouse | `anthropic` | `https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true` |
| 2 | Lever | `palantir` | `https://api.lever.co/v0/postings/palantir?mode=json` |
| 3 | Ashby | `linear` | `https://api.ashbyhq.com/posting-api/job-board/linear` |
| 4 | Greenhouse | `js2-deliberately-missing-board` | `https://boards-api.greenhouse.io/v1/boards/js2-deliberately-missing-board/jobs?content=true` |

Board 4 fails on purpose: the name does not exist, and Greenhouse answers `404`. It is there so every run shows the error policy working.

The Anthropic board starts from JS1's state file (675 ids seen by 2026-10-31), so its first JS2 run is a watch, not a baseline. Lever and Ashby start with no state, so their first run is a baseline: every id is recorded and none is reported as new.

## 1. Exits

Every run ends with exactly one exit. The exit is written in the run record, the report and the last trace line, and it sets the process exit code, so a script cannot mistake a stop for a success.

| Exit | When | What it reports | Exit code |
|---|---|---|---:|
| `finished` | Every board in the list was attempted within budget, and every board's status is `ok` (or `skipped_repeat`, see section 3). | Per board: postings, new, gone since last run. Every new posting with its rule verdict. Budget used. | 0 |
| `incomplete` | Every board was attempted within budget, but at least one board is `failed` or `suspect`. | The same as `finished` for the `ok` boards. For each failed or suspect board: the reason, the HTTP status or error, the saved raw response if there was one, and **no counts** (they are `null`, never `0`). Its state is not changed. | 2 |
| `budget_exhausted` | A budget in section 2 ran out before every board was attempted. | Which budget ran out, which boards were attempted and their statuses, which boards were **not** attempted. State is updated only for boards that ended `ok`. | 3 |
| `error` | The run cannot go on safely: the config or a state file cannot be read, the persona is not fictional, the policy refused an action the loop itself asked for (section 5), the repeat limit was hit (section 3), or an unexpected exception. | The error and the step where it happened. Nothing else is written after the error except the last trace line and the run record. | 1 |

**`finished` is not the same as correct.** `finished` only says the loop did what it planned to do and every response looked usable. It does not say the board really has no new jobs. That claim is checked separately, by `check_run.py`, which does not use the loop's own report (section 7).

## 2. Budgets

| Budget | Limit per run | Why this number |
|---|---:|---|
| Boards | 5 | Four boards are configured. One spare so adding a board is a written decision, not an accident. |
| Requests | 8 | 4 boards × 1 request, plus room for 4 retries. A run where many boards need retries should stop as `budget_exhausted`, not keep trying. |
| Seconds | 120 | One run is 4 GET requests. Palantir's response is about 6 MB, the largest. |
| Seconds per request | 30, or the seconds left in the run if fewer | One slow board cannot use the whole run. |
| Bytes per response | 20,000,000 | The largest board (Palantir) is about 6 MB. A response larger than this is not read to the end. |

- Retries count against the request budget and the seconds budget. So do requests that fail.
- The loop checks the budget **before** every request. It never starts a request it cannot afford, and it gives each request at most the seconds left in the run.
- **Who may change a budget:** only me, and only by a new dated entry under **Decisions** below, followed by a code change that matches it. The program has no flag or setting that **raises** a budget. Command-line flags may only **lower** one, for tests and demonstrations.

## 3. Repeat rule

**What counts as "the same" action:**

- **The same board:** the same system and the same board name, ignoring upper and lower case (`Greenhouse/Anthropic` and `greenhouse/anthropic` are the same).
- **The same fetch:** the same method and the same URL after normalizing it: scheme and host in lower case, the default port removed, and query parameters sorted.
- **The same write:** the same file, after resolving `..` and symbolic links to a real path.

**What the loop does:**

- A board that appears twice in the config is watched once. The second entry is recorded as `skipped_repeat` and uses no request. It does not stop the run from finishing.
- A fetch the loop has already made successfully in this run is refused without being sent.
- A retry is the only allowed repeat of a fetch, and only after a transient failure (section 4), at most 2 retries per board.
- Raw responses and run records are written once. A second write to the same file is refused.
- If the loop has 3 refused repeats in one run, it is stuck: it stops with exit `error` and reason `repeat_limit`.

## 4. Error policy

What happens when a board fails. A failed board never gets an invented value: its counts are `null`, its new-postings list is absent, and its state file is not touched.

| What came back | Board status | Retry? | Why |
|---|---|---|---|
| `404` or `410` (no such board) | `failed: not_found` | **No** | The board name is wrong or the board is gone. Asking again gives the same answer, so a retry only spends budget. **Escalate to me:** the report tells me to check the board name. |
| `401` or `403` | `failed: forbidden` | **No** | The board wants a login. The agent never logs in. Escalate to me. |
| Any other `4xx` | `failed: http_4xx` | **No** | The request itself is wrong; repeating it does not fix it. |
| Timeout, connection error, `429`, `500`, `502`, `503`, `504` | retried, then `failed: transient` if it still fails | **Yes, at most 2 retries**, after waiting 2 s, then 4 s | These errors are about the server or the network at that moment, not about the request. A GET to a public, read-only board changes nothing, so asking again is safe. A `429` with a `Retry-After` longer than 10 s is not retried. Every retry must fit the request and seconds budgets. |
| A redirect to a host or path the policy refuses | `failed: refused_redirect` | **No** | The redirect is not followed (section 5). |
| `200`, but the body is not JSON, or does not have the shape this system sends (a `jobs` list for Greenhouse and Ashby, a list for Lever) | `failed: bad_shape` | **No** | The board answered, but not with a board. Parsing a guess would invent data. |
| `200`, but the response is larger than the byte budget | `failed: too_large` | **No** | Reading it to the end would break the budget. |
| `200` with **zero** postings | `suspect: empty` | **No** | An empty list is not proof of "no jobs". It is what an outage, a wrong board or a changed API can look like. The board's state is not updated, the run cannot end `finished`, and the report asks me to check the board's public page by hand. |
| `200` with one or more postings | `ok` | — | Compared with the board's state; new ids reported. |

After a failed or suspect board, the loop goes on to the next board. One bad board should not hide the others. The run then ends `incomplete`, not `finished`.

## 5. Permission policy

The policy is enforced in code, in one place (`agent/policy.py`). Every network request and every file read or write the agent makes goes through it, and the agent has no other way to reach the network or the disk. A refused action is not attempted, and the refusal is written to the trace.

**Hosts.** Only HTTPS `GET` to exactly these hosts, on port 443, with no user name or password in the URL:

| Host | Allowed paths |
|---|---|
| `boards-api.greenhouse.io` | `/v1/boards/<board>/jobs` |
| `api.lever.co` | `/v0/postings/<board>` |
| `api.ashbyhq.com` | `/posting-api/job-board/<board>` |

`<board>` is letters, digits and hyphens only. The host must match exactly: not a subdomain (`evil.api.lever.co`), not a longer name (`api.lever.co.evil.example`), and not the allowed name hidden in the path or query (`https://evil.example/?u=api.lever.co`). Redirects are checked by the same rule before they are followed.

**Folders.**

| Request | Where | Decision |
|---|---|---|
| Read | Inside this folder (`js2-loop-tools-diff/`): `config/`, `persona/`, `jobs/`, `fixtures/` | allowed |
| Read | Anywhere else (my home folder, my real résumé, `~/.ssh`) | refused |
| Write a new file | Inside `jobs/` only (`jobs/raw/`, `jobs/runs/`, `jobs/state/`) | allowed |
| Write | `config/`, `persona/`, code, tests, or anything outside `jobs/` | refused |
| Overwrite | An existing raw response or run record in `jobs/` | refused (evidence is written once) |
| Update a state file | Only adds ids to what it already holds | allowed |
| Replace a state file with one that **drops** seen ids (a reset) | `jobs/state/` | **needs my approval**: refused unless I give `--approve-state-reset <board>` on the command line for that board in that run |

Paths are checked after resolving `..` and symbolic links to a real path, and containment is checked by path components, not by comparing strings. So `jobs/../config/boards.json` and a symbolic link inside `jobs/` that points outside are both outside `jobs/`. A folder named `jobs-evil/` next to `jobs/` is not inside `jobs/`, even though its name starts with `jobs`.

**Never.** The agent never applies to a job, sends email, sends a message, logs in, sends cookies or credentials, makes a request other than `GET`, calls a host off the list above, or runs a shell command. It has no tool that could do any of these. A URL for an apply page, a `mailto:` link or any `POST` is refused by the policy even if something asks for it.

**Approval.** Only I can approve, and only by typing the flag for one run. The agent cannot approve its own request, and an approval is not remembered between runs. The trace records that the approval came from a command-line flag. It cannot prove that a person typed it.

## 6. Wrong versions

Plausible implementations that look right and are wrong. Each one must make at least one test fail.

| # | Wrong version | The test that must catch it |
|---|---|---|
| W1 | Folder check by string prefix (`str(path).startswith(str(jobs))`) | Writing `jobs-evil/x.json` is refused. |
| W2 | Folder check on the path as written, before resolving symbolic links | Writing through a symbolic link in `jobs/` that points outside is refused. |
| W3 | `..` not resolved before the check | Writing `jobs/../config/boards.json` is refused. |
| W4 | Host check by substring or by "ends with" | `api.lever.co.evil.example`, `evil.api.lever.co` and `https://evil.example/?u=api.lever.co` are refused. |
| W5 | An empty board reported as "no new jobs", with exit `finished` | A `200` with zero postings makes the board `suspect: empty`, leaves its state unchanged, and the run ends `incomplete`. |
| W6 | A failed board recorded as 0 postings, or its state overwritten | After a `404`, the board's counts are `null` and its state file is byte-for-byte unchanged. |
| W7 | Every stop reported as `finished` | A run with a lowered request budget that cannot reach every board ends `budget_exhausted`, and lists the boards not attempted. |
| W8 | Retrying everything, or retrying forever | A `404` is requested exactly once. A board that keeps answering `503` is requested exactly 3 times, then `failed: transient`. |
| W9 | Following a redirect without checking it | A redirect to a host off the list is not followed. |
| W10 | A flag or setting that raises a budget | Asking for more requests than section 2 allows is refused before the run starts. |
| W11 | The same board watched twice | A config with the same board twice makes one request for it, and the second entry is `skipped_repeat`. |
| W12 | The budget checked only between boards | A request is never given more seconds than are left in the run. |

## 7. How I will know a finished run is right

The loop's own report can be wrong and still say `finished`. So `check_run.py` checks a run from the outside. It does not import the loop's code. It reads the trace, the saved raw responses and the state files, and checks that:

- every saved raw response's SHA-256 matches the trace;
- its own count of postings in each raw response matches the count the loop reported;
- no board with zero postings, or with a failure, is counted in a `finished` run;
- a board whose count dropped to zero since its last good run is flagged, whatever the loop said;
- the requests in the trace are within the budgets, and every request went to an allowed host.

## Decisions

Budgets and policies change only by a new dated entry here.

- **2026-11-10:** First version (this file).
- **November 10, 2026 — the time budget (my decisions, after review findings 2 and 5).** These are separate from findings 8b and 8c (503 retries and redirects to another board), which are still open.
  1. **Invalid time budget:** If the time budget is invalid, such as NaN, or cannot be checked reliably, the agent should fail safely. It must not continue running without a valid time limit.
  2. **Independent check:** Yes, the independent checker should enforce the same time budget as the agent. It should independently verify the total time and that no request was allowed to exceed the remaining budget.

  *How the code follows them (Claude Code's note; tests `304b599`, changes `71491b1`):*
  - A NaN budget flag is refused before the run starts (finding 2).
  - If the clock gives a time that is not a finite number, the run stops at the next budget check with exit `error`, reason `time_budget_invalid`. No further request is made, and the record and trace write `null`, never a guessed number.
  - Each fetch line in the trace now records `started_t` and `seconds_left_at_start`, measured at the same moment the time left was computed.
  - `check_run.py` checks every request against GATE.md's own numbers, with no slack beyond rounding (0.01 s):
    - it must not start after the budget is spent;
    - its timeout must not be more than the seconds left at its start.
  - For the total time, it allows 5 s for work done after the last request (parsing and writing files, which no request's timeout covers).
  - A total or start time that is not a number fails the check.
  - Traces written before this decision do not record `started_t`, so for those the check estimates each start and allows 5 s.
