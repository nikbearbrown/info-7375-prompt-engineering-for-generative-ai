# GATE — Job-Search Agent 2

**Written 2026-11-09, before any JS2 code existed.** Its sha256 and time are in `evidence/TIMELINE.md`.

**Who wrote what.** Omkar handed the whole assignment to Claude Code on 2026-11-09 (about 07:50 UTC) and then went offline. He did not answer any gate question in this session. So every decision below is a **[Claude, proposed]** default. It holds until Omkar confirms or changes it in the *Omkar's decisions* section at the end. The code enforces these values as written. If Omkar changes one, the change goes in the change log, `config/budgets.json` is edited to match, and the tests are rerun.

Starting point: **my JS1 agent** (`../js1-contract-and-watch/`). From it, `persona.py` and `rule.py` are copied unchanged, along with the fictional persona Aarav Patel and the contract-v2 rule. The ATS endpoints and the slug traps come from the instructor's **Lectern** (`fall-2026/nik-bear-brown/lectern/ATS.md`). It was read as a reference, and no code was copied from it.

---

## 1. Exits

A loop that stops has not necessarily succeeded. Every run ends in exactly one of these four statuses. Each one is written to `report.json` (`exit.status`), to the last line of `trace.jsonl`, and to the process exit code.

| Exit | When | What it reports | Code |
|---|---|---|---:|
| `finished` | Every board on the watch list was attempted, **and** every board returned a non-empty, schema-valid list of postings. | Per board: postings seen, new since last run, removed, and the rule's verdict on each new posting. | 0 |
| `incomplete` | Every board was attempted within budget, but at least one board ended `error`, `refused`, `empty_unverified` or `repeat_skipped`. | Same as `finished`, plus **which boards did not yield an answer and why**. A failed board's posting count is `null`, never `0`. | 3 |
| `budget_exhausted` | A budget (boards, requests or seconds) ran out **before** every board was attempted. | The boards already done, plus the boards **not attempted**, listed by name. The budget that ran out and its value. | 4 |
| `error` | The loop itself cannot be trusted to go on: the config is invalid, the agent's own output folder is not writable under the policy, or **every** board failed so that nothing was observed. | `ESCALATE: Omkar must look`, with the reason. No "0 new jobs" line is printed. | 5 |

Only `finished` exits with 0. A scheduler or shell `&&` will therefore never treat a partial run as a success.

## 2. Budgets

Per run, read from `config/budgets.json`:

| Budget | Value | Why this value |
|---|---:|---|
| `max_boards` | **8** | The watch list has 6 boards. This leaves room for 2 more and stops a watch list that has grown by mistake. |
| `max_requests` | **12** | 6 boards plus up to 2 retries for 3 of them. One request is one HTTP attempt, retries included. |
| `max_seconds` | **90** | Wall clock for the whole run. On 2026-11-09, each board took 0.1–1.3 s. |
| `max_retries_per_board` | **2** | See the error policy. |
| `request_timeout_seconds` | **20** | Per attempt. It is capped further by the time left in `max_seconds`. |
| `max_response_bytes` | **10 000 000** | The largest board in this watch list was about 0.8 MB on 2026-11-09. |

**The order of the check is fixed.** A budget is checked **before** each request, never after. The 13th request is never sent, so a 12-request budget cannot be overrun by one.

**Who may change a budget:** only Omkar, and only by a new dated entry in the change log below with `config/budgets.json` edited to match. The agent cannot change its own budgets: `config/` is outside its write area, and every write there needs approval (§5).

## 3. Repeat rule

**"The same action"** means the same method (always `GET`) to the same **normalized URL**. The ATS name and the board slug are lower-cased and the slug is URL-encoded, so `Klaviyo` and `klaviyo` on Greenhouse are the same action.

| Situation | What the loop does |
|---|---|
| The watch list names the same board twice | The second entry is **not fetched**. It is recorded as `repeat_skipped`, and it spends no request. The run cannot be `finished`, because the watch list itself is wrong. |
| A board failed **transiently** (timeout, connection error, 429, 5xx) | It is retried. This is the only allowed repeat, at most `max_retries_per_board` (2) times, and every retry counts against `max_requests`. |
| A board failed **permanently** (404/410, bad schema, refused by the policy) | It is **never repeated** in this run. The same request would get the same answer. |
| An action the policy **refused** | Never re-attempted, and no other route to the same host is tried. |

Across runs, nothing counts as a repeat. Each run is a new observation, and that is how the watch finds new postings.

## 4. Error policy

