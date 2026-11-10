# GATE.md — Job-Search Agent 2

This is the **pre-implementation contract** for a bounded, read-only job-board watcher. The implementation must obey these rules; if the code and this document disagree, the code or this specification must be revised and the decision recorded before treating the run as verified.

## Starting point and boards

The starting point is Job-Search Agent 1's JavaScript/Node.js board watcher and saved-ID logic. JS2 extends that watcher to multiple applicant-tracking systems; it does not apply to jobs.

| Board ID | ATS | Configured token | Role in the run |
|---|---|---|---|
| `gh-stripe` | Greenhouse | `stripe` | Original Greenhouse board |
| `gh-airbnb` | Greenhouse | `airbnb` | Second Greenhouse board |
| `lv-spotify` | Lever | `spotify` | Second ATS; preserves string/UUID job IDs |
| `gh-broken` | Greenhouse | `no-such-board-js2` | Deliberately invalid board; expect an HTTP 404, not a fabricated zero |

On **2026-11-10**, Claude Code initially spot-checked HTTP 200 for the three real boards and HTTP 404 for the deliberately invalid board; that preliminary check reported 84 Spotify postings (see `SOURCES.md`). **That 84 count is not the controlled demonstration fixture.** The saved pre-fix baseline and replay contain **86** Spotify postings (`20261110T215021538Z` and `20261110T215313703Z`); the post-patch live runs contain **85** (`20261110T225022146Z` and `20261110T225032086Z`). These are different observations, not interchangeable fixture counts.

**Decision: retain four boards rather than add a fifth.** Four already exceed the minimum of three boards across two ATSs, and the eight-request ceiling permits four initial attempts plus up to four counted retries. The deliberately broken board does not retry on 404. A fifth board is not necessary for this submission; adding one requires rechecking the worst-case retry budget and recording a new decision.

## Loop exits

A run ends in exactly one terminal status. If multiple conditions apply, precedence is `error` > `budget-exhausted` > `incomplete` > `finished`.

| Status | Condition | Required report | Process exit |
|---|---|---|---|
| `finished` | Every configured unique board was successfully observed with a **nonempty, valid** response; all required writes and checks succeeded | Per-board observed count, new IDs, and evidence paths | `0` |
| `incomplete` | The board list was processed, but one or more boards failed, were rate-limited, or yielded an unverified empty response | Successful observations **plus** the failed/suspect boards and precise reasons; never represent a failure as `0 new jobs` | `10` |
| `budget-exhausted` | The next requested action (including a retry or its required wait) cannot fit within a request, board, or wall-clock budget | The budget reached, completed observations, and every board not attempted; do not issue the over-budget action | `11` |
| `error` | Run integrity fails: invalid config, unauthorized own operation, unreadable/corrupt state, unrecordable required trace/state/failure count, or other invariant violation | Specific reason, partial evidence if safe, **no trustworthy overall new-job claim** | `12` |

Stopping is not the same as being correct. `finished` is a loop-status claim; `src/check.mjs` independently validates evidence and may identify a wrong `finished` answer. The final JS2 specification requires ID validation in `src/state.mjs`; the controlled pre-fix JS1 demonstration deliberately runs the old, defective version of that module, so its `finished` result does **not** satisfy this revised specification.

With `gh-broken` enabled, an ordinary complete traversal should end **`incomplete` (exit 10)** due to its 404, even if the other three boards succeed. A clean `finished` demonstration requires a separate controlled fixture/configuration that excludes the deliberate failure; its different configuration must be named in the trace.

An empty list **with prior seen IDs** is `suspect: empty`; an empty list **without prior state** is `empty (unverified)`. Both count as failed/unverified boards and produce `incomplete` at end-of-list (or `budget-exhausted`/`error` if a higher-priority condition arises). Neither is called `no new jobs`; neither changes seen-ID state.

## Budgets and limits

