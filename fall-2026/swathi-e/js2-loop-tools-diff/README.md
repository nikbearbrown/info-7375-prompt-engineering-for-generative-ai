# Job-Search Agent 2 — The Loop, the Tools, and the Diff

Drafted by Claude Code from the committed records; reviewed by Swathi.
Built on my JS1 agent: the starting point (`5a8f4cf`) copies the JS1 core
unchanged from JS1 commit `ebcd515`.

Labels: **record** = recomputable from the committed files and code;
**SIMULATED** = a constructed response, never fetched; **my input** = run or
decided by me (Swathi).

## What the agent does

For Priya Nair (a fictional F-1 OPT candidate), the agent loops over four
public job boards: Databricks and Stripe on Greenhouse, Plaid on Ashby, and a
deliberately nonexistent Greenhouse board. Every request, read and write goes
through a permission policy in code (`policy.py`), and the loop keeps to the
exits, budgets, repeat rule and error policy in my `GATE.md`. Each run saves
every raw response and a trace, reports new postings per board with my JS1
rule's verdict (a record), and ends with exactly one exit status; anything
other than `finished` is escalated to me. It never applies, emails, messages
or logs in anywhere.

## Language and toolchain

- Python, standard library only; nothing to install, no API key, no Claude
  call. Ran with Python 3.12.2 (Anaconda); the tests also pass with macOS's
  Python 3.9.6.
- Allow-listed hosts (exact match, https only): `boards-api.greenhouse.io`,
  `api.ashbyhq.com`.

## Commands

Run from this folder. **Quick check from a fresh clone** (tested 2026-11-07 in
an empty folder: a sparse clone of this folder only, about 9 MB, then 81
tests offline):

```bash
git clone --depth 1 --filter=blob:none --sparse -b js2-loop-tools-diff-swathi-e https://github.com/BESWATHI/info-7375-prompt-engineering-for-generative-ai.git js2 && cd js2 && git sparse-checkout set fall-2026/swathi-e/js2-loop-tools-diff && cd fall-2026/swathi-e/js2-loop-tools-diff
```

```bash
python3 -m unittest discover -s tests
```

**Independent check** (offline; the second file is SIMULATED). Expected: the
empty file is flagged `EMPTY, UNVERIFIED; DROP TO ZERO (923 -> 0)`, exit code 1.

```bash
python3 independent_check.py runs/2026-11-05T23-11-48-228373-0500/001-databricks-request.json runs/simulated-2026-11-05-finished-wrong-answer/SIMULATED-databricks-empty-200.json
```

**Finished-wrong-answer demo** (offline, SIMULATED). It refuses while its
committed folder exists (evidence is never overwritten); to rerun it in a
scratch clone, delete that folder first:

```bash
rm -rf runs/simulated-2026-11-05-finished-wrong-answer && python3 demo_finished_wrong_answer.py
```

**Live run** (network; writes a new `runs/<time>/` folder and updates
`state/seen_ids.json`). It always ends `incomplete`, exit code 1, because the
deliberate bad board fails:

```bash
python3 loop.py
```

## What ran

| What | When (ET) | Commit | Label |
|---|---|---|---|
| Live run 1 (baseline) | 2026-11-04 22:44:47 | `d8a5a7b` | record |
| Live run 2 | 2026-11-05 23:11:47 | `bd602a2` | record |
| Finished-wrong-answer demo | 2026-11-05 23:19:17 | `ae284ca` | SIMULATED input, real Nov 5 baseline |
| Review packet: fix and my runs | 2026-11-05 to 2026-11-07 | `5909627` … `4a3db26` … `4c08a7f` | my input + record |

## Where to find each required part

| Required part | Where |
|---|---|
| Exits, budgets, repeat rule, error policy, permission policy, wrong versions | `GATE.md` (`510a59a`; revisions `96dde19`, `d131b5f`) |
| Permission policy in code, ≥10 boundary cases | `policy.py`; my 15 predictions in `BOUNDARY-CASES.md`; case N is checked by `test_case_NN` in `tests/test_policy.py` |
| Loop over ≥3 boards, 2 ATSs, one deliberate failure | `loop.py`, `parsers.py`; tests in `tests/test_loop.py` |
| Agent trace with the deliberate failure | `runs/2026-11-05T23-11-48-228373-0500/trace.json` (observation 7: 404, no retry) and the Nov 4 run |
| Finished-wrong-answer demonstration | `runs/simulated-2026-11-05-finished-wrong-answer/` (`SIMULATED.md`), `independent_check.py` |
| Review packet | `review-packet/REVIEW-PACKET.md` and files 01–04 |
| Raw responses | `runs/<time>/NNN-<board>-request.json`, sha256 in each `trace.json` |
| Sign-off, driver's seat, friction | `SIGNOFF.md` (copied below), `FRICTIONAL.md` |

