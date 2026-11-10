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

## Live run 2: 2026-11-09 20:17 EST, the same six boards

Command: `python3 -m jsagent run`. Evidence: `evidence/run2-terminal-2026-11-09.txt`, `runs/20261110T011708Z/`.

- **Result.** Exit `incomplete` again: the same 404 handled the same way, WHOOP `empty` again, 6/12 requests, 7.8 s.
- **Not a baseline.** It read run 1's state (sequence 1), so no board was a baseline, and all four working boards reported **0 new**.
- **Recount.** `evidence/run2-recount-2026-11-09.txt` compares run 2's raw files with run 1's directly. All six responses are byte-for-byte identical, with 0 new and 0 gone ids. So "0 new" is true, not a missed change.
- **Independent check:** no findings.
- **What this leaves untested.** Neither live run saw a new posting, so the loop's step of judging new postings with rule v2 has run only in tests, on constructed postings.

## Live run 3: 2026-11-10 15:47 EST, the same six boards, a day later

Command: `python3 -m jsagent run`. Evidence: `evidence/run3-terminal-2026-11-10.txt`, `evidence/run3-recount-2026-11-10.txt`, `runs/20261110T204749Z/`.

- **Result.** Exit `incomplete` again: the same 404, WHOOP `empty` again, 6/12 requests, 3.8 s.
- **Six real new postings, each judged in the loop by rule v2 revision 3**, all Not Relevant:
  - **Oscar 8227025**, Associate Director, Appeals & Grievances (Remote): failed 1–6; remote limited to listed states without Massachusetts; "7+ years of progressive experience…".
  - **Oscar 8224080**, Staff User Experience Researcher (New York): failed 1–6.
  - **Linear**, Field Marketing Manager, Europe: failed 1, 2, 3, 4, 6.
  - **Palantir**, two *Software Engineer, Intern – Connectivity Platform and Product* postings (New York, Denver) and *Software Engineer, Internship – Data Connectors* (New York): failed only **2 and 3**. Palantir's Lever department is `Dev`, which is not on the contract's list, and neither city is Boston or remote. These are the closest calls in any live run.
- **Recount.** From the raw files, against run 2: the new ids match the agent's list on every board (1 Linear, 2 Oscar, 3 Palantir). 9 Oscar, 2 Klaviyo and 3 Palantir postings closed since run 2. The loop does not report closed postings.
- **Independent check:** no findings.

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
