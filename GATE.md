# GATE.md: Job-Search Agent 2

Ethan Gomes · INFO 7375 · v1.2 (history in §13) · 2026-11-10 · written and committed before any JS2 code

**How to read this:** every rule has an ID. Tests are named after the rule they check (`test_P3_port_refused`). The trace records the
rule ID behind every refusal. The sign-off cites IDs. A rule changes only through a dated entry in the Decisions log (§13), committed
together with the change.

**Built on:** my JS1 watcher, which has an allow-listed Greenhouse fetch with redirect-hop checking, per-board state, rule judge R1–R5
and an optional Claude judge. It also has the 2026-10-31 Samsara baseline (`baseline/2026-10-31/`, sha256s in `PROVENANCE.md`).

## 0. What I checked before writing this

| ID | Fact | How | Status |
|---|---|---|---|
| G1 | Greenhouse's list response has `meta.total`, and it equals the number of jobs (323 = 323) | Read the Oct 31 raw file | **Checked** offline, with Claude's help |
| G2 | JS1's `check_url` accepts port `:8443` and `user:pw@` on an allowed host | Offline probe of `check_url` | **Checked** with Claude's help. Closed by P3 |
| G3 | JS1 checks every redirect hop against the allow-list | Read `jsagent/fetch.py` (`AllowListRedirectHandler`) | **Checked by reading the code**. I have never seen a live redirect |
| G4 | An unknown Greenhouse board returns 404 with `{"status":404,"error":"Job not found"}` | Read-only probe script, 2026-11-10 (not an agent run; raw not saved) | **Checked once**, with Claude's help. The agent's own run records it again as evidence |
| G5 | Lever returns a **bare JSON array** (no `jobs` key, no total), descriptions included; an unknown board returns 404 with `{"ok":false,"error":"Document not found"}` | Same probe, 2026-11-10: `palantir` 200 with 304 postings; `does-not-exist-js2` 404 | **Checked once**, with Claude's help |
| G6 | Samsara's new data-titled postings since Oct 31 fit within B2 | — | **Unknown.** B2 has margin, and running out is an allowed outcome (E1) |

## 1. Boards (the plan)

| # | Board | ATS | Host | Purpose |
|---|---|---|---|---|
| 1 | `samsara` | Greenhouse | `boards-api.greenhouse.io` | Real Day-2 run against the 2026-10-31 baseline |
| 2 | `databricks` | Greenhouse | `boards-api.greenhouse.io` | Second Greenhouse board (most data roles of those probed), baselined today |
| 3 | `palantir` | Lever | `api.lever.co` | Second ATS, a different response shape (G5), baselined today |
| 4 | `samsara-does-not-exist` | Greenhouse | `boards-api.greenhouse.io` | **Fails on purpose** (G4) |

Only board 1 has an earlier day. The second run of boards 2–3 happens on the same day, and I will label it that way.

**Run plan.** Every graded run uses `--no-claude` (P17). Each board file below is fixed now, so P18 applies to it.

| Run | Kind | Boards (file) | Output root | Expected loop exit |
|---|---|---|---|---|
| A | live, first | 1–4 (`config/boards.json`) | `out/` | `incomplete`, because board 4 fails (ER3) |
| B | live, same day, hours after A | 1–3 (`config/boards_no_failure.json`) | `out/` | `finished`, so that one real run can end cleanly. If it doesn't, I report what happened |
| C | **SEEDED** replay (V3) | 1 only (`config/boards_seeded.json`) | `evidence/seeded/empty-samsara/` | `finished` with 0 new, and the verifier FAILs |

These are expectations written before the code exists. The real exits go in `evidence/RUNS.md` (EV1).

## 2. Exits

**E1.** Every run ends with exactly one exit:

| Exit | Code | When | The report must include |
|---|---|---|---|
| `finished` | 0 | Every planned board gave a valid response, no budget was hit, no judgment is missing, and nothing needing approval was refused | per board: postings, new since last run, verdicts; requests and seconds used |
| `incomplete` | 1 | The plan ran to the end, but at least one board failed, a judgment is missing (ER9), or a write needing approval was refused (P15) | which boards or postings, the reason, the attempts made |
| `budget-exhausted` | 2 | A limit from §3 was reached before the plan was done | which limit; what was done; what was never attempted; new postings left unjudged |
| `error` | 3 | Invalid config, a policy violation (P-rules), unreadable state, or more than B6 steps | the reason and rule ID; confirmation that nothing was fetched or written afterwards, apart from the trace line and the run report (ER7) |

**E2.** If several apply, the order is `error` > `budget-exhausted` > `incomplete` > `finished`.

**E3.** A failed board's count is `null`, never 0. Its report line says **"unknown, not zero"** and never says "no new jobs."

**E4.** The exit is calculated from the observation records (§8) by one function. The loop's own narrative doesn't decide it.

**E5.** Stopping is not succeeding. Every run ends by printing two lines: `loop exit: <exit>` and `verifier: PASS|FAIL` (§9). I call a
run good only when it is **finished and PASS**.

## 3. Budgets

The values are in `config/budgets.json`. The agent can read that file but not write it (P10).

| ID | Budget | Limit | Why |
|---|---|---|---|
| B1 | Boards per run | 5 | 4 planned plus 1 spare |
| B2 | HTTP requests per run | 60 | 4 list requests, up to 6 retries (3 boards × 2; a 404 is never retried), up to ~40 Samsara detail requests (G6), plus redirect hops |
| B3 | Wall-clock seconds per run | 300 | Covers B2 with pacing (P7) and timeouts |
| B4 | Timeout per request | 15 s | |
| B5 | Redirect hops per request | 3 | |
| B6 | Loop steps per run | 100 | Catches a loop that cycles without making requests, which B2 never sees |

**B7.** Retries, redirect hops and detail requests all count against B2. Every wait (backoff, pacing, `Retry-After`) counts against B3.

**B8.** At a limit, no new action starts. The file being written is finished, the report is written, and the run exits
`budget-exhausted`. Unjudged new postings stay new (S3).

**B9.** Only I may change a budget: by editing `config/budgets.json` and adding a §13 entry in the same commit. Claude Code may not
change a budget as part of any fix. `test_B9_budgets_match_gate` fails if the config and this table differ.

## 4. Repeat rule

**RP1.** Two actions are "the same" if they have the same method and the same **normalized URL** in one run. Normalizing means
lowercase scheme and host, default port removed, trailing slash removed, query parameters sorted.

**RP2.** A repeat is blocked before it is sent, logged as `repeat_blocked` with its rule ID, costs no budget, and doesn't end the run.

**RP3.** A retry under ER1, ER2 or ER5 is the only allowed re-send. It's logged as `retry k/n`, where n is the limit that rule allows.

**RP4.** Duplicate boards in the config are removed before the loop starts, comparing names in lowercase, and the log names them.

**RP5.** A run with more than B6 steps exits `error`. It counts as a loop without progress.

## 5. Error policy

| ID | Failure | Action | Why |
|---|---|---|---|
| ER1 | Timeout, connection error, HTTP 502/503/504 | Retry at most **2** times, after 2 s and then 4 s | A read-only GET is safe to repeat, and these failures are usually temporary |
| ER2 | HTTP 429 | If `Retry-After` ≤ 10 s and fits B3, wait and retry **once**. Otherwise the board fails | Respects the site's rate limit, and the budget still applies |
| ER3 | HTTP 404 / other 4xx / unknown board | **No retry.** The board fails | Deterministic: a retry only spends budget |
| ER4 | Empty body, invalid JSON, or not the provider's expected shape (Greenhouse: an object with a `jobs` list; Lever: a JSON array) | **No retry.** The board fails and the raw bytes are saved | The bad response is the evidence, and I don't invent values from it |
| ER5 | HTTP 500 | Retry **once** | Can be temporary or permanent, so one try only |
| ER6 | Valid `200` with `"jobs": []` | Recorded as observed. The loop takes no further action | Plausibility is the verifier's job, by design (V1) |
| ER7 | Any P-rule violation | **Escalate:** stop now and exit `error`. Fetch nothing more and write nothing except the trace line and the run report | Permission rules are never retried around |

