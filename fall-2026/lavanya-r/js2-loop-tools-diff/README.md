# Job-Search Agent 2 — The Loop, the Tools, and the Diff

**Lavanya R** · INFO 7375 · Fall 2026 · Chapters 4–6.

**What it does.** A bounded loop watches several public job boards on three applicant-tracking systems: Greenhouse, Lever and Ashby. It obeys a permission policy enforced in code, and ends in exactly one of four honest exits. It reports postings that are new since the last run. Every request, response and decision is saved.

The agent never applies, emails, messages or logs in. There is no code for any of those, and the policy refuses them by name. It uses the fictional persona Priya Nair (`persona/priya-nair.resume.json`), not a real résumé.

**What I started from:**
- my own JS1 folder (`../js1-contract-and-watch`), copied unchanged in commit `7e1bacb`;
- the Ashby and Lever endpoints from the instructor's collector, Lectern (`fall-2026/nik-bear-brown/lectern/sources.json`).

I did not use the Reallocation Engine's code.

**Read in this order:**
1. [GATE.md](GATE.md): the rules, written before any code (`77537ea`).
2. [TRACE.md](TRACE.md): one real run.
3. [PREDICTIONS.md](PREDICTIONS.md): the boundary table.
4. [REVIEW-PACKET.md](REVIEW-PACKET.md).
5. This file's sign-off.

## Language and toolchain

| Tool | Version used | Needed for |
|---|---|---|
| Python | 3.11.5, **standard library only** (no `pip install`) | everything |
| git | 2.50.1 | the commit history this packet cites |
| Network | `boards-api.greenhouse.io`, `api.lever.co`, `api.ashbyhq.com` (https GET only) | the live loop only; tests are offline |
| Claude Code CLI | 2.1.312 (NEU login) | not needed to run anything here; it was the tool that wrote the code |
| OS | macOS 26.5 | — |

## Commands (from a fresh clone)

```bash
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/lavanya-r/js2-loop-tools-diff
```

All commands run from this folder.

**1. Tests: 94, offline, and nothing in this folder changes**
```bash
python3 -B -m unittest discover -s tests -t . -v
```

**2. Independent check of the committed live run**
```bash
python3 -B check.py runs/2026-11-10T222859Z-live/report.json
```

**3. Boundary cases: predicted vs actual**
```bash
python3 -B review/boundary_table.py
```

**4. The review evidence**
```bash
python3 -B review/revalidate.py
```

**5. The finished-wrong demo.** Seeded, no network. It adds files under `runs/`.
```bash
bash review/finished_wrong_demo.sh
```

**6. A live run.** This adds a folder under `runs/` and may write `state/`.
```bash
python3 -B -m agent.loop
```

At a terminal, it asks before overwriting a file in `state/`; type `y` to approve. `--approve-state` approves for that one run. With no terminal and no flag, the state is not written and the run ends `incomplete`. The 120 s budget includes time spent waiting at that prompt.

If every board fails with `CERTIFICATE_VERIFY_FAILED`, that is the machine's Python certificate setup, not the boards (see Not checked 2). On my Mac, the app's Terminal tab, using `~/anaconda3/bin/python3`, worked.

Exit codes: `finished` 0, `error` 1, `incomplete` 2, `budget_exhausted` 3.

## What ran (all real, all dated, 2026-11-10 ET)

| When | What | Result | Evidence |
|---|---|---|---|
| 17:22 | GATE.md and my predictions committed, before any JS2 code | — | `77537ea` |
| 17:23 | JS1 code copied unchanged; the bug test committed and run on the unchanged validator | 5 failures (the reproduction) | `7e1bacb`, `8fc4022`, `logs/01` |
| 17:28 | **Live run 1**: 5 board entries on 3 ATS, including a deliberate bad name and a deliberate repeat | `incomplete` (2). Databricks: 917 jobs, **89 new since JS1's 2026-10-30 run**, memory not saved (no approval). Notion: 155, baseline. Palantir: 304, baseline. `no-such-board-js2`: 404 after 1 attempt. `Databricks` (repeat): skipped. 4 requests, 2.2 s. | [TRACE.md](TRACE.md), `runs/2026-11-10T222859Z-live/`, `logs/02` |
| 17:29 | Independent check on live run 1 | 9/9 pass | `logs/03` |
| 17:29 | **Finished-wrong demo** (SEEDED) | JS1's watcher: exit 0, "New since last run: 0" on a 0-job board. check.py: **FAIL**. JS2: `suspicious_empty`, `incomplete`; check.py: pass | `logs/04`, `runs/finished-wrong-demo/` |
| 17:31–17:33 | Patch, review, revision, re-review | see REVIEW-PACKET.md | `7044eaf`, `40b55f0`, `54b5602`, `logs/05`–`11` |
| 17:31 | Boundary predictions vs actual | 13/14 matched (case 3 wrong) | `logs/08`, PREDICTIONS.md |
| 17:38, 17:43 | **Live runs 2 and 2b, run by me** in my own Terminal window | every board failed TLS verification → exit `error`, no value invented. Cause unresolved | `runs/2026-11-10T223836Z-live/`, `runs/2026-11-10T224326Z-live/`, `logs/12`–`13` |
| 17:44 | **Live run 3**: I approved the state overwrite by typing `y` | Databricks saved with my approval; then `budget_exhausted` (waiting for me counted against 120 s) | `runs/2026-11-10T224443Z-live/`, `logs/13` |

