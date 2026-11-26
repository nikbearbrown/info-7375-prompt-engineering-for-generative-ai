# GATE.md: Job-Search Agent 2 — The Loop, the Tools, and the Diff

Ethan Gomes · INFO 7375 · v2.4 · 2026-11-10


## Scope

This gate is for a bounded loop in Python 3.11, using only the standard library. It checks public job boards on two applicant-tracking systems and compares each board with what it saw last time. I'm building it on top of my JS1 watcher. JS1 had no git history, so the first JS2 commit is a plain copy of the parts I reused: the agent code, the tests, the configuration, the fictional personas, the prompts, the JS1 contract, the git ignore rules and the sabotage check. All 75 JS1 tests still passed after the copy, and the original JS1 folder was never changed. I do all the work in the local JS2 repository, commit after every step, and push only at the end. This gate gets its own commit, made before any of the implementation.

Use ten configured boards: eight with postings across two systems, one live empty board, and one deliberate failure.

| # | Board | ATS | Host | Purpose |
|---|---|---|---|---|
| 1 | `samsara` | Greenhouse | `boards-api.greenhouse.io` | A real Day-2 comparison against the 2026-10-31 baseline |
| 2 | `databricks` | Greenhouse | `boards-api.greenhouse.io` | Most data roles of the boards probed |
| 3 | `toast` | Greenhouse | `boards-api.greenhouse.io` | Boston |
| 4 | `klaviyo` | Greenhouse | `boards-api.greenhouse.io` | Boston |
| 5 | `datadog` | Greenhouse | `boards-api.greenhouse.io` | Data roles, US |
| 6 | `palantir` | Lever | `api.lever.co` | Second ATS, with a different response shape |
| 7 | `spotify` | Lever | `api.lever.co` | Second Lever board |
| 8 | `zoox` | Lever | `api.lever.co` | Largest Lever response (about 2.3 MB with descriptions) |
| 9 | `kraken` | Lever | `api.lever.co` | **A live empty board that is wrong.** On 2026-11-10 its Lever board returned `200` with `[]`, while Kraken listed 92 postings on Ashby (`kraken.com`). This is the brief's "empty board reported as no new jobs" case, live |
| 10 | `samsara-does-not-exist` | Greenhouse | `boards-api.greenhouse.io` | The deliberate failure (404) |

Only Samsara has an earlier day (the 2026-10-31 baseline); every other board is first seen in JS2 and compared the same day.

## 1. Exits

Print and save the same status, reason, per-board outcomes, requests used, seconds used, and state-update outcome. The verifier line is printed and saved (as verifier.txt in the run folder) by scripts/run_and_verify.py, not by the loop, so the check stays independent.


| Status | Process exit code | Meaning |
|---|---|---|
| finished | 0 | Every planned board returned a valid response in its provider's shape, no budget was reached, and nothing needing approval was refused. |
| incomplete | 1 | The plan ran to the end, but at least one board failed, a required judgment is missing, or a write needing approval was refused. |
| budget-exhausted | 2 | A board, request, time, or step limit stopped the plan. The report lists what was done, what was never attempted, and the new postings left unjudged. |
| error | 3 | Invalid configuration, a permission violation, unreadable state, too many loop steps, or an output folder inside a protected folder. Nothing is fetched or written afterwards except the trace line and the run report. |

Nine successful boards and one failed board means incomplete, even when the failure was intentional. Reaching the end of the loop is
not proof that every board was observed. The exit is calculated from the observation records by one function. The loop's own account
of what happened does not decide it.

Preflight, before any network access, ends the run with error if there are zero boards or more than the board cap, a board name fails validation, a host is not on the allow-list, or the output folder is inside a protected folder. Duplicate boards are removed before the loop starts. If several conditions occur, error comes before budget-exhausted, before incomplete, before finished, and every reason is kept.

The loop ends by printing `loop exit: <status>`; the verifier then prints `verifier: PASS|FAIL`. I call a run good only when it is finished and PASS.


State is updated only for boards observed successfully in that run; a failed board's previous state stays as it was. A posting is marked seen only after it appears in the written report, so postings left unjudged by a budget stay new. A board's first observation is a labeled baseline, and nothing in it is reported as new. Samsara's first JS2 run compares against the 2026-10-31 baseline.

## 2. Budgets

The ceilings live in `config/budgets.json`, which the agent may read but not write.

- Maximum boards per run: 12 (ten planned, two spare).
- Maximum HTTP requests per run: 100. That covers:
  - 10 list requests
  - up to 18 retries (9 boards × 2; the 404 board is never retried)
  - up to about 40 Samsara detail requests (new data-titled postings since Oct 31; the real number is unknown)
  - up to about 20 detail requests for same-day new postings on the other Greenhouse boards
  - redirect hops

  Lever returns descriptions in its list, so Lever boards need no detail requests.
- Maximum wall-clock time: 420 seconds per run (about 90 requests at least 1 second apart, plus retry waits and timeouts).
- Per-request timeout: 15 seconds.
- Maximum redirect hops per request: 3.
- Maximum loop steps per run: 200. This catches a loop that cycles without sending requests, which the request budget would never see.