| Failure on a board | Class | Retry? | Why | Board status | What the trace records |
|---|---|---|---|---|---|
| HTTP 404 / 410 (bad board name) | permanent | **No** | The name is wrong; asking again returns the same 404 and burns budget. | `error` (`not_found`) | status code, body bytes saved raw, `postings: null` |
| Timeout, connection reset, DNS failure | transient | **Yes, ≤ 2**, after waits of 1 s then 2 s (never past the deadline) | A GET to a public read-only endpoint is idempotent, so retrying it changes nothing on the server, and these failures often clear in seconds. | `error` (`timeout` / `network`) if all 3 attempts fail | each attempt separately |
| HTTP 429 / 5xx | transient | **Yes, ≤ 2**, same waits | Same reasoning: the server said "not now", not "never". | `error` (`http_5xx` / `rate_limited`) | each attempt |
| HTTP 200, body not JSON or no posting list | permanent | No | The same request returns the same body. | `error` (`bad_response`) | raw body saved |
| HTTP 200, **valid but zero postings** | suspicious | No | An empty board is evidence of nothing. It may be a moved board, a wrong slug, or a real lull, and the agent cannot tell which. | `empty_unverified` | `postings: 0`, flagged; **never** turned into "no new jobs" |
| Redirect, or a host off the allow-list | refused | No | Policy (§5). | `refused` | the policy decision |
| Response larger than `max_response_bytes` | permanent | No | The response is not what this board should send. | `error` (`too_large`) | size |

**Escalation to Omkar:** the run exits `error` with `ESCALATE` if **every** board failed, or if the agent's own write is denied. Any `incomplete` run lists its failed boards at the top of `report.md`. **The agent never invents a value.** A failed board has `postings: null` and `new: null`, never `0`.

## 5. Permission policy (enforced in `agent/policy.py`, not in a prompt)

Every network request and every file write goes through `policy.check_request()` or `policy.check_write()`. Each returns `ALLOW`, `DENY` or `ASK`. Every decision is written to the trace.

**Network**
- Allowed hosts, exact match only: `boards-api.greenhouse.io`, `api.ashbyhq.com`, `api.lever.co`.
- `https` only, on port 443 only. No user/password in the URL.
- Method `GET` only. Any other method (`POST`, `PUT`, `DELETE`, and so on) is `DENY`. Applying to a job is a POST.
- No `Authorization` or `Cookie` header, ever. The agent has no credentials and never logs in.
- Redirects are refused, not followed. A 3xx is never allowed to carry a request off the allow-list.

**Files**
- **Read:** any file inside this assignment folder (configs, fixtures, persona). Nothing outside it.
- **Write:** only inside the run output folder `runs/`, checked after resolving the real path (`os.path.realpath`) with a path-component comparison (`os.path.commonpath`), never a string prefix. So `runs-evil/` beside `runs/` is outside. A `..` that climbs out is outside. A symlink inside `runs/` that points outside is outside.
- **Write that needs approval (`ASK`):** (a) overwriting a file that already exists in `runs/`, except the state file, since raw responses are evidence and are append-only; (b) any write to `config/`, because budgets and the watch list change only by a written decision. With no approver (the normal, non-interactive run), `ASK` is treated as **not granted** and the write does not happen.
- **Write elsewhere:** `DENY`.

**Never, under any input:** apply, email, message, or log in. These four are named actions in the policy that always return `DENY`, and the program has no code that sends mail, posts a form, or stores a credential.

## 6. Wrong versions the tests must catch

Each one is a plausible implementation that looks fine on a happy-path run. Each has a mutant in `tests/mutants/` that `tests/run_mutants.py` applies, and the suite must **kill** it.

| # | Wrong version | Why it is plausible | Caught by |
|---|---|---|---|
| W1 | An **empty board is reported as "0 new jobs"** and the run exits `finished` | 200 OK with `jobs: []` parses cleanly | `test_empty_board_is_not_finished` (the review-packet test) |
| W2 | A **failed board reports `0` postings** instead of `null` | `len(jobs or [])` is a natural line to write | `test_failed_board_has_null_not_zero` |
| W3 | The run says **`finished` although a board failed** | "the loop ended" is mistaken for "the loop succeeded" | `test_404_board_makes_run_incomplete` |
| W4 | The path check uses **`startswith`** | `runs-evil/x` starts with `runs` | boundary case B5 |
| W5 | The path check **skips `realpath`** | a symlink inside `runs/` looks inside | boundary case B6 |
| W6 | The host check uses **substring or `endswith`** | `boards-api.greenhouse.io.evil.example` contains the allowed host | boundary cases B2, B3 |
| W7 | A **404 is retried** | "retry on any error" is common advice | `test_404_is_not_retried` |
| W8 | The budget is checked **after** the request | off-by-one: 13 requests on a budget of 12 | `test_request_budget_never_exceeded` |
| W9 | A **duplicate board is fetched twice** | a plain `for board in watchlist` loop | `test_duplicate_board_is_repeat_skipped` |
| W10 | **Retries are unbounded** while the deadline is ignored | `while not ok:` | `test_transient_failure_retries_at_most_twice` |