| Resource | Maximum per run |
|---|---:|
| Unique boards attempted | 5 |
| HTTP requests, including retries | 8 |
| Wall-clock duration | 60 seconds |
| Timeout per HTTP attempt | `min(15 seconds, wall-clock time remaining)` |
| Retries per failed attempt/board | 1 |

Before **each** request, retry wait, board attempt, and filesystem mutation, validate the relevant budget and permission. If no positive wall-clock time remains, stop rather than starting a request. A timeout must abort/cancel the in-flight fetch. Retry waits and state/trace writes also consume wall-clock time.

The CLI/config may **lower** limits, never raise them. For example, `--max-requests 2` must stop with `budget-exhausted` and list unattempted boards; `--max-requests 20` must be **rejected before networking** (chosen behavior: reject, not silently clamp). The constants enforced by `src/policy.mjs` and the CLI must match this table. Changing a maximum requires a dated, reviewed, committed entry under **Decisions**.

**Replay mode:** `--replay <path>` reads a saved raw response **only from `out/raw/`**, makes **zero network requests**, and labels the trace `mode: replay` (and the run as a replay in `README.md`). Require a single-board configuration matching the saved response. Validate the supplied path using canonical/real paths and reject `..` escapes, sibling-directory prefix tricks, and symlinks that resolve outside `out/raw/`; a missing or invalid file is a run `error` before any network action. Replay still obeys the filesystem policy, board and wall-clock budgets, ID/state checks, and required evidence writes. Never silently fall back to a live fetch.

## Repeat rule

- Same network action within a run = identical HTTP method plus canonical URL (lowercased hostname, normalized allowed path, sorted allowed query parameters). A duplicate is rejected unless it is **the one counted retry** explicitly authorized by the error policy.
- Same board = identical ATS plus validated token. Duplicate config entries are observed once and recorded as `skipped: duplicate`; they do not consume a second HTTP request.
- A repeat across different runs is permitted. When no unseen IDs are found, report `unchanged (no new IDs)`; this means the **cumulative seen set** did not change, not that the current public board has identical postings.

## State meaning and preservation

Each `out/state/<board-id>.json` stores the **append-only set of distinct job IDs ever successfully seen** on that board. IDs are exact **strings**, including Lever UUIDs; never coerce them with `Number(...)`. Comparing IDs is string-exact. The state is not a current-postings snapshot.

On a verified, nonempty response:

1. `src/state.mjs` owns ATS ID canonicalization and **persisted-state validation**. In the reviewed JS2 patch, Greenhouse positive safe-integer or decimal-string IDs become canonical decimal strings; Lever UUIDs stay exact strings. The **provider parsers** check duplicate IDs within an individual raw response. Since `42c9bc52`, a duplicate makes only that board `error: malformed`, with **no state update**; the run ends `incomplete` unless a higher-priority exit occurs. The intended rule is the same for null/missing/malformed raw IDs, but the remaining **null-ID exception is documented under Decisions**: the current `saveState` path raises a run-wide integrity `error` (exit `12`) rather than marking one board malformed. Duplicate/invalid IDs already in persisted state are an integrity `error` for the run. **Never** apply `Number(...)` to Lever IDs. The pre-fix wrong-answer demonstration runs JS1's uncorrected `src/state.mjs`; that file is the reviewed patch target.
2. Read the pre-run seen set, `S_before`. Compute `newIds = rawIds \ S_before` and `S_after = S_before ∪ rawIds`, where `rawIds` is the set of canonical string IDs.
3. Atomically persist `S_after` only after validating the result and obtaining the required file permission. Save a read-only pre-run state snapshot in `out/` so an independent checker can recompute the delta.
4. Never remove a previously seen ID merely because a posting was taken down. If a proposed overwrite would shrink the cumulative set, require explicit approval; otherwise reject it.

An expected drop in **current live postings** is not a state shrink. Failed, malformed, rate-limited, or unverified-empty boards do **not** update `out/state/`. This preserves the original JS1 “seen IDs” semantics without preventing legitimate removals from public job boards.

