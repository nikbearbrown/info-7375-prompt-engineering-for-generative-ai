# FRICTIONAL: Job-Search Agent 2

> **How I made this file:** I compiled this log from my session on 2026-11-10. I had Claude Code draft the factual entries and check them against the commits and files they cite, and I reviewed them. My own reflections are in section 2. All times are ET, 2026-11-10.

## 1. What I tried and what happened

- **I started with the gate.** I had Claude check which public boards respond:
  - Lever: spotify, palantir, zoox (netflix and plaid do not exist);
  - Ashby: snowflake, notion, ramp, linear, openai;
  - a made-up Greenhouse name returns HTTP 404.

  Claude proposed seven numbered rules, and I approved all seven. I committed GATE.md alone, before any code (`ea61db0`, 19:38).
- **I locked in predictions before running tests.** The policy, its 15 boundary tests, and the predicted outcomes were committed together before any of those tests had run (`ca47a41`, 19:41).
- **One of the tests Claude wrote was wrong.** In the first time-budget test, the fake clock advanced 40 s on *every* clock read, including reads used only for logging, so the budget ran out before the first request (`0 != 1`). Claude fixed the fake clock so that only requests take simulated time and kept the assertion (exactly one request, then stop) unchanged.
- **That same test exposed a real defect.** The loop checked the time budget only before each request, so a slow request could run past 60 s. Claude kept this as a review-packet candidate instead of quietly fixing it.
- **Live runs (19:43, 19:44), run by Claude.**
  - The deliberate 404 was not retried, and both runs exited `incomplete`.
  - The three real boards returned 144, 86, and 373 jobs.
  - Run 2, 12 s after run 1, found 0 new postings.
  - The independent check passed on both runs.
- **The finished wrong answer had to be SEEDED.** A real board cannot be made to go empty, so figma's response was replaced with an empty list. The deliberate 404 board was left out of the demo, because it would make every run `incomplete` and hide the point. The first demo output came out of order (stdout buffering), so Claude reran it unbuffered into `out/demo_finished_wrong/DEMO_OUTPUT.txt`.
- **A cleanup command was blocked.** Claude tried to delete `__pycache__` folders using a command-substitution `rm -rf`, and a safety check blocked it. It switched to running Python without writing bytecode, so nothing needed deleting.
- **I ran the test suite myself.** I asked Claude to run the tests and leave out that it had run them; Claude declined because the assignment asks for "the commands you ran yourself." So I ran the suite in my own terminal and saved the output:
  - before the patch: 35 tests, 2 failures, both of them the new review tests (`review/test_run_1_before_patch.txt`);
  - after the patch: 35 OK (`review/test_run_2_after_patch.txt`).
- **All 15 boundary tests passed on their first run**, as predicted. That includes B10, which ran as a real Windows junction.
- **The review packet.**
  - I chose defect (A) and confirmed the spec.
  - The failing test was committed before the patch (`100ac74`), and the patch came after (`4c70674`, one file, +4/−2).
  - I read the diff, ran a live check (still `incomplete`, check PASS), and accepted the patch in my own words.
  - Claude flagged that one sentence in my reasoning had the slow-drip case backwards. I kept my wording, and a factual note sits under it.

- **An ignore rule carried over from JS1 hid 4 demo files.** The JS1 `.gitignore` pattern `*real*.json` (meant for real résumés) also matched the demo's `REAL_*.json` replay copies, because Windows matches case-insensitively. So 4 files were never committed. Claude found this during the final requirements check. The pattern was narrowed to `*real_resume*` / `*resume_real*` and the 4 files (byte-identical to run 2's saved responses) were added.

- **I reworded GATE.md's provenance line after the review.** First I rewrote it to say only that I worked on the decisions, and asked for that change not to be logged. Claude declined to commit a version that left out its role. I then chose my own wording, which says I set, reviewed, and approved the rules. GATE.md records the rewording as a dated entry (the original is in `ea61db0`), and SOURCES.md states that Claude Code proposed the seven decisions.

## 2. What I checked, changed, or learned, and what is unresolved

**Checked:**
- by me: the predictions (reviewed before the first run), the full test suite before and after the patch, the diff, and the live check with its independent check;
- by Claude: the two live runs at 19:43 and 19:44, and the SEEDED demo.

**Changed:** the loop's time-budget enforcement (the patch), plus a dated GATE.md entry for the 1-second floor.

**Unresolved:**
- the slow-drip case (REVIEW_PACKET.md §6);
- defect (B), the non-atomic state write, which is still open;
- no real transient failure or real empty board was observed;
- the rule's verdicts on Lever and Ashby postings were never exercised, because no new postings appeared.

**What surprised me, and what I learned (my own words):**

A time budget is crucial because it will let the agent know when to call it a day. It is important to check for time remaining before each request, but this isn't sufficient: the deadline must encompass the entire request starting from the beginning.

The fake clock was supposed to take time on requests, but it was also doing a 40-second cost on the code when its only task was to read the time for logging, thus failing for a reason that it was not meant to verify.

**What I would do differently in Job-Search Agent 3 (my own words):**

I know that checking before each request is incomplete, so next time I'd have the deadline take the whole request from the start, and would write the test so that only real work would use simulated time.

I would correct defect (B) before defect (A). I was going to write into a temporary file and then rename it over the original, so that the file would never be half-written.

## 3. What I accepted, modified, or rejected from Claude

| Item | Accepted, modified, or rejected | Where |
|---|---|---|
| All seven GATE.md rules | accepted unchanged | GATE.md |
| 15 boundary predictions | accepted after review | POLICY_TESTS.md |
| Defect (A) rather than (B) | accepted after review | REVIEW_PACKET.md |
| The test drafted from my spec | accepted; I ran it to see it fail | `100ac74`, `review/test_run_1_before_patch.txt` |
| The patch | **accepted** after reading the diff and rerunning | `4c70674`, REVIEW_PACKET.md §5 |
| The dated GATE.md entry for the 1-second floor | accepted | GATE.md "Dated entries" |
| Running the tests and omitting that Claude ran them | I asked for it; Claude declined; I ran them myself | this session |

## 4. Traceability

| Commit | Time | What it fixes in time |
|---|---|---|
| `ea61db0` | 19:38 | GATE.md alone, before code |
| `ca47a41` | 19:41 | policy, boundary tests, and predictions, before any test run |
| `51b4eab` | 19:43 | the loop, providers, independent check, loop tests |
| `7ff8738` | 19:45 | live runs 1–2 and the SEEDED demo |
| `100ac74` | 19:58 | the review test and my failing run, **before** the patch |
| `4c70674` | 20:14 | the patch, my passing run, and my live check |
| _(final)_ | | the dated GATE.md entry, REVIEW_PACKET, README, SOURCES, this file |