# Job-Search Agent 2: The Loop, the Tools, and the Diff

A bounded watch loop over three public job boards on two applicant-tracking systems (Greenhouse and Lever), with a permission policy enforced in code, a deliberate failure, a finished-wrong-answer demonstration caught by an independent check, and one reviewed Claude Code change.

Persona: **Sam Rivera**, a fictional new-grad engineer (`examples/persona.example.json`). No real résumé, contacts, tracker or applications are in this folder.

## What I started from

My Job-Search Agent 1 (`../js1-contract-and-watch/`). The skill matcher in `agent/skills.py` was ported from JS1's `agent/rule.py` unchanged in `f982c6a`, then fixed in the review packet. The loop, policy and checks are new in JS2. I did not use the Reallocation Engine or Lectern.

## Language and toolchain

- Python 3.12.7, **standard library only** (nothing to install)
- Tests: `unittest` (standard library)
- Tested on macOS. On Nov 9, 2026 Claude re-ran every command below except the live run from a fresh clone of the branch; all worked.

## Exact commands

Run every command from this folder (`fall-2026/atharva-c/js2-loop-tools-diff/`).

**All tests (36):**
```bash
python3 -m unittest discover -s tests -t . -v
```

**Live run on `boards.json` (makes 4 real GET requests):**
```bash
python3 -m agent.loop
```

**Replay a saved run without the network (same report as the live run):**
```bash
python3 -m agent.loop --replay evidence/run-20261109-041358Z
```

**Budget-exhausted demo (DEMO budget of 2 requests):**
```bash
python3 -m agent.loop --replay evidence/run-20261110-025730Z --budget examples/budget-demo-2-requests.json
```

**Finished wrong answer, then the independent check that catches it:**
```bash
python3 -m agent.naive_demo --replay evidence/SEEDED-empty-robinhood --boards examples/boards-3-real.json
python3 -m agent.independent_check --previous evidence/run-20261110-025626Z --current evidence/NAIVE-DEMO-replay-20261110-030157Z-of-SEEDED-empty-robinhood
```

**Independent recompute of new jobs between the two live days:**
```bash
python3 -m agent.independent_check --recompute-new evidence/run-20261109-041358Z evidence/run-20261110-025626Z
```

**Review packet: React/Go matches on the saved Wealthfront postings:**
```bash
python3 -m agent.reproduce_skills evidence/run-20261109-041358Z/raw/03-wealthfront-a1.json
```

Exit codes from `agent.loop`: 0 finished, 1 incomplete, 2 budget-exhausted, 3 error. Each run writes `out/<run-id>/` (report, trace, raw responses, seen-jobs snapshot); `out/` is not committed, so runs worth keeping were copied into `evidence/`.

## How the loop works

The loop operates sequentially over target boards loaded from `boards.json`. For each board, the URL is first normalized by stripping trailing slashes and converting the path to lowercase; if the normalized endpoint has already been queried in the current run, the duplicate request is skipped without deducting anything from the network budget. Before dispatching any network call or writing any output file, the agent invokes `agent/policy.py` to verify permissions. Any attempt to use an HTTP method other than GET, contact an unapproved domain, read outside permitted paths, or write outside `out/` (or touch protected configuration without `--approve`) triggers an immediate policy violation that halts the run with an `error` exit report and zero fallback data.

For permitted requests, the client dispatches a GET call with a 10-second timeout. If the request times out or returns a 5xx server error, the runner waits 2 seconds and attempts a single retry; if it returns a 404, invalid JSON, or fails the retry, the board is marked as `failed` immediately with no further attempts. When an endpoint returns a `200 OK` with zero jobs, the board is flagged as empty-response, and the run ends `incomplete` rather than treating it as a clean success with no new postings, because an empty response payload cannot prove that a company has no openings versus an archived board, mistyped slug, or altered API schema. The loop checks the three limits (5 boards, 15 requests, 60 seconds) before every board and before every request, capping the request timeout to whatever time remains. If any limit is reached, the run ends `budget-exhausted`, correctly reporting a board stopped between its first attempt and retry as `stopped mid-board` and boards that were never requested as `not reached`.

