# The agent trace of a real run, and the finished wrong answer

*Written by Claude Code on 2026-11-09 from the saved files. Line numbers refer to `runs/20261110T002501Z/trace.jsonl`.*

## Live run 1: 2026-11-09 19:25 EST, six boards on three systems

Command: `python3 -m jsagent run`. The terminal output is in `evidence/run1-terminal-2026-11-09.txt` and the summary in `runs/20261110T002501Z/summary.md`.

| Trace lines | Board | What happened | What GATE.md asked |
|---|---|---|---|
| 1 | — | `start`: budgets 6 boards / 12 requests / 120 s, read from `budgets.json` and checked against GATE.md's dated row | §3 budgets |
| 2–4 | oscar (Greenhouse) | 1 request; 200; 2,126,255 bytes saved to `raw/` before parsing; 199 postings, matching the board's own `meta.total` 199; first run, so a baseline with 0 new | §2 baseline |
| 5–7 | klaviyo (Greenhouse) | the same: 150 postings, `meta.total` 150 | |
| 8–10 | linear (Ashby) | 32 postings | two systems |
| 11–13 | palantir (Lever) | 304 postings | three systems |
| **14–16** | **oscarhealth-doesnotexist (Lever)** | **the deliberate failure.** 1 request; HTTP 404; the 41-byte body saved as evidence; status `failed`, error `not-found`; **no retry**; fetched and new are `null`, not 0 | §5: no retry on a 404, never invent a count |
| **17–19** | **whoop (Lever)** | **a real empty board.** 200 with the 2-byte body `[]`; status `empty`, needs review, new `null`. Not counted as "no new jobs" | §7 wrong version 1 |
| 20 | — | `exit`: **incomplete**, 6 of 12 requests, 3.43 s; needs review: oscarhealth-doesnotexist, whoop | §2: some boards did not check out, so not `finished` |

**The independent check** (`python3 jsagent/check.py runs/20261110T002501Z`) printed `no findings`. It recounts each saved raw file with its own parser, compares the count with Greenhouse's `meta.total`, compares it with the previous state, and confirms the exit is not `finished` while a board failed.

## The finished wrong answer: SEEDED, and labeled as such

The full output is in `evidence/finished-wrong-SEEDED-2026-11-09.txt`; the builder is `demo/make_finished_wrong.py`.

- **Input.** Run 1's real saved responses for the four boards that answered, except that Oscar's response is cut to its first 20 jobs, with `meta.total` left at 199 as the board sent it. This copies a real failure mode: a cache or proxy serving a partial body. Run 1's state is copied in, so this is a normal second run.
- **What the agent said.** Exit **`finished`**: 4 of 12 requests, every board `ok`, Oscar "fetched 20, new 0". Nothing in its own report looks wrong.
- **What the independent check said**, reading only the saved files:
  - `oscar: the response lists 20 jobs but its own meta.total says 199`
  - `oscar: 179 of 199 postings disappeared since the previous run (more than half in one run is not believable without a second look)`

  Exit code 1. On real run 1 the same check says `no findings`.
- **What the check would miss.** It works for Greenhouse because Greenhouse reports `meta.total`. Ashby and Lever report no total, so a partial Ashby or Lever response that kept more than half the postings would pass the check.
- **A slip on the way.** The first attempt at this demo crashed inside the check: its command line assumed every run sits directly in `runs/`. That crash was not counted as a catch. The check's folder lookup was fixed and only the check was re-run (both recorded in the evidence file).
