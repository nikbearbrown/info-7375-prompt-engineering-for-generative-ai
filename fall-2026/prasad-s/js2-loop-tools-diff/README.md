# Job-Search Agent 2 — the loop, the tools, the diff

Written 2026-11-08 (JS2-CP10). Every number, time and claim below is taken
from a file in this folder or a commit message, and cited, or, where marked
"(Prasad, confirmed 2026-11-08; not in a committed file)", rests on Prasad's
confirmation. Commits are cited by checkpoint ID (the first word of the
commit subject, e.g. JS2-CP6).

## What this is

Job-Search Agent 2 is a bounded loop that watches five job boards, three on
Greenhouse and two on Ashby, one of which fails on purpose, and reports for
each board the postings that are new since its last run (GATE.md §0, §1).
Every fetch, read and write passes through one permission check in a tool
layer, under the policy in GATE.md §5, and a run is held to 5 boards, 10
requests and 60 seconds (GATE.md §2). The agent never calls Claude: every new
posting carries the fixed line "rejected — no saved reply (judge not run in
JS2)" (GATE.md §1; CONTRACT.md v0.5 item 7).

**Started from:** Job-Search Agent 1, `js1-contract-and-watch/` at commit
`bff5356` (JS1-CP18, 2026-10-31), as signed off on 2026-10-31 (GATE.md header).
Its agent, tests, tools, CONTRACT.md, config.json, resume_persona.json and
.gitignore were copied in unchanged, via git archive, with `diff -r` clean and
45/45 tests passing (JS2-CP3).

**Lectern** (`fall-2026/nik-bear-brown/lectern/`) was used as a reference
only. No Lectern file is in this folder (`git ls-files`). It is cited for the
Ashby URL pattern (CONTRACT.md v0.5 item 1: "pattern from Lectern,
collect.py:52") and as precedent for the User-Agent (CONTRACT.md v0.8 item 1:
"Lectern does the same (collect.py:42)"). See SOURCES.md.

## Language and toolchain

