# Finished-wrong-answer demonstration — log

Labels: REPLAY = LIVE Figma bytes re-read; SYNTHETIC = constructed empty board.

## 1. FAULTY VERSION: inherited single-board agent/watch.py

```text
$ -m agent.watch --board figma --resume resume/priya-nair.resume.example.json --state evidence/finished_wrong/faulty_watch/state.json --runs-dir evidence/finished_wrong/faulty_watch/runs --label replay-baseline --from-file out/runs/20261110T232115022Z_live/raw/02_greenhouse_figma_a1.json.gz --seeded-note REPLAY of the LIVE Figma response from run 20261110T232115022Z_live
BASELINE: recorded 144 posting ids; 0 reported as new. Report: evidence/finished_wrong/faulty_watch/runs/20261110T232425Z_replay-baseline/report.md
[exit status: 0]
```
```text
$ -m agent.watch --board figma --resume resume/priya-nair.resume.example.json --state evidence/finished_wrong/faulty_watch/state.json --runs-dir evidence/finished_wrong/faulty_watch/runs --label synthetic-empty --from-file evidence/finished_wrong/inputs/empty_SYNTHETIC.json --seeded-note SYNTHETIC empty board
COMPLETE: 0 new posting(s), 0 retried. Report: evidence/finished_wrong/faulty_watch/runs/20261110T232425Z_synthetic-empty/report.md
[exit status: 0]
```
## 2. Independent checker on the faulty runs (predeclared EXPECTATION.json)

```text
$ scripts/check_run.py watch-pair evidence/finished_wrong/faulty_watch/runs/20261110T232425Z_replay-baseline evidence/finished_wrong/faulty_watch/runs/20261110T232425Z_synthetic-empty evidence/finished_wrong/faulty_watch/exit_codes.json evidence/finished_wrong/EXPECTATION.json
# Independent check against predeclared expectation EXPECTATION.json: A board whose previous response contained postings must not end a run with exit 0 (finished / COMPLETE, zero new) when its next response contains none. GATE.md §4: for these selected boards an empty jobs array is suspect-empty, a failure.
      prior response: 144 ids; later response: 0 ids; vanished: 144; later exit code: 0; later report run entry: {'kind': 'watch', 'new': 0, 'completed': 0, 'pending': 0}
FAIL  no finished-wrong answer: an emptied, previously nonempty board must not end with exit 0  — CONTRADICTION: 144 previously observed postings all vanished, yet the run exited 0 and reported 0 new

1 CONTRADICTION(S) FOUND (1 checks)
[exit status: 1]
```
## 3. Same inputs through the JS2 loop (file replay instead of the network)

run_loop(label='replay-baseline') -> exit 0; report evidence/finished_wrong/js2_loop/out/runs/20261110T232425650Z_replay-baseline/report.md

run_loop(label='synthetic-empty') -> exit 3; report evidence/finished_wrong/js2_loop/out/runs/20261110T232425676Z_synthetic-empty/report.md

```text
$ scripts/check_run.py run evidence/finished_wrong/js2_loop/out/runs/20261110T232425676Z_synthetic-empty
# Independent check of 20261110T232425676Z_synthetic-empty (reported status: incomplete, exit 3)
PASS  trace sequence is contiguous from 1  — 7 events
PASS  HTTP attempts within the gate limit (8) and equal to the report  — 1
PASS  model calls within the gate limit (10) and equal to the report
PASS  elapsed time within 180 s  — 0.003 s
PASS  every attempt timeout ≤ 20 s and ≤ 180 − t − 10 at dispatch
PASS  every dispatched URL is an allow-listed board endpoint
PASS  no URL dispatched twice except one linked retry
PASS  every saved raw response matches its recorded sha256 and size  — 1 boards
PASS  greenhouse:figma: failed/unattempted board reports unknown counts as null (not 0)  — suspect-empty: the jobs array is empty for a board previously observed nonempty
PASS  greenhouse:figma: failed board state unchanged
PASS  greenhouse:figma: raw response confirms the failure (HTTP 200)
PASS  status recomputed by precedence matches the report, and the exit code matches the status  — incomplete
PASS  state: every valid judgment is 'completed' and every unjudged one is 'pending'  — 0 completed, 0 pending
PASS  every reported valid JUDGMENT's saved response names its own posting and verdict

NO CONTRADICTION FOUND (14 checks)
[exit status: 0]
```
## Summary
{
 "faulty_watch": {
  "baseline_exit": 0,
  "later_exit": 0,
  "state_changed_by_empty_run": true
 },
 "checker_on_faulty_exit": 1,
 "js2_loop": {
  "baseline_exit": 0,
  "later_exit": 3
 },
 "checker_on_js2_loop_exit": 0
}
