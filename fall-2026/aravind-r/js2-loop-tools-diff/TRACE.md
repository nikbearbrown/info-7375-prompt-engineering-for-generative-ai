# Traces: the real run with the deliberate failure, and the finished-wrong answer

## The real run: `20261110T225022146Z-post-patch-1`

Trace: `out/traces/20261110T225022146Z-post-patch-1.jsonl`. A live run of the normal four-board config, after the `src/state.mjs` patch (`c04d1ecf`) and the trace-timing fix (`85657387`). Started with `["--config","boards.json","--label","post-patch-1"]` (its `run_start` event), on Node v20.20.2.

The deliberate failure is `gh-broken`, Greenhouse token `no-such-board-js2` (`boards.json`).

Key events, in the order the trace records them. For `request` events, `at` is when the request was sent and `completed_at` when its response came.

| `at` (UTC) | Event | Details |
|---|---|---|
| 22:50:22.154 | `run_start` | mode `live` |
| 22:50:22.155 | `config` | limits: 5 boards, 8 requests, 60 s |
| 22:50:22.157 | `request` 1 | gh-stripe, 200, completed 22:50:22.528, timeout 15000 ms |
| 22:50:22.546 | `board_result` | gh-stripe `unchanged (no new IDs)`, 776 jobs, 0 new |
| 22:50:22.546 | `request` 2 | gh-airbnb, 200, completed 22:50:22.672 |
| 22:50:22.681 | `board_result` | gh-airbnb `unchanged (no new IDs)`, 203 jobs, 0 new |
| 22:50:22.682 | `request` 3 | lv-spotify, 200, completed 22:50:23.497 |
| 22:50:23.505 | `board_result` | lv-spotify `observed`, 85 jobs, 85 new; `state_before: null` (prior state quarantined in `c4f9b555`) |
| 22:50:23.505 | `board_start` | gh-broken, 58641 ms of wall clock left, 3 requests used |
| 22:50:23.506 | `request` 4 | `GET https://boards-api.greenhouse.io/v1/boards/no-such-board-js2/jobs?content=true`, permission `allow`, **status 404**, completed 22:50:23.562, body saved to `out/raw/20261110T225022146Z-post-patch-1/gh-broken.attempt1.json` |
| 22:50:23.564 | `board_result` | gh-broken **`error: not found`**, `raw_count: null`, `new_count: null`, `state_updated: false`, `escalate: true` |
| 22:50:23.566 | `failures_written` | `out/failures.json` |
| 22:50:23.568 | `run_end` | **`incomplete`, exit 10**, 4 requests |

How the error policy handled the failure, from this trace:

- **No retry:** the trace has one request for gh-broken, and no `retry` or `no_retry` event after it.
- **The error body was saved,** not discarded: `out/raw/20261110T225022146Z-post-patch-1/gh-broken.attempt1.json` holds `{"status":404,"error":"Job not found"}`.
- **No invented value:** the board's counts are `null`, not `0`, and no state file was written for it (`state_after: null`).
- **Escalation:** `escalate: true` because gh-broken had failed on consecutive attempted runs. `out/failures.json` holds `consecutive: 4` after the next run, `20261110T225032086Z-post-patch-2`.
- **The run did not end `finished`:** the three real boards were observed, but the deliberate failure made the run `incomplete`.

The checker passed every rule for every board of this run (`evidence/check-post-patch.txt`, quoted in `REVIEW.md`, "Live runs after the patch").

## The finished-wrong answer

A run that ended cleanly (`finished`, exit 0) and was wrong. All three runs below used JS1's unpatched `src/state.mjs` and predate the trace-timing fix (`85657387`), so their `request` and `retry` times are write times (see `README.md`, "What ran").

1. **Baseline, live: `20261110T215021538Z-prefix-lever-baseline`** (`--config configs/lv-spotify-only.json`).
   - Request 1 timed out, and the retry (request 2) returned 200.
   - The raw response, `out/raw/20261110T215021538Z-prefix-lever-baseline/lv-spotify.attempt2.json`, has 86 postings.
   - `board_result`: `observed`, 86 jobs, 86 new, which is correct for a first observation with no prior state.
   - `run_end`: `finished`, exit 0.
   - The state it saved, `out/snapshots/20261110T215021538Z-prefix-lever-baseline/lv-spotify.after.json`, holds `[null]`.
2. **Normal run, live: `20261110T215039330Z-normal`** (`--config boards.json`). It loaded `[null]` and reported lv-spotify `observed`, 86 new again. It saved `[0, null]` (`out/snapshots/20261110T215039330Z-normal/lv-spotify.after.json`).
3. **Replay: `20261110T215313703Z-prefix-lever-replay-2`** (`--replay out/raw/20261110T215021538Z-prefix-lever-baseline/lv-spotify.attempt2.json`). This is a **replay**, not a live observation:
   - mode `replay` in `run_start`;
   - zero `request` events;
   - a `replay_read` of the baseline's saved raw response, the same bytes as step 1.
   - Its pre-run state was `[0, null]` (`out/snapshots/20261110T215313703Z-prefix-lever-replay-2/lv-spotify.before.json`).
   - `board_result`: `observed`, 86 jobs, **86 new**. `run_end`: **`finished`, exit 0**.
   - **This is the wrong answer.** The correct new count was 0: every one of the 86 UUIDs was in the baseline's response.

An earlier replay attempt, `20261110T215039252Z-prefix-lever-replay`, ended `error`, exit 12, with zero requests and no observations. Its `--replay` path was empty (`argv` shows `"--replay",""`).

**The independent check.** Saved in `evidence/check-pre-fix.txt`, quoted in full below. The checker reads only the raw responses, snapshots and traces in `out/`, and never the loop's report.

```
# 20261110T215021538Z-prefix-lever-baseline (mode: live) — out/traces/20261110T215021538Z-prefix-lever-baseline.jsonl
lv-spotify rule 1: PASS — 86 raw job(s), 86 unique valid id(s)
lv-spotify rule 2: PASS — expected 86 new, claimed 86
lv-spotify rule 3: FAIL — post-run state has 1 invalid id(s), e.g. null; post ≠ pre ∪ raw: 86 id(s) missing from post-run state; post ≠ pre ∪ raw: 1 id(s) in post-run state not in pre ∪ raw; first observation: 0 valid persisted id(s), raw has 86
20261110T215021538Z-prefix-lever-baseline: FAIL
# 20261110T215313703Z-prefix-lever-replay-2 (mode: replay) — out/traces/20261110T215313703Z-prefix-lever-replay-2.jsonl
lv-spotify rule 1: PASS — 86 raw job(s), 86 unique valid id(s)
lv-spotify rule 2: PASS — expected 86 new, claimed 86
lv-spotify rule 3: FAIL — pre-run state has 2 invalid id(s), e.g. 0; post-run state has 2 invalid id(s), e.g. 0; post ≠ pre ∪ raw: 86 id(s) missing from post-run state
20261110T215313703Z-prefix-lever-replay-2: FAIL
```

Both results are FAIL, so a checker run over these two traces exits 1 (`exitCodeFor` in `src/check.mjs`).

- **For the replay, rule 2 agrees with the false claim** (expected 86 new, claimed 86). Rule 2 recomputes the new ids against the pre-run seen set, and that set was already corrupt (`[0, null]`), so no UUID appears seen.
- **Rule 3 catches it.** The persisted ids are not valid Lever ids, and the post-run state does not contain the 86 raw UUIDs.
- **For the baseline,** rule 2 passed correctly (86 new on a first observation), and rule 3 flagged the `[null]` the run wrote.
