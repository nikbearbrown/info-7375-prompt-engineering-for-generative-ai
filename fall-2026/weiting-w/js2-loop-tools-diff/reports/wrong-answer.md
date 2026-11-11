# The finished wrong answer

**What this demonstrates.** A run that completes, reports honestly, exits
`finished`, returns 0 to the shell — and is wrong.

**Gate reference.** `GATE.md` §6. **Run on** 2026-11-09, by Claude (Opus 5), in
the Cowork cloud container. **Verbatim output.**
[`reports/wrong-answer-transcript.txt`](wrong-answer-transcript.txt).
**Tests.** `tests/test_wrong_answer.py`, 9 tests.

Everything in this file is **SEEDED**. The response that produces the wrong
answer is `evidence/seeded/replay-wrong-answer/greenhouse-reddit.json`, written
by hand on 2026-11-09, and it says so in its own `_seeded` field:

```json
{
 "_seeded": "CONSTRUCTED BY HAND, NOT A CAPTURE. ... HTTP 200, valid JSON,
             correct schema, zero postings. boards-api.greenhouse.io never
             sent this.",
 "jobs": [],
 "meta": {"total": 0}
}
```

Both runs used `--replay-from`. No request was made to any host.

---

## 1. Why this failure and not a crash

An exception is easy. It stops the loop, it lands in the trace with a
classification, the exit status becomes `error` or `incomplete`, and the run
report says so in a line beginning `ESCALATE:`. Nothing about it is quiet.

The failure worth building a tool against is the one where **every component
behaves correctly and the conclusion is false**. A board token that has been
retired, or a provider that renamed its postings array, looks like this from the
outside:

| | |
|---|---|
| the request | allowed by the policy, issued, HTTP **200** |
| the body | valid JSON |
| the schema | correct — `{"jobs": [...]}` is exactly the shape the adapter expects |
| the parse | succeeds, **0** postings |
| new postings | 0 of 0 |
| exit status | `finished` |
| exit code | **0** |

There is nothing in that column for the loop to object to. `finished` is the
*right* status for what the loop knows, and "no new postings" is a true
statement about what it saw. The loop is not broken. It is answering a different
question than the one I care about: it knows what the response contained, and I
want to know whether the board has jobs.

This is also why the distinction between an empty board and a malformed one is
load-bearing, and why it is a test
(`tests/test_providers.py::test_a_payload_of_the_wrong_shape_is_a_schema_failure_not_an_empty_board`).
A payload of the wrong shape raises `SchemaFailure` and the board is reported
failed. `{"jobs": []}` does not, and must not — because 161 of the 163 real
postings in this repository came through the same code path, and an adapter that
treated "zero" as "broken" would be lying about the honest case to protect me
from the dishonest one.

## 2. The two runs

Run 1 replays the real 2026-10-31 capture, so the board has a previous count on
disk. Run 2 replays the constructed empty response.

```
[FINISHED] complete=True  mode=replay:evidence/seeded/replay-real  loop=L-v1  rule=R-v3
  ok        greenhouse:reddit            postings=163  attempts=1
  first run: every posting recorded as seen, none reported as new.
exit=0

[FINISHED] complete=True  mode=replay:evidence/seeded/replay-wrong-answer  loop=L-v1  rule=R-v3
  boards planned=1 attempted=1 observed=1 failed=0
  requests 1/12   seconds 0.001/90.0
  ok        greenhouse:reddit            postings=0  attempts=1
  new postings: 0
exit=0
```

Read run 2 as a user would. One board planned, one attempted, one observed, none
failed. Well inside budget. No retries. `new postings: 0`. No `ESCALATE:` line,
because the run report only emits one when the exit status is not `finished`,
and this status is `finished`. Exit code 0, so a cron job wrapping this would
record a success and send no mail.

If this ran nightly, the honest report "no new postings" would arrive every
morning, indefinitely, and look exactly like a quiet week in the job market.

## 3. What catches it

`tools/crosscheck.py`, against the same two saved responses and the floor
written by hand in `config/boards-wronganswer.json`:

```
crosscheck: reading evidence/seeded/wrong-answer (never the run report)

board                           latest  previous  floor  state  flags
greenhouse-reddit                    0       163      1      0  BELOW_FLOOR,SUSPECT_EMPTY,SUSPECT_DROP

<run total>                          0       163      -      -  SUSPECT_TOTAL

FLAG BELOW_FLOOR    greenhouse-reddit
FLAG SUSPECT_EMPTY  greenhouse-reddit
FLAG SUSPECT_DROP   greenhouse-reddit
FLAG SUSPECT_TOTAL  <run total>

crosscheck: 4 flag(s). A flag is not proof of a bug; it is a place I have to look myself.
exit=1
```

**The loop returned 0. The cross-check returned 1.** Same bytes, same run, two
different questions.

Four independent reasons fired, which matters because any one of them alone
would be a thin signal:

- `BELOW_FLOOR` — 0 is under the floor of 1 I wrote by hand. The floor is not an
  estimate of the board's size. It is the one thing I was willing to assert
  without looking: *a live public job board answering 200 with zero postings is
  not something I believe without checking.*
- `SUSPECT_EMPTY` — the board had postings in the previous saved response and
  has none now.
- `SUSPECT_DROP` — the count fell by more than half (`DROP_RATIO = 0.5`).
- `SUSPECT_TOTAL` — the run's total across all boards fell by more than half,
  which is the flag for a change that hits every board at once, such as a
  provider-wide field rename.

### What makes it independent, and how that is checked

The tool never reads a run report. That is a claim about a program, so it is
asserted rather than stated:
`test_the_crosscheck_reaches_its_verdict_with_no_run_report_on_disk` runs the
loop twice, then **deletes every run report and trace** from `evidence/runs/`,
leaves only the saved responses and the hand-written floor, and requires the
same `BELOW_FLOOR` verdict and the same exit code 1. The agent's own account of
the run is not merely unused; it is not there.

It also has to be able to stay quiet, or a flag means nothing when it fires:
`test_a_board_above_its_floor_is_not_flagged` runs a board with 3 postings
against a floor of 1 and requires exit 0 and `nothing flagged`.

## 4. The thing I did not design, and found by running it

Look at the `state` column: **0**.

The state file's `last_count` for this board was 163 after run 1 and is 0 after
run 2, because the state file records what was last observed and 0 *was* last
observed. The loop overwrote the number that would have raised the alarm with
the number that needs an alarm raised about it, and said nothing, because
nothing went wrong.

So the state file cannot be the cross-check's baseline. By the time anyone looks,
the evidence of the drop is gone from it. This is the concrete reason
`tools/crosscheck.py` compares **saved response bytes against each other** and
treats the state column as display only — a design decision that was taken on
instinct when the tool was written and that this demonstration turned into a
reason I can state.

Pinned by `test_the_state_file_records_the_wrong_count_and_is_not_a_safe_baseline`,
so that a future change which starts trusting `state.boards[*].last_count`
fails. The same test records the limit of the problem: `seen_ids` is monotonic,
so the 163 postings are not forgotten — it is only the per-board count that
regresses.

## 5. Two refusals that happened while building this

Neither was planned. Both are the permission policy working on me, and they are
better evidence that §5 is enforced in code than the boundary table is, because
I was not trying to trigger them.

**Writing outside `evidence/`.** The first attempt pointed `--raw-dir` at a
scratch directory outside the project:

```
[ERROR] complete=False  exit_status=error
  policy refusal aborted the run: PathEscapes: /tmp/.../wa-baseline/raw/20261109T215209Z-greenhouse-reddit.json
  does not resolve to a location inside /home/.../js2-loop-tools-diff/evidence
  ESCALATE: no posting list is emitted for an aborted run.
exit=3
```

The write confinement check resolves the whole parent chain, so a path outside
the output root is refused no matter how it is spelled. The run aborted with
exit 3 and emitted no posting list.

**Overwriting a saved response.** Two runs inside the same wall-clock second want
the same filename, `<utc-stamp>-<board>.json`, and replacing a file under `raw/`
requires `--approve-overwrite` (§5.3). The second run raised `NeedsApproval` and
the first run's captured bytes were still on disk, unmodified.

That second one is a real operational limitation, not just a demonstration: two
legitimate back-to-back runs in the same second cannot both save. It is written
up in `FRICTIONAL.md` and **not fixed**, because the failure direction is the
safe one — it stops, it says which file and which flag, and it never silently
replaces a captured response. A sub-second suffix is the fix. The test to write
first already exists:
`test_two_runs_in_one_second_refuse_rather_than_overwrite_evidence` asserts the
refusal *and* that the bytes on disk are byte-identical afterwards.

## 6. What this does not do

- **It needs a previous response to compare against.** On a board's very first
  run, `previous` is `None`, and only `BELOW_FLOOR` can fire. The floor is
  therefore the whole defence on a first run, which is why it is hand-written
  per board and justified in `config/boards.json` rather than computed.
- **The floors are 1, not the boards' real sizes.** A board that drops from 163
  postings to 1 is above its floor and is not empty, so neither `BELOW_FLOOR`
  nor `SUSPECT_EMPTY` fires and only `SUSPECT_DROP` is left — and on that
  board's first run, nothing at all would fire. I do not know how many postings
  these boards carry and will not write a number I would be guessing.
- **A provider-wide rename that produces a *parse error* rather than an empty
  array is caught by the loop instead**, as a `schema` failure, and never
  reaches this tool. That is the intended split, but it means the cross-check is
  tested against one of the two shapes a rename can take.
- **Nothing here runs automatically.** `tools/crosscheck.py` is a command I have
  to run. A nightly job that ran the loop and not the cross-check would get the
  quiet wrong answer every morning, exactly as described in §2. Wiring it into
  the run is the obvious next step and is not done.