## Results

- **Live run 1 (record):** `incomplete`. Databricks 926, Stripe 759, Plaid 144
  postings, all baselines (0 new); the bad board returned a real 404 after one
  request. 4 requests, 3.1 s.
- **Live run 2 (record):** `incomplete`. Databricks 923, Stripe 768, Plaid 144;
  31 new postings (9, 20, 2), of which 1 is relevant by my rule: *AMER Data
  Analyst - Sales Strategy and Operations* (Stripe). Bad board: 404, no retry.
  4 requests, 2.1 s.
- **Demo (SIMULATED empty Databricks response):** the JS1 watch reports
  "0 new" and its saved ids go from 923 to 0; the independent check flags
  `DROP TO ZERO (923 -> 0)`; the JS2 loop reports `empty, unverified`, exit
  `incomplete`, and keeps the 923 ids.
- **Review packet:** in my real Nov 4 and Nov 5 runs, 41 Plaid postings failed
  my rule's location check because of office-only names, 2 of them on that
  check alone (record, counted by Claude Code). Before the fix 4 tests failed
  (5 failures); after it, all 81 passed and posting `1bcfe93d` became relevant
  (my input: files 02–04).
- **Tests (record):** 81, offline, no network.

## Boundary tests: my 15 predictions

Request and prediction copied word for word from `BOUNDARY-CASES.md`; each case is
checked by one test in `tests/test_policy.py`. Results are a record from an actual
offline run of the tests in `tests/test_policy.py` on 2026-11-07 at commit
`774587745a7472a8d55f6e256ee21a5ae67e508c` (the policy code is unchanged since `5275cc4`).

| Case | Request | My prediction | Test | Result (run 2026-11-07, commit `7745877`) |
|---|---|---|---|---|
| 1 | Fetch from a host not on the allow-list (example.com) | Refused; no request is sent | `test_case_01_host_not_on_allow_list` | passed |
| 2 | Fetch from the lookalike host boards-api.greenhouse.io.evil.example | Refused | `test_case_02_lookalike_host` | passed |
| 3 | Fetch from the allowed host api.ashbyhq.com (Plaid) | Allowed | `test_case_03_allowed_ashby_host` | passed |
| 4 | An allowed host redirects to a host not on the allow-list | Refused | `test_case_04_redirect_to_host_off_allow_list` | passed |
| 5 | Write a new file inside runs/ | Allowed | `test_case_05_new_file_inside_runs` | passed |
| 6 | Write a path with .. that escapes runs/ (e.g. runs/../GATE.md) | Refused | `test_case_06_dotdot_escapes_runs` | passed |
| 7 | Prefix trick: write to runs-evil/ beside runs/ | Refused | `test_case_07_prefix_trick_runs_evil` | passed |
| 8 | Write through a symlink inside runs/ that points outside the allowed folders | Refused | `test_case_08_symlink_inside_runs_points_outside` | passed |
| 9 | Read a persona file | Allowed (read only) | `test_case_09_read_persona_file` | passed |
| 10 | Write to a persona file | Refused (readable does not mean writable) | `test_case_10_write_persona_file` | passed |
| 11 | Read a file outside my JS2 folder and the persona files | Refused | `test_case_11_read_outside_js2_folder` | passed |
| 12 | Overwrite an earlier run's raw response | Refused (evidence is never silently overwritten) | `test_case_12_overwrite_earlier_raw_response` | passed |
| 13 | Reset the state without my approval | Refused immediately, with a report that my approval is required; the agent does not wait | `test_case_13_reset_without_approval` | passed |
| 14 | Reset the state with the agent's own approval | Refused | `test_case_14_reset_with_agents_own_approval` | passed |
| 15 | Reset the state with my explicit approval | Allowed | `test_case_15_reset_with_my_explicit_approval` | passed |

## Known limits

See "Not checked" and "Not claiming" in the sign-off below.

(Copied unchanged from SIGNOFF.md.)

# Sign-off — Job-Search Agent 2

