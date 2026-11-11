# Job-Search Agent 2: the loop, the tools, and the diff

**Mayank Bhadrasen (mayank-b)** · INFO 7375 · Fall 2026 · Chapters 4–6

## Executive summary

**What this is.** My job-search agent from JS1 watched one Greenhouse board. This version is a bounded loop. It reads several public job boards across two applicant-tracking systems (Greenhouse and Ashby), stops in one of four stated ways, and records every observation. It may touch only what a permission policy in the code allows, and it was changed through one reviewed patch.

**Why read it.** The interesting part isn't that it fetches jobs. It's what happens when a board fails, when the same board appears twice, when a run ends cleanly with a wrong answer, and when a path tries to escape its folder. Each case has a rule written first (`GATE.md`), a test, and a saved real run.

**What it showed (2026-11-10, Eastern):**
- **The real run** read Anthropic (679 postings), HubSpot (122) and Notion (156). The deliberately bad board returned HTTP 404 and was recorded as an *error*, not "0 jobs"; it was not retried. A repeated board was skipped without a request. The run stopped as `incomplete` with exit code 3 and "NEEDS MAYANK" on its first line.
- **The finished-wrong answers.** Two runs ended `finished` with exit code 0 while reporting a board as "0 postings, 0 new". A separate checker, reading only the saved raw responses and my floors, flagged both as `suspect`.
- **The permission policy** holds all 16 boundary cases predicted in advance. The review patch fixed a symlink escape inherited from JS1. A probe shows one escape it still misses.

**Started from:** my JS1 (`../js1-contract-and-watch`). I kept its fictional persona, title rule, allow-list idea, atomic writes, seen-ids state, and raw response + SHA-256, and ported them from JavaScript to Python. The provider pattern comes from the Reallocation Engine (`scripts/ats/providers/`); board slugs and traps come from the instructor's Lectern (`fall-2026/nik-bear-brown/lectern/ATS.md`). See `SOURCES.md`.

---

## Language, toolchain, commands

- **Language:** Python 3, **standard library only** (`urllib`, `json`, `pathlib`, `unittest`). No install, no keys. Ran with **Python 3.11.16** on macOS; needs Python ≥ 3.9 (`Path.is_relative_to`).
- **Why Python:** the course repo's `scripts/validate_course.py` rejects `.js/.ts` files; my JS1 JavaScript files are on its failure list.

From a fresh clone:

```bash
cd fall-2026/mayank-b/js2-loop-tools-diff

python3 -m unittest discover -s tests -p "test_*.py"     # 50 tests, offline
python3 scripts/wrong_versions.py                         # plants W1–W9 and shows which test catches each

python3 agent.py run --plan config/boards.json --label real                 # LIVE: 5 planned entries
python3 checker/check.py runs/<run-id> --plan config/boards.json            # independent check

python3 agent.py run --plan config/boards-empty-live.json --label empty-board-live     # LIVE finished-wrong
python3 checker/check.py runs/<run-id> --plan config/boards-empty-live.json

python3 agent.py run --plan config/boards-finished-wrong.json --replay config/replay/finished-wrong.json --label seeded-finished-wrong   # SEEDED, no network
python3 checker/check.py runs/<run-id> --plan config/boards-finished-wrong.json

python3 agent.py approve <run-id> --approve-state <run-id> [--ack <ats>/<slug>]   # the one write that needs me
```

Exit codes: `0` nothing needs me · `3` a board needs me (error or suspect) · `2` run-level error (`state/` untouched).

## Files

| File | What it is |
|---|---|
| `GATE.md` | exits, budgets, repeat rule, error + permission policy, wrong versions, written before any code (JS2-CP1) |
| `notes/gate-answers-2026-11-10.md` | my answers, verbatim; `notes/GATE-QUESTIONS.md` is the sheet Claude gave me |
| `src/jsa/` | `loop.py` (controller), `policy.py` + `net.py` (permission policy in code), `boards.py` (Greenhouse, Ashby), `rule.py` (JS1 title rule), `cli.py` |
| `checker/check.py` | the independent check; it does not import `src/jsa` |
| `tests/` | 50 tests: `test_policy.py` (boundary B1–B16), `test_loop.py`, `test_checker.py`, `test_approve.py`, `test_gate_config.py` |
| `scripts/wrong_versions.py` | plants each wrong version W1–W9 |
| `BOUNDARY-TESTS.md` | the permission policy and the 16-case table: prediction first (CP2), then what happened |
| `REVIEW-PACKET.md` + `review/` | the Chapter 6 review packet |
| `runs/<run-id>/` | `trace.jsonl` (every step), `raw/` (exact bytes as received), `report.{json,md}`, `proposed-seen-ids.json`, `check.{json,md}`, captured stdout |
| `config/` | budgets, plans, floors (`expected-boards.json`), replay files for the seeded run |
| `SOURCES.md`, `FRICTIONAL.md` | what I used and what Claude contributed; the dated friction log |

