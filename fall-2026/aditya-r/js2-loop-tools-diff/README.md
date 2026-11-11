# Job-Search Agent 2 — The Loop, the Tools, and the Diff

**Student:** Aditya Raj (`aditya-r`) · **Course:** INFO 7375 · **Assignment:** JS2 (Chapters 4–6)
**Folder:** `fall-2026/aditya-r/js2-loop-tools-diff/` in [nikbearbrown/info-7375-prompt-engineering-for-generative-ai](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai)

This agent is a bounded loop over **four public job boards on two applicant-tracking systems**: Greenhouse `databricks` and `figma`, Ashby `notion`, and one Greenhouse board that fails on purpose. It runs under a permission policy enforced in code, and it ends with exactly one of four statuses. Every new posting gets a **RECORD**, a deterministic rule anyone can recompute, and a **JUDGMENT**, Claude's opinion validated for format and cited evidence, not for correctness.

The agent never applies, emails, messages anyone or logs in. It has two network channels, kept separate as GATE.md §5 requires:

- **Board fetching** (`agent/net.py`, called only through `fetch_board`). This is HTTPS GET to exactly `boards-api.greenhouse.io` and `api.ashbyhq.com`, on the board paths only, with no redirects. It is checked by `policy.check_request` before every dispatch, and it is the only channel the allow-list and the HTTP-attempt budget govern.
- **Judgments** (`agent/judge.py`, inherited from JS1). This runs the installed Claude Code CLI (`claude -p`) as a subprocess, with a fixed argument list, under Aditya's existing login, with model tools disabled. The CLI talks to Anthropic's service itself. That traffic is **not** governed by the board allow-list: GATE.md §5 authorizes it separately, the 10-call model budget counts it, and each call is bounded by a subprocess timeout of min(20 s, remaining allowance). The agent does not count or inspect the CLI's internal network requests (GATE.md §2).

_This README is technical documentation drafted by Claude Code. Aditya dictated the sign-off items. The driver's-seat "why" column was drafted by Claude from the responsibilities he named. The signature is his._

## Starting point: JS1, credited (see [`BASELINE.md`](BASELINE.md))

JS2 builds on Aditya's own **Job-Search Agent 1**, posted at [`../js1-contract-and-watch/`](../js1-contract-and-watch/) (commit `693b7d3`). The JS1 files were imported **unchanged** from JS1 commit `819f2e9`, with per-file hashes in `evidence/baseline/js1_import_manifest.sha256`. All inherited checks passed before any JS2 code existed.

