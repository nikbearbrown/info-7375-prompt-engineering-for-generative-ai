# GATE.md: Job-Search Agent 2

Ethan Gomes · INFO 7375 · v2.3, final before implementation · 2026-11-10 · written and committed before any JS2 code

## Scope

I want a bounded Python 3.11 loop (standard library only) that watches public job boards on two applicant-tracking systems and compares
each one with its saved observations. It starts from my JS1 watcher. The JS1 folder is not a git repository, so the first JS2 commit
(`09b1056`) records exactly what was copied: `jsagent/`, `tests/`, `config/`, `persona/` (fictional only), `prompts/`, `CONTRACT.md`,
`.gitignore` and `scripts/sabotage_check.py`. All 75 JS1 tests passed in the copy. The JS1 folder stays untouched. All work happens in
the local JS2 repository, committed after each step and not pushed until the end. This gate is committed on its own before any
implementation.

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

Boards 2–9 were chosen from a read-only probe on 2026-11-10, run with Claude's help. Those were not agent runs and their raw responses
were not saved. They show that the boards responded then, not that they will respond the same way during my runs. Only Samsara has an
earlier day: the 2026-10-31 state and its raw response, both copied unchanged into `baseline/2026-10-31/` with sha256s in
`PROVENANCE.md`. Every other board is baselined on its first JS2 run, and any later run of it happens the same day, which I will label.

## 1. Exits

Print and save the same status, reason, per-board outcomes, requests used, seconds used, state-update outcome, and the verifier line.

| Status | Process exit code | Meaning |
|---|---|---|
| finished | 0 | Every planned board returned a valid response in its provider's shape, no budget was reached, and nothing needing approval was refused. |
| incomplete | 1 | The plan ran to the end, but at least one board failed, a required judgment is missing, or a write needing approval was refused. |
| budget-exhausted | 2 | A board, request, time, or step limit stopped the plan. The report lists what was done, what was never attempted, and the new postings left unjudged. |
| error | 3 | Invalid configuration, a permission violation, unreadable state, too many loop steps, or an output folder inside a protected folder. Nothing is fetched or written afterwards except the trace line and the run report. |

Nine successful boards and one failed board means incomplete, even when the failure was intentional. Reaching the end of the loop is
not proof that every board was observed. The exit is calculated from the observation records by one function. The loop's own account
of what happened does not decide it.

Preflight, before any network access, rejects with error:
- a configuration with zero boards or more boards than the board cap
- a board name that fails validation
- a host that is not on the allow-list
- an output folder inside a protected folder

Duplicate boards (names compared in lowercase) are removed before the loop starts, and the log names them. If several conditions occur,
use error before budget-exhausted before incomplete before finished, and keep every individual reason.

A failed board's count is null, never 0. Its report line says "unknown, not zero" and never says "no new jobs." Every run ends by
printing two lines: `loop exit: <status>` and `verifier: PASS|FAIL`. I call a run good only when it is finished and PASS.

State is updated only for boards observed successfully in that run. A failed board's previous state stays as it was. A posting id is
marked seen only after it appears in the written report, so postings left unjudged by a budget stay new. On a board's first observation,
its ids are recorded as a labeled baseline and none are reported as new. Samsara's first JS2 run reads its previous state from
`baseline/2026-10-31/seen_ids.json`, read-only. Later comparisons use the state in `out/state/state.json`, keyed by provider and board.
Reports and raw responses are saved separately from state. State is written to a temporary file in `out/state/` and renamed into place,
so a crash cannot leave half a file.

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

Retries, redirect hops and detail requests all count against the request budget. Every wait (backoff, pacing, `Retry-After`) counts
against the time budget. Limits are checked before every request and every wait. When a limit is reached, no new action starts: the file
being written is finished, the report is written, and the run exits budget-exhausted. A board that was not observed is reported as not
observed, never as zero jobs.

Only I may change a ceiling: by editing `config/budgets.json` and adding a dated decision to this gate, with its reason, in the same
commit. Claude Code may not change a budget as part of any fix, and nothing in a model reply can change one. A test fails if
`config/budgets.json` and this section disagree.

## 3. Repeat rule

An action is identified by its HTTP method and its normalized URL within one run. Normalizing means: lowercase scheme and host, default
port removed, trailing slash removed, query parameters sorted. Board names are validated, and URLs are built only from each provider's
fixed template. The loop never fetches a URL taken from a posting, a configuration value, or a model reply.