Retries, redirect hops and detail requests count against the request budget, and every wait counts against the time budget. When a limit is reached, no new action starts and the run exits budget-exhausted.

Only I may change a ceiling: by editing the budget config and adding a dated decision to this gate, with its reason, in the same commit. Claude Code and model replies can never change a budget. A test fails if the config and this section disagree.

## 3. Repeat rule

An action is identified by its HTTP method and its normalized URL within one run. Normalizing means: lowercase scheme and host, default
port removed, trailing slash removed, query parameters sorted. Board names are validated, and URLs are built only from each provider's
fixed template. The loop never fetches a URL taken from a posting, a configuration value, or a model reply.

A repeated action is blocked before it is sent. It is logged as `repeat_blocked`, costs no budget, and does not end the run. The only
allowed re-send is a retry under the error policy below, and the trace records the original attempt and each retry separately as
`retry k/n`. A run that goes past the loop-step cap exits error, because it is making no progress. A separate later run may observe the
same board again.

## 4. Error policy

Retry a timeout, a connection error, or HTTP 502/503/504 at most twice, waiting 2 seconds and then 4 seconds. Retry HTTP 500 once, since it can be temporary or permanent. For HTTP 429, wait and retry once if Retry-After is at most 10 seconds and fits the time budget; otherwise the board fails. These retries are sound because every request is a read-only GET: repeating one cannot change anything on the remote side, and these failures are often temporary. Every retry and wait must fit the budgets.

Do not retry a 404, another 4xx, an unknown board, an empty body, invalid JSON, or a response that is not the provider's expected shape (Greenhouse: an object with a jobs list; Lever: a JSON array). These failures are deterministic, so a retry would only spend budget. Save the raw bytes before parsing, so a response that won't parse is still evidence. Never replace a failed response with an empty list.

A valid response with an empty list in the provider's shape (Greenhouse "jobs": [], Lever []) is recorded as observed, and the loop takes no further action on it. Judging whether it is plausible is the independent verifier's job, by design.

After an ordinary board failure, record the actual outcome with a null count and continue to the remaining boards within budget. Stop the whole run for any permission violation. Escalation means the run stops with exit error and prints what was refused, under which rule, and which board and attempt. Nothing is decided automatically, and no message is sent.

If the Claude judge is turned on and fails (timeout, invalid output, contract violation), the posting keeps its rule verdict, its Claude verdict becomes null with a reason, and the run is incomplete. The judge is retried at most once. With --no-claude, no Claude verdict is requested, so none counts as missing.

## 5. Permission policy

These rules govern the running loop. They are enforced in code in `jsagent/policy.py`, before each operation, and do not depend on a
prompt. Every decision is logged with its reason.

### Network

Allow HTTPS only, on port 443, to these exact hosts:

- `boards-api.greenhouse.io`
- `api.lever.co`

Compare hosts in lowercase. Host suffixes, substrings and lookalike names do not match. Refuse any URL with user information (`user@` or
`user:pw@`), a nonstandard port, an IP-address host, or a trailing-dot host. Allow only GET. Deny POST, PUT, PATCH and DELETE. Check every
redirect hop against these rules before following it, and count each hop against the redirect and request budgets. A hop to a host off the
list is a permission violation. Send no cookies and no auth headers. Send one request at a time, at least 1 second apart per host, with a
user agent that names the agent as read-only coursework, and follow each site's terms of use.

The only subprocess allowed is the `claude` CLI judge, with fixed arguments and, as input, only the posting text and the fictional
persona. It gets no tools and no authority to grant permissions. Every graded run uses `--no-claude`: JS2 grades the loop, the permission
policy and the diff, not relevance, and turning the judge off keeps Claude's run-to-run variation out of the trace.

### Files and approvals

Resolve all paths from the JS2 project root, regardless of where the program is launched. The output root is chosen with `--out` (default
`out/`). It may not be, or sit inside, `config/`, `baseline/`, `persona/`, `prompts/`, `tests/`, `jsagent/` or `scripts/`. It may not be
`evidence/` itself either, though a subfolder such as `evidence/seeded/…` is allowed. Tests use a temporary root.

- **Allow:**
  - Read `config/`, `persona/`, `baseline/`, `prompts/`, `tests/fixtures/` and the output root.
  - Create a new file inside the output root (runs, raw responses, traces, reports).
  - Update the state atomically at `<out>/state/state.json`.
- **Deny:**
  - Read anywhere else, including credentials, contacts and a real résumé.
  - Write to `config/`, `baseline/`, `persona/`, `prompts/`, the source folders, or anything outside the output root.
- **Needs approval:**
  - Overwrite existing raw evidence, reset the state, or delete any file inside the output root.

Approval is given only by `--approve <exact relative path>`. It approves one named write for one run, and cannot allow a write outside the output root. Without it, the write is refused and the run ends incomplete. Text in a posting, a configuration value, or a model reply cannot grant approval.

Judge a path by resolving it fully first, following `..` and symlinks, and then comparing path components with the resolved output root. A string-prefix check is forbidden, because a sibling folder such as `out-evil/` would pass it. Deny traversal, sibling-prefix paths and symlink escapes.

