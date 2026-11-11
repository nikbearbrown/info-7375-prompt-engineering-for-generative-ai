# A finished wrong answer, and the check that caught it

## The run that ended cleanly and was wrong

**Setup (deliberate, labelled):** `config/watch-wrong-board.toml` plans one board,
`greenhouse/ramp`. While probing boards on 2026-11-09 (before writing any loop code), Claude
found that Ramp's old Greenhouse board still answers `200 OK` with a valid response holding one
posting, while Ramp's real board is on Ashby. That made a natural wrong board: it is what a
person gets by assuming Ramp still uses Greenhouse.

**Two live runs, 2026-11-09 08:16 UTC, code `e54a26d`** (run by Claude; not simulated):

| Loop | Agent's exit | Board status | Fetched | New | "Needs your attention" |
|---|---|---|---:|---:|---|
| [`2026-11-09T08-16-13Z`](../../data/watch/loops/2026-11-09T08-16-13Z/report.md) | `FINISHED` (exit 0) | `BASELINE` | 1 | 0 | "Nothing: every planned board was checked." |
| [`2026-11-09T08-16-16Z`](../../data/watch/loops/2026-11-09T08-16-16Z/report.md) | `FINISHED` (exit 0) | `SUCCESS_NO_NEW` | 1 | 0 | "Nothing: every planned board was checked." |

The second run is the classic wrong answer: **"no new jobs" from a board that is not Ramp's
board.** Every step the agent took was internally correct: HTTP 200, a valid shape, one valid
ID, the state saved, no new IDs. The raw response (saved byte for byte,
`data/watch/boards/greenhouse-ramp/live/runs/2026-11-09T08-16-16Z/raw/greenhouse-ramp.json`)
holds one posting: ID `8042562003`, title **"Copy of Chief Legal Officer"**, location
**"dublin"**, `updated_at` 2026-10-23, `meta.total` 1.

What is true instead: Ramp's careers page (`ramp.com/careers`, fetched outside the agent on
2026-11-09) mentions `ashbyhq` 338 times and `greenhouse` 0 times, and the same morning's loop
run 1 read **169** postings from `ashby/ramp`.

## The independent check

[`checks/check_watch.py`](../../checks/check_watch.py) is not the agent's report and does not
import the agent: it uses the Python standard library only (a test,
`test_checker_imports_nothing_from_the_agent`, keeps it that way). It reads what a loop run left
behind and recomputes from the raw bytes:

- every planned board appears in the report; trace attempts equal the reported requests and
  stay within the budget;
- per board: the raw file's sha256 equals both the report's and the trace's; the posting count
  recomputed from the raw JSON equals the report's; new IDs recomputed as raw IDs minus
  `state.before.json` equal the report's; a failed board claims no count;
- against [`checks/expectations.toml`](../../checks/expectations.toml), which records what a
  person knows without the agent: the job system the company's careers page links to, and a
  floor its board should not fall below;
- `FINISHED` is allowed only if every board is OK **and** passes these checks.

Its output on the second wrong run
([`evidence/check-2026-11-09T08-16-16Z.txt`](evidence/check-2026-11-09T08-16-16Z.txt)):

```text
| board | check | result | detail |
|---|---|---|---|
| (loop) | every planned board reported | PASS | 1 planned, 1 reported |
| (loop) | requests = trace attempts <= budget | PASS | 1 attempts |
| (loop) | FINISHED only if every board is OK and checks out | FAIL | agent says FINISHED |
| greenhouse/ramp | sha256 raw = report = trace | PASS | 4127597215cc |
| greenhouse/ramp | count = raw jobs (a failed board may report none) | PASS | raw 1, report 1 |
| greenhouse/ramp | new = raw - before | PASS | recomputed 0 |
| greenhouse/ramp | careers page uses this system | FAIL | board greenhouse, careers page ashby |
| greenhouse/ramp | at least the expected floor | FAIL | 1 vs 20 |

5 passed, 3 failed.
exit=1
```

The arithmetic checks pass: the agent did not miscount anything. The answer is wrong only
against knowledge from outside the agent. The same checker passes all 21 checks on live run 1
([`evidence/check-2026-11-09T08-14-22Z.txt`](evidence/check-2026-11-09T08-14-22Z.txt)), and
`tests/test_check_watch.py` pins both results on the committed runs.

## What changed because of it

The loop cannot see which system a careers page links to: `ramp.com` is off the allow-list on
purpose. But it can enforce the floor. GATE amendment A2 (`b4582e7`) made a board below its
written floor a failed board; that change is the reviewed change in
[`review/REVIEW_PACKET.md`](review/REVIEW_PACKET.md). The checker stays separate: the system
check is still only there.

## The same plan after the patch

Live, 2026-11-09 08:23 UTC, code `8259d8b` (the patch), loop
[`2026-11-09T08-23-46Z`](../../data/watch/loops/2026-11-09T08-23-46Z/report.md): `greenhouse/ramp`
is `FAILED`, `INVALID_RESPONSE`, note `below_floor`; the loop exits `ERROR` (code 10), because
its only board failed. The board's `state.json` is byte-identical to that run's
`state.before.json`: nothing was written. The independent check now agrees with the agent: 7
passed, 0 failed ([`evidence/check-2026-11-09T08-23-46Z.txt`](evidence/check-2026-11-09T08-23-46Z.txt)).
How the checker treats a board the agent failed changed twice, and both versions are on record.
The checker as first written reported this run as 3 failed, because it expected a count and
expectations met even from a board the agent had failed
([`evidence/check-2026-11-09T08-23-46Z.original-checker.txt`](evidence/check-2026-11-09T08-23-46Z.original-checker.txt)).
Claude then relaxed it (`c51335d`) so that a failed board's missed expectations counted as
agreement. The independent review pointed out that this made the checker unable to catch an agent
that wrongly fails a good board. The current version (`32d0d8c`) records a failed board's
expectations as facts and has one decisive row: the failure must be justified by a missed
expectation. `tests/test_check_watch.py` checks that it now fails a constructed copy of run 1 in
which `ashby/ramp` is marked FAILED. All five runs' check outputs were regenerated with this
version; the wrong runs still fail 3 checks, and this run passes 6 with 0 failures.

The stale ID `8042562003` from the two earlier runs is still in that board's saved state.
Clearing it is the one write that needs Shubham's approval: `uv run jsa watch reset
greenhouse/ramp` at a terminal (GATE §6, B16–B18).

## Limits of this demonstration

- The wrong board was chosen on purpose after probing; it is a demonstration, not an accident.
- The floors and the careers-page facts in `expectations.toml` were recorded by Claude on
  2026-11-09. They are only as good as that reading; Shubham re-checks them by hand.
- A stale board above its floor, on the system the careers page names, passes every check.
