# Job-Search Agent 2 — The Loop, the Tools, and the Diff

Varnika M · INFO 7375, Fall 2026

My JS1 agent watched one board. This version runs a **bounded loop** over four boards on three applicant-tracking systems (Greenhouse, Lever, Ashby), one of which fails on purpose. Every request and file write goes through a **permission policy enforced in code**. Every run ends with exactly one exit (`finished`, `incomplete`, `budget_exhausted` or `error`), and a separate program, `check_run.py`, checks each run from the outside.

The rules came first: [GATE.md](GATE.md), committed before any code (`040be50`). Who did what is in [SOURCES.md](SOURCES.md), and my log is in [FRICTIONAL.md](FRICTIONAL.md).

## What I started from

- **My JS1 work** (`../js1-contract-and-watch/`):
  - The rule R1–R5, `agent/rule.py`, is copied **byte-identical** (SHA-256 `2aa42900…`).
  - The fictional-résumé check is JS1's, adapted to take text, so it no longer opens a file itself: `agent/resume.py`.
  - The persona, Aarav Patel, is the same file (SHA-256 `f6ee24e4…`).
  - JS1's Anthropic state (675 ids seen on 2026-10-31) is the starting state for the Anthropic board (`scripts/import_js1_state.py`), so the first JS2 run was a real watch over 10 days.
- **The Reallocation Engine** (`nikbearbrown/the-reallocation-engine`, my local copy, read only, commit `bb22533`): its Lever and Ashby providers, `scripts/ats/providers/lever.mjs` and `ashby.mjs`, gave the endpoints and field names. I rewrote them in Python, in `agent/boards.py`. No code was copied.
- **Not** Lectern.

## Language, toolchain, commands

| What | Version | Needed for |
|---|---|---|
| Python, standard library only | 3.9 or later (tested on 3.9.6, macOS) | everything |
| git | any | cloning |
| Network access to `boards-api.greenhouse.io`, `api.lever.co`, `api.ashbyhq.com` | — | live runs only |

Nothing needs to be installed. The agent does not call Claude or any other model.

From a fresh clone:

```bash
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/varnika-m/js2-loop-tools-diff

python3 -m unittest discover -s tests -t .     # 121 tests; no network except local servers on 127.0.0.1
python3 check_run.py jobs/runs/2026-11-10T215306Z.json   # the independent check, on a saved run
python3 -m agent.loop                          # a live run: 4 GET requests; writes jobs/; exit code 0/1/2/3
```

The exit codes are `finished` 0, `error` 1, `incomplete` 2 and `budget_exhausted` 3. A live run continues from the committed state in `jobs/state/`. Other options:

```bash
python3 -m agent.loop --max-requests 2         # lower a budget (raising one is refused)
python3 -m agent.loop --fixture ashby/linear=fixtures/FILE   # a seeded run from a saved response
python3 -m agent.loop --approve-state-reset lever/palantir   # my approval for one state reset, this run only
```

To replay the finished-wrong demonstration without network, in a copy, because it refuses to overwrite `finished-wrong/`:

```bash
cp -R . /tmp/js2-copy && cd /tmp/js2-copy && rm -rf finished-wrong && python3 scripts/finished_wrong_demo.py
```

**Checked on 2026-11-10 from a fresh clone** of `02e3655` in a scratch folder:
- 113 tests OK.
- `check_run.py` gave the same verdicts on all three saved live runs.
- The demonstration replayed with the same exits (A `finished`, C `incomplete`, B `finished`, and check_run exit 1 on B).

## What ran

### Live runs (`jobs/runs/`): every one is a real fetch of the four boards on 2026-11-10

| Run | Who ran it, on what code | Exit | Anthropic (Greenhouse) | Palantir (Lever) | Linear (Ashby) | Deliberate failure | Budget used | `check_run.py` |
|---|---|---|---|---|---|---|---|---|
| [`2026-11-10T212848Z`](jobs/runs/2026-11-10T212848Z.md) | Claude Code, at `762801a` | `incomplete` (2) | 677 postings, **80 new** since JS1, 78 gone | 304, baseline | 33, baseline | `404`, requested once, no counts | 4/8 requests, 3.6/120 s | SUPPORTED |
| [`2026-11-10T214509Z`](jobs/runs/2026-11-10T214509Z.md) | **me**, in my terminal, at `a852e45` (after the patch) | `incomplete` (2) | 677, 0 new, **gone 78 (wrong, should be 0)** | 304, 0 new | 33, 0 new | `404`, once | 4/8, 4.4 s | **NOT SUPPORTED**: `gone_recomputed` |
| [`2026-11-10T215306Z`](jobs/runs/2026-11-10T215306Z.md) | Claude Code, at `f51b6c8` (all fixes) | `incomplete` (2) | 677, 0 new, gone 0 | 304, 0 new | 33, 0 new | `404`, once | 4/8, 17.9 s | SUPPORTED |

