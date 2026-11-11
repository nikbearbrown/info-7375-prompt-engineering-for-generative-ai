# Agent trace: one real run, with the deliberate failure

**Run:** `runs/2026-11-09T08-29-32Z-final/`. A **live** run on 2026-11-09 at 08:29:32 UTC, using the **final code**. Claude Code ran `python3 -m agent.loop --label final`.

This run diffs against the previous run of the same watch list (`final-code`, 08:23:37 UTC, about 6 minutes earlier). That is because each board's state is rewritten after every run. The watch list's baseline was `main-prepatch` at 08:07:29.

| File | What it is |
|---|---|
| `trace.jsonl` | The full trace: 37 lines, all paths relative to the assignment folder. `run_start`; 6 `observation` (each carries its **request** policy decision); 4 `policy` **read** decisions (state files); 6 `board_done`; 19 `policy` **write** decisions (all ALLOW); `run_end` |
| `raw/*.json` | The six raw HTTP bodies exactly as received. Each one's sha256 is in its observation line |
| `report.json`, `report.md` | The agent's own report |
| `console.txt` | What the terminal printed |
| `independent-check.md` | The independent check of this run (see WRONG-ANSWER.md) |

## The trace, without the 19 write-decision lines

`t` is seconds since the run started. Sha256 values are shortened here; `trace.jsonl` has them in full.

```text
t=0.001  run_start      watchlist = klaviyo(gh), hubspotjobs(gh), linear(ashby), spotify(lever), webflow(gh), klaviyoo(gh)
t=0.488  observation    greenhouse:klaviyo     a1  HTTP 200  2,846,399 B  ok         152 postings  request ALLOW  sha a20e24a2a429…
t=0.489  policy read    ALLOW runs/state/greenhouse-klaviyo.state.json
t=0.491  board_done     greenhouse:klaviyo     ok  postings 152  new 0
t=0.869  observation    greenhouse:hubspotjobs a1  HTTP 200  2,071,258 B  ok         122 postings  request ALLOW
t=0.872  board_done     greenhouse:hubspotjobs ok  postings 122  new 0
t=1.009  observation    ashby:linear           a1  HTTP 200    452,742 B  ok          32 postings  request ALLOW
t=1.011  board_done     ashby:linear           ok  postings 32   new 0
t=2.759  observation    lever:spotify          a1  HTTP 200    814,089 B  ok          85 postings  request ALLOW
t=2.763  board_done     lever:spotify          ok  postings 85   new 0
t=2.991  observation    greenhouse:webflow     a1  HTTP 200         30 B  EMPTY        0 postings  request ALLOW
t=2.992  board_done     greenhouse:webflow     empty_unverified  postings 0  new null
t=3.124  observation    greenhouse:klaviyoo    a1  HTTP 404         38 B  permanent (not_found)    request ALLOW
t=3.125  board_done     greenhouse:klaviyoo    error  postings null  new null
t=3.127  run_end        exit = incomplete (code 3): "no answer from: greenhouse:webflow (empty_unverified), greenhouse:klaviyoo (error)"
```

The other three state reads (hubspotjobs, linear, spotify) follow the same pattern as Klaviyo's. Webflow and klaviyoo have no state read, because a board that is empty or failed never reaches the diff.

## How to read it against GATE.md

| GATE rule | What the trace shows |
|---|---|
| **3 boards, ≥ 2 ATSs** | 6 boards across **3** systems: Greenhouse (4), Ashby (1), Lever (1) |
| **Budget checked before each request** | 6 requests against a cap of 12; 3.1 s of the 90 s; 6 of 8 boards |
| **Deliberate failure: bad board name `klaviyoo`** | HTTP 404 → `permanent` → **one attempt, no retry** (GATE §4: retrying a 404 gets the same 404). `postings: null` and `new: null`, so **no value was invented**. The 38-byte 404 body is saved as `raw/greenhouse-klaviyoo-a1.json` |
| **Empty board** | Webflow's Greenhouse board returned `{"jobs":[],...}` with HTTP 200. Outcome `empty` → `empty_unverified`, `new: null`, state not read or written. (Before the reviewed patch, this line said `ok`; see REVIEW-PACKET.md) |
| **Permission policy, every decision traced** | 6 request decisions (inside the observations), 4 read decisions, 19 write decisions. All ALLOW, as expected for this watch list. The DENY cases are in the boundary tests (POLICY.md) |
| **Exit** | `incomplete`, code 3, with both failed boards named. **Not** `finished`: the loop stopped, but it did not succeed on every board |
| **Every observation recorded** | 6 requests → 6 `observation` lines, each with a raw file and a sha256. The independent check recomputed all six and found them intact (C1) |

**No new postings.** All four boards that answered showed **0 new** compared with the run 6 minutes earlier. That means only that no id appeared in those 6 minutes. Every JS2 run was made on 2026-11-09 between 08:07 and 08:30 UTC.

**Earlier traces.** Runs before 08:29 (`main-prepatch`, `main-postpatch`, `main-final` at 08:10:05, `final-code` at 08:23:37) were made on earlier versions of the code:
- Their traces do not contain request or read decisions.
- Their write decisions use absolute local paths (the macOS user folder; no secrets).

They are kept unchanged as evidence. `main-final` (08:10:05) is the reviewed v2 code. Its trace (33 lines) is cited in REVIEW-PACKET.md and WRONG-ANSWER.md.

## The other exits, also from real runs

| Exit | Run | Why it ended that way |
|---|---|---|
| `finished` (0) | `runs/wrong-answer-demo/2026-11-09T08-07-44Z-wrong-answer-prepatch-run2/` | Pre-patch code. **This is the finished wrong answer** (WRONG-ANSWER.md) |
| `incomplete` (3) | this run; `main-final`; `main-postpatch`; `wrong-answer-postpatch` | A 404 board and/or an empty board |
| `budget_exhausted` (4) | `runs/budget-demo/2026-11-09T08-10-09Z-budget-demo/` | Labelled DEMO budget `config/budgets-demo-tight.json` (max_requests 3). 3 requests were sent, a 4th never was, and 3 boards are listed `not_attempted` |
| `error` (5) | `runs/error-demo/2026-11-09T08-10-20Z-error-demo/` | Labelled DEMO watch list with only the typo board. Every board failed → `ESCALATE: … Omkar must look.` |

**A failed attempt is also kept:** `runs/timeout-demo/…-timeout-demo/`. Claude Code tried to show a real timeout and retry on the network by cutting the per-request timeout to 0.1 s. **It did not time out:** the request finished in 0.302 s (the whole run in 0.355 s), because Python's socket timeout applies to each read, not to the whole request. The retry path (≤ 2 retries, waits of 1 s then 2 s, never past the deadline) is therefore shown **only in the offline tests** (`test_transient_failure_retries_at_most_twice`, `test_transient_then_success`, `test_retry_never_waits_past_deadline`), not against a live server. This is listed under *Not checked* in the sign-off.