## Error and escalation policy

| Observation | Response | Reason |
|---|---|---|
| Connection failure, timeout, or HTTP 5xx | Retry **at most once** after a 2-second wait, only when the request/wait fits the budgets; otherwise record the failure | A transient failure may clear, but repeated attempts are bounded |
| HTTP 429 | Parse `Retry-After` (delta seconds or HTTP date). Retry once **only** if the parsed nonnegative wait is at most **5 seconds** and the wait and next request fit remaining budgets; otherwise record `rate-limited`, with no retry | The server's rate limit takes priority over a blind 2-second retry; missing/invalid header means no retry |
| HTTP 404 | Never retry; record `error: not found` | Intentionally invalid board should remain visibly failed |
| Other HTTP 4xx | No retry; record status and cause | Most are non-transient client/permission errors |
| 3xx redirect | Never follow; record `error: redirect refused` | Redirect destinations may escape the allow-list |
| Non-JSON, missing expected jobs array, or duplicate/null/malformed raw job IDs | No retry; board `error: malformed`, **no state update** | The entire board observation is invalid; do not silently drop an offending ID |
| Empty jobs array, prior nonempty state | `suspect: empty`; count as failed; preserve state | Could be a server or parsing failure |
| Empty jobs array, no prior state | `empty (unverified)`; count as failed; preserve state | Cannot infer a verified “zero new jobs” baseline |
| Same board fails on two consecutive **attempted** runs | Set `escalate: true` and retain reasons for manual review | A person must decide whether to update the board or code |

Persist per-board consecutive attempted-run failures and last error in `out/failures.json`. Update this file for both success (reset to zero) and failure (increment); a board skipped because the budget ended is **not** counted as a success or failure. Make updates atomic and policy-checked. A failure to persist this required metadata is an `error`, not a silently completed run.

Since `gh-broken` is deliberately invalid, **its second consecutive attempted run is expected to set `escalate: true`**. That escalation is evidence that the rule ran, not an unexpected recovery or a successful board.

## Permission policy (enforced by `src/policy.mjs`)

### Network requests

Permit HTTPS **GET only**, with no credentials, to the following host/method/path combinations:

| Host | Exact path pattern | Permitted query |
|---|---|---|
| `boards-api.greenhouse.io` | `/v1/boards/<token>/jobs` | None or exactly `content=true` |
| `api.lever.co` | `/v0/postings/<token>` | None or exactly `mode=json` |

Validate `<token>` against **`^[a-z0-9-]{1,64}$` before building the URL**. When assessing any supplied URL, validate the unnormalized input path/segments too; do not rely solely on `new URL(...).pathname`, which may already normalize encoded dot-segments such as `%2e%2e`. Refuse encoded separators/traversal, extra path segments, fragments, unknown/duplicate query parameters and tokens with forbidden characters.

Hostname comparisons use the URL parser's **case-insensitive DNS normalization** (so uppercase hostname letters are accepted), followed by an **exact** comparison to the listed lowercase hostname. A trailing-dot hostname is **not** accepted. Reject non-default ports such as `:8443`, subdomain/suffix tricks, schemes other than HTTPS, URL usernames/passwords, `Authorization`, `Cookie`, `Proxy-Authorization`, and equivalent credential-bearing headers. No request may be sent to a posting's `applyUrl`.

Set `redirect: 'manual'` on every fetch and reject all 3xx responses, regardless of location. Permission is checked **before** any network action, including retries. Method/path restrictions apply even on allow-listed hosts: **no POST**, application submission, email, message, form submission, or login.

### Filesystem