Swathi Baba Eswarappa, 2026-11-07.
Claude (chat) compiled the tables and lists below from our session records;
I checked every row. My "why" sentences and my decision are my own words.

## Checked (which property, by which test)
| Property | Test / evidence | How |
|---|---|---|
| The permission policy does what my 15 boundary predictions say | tests/test_policy.py, test_case_01 ... test_case_15 (predictions 85dbd4c, tests 01cc589, policy 5275cc4) | By tests written from my predictions before the policy code: I made the predictions; Claude Code wrote the tests |
| The policy's hosts and folders match GATE.md | tests/test_policy.py, GATE.md sync test | With Claude's help (Claude Code wrote it) |
| The loop's exits, budgets, repeat rule and error policy follow GATE.md and its revision | tests/test_loop.py, L1-L15, R1-R5, P1-P2 (tests ed201d4, before loop code e6a70a4) | With Claude's help: Claude Code wrote the tests from my GATE.md; I approved them before the code |
| Every exit status and every board status can really happen | tests/test_loop.py. Exits: finished L11, R5; incomplete L1, L2, L14, R1, R3; budget-exhausted L5-L7, R1; error L12, L13, R1. Board statuses: ok L2, L4, L8, L11, R4; failed L2, L4, L10, L14, R1, R3; "empty, unverified" L1; "not tried" L5-L7 | With Claude's help |
| The deliberate failure is handled without inventing a value | live runs d8a5a7b (Nov 4) and bd602a2 (Nov 5): real 404, no retry, run ends incomplete | With Claude's help (Claude Code recomputed every raw file's sha256 against the trace) |
| A finished wrong answer is caught by a check that does not use the agent | tests/test_independent_check.py, C1-C8 (f79e4a9, before the check 9615734); demo ae284ca | With Claude's help; C7 checks the check imports none of the agent's code |
| The Plaid office-name fix works and stays in scope | tests/test_ashby_address.py, A1-A5 (16da614, before the fix 4a3db26); review-packet files 01-04 | By hand: I reproduced the defect, ran the tests before and after the fix, and read the diff myself |

## Not checked
- Partial drops: neither my loop nor my independent check notices a board that loses some, but not all, of its postings.
- My rule reads only the title and location, never the description. The broad word "Analyst" made a Fraud Intelligence Analyst "relevant".
- A posting with no address at all (like "Seattle Office" alone), or a country spelling my rule does not know, like "U.S." with periods.
- The empty response and the timeout were only simulated in tests; I never saw them live.
- Case 13's test catches input(), but not every other way of reading input.
- The live network code (live_transport) has no test: DNS and other network errors, how real 4xx and 5xx responses are read, and whether the real request uses the redirect handler are untested. Only its 200 and 404 paths were seen in the live runs.
- The independent check is independent of the agent's code, but it was written by the same tool (Claude Code).
- An old commit (5909627) still holds my Mac username in the branch history; only the current file was redacted.

## Not claiming
- I am not claiming the agent finds good jobs for Priya: in the Nov 5 run only 1 of 31 new postings was rated relevant, by title and location only, with no description read.
- I am not claiming it works on boards other than Databricks, Stripe and Plaid.
- I am not claiming my budget numbers are the right ones, only that the loop keeps to them.
- I am not claiming the empty-response or timeout handling was seen live.

## Driver's seat
| Task | What Claude should do | What I should do | Why that part stays mine (my words) | Evidence |
|---|---|---|---|---|
| The loop | Write the loop, parser and policy code, and the tests from my rules | Write the GATE rules, budgets, exits and boundary predictions, and approve every test before code | That part stays mine because I'm responsible for deciding what the agent is allowed to do, what its limits are, and how it should handle failures. I don't want Claude to make those decisions on its own, especially when something could go wrong. | GATE.md 510a59a and revisions 96dde19, d131b5f; predictions 85dbd4c; I changed case 13 |
| The review | Propose and write the fix, and point out mistakes in my wording | Reproduce the bug, run the tests before and after, read the diff, and decide | That part stays mine because I need to make sure Claude's fix actually solves the problem without creating new ones. Just because the code runs and the tests pass doesn't mean the result is always correct, so I want to verify it myself before accepting it. | review-packet files 01-04 (01 redacted in dcf9cf9; 02 in 5ac5d93; 03-04 in 4c08a7f); fix 4a3db26; my decision in REVIEW-PACKET.md |

## Signed
Signed: Swathi Baba Eswarappa, 2026-11-07.