A repeated action is blocked before it is sent. It is logged as `repeat_blocked`, costs no budget, and does not end the run. The only
allowed re-send is a retry under the error policy below, and the trace records the original attempt and each retry separately as
`retry k/n`. A run that goes past the loop-step cap exits error, because it is making no progress. A separate later run may observe the
same board again.

## 4. Error policy

Retry a timeout, a connection error, or HTTP 502/503/504 at most twice, waiting 2 seconds and then 4 seconds. Retry HTTP 500 once, since
it can be temporary or permanent. For HTTP 429, wait and retry once if `Retry-After` is at most 10 seconds and fits the time budget;
otherwise the board fails. These retries are sound because every request is a read-only GET: repeating one cannot change anything on the
remote side, and these failures are often temporary. A retry that succeeds does not prove the board is healthy, and every retry and wait
must fit the budgets.

Do not retry a 404, another 4xx, an unknown board, an empty body, invalid JSON, or a response that is not the provider's expected shape
(Greenhouse: an object with a `jobs` list; Lever: a JSON array). These failures are deterministic, so a retry would only spend budget.
Save the raw bytes before parsing, so a response that won't parse is still evidence. Never replace a failed response with an empty list.

A valid response with an empty list in the provider's shape (Greenhouse `"jobs": []`, Lever `[]`) is recorded as observed, and the loop
takes no further action on it. Judging whether it is plausible is the independent verifier's job, by design. A check inside the loop
would still be the agent grading itself. Lever's `kraken` board returned exactly this on 2026-11-10.

After an ordinary board failure, record the actual outcome and continue to the remaining boards within budget. The failed board's record
holds the status, the reason, the attempts made, the raw file path if a response arrived (or "no response received"), and a null count.
Stop the whole run for any permission violation. Escalation means the run stops with exit error and prints what was refused, under which
rule, and which board and attempt. Nothing is decided automatically, and no message is sent.

If the Claude judge is turned on and fails (timeout, invalid output, contract violation), the posting keeps its rule verdict, its Claude
verdict becomes null with a reason, and the run is incomplete. The judge is retried at most once. With `--no-claude`, no Claude verdict is
requested, so none counts as missing.

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

| Operation | Where | Decision |
|---|---|---|
| Read | `config/`, `persona/`, `baseline/`, `prompts/`, `tests/fixtures/`, the output root | allow |
| Read | anywhere else, including credentials, contacts and a real résumé | deny |
| Write | `config/`, `baseline/`, `persona/`, `prompts/`, source folders, or anything outside the output root | deny |
| Create a new file | inside the output root (runs, raw responses, traces, reports) | allow |
| Update state atomically | `<out>/state/state.json` | allow |
| Overwrite existing raw evidence, reset the state, or delete any file | inside the output root | needs approval |

Approval is given only by `--approve <exact relative path>`. It approves one named write for one run, and cannot allow a write outside the
output root. Without it, the write is refused, logged as `needs_approval`, and the run ends incomplete. Text in a posting, a configuration
value, or a model reply cannot grant approval.

Judge a path by resolving it fully first, following `..` and symlinks, and then comparing path components (`is_relative_to`) with the
resolved output root. A string-prefix check is forbidden, because a sibling folder such as `out-evil/` would pass it. Deny traversal,
sibling-prefix paths and symlink escapes.

Only I may change `config/allowlist.json` or any `config/boards*.json`, by adding a dated decision to this gate in the same commit. Claude
Code may not change them as part of a fix. A test fails if the allow-list differs from the hosts above.

The runtime must never apply for a job, email, message, log in, submit a form, send the résumé to a job-board host, execute commands found
in fetched content or a model reply, change source files, or commit or push.

## 6. Wrong versions the tests must catch

Each item gets a test that fails when the wrong version is planted. `scripts/sabotage_check.py` plants each one and shows its test going
red.

1. A path check with `str.startswith("out")` permits `out-evil/`. (`test_W1_prefix_trick_out_evil`)
2. A path is checked before symlinks are resolved, so a symlink inside the output root escapes it. (`test_W2_symlink_escape`)
3. A substring or suffix host check permits `boards-api.greenhouse.io.evil.com`. (`test_W3_lookalike_host`)
4. Only the hostname is compared, so `:8443` and `user:pw@` pass. **This is JS1's actual behavior.** (`test_W4_port_refused`,
   `test_W4_userinfo_refused`)