- **Read:** only files inside the project's real, canonical root. Do not expand `~` automatically or treat a relative `~/.ssh/...` as a home path. A home-directory boundary test must use an **absolute path constructed from `os.homedir()`**.
- **Create/overwrite:** only files within the project's real `./out/` directory. Resolve `..`, compare **path segments** instead of string prefixes, and resolve symlinks using `realpath`; for a target not yet created, check the real path of its nearest existing ancestor and the resulting destination.
- **Guarded mutations:** delete of any file in `out/`, and an overwrite that would **reduce the append-only seen-ID set**, return `ask` unless approved. The policy cannot be bypassed by renaming or symlink swaps; check immediately before mutation.
- **Approval mechanism:** only a command-line `--approve <path>` authorizes **one specific guarded mutation** of that canonical in-scope path during **that one run**. Consume the approval when used. Without that flag, the loop treats `ask` as refused and logs `refused: needs approval`; approval never makes an out-of-scope write permissible.
- Reject writes to `boards.json`, the repository, `out-evil/`, escaped `..` paths, or links from `out/` to external directories.

### Subprocesses and autonomous actions

The JS1 optional judge calls an external `claude` CLI, which is an unpoliced subprocess capable of separate network requests. **Disable that path in JS2.** `--judge none` is the **only** accepted judge mode; any other mode is a configuration error **before** any subprocess/network action. The JS2 runtime must not invoke `child_process`/shell spawning for a judge or other hidden network-capable helper. All gate decisions are deterministic program logic.

This policy controls JS2's own code paths, not unrelated processes on the computer. The program must not submit applications, email, message recruiters, log in, or execute arbitrary downloaded code.

## Evidence and trace discipline

Record **every observation and decision** in an append-only per-run trace under `out/traces/`: board ID, UTC timestamp, request count, allowed method and canonical URL, HTTP response status or transport error, retry reason and delay, timeout/remaining budget, raw-response file path, parsed raw count, state-before/state-after artifact paths, permission result, board disposition, and terminal exit code. Persist the **raw response body** even when malformed or returned with an error, without persisting credentials. Never replace missing data with a fabricated `0`.

Use unique run IDs and atomic writes for required run metadata. The checker may use trace references to locate artifacts, but must recompute all substantive counts and differences from raw response bytes and state snapshots. Attach a trace of a normal four-board run showing the deliberate failure as part of the final submission.

## Independent check (`src/check.mjs`)

The checker is separate from the loop. It reads **saved raw ATS responses, the before/after cumulative state snapshots, and trace evidence** from `out/`; it does **not** trust the loop's report as the source of job counts or new IDs. It parses the raw ATS payload itself and recomputes:

1. **Raw validity:** every returned job has a valid ATS-native ID that the checker independently normalizes to a canonical string (Greenhouse numeric/decimal ID; Lever UUID string); the raw unique-ID count is computed independently. Empty responses cannot prove “no new jobs” on an unverified baseline.
2. **Delta correctness:** `expectedNew = rawUniqueIds \ preRunSeenIds`; the claimed new set/count is checked against this recomputation, not merely against a loop-authored summary. This calculation alone cannot detect a corrupted pre-run seen set; validate persisted state separately under rule 3.
3. **State integrity:** all persisted IDs are valid non-null strings; `postRunSeenIds` must equal `preRunSeenIds ∪ rawUniqueIds` for a successful board and must equal `preRunSeenIds` for a failed/unverified board. This includes subset and append-only checks.

**Important count nuance:** With append-only state, the total number of stored IDs can legitimately be greater than the count in today's raw response. A blanket rule “state count ≠ raw count means a bug” is **wrong** after the first run. On a first observation with an empty prior state, however, the valid persisted-ID count **must** equal the raw unique-ID count; that special-case count check is sound.

### Finished-but-wrong demonstration: Lever UUID defect

**Review-packet target:** `src/state.mjs`. ID canonicalization and validation belong in this module; the **pre-fix version is JS1's `src/state.mjs`**, which incorrectly converts Lever UUIDs with `Number(...)` and does not enforce the new ID-validation invariant. The reviewed JS2 patch is the fix to this file. The pre-fix demonstration uses the old code **before** this patch, so it can write `[null]` and return `finished` even though that behavior would violate the revised JS2 contract. No separate loop-level validation may be silently added to the pre-fix test.

