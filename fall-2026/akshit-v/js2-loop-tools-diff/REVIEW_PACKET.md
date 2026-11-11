# Review packet (Chapter 6): one change I asked Claude Code to make

> Claude Code drafted the structure and the factual parts of this file from the commits and the saved outputs. The spec, the commands I ran, the decision, and my reasoning are mine and are marked as such.

## The change

**Defect (A): the time budget could be overrun.** GATE.md §3 sets a 60-second budget per run, "checked before each request". In v1 (`2711716`), the loop checked only whether 60 s had **already** passed, then gave every request a fixed 20 s timeout. A request started at second 59 could therefore run to about second 79, or longer with a retry.

Claude Code found this while reading v1 against GATE.md. It offered it to me as one of two candidates (the other was a non-atomic state-file write). I chose (A).

**My spec, confirmed by me on 2026-11-10 before the patch:**
> No request may run past the 60-second budget. Each request's timeout must be at most the time left in the budget. If less than 1 second remains, the loop must stop with `budget_exhausted` *before* sending the request.

## 1. The defect reproduced, with the test written before the patch

- **Test:** `tests/test_review_time_budget.py`, drafted by Claude Code from my spec. It uses a fake transport that records the timeout each request was given, so no network is involved.
  - `test_timeout_never_exceeds_time_left`: after one 50 s request, 10 s remain, so the second request's timeout must be ≤ 10 s.
  - `test_stops_before_sending_when_under_one_second_left`: after one 59.5 s request, the second must not be sent, and the run must exit `budget_exhausted`.
- **Committed before the patch:** `6246eab` (19:58), with my run's output. The patch is the later commit `9783db3` (20:14).
- **Reproduced by me**, in my own terminal: `review/test_run_1_before_patch.txt` shows 35 tests, **2 failures**, both of them these tests:
  - `AssertionError: 20 not less than or equal to 10 : second request was given 20 s with only 10 s left`
  - `AssertionError: 2 != 1 : a request was sent with under 1 s of budget left`

## 2. The diff, read as a change in behavior

```diff
 REQUEST_TIMEOUT = 20
 RETRY_WAIT = 2
+MIN_REQUEST_SECONDS = 1   # below this much time left, a request is not sent
...
-                if clock() - t0 >= budget.max_seconds:
+                time_left = budget.max_seconds - (clock() - t0)
+                if time_left < MIN_REQUEST_SECONDS:
                     stop_for_budget(i, f"time budget ({budget.max_seconds}s) reached")
                     break
...
-                r = transport.get(b.url, timeout=REQUEST_TIMEOUT)
+                r = transport.get(b.url, timeout=min(REQUEST_TIMEOUT, time_left))
```

| | Before | After |
|---|---|---|
| When the loop stops for time | only once ≥ 60 s have already passed | as soon as less than 1 s is left |
| A request's timeout | always 20 s | the smaller of 20 s and the time left |
| A request started at second 59 | sent; could end around second 79 or later | not sent; exit `budget_exhausted` |
| A normal live run (about 2 s) | 20 s timeout | still 20 s, so no visible change |

## 3. Did it stay in scope?

Yes. `git show --stat 9783db3` shows one code file (`agent2/loop.py`, +4/−2). The rest of that commit is my saved outputs and the live-check run. Exits, the repeat rule, the error policy, and the permission checks did not change. The new 1-second floor is recorded as a dated entry in GATE.md, because it is a rule about how a budget is enforced.

## 4. Commands I ran myself (2026-11-10)

```
python -B -m unittest discover -s tests -t . -v      # before the patch -> review/test_run_1_before_patch.txt (2 failures)
python -B -m unittest discover -s tests -t . -v      # after the patch  -> review/test_run_2_after_patch.txt (35 OK)
git diff agent2/loop.py                              # read the diff
python -B -m agent2.run --resume data/resume_jack_spencer.json   # live check -> review/live_run_after_patch.txt
python -I -B scripts\check_run.py out\runs\20261111T011106Z.json  # independent check: PASS
```

The live check after the patch: exit `incomplete` (the deliberate 404 board), figma/spotify/snowflake `ok` with 144/86/373 jobs, 0 new, 4/10 requests. The independent check printed `PASS: report agrees with the saved evidence`.

## 5. My decision: accept

My reasoning, in my own words:

> Accept. My two tests both caused the defect prior to patch. A request was given 20 s, 10 s of which were remaining, and a request was sent with 0.5 s remaining (review/test_run_1_before_patch.txt). It is passed by both passes and the other 33 tests passed as well (see review/test_run_2_after_patch.txt), so no other tests were broken. The diff was all within the time-budget check: 1 file changed, 4 lines added, 2 lines deleted. It just affects the distance that a request can be from the 60 s limit and the waiting time. After patch (review/live_run_after_patch.txt) was still incomplete, due to intentional 404 board with the same 3 boards ok. I will accept it, but there is one exception: if the server sends a flow of data very slowly, it can still allow one of the requests to exceed the budget for a single wait, but not for the duration of the connection.

*Factual note (Claude Code):* the last sentence has the direction reversed. Python's `timeout` **does** limit each single wait (connecting, or reading one chunk). It does **not** limit the whole connection's total time. A slow-dripping server can therefore keep one request past the budget over the whole connection.

## 6. One case my test would still miss

**A server that sends data slowly but steadily.** The timeout passed to `urllib` applies to each socket operation, not to the total duration of the request. A response that delivers a few bytes every few seconds never trips any single wait, but it can carry the run well past 60 s. My test cannot see this: its fake transport only records the timeout value and does not simulate socket behavior. Catching it would need a wall-clock deadline enforced around the whole read, and a test against a real slow local server.