---

## What ran (past tense only; times are UTC run ids)

### 1. The real run with the deliberate failure: `runs/2026-11-11T00-24-30Z-real/`

The plan had five entries: Greenhouse `anthropic`, Greenhouse `hubspotjobs`, Ashby `notion`, a board name that doesn't exist (**the deliberate failure**), and Ashby `Notion` (**a deliberate repeat**). The trace (`trace.jsonl`), one line per step, abridged:

```text
1 start        planned 5, budget {boards 5, requests 10, seconds 60, timeout 10}
2 observation  greenhouse/anthropic     200  679 postings  raw/greenhouse__anthropic__a1__200.json  sha256 39e41f80…
3 observation  greenhouse/hubspotjobs   200  122 postings  raw/greenhouse__hubspotjobs__a1__200.json sha256 c00a1fdf…
4 observation  ashby/notion             200  156 postings  raw/ashby__notion__a1__200.json          sha256 dee2e0c7…
5 observation  greenhouse/mayank-js2-no-such-board  404  http-4xx  (not retried: a 404 is not transient)
6 skipped      ashby/Notion  repeat of ashby/notion — no request sent
7 stop         exit=incomplete  requests=4  needs_mayank=[greenhouse/mayank-js2-no-such-board]
```

- The failed board shows `— (not 0)` in the report, and **its state is untouched**: there's no entry for it in `proposed-seen-ids.json`.
- The process exited **3**. The first line of `report.md` is `NEEDS MAYANK: greenhouse/mayank-js2-no-such-board`.
- **Exit `incomplete`**, because one planned entry was skipped as a repeat (GATE §1). Not `finished`, and certainly not "success".
- All three real boards were **baselines** (first time seen), so nothing was reported as new. I didn't run a second calendar day.
- Independent check (`check.md`): anthropic, hubspotjobs and notion are `ok` against my floors; the bad board is `error-response`.

### 2. A finished wrong answer, caught by the independent check

| Run | How it ended | What the agent said | What the checker said (raw bytes + my floors) |
|---|---|---|---|
| **LIVE** `runs/2026-11-11T00-26-09Z-empty-board-live/`: Ashby `greenlight` | `finished`, process exit **0** ("nothing needs Mayank") | `ashby/greenlight: ok, 0 postings, 0 new` | **`suspect`**: "0 postings in the raw response (an empty board is not 'no new jobs')"; exit **3** |
| **SEEDED** (labelled; no network) `runs/2026-11-11T00-26-11Z-seeded-finished-wrong/`: Greenhouse `hubspot` replayed as the empty board Lectern recorded on 2026-09-26 | `finished`, exit **0** | `greenhouse/hubspot: ok, 0 postings, 0 new` | **`suspect`**: 0 postings, below my floor of 20 (HubSpot posted 133 at `hubspotjobs` per Lectern, and 122 in my live run) |

- **Why two.** I planned to use `greenhouse/hubspot` live. On 2026-11-11 the live API returned **404** for it (`runs/2026-11-11T00-24-41Z-finished-wrong/`), so the agent correctly reported an error and the trap no longer existed. The world had moved since Lectern's note.
- The live replacement, `ashby/greenlight`, is a real valid-but-empty board. Its *identity* is unconfirmed: my Reallocation Engine probe flagged it as possibly not GreenLight Biosciences. So the agent's "no new jobs" is **unsupported**, but I can't prove it **wrong**.
- The seeded HubSpot replay is provably wrong. It's labelled `SEEDED RUN` on the first line of its report, and its replay file names the origin of every byte.
- **What makes the check independent:** `checker/check.py` doesn't import the agent. It counts postings from the raw bytes itself, uses floors *I* set with named sources, and reads the agent's report only afterwards, to show the claim next to the verdict.

### 3. The permission policy, in code

GATE §6 is enforced in `src/jsa/policy.py` and `src/jsa/net.py`:
- **Hosts:** exact allow-list, https only, GET only, redirects refused.
- **Paths:** judged by where they resolve, with component containment.
- **Writes:** free inside `runs/<run-id>/`; `state/seen-ids.json` only with `--approve-state` exactly equal to the run id; everything else refused.

The 16 boundary cases, each with its prediction committed before the tests ran, are in **`BOUNDARY-TESTS.md`**.
- All 16 were allowed or refused as predicted on the final code.
- **B7** was refused for a different reason than I predicted.
- **B8** (symlink escape) failed on the first version on purpose: it's the review-packet defect.

`scripts/wrong_versions.py` → **9/9 wrong versions caught** (`review/03-after-patch.txt`).

### 4. The review packet