Use a clearly identified **single-board controlled configuration** containing only `lv-spotify`, not the ordinary four-board run containing `gh-broken`. Preserve the same real Spotify raw-response bytes between the two pre-fix executions:

1. **Baseline run (pre-fix, fresh state):** `20261110T215021538Z-prefix-lever-baseline` observed **86 Spotify jobs** and correctly claimed **86 new** on the first observation; JS1's defective `src/state.mjs` nevertheless persisted `[null]` and the loop exited `finished`. The saved response used for replay is `out/raw/20261110T215021538Z-prefix-lever-baseline/lv-spotify.attempt2.json` (attempt 1 timed out).
2. **Labeled replay (pre-fix, `mode: replay`):** `20261110T215313703Z-prefix-lever-replay-2` used those **same saved bytes**, made **zero HTTP requests**, and falsely claimed **86 new** again while exiting `finished`. The correct unseen count relative to the previously observed 86 UUIDs is **0**. An intervening four-board live run (`20261110T215039330Z-normal`) had reloaded the corrupt `[null]` state and left `[0, null]`; the replay therefore starts with `[0, null]`, not an untouched baseline state. The README and trace distinguish the replay from live observations.
3. **Independent check:** run `src/check.mjs` against the raw response plus the pre/post state snapshots, without trusting either run's reported counts. **Rule 3 is what catches it. Rule 2 alone would agree with the false claim, because it recomputes against the corrupted pre-run state.** Rule 3 must fail on the invalid/null persisted IDs and the missing UUID union. Save the checker command, output, and nonzero exit result.
4. **Regression and patch:** keep the failing regression test written **before** changing `src/state.mjs`; review that file's diff, run the test against the patched code using a clean/valid baseline state, and record the passing output. If reusing corrupted pre-fix state, explicitly test or document the recovery/migration rather than hiding it.

**Saved demonstration evidence:** `out/traces/20261110T215021538Z-prefix-lever-baseline.jsonl` (86 new, saved `[null]`), `out/traces/20261110T215039330Z-normal.jsonl` (intervening run; `[0, null]`), `out/traces/20261110T215313703Z-prefix-lever-replay-2.jsonl` (`mode: replay`, false 86 new), and `evidence/check-pre-fix.txt` (rule 3 FAIL; rule 2 PASS). The test-first patch record is `evidence/regression-failing.txt` and `evidence/state-patch.diff`; the post-patch runs and checker output are recorded in `TRACE.md`, `REVIEW.md`, and `evidence/check-post-patch.txt`.

The ordinary run including `gh-broken` must remain `incomplete`. An empty board is **not** the finished-wrong demo because the loop already classifies it as unverified.

## Wrong implementations the tests must reject

1. Host check by `endsWith` or `includes` accepts `boards-api.greenhouse.io.evil.example`.
2. Path check by a raw `startsWith(out)` accepts the sibling `out-evil/`.
3. String normalization without `realpath` lets `out/link` point outside the allowed write tree.
4. Allow-listed host but unchecked method/path permits a POST to an application endpoint.
5. `fetch` defaults to following an off-list redirect.
6. An empty/failed board is mislabeled `0 new jobs`, or wipes prior state.
7. A 404 is retried, or retries have no cap.
8. A budget is checked **after** the next request.
9. A run is called `finished` despite the deliberate broken board.
10. Lever UUID IDs are cast to numbers, yielding `[null]` and repeated false “new” jobs.
11. A duplicate configured board is fetched twice.
12. A JS1 judge subprocess can still run despite the JS2 `--judge none` restriction.
13. A token is interpolated without validation, allowing encoded path traversal/extra segments.
14. An HTTP 429 is blindly retried without honoring `Retry-After`.
15. A CLI flag raises a hard budget beyond the documented maximum.
16. `check.mjs` trusts the loop's report as its source of truth instead of raw data and preserved state snapshots.
17. An ordinary reduction in live postings incorrectly shrinks the cumulative seen-ID state.
18. An approval flag for one file silently authorizes a second file or second guarded mutation.
19. A request begun near the 60-second deadline uses the full 15-second timeout.
20. `--replay` accepts an arbitrary file outside `out/raw/`, follows an escaping symlink, or falls back to network when the raw fixture is missing.