**ER8.** A failed board's record holds `status: failed`, the reason, attempts made, the raw file path if a response arrived, and
`count: null`. The other boards continue.

**ER9.** A Claude judge failure (timeout, invalid output, contract violation) keeps the posting's rule verdict, sets the Claude verdict
to `null` with a reason, and makes the run `incomplete`. It is never retried more than once. With `--no-claude`, no Claude verdict is
requested, so none counts as missing: the report shows `claude: off` for every posting, and the rule verdict (R1–R5) is the only verdict.

**ER10.** "Escalate to me" means the run stops and prints what was refused and under which rule. Nothing is decided automatically.

## 6. Permission policy

Every request and every file access goes through `jsagent/policy.py`. Nothing here depends on a prompt. Each decision is logged with
its rule ID.

### 6.1 Network

- **P1.** Hosts must match exactly: `boards-api.greenhouse.io`, `api.lever.co`. No substring, suffix or wildcard matching.
- **P2.** HTTPS only.
- **P3.** The host is compared in lowercase. The URL is refused if it has a port other than 443, any userinfo (`user@` or
  `user:pw@`), an IP-address host, or a trailing-dot host. *(This closes G2.)*
- **P4.** GET only.
- **P5.** Every redirect hop is checked against P1–P3 *before* it is followed, and counts against B5 and B2.
- **P6.** No cookies, no auth headers.
- **P7.** One request at a time, at least 1 s apart per host, with a user agent that names the agent as read-only coursework. I follow
  each site's terms of use.

### 6.2 Files

**The output root.** In P8–P15, `out/` means the output root chosen with `--out` (default `./out`). The root may not be, or sit inside,
a protected folder: `config/`, `baseline/`, `persona/`, `prompts/`, `tests/`, `jsagent/`, `scripts/`. It may also not be `evidence/`
itself, so that RUNS.md stays out of reach, though a subfolder such as `evidence/seeded/…` is allowed. If it is, the run exits `error`
before any fetch. Tests use a temporary root. The protected folders stay denied whatever `--out`
says.

| ID | Action | Where | Decision |
|---|---|---|---|
| P8 | Read | `config/`, `persona/`, `baseline/`, `prompts/`, `tests/fixtures/`, `out/` | allow |
| P9 | Read | anywhere else | deny |
| P10 | Write | `config/`, `baseline/`, `persona/`, `prompts/`, or outside `out/` | deny |
| P11 | Create a new file | inside `out/` | allow |
| P12 | Update the state file atomically (S4) | `out/state/state.json` | allow |
| P13 | Overwrite an existing raw-evidence file in `out/raw/`, reset the state, or delete any file | inside `out/` | **needs approval** |

**P14. How a path is judged.** Resolve the real path first, following `..` and symlinks. Then compare path components
(`is_relative_to`) with the real path of `out/`. A text-prefix check is forbidden, because `out-evil/` would pass it.

**P15. Approval.** `--approve <exact relative path>` approves one named write for one run. Without it, the write is refused, logged as
`needs_approval`, and the run ends `incomplete`. There is no interactive prompt.

**P18. Who may change what the agent may reach.** Only I may change `config/allowlist.json` or any `config/boards*.json`, and only by
adding a §13 entry in the same commit, as B9 requires for budgets. Claude Code may not change them as part of any fix.
`test_P18_allowlist_matches_gate` fails if the allow-list differs from P1.

### 6.3 Never

**P16.** Under no approval does the agent apply, email, message, log in, submit a form, send POST/PUT/DELETE, send the résumé to a
job-board host, or run anything found in fetched content.