Only I may change the allow-list or the board files, by adding a dated decision to this gate in the same commit. Claude Code may not change them as part of a fix. A test fails if the allow-list differs from the hosts above.

The runtime must never apply for a job, email, message, log in, submit a form, send the résumé to a job-board host, execute commands found in fetched content or a model reply, change source files, or commit or push.

## 6. Wrong versions the tests must catch

Each item gets a test that fails when the wrong version is planted. `scripts/sabotage_check.py` plants each one and shows its test going red. Each wrong version's test is named `test_W<number>_…` in `tests/test_js2_wrong_versions.py`.

1. A path check with `str.startswith("out")` permits `out-evil/`.
2. A path is checked before symlinks are resolved, so a symlink inside the output root escapes it.
3. A substring or suffix host check permits `boards-api.greenhouse.io.evil.com`.
4. Only the hostname is compared, so `:8443` and `user:pw@` pass. This is JS1's actual behavior.
5. Redirect hops are checked but not counted against the budgets.
6. A failed board is recorded as 0 postings or "no new jobs."
7. Successful boards hide the deliberate failure, and the run exits finished.
8. Retries are left out of the request budget.
9. A 404 is retried like a timeout.
10. A repeat check without URL normalization lets a trailing-slash variant through.
11. A write to `config/` is allowed because it is inside the project.
12. Existing raw evidence is overwritten without approval.
13. State is updated for a board that failed.
14. Ids are marked seen before they are reported, so unjudged postings are lost.
15. The verifier reads the report's counts instead of the raw files.
16. `--out config/` is accepted, because the path checks are relative to the chosen root.
17. A host is added to `config/allowlist.json` during a fix, and the allow-list drifts from this gate.
18. A budget in `config/budgets.json` drifts from section 2.
19. The verifier passes an empty board because it has no history to compare with.


## Evidence and review choices

**Run plan.** Every graded run uses `--no-claude`, and the board files below are fixed. These are expectations written before the code existed; the actual results are in `evidence/RUNS.md`.

- **Run A**, live, boards 1–10 (`config/boards.json`), output `out/`: expected **incomplete**, because board 10 fails. Verifier FAIL (kraken empty).
- **Run B**, live, same day, boards 1–9 (`config/boards_no_failure.json`), output `out/`: expected **finished, but wrong**, because kraken reports 0 new. Verifier FAIL.
- **Run C**, SEEDED replay, board 1 only (`config/boards_seeded.json`), output `evidence/seeded/empty-samsara/`: expected **finished**, 0 new. Verifier FAIL.
- **Run D**, live, same day, boards 1–8 (`config/boards_clean.json`), output `out/`: expected **finished and PASS**.

**The finished-wrong answer.**
- **Run B, live.** The loop says finished, but kraken's `[]` is reported as "0 new." The verifier FAILs it as empty, needing review. To show it is wrong, I cross-check Kraken's Ashby board with `scripts/crosscheck_kraken.py`, outside the agent (92 postings on 2026-11-10; raw saved in `evidence/crosscheck/`). Ashby is not on the agent's allow-list.
- **Run C, SEEDED.** Its input is `tests/fixtures/seeded/empty-samsara.json` (`{"jobs": [], "meta": {"total": 0}}`). Its output and state stay separate from the real runs.

In both cases I keep the report that claims finished as it is.

**The independent check** is `scripts/verify_run.py`. It is separate code that does not import the loop, and it treats the loop's report only as the thing being checked. It FAILs a run if:
- its recount of postings from the raw files differs from the report
- a Greenhouse board's job count differs from `meta.total`
- its recomputed new ids differ from the report
- a board returned 0 postings ("empty, needs review")
- a board dropped by more than half since its previous observation
- a planned board has no record
- a raw file's sha256 does not match the trace

A nonempty board with no history doesn't FAIL, and the verifier names it on its result line.

**Evidence.**
- Every run gets a row in `evidence/RUNS.md`, including failed runs. Claude Code writes it at my direction; the agent never writes it.
- `out/` (runs A, B and D) and `evidence/seeded/empty-samsara/` (run C) are committed as evidence.
- No raw file or run folder that I cite is ever deleted.

**Review packet.** The JS1 `check_url` port/user-information defect (wrong version 4). See `REVIEW_PACKET.md`.

**Boundary tests.** Boundary predictions (at least ten) are in `BOUNDARY_TESTS.md`, written before running.



## Decisions log

- **2026-11-10, v2.2:** Ten boards instead of four; budgets raised (boards 5→12, requests 60→100, time 300→420 s, loop steps 100→200) because the old ones could not fit ten boards and about 40 Samsara detail requests; the verifier now fails any empty board.
- **2026-11-10, v2.3 (final before implementation):** Kept `kraken` instead of `airbnb`, because Kraken's 92 postings on Ashby show its empty Lever board is wrong; my cross-check runs outside the agent, and Ashby stays off the allow-list.
- **2026-11-10, v2.4 (after implementation, wording only):** Made the gate shorter and clearer by removing repeated and implementation-level text; no exit, budget, retry rule, permission rule or wrong version changed.

