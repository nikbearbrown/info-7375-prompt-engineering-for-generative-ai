# Job-Search Agent 2: the loop, the tools, and the diff

A bounded loop that watches four public job boards across two applicant-tracking systems (Greenhouse and Lever), under a permission policy enforced in code (`src/policy.mjs`), and ends every run in exactly one exit status. An independent checker (`src/check.mjs`) recomputes each run's claims from the saved raw responses and state snapshots. The specification is `GATE.md`; the boundary-case predictions are `test/boundary-cases.md`. Both were committed before any JS2 code (`aedc7034`, `359ee568`; the first JS2 code is `49c6066e`).

The agent never applies, emails, messages, or logs in. It sends HTTPS GET requests only, to two hosts and two path shapes (`src/policy.mjs`, `checkRequest`).

## Starting point

My Job-Search Agent 1 code, from `fall-2026/aravind-r/js1-contract-and-watch/` (branch `js1-contract-and-watch-aravind-r`, last JS1 commit `fa577f9`), copied into this folder in `ce33fd8d`. From JS1: `src/{claude-judge,fetch,persona,rule,state,text,watch}.mjs`, `test/contract.test.mjs`, `test/fixtures/`, `persona/`, `prompts/`, `CONTRACT.md`. JS1's `src/state.mjs` was kept unchanged through the pre-fix runs and patched in `c04d1ecf` (see `REVIEW.md`). JS1's `watch.mjs`, `fetch.mjs` and `claude-judge.mjs` remain in `src/` because JS1's tests import them; `test/wrong-versions.test.mjs` (WV12) checks that none of them is reachable from `src/loop.mjs`.

## Language and toolchain