**Seeded vs live.** Runs 1, 2, 2b and 3 are live. The finished-wrong demo is **seeded**:
- its baseline is a real JS1 response from 2026-10-30, replayed;
- its empty board is a constructed `{"jobs": []}`.

Every test response is constructed and labeled as such in `tests/loop_fakes.py`.

## The loop (Chapter 4)

| GATE.md rule | Where in code | Tests |
|---|---|---|
| 4 exits, each with a reason and a process exit code; "finished" only if every board was fetched, non-empty and saved | `agent/loop.py` `_exit` | `test_loop.TestExits` |
| Budgets of 10 boards, 20 requests and 120 s, checked **before** every request, with retries counted | `Budget` | `TestBudgets`, `test_budget_gate` (config must equal GATE.md's table) |
| Repeat = same ATS + same board name, ignoring case; skipped and free | `repeat_key` | `TestRepeatRule` |
| 404: no retry. Timeout or 5xx: one retry after 2 s. 403 or bad body: no retry. 0 jobs: `suspicious_empty`. A failed board's count is `null`, never 0 | `classify`, `RETRYABLE` | `TestErrorPolicy` |
| Every observation in `trace.jsonl`; every response body saved gzipped, byte for byte | `observe`, `raw/` | `test_raw_bodies_saved_byte_for_byte` |

## A finished wrong answer, and the independent check that catches it

`logs/04-finished-wrong-demo.txt` (SEEDED):

1. **Baseline.** My JS1 watcher, unchanged, reads a real 903-job Databricks response saved on 2026-10-30.
2. **The wrong answer.** On the next run, the board answers 200 with `{"jobs": []}`. The JS1 watcher prints **"New since last run: 0"** and exits **0**. That run ended cleanly and is wrong: a board that had 903 jobs did not become a quiet day. The fetch broke.
3. **The independent check catches it.** `check.py` imports nothing from `agent/`. It re-reads the saved raw bytes and recounts them itself. It sees 0 jobs behind a "0 new" claim, prints **FAIL**, and exits 1. The agent's own report is never trusted.
4. **The JS2 loop on the same input** says `suspicious_empty`, ends `incomplete`, and doesn't touch the state. check.py passes it.

`check.py` also caught a weakness in itself while I was building it. Its "exit honesty" check first trusted the statuses the report gave itself, so a doctored report passed (`test_check_catches_a_doctored_report` failed). It now decides from the raw bytes which boards really worked.

## The permission policy, in code (Chapter 5)

`agent/policy.py`. All network and file I/O goes through it:
- `net.make_get` calls `check_url` before a socket opens, and again on every redirect;
- `write_bytes` resolves the real path (following `..` and symlinks) and compares path parts, not strings, so `runs-evil/` is not inside `runs/`.

**Boundary table.** 14 predicted cases are in [PREDICTIONS.md](PREDICTIONS.md), with predictions written before the code and results filled in after. `tests/test_policy_boundary.py` has 16 more cases:
- a userinfo trick, a port, `evilgreenhouse.io`, an uppercase host, POST;
- each never-action;
- a final-component symlink, the `runs` folder itself, and a read outside.

Enforcement tests also check that refused writes leave **no file** anywhere, and that refused URLs **never reach the network**.

**Wrong versions from GATE.md 6**, each built and shown caught (`tests/test_wrong_versions_js2.py`):
1. empty board = "no new jobs";
2. a "contains" host check;
3. retries that skip the budget.

## Commands I ran myself

In my own terminal, 2026-11-10 (summarised in FRICTIONAL.md):

| Command | When (ET) | What I saw |
|---|---|---|
| `python3 -B -m unittest discover -s tests -t .` | before 17:38 | `Ran 94 tests` … `OK` |
| `python3 -B check.py runs/2026-11-10T222859Z-live/report.json` | before 17:38 | `9 passed, 0 failed` |
| `python3 -B -m agent.loop` (my own Terminal window) | 17:38 | **live run 2**: every board `CERTIFICATE_VERIFY_FAILED`, exit `error` (1), 8 requests, nothing invented. `runs/2026-11-10T223836Z-live/` |
| same, again | 17:43 | **live run 2b**: the same failure. `runs/2026-11-10T224326Z-live/` |
| `python3 -B -m agent.loop` in the app's Terminal tab (Claude typed the command; **I typed `y`** at the approval prompt) | 17:44, answered ~17:56 | **live run 3**: Databricks 917 jobs, 89 new, **state overwritten with my approval**. Then exit `budget_exhausted` (3): the 120 s budget counts the 12 minutes the run waited for my answer, so the other 4 boards were `not_visited`. `runs/2026-11-10T224443Z-live/` |

`check.py` on runs 2, 2b and 3: 8/8 each (`logs/12`, `logs/13`).

## Sign-off — Job-Search Agent 2

**Checked:**
- **Three boards across three ATS, live.** Greenhouse `databricks`, Ashby `notion` and Lever `palantir`, with real responses saved. The recounts match: `check.py` on live run 1, 9/9.
- **The deliberate failure was handled without inventing a value.** The 404 got 1 attempt and a `null` count, and was excluded from the total (TRACE.md seq 8; `TestErrorPolicy.test_404_is_not_retried_and_invents_no_count`).
- **The repeat rule:** live seq 9; `TestRepeatRule`.
- **Exits:** `TestExits`, and live run 1 really ended `incomplete` with exit code 2.
- **Budgets checked before requests, with retries counted:** `TestBudgets.test_retries_count_against_request_budget`; wrong version 3 caught.
- **Budgets equal GATE.md:** `test_budget_gate`.
- **The finished wrong answer was caught by an independent check:** `logs/04` step 3.
- **The permission policy:** 14 predicted cases plus 16 extras, with enforcement (`test_policy_boundary`). My predictions matched 13/14 (`logs/08`).
- **A real failure, handled honestly:** live runs 2 and 2b (my own terminal) failed TLS on every board and ended `error` with no invented counts; `check.py` 8/8.
- **Approval by a person:** in live run 3 I typed `y`, and only then was `state/greenhouse-databricks.json` overwritten (trace seq 3, `overwrite: true`). In live run 1, with no approval, it was not.
- **The seconds budget, live:** run 3 stopped with `budget_exhausted` and listed 4 boards `not_visited`.
- **The index fix:** reproduced on unchanged code (`review/01`); test first (`8fc4022`, failing in `logs/01`); a regression found by reading the diff and a revision (`40b55f0` then `54b5602`); 73 saved real replies re-validated (`logs/11`).

**How:**
- **By a test I wrote before reading Claude's code:** none written by me. The tests that came before their code are GATE.md (`77537ea`, my picks and my two sentences), my 14 boundary predictions (`77537ea`), and `tests/test_path_index.py` (`8fc4022`, before the patch). The expected values in that file are Claude's, under my delegation.
- **By hand:** I picked every GATE.md rule and every prediction, and wrote the two "In my own words" paragraphs. I ran the test suite and `check.py` myself (94 OK; 9/9), ran live runs 2 and 2b myself, and approved run 3's state overwrite myself ("Commands I ran myself").
- **By recomputation:** `check.py` recounts every saved raw response independently of the agent's code. `review/revalidate.py` re-runs the old and new validators on saved replies.
- **With Claude's help:** Claude Code wrote all of the code and tests, ran every command in the logs, wrote the first drafts of every document, and proposed the options I picked from. It also pointed out the conflicts in my first GATE.md picks and the regression in its own first patch.

**Not checked:**
1. **A real slow-server timeout, a real 5xx and a real empty board.** These were exercised only with constructed responses. The real failures were the 404 (run 1) and the TLS failures (runs 2 and 2b).
2. **Why my own Terminal window fails TLS** while the app's terminal tabs, with the same Python, folder and code, succeed. No proxy or certificate variables were set, and the chain is the real Amazon one. That window runs a different `openssl` (its output format differs), so its `PATH` probably differs too. Unresolved.
3. **Any posting I would label "fit".** My JS1 feedback asked for this so false negatives could be measured. JS2 does no relevance judging, and I did not label postings. It is still open.
4. **Whether waiting for my approval should count against the seconds budget.** GATE.md says "wall clock for the whole run", so it does, and run 3 stopped because of it. That may not be the rule I want. I have not changed GATE.md.
5. **A single run that ends `finished` live.** Run 1 was `incomplete` (on purpose), runs 2 and 2b were `error`, and run 3 was `budget_exhausted`. `finished` is shown only by `test_loop.TestExits`.
6. **The terms of use** of Greenhouse, Lever and Ashby, beyond using their public, documented job-board endpoints at one request per board per run.
7. **The review's "would still miss" case** (REVIEW-PACKET.md section 7), and that `check.py --previous-count 903` was typed in from the step-1 report, not read from it.
8. **That a posting's content changed without its id changing.** As in JS1, new means a new id only.

**Not claiming:**
- That this agent finds good jobs. JS2 watches and reports; it does not judge fit.
- That it works on boards other than the three I ran, or on Ashby or Lever responses shaped differently from the ones saved on 2026-11-10.
- That the policy is a security boundary against a hostile machine. It protects against the agent's own mistakes in this program. Other programs on my computer are not bound by it.

**Signed** Lavanya R, 2026-11-10

## Driver's seat

| Part | What Claude should do | What I should do | Why it stays mine | Evidence |
|---|---|---|---|---|
| The loop's rules (exits, budgets, repeats, errors) | offer options, point out conflicts, implement them exactly | pick the rules; say why "incomplete" isn't "finished" and why a 404 isn't retried | a loop's stopping rules decide what "done" means for **my** job search; the agent can't decide that for itself | GATE.md "Changes" table (3 conflicts I fixed); my two "In my own words" paragraphs in GATE.md; `77537ea` before any code |
| The permission policy | write the enforcement and the boundary tests | predict each case **before** it runs; decide what needs my approval | an agent shouldn't set its own permissions; predictions written first show whether I understand my own policy | PREDICTIONS.md (13/14; case 3 wrong and kept); `77537ea` |
| Approving a state overwrite | ask, and refuse when no one answers | type `y` myself, or not | it's the agent's memory of what I've already seen; overwriting it changes what counts as "new" next time | live run 1 seq 3 (`state_not_written`, no approval) vs live run 3 seq 3 (`state_written`, after I typed `y`) |
| The review: reproduce, test, patch | reproduce on unchanged code, write the test first, patch, re-run everything, read its own diff | run the commands myself; accept, revise or reject | the decision to ship a change is mine to defend, even when Claude recommends it | REVIEW-PACKET.md; `8fc4022` → `7044eaf` → `40b55f0` → `54b5602` |
| Saying what was checked | draft this sign-off from the logs | correct it and sign it, or withhold | only I can vouch for what I submit | the signature line above |

**Where I didn't keep the driver's seat:** for the `.0` fix, I handed the design decisions to Claude (2026-11-10). Claude chose the bug-test expected values and the review decisions, and I approved them. I am recording that rather than hiding it (FRICTIONAL.md).

## Files

- **Rules and results:** `GATE.md`, `PREDICTIONS.md`, `TRACE.md`, `REVIEW-PACKET.md`, `SOURCES.md`, `FRICTIONAL.md`.
- **Code:**
  - `agent/policy.py`, `net.py`, `providers.py`, `loop.py`, `import_js1_state.py`;
  - `check.py`, the independent check;
  - `agent/claude_judge.py`, the JS1 validator plus the review fix. The other JS1 files are unchanged.
- **Config:** `config/budgets.json` (must equal GATE.md) and `config/boards.json`.
- **Tests (94, offline):**
  - `test_policy_boundary`, `test_loop`, `test_wrong_versions_js2`, `test_budget_gate`, `test_providers`, `test_path_index`, `test_path_index_review`;
  - the 43 JS1 tests, unchanged.
- **Evidence:**
  - `runs/<stamp>-live/` and `runs/<stamp>-seeded/`, each with `trace.jsonl`, `report.json`, `report.md` and `raw/` (the saved raw responses);
  - `runs/finished-wrong-demo/`;
  - `state/`;
  - `logs/01`–`11`;
  - `review/`.
