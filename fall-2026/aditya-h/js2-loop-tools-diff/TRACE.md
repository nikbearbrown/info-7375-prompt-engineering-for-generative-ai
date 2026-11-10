# Agent traces of real runs, and the finished-wrong answer (Chapter 4)

Every run writes `runs/<run-id>/trace.jsonl`, one line per step: `start`, `read`, `plan`, `request`, `write`, `observation`, `exit`, and `retry-wait` / `escalate` when they occur. Raw responses are in `runs/<run-id>/raw/`. All three runs below were live runs against the real public APIs.

| run | when (EST) | boards | exit | what it shows |
|---|---|---|---|---|
| `20261109T204551Z-2ac7e2` | 2026-11-09 15:45 | `boards.json` (7) | **incomplete** | **baseline**, plus the **deliberate failure** handled |
| `20261109T204623Z-906e94` | 2026-11-09 15:46 | `boards.finished-wrong.json` (6) | **finished** | the **finished-wrong answer**, caught by `check_run.py` |
| `20261110T184710Z-df53fd` | 2026-11-10 13:47 | `boards.json` (7) | **incomplete** | **second calendar day**: 57 new postings, 1 relevant; the deliberate failure handled again |

## Annotated trace — Nov 10 second-day run (`20261110T184710Z-df53fd`)

The output was condensed from `trace.jsonl` (paths and URLs dropped), plus `report.md`.

| t (s) | step | board | what happened |
|---|---|---|---|
| 0.0 | start | — | budgets `{boards 10, requests 15, seconds 120}`; 7 boards listed |
| 0.0 | read | — | persona read: **allow** (inside the folder); persona guard passed |
| … | plan → request → write → observation | `greenhouse/stripe` | 200, 776 postings, **16 new**, **1 relevant** |
| … | same | `greenhouse/anthropic` | 200, 676 postings, 11 new, 0 relevant |
| … | same | `ashby/openai` | 200, 830 postings, 26 new, 0 relevant |
| … | same | `ashby/notion` | 200, 153 postings, 1 new |
| … | same | `lever/palantir` | 200, 304 postings, 3 new |
| … | request | `greenhouse/stripe-js2-bad` | **HTTP 404, attempt 1, no retry** (4xx is deterministic, per the error policy) |
| … | observation | `greenhouse/stripe-js2-bad` | **status `failed`, reason `HTTP 404`**; fetched/new/relevant = **null**; its state was never written |
| … | observation | `greenhouse/ramp` | 200, 1 posting, 0 new, status `ok` |
| 3.44 | exit | — | **`incomplete`**, used 7/10 boards, 7/15 requests, 3.44/120 s |

**The one relevant new posting:** "Product Operations Manager" (Stripe, gh_jid 8315943). The rule matched the title phrase `product operations` and the US marker `US`, and cited `experience[0].title`, `personal.location`, `title`, `location_name` and `us_office`.

## The deliberate failure — handled without inventing a value

`greenhouse/stripe-js2-bad` failed in all three of my runs that included it.
- **One request each time:** `attempts: 1`. The error policy never retries a 404.
- **No invented counts:** fetched/new/relevant were `null`, never 0. The report shows "—".
- **No state written** for the failed board: there is no `runs/state/greenhouse__stripe-js2-bad.json`.
- **The run did not claim success:** the exit was `incomplete`, and the report says "Not a clean finish".

## The finished-wrong answer and the independent check

**Run `20261109T204623Z-906e94`** watched 6 boards. Each returned HTTP 200 and parsed, so the loop ended **`finished`**, exit code 0, and reported `greenhouse/ramp: ok, fetched 1, new 0`. The loop's own report was clean.

**It was wrong.** Ramp's Greenhouse board is a leftover. Its only posting is "Copy of Chief Legal Officer", first published 2026-10-23. Ramp's real board is on Ashby. An agent trusting the loop would conclude "Ramp has nothing new", forever.

**The independent check** (`python3 check_run.py runs/20261109T204623Z-906e94`, output in `check.md` / `check.json`) caught it:

```text
loop exit: finished -> independent check: wrong
  greenhouse/ramp: finished-wrong — 1 postings (< 3); newest posting 17 days old; the same company on ashby/ramp lists 175 postings
```

**Why the check counts as independent:**
- It doesn't trust the loop's numbers. From the saved raw files it recomputes the posting count, checks that every "new" id exists in the raw response, and re-applies the rule to recompute `relevant`. Tests tamper with each of these to prove it. It **cannot** recompute *which* postings were new, because that needs the state as it was before the run.
- It applies its own suspicion rule: fewer than 3 postings, or the newest older than 14 days.
- It makes its own read-only cross-check request to a second source (`api.ashbyhq.com`, also allow-listed), with a budget of 1 request per suspect board.
- It never writes state. It keeps its own trace (`check-trace.jsonl`) of every read, request and write decision.
- It works from a fresh clone at any path (patch v3; `test_committed_finished_wrong_run_checks_in_another_folder`). On 2026-11-10 14:00 EST, a copy of this folder at a different path re-checked this committed run live and again said **wrong** (Ashby now lists 173 for Ramp).

**What it would miss:** a wrong board that is *large and fresh*, for example a different company's board under a similar slug. It also can't cross-check a board with no second source in `checks.json`; it can only mark it `suspect`.