- **Language:** JavaScript, ES modules (`.mjs`).
- **Runtime:** Node.js v20.20.2 (recorded as `node` in every trace's `run_start` event, e.g. `out/traces/20261110T225022146Z-post-patch-1.jsonl`).
- **Dependencies:** none. No `package.json`; only Node built-ins (`fetch`, `node:test`, `node:fs`, `node:path`, `node:url`, `node:util`). `node:child_process` is used by tests, `tools/mutate-policy.mjs`, and JS1's `src/claude-judge.mjs`, which `src/loop.mjs` does not import (`test/wrong-versions.test.mjs`, WV12).
- **Tests:** `node --test` (Node's built-in runner).

## Commands (from a fresh clone)

Run everything from this folder:

```bash
cd fall-2026/aravind-r/js2-loop-tools-diff
```

Tests (no network; stubbed fetch, injected clocks, temp directories):

```bash
node --test
```

The normal four-board run (live requests to `boards-api.greenhouse.io` and `api.lever.co`):

```bash
node src/loop.mjs --config boards.json --label normal
```

The same run with the request budget lowered to 2:

```bash
node src/loop.mjs --config boards.json --label max-requests-2 --max-requests 2
```

A replay: zero network requests, reading a raw response already saved under `out/raw/`, with a single-board config:

```bash
node src/loop.mjs --config configs/lv-spotify-only.json --label replay --replay out/raw/20261110T225022146Z-post-patch-1/lv-spotify.attempt1.json
```

The independent checker on one or more traces:

```bash
node src/check.mjs --trace out/traces/20261110T225022146Z-post-patch-1.jsonl
```

The mutation check for the policy (copies go to `.mutants/`, which is gitignored):

```bash
node tools/mutate-policy.mjs
```

Loop exit codes (`src/loop.mjs`, `EXIT`): `0` finished, `10` incomplete, `11` budget-exhausted, `12` error. Checker exit codes (`src/check.mjs`): `0` every rule passed for every trace, `1` any rule failed or a run had no observations, `2` usage or evidence error.

checker PASS means the claims match the raw data, not that the run finished.

## What ran

The final `node --test` execution after the duplicate-ID fix (`42c9bc52`) and the administrator-safe snapshot test (`ea5e0198`) is recorded in `evidence/node-test-final.txt`: **123 tests passed, 0 failed**. This is a separate, later run from `evidence/node-test-post-patch.txt`, which is retained as historical patch evidence.

Every run below is a trace in `out/traces/`. "Requests" counts `request` events in the trace. All runs were on 2026-11-10 (UTC timestamps in the run ids).

| Run id | Mode | Command flags | End | Requests | Boards |
|---|---|---|---|---|---|
| `20261110T215021538Z-prefix-lever-baseline` | live | `--config configs/lv-spotify-only.json` | finished, 0 | 2 | lv-spotify observed, 86 jobs, 86 new (request 1 timed out, request 2 returned 200) |
| `20261110T215039252Z-prefix-lever-replay` | replay | `--replay ""` | error, 12 | 0 | none; `--replay` path was empty, refused as "not under out/raw/" |
| `20261110T215039330Z-normal` | live | `--config boards.json` | incomplete, 10 | 4 | gh-stripe 775 new; gh-airbnb 203 new; lv-spotify 86 new; gh-broken `error: not found` |
| `20261110T215044569Z-max-requests-2` | live | `--max-requests 2` | budget-exhausted, 11 | 2 | gh-stripe, gh-airbnb unchanged; lv-spotify and gh-broken not attempted |
| `20261110T215313703Z-prefix-lever-replay-2` | **replay** | `--replay out/raw/20261110T215021538Z-prefix-lever-baseline/lv-spotify.attempt2.json` | finished, 0 | 0 | lv-spotify observed, 86 jobs, 86 new (the finished-wrong answer, see `TRACE.md`) |
| `20261110T220054650Z-prefix-lever-baseline` | live (supplementary) | `--config configs/lv-spotify-only.json` | finished, 0 | 1 | lv-spotify 86 jobs, 86 new |
| `20261110T220059459Z-prefix-lever-replay` | **replay** (supplementary) | `--replay out/raw/20261110T220054650Z-prefix-lever-baseline/lv-spotify.attempt1.json` | finished, 0 | 0 | lv-spotify 86 jobs, 86 new |
| `20261110T220108098Z-normal` | live (supplementary) | `--config boards.json` | incomplete, 10 | 4 | gh-stripe 776 jobs, 1 new; gh-airbnb unchanged; lv-spotify 86 new; gh-broken `error: not found`, escalate |
| `20261110T220114084Z-max-requests-2` | live (supplementary) | `--max-requests 2` | budget-exhausted, 11 | 2 | gh-stripe, gh-airbnb unchanged; lv-spotify and gh-broken not attempted |
| `20261110T224942910Z-post-patch-integrity` | live | `--config boards.json` | error, 12 | 3 | gh-stripe 1 new; gh-airbnb unchanged; then `STATE_INTEGRITY` on `out/state/lv-spotify.json` (`[0, null]`) |
| `20261110T225022146Z-post-patch-1` | live | `--config boards.json` | incomplete, 10 | 4 | gh-stripe, gh-airbnb unchanged; lv-spotify 85 jobs, 85 new; gh-broken `error: not found`, escalate |
| `20261110T225032086Z-post-patch-2` | live | `--config boards.json` | incomplete, 10 | 4 | all three real boards unchanged (lv-spotify 85 jobs, 0 new); gh-broken `error: not found`, escalate |

Notes on these runs:

- **Pre-fix traces predate the timestamp fix.** The first nine runs (21:50 to 22:01 UTC) ran before `85657387` ("Write trace events as they happen, stamped with their own time"). In those traces, `request` and `retry` events were written after the board's request finished, each stamped with its write time, and they have no `completed_at` field. Example: in `20261110T215021538Z-prefix-lever-baseline`, request 1 (timeout), request 2 (200) and the `retry` event are all stamped 21:50:39.197 to .198, and `retry` appears after request 2. The three post-patch traces have `completed_at` and are in event order.
- **The 22:00 runs started from corrupted state.** Before `20261110T220054650Z-prefix-lever-baseline`, `out/state/lv-spotify.json` already held `[0, null]`, written by `20261110T215039330Z-normal` and carried through `20261110T215313703Z-prefix-lever-replay-2` (`out/snapshots/20261110T220054650Z-prefix-lever-baseline/lv-spotify.before.json`). So that run was not a fresh-state baseline, and its 86 new is not a first-observation count. `20261110T220059459Z-prefix-lever-replay` and `20261110T220108098Z-normal` also started from `[0, null]` (their `lv-spotify.before.json` snapshots). The four 22:00 runs (`220054650Z`, `220059459Z`, `220108098Z`, `220114084Z`) are supplementary. The finished-wrong demonstration cited in `TRACE.md` is the 21:50 chain: `215021538Z` baseline → `215039330Z` normal → `215313703Z` replay-2.
- **The pre-fix runs used JS1's `src/state.mjs`** (unchanged since `ce33fd8d`); the three post-patch runs ran after `c04d1ecf` (state patch), `15ae4789` and `377fd51c`, by commit time.
- **Recovery between the integrity run and post-patch-1** was manual: `out/state/lv-spotify.json` moved to `out/quarantine/lv-spotify.corrupt.json` in `c4f9b555`. So post-patch-1 observed Spotify with no prior state (its `board_result` has `state_before: null`).
- The raw responses, snapshots, state and traces of the pre-fix runs were committed in `b0bc86f9`; the post-patch evidence in `c4f9b555` and `0326b046`.

## Trace schema

One JSON object per line in `out/traces/<run>.jsonl`, appended as events happen. Every event has `at` (UTC ISO time), `run` (the run id) and `event`. Events and their fields (from `src/loop.mjs`):

| Event | Fields |
|---|---|
| `run_start` | `mode` (`live` or `replay`), `label`, `argv`, `node`, `root`, `config`, `replay`, `approve` |
| `config` | `config` (path), `limits` (`boards`, `requests`, `wallSeconds`), `boards` |
| `board_skipped` | `board`, `disposition: "skipped: duplicate"`, `duplicate_of` |
| `board_start` | `board`, `system`, `token`, `remaining_ms`, `requests_used` |
| `request` | `at` = **when the request was sent**, `completed_at` = **when its response, error or timeout came** (added in `85657387`), `board`, `request` (number in this run), `method`, `url`, `permission`, `status`, `outcome` (`ok`, `http`, `redirect`, `timeout`, `transport`), `error`, `location`, `timeout_ms`, `raw_path` |
| `request_refused` | `board`, `outcome`, `reason` (policy denial or repeat) |
| `retry` | `board`, `after` (first attempt's outcome), `status`, `wait_ms` |
| `no_retry` | `board`, `reason` (e.g. `rate-limited`, `budget: wall-clock`) |
| `replay_read` | `board`, `raw_path`, `network_requests: 0` |
| `board_not_attempted` | `board`, `budget` |
| `board_result` | `board`, `system`, `token`, `disposition`, `raw_path`, `raw_count`, `new_count`, `new_ids`, `state_path`, `state_before`, `state_after`, `state_updated`, `escalate` |
| `failures_written` / `failures_unchanged` | `path`; `failures_unchanged` also has `reason` (replay runs, `e871e90d`) |
| `run_end` | `status`, `exit_code`, `reason`, `requests`, `unattempted` |

A failed board's `raw_count` and `new_count` are `null`, never `0`.

## Layout of `out/`

| Path | Contents |
|---|---|
| `out/traces/<run>.jsonl` | the append-only trace of each run |
| `out/raw/<run>/<board>.attempt<k>.json` | the raw response body of each attempt that returned one, including error bodies (e.g. the 404 body for gh-broken); a replay reads its file from here and writes none |
| `out/snapshots/<run>/<board>.before.json`, `.after.json` | read-only copies of the board's state file before and after the run; no `before` file means there was no state |
| `out/state/<board>.json` | the cumulative set of seen ids per board (`board`, `updated_by_run`, `count`, `ids`) |
| `out/failures.json` | consecutive attempted-run failures per board (`consecutive`, `last_error`, `last_run`, `escalate`); since `e871e90d` a replay leaves it unchanged (the two pre-fix replays, `215313703Z` and `220059459Z`, ran before that commit) |
| `out/reports/<run>.json` | the loop's own report; `src/check.mjs` refuses to read it |
| `out/quarantine/lv-spotify.corrupt.json` | the corrupt pre-fix Lever state (`[0, null]`), moved here by hand in `c4f9b555` |

## Other files

| File | What it is |
|---|---|
| `GATE.md` | the spec: exits, budgets, repeat rule, error policy, permission policy, wrong versions, dated Decisions |
| `test/boundary-cases.md` | 43 boundary cases with predictions and results |
| `REVIEW.md` | the review packet for the `src/state.mjs` change |
| `TRACE.md` | the real run with the deliberate failure, and the finished-wrong demonstration |
| `SOURCES.md` | what came from JS1, from Claude Code, and from Claude chat |
| `evidence/` | saved test, mutant-check and diff output used by `REVIEW.md` |
| `configs/lv-spotify-only.json` | the single-board config used for the finished-wrong demonstration |
| `tools/mutate-policy.mjs` | the mutation check |