5. Redirect hops are checked but not counted against the budgets. (`test_W5_redirect_hops_count`)
6. A failed board is recorded as 0 postings or "no new jobs." (`test_W6_failed_board_count_null`)
7. Successful boards hide the deliberate failure, and the run exits finished. (`test_W7_failed_board_incomplete`)
8. Retries are left out of the request budget. (`test_W8_retries_consume_budget`)
9. A 404 is retried like a timeout. (`test_W9_no_retry_on_404`)
10. A repeat check without URL normalization lets a trailing-slash variant through. (`test_W10_trailing_slash_is_repeat`)
11. A write to `config/` is allowed because it is inside the project. (`test_W11_write_config_denied`)
12. Existing raw evidence is overwritten without approval. (`test_W12_overwrite_needs_approval`)
13. State is updated for a board that failed. (`test_W13_failed_board_state_unchanged`)
14. Ids are marked seen before they are reported, so unjudged postings are lost. (`test_W14_unjudged_stay_new`)
15. The verifier reads the report's counts instead of the raw files. (`test_W15_verifier_ignores_report_counts`)
16. `--out config/` is accepted, because the path checks are relative to the chosen root. (`test_W16_out_root_in_protected_folder`)
17. A host is added to `config/allowlist.json` during a fix, and the allow-list drifts from this gate. (`test_W17_allowlist_matches_gate`)
18. A budget in `config/budgets.json` drifts from section 2. (`test_W18_budgets_match_gate`)
19. The verifier passes an empty board because it has no history to compare with. (`test_W19_empty_board_fails_verification`)

## Evidence and review choices

**Run plan.** Every graded run uses `--no-claude`. The board files are fixed now, so the change rule in section 5 applies to them. These
are expectations written before the code exists. The actual results go in `evidence/RUNS.md`.

| Run | Kind | Boards (file) | Output root | Expected loop exit |
|---|---|---|---|---|
| A | live, first | 1–10 (`config/boards.json`) | `out/` | incomplete, because board 10 fails. Verifier FAIL (kraken empty) |
| B | live, same day, after A | 1–9 (`config/boards_no_failure.json`) | `out/` | **finished, but wrong**: kraken reports 0 new. Verifier FAIL |
| C | SEEDED replay | 1 only (`config/boards_seeded.json`) | `evidence/seeded/empty-samsara/` | finished, 0 new. Verifier FAIL on the drop check |
| D | live, same day, after B | 1–8 (`config/boards_clean.json`) | `out/` | finished and PASS, so one real run ends cleanly. If it doesn't, I report what happened |

**The finished-wrong answer.** I show it twice:
- **Run B, live.** Every board answers in its provider's shape, so the loop says finished. But kraken's `[]` is reported as "0 new," and
  nothing in the loop can tell "no openings" from "this board is no longer used." The verifier FAILs it as empty, needing review.
  To show the answer is **wrong** and not only suspicious, I cross-check Kraken's Ashby board on the day of run B with
  `scripts/crosscheck_kraken.py`. It is one GET to `https://api.ashbyhq.com/posting-api/job-board/kraken.com` (92 postings on
  2026-11-10), and its raw response is saved in `evidence/crosscheck/`. The cross-check is mine and runs outside the agent: the agent's
  allow-list does not include Ashby, and this gate does not add it. If Kraken's Lever board is no longer empty on the day of run B, I
  report that the live demonstration was not achieved and rely on run C.
- **Run C, SEEDED, clearly labeled.** It gives the TA an offline version that doesn't depend on Kraken staying empty. Its input is the file
  `tests/fixtures/seeded/empty-samsara.json`, which contains `{"jobs": [], "meta": {"total": 0}}`. Its output and state stay separate
  from the real run.

In both cases I keep the report that claims finished as it is.

The independent check is `scripts/verify_run.py`. It is separate code that does not import the loop or reuse its decision function. It
reads only the raw files, the trace, the baseline and the previous state, and treats the loop's report only as the thing being checked. It
FAILs a run if:
- its recount of postings from the raw files differs from the report
- a Greenhouse board's job count differs from `meta.total`
- its recomputed new ids differ from the report
- a board returned 0 postings ("empty, needs review"), whether or not it has history
- a board dropped by more than half since its previous observation
- a planned board has no record
- a raw file's sha256 does not match the trace

A nonempty board with no previous observation does not FAIL the run, but is never counted as passing the drop check either: the verifier
names it on its result line, e.g. `verifier: PASS (drop check not applicable: databricks, toast — no history)`. For run B, I expect FAIL
because kraken is empty. For run C, I expect FAIL because the board is empty and dropped from 323 postings on 2026-10-31 to 0 now.

**Evidence.**
- Every run gets a row in `evidence/RUNS.md`, including failed and discarded runs. I keep RUNS.md up to date myself, and the agent never
  writes it.