All three end `incomplete`, never `finished`, because board 4 is a name that does not exist. That is the error policy working (GATE.md section 4): the board gets `failed: not_found`, no counts (`null`, not 0), no state file, no retry, and a line telling me to check the name. Run 2's wrong `gone` is a real bug that the independent check caught in a real run ([REVIEW-FINDINGS.md](REVIEW-FINDINGS.md), row 7b). Its record was not edited.

**The trace of one real run, with the deliberate failure:** [`jobs/runs/2026-11-10T212848Z.trace.jsonl`](jobs/runs/2026-11-10T212848Z.trace.jsonl), 13 lines. Every step is one JSON line: start, each fetch (URL, policy decision, timeout, HTTP status, raw file, SHA-256), classify, compare, and exit. Each line carries the budget left after it. The deliberate failure is the fetch with `"http_status": 404`, then `classify` `failed: not_found`, and no `compare` line.

**Saved raw responses:** `jobs/raw/`, byte for byte, gzip-compressed (`gunzip -c FILE`). They include the 404 bodies. Each one's SHA-256 is in the trace.

### The finished wrong answer ([FINISHED-WRONG.md](FINISHED-WRONG.md)): SEEDED, with one CONSTRUCTED response

Wrong version W5 treats an empty board as "no new jobs". It ended `finished` on a constructed empty Linear response. `check_run.py` said **NOT SUPPORTED** (Linear had 33 postings in its last good run). The real agent, on the same bytes, said `incomplete` with Linear `suspect: empty`, and the check said SUPPORTED.

### The permission policy ([POLICY.md](POLICY.md))

30 boundary cases, B01–B28 plus B12b and B12c, each with its outcome **predicted before the tests ran**. The cases are:
- hosts off the list, subdomains, an allowed name hidden in the query, `http`, credentials, a port, `POST`, an apply path, `mailto:`, and `..` in the URL;
- `..`, the `jobs-evil` prefix trick, a folder symbolic link and a file symbolic link out of `jobs/`;
- a read versus a write of the same file;
- overwriting saved evidence;
- a state reset that **needs my approval**, given or not given, and for which board.

All 30 behaved as predicted, though B14 first passed for the wrong reason (see its row). Wrong versions W1–W4 of the checks were run, and each one makes its boundary test fail.

### The review packet ([REVIEW-PACKET.md](REVIEW-PACKET.md))

1. The change: the real network code ignored its timeout on a slow body.
2. Claude Code reproduced it, and the test was committed before the patch (`8ddfec0`). **I ran it myself, before the patch, and saw it fail.**
3. The patch is `91bfbda`. I read the diff, ran the suite, and ran live run 2 on the patched code.
4. **My decision: REVISE, then ACCEPT.** In my words: the test should fail immediately if the private `._sock` attribute is missing. That revision is `764c262`. I ran the guard test myself (3 OK) and accepted the revised patch, without claiming every timeout problem is fixed.
5. One case the test still misses: slow **headers**, which held a 1-second request for 21 s.

### My later decision on the time budget ([GATE.md](GATE.md), Decisions, November 10, 2026)

After findings 2 and 5, I decided that an invalid or unreliable time budget must stop the run, and that `check_run.py` must enforce the same time budget as the agent. Tests came first (`304b599`, 5 of 6 failed: a clock giving NaN let a run end `finished` with no time limit). The changes are `71491b1`.

### Other reviews ([REVIEW-FINDINGS.md](REVIEW-FINDINGS.md))

A separate Claude reviewer reported 8 findings. Each was reproduced as a test before any fix. 7 are fixed, and 2 are open decisions for me in GATE.md (8b, 8c). Row 7b, the wrong `gone`, was found in my own live run 2.

## What is in this folder

