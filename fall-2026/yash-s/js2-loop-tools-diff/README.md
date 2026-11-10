# Job-Search Agent 2 — The Loop, the Tools, and the Diff

**Yash Saraf** · INFO 7375 · Fall 2026 · due 2026-11-10

- **Boards:** Databricks and Anthropic on Greenhouse, OpenAI on Ashby, plus one deliberately misspelled Greenhouse board
- **Résumé:** Priya Nair, a **fictional** persona (`@example.com`, 555-01xx phone), copied from my JS1 project. My real résumé is not used anywhere.
- **Language:** Python 3.9 or newer, standard library only. The tests passed on Python 3.13.5 (my runs) and 3.9.6 (Claude's runs), on macOS.
- **Claude at run time:** none. The agent calls no model. Claude Code wrote code that I reviewed (see SOURCES.md).

My JS1 agent watched one board. This agent watches several boards in one **bounded loop**. It has written exits, fixed budgets, a repeat rule and an error policy. Every request and file write goes through a **permission policy enforced in code**. I wrote the rules first, in [`GATE.md`](GATE.md) and [`BOUNDARY-TESTS.md`](BOUNDARY-TESTS.md), and committed them before any code existed. The agent never applies, emails, messages or logs in anywhere.

## What is in this folder

| Path | What it is |
|---|---|
| [`GATE.md`](GATE.md) | My exits, budgets, repeat rule, error policy, permission policy and wrong versions, written before any code (commit `e18f63c`), plus a dated note |
| [`BOUNDARY-TESTS.md`](BOUNDARY-TESTS.md) | My 15 permission-boundary predictions, written before any code, and the results after testing |
| [`agent.py`](agent.py) | The loop: budgets, exits, repeat rule, retries, raw responses saved first, state updates, trace and report |
| [`policy.py`](policy.py) | The permission policy: HTTPS GET to two exact hosts, no redirects, resolved-path folder checks, create-only evidence, and approval for state resets |
| [`providers.py`](providers.py) | Greenhouse and Ashby: board URLs and response-structure checks |
| [`record.py`](record.py) | My JS1 RECORD rule, copied unchanged from `judge.py` at JS1 commit `73260d2` |
| [`independent_check.py`](independent_check.py) | A separate checker that recounts boards from the saved raw responses. It does not use the agent's code. |
| [`wrong_versions.py`](wrong_versions.py) | Plants my three wrong versions in a scratch copy and confirms that the tests catch each one |
| [`config/`](config/) | `live.json` (the four planned boards) and `demo-finished-wrong.json` (three boards, for the seeded demonstration) |
| [`persona/`](persona/) | `priya-nair.resume.example.json`, copied unchanged from JS1 (sha256 `a4fdbc96…`) |
| [`state/`](state/) | One state file per board after the live run. Databricks started from my JS1 state (924 ids). |
| [`runs/run-2026-11-10T025118Z/`](runs/run-2026-11-10T025118Z/) | **The real run:** four raw responses (including the 404), `trace.jsonl`, `summary.json` and `report.md` |
| [`demo/`](demo/) | **The finished-wrong-answer demonstration (SEEDED):** replayed responses, its run, and the independent check's output |
| [`review/`](review/) | **The review packet** ([`REVIEW-PACKET.md`](review/REVIEW-PACKET.md)), with the test outputs from before and after the patch, and the diff |
| [`tests/`](tests/) | 65 offline tests |
| [`FRICTIONAL.md`](FRICTIONAL.md) · [`SOURCES.md`](SOURCES.md) | My log, and what I used, wrote and got from Claude |

## Setup

From a fresh clone, go into this folder: `cd fall-2026/yash-s/js2-loop-tools-diff`. Nothing needs installing. Every command below runs from this folder.

## How to run it

**Tests (offline).** The network is never contacted; a fake network and a fake clock stand in.

```bash
python3 -m unittest discover -s tests -v
python3 wrong_versions.py
```

**The live run, as I ran it.** It makes 4 HTTPS requests and writes a new folder in `runs/`. It also updates `state/`, so a second live run reports what is new since mine.

```bash
python3 agent.py --config config/live.json
```

To try it without touching my committed state, give it empty folders: `T="$(mktemp -d)"`, then add `--state-dir "$T/state" --runs-dir "$T/runs"`. With a new state folder, every board's first run is a baseline.

**The finished-wrong-answer demonstration (offline, SEEDED).** See [`demo/README.md`](demo/README.md).

```bash
python3 agent.py --config config/demo-finished-wrong.json --replay demo/replay --state-dir demo/state --runs-dir demo/runs
python3 independent_check.py demo/runs/run-2026-11-10T030055Z --earlier runs
```

**The independent check on my real run (offline):**

```bash
python3 independent_check.py runs/run-2026-11-10T025118Z
```

**Resetting a board's state needs my approval.** Try it on an empty folder:

```bash
python3 agent.py --reset-state greenhouse-anthropic --state-dir "$T/state"                   # REFUSED
python3 agent.py --reset-state greenhouse-anthropic --state-dir "$T/state" --approve-reset   # allowed
```

**Exit codes:** 0 finished · 1 incomplete · 2 error · 3 budget-exhausted.

## What ran

Files are named in UTC. Eastern Time is my local date.

| When (ET) | When (UTC) | What | Evidence |
|---|---|---|---|
| Mon Nov 9, 4:21 pm | 2026-11-09T21:21:17Z | Gate and boundary predictions committed, before any code | commit `e18f63c` |
| Mon Nov 9, 9:51 pm | 2026-11-10T02:51:00Z | Code and tests committed, before the live run | commit `841dbce` |
| Mon Nov 9, 9:51 pm | 2026-11-10T02:51:18Z | **Live run:** incomplete, 4 requests, 3.2 s | `runs/run-2026-11-10T025118Z/`, commit `dd8e287` |
| Mon Nov 9, 10:00 pm | 2026-11-10T03:00:55Z | **Seeded demonstration:** the agent finished; the independent check flagged it | `demo/`, commit `9e757cb` |
| Mon Nov 9, 10:31 pm | 2026-11-10T03:31:21Z | Review packet: my failing test committed before the patch | commit `bca5bb6`, `review/test-before-patch.txt` |
| Mon Nov 9, 10:49 pm | 2026-11-10T03:49:37Z | After the patch: 65 tests pass, and all three wrong versions are caught | `review/tests-after-patch.txt`, `review/wrong-versions-after-patch.txt` |
| Mon Nov 9, 10:57 pm | 2026-11-10T03:57:08Z | **Patch accepted:** the patch and the review packet committed together | commit `630b99a` |

## The real run, step by step

From [`trace.jsonl`](runs/run-2026-11-10T025118Z/trace.jsonl). The time `t` is seconds since the run started.

| t (s) | Event | What happened |
|---|---|---|
| 0.000 | start | Budgets: 4 boards, 6 requests, 120 seconds, 1 retry |
| 0.001 | request | Databricks, attempt 1, request 1 of 6 |
| 0.950 | observation | HTTP 200, 9,976,670 bytes, saved as `raw-greenhouse-databricks-attempt1-http200.json` |
| 1.062 | state updated | 915 postings, **80 new**, seen ids 924 → 1,004 |
| 1.062 | request | Anthropic, request 2 |
| 1.920 | observation | HTTP 200, 10,286,765 bytes |
| 1.966 | state updated | 675 postings, a **baseline** (its first run reports none as new) |
| 1.966 | request | OpenAI (Ashby), request 3 |
| 3.005 | observation | HTTP 200, 14,440,028 bytes |
| 3.059 | state updated | 825 postings, a **baseline** |
| 3.059 | request | Deliberate failure (`databricks-misspelled`), request 4 |
| 3.166 | observation | **HTTP 404**, 38 bytes (`{"status":404,"error":"Job not found"}`), saved as evidence. Not retried, because a 404 is not temporary. No state file was written. |
| 3.166 | exit | **incomplete**: no budget was reached, and the problem was "Deliberate failure: failed (HTTP 404)" |

Each saved raw file's SHA-256 matches the one recorded in the trace. The posting counts in `summary.json` match a recount from the raw files, and `independent_check.py` reported no mismatch.

## Results

**The live run** ([`report.md`](runs/run-2026-11-10T025118Z/report.md)):

| Board | ATS | Status | Postings | New |
|---|---|---|---|---|
| Databricks | Greenhouse | ok | 915 | 80 |
| Anthropic | Greenhouse | ok | 675 | baseline |
| OpenAI | Ashby | ok | 825 | baseline |
| Deliberate failure | Greenhouse | failed (HTTP 404) | - | unknown |

My predictions came true for the 404, the incomplete exit and the two baselines. I predicted about 10 new Databricks postings, and there were 80. My JS1 RECORD rule marked 3 of the 80 as relevant. All three are Senior, Sr. or Staff roles, or based in Bengaluru, so my fuller labeling rule would reject them. RECORD does not look at seniority or location.

**The finished-wrong-answer demonstration (SEEDED).** Databricks and OpenAI were replayed from exact copies of my real responses. Anthropic was replaced by a **constructed** `{"jobs": []}`.
- The agent reported **finished**: 3 boards ok, 0 new.
- `independent_check.py` recounted from the saved responses and flagged **DROP-TO-ZERO: 675 postings in run-2026-11-10T025118Z, none now** ([`demo/independent-check-output.txt`](demo/independent-check-output.txt)).

**The review packet.** My live run showed the 404 board as `new=0` on the console and as `"new_count": 0` in `summary.json`, which breaks my GATE. I wrote a failing test before the patch, Claude made a two-line patch I asked for, and I reviewed the diff, ran the checks and **accepted** it. Unobserved boards now show `null` and `new=unknown`. Details: [`review/REVIEW-PACKET.md`](review/REVIEW-PACKET.md).

**Tests.**
- **65 tests** pass, including one test per boundary case (all 15 matched my predictions; see BOUNDARY-TESTS.md).
- **`wrong_versions.py`** catches all three wrong versions: WV1 (a failed board reported as zero new) by 7 tests, WV2 (a string-prefix folder check) by 1, and WV3 (retries not counted) by 2.

## Known limitations

- **The agent accepts a well-formed empty board** as a real observation. Only the separate independent check catches a sudden drop to zero (GATE.md).
- **My regression tests for the review patch cover only the 404 case.** Unavailable, not-checked and stopped-by-error boards use the same rule but are not tested through the outputs.
- **The live run ran once, before the patch.** There has been no live run since.
- **Redirect refusal is tested at the handler.** No real server sent a redirect.
- **The approval flag** proves that the flag was given, not who gave it.
- **RECORD has no seniority or location rule,** so its 3 "relevant" postings would fail my labeling rule.
- **Size:** the folder is about 80 MB. The live run's raw responses are 33 MB. The demonstration is 47 MB: 23 MB of replay copies, plus 23 MB that its own run saved again, because evidence is never shared or overwritten.

## Driver's seat

The loop and the review, and who did what. The evidence column points to commits and files.

| Part | What Claude did | What I did | Why that part stays mine | Evidence |
|---|---|---|---|---|
| **Loop:** exits, budgets, repeat rule, error and permission policy | Reviewed GATE.md and pointed out two unclear rules | Wrote GATE.md and decided every rule and limit | I chose the limits and stopping rules before Claude wrote the code. | `e18f63c`, before any code |
| **Loop:** boundary predictions | Wrote the tests for my cases, plus 10 extras | Predicted all 15 outcomes before any code, and checked the results | I predicted all 15 results before implementation and checked them against the tests. | `e18f63c`; BOUNDARY-TESTS.md results |
| **Loop:** implementation | Wrote `agent.py`, `policy.py`, `providers.py`, `independent_check.py`, `wrong_versions.py` and the tests | Ran the tests and the wrong-version check myself before committing | I ran the tests myself and checked the deliberately broken versions before accepting the implementation. | `841dbce` |
| **Loop:** the live run | Checked the run files afterwards (fingerprints, recounts, state) | Ran it, compared it with my predictions, and found the "new=0" defect | I ran the real agent, compared the results with my predictions, and identified the misleading count. | `dd8e287`; FRICTIONAL entry of 2026-11-09 |
| **Loop:** the finished wrong answer | Built the replay files and rehearsed the demonstration in a scratch copy | Ran the demonstration and the independent check myself | I ran the seeded demonstration and verified that the independent checker caught the wrong answer. | `9e757cb`; `demo/independent-check-output.txt` |
| **Review:** the test before the patch | Wrote the test setup only | Wrote the assertions, which decide the correct behavior, and committed them failing | 	I wrote the assertions and committed the failing tests before asking for the fix. | `bca5bb6`; `review/test-before-patch.txt` |
| **Review:** the patch | Wrote the two-line patch I asked for, and pointed out the "stopped by error" scope | Wrote the request and its limits | I defined the expected behavior, limited Claude's changes, and reviewed the diff. | `review/REVIEW-PACKET.md` §3–4; `review/agent-patch.diff` |
| **Review:** the decision | Drafted the review packet from the commits and outputs | Read the diff, ran the tests and `wrong_versions.py`, and accepted the patch | I reran the tests and wrong-version checks before deciding to accept the patch. | `review/tests-after-patch.txt`, `review/wrong-versions-after-patch.txt`; accepted in `630b99a` |

## Sign-off — Job-Search Agent 2

**Checked:**
- The loop follows its defined exits and budgets, checked using `tests/test_loop.py`.
- The permission policy matches all 15 boundary predictions, checked using `tests/test_policy.py` and `BOUNDARY-TESTS.md`.
- The real run saved raw responses, recorded requests and observations, and preserved state, checked against `runs/run-2026-11-10T025118Z/`.
- The independent checker caught the constructed Anthropic drop from 675 to zero postings, checked using `demo/independent-check-output.txt`.
- My failed-board regression tests failed before the patch and passed afterward, checked using `tests/test_review_failed_board_count.py` and the saved review outputs.
- All 65 tests passed after the patch. `wrong_versions.py` caught all three deliberately incorrect implementations.

**How:**

I wrote my gate and 15 boundary predictions before Claude implemented the agent. Claude helped write the implementation and automated tests, but I ran the tests myself and compared the results with my predictions.

For the review patch, Claude prepared the test setup, and I wrote the assertions that defined the correct behavior. I ran them before the patch and saved both failures. After Claude made the fix, I inspected the diff, reran all 65 tests, checked the wrong versions again, and accepted the change.

I also checked the live run's raw responses, trace and posting counts. I used the independent checker to examine the seeded demonstration.

**Not checked:**
1. I did not repeat the live network run after the review patch.
2. I did not encounter a real HTTP redirect during the live run. Redirect refusal was tested offline.
3. My new regression tests do not separately verify console and JSON output for unavailable, not-checked or stopped-by-error boards.
4. I did not test a filesystem race in which a symlink changes between the permission check and file write.
5. I did not verify that RECORD correctly identifies every suitable job. Its three relevant results from the live run do not satisfy my fuller seniority or location rules.

**Not claiming:**

I am not claiming that this agent finds every relevant job, that every job marked relevant is suitable, or that a `FINISHED` run guarantees correct answers. The seeded demonstration shows why an independent check matters.

I am also not claiming complete coverage of all failure conditions or that the agent is safe for unattended production use.

**Signed:** Yash Saraf, November 9, 2026 (ET)