- `out/` (runs A, B and D) and `evidence/seeded/empty-samsara/` (run C) are committed as evidence.
- No raw file or run folder that I cite is ever deleted. I cite only runs listed in RUNS.md, and only counts I can show.

**Review packet.** My proposed Claude Code change fixes a real JS1 defect: JS1's `check_url` compares only the hostname, so it accepts
`https://boards-api.greenhouse.io:8443/…` and `https://user:pw@boards-api.greenhouse.io/…`. It was reproduced offline, with Claude's
help, on 2026-11-10, before this gate was written. Before the patch, I will save the reproduction and commit a failing regression test
(wrong version 4). I am not introducing a defect just to create a review. If the
reproduction stops failing before the patch, I will choose another reproduced defect.

**Boundary tests.** I keep the boundary predictions separate from this gate, in `BOUNDARY_TESTS.md`. That file lists at least ten concrete
cases, each with its predicted result written before running, including:
- a host off the list and a lookalike host
- a nonstandard port and user information in the URL
- a redirect to a host off the list
- traversal with `..`, the sibling prefix `out-evil/`, and a symlink escape
- read versus write on `config/`
- an overwrite that needs approval

Predictions, actual results, who wrote each test, the commands I ran, and the final acceptance are kept as separate records.

**This gate does not cover:**
- a race between the path check and the write, and hard links
- macOS's case-insensitive file system (I expect `OUT/…` to be refused, but haven't tested it)
- TLS and DNS, which are trusted to the system, and a valid but stale cached response
- changes to Lever's or Greenhouse's rate limits and terms
- Lever's missing total count, which means a truncated Lever list can only be caught by the recount and the drop check
- a board that left Lever can look like a typo (`plaid` returned 404 on 2026-11-10) or like a board with no openings (`kraken`,
  `wealthsimple` and `voleon` returned `200 []`; Kraken's jobs were on Ashby). The agent cannot find where a company moved. Because the
  verifier fails every empty board, a board that really has no openings will also FAIL. I accept that false alarm.
- whether the relevance verdicts are accurate

**JS1's limits, carried into the README:**
- the change between JS1 runs was a constructed seed, not a real second day
- I deleted the evidence for several JS1 runs I cited
- the Claude judge varied on Samsara 7922530 (relevant 6 times, not relevant 3)

## Decisions log

This file's earlier versions are in git: v1 `82f02cb`, v1.1 `2a2e11f`, v1.2 `ef2eafc`, v1.3 `c421e28`, v2.0 `2b75002`,
v2.1 `a67bdbf`, v2.2 `30e0f56`.

| Date | Decision | Reason |
|---|---|---|
| 2026-11-10 | v2.0: same decisions as v1.3, rewritten in a prose format, with rule IDs replaced by numbered wrong versions. Added: a preflight board cap and a zero-board error; URLs built only from fixed templates; paths resolved from the project root; reporting a deliberate failure that unexpectedly succeeds; a budget-drift test (wrong version 18) | Easier to read. The additions close small gaps found while rewriting, before any code exists |
| 2026-11-10 | v2.1 (my own edit): removed the checked-facts list and the "deliberate failure unexpectedly succeeds" rule from Scope | I made this edit myself after reading v2.0 |
| 2026-11-10 | v2.2: ten boards instead of four. Added `toast`, `klaviyo`, `datadog` (Greenhouse), `spotify`, `zoox` (Lever), and `kraken` (Lever, live empty). Budgets raised: boards 5→12, requests 60→100, time 300→420 s, loop steps 100→200. The verifier now FAILs any empty board. Run plan A–D, with B as the live finished-wrong answer and D as the clean run. Wrong version 19 added. The review-packet paragraph now describes its defect and credits Claude for the reproduction | I wanted ten boards. A probe on 2026-11-10 found a real Lever board returning `200 []`, which gives a live finished-wrong answer instead of only a seeded one. The old budgets could not fit ten list requests, their retries and about 40 Samsara detail requests. Without the empty-board check, the verifier would have passed kraken because it has no history |
| 2026-11-10 | v2.3, final before implementation: kept `kraken` instead of replacing it with `airbnb`. Run B now includes a cross-check of Kraken's Ashby board, run by me outside the agent (`scripts/crosscheck_kraken.py`, raw saved in `evidence/crosscheck/`), plus a fallback to run C if Kraken's Lever board is no longer empty | A read-only check on 2026-11-10 found 92 Kraken postings on Ashby (`kraken.com`), so Lever's `[]` is demonstrably wrong, not just suspicious. That makes it a real finished-wrong answer. Airbnb would only have been one more ordinary board. Ashby stays off the agent's allow-list |