## Verification cases to run and record

| Case | Expected observation | Evidence to save |
|---|---|---|
| Normal four-board traversal | Three real-board observations; deliberate 404; overall `incomplete`, exit `10` if no higher-priority issue | Raw responses, trace, failure counter, terminal output |
| `--max-requests 2` | `budget-exhausted`, exit `11`; unattempted boards listed; at most two HTTP attempts | CLI output, trace with request count |
| `--max-requests 20` | CLI/config rejected before networking; `error`, exit `12` | Error message, zero-request trace/test |
| Repeat board in test config | One request for the duplicate board; `skipped: duplicate` logged | Trace and repeat-policy test |
| Stubbed 429, `Retry-After: 30` | `rate-limited`, no retry | Response fixture + test log |
| Stubbed 429, `Retry-After: 2` | At most one retry if enough time/requests remain | Response fixture + budget counters |
| Deadline-aligned mock fetch | Timeout capped to remaining wall-clock; no overrun-inducing second action | Fake clock / abort test output |
| Controlled pre-fix Lever baseline + replay | Baseline on fresh state: **86 new**, correctly, but state saved as `[null]`; after an intervening normal run left `[0, null]`, a labeled offline `--replay` of the same 86-job fixture falsely reports **86 new** again and exits `finished`. `check.mjs` **fails rule 3**, even though rule 2 agrees with corrupted pre-run state | `215021538Z` baseline, `215039330Z` intervening live run, `215313703Z` replay trace; saved raw JSON; `evidence/check-pre-fix.txt`; test-first regression and diff |
| Replay-mode path and network policy | Fixture under `out/raw/` is accepted with zero HTTP requests; `../` or symlink escape and missing fixture are rejected without fetching | CLI output, trace, file-policy unit tests and network-call counter |

The table preserves the expected outcomes for the contract. Executed results are in `test/boundary-cases.md` (43 rows with test references), `TRACE.md`, `REVIEW.md`, and `evidence/`. The final Node test-suite record is `evidence/node-test-final.txt` (**123 passed out of 123**, following commits `42c9bc52` and `ea5e0198`); earlier logs remain as historical test-first evidence.

## Decisions