---

## Omkar's decisions

*(Filled in by Omkar on 2026-11-10.)*

| Section | Confirm / change | Omkar's words and date |
|---|---|---|
| 1 Exits | confirm | Code 0 means that everything went right. (2026-11-10) |
| 2 Budgets | confirm | Budgets of eight boards, 12 requests, and 90 seconds are sufficient to complete the task and prevent runs from going too far. (2026-11-10) |
| 3 Repeat rule | confirm | Two entries using the same ATS and the same slug count as one board regardless of different capitalization. (2026-11-10) |
| 4 Error policy | confirm | There should not be any attempts to retry 404. Timeout, 429, or 5xx status codes may be retried up to two times if there is enough time till the deadline. (2026-11-10) |
| 5 Permission policy | confirm | The program is allowed to send GET request to three specified hosts and write only within runs/ directory. It is never allowed to apply for jobs, send e-mails, or log in. (2026-11-10) |
| 6 Wrong versions | confirm | Confirm the current list. I would include the case of almost empty board later. (2026-11-10) |

## Change log

- **2026-11-09** — v1 written by Claude Code from the assignment text, before any JS2 code. Not yet confirmed by Omkar.
- **2026-11-09 08:2x UTC, errata (Claude Code, after an independent review):** in §6 the "Caught by" cells for W4, W5 and W6 cite the wrong boundary cases. The tests that actually kill them are **W4 → B15** (`test_B15_prefix_trick_sibling`), **W5 → B16/B16b** (`test_B16_symlink_escape`, `test_B16b_…`), and **W6 → B3** (`test_B03_suffix_trick_host`), per `tests/run_mutants.py` output. The table above is left as first written; the frozen copy is `evidence/GATE-v1-2026-11-09T0801Z.md`. No rule changed.
- **2026-11-09 08:3x UTC, errata 2 (Claude Code, after a second independent review):**
  - §2 "each board took 0.1–1.3 s": those timings were printed by `curl -w %{time_total}` at ~07:55 in the session but **not saved**. The saved probes (`evidence/probes/PROBES.log`) have no timings. Later saved runs show 0.13–1.3 s per board in `elapsed_s`.
  - §2 "largest board … about 0.8 MB" is **wrong**: Klaviyo with `content=true` is 2,846,399 bytes and HubSpot is 2,071,258. Both are still under the 10,000,000-byte cap, so no value changes.
  - §5 "every decision is written to the trace": until 08:29 only **write** decisions were traced. Since then, each observation carries its request decision and every state read is traced (`test_trace_records_request_and_read_decisions_with_relative_paths`).
  - §6 W8 is worded "checked after the request". Its mutant is the off-by-one that has the same effect (`>=` → `>`, one request too many).
  - §6 W10 names both an unbounded retry count and an ignored deadline. Mutant W10 covers the count; **W10b** (added 08:2x) covers the deadline. W10b first **survived**, which showed `test_retry_never_waits_past_deadline` was too weak. The test was strengthened (it now also checks that the loop never sleeps past the deadline), and W10b is killed.
- **2026-11-10** — Omkar confirmed all six sections as written. No value changed; `config/budgets.json` is unchanged.
- **2026-11-10T10:37Z, Omkar's rule: the drop rule (decided by Omkar; Claude Code asked the questions and offered options, Omkar chose)**
  - **Suspicious drop:** a board that answers `ok` with **more than 50% fewer postings** than its last recorded run is flagged `suspicious_drop`. Why 50%: losing over half the jobs at once usually means the board moved or broke, not normal hiring.
  - **Small boards:** the rule applies only when the last run had **at least 10** postings. Small boards swing a lot, so 4 → 1 is not flagged.
  - **No baseline:** the first time a board is watched there is nothing to compare with, so the agent **warns `no_baseline`**.
  - **What the agent does:** the run still counts as `finished` (exit 0) when every board answered, but each warning is printed in `report.md`, stored in `report.json` and written to the trace. Omkar chose a warning over `incomplete` because the drop could be real hiring.
  - Implemented after this entry, test first; see REVIEW-PACKET.md "Second review".