## What ran

Times are from the UTC run IDs; Eastern time in brackets.

| Evidence | What it is | Who ran it |
|---|---|---|
| `evidence/policy-tests-20261108.txt` | 12 boundary tests, all passed | Atharva, Nov 8 |
| `evidence/run-20261109-041358Z/` | **Live run 1** (Nov 8, 11:13 pm): robinhood 150, affirm 222, wealthfront 23, nonexistent-co-xyz 404 not retried → `incomplete` | Claude |
| `evidence/loop-tests-20261108.txt` | 29 tests (policy + loop), all passed | Atharva, Nov 8 |
| `evidence/skills-defect-repro-20261109.txt` | React/Go defect on real postings: 5 matches, 2 false | Claude |
| `evidence/skills-tests-RED-20261109.txt` | Skill tests before the patch: 7 failures | Atharva, Nov 9 |
| `evidence/skills-tests-GREEN-20261109.txt` | All 35 tests after the patch | Atharva, Nov 9 |
| `evidence/skills-after-patch-20261109.txt` | Same postings after the patch: 3 real matches, 0 false | Atharva, Nov 9 |
| `evidence/run-20261110-025626Z/` | **Live run 2** (Nov 9, 9:56 pm): robinhood 153 (6 new), affirm 221 (5 new), wealthfront 23 (0 new), 404 → `incomplete` | Atharva |
| `evidence/run-20261110-025634Z/` | **DEMO** budget-exhausted run that exposed a mislabel ("stopped mid-board", 3 boards) | Atharva |
| `evidence/loop-budget-bug-RED-20261109.txt` | New test failing on that mislabel | Claude |
| `evidence/run-20261110-025730Z/` | **DEMO** budget-exhausted re-run after the fix ("not reached", 2 boards) | Atharva |
| `evidence/all-tests-after-budget-fix-20261109.txt` | All 36 tests after the fix | Claude |
| `evidence/SEEDED-empty-robinhood/` | **SEEDED** input: real Nov 9 responses with Robinhood's jobs replaced by `[]` | built by Claude |
| `evidence/finished-wrong-1-naive-agent.txt` | Naive loop on the seeded input says `finished` | Atharva, Nov 9 |
| `evidence/finished-wrong-2-independent-check.txt` | Independent check: FINISHED WRONG ANSWER, robinhood 153 → 0 | Atharva, Nov 9 |
| `evidence/recompute-new-day1-day2.txt` | New jobs recomputed from raw files: 6 / 5 / 0, matching the agent | Atharva, Nov 9 |

## Index

| File | What it is |
|---|---|
| `GATE.md` | Exits, budgets, repeat rule, error policy, permission policy (written before code) |
| `WRONG_VERSIONS.md` | 12 plausible-but-wrong implementations and the test that catches each |
| `BOUNDARY_TABLE.md` | 12 permission boundary cases: predicted, then actual |
| `REVIEW_PACKET.md` | The React/Go skill-matching change, reviewed |
| `SIGNOFF.md` | Sign-off and driver's seat |
| `SOURCES.md` | What I started from and what Claude Code contributed |
| `FRICTIONAL.md` | Dated log |
| `boards.json`, `budget.json` | The 4 boards and the real budget (protected: writable only with `--approve`) |
| `agent/policy.py` | Permission policy in code |
| `agent/loop.py` | The bounded loop, live and replay |
| `agent/skills.py` | Skill matcher (React/Go fix) |
| `agent/naive_demo.py` | DEMO ONLY: wrong version #1, used for the finished-wrong-answer demo |
| `agent/independent_check.py` | Independent check of a report against raw files and an earlier run |
| `agent/reproduce_skills.py` | Prints React/Go matches with context |
| `tests/` | `test_policy.py` (12), `test_loop.py` (18), `test_skills.py` (6) |
| `examples/` | Fictional persona, DEMO budget, DEMO 3-board list |
| `review/` | The prompt, the diff and Claude's response for the review packet |
| `evidence/` | Saved runs, raw responses and test output |