See **`REVIEW-PACKET.md`**:
1. Failing tests committed first (CP5 `f2e775e`).
2. The request and its scope.
3. A 1-function diff, read as a behaviour change (it also changed reads, which I didn't ask for by name).
4. 50/50 tests and 9/9 wrong versions after the patch.
5. A probe proving one escape still open.
6. My decision.

---

## Sign-off — Job-Search Agent 2

**Checked** (and by which of my tests):
- Exits and budgets: `test_loop.Exits.*`: one failed board still `finished` (1a); `test_W6_budget_exhausted_is_not_finished` (the 3rd request is never sent); `test_board_cap`; `test_seconds_cap_checked_before_request`.
- Repeat rule: `test_W7_same_board_other_case_and_encoding_is_skipped` (`Notion`, `Jasper%20AI`).
- Error policy: `test_404_never_retried`, `test_malformed_never_retried`, `test_5xx_retried_once_then_ok`, `test_timeout_retried_once_then_error`, `test_retry_counts_against_request_budget`, `test_W5_failure_is_error_not_zero`.
- State: `test_W9_failed_board_keeps_its_seen_ids`, `test_W9_error_board_state_survives_approve`, `test_suspect_board_held_until_acked` (4b-C).
- Permission policy: `test_policy.*` B1–B16 + B8b; approval through the CLI (`test_truthy_approval_writes_nothing`).
- Independent check: `test_W4_empty_board_is_suspect`, `test_reads_raw_not_report`, `test_checker_does_not_import_the_agent`.
- Budgets in code = GATE.md: `test_gate_config.GateMatchesConfig`.

**How:**
- The rules, predictions and wrong versions are mine, written before code (CP1, CP2).
- The B8/B8b tests were committed before the patch (CP5).
- By recomputation: the checker counts postings from raw bytes, and the hashes in the trace match the saved files (`test_raw_response_saved_byte_for_byte_with_hash`).
- With Claude's help: Claude Code wrote all the code, the tests and this README from my gate (see `SOURCES.md`).

**Not checked:**
1. **`runs/` itself being a symlink.** Probed: the write escapes (`review/04-still-missed-probe.txt`).
2. A link swapped in between the check and the write (time-of-check/time-of-use).
3. A real timeout or 5xx: those paths were exercised only with a scripted fetch; no live board timed out.
4. The 60-second cap against a real slow board: tested only with a fake clock.
5. The title rule on live new jobs: every live board was a baseline, so no job was "new" and the rule never judged a live posting.
6. A second calendar day. I ran `approve` on the real run myself (2026-11-11T01:00Z UTC, `runs/2026-11-11T00-24-30Z-real/approval.json`): `state/seen-ids.json` now holds 679 / 122 / 156 ids for the three healthy boards. No later run has used that state yet, so "new since last check" was never shown live.
7. Board identity for `ashby/greenlight` (unknown), and this time for the other boards (taken from Lectern's 2026-09-26 verification, not re-confirmed by me).
8. Reads through symlinks are now refused, but no test covers that yet (`REVIEW-PACKET.md`).

**Not claiming:**
- That any reported job list is complete or correct.
- That an empty board means a company has no jobs.
- That `finished` means success.
- That the policy is a sandbox: it returns a path; it doesn't stop other code.
- That anything here works on Lever or SmartRecruiters.
- That one evening's runs say anything about reliability over time.

**Signed or withheld:** Signed: Mayank Bhadrasen, 2026-11-10

## Driver's seat

| Part | What Claude did | What I did | Why it stays mine | Evidence |
|---|---|---|---|---|
| The gate | wrote the question sheet (2026-11-05), then turned my answers into GATE.md with 6 listed edits | chose every rule; chose 4b = A+B+C; wrote my failure sentence and W9; ran `approve` on the real run myself | the rules are the criterion everything is checked against; written by the producer, they would describe its output | `notes/GATE-QUESTIONS.md`, `notes/gate-answers-2026-11-10.md`, GATE.md "Changes Claude made" · CP1 `3ce860b` |
| Predictions | drafted the 16 cases with predicted results | accepted them before any test ran | a prediction written after the run tests nothing | CP2 `1581f58` (before code, CP3 `b8b3fb4`) |
| The loop | wrote `src/jsa/`, the tests, the harness; ran the live runs | decided boards, caps, the deliberate failure and the repeat | how much the agent may spend and try is my decision, not a property of the code | CP3 `b8b3fb4`, CP4 `ebb7b3f`, `runs/*-real/trace.jsonl` |
| Floors for the checker | proposed each floor from a named source | _approve or change them_ | the checker is only independent if its expectations aren't the agent's | `config/expected-boards.json` (`_status`) |
| The review | reproduced the defect with a failing test, wrote the patch, collected the evidence, probed what it misses | ran the commands myself ("Ran, matched"); decided **ACCEPT**, with the missed case logged as a follow-up | the same session wrote the code, the test and the patch, so its agreement is "the first opinion run twice" | CP5 `f2e775e`, CP6 `9416437`, `REVIEW-PACKET.md` |
| Sign-off | drafted the Checked / Not checked lists from the record | signed: Mayank Bhadrasen, 2026-11-10 | my name goes on it | this section |