- **2026-11-10:** Keep hard budgets at 5 boards, 8 HTTP attempts, 60 seconds, and a 15-second **maximum** attempt timeout. Four configured boards leave room for bounded retries without a budget increase.
- **2026-11-10:** Disable the JS1 external judge in JS2 because its CLI subprocess bypasses the network policy; deterministic gating only, `--judge none`.
- **2026-11-10:** Make seen-ID state append-only; an observed removal is not permission to forget an ID.
- **2026-11-10:** Treat both forms of empty response as unverified and `incomplete`; keep the Lever UUID defect as the independently detectable finished-wrong-answer demonstration.
- **2026-11-10:** Use case-insensitive DNS hostname normalization followed by an exact allow-list match; reject trailing-dot hostnames and non-default ports.
- **2026-11-10:** Require a single-use `--approve <path>` for guarded in-scope mutation; reject budget-raising CLI arguments.
- **2026-11-10:** Honor bounded `Retry-After` values on 429, cap per-attempt timeout at remaining wall time, and persist consecutive attempted-run failures in `out/failures.json`.
- **2026-11-10:** Define `--replay <path>` as offline, single-board raw-response processing limited to canonical paths under `out/raw/`; never fall back to a network request. Rule 3, not rule 2 alone, detects the corrupted pre-run Lever state.
- **2026-11-10 (after first live runs):** A `--replay` run is not an attempted run; it leaves `out/failures.json` unchanged. Recorded after its code commit e871e90d.
- **2026-11-10 (after first live runs):** Patched `src/state.mjs` normalizes legacy numeric Greenhouse ids to decimal strings on load (migration). Invalid Lever ids in persisted state (`null`, `0`, any non-UUID) are an integrity `error`; recovery requires an approved, guarded rewrite via `--approve`.
- **2026-11-10 (after mutant check):** Boundary rows 42–43 added after mutants `wv01-host-endsWith` and `wv07-404-retried` survived; they are post-implementation tests, not original predictions.
- **2026-11-10 (before the state.mjs patch):** `src/state.mjs` derives a board's ATS from its board id prefix (`gh-` = Greenhouse, `lv-` = Lever); an unknown prefix is `STATE_INTEGRITY`. An explicit `ats` parameter would be cleaner but widens the patch beyond `state.mjs`; deferred.
- **2026-11-10 (after first patch attempt; supersedes the ATS-from-prefix Decision):** `lv-` ids must be UUID strings; `gh-` ids must be decimal strings or safe integers (normalized to decimal strings); any other board id gets generic validation: non-empty strings or safe integers normalized to decimal strings. `null`, `NaN`, non-scalars and post-normalization duplicates are `STATE_INTEGRITY` everywhere. Reason: the stricter rule broke JS1's tests for boards `fixture` and `stripe`; this keeps the patch in `src/state.mjs` with no test changes.
- **2026-11-10 (supersedes the --approve recovery clause):** The loop has no guarded rewrite path, so recovering corrupt state is a manual human step: move the file to `out/quarantine/` and commit it. The corrupt original is preserved in commit b0bc86f9. An agent-side approved rewrite is deferred.
- **2026-11-10 (before `42c9bc52`):** `src/state.mjs` could not distinguish raw-response duplicates after merging IDs with prior state. At that stage provider-level raw-ID validation was deferred. The subsequent `42c9bc52` Decision supersedes the **duplicate-ID** part of this deferral; null-ID disposition remains an interim exception.
- **2026-11-10 (clarifies the id-rule Decision above):** Post-normalization duplicates are `STATE_INTEGRITY` when a persisted state file is loaded, for every board. `saveState` still merges overlapping ids, since its input is always prior state merged with a new response. `gh-` ids must be positive safe integers or their canonical decimal strings, matching `src/check.mjs`.
- **2026-11-10 (interim, commit `377fd51c`):** A null raw ID still reaches `saveState` and ends the whole run as `error` (exit 12, with `run_end`), rather than causing a per-board `error: malformed`. **Per-board null-ID handling** remains deferred; this is specifically disclosed under SIGNOFF.md / Not checked. This no longer describes duplicate IDs, which were fixed in `42c9bc52`.
- **2026-11-10 (after `42c9bc52`):** Both Greenhouse and Lever provider parsers reject duplicate raw-response IDs, including equivalent numeric/string Greenhouse representations such as `101` and `"101"`. A duplicate produces a board-level `error: malformed` with no state update; other boards may continue, and the run ends `incomplete` (exit 10) when no higher-priority error occurs. Regression tests failed before the provider patch and passed after it. This **supersedes the duplicate-ID deferral**, not the null-ID interim exception.
- **2026-11-10 (after `ea5e0198`):** The snapshot read-only test checks that write-permission bits are absent rather than relying on a write failing under administrator privileges. The modified test was checked against a mutant without `chmodSync`; the final suite was reported as 123/123.
- **2026-11-10 (after saved-run review):** An earlier spot check recorded 84 Spotify postings, but the actual pre-fix baseline/replay fixture contains 86 and later post-patch runs contain 85. The graded finished-wrong claim is **86 new again** on replay; this is not the 84-posting spot check. Evidence: `TRACE.md`, `evidence/check-pre-fix.txt`, `evidence/check-post-patch.txt`.

Behavior is verified only by the tests, traces, and reviewed diff listed in the sign-off.