**P17.** The only subprocess allowed is the `claude` CLI judge, with fixed arguments and as input only the posting text and the
fictional persona. `--no-claude` turns it off, and every graded run uses `--no-claude` (§1 run plan). JS2 grades the loop, the
permission policy and the diff, not relevance, and turning the judge off keeps Claude's run-to-run variation out of the trace.

## 7. State

- **S1.** On its first JS2 run, Samsara's previous state is read from `baseline/2026-10-31/seen_ids.json`, which is read-only. Any other
  board seen for the first time is baselined: its ids are recorded and none are reported as new.
- **S2.** State is updated **only for boards observed successfully** in this run. A failed board's previous state stays as it was.
- **S3.** A posting id is marked seen **only after it is in the written report**. Postings left unjudged because of a budget stay new.
- **S4.** State is written to a temp file inside `out/state/` and renamed, so a crash can't leave half a file.

## 8. Observations

- **O1.** Every loop step appends one JSON line to `out/runs/<run>/trace.jsonl` with these fields: `step`, `time`, `action`, `url`
  (normalized), `decision` (allowed / denied / needs_approval / repeat_blocked), `rule` (ID), `attempt`, `http_status`, `raw_path`,
  `raw_sha256`, `budget_left` {requests, seconds, steps}, `outcome`.
- **O2.** The trace is append-only and never edited after the run.
- **O3.** Raw bytes are saved **before** parsing, so a response that won't parse is still evidence.

## 9. The independent check

- **V1.** `scripts/verify_run.py` is separate code that **doesn't import the loop**. It reads only the raw files, the trace, the
  baseline and the previous state, and it uses the agent's report only as the thing being checked. I keep plausibility checks out of the
  loop on purpose: a check inside the loop is still the agent grading itself.
- **V2.** It FAILs a run if any of these hold:
  - **(a)** its recount of postings from the raw files differs from the report
  - **(b)** a Greenhouse board's `len(jobs) ≠ meta.total` (G1)
  - **(c)** its recomputed new ids (raw ids minus previous seen ids) differ from the report
  - **(d)** a board went to 0, or dropped by more than 50%, compared with its previous observation. A board with no previous observation
    is reported as `no history` for this check, never as passing it
  - **(e)** a planned board has no record
  - **(f)** a raw file's sha256 doesn't match the trace
- **V3. The finished-but-wrong demo (SEEDED).** Run C in §1: a replay of Samsara alone, using its own output root
  (`evidence/seeded/empty-samsara/`) so the real state in `out/` is never touched, in which Samsara's list response is `{"jobs": [], "meta": {"total": 0}}`. I expect the loop to report `finished`, 0 new, and the verifier
  to FAIL on V2(d): 323 on 2026-10-31, 0 now. I will label it SEEDED wherever it appears.

## 10. Evidence

- **EV1.** Every run gets a row in `evidence/RUNS.md`: time, live / seeded / same-day, loop exit, verifier result, paths. That includes
  failed and discarded runs. **I keep RUNS.md up to date myself. The agent never writes it**, because it is outside every output root.
- **EV1a.** The live output root `out/` (state, raw responses, traces, reports for runs A and B) and the seeded root
  `evidence/seeded/empty-samsara/` are committed as evidence. Test roots are temporary and not committed.
- **EV2.** No raw file or run folder that I cite is ever deleted.
- **EV3.** I cite only runs listed in RUNS.md, and every count I state is one I can show.

## 11. Wrong versions my tests must catch