| Inherited from JS1 (unchanged unless noted) | New in JS2 |
|---|---|
| `agent/rules.py` (RECORD rule), `judge.py` (isolated `claude -p` call), `validate.py` (JUDGMENT validator), `resume.py` (fictional-persona guard), `state.py` (used to validate the JS1 state before seeding), `prompts/`, `resume/priya-nair.resume.example.json`, `state/seen.json` (JS1's Databricks state, 2026-10-30), JS1 tests | `agent/loop.py` (the loop), `agent/policy.py` (permissions), `agent/net.py` (HTTP client that never follows redirects), `agent/providers.py` (Greenhouse and Ashby adapters), `config/boards.json`, `tests/test_loop.py`, `tests/test_boundary.py`, `tests/test_net_deadline.py`, `tests/mutation_check_js2.py`, `scripts/check_run.py` (independent checker), `scripts/demo_finished_wrong.py` |
| `agent/board.py` and `agent/watch.py`: **changed only by the reviewed patch** (`0007bbd`, `d58682c`; see [`review/REVIEW.md`](review/REVIEW.md)) | `tests/test_aditya_total_mismatch.py` (**Aditya's** regression test), `tests/test_total_validation.py` and `tests/test_meta_object.py` (Claude's focused tests) |

## Toolchain

- **Language:** Python **3.12.8** (`/usr/local/bin/python3`). The standard library is enough to run the agent. **pytest 8.3.3** runs the tests (`requirements.txt`).
- **Judgments:** the Claude Code CLI **2.1.310** (`claude -p`), logged in with Aditya's account. Model `claude-opus-5-5`, effort `medium`. Tools, MCP and settings are disabled, and the CLI runs in an empty temp directory (inherited from JS1). Each call's `modelUsage` also lists `claude-haiku-5-5`, which is not explained here.
- **Platform:** macOS 26.5.1 (arm64), zsh, git 2.39.3. Version numbers were checked on 2026-11-10.

## Commands (from a fresh clone)

```bash
git clone --filter=blob:none --sparse https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai
git sparse-checkout set fall-2026/aditya-r/js2-loop-tools-diff
cd fall-2026/aditya-r/js2-loop-tools-diff
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# Offline: no network and no model needed
.venv/bin/python -m pytest -q                                   # 178 tests
.venv/bin/python tests/mutation_check_js2.py                    # plants W1–W12 + the reviewed patch; all 21 CAUGHT
.venv/bin/python tests/mutation_check.py                        # JS1's 3 wrong versions; all CAUGHT
.venv/bin/python scripts/check_run.py run out/runs/20261110T232115022Z_live   # independent re-check of the LIVE run
sh scripts/clean_clone_check.sh                                 # all of the above, in a fresh extraction of HEAD

# Live (network; Claude Code CLI logged in for judgments)
.venv/bin/python -m agent.loop --label live --propose-export    # watch the 4 boards; exit 0/2/3/4
.venv/bin/python -m agent.loop --export <run-id>                # export-only; needs approvals/<run-id>.json
```

A live run reads and updates the working state `out/state/seen.json`. To start fresh, run it in a copy of this folder.

**Exit codes** (GATE.md §1): `0` finished · `2` error · `3` incomplete · `4` budget-exhausted · `1` reserved for a crash. When more than one applies, error > budget-exhausted > incomplete > finished. Options such as `--max-http-attempts 4` may **lower** a limit but never raise one.

## The gate, applied

[`GATE.md`](GATE.md) is Aditya's text, committed first (`8257ffb`) before any JS2 code. [`GATE_ADDENDUM_1.md`](GATE_ADDENDUM_1.md) holds his six clarifications, saved verbatim (`8a0ef83`).

| Gate rule | Where it is enforced | Tested by |
|---|---|---|
| Exits and precedence; unknown counts are `null`, never 0 | `loop.run_loop` (end) | `test_loop.py` W2/W12, precedence, run-level-error tests |
| Budgets: 4 boards, 8 HTTP attempts (8th allowed, 9th never sent), 180 s with a 10 s reserve and per-call timeout = min(20 s, allowance), 10 model calls | `Budget`, `fetch_board`, the judgment loop; the per-attempt deadline in `agent/net.py` | `test_W3_*`, `test_elapsed_budget_*`, `test_exactly_ten_*`, `tests/test_net_deadline.py` |
| Repeat rule: same method and URL once per run, plus one linked retry; duplicate boards rejected | `fetch_board`, `load_config` | `test_b19`, `test_config_errors_*` |
| Error policy: 4xx no retry; 5xx, timeout or reset retried once after 0.5 s and counted; empty board → suspect-empty; `meta.total` checked; redirect → run-level error | `fetch_board`, `providers`, `board.parse_jobs` | `test_W1_*`, `test_W4_*`, `test_b07` |
| Identity `(provider, board, id)`; state staged and published only when there is no run-level error | `loop`, `out/state/seen.json` | `test_W9_*`, `test_W10_*`, `test_run_level_error_*` |
| Permission policy (hosts, folders, protected export, approvals) | `agent/policy.py`, `export_run` | [`BOUNDARY_TABLE.md`](BOUNDARY_TABLE.md): 20 predicted cases, B1–B20 |

**Honest limits of enforcement.**
- These are application-level controls, not an OS sandbox (GATE §5).
- **Board-attempt deadline (changed after the LIVE run).**
  - *What changed:* the LIVE run and Aditya's 18:41 check used the earlier client. It bounded body reads only: DNS inside `getaddrinfo` was unbounded (this was disclosed), and the TLS handshake, status line and headers got a fresh socket timeout on every `recv` (this was **not** disclosed until the tests showed it).
  - *How it works now* (`be5d821`): the whole attempt runs in a worker thread, and the agent waits at most until the attempt's deadline. A DNS answer that arrives late is not connected, and an expired deadline dispatches nothing.
  - *What remains:* a worker stuck in `getaddrinfo` keeps running in the background until the OS resolver returns, as a daemon thread that sends nothing. The connect hook relies on `http.client._create_connection`, which is not a public API; if it is missing, the client fails closed. All of this was tested against local servers and a stub resolver only (`evidence/net_deadline/`), not a real slow DNS server.
- A model subprocess is bounded by `subprocess.run(timeout=…)`.
- Races between the path check and the write are narrowed by a re-check after creating folders and by `O_EXCL|O_NOFOLLOW`. They are not eliminated.

## What ran (2026-11-10; all times real)

| Evidence | Label | Result |
|---|---|---|
| [`out/runs/20261110T232115022Z_live/`](out/runs/20261110T232115022Z_live/) — `trace.jsonl`, `raw/` (exact bytes, gzip-wrapped), `judgments/`, `report.md`, `state_before/after.json`; console in `evidence/live/console.txt` | **LIVE**, started 18:21:14 EST by Claude Code | **`budget-exhausted`, exit 4**. Databricks: 920 postings, **89 new** since JS1's 2026-10-30 state (inherited, not captured by JS2). Figma (144) and Notion (155): baselines. `js2-no-such-board-zzz`: **HTTP 404 → failed**, counts `null`, not retried. Used 4/8 HTTP attempts, **10/10 model calls** (all valid; all RECORD = JUDGMENT = `not_relevant`) and 58.1/180 s. **79 new postings remain `pending`.** An export proposal was written (0 entries, `partial: true`, 4 RECORD-relevant withheld). |
| [`evidence/approval_demo.txt`](evidence/approval_demo.txt), [`approvals/20261110T232115022Z_live.json`](approvals/20261110T232115022Z_live.json), `out/exports/`, `out/approved-shortlists/` | **LIVE**, run by **Aditya**, 18:36:37–18:38:11 EST | Export without approval: **exit 3**. Aditya wrote the approval record himself (`approved_at` 18:37:50 EST, bound to the proposal's sha256 `df370075…`). Export: **exit 0**, and the bytes equal the proposal (`cmp` exit 0). Repeat: **exit 2** (create-only). The approval covers this one local file. It does not change the LIVE run's status. |
| [`evidence/aditya_clean_clone_check.txt`](evidence/aditya_clean_clone_check.txt) | run by **Aditya**, 18:41:36–18:42:07 EST, at `1019351` | 171 passed; 3/3 + 18/18 mutants caught; checker 24/24; exit 0. This **predates** the `net.py` deadline fix. |
| [`evidence/net_deadline/`](evidence/net_deadline/) | SYNTHETIC (local servers, stub resolver), Claude Code | Tests committed failing first (`20c9d05`: 4 failed, 3 passed), then the fix (`be5d821`): 7 passed |
| [`evidence/aditya_final_verification.txt`](evidence/aditya_final_verification.txt) | run by **Aditya**, 20:19:19–20:20:31 EST, at `049e8b5` | Pre-fix deadline tests: 4 failed, 3 passed, exit 1. Fresh extraction: 178 passed; 3/3 + 21/21 mutants caught; checker 24/24; exit 0. **Aditya accepted the deadline fix within its documented limits.** In his words: "I understand that the caller’s wait is bounded, while an underlying blocked DNS resolver thread may continue until the system resolver returns. The tests use local servers and a stubbed resolver; they do not prove behavior under every live-network condition." |
| `scripts/check_run.py run …live` | independent recomputation | 24/24 checks passed: limits, allow-listed URLs, raw hashes, new ids = raw ids − inherited ids, `meta.total`, null counts, status by precedence, state |
| [`evidence/finished_wrong/`](evidence/finished_wrong/) ([`DEMO_LOG.md`](evidence/finished_wrong/DEMO_LOG.md)) | **REPLAY** (LIVE Figma bytes) + **SYNTHETIC** (empty board); expectation committed first (`8664385`) | **Finished wrong answer:** the inherited single-board `agent/watch.py` exits **0**, "COMPLETE: 0 new", after 144 postings vanish. The **independent checker** (no `agent/` imports) flags the contradiction from the raw evidence (exit 1). The JS2 loop on the same inputs: suspect-empty, **exit 3**, state unchanged; checker exit 0. |
| `evidence/boundary/boundary_run.txt` | SYNTHETIC; B7 uses the real HTTP client against two local servers | 30 passed; 20/20 rows observed as predicted |
| `evidence/mutation/mutation_check_js2_output.txt` | **MUTATION** | 21/21 CAUGHT, including 3 attempt-deadline mutants. Two earlier runs had misses. The first had 3 MISSED: W3, an untested path that is now tested; and W6 and W11, each masked by a second defense, so those mutants now remove both layers. The first deadline run had 1 MISSED, also masked, and is kept as `mutation_check_js2_dns_first_run.txt` |
| [`review/`](review/) | Aditya's reproduction and test; Claude's patch | Reproduce → test first → patch → REVISE → revision tests first → revision → **ACCEPT** by Aditya (18:03 EST check) |
| `evidence/pre_gate_recon/` | LIVE recon before the gate | status codes and response shapes only (disclosed in GATE.md) |

**What the live run does not show:** a second live day, a real 5xx or timeout, a real redirect, a real empty board, or judgments on the 79 pending postings.

## The review packet

See [`review/REVIEW.md`](review/REVIEW.md). Claude flagged the defect with probe P2. **Aditya reproduced and characterized it, wrote the regression test before the patch, wrote the change request, ran the checks himself, requested one revision and accepted the result.** The full chronology is in the packet, and every step is a separate commit.

## Driver's seat

_The "Why" column was drafted by Claude Code at Aditya's request (2026-11-10, about 20:30 EST), from the four responsibilities he named: adopting limits, authorizing actions, deciding whether to accept changes, and signing only claims supported by evidence._

| Part | What Claude did | What Aditya did | Why that part stays Aditya's | Evidence |
|---|---|---|---|---|
| Gate (exits, budgets, policy) | Asked the clarifying questions; pointed out the ambiguities | Wrote GATE.md and the six decisions in Addendum 1 | **Adopting limits.** The gate defines what "finished" means and how far the agent may go. Claude could propose limits, but only Aditya could adopt them, and only a new dated decision from him can raise one (GATE.md §2). | `8257ffb`, `8a0ef83` |
| Loop and tools | Wrote the loop, policy, adapters, tests, mutants and checker; ran the live run | Set the limits, the hosts, the deliberate failure and the expected outcome; accepted the `budget-exhausted` LIVE result without raising a budget; accepted the deadline fix only after his own 20:19 check | **Adopting limits and accepting changes.** Claude wrote the code, but the code is accountable to limits Aditya adopted. Whether its outcome is acceptable, including an incomplete one, is his decision, not the agent's. | `785138a`, `31dd501`; Addendum §6 |
| Review | Flagged P2, wrote the probes, the patch, the revision and the focused tests | Reproduced it, wrote `test_aditya_total_mismatch.py` and CHANGE_REQUEST.md, ran the checks, decided REVISE then ACCEPT | **Deciding whether to accept changes.** A passing test suite did not settle it: he asked for a revision after round 1 passed, and accepted only after his own final check. | `b0e3fb4`, `6d37618`, `9589e64` |
| Approval of the export | Built the proposal and the export-only path | Inspected the proposal and checked its hash; wrote `approvals/20261110T232115022Z_live.json` himself (18:37:50 EST); ran the export without approval, with approval, and repeated | **Authorizing actions.** The agent may propose a protected write; only a human may authorize that exact write. The runtime cannot create the approval itself (B14, W11). | `evidence/approval_demo.txt`, `e1a4a69` |
| Sign-off | Drafted the evidence pointers and formatted the items Aditya dictated | Chose what is checked, not checked and not claimed; signs or withholds | **Signing only claims supported by evidence.** A signature vouches for the claims above it, so each item must point to a record he produced or verified himself. | this section; `evidence/aditya_final_verification.txt` |

## Sign-off — Job-Search Agent 2

_The items below are Aditya's: he dictated them in the session on 2026-11-10 (about 20:30 EST). Claude Code formatted them and added the evidence pointers in brackets. The signature line is Aditya's to complete._

- **Checked:**
  - my recorded regression runs [`review/prepatch_failure.txt`, `review/aditya_postpatch_run.txt`, `review/aditya_final_check.txt`];
  - the approval demonstration [`evidence/approval_demo.txt`, 18:36:37–18:38:11 EST];
  - the fresh-extraction checks [`evidence/aditya_clean_clone_check.txt` at `1019351`; `evidence/aditya_final_verification.txt` at `049e8b5`];
  - the deadline tests [pre-fix at `20c9d05`: 4 failed, 3 passed, exit 1; current: passing];
  - the mutation checks [3/3 inherited, 21/21 JS2];
  - verification of the saved evidence [independent checker: no contradiction found across 24 checks].
- **How:** I personally executed the commands.
- **Not checked:**
  1. arbitrary live-network deadline failures;
  2. judgments for the 79 pending postings;
  3. behavior across multiple live days and future schema changes;
  4. the truth of all free-text explanations;
  5. complete protection against filesystem races.
- **Not claiming:** universal correctness, OS-level isolation, completed evaluation of every posting, or independent authorship of AI-produced work.
- **Signed or withheld:** ____________ _(name, date)_

## Privacy

- **Persona:** the résumé is the fictional Priya Nair persona from JS1.
- **Kept local, unpublished:** Aditya's screenshots, private conversations, his local workspace notes and the originals of redacted files.
- **Redactions:** only local paths and the username, all listed in `review/EVIDENCE_REDACTIONS.md` and `BASELINE.md`.
- **ZIP contents:** `scripts/package.sh` builds the ZIP from committed files only.
