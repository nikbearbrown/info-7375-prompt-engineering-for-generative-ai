# Agent trace: one real run, the deliberate failure, and a finished wrong answer
These are all real runs on my Mac, 2026-11-10 ~9:31 pm, against the live boards. Every request is recorded in each run's `trace.json` under `observations`, with its time, URL, attempt, HTTP status, bytes and outcome. The raw response bodies and status codes are saved in `raw/`.

## 1. A real run, with the deliberate failure: `reports/job-watch/runs/20261110T213125-live/`
Console: `logs/10_live_run1.txt`.
```
20261110T213125-live: exit=incomplete (1 board(s) failed); boards checked 3, new jobs 0, requests 4/15, seconds 2.272/60.0
  greenhouse:klaviyo                 ok           jobs=145 new=0
  greenhouse:datadog                 ok           jobs=394 new=0
  lever:palantir                     ok           jobs=304 new=0
  greenhouse:no-such-board-7375      failed       jobs=None new=None HTTP 404: board name not found
```
- **Three boards, two systems:** Greenhouse (klaviyo, datadog) and Lever (palantir).
- **The deliberate failure:** `no-such-board-7375` got HTTP 404. Following GATE 4, it was reported and **not** retried, the loop moved on, and **no value was invented**: `jobs=None`, `new=None`, not 0.
- **The exit:** `incomplete`, because some boards worked and one failed (GATE 1). It's not `finished`.
- **The budget:** 4 of 15 requests, 2.3 of 60 seconds, 4 of 5 boards.
- **A baseline:** this was the first run, so it reports none as new (`new=0`) and saves the ids in `reports/job-watch/state/seen-20261110T213125-live.json`.

**Independent check:** `logs/11_check_run1.txt`, `PASS`. It recounted each ok board from the saved raw response **and** asked again with curl.

**Run 2**, 7 seconds later (`20261110T213132-live`, `logs/12`, `logs/13`): the same 4 boards and 0 new postings. That's correct, since nothing changed between the runs. The check said `PASS`.

## 2. A finished wrong answer, and the independent check that catches it
Both demos are **deliberately wrong versions** (`wrong_versions/`). Each one changes one piece of the real loop, and is labelled `WRONG-DEMO` in its run folder. Neither writes the real state.

**Demo A: a failed board reported as "0 jobs"** (my GATE wrong version 1). Run `20261110T213138-WRONG-DEMO-empty_as_zero`, `logs/14`:
```
exit=finished (every board was checked); boards checked 4, new jobs 0
  greenhouse:no-such-board-7375      ok           jobs=0 new=0
```
The run ends cleanly, says "finished" and "no new jobs", and it's wrong: that board doesn't exist.
**Caught by** `python3 watch.py check …` (`logs/15`):
```
INDEPENDENT CHECK: FAIL - 1 problem(s)
  - greenhouse:no-such-board-7375: reported ok with 0 jobs, but the raw response was HTTP 404
```

**Demo B: a board with jobs reported as empty, "no new jobs"** (the assignment's own example). A Lever parser bug. Run `20261110T213143-WRONG-DEMO-lever_reads_nothing` on `boards-demo.json`, `logs/16`:
```
exit=finished (every board was checked); boards checked 2, new jobs 0
  lever:palantir                     ok           jobs=0 new=0
```
**Caught by** `python3 watch.py check … --live` (`logs/17`):
```
INDEPENDENT CHECK: FAIL - 2 problem(s)
  - lever:palantir: reported 0 jobs, but a live recount now finds 304 (the board may also have changed since the run)
  - lever:palantir: reported 0 jobs, but the raw response contains 304
```

**Why the check is independent:**
- **It ignores the agent's verdicts.** It recounts the jobs from the saved raw bytes with its **own** parser (`watcher/check.py`).
- **With `--live`, it asks the board again through a separate path:** `curl`, not the agent's fetch code.

The first version of the check only re-read the agent's own files. Claude Code pointed out that a self-consistent wrong answer would pass that, so the live recount was added, with a test written first (`tests/test_review_fixes.py`).