| Path | What it is |
|---|---|
| `GATE.md` | exits, budgets, repeat rule, error policy, permission policy, wrong versions: written first |
| `POLICY.md` | the boundary-test table, with predictions |
| `FINISHED-WRONG.md`, `finished-wrong/` | the demonstration, with its own config, persona copy, fixtures and runs |
| `REVIEW-PACKET.md`, `review/` | the review packet and its saved command outputs (mine and Claude Code's) |
| `REVIEW-FINDINGS.md` | the independent reviewer's findings and what happened to each |
| `agent/` | `loop.py` (the loop, budgets, exits, trace), `policy.py` (decides), `tools.py` (the only file that touches the network or disk), `boards.py` (the three systems), `rule.py` (JS1, unchanged), `resume.py` |
| `check_run.py` | the independent check. It does not import `agent/` |
| `config/boards.json` | the four boards |
| `persona/` | the fictional résumé (`@example.com`, 555 phone) |
| `jobs/` | everything the agent writes: `raw/`, `runs/` (record, report, trace and check per run) and `state/` |
| `scripts/` | the one-time JS1 state import and the demonstration (not the agent) |
| `tests/` | 121 tests |

Left out: caches, credentials (there are none), my real résumé, and the Claude Code conversation transcripts, which stay on my machine.

## Sign-off — Job-Search Agent 2

*Written by me, Varnika M, and pasted in word for word by Claude Code.*

**Checked:**
- The agent watches Greenhouse, Lever and Ashby.
- The agent records its results and handles a failed board.
- The permission rules are checked through boundary tests.
- The independent check can identify an incorrect result.
- The socket guard test passes when the socket is found and fails when `_sock` is missing.

**How I checked:**
- I ran tests in my own terminal.
- I ran the live agent and checked its reports.
- I read the code diff.
- I checked the results from the independent checker.
- Claude Code helped write the code and tests. I reviewed the results and made the final decisions.

**Not checked:**
- I did not test every possible response from all three job-board providers.
- I did not test every possible Python version.
- I did not test every possible network failure or slow response.
- I did not test the macOS system proxy settings.

**Not claiming:**
This agent does not guarantee that every matching job will be found. It does not apply for jobs, send emails or messages, or log in to any website. Its results are limited to the boards and tests included in this project.

**Signed or withheld:** Signed, Varnika M, 2026-11-10

### The detailed draft behind it (Claude Code's, not signed)

*Claude Code's draft, written from the record before I wrote my own sign-off above. I did not sign it. It is kept because it names the tests and the specific gaps.*

**Checked**

- **A stop is not a success.**
  - Tests: `test_deliberate_failure_makes_the_run_incomplete_not_finished`, `test_request_budget_runs_out_before_every_board`, `test_seconds_budget_runs_out_before_a_board`, `test_exit_codes`.
  - Real runs: all three ended `incomplete`, with exit code 2.
- **A failed or empty board invents nothing.**
  - Tests: `test_not_found_has_null_counts_and_no_state`, `test_failure_after_a_good_run_leaves_state_byte_for_byte_unchanged`, `test_empty_board_is_suspect_not_no_new_jobs`.
  - Real runs: the deliberate 404 was requested once in each.
- **Retries only where sound.** Tests: `test_not_found_is_requested_exactly_once`, `test_service_unavailable_is_tried_three_times_then_fails` (sleeps 2 s, then 4 s).
- **The policy is in code.**
  - Boundary tests B01–B28, B12b, B12c, all as predicted.
  - `test_refused_write_writes_nothing` and `test_refused_fetch_sends_nothing`.
  - `test_no_code_outside_tools_touches_the_network_or_writes_files`.
  - W1–W4 are caught.
- **Budgets cannot be raised.** Tests: `test_raising_a_budget_is_refused_before_the_run_starts`, `test_nan_cannot_switch_a_budget_off`, `test_budgets`, which compares the code to GATE.md's table.
- **The real network code keeps its timeout on a slow body.** `test_slow_trickle_body_stops_at_the_timeout`: I ran it before the patch and saw it fail. After the patch I ran the suite and it was OK.
- **A finished wrong answer is caught from the outside.** `test_finished_wrong_answer_is_caught` and the demonstration (run B: NOT SUPPORTED).
- **New ids recomputed.** `check_run.py` recomputed run 1's 80 new Anthropic ids from JS1's saved 2026-10-31 responses, without the loop's state, and they matched.

**How**

- **By hand:**
  - I ran the review test before the patch (1 FAIL).
  - I ran the suite after it (96 OK).
  - I read the diff.
  - I ran live run 2 myself.
  - I made the REVISE decision, ran the revision's guard test (3 OK), and accepted the revised patch.
- **By a test written before the code it tests:** the review test (`8ddfec0`) was committed before the patch (`91bfbda`), and every review-finding test before its fix (`7e09390`, `9a2179e`, `3e48c6c`). **Claude Code wrote these tests, not me.** I saw the review test fail on my machine before the patch.
- **By recomputation:** `check_run.py` recomputes counts, new ids and gone from the raw bytes. Claude Code wrote it.
- **With Claude's help:** everything else. Claude Code drafted GATE.md, which I kept unchanged ("ok"), and wrote all the code, tests, documents and runs 1 and 3. A separate Claude reviewer found 8 defects.

**Not checked**

1. **Slow headers, DNS and TLS handshakes are not bounded.** A server sending headers slowly held a 1-second request for 21 s on the final code. A whole run can still pass its seconds budget this way.
2. **A redirect to a different board on an allowed host would be followed, and its postings filed under the original board** (finding 8c). GATE.md allows it, and I have not decided to change GATE.md. 8b, a `503` with a long `Retry-After`, is also open.
3. **"New by id" is not "newly posted".** 9 of run 1's 80 new Anthropic ids have a `first_published` date before 2026-10-31, so they were not on JS1's board but are not new postings. I did not find out why.
4. **Completeness of each response.** I did not check that Lever's API returns every posting in one response (304 is taken as all of them), or compare Greenhouse's `meta.total`. Only a drop to **zero** is caught; a partial response is not.
5. **I did not read the test code line by line.** The code, the tests, `check_run.py` and the reviewer are all Claude. A misunderstanding they share would not be caught.
6. **Terms of use.** I did not read Greenhouse's, Lever's or Ashby's terms for these public endpoints. In all, 12 agent requests were made (three runs of 4), plus 10 one-off requests by Claude Code while choosing boards (listed in SOURCES.md).
7. **The gap between check and open in `tools.py`** (a path swapped between the policy check and the open) is not tested. Neither is the `._sock` path under HTTPS by a test; live runs 2 and 3 only.

**Not claiming**

- That the agent finds good jobs for Aarav or for anyone real. All 80 new Anthropic postings are `NOT_MATCH` by JS1's rule.
- That the 80 new ids are 80 new jobs (Not checked, item 3).
- That `check_run.py` catches every wrong run: it missed run 2's wrong `gone` until a check for it was added.
- That the policy would stop a determined local attacker (item 7), or that the reviewer found every defect.
- That any result holds for other boards, another day or another persona.


## Driver's seat

| Part | What Claude should do (and did) | What I should do (and did) | Why that part stays mine | Evidence |
|---|---|---|---|---|
| **The loop:** the gate | Draft exits, budgets, retries and policy from the assignment | Read it, change or keep it, and own the numbers. I kept the draft unchanged ("ok") | A budget changes only by my written decision. If I cannot defend "why 2 retries?", it is not my gate | `040be50` before any code; GATE.md header |
| **The loop:** build and run | Write the code and tests; run live runs 1 and 3; reproduce bugs before fixing them | Run a live run myself (run 2); read the trace and reports | I am the one calling real companies' endpoints, under their terms | `3bd3518`; [review/6-after-patch-varnika-run.txt](review/6-after-patch-varnika-run.txt) |
| **The loop:** escalations | Stop, mark the board, and tell me what to check (`not_found`: the name; `empty`: the public page) | Act on the escalation. For the deliberate board, the name is invented on purpose, so nothing to fix | The agent must not guess past a failure. A person decides what a failure means | the report line for `not_found` in each run |
| **The review:** reproduce and test | Find the defect, write the test, commit it before the patch, write the patch | Run the failing test **myself** before the patch | A test only Claude ran proves Claude's claim; my run makes it my evidence | `8ddfec0` before `91bfbda`; [review/2-before-patch-varnika-run.txt](review/2-before-patch-varnika-run.txt) |
| **The review:** decision | Lay out the evidence for and against; suggest an option when asked | Decide, in my words: **REVISE**, the test must fail at once if `._sock` is missing. Then, after running that test myself, **ACCEPT** | Claude reviewing Claude's patch is not independent. Accepting code into my agent is my decision | REVIEW-PACKET.md section 6; `764c262` |
| **The review:** independent check and reviewer | Write `check_run.py`; start a separate reviewer; turn its findings into tests first | Decide the open GATE.md questions (8b, 8c), and decide whether to sign | The open findings are policy choices. My name is the one on the sign-off | REVIEW-FINDINGS.md; the sign-off above |
