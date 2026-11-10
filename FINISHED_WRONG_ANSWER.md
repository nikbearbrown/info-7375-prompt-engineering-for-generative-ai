# A finished wrong answer, and the independent check that catches it

The brief's example is an empty board reported as "no new jobs." JS2 shows it **live** (run B) and **seeded** (run C). In both runs the
loop ends cleanly with `finished (0)`, and in both runs its answer is wrong.

## Run B: live, 2026-11-10 17:15:27 ET

From the loop's own output, [out/runs/2026-11-10T171527_live/console.txt](out/runs/2026-11-10T171527_live/console.txt):

```
  lever:kraken                         ok              0 postings  compared with state; new: 0 (0 judged, 0 not judged, 0 other)
...
loop exit: finished (0)
```

Lever answered `200` with `[]`, a valid response in Lever's shape (raw: `out/runs/2026-11-10T171527_live/raw/lever_kraken_list.json`,
2 bytes). Nothing inside the loop can tell "no openings" from "this company no longer uses this board," so it reports finished.

**The independent check** is [scripts/verify_run.py](scripts/verify_run.py). It is separate code that imports nothing from `jsagent/`,
recounts from the raw bytes, and treats the report only as the thing being checked
([verifier.txt](out/runs/2026-11-10T171527_live/verifier.txt)):

```
[FAIL] lever:kraken: 0 postings (empty, needs review)
verifier: FAIL (lever:kraken: 0 postings (empty, needs review))
```

**Proof that the answer is wrong, not just suspicious.** 26 s later I ran my own cross-check, outside the agent, against Kraken's Ashby
board. Ashby is not on the agent's allow-list. See [evidence/crosscheck/crosscheck_console.txt](evidence/crosscheck/crosscheck_console.txt):

```
2026-11-10T17:15:53-05:00  GET https://api.ashbyhq.com/posting-api/job-board/kraken.com  ->  HTTP 200, 92 postings (32 US or remote)
  - Senior Analytics Engineer - Finance | United States
```

So "0 new jobs at Kraken" was wrong: Kraken had 92 open postings, on a different system. The raw response is saved with sha256
`985c7087a03865ec392fdad0a8b0be5604712445129c5878b715aed1441100a8`.

## Run C: SEEDED, offline, 2026-11-10 17:16:05 ET

This is **constructed, not live**. Samsara's list was replaced by
[tests/fixtures/seeded/empty-samsara.json](tests/fixtures/seeded/empty-samsara.json) (`{"jobs": [], "meta": {"total": 0}}`), using its
own output root `evidence/seeded/empty-samsara/`, so the real state was never touched. It exists so a TA can reproduce the failure
offline, without depending on Kraken staying empty.

```
Run 2026-11-10T171605_seeded  [SEEDED (constructed: Samsara's list replaced by ...; no network)]
  greenhouse:samsara                   ok              0 postings  compared with baseline 2026-10-31; new: 0 (...)
loop exit: finished (0)
[FAIL] greenhouse:samsara: 0 postings (empty, needs review)
[FAIL] greenhouse:samsara: 0 now vs 323 in baseline 2026-10-31 (drop check: not more than half)
verifier: FAIL (...)
```

## Why the check is outside the loop

A plausibility check inside the loop would still be the agent grading itself (GATE.md, section 4). The verifier reads the raw files,
the trace, the board file, the baseline's raw response and earlier runs' raw files. It does not reuse the loop's adapters or its exit
function. `test_W15_verifier_ignores_report_counts` shows it catches a report that lies about a count.
`test_W19_empty_board_fails_verification` shows it fails an empty board even with no history. `scripts/sabotage_check.py` shows both
tests go red when those checks are removed.

## What the check does not prove

- The verifier flags *every* empty board, so a company that truly has no openings would also FAIL. GATE.md accepts that false alarm.
- It cannot find where a company moved. The Ashby cross-check was my manual step.
- It trusts earlier runs' reports for which ids were left unjudged. It recounts everything else from raw bytes.