- Python 3.11 or newer, standard library only, tests with `unittest`. No
  `pip install` is required or permitted (CONTRACT.md header, "Language /
  toolchain").
- On Prasad's machine: Python 3.13.17, run as `python3.13`; the Mac's default
  `python3` is 3.9.6, which is too old (CONTRACT.md header).
- Standard-library modules imported by `agent/`: argparse, dataclasses,
  datetime, hashlib, html, json, os, pathlib, re, socket, sys, time, urllib.
- Git, for the two reproductions below (they extract earlier checkpoints with
  `git archive`).

## Commands

From a fresh clone (the course repository, per `git remote -v`):

```bash
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
```

```bash
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/js2-loop-tools-diff
```

Every command below runs from that folder. The JS2 commits reach a fresh
clone only once they are pushed: on 2026-11-08 the local branch was ahead of
`origin/main` (`git status`). The test commands make no network request
("Offline only: no test touches the network", `tests/support.py`; the loop
tests replace the tool layer's one network function, and any socket fails the
test, `tests/test_loop.py` docstring).

**Full test suite** (CONTRACT.md header gives this command):

```bash
python3.13 -m unittest discover -s tests -v
```

Last result, 2026-11-08: `Ran 109 tests` … `OK`. The suite was 109/109 after
JS2-CP8c (commit message).

**The W5 test alone** (GATE.md v0.3 §6 W5):

```bash
python3.13 -m unittest discover -s tests -p test_review_empty_board.py -v
```

**The boundary tests alone** (GATE.md §7, B01–B11, plus eight policy-rule
tests in the same file; 19 tests in all):

```bash
python3.13 -m unittest discover -s tests -p test_boundary.py -v
```

**A live run.** This sends real GET requests to boards-api.greenhouse.io and
api.ashbyhq.com (five requests at least, ten at most: GATE.md §2), and writes
new files into `state/`, `evidence/` and `output/`:

```bash
python3.13 -m agent
```

Options (`agent/__main__.py`): `--config PATH` (default `config.json`; the
project folder is the folder that holds the config, `agent/run.py`),
`--seed BOARD_KEY=PATH` (repeatable; read that board from a saved response
under `evidence/` instead of fetching it, CONTRACT.md v0.7 item 8) and
`--approve PATH` (repeatable; GATE.md §5). Exit codes: 0 finished (with or
without failures), 1 error, 2 refused, 3 incomplete, 4 budget-exhausted
(CONTRACT.md v0.7 E18).

**The CP7 demo (the finished wrong answer), reproduced in a throwaway copy.**
This extracts the folder as it was at JS2-CP7, before the W5 patch. It makes
no request, because all four boards in `config_demo.json` are seeded. The
config is copied over `config.json` because the project folder is the
config's folder (`agent/run.py`).

```bash
C=$(git log --format=%H -1 --grep='^JS2-CP7:' -- .)
T=$(mktemp -d)
git archive "$C" -- . | tar -x -C "$T"
cp "$T/evidence/demo_finished_wrong_answer/config_demo.json" "$T/config.json"
cd "$T" && python3.13 -m agent \
  --seed greenhouse:stripe=evidence/greenhouse_stripe_2026-11-07T000611Z_a1.json \
  --seed ashby:notion=evidence/ashby_notion_2026-11-07T000611Z_a1.json \
  --seed greenhouse:duolingo=evidence/constructed/duolingo_EMPTY_constructed_2026-11-07.json \
  --seed greenhouse:robinhood=evidence/greenhouse_robinhood_2026-11-07T000612Z_a1.json
```

Expected output: the lines of
`evidence/demo_finished_wrong_answer/demo_terminal.txt` ("finished", with
duolingo "ok — 0 jobs, 0 new"), with a new report file name.

**The after-patch rerun**: the same commands with `JS2-CP8c` in place of
`JS2-CP7`. Expected output: the lines of
`evidence/demo_finished_wrong_answer/after_patch_terminal.txt` ("finished —
with failures: greenhouse:duolingo", with duolingo "failed — empty board: 0
jobs, 59 ids saved before"), with a new report file name.

Both reproductions were checked on 2026-11-08 in throwaway folders, with
the network disabled, and their board lines and exit lines matched the two
committed terminal files exactly. Prasad ran the original demo and the rerun
in throwaway copies (/tmp/js2_demo and /tmp/js2_after), with the same seeds as
these commands (Prasad, confirmed 2026-11-08; not in a committed file).

## What ran

Local time is UTC-5 (EST), the offset on every JS2 commit timestamp.

| Run | Checkpoint | UTC | Local (UTC-5) | Source |
|---|---|---|---|---|
| Smoke run 1, before the fix | JS2-CP5c | 2026-11-06 23:36:14 | 2026-11-06 18:36:14 | report file name printed in Prasad's terminal (not saved) |
| Smoke run 2, after the fix | JS2-CP5c | 2026-11-06 23:47:41 | 2026-11-06 18:47:41 | report file name printed in Prasad's terminal (not saved) |
| Run 1, live baseline | JS2-CP6 | 2026-11-07 00:06:11 | 2026-11-06 19:06:11 | `output/run_report_2026-11-07T000611Z.json` (`run_at`) |
| CP7 demo, seeded | JS2-CP7 | 2026-11-07 23:38:28 | 2026-11-07 18:38:28 | `evidence/demo_finished_wrong_answer/run_report_2026-11-07T233828Z.json` (`run_at`) |
| CP7 independent check | JS2-CP7 | 2026-11-07 23:40:39 | 2026-11-07 18:40:39 | `evidence/demo_finished_wrong_answer/independent_check.txt` |
| W5 test, failing before the patch | JS2-CP8b | 2026-11-08 00:42:10 | 2026-11-07 19:42:10 | `evidence/tests/cp8_W5_failing_before_patch_2026-11-08T004210Z.txt` (file name) |
| After-patch rerun, seeded | JS2-CP8c | 2026-11-08 01:02:25 | 2026-11-07 20:02:25 | report name in `evidence/demo_finished_wrong_answer/after_patch_terminal.txt` |
| Run 2, live | JS2-CP9 | 2026-11-08 01:54:37 | 2026-11-07 20:54:37 | `output/run_report_2026-11-08T015437Z.json` (`run_at`) |
| Run 2 recount | JS2-CP9 | 2026-11-08 02:07:56 | 2026-11-07 21:07:56 | `evidence/terminal/run2_recount_by_me_2026-11-08T020756Z.txt` (file name) |
| Boundary run (twice) | JS2-CP9b | 2026-11-08 02:10:20 and 02:10:24 | 2026-11-07 21:10:20 and 21:10:24 | `evidence/tests/boundary_B01-B11_run_by_me_*.txt` (file names) |

### Smoke runs, not committed (JS2-CP5c)

From the JS2-CP5c commit message: "Found by my smoke run: Ashby's API (behind
Cloudflare) answered Python's default User-Agent with 403, error 1010, for
every board. Confirmed with curl; an honest identity gets 200/404."
CONTRACT.md v0.8 item 1 adds the date (2026-11-06), the default User-Agent
("Python-urllib/3.13"), and which board got which answer: 200 for notion and
404 for js2nosuchboard. The fix, which sends
`User-Agent: js2-loop-tools-diff/0.7 (INFO 7375 course project)` on every
request, was written test-first. The failing test output is
`evidence/tests/cp5c_user_agent_failing_before_fix_2026-11-06.txt`
("FAILED (failures=9)"), and the suite was 108/108 after the fix (JS2-CP5c).

No smoke-run output is committed: no file in this folder records it. There
were two, both run by Prasad on 2026-11-06 in throwaway copies (/tmp/js2_smoke
and /tmp/js2_smoke2). The source is Prasad's terminal output, which was not
saved; the times come from the report file names it printed (Prasad,
confirmed 2026-11-08; not in a committed file).
- Smoke run 1, 2026-11-06T23:36:14Z (18:36 local): four boards seeded from the
  2026-11-05 snapshots, and js2nosuchboard live: "failed — HTTP 403". Its
  saved body was Cloudflare error 1010, read in the copy and not saved.
- Smoke run 2, 2026-11-06T23:47:41Z (18:47 local), after the fix: notion live,
  "ok — 154 jobs, 0 new (baseline)"; js2nosuchboard live, "failed — not found
  (404)".

### Run 1 — live baseline (JS2-CP6)

From `evidence/terminal/run1_terminal_2026-11-07T000611Z.txt` and
`output/run_report_2026-11-07T000611Z.json`:

| Board | Line | Attempts | Status | Elapsed (s) |
|---|---|---|---|---|
| greenhouse:stripe | ok — 765 jobs, 0 new (baseline) | 1 | 200 | 0.398 |
| ashby:notion | ok — 154 jobs, 0 new (baseline) | 1 | 200 | 0.189 |
| greenhouse:duolingo | ok — 59 jobs, 0 new (baseline) | 1 | 200 | 0.232 |
| greenhouse:robinhood | ok — 150 jobs, 0 new (baseline) | 1 | 200 | 0.254 |
| ashby:js2nosuchboard | failed — not found (404); attempts: 1 | 1 | 404 | 0.157 |

- Exit: "finished — with failures: ashby:js2nosuchboard".
- Budgets used: boards 5 of 5, requests 5 of 10, seconds 1.345 of 60.
- State read: none, so every board is a baseline. State written:
  `state/state_2026-11-07T000611Z.json`.
- **Label:** the report says `contract_version` "v0.6" and `gate_version`
  "v0.2". The contract was v0.7 at the time. v0.7 recorded decisions the code
  already implemented, so run 1 behaved as v0.7 says; the report is not edited
  (CONTRACT.md v0.8 item 3; JS2-CP6 commit message).

### CP7 demo — the finished wrong answer (JS2-CP7)

A seeded run in a throwaway copy. Four boards were seeded from run 1's raw
responses, and duolingo from a constructed empty response,
`evidence/constructed/duolingo_EMPTY_constructed_2026-11-07.json`
(`{"jobs": [], "meta": {"total": 0}}`, 35 bytes). Sources: JS2-CP7 commit
message; `run_report_2026-11-07T233828Z.json`; `config_demo.json`, which lists
four boards and leaves out js2nosuchboard.

- Agent output (`demo_terminal.txt`): exit "finished", with
  greenhouse:duolingo "ok — 0 jobs, 0 new". The other three boards were "ok",
  0 new each (stripe 765, notion 154, robinhood 150 jobs).
- Budgets used: boards 4 of 5, requests 0 of 10, seconds 0.049 of 60. State
  read: `state/state_2026-11-07T000611Z.json`.
- Independent check, by hand, with no agent code (`independent_check.txt`): 59
  duolingo jobs in run 1's saved raw response, and 59 on the live board at the
  time of the check.
- The JS2-CP7 commit message says: "Prediction written before the run
  matched." Prasad wrote the prediction in a notebook before the run; the
  notebook is not in this folder (Prasad, confirmed 2026-11-08; not in a
  committed file).
- The demo report is also labeled contract "v0.6" and gate "v0.2".
- What followed: GATE.md v0.3 split §4's zero-jobs row and added W5
  (JS2-CP8a). The W5 test failed first (JS2-CP8b), and the patch followed
  (JS2-CP8c).

### After-patch rerun (JS2-CP8c)

The CP7 demo, rerun after the W5 patch (`after_patch_terminal.txt`):

- Exit: "finished — with failures: greenhouse:duolingo".
- greenhouse:duolingo: "failed — empty board: 0 jobs, 59 ids saved before".
- stripe 765, notion 154, robinhood 150 jobs: "ok", 0 new each.
- Its report, `output/run_report_2026-11-08T010225Z.json`, was written in the
  throwaway copy and is not committed.
- Suite after the patch: 109/109. W5 passes (JS2-CP8c commit message).

### Run 2 — live, a new day (JS2-CP9)

From `evidence/terminal/run2_terminal_2026-11-08T015437Z.txt` and
`output/run_report_2026-11-08T015437Z.json`:

| Board | Line | Attempts | Status | Elapsed (s) |
|---|---|---|---|---|
| greenhouse:stripe | ok — 766 jobs, 1 new | 1 | 200 | 0.396 |
| ashby:notion | ok — 154 jobs, 0 new | 1 | 200 | 0.219 |
| greenhouse:duolingo | ok — 59 jobs, 0 new | 1 | 200 | 0.188 |
| greenhouse:robinhood | ok — 150 jobs, 0 new | 1 | 200 | 0.223 |
| ashby:js2nosuchboard | failed — not found (404); attempts: 1 | 1 | 404 | 0.097 |

- The new posting: 8250475, "Account Executive, SMB Grower (French speaking)",
  location "Toronto, Canada ". Rule verdict: not_relevant. Claude line:
  "rejected — no saved reply (judge not run in JS2)".
- Exit: "finished — with failures: ashby:js2nosuchboard".
- Budgets used: boards 5 of 5, requests 5 of 10, seconds 1.236 of 60.
- State read: `state/state_2026-11-07T000611Z.json` (run 1's). State written:
  `state/state_2026-11-08T015437Z.json`.
- Labels: gate "v0.3", contract "v0.8".
- The agent trace of this run is the "trace" list in
  `output/run_report_2026-11-08T015437Z.json`: every request, with its board,
  attempt, URL, status, elapsed time and saved file.
- **Recount**, by Prasad, from the raw responses only, with no agent code
  (`run2_recount_by_me_2026-11-08T020756Z.txt`):
  - stripe: 765 ids in run 1, 766 in run 2; new ['8250475']; gone 0.
  - notion: 154 and 154; duolingo: 59 and 59; robinhood: 150 and 150. Each has
    no new ids and 0 gone.

  This agrees with the agent (JS2-CP9 commit message).

### Boundary run (JS2-CP9b)

The boundary tests, run twice by Prasad. Both outputs are saved in
`evidence/tests/` (02:10:20Z and 02:10:24Z):

- B01–B11 and the eight policy-rule tests all print "ok".
- "Ran 19 tests in 0.030s" and "Ran 19 tests in 0.029s", each "OK".
- The two files differ only in that time line.

GATE.md §7 holds the predictions, written 2026-11-05 before any code. The
comparison is Prasad's: see "Boundary tests: predicted vs actual" below.

### Before JS2's code: probes and snapshots (no agent run)

- **Gate probes, 2026-11-02** (`evidence/gate_probes/probe_log.txt`, included
  in JS2-CP1). Ten GETs:
  - stripe, duolingo, robinhood (Greenhouse) and openai, notion (Ashby): 200.
  - miro, hubspot and js2nosuchboard (Greenhouse), and js2nosuchboard (Ashby):
    404.
  - Canva (SmartRecruiters): 200.
  - The OpenAI body (14,064,699 bytes) is not committed; its SHA-256 is in
    `evidence/gate_probes/SHA256SUMS.txt` (JS2-CP1 commit message).
- **Snapshots, 2026-11-05** (`evidence/snapshots/snapshot_log.txt`;
  JS2-SNAP). Four GETs, all 200: stripe 763 jobs, duolingo 56, robinhood 151,
  notion 150. The job counts are recounted from the saved bodies.

## Where everything is

| Path | What it holds |
|---|---|
| `GATE.md` | Exits, budgets, repeat rule, error policy, permission policy, wrong versions (W1–W5), boundary-test predictions. Currently v0.3 |
| `CONTRACT.md` | JS1's contract, amended for JS2 in v0.5–v0.8; §9 holds the amendment log |
| `config.json` | The five boards, the two-host allow-list, the persona path and the three working folders (CONTRACT.md v0.7 E1) |
| `resume_persona.json` | The persona the rule reads (carried over from JS1, JS2-CP3) |
| `agent/__main__.py` | Command line: `--config`, `--seed`, `--approve`; exit codes |
| `agent/run.py` | The loop, budgets, exits and the run report |
| `agent/tool_layer.py` | The only network and file I/O: fetch, read, write, list_dir, move; the User-Agent constant |
| `agent/policy.py` | The one permission check (GATE.md §5) |
| `agent/adapters.py` | Greenhouse and Ashby responses into postings |
| `agent/config.py`, `agent/state.py`, `agent/fetch.py` | Config parsing; per-run state files; evidence and seeds |
| `agent/persona.py`, `agent/replies.py`, `agent/errors.py` | Carried over from JS1, unchanged since JS2-CP3 (`git diff`) |
| `agent/rule.py` | JS1's rule, plus Ashby's step-4-only path (CONTRACT.md v0.7 item 5) |
| `tests/` | The suite (109 tests); `tests/expected/` holds JS1's expected-outcome tables |
| `tests/test_boundary.py` | B01–B11 and the policy-rule tests |
| `tests/test_loop.py` | The loop: W3, W4, exits, budgets, errors, state, seeds |
| `tests/test_review_empty_board.py` | W5 |
| `tests/test_user_agent.py` | The User-Agent test (JS2-CP5c) |
| `tools/` | JS1's helper scripts, carried over; not called by the agent (CONTRACT.md v0.7 E20) |
| `state/` | Saved ids per run: `state_2026-11-07T000611Z.json` (run 1), `state_2026-11-08T015437Z.json` (run 2) |
| `output/` | Run reports with the agent trace: `run_report_2026-11-07T000611Z.json` (run 1), `run_report_2026-11-08T015437Z.json` (run 2) |
| `evidence/*_a1.json`, `*.sidecar.json` | Raw responses from runs 1 and 2, one file per attempt, each with a sidecar giving status, URL and UTC time (CONTRACT.md v0.7 item 1) |
| `evidence/gate_probes/` | Probes of 2026-11-02, read-only (GATE.md §5) |
| `evidence/snapshots/` | Board snapshots of 2026-11-05 |
| `evidence/constructed/` | The constructed empty duolingo response (labeled "constructed") |
| `evidence/demo_finished_wrong_answer/` | The CP7 demo: config, terminal output, report, state, independent check, and the after-patch terminal output |
| `evidence/terminal/` | Terminal output of runs 1 and 2, and the run 2 recount |
| `evidence/tests/` | Test output saved by Prasad: the User-Agent test failing, the W5 test failing, and the two boundary runs |

## Known limits

From CONTRACT.md v0.6 item 5:
- The 10 s timeout limits each wait on the socket, not the whole request: a
  server that sends one byte every 9 s never times out. The 60 s run budget is
  checked between requests, not during one.
- The read-only folders are not protected through a hard link the way GATE.md
  is: if `output/x` were a hard link to a snapshot file and an overwrite of
  `output/x` were approved, the snapshot would change.

From CONTRACT.md v0.7 item 9:
- If the state move fails after the report is written, the report on disk
  still says the state was written; only the printed and returned report
  records `state_error`.
- Between the check that the target does not exist and the rename there is a
  small race window. It is harmless for a single run at a time.
- The JS1 helpers in `tools/` write files directly, outside the policy. The
  agent never calls them.

From CONTRACT.md v0.8 item 4:
- A board whose saved section exists but is empty, `[]`, and which returns
  zero jobs is ok under GATE.md v0.3, since it holds no ids. That is correct,
  but no test pins it.
- A partial drop, such as 59 jobs falling to 3, is not caught.

From GATE.md v0.3's changelog, "Not covered":
- A partial drop, such as 59 jobs falling to 3, is still just a smaller board
  (the same limit as the one above).
- An empty first run: a board with no saved ids that reports zero jobs is ok
  under this rule (CONTRACT.md v0.7 item 6).

## Boundary tests: predicted vs actual

| ID | Case | Predicted (GATE.md §7, 2026-11-05, before any code) | Actual (my run, JS2-CP9b) | Match |
|---|---|---|---|---|
| B01 | Host off the allow-list | Refused; no request is sent; the refusal names the host | Refused under the host rule; no request was sent; the refusal named example.com (test_B01 ok) | Yes |
| B02 | Path with `..` | Refused; nothing is written | Refused under "inside the project folder only"; outside.txt was not created and nothing changed (test_B02 ok) | Yes |
| B03 | Prefix trick on the host | Refused; no request is sent | Refused under the host rule; no request was sent (test_B03 ok) | Yes |
| B04 | Symlink out of the output folder | Refused; nothing is written | Refused under "inside the project folder only", after the symlink was resolved; nothing was written outside or changed (test_B04 ok) | Yes |
| B05 | Read in an allowed folder | Allowed; the content is returned | Allowed; the file's exact bytes were returned (test_B05 ok) | Yes |
| B06 | Write to that same path | Refused; nothing is written | Refused under the read-only rule for evidence/gate_probes/; nothing changed (test_B06 ok) | Yes |
| B07 | Config write without approval | Refused; the file is unchanged | Refused; every reason cited the approval rule; config.json's bytes were unchanged (test_B07 ok) | Yes |
| B08 | Config write with approval | Allowed; the file is written, and the report records the flag | Allowed; the file was written, and the policy's approval record lists the flag as used (test_B08 ok). No real run writes config.json, so the flag's record is checked there rather than in a run report | Yes |
| B09 | Right host, wrong scheme | Refused; no request is sent | Refused under "https only", the only rule cited; no request was sent (test_B09 ok) | Yes |
| B10 | Userinfo trick | Refused; no request is sent | Refused under the userinfo and host rules; no request was sent; the refusal named evil.example (test_B10 ok) | Yes |
| B11 | Sibling-folder prefix trick | Refused; nothing is written | Refused, because output-evil/ is outside state/, evidence/ and output/ and no approval was given; nothing changed (test_B11 ok) | Yes |

All 11 match. The same file has eight more policy-rule tests, which Claude
Code added beyond my rows; they also passed, but they carry no prediction
of mine and are not part of this table.

## Review packet

See REVIEW_PACKET.md: the empty-board change (W5), from the CP7 defect through my test written before the patch (JS2-CP8b) to the accepted patch (JS2-CP8c).

## Sign-off

## Sign-off — Job-Search Agent 2

Checked:
- The permission layer holds at its boundaries: boundary tests B01–B11 (off-list host, `..` path, prefix-trick host, symlink out of output/, read allowed in gate_probes/, write to the same path refused, config write refused without --approve (B07) and allowed with it (B08), http scheme, userinfo trick, sibling-folder prefix trick) — predicted by me before any code (2026-11-05), and run by me on 2026-11-07 (JS2-CP9b); results table written from that saved output (JS2-CP11).
- W3: in both live runs js2nosuchboard is reported as failed — "failed — not found (404)" — and never as an empty board, and both runs end finished — with failures naming it (run 1, JS2-CP6; run 2, JS2-CP9). That a failed board keeps its saved ids is covered by the W3 test (constructed, written by Claude Code): js2nosuchboard itself never held ids, since it failed both times, so the live runs cannot show it.
- W5: a board with saved ids returning zero jobs is a failure, not an empty board — the test holds saved state with 59 ids for greenhouse:duolingo, as after run 1, delivers the empty 200 through the live path (network patched), and checks the board line ("failed — empty board: 0 jobs, 59 ids saved before"), the unchanged saved ids, the saved evidence, and the exit. The test was written before the patch and failed on the unpatched code (JS2-CP8b); the patch followed (JS2-CP8c).
- The User-Agent: every request carries the honest identity — tests/test_user_agent.py, written failing before the fix, after Ashby answered the smoke run 403 (Cloudflare 1010) (JS2-CP5c).
- Run 1 is a true baseline: five boards visited, nothing reported new, state saved for the four boards that answered (the failed board has no section) (state/state_2026-11-07T000611Z.json). Run 2, a new day, diffs against it: 1 new posting (Stripe, 8250475) and 0 on the other three watched boards.
- The CP7 demo and its independent check: a seeded empty response against saved ids produced a finished run with the wrong answer under GATE v0.2 §4, and the check — not the loop's own report — is what caught it (evidence/demo_finished_wrong_answer/).
- 109/109 tests pass — the copied JS1 suite (three of its test files adapted in CP5b, per CONTRACT v0.5–v0.7) plus the JS2 tests — run by me after JS2-CP8e.

How:
- B01–B11: predictions mine, made before any code; the suite typed by Claude Code (JS2-CP5a) and run by me (JS2-CP9b); the results table was typed by Claude.ai from my saved output and I checked each row.
- W5: by a test required before the patch existed — assertions mine (GATE §6), code typed by Claude Code — which failed first (JS2-CP8b), which is what makes its passing now mean anything.
- W3 and the exits: by reading both live run reports against GATE §1; the ids-kept property by the constructed W3 test.
- Run 2's diff: by recomputation — I recounted the new ids from the raw responses of runs 1 and 2, with no agent code (evidence/terminal/run2_recount_by_me_2026-11-08T020756Z.txt), and the recount agrees with the report: 1 new, Stripe 8250475.
- The User-Agent: checked twice — by my own curl checks (200 for Notion, 404 for the bad name) and by the test, which failed first.
- The demo: by an independent check whose commands Claude.ai wrote and I ran.
- This sign-off: drafted with Claude.ai's help from my checkpoint log; its numbers come from my own runs and recount, not from the reports alone.

Not checked:
- A partial drop: a board falling from 59 jobs to 3 is reported as a smaller board, not a failure — the v0.3 rule does not cover it, by design, and no test says otherwise.
- An empty first run: a board with no saved ids reporting zero jobs is "ok" under §4 (CONTRACT v0.7 item 6); if a board were empty from the start, nothing here would flag it.
- Real network failures: the timeout and 5xx paths were exercised with the network patched, never against a real outage; no live board has yet returned zero jobs against saved ids, so W5's rule has only been met in the constructed test.
- I did not read every line of Claude Code's code; the 31 build decisions (D1–D11, E1–E20) I reviewed and accepted at the decision level, not line by line. Tests run on my machine and Python only.

Not claiming:
- That any posting on any board is relevant or worth applying to: the judge was not run in JS2, and every new posting carries "rejected — no saved reply (judge not run in JS2)", which is a missing judgment, not a verdict.
- That the loop works for boards or ATSs beyond the five in GATE §0, or for a persona other than JS1's.
- That "new" in run 2 means newly posted — it means new to the agent since run 1's state.
- That the budgets (5 boards, 10 requests, 60 s) are the right budgets — only that the runs stayed inside them.

Signed or withheld: Prasad Shinde, 2026-11-08


## Driver's seat

Written by me. The evidence column points to commits and files anyone can check.

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence |
|---|---|---|---|---|
| Loop: the rules | Review my rules and flag what they leave open; never originate or quietly change a rule | Write GATE.md and decide every rule in it, before any code exists | The gate is the assignment. A rule Claude wrote and Claude's code then obeyed would prove nothing | GATE.md v0.1, written before any code (JS2-CP1); the review fixes I decided (JS2-CP2, GATE v0.2 changelog) |
| Loop: the build | Claude Code builds the permission layer and then the loop, to GATE.md and CONTRACT.md as written | Hand over the files as the only spec; review its 31 decisions (D1–D11, E1–E20) and accept or reject each | The code is the labor; the spec and the acceptance are the accountability. If I don't decide what gets built, I'm reporting Claude's agent, not mine | JS2-CP5a and JS2-CP5b commit messages |
| Loop: open questions | Claude Code stops and asks when the files don't pin something down — 4 questions in CP5a, 5 in CP5b — instead of deciding silently | Decide each question myself; the decisions enter CONTRACT.md as dated amendments | A decision the builder takes silently never reaches the record. Decided by me, it is an amendment anyone can check | Claude Code's 4 + 5 questions; CONTRACT v0.6 item 3, v0.7 items 1–5 |
| Loop: running and checking | Claude.ai writes the check commands I run — the recount script, the bypass grep, the curl checks; Claude Code runs the probes and snapshots at my instruction; Claude.ai types the results table from my output | Run the smoke run, runs 1 and 2, the recount, and the bypass grep myself | A run I didn't perform is a report I'm repeating. The checks count only if they're independent of the code being checked | Runs 1 and 2 (JS2-CP6, JS2-CP9); the recount; the bypass grep; the smoke run (JS2-CP5c) |
| Review: the defect | Claude.ai writes the demo's commands and the independent check's commands | Run the demo, read the finished-but-wrong answer, and decide the defect is in my rule, not the code | The loop had obeyed §4 as written. Calling my own rule wrong — and amending it before touching code — is the judgment this review exists for | The CP7 demo and independent check (JS2-CP7) |
| Review: the test | Claude Code types the W5 test code | Write the assertions (GATE §6), require the test before any patch, and watch it fail on the current code | Assertions are the rule stated as a test. If Claude writes them, the test checks Claude's reading of my rule, not the rule | W5 (JS2-CP8a); the failing test (JS2-CP8b) |
| Review: the patch | Claude Code writes the patch; Claude.ai helps me read the diff as a change in behavior, and I check its reading against the code | Read the diff and accept or reject it | The patch changes what the agent does. Accepting a diff I haven't read is how a fix becomes the next defect | The JS2-CP8c diff |
| Review: reading and deciding | Assemble REVIEW_PACKET.md from the evidence, with nothing in it I can't trace | Read the packet and after_patch_terminal.txt, and make the final call | The packet is evidence, organized. The decision on it is mine because I'm the one who signs for it | REVIEW_PACKET.md; after_patch_terminal.txt |