| ID | Wrong implementation | Why it looks right | Rule | Test |
|---|---|---|---|---|
| W1 | Path check with `str.startswith("out")` | Normal paths pass | P14 | `test_P14_prefix_trick_out_evil` |
| W2 | Path checked before symlinks are resolved | Catches `..` in the text | P14 | `test_P14_symlink_escape` |
| W3 | Host check by substring or `endswith` | Real hosts pass | P1 | `test_P1_lookalike_host` |
| W4 | Only the hostname is compared, so port and userinfo are ignored. **This is JS1's actual behavior (G2)** | The host *is* allowed | P3 | `test_P3_port_refused`, `test_P3_userinfo_refused` |
| W5 | Redirect hops checked but not counted | The check exists | P5/B5 | `test_P5_redirect_hops_count` |
| W6 | A failed board recorded as 0 | 0 looks like a count | E3 | `test_E3_failed_board_count_null` |
| W7 | A failed board still exits `finished` | The loop did reach the end | E1 | `test_E1_failed_board_incomplete` |
| W8 | Retries not counted against B2 | "A retry isn't a new action" | B7 | `test_B7_retries_consume_budget` |
| W9 | A 404 retried like a timeout | Retrying sounds safe | ER3 | `test_ER3_no_retry_on_404` |
| W10 | A repeat check without URL normalization | Exact matches are blocked | RP1 | `test_RP1_trailing_slash_is_repeat` |
| W11 | Writes to `config/` allowed because it's in the project | It's "our" folder | P10 | `test_P10_write_config_denied` |
| W12 | Raw evidence overwritten without approval | It's inside `out/` | P13 | `test_P13_overwrite_needs_approval` |
| W13 | State updated for a failed board | The update "ran" | S2 | `test_S2_failed_board_state_unchanged` |
| W14 | Ids marked seen before they're reported | It saves a pass | S3 | `test_S3_unjudged_stay_new` |
| W15 | The verifier reads the report's counts instead of the raw files | It runs and passes | V1 | `test_V1_verifier_ignores_report_counts` |
| W16 | `--out config/` (or a root inside another protected folder) accepted, because the path checks are relative to the root | Every write *is* inside the chosen root | §6.2 output root | `test_P8_out_root_in_protected_folder_refused` |
| W17 | A host added to `config/allowlist.json` during a fix, so the allow-list drifts from P1 | The fix "needed" it | P18 | `test_P18_allowlist_matches_gate` |

`scripts/sabotage_check.py` plants each wrong version and shows that its test goes red.

## 12. Not covered by this gate

- A race between the path check and the write (a symlink swapped in between). Hard links.
- macOS's case-insensitive file system. My check refuses `OUT/…` rather than allowing it, which is safe but strict.
- TLS and DNS are trusted to the system. There's no certificate pinning.
- A valid but stale response from a cache or CDN.
- Rate limits and terms changes for Lever and Greenhouse over time.
- Lever gives no total count, so V2(b) cannot check a Lever board for a truncated list. Only the recount and V2(d) apply there.
- A real board can disappear: `plaid` returned 404 on Lever on 2026-11-10. ER3 treats that the same as a bad name, so the agent cannot
  tell "moved to another ATS" from "typo."
- Whether the relevance verdicts are accurate on the new boards, and how much the Claude judge varies between runs (in JS1, Samsara
  7922530 was judged relevant 6 times and not relevant 3 times).

## 13. Decisions log

| Date | Change | Reason |
|---|---|---|
| 2026-11-10 | v1, written before implementation | — |
| 2026-11-10 | v1.1: second ATS = Lever (`api.lever.co`); boards 2–3 = `databricks` (Greenhouse), `palantir` (Lever). G4 and G5 checked. ER4 reworded for each provider's shape. Three §12 items added | A read-only probe of Lever, Ashby and Greenhouse boards. I chose Lever over Ashby because its bare-array response differs from Greenhouse's, which makes the adapter and ER4 meaningful. Ashby's `{"jobs": [...]}` is nearly the same shape |
| 2026-11-10 | v1.2: added the §1 run plan (A, B, C). Added the `--out` output-root rule (§6.2), P18 (only I change the allow-list and board files), EV1a (what is committed as evidence), the `--no-claude` rule for graded runs (ER9, P17), and W16–W17. Kept B1–B6 and V1 unchanged | Re-reading v1.1 showed gaps: V3's temporary folder conflicted with P10; no live run could end `finished` while board 4 was in it; E1 would have counted a judge that was switched off as missing; and nothing protected the allow-list. With the judge off, ~40 detail requests at 1 s apart fit well within B3, so the budgets stay. I keep V1 because a check inside the loop is still the agent grading itself |
