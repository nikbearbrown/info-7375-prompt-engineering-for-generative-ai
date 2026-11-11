# JS2 — The Loop, the Tools, and the Diff (Siddi Kommuri)

A bounded loop over **four job boards on three applicant-tracking systems**. It runs under the budgets, exits, repeat rule, error policy and permission policy in [GATE.md](GATE.md), which Siddi wrote before any code (`1793a11`). It builds on JS1 (`../js1-contract-and-watch/`), reusing the allow-listed, no-redirect fetch idea and saving raw responses as evidence.

| Board | System | Role in the run |
|---|---|---|
| `stripe` | Greenhouse | real |
| `notion` | Ashby | real |
| `Canva` | SmartRecruiters | real |
| `stripee` | Greenhouse | **deliberate failure** (404) |

## Language, toolchain, commands

- **Python 3.13.2**, standard library only. Run on Windows 11 with Git Bash. Network: only the three allow-listed hosts.

```bash
python -m agent2 run --config config/boards.json                 # the real run (4 boards, one deliberate failure)
python -m agent2 run --config config/boards.wrong-answer.json    # the finished-wrong-answer demo (Canvaa)
python check/independent_check.py evidence/runs/<run_id>         # independent check of any run
python tests/run_tests.py                                        # 8 tests, scripted fetch, no network
python tests/mutants.py                                          # each GATE §6 wrong version must fail its test
python tests/boundary_tests.py                                   # 15 policy cases; runs only after predictions are committed
```

The exit code is the run's exit: `finished` 0, `incomplete` 1, `budget-exhausted` 2, `error` 3.

## What ran (2026-11-10 ET; run ids are UTC)

| When | What | Evidence |
|---|---|---|
| 22:04 | `GATE.md` committed, before any code | `1793a11` |
| 22:08 | First real run. Result correct (`incomplete`), but its trace had spurious `board_done status=failed` lines from a `finally`-block bug. Kept as evidence; fixed before the next run. | `evidence/runs/2026-11-11T03-08-32Z/` |
| 22:08 | **Real run, the 4 GATE boards:** `EXIT incomplete`. stripe 778 · notion 156 · Canva 35 · **stripee failed `not_found`, no count reported**. 4/12 requests, 2.2 s. Independent check passed. | `evidence/runs/2026-11-11T03-08-59Z/` (trace, summary, raw), `evidence/checks/` |
| 22:09 | **Finished wrong answer:** the Canvaa config gives `EXIT finished`, with Canvaa "success, 0". The independent check **failed** it. | `evidence/runs/2026-11-11T03-09-02Z/`, `evidence/checks/2026-11-11T03-09-02Z.txt` |
| 22:09 | Loop v0 committed | `24d6e27` |
| 22:12 | Tests and the review test committed **before** the patch; the review test fails on v0 | `c0eea55`, `evidence/review/1-…` |
| 22:13 | Patch (GATE §4 identity check): 8/8 tests, 5/5 mutants. The Canvaa rerun is now `incomplete`, and the independent check passed. | `ef6456a`, `evidence/review/` |
| 22:16 | Siddi's 15 boundary predictions committed, then the boundary tests ran: **14/15 matched**. Case 12: predicted refused, code says needs approval, as GATE §5 says. | `e769016`, `0248ff2`, `BOUNDARY-TESTS.md` |
| 22:18 | Siddi ran the tests (8/8) and the independent check (CHECK PASSED) in their own terminal, then **accepted** the patch | `b24d512`, REVIEW-PACKET §5 and §7 |

**Interpretation, flagged for Siddi:** GATE §3 says "the same action" is skipped. The code treats §4's timeout retries as attempts of *one* action, not as repeats; anything else would make §3 and §4 contradict each other.

## Deliverables

- **Agent trace of one real run, including the deliberate failure:** `evidence/runs/2026-11-11T03-08-59Z/trace.jsonl`.
- **Finished-wrong-answer demonstration:** run `2026-11-11T03-09-02Z`, plus the independent check `check/independent_check.py` and its output in `evidence/checks/`.
- **Permission policy:** in code at `agent2/policy.py`; predictions and results in [BOUNDARY-PREDICTIONS.md](BOUNDARY-PREDICTIONS.md) → [BOUNDARY-TESTS.md](BOUNDARY-TESTS.md).
- **Review packet:** [REVIEW-PACKET.md](REVIEW-PACKET.md).
- **Sources and reflection:** [SOURCES.md](SOURCES.md), [FRICTIONAL.md](FRICTIONAL.md).

## Sign-off — Job-Search Agent 2

> Lines drafted by Claude; Siddi reviewed them and chose to sign them as they stand (2026-11-10, about 22:21 ET).

- **Checked:**
  - Each GATE §6 wrong version is caught by its own test (`tests/test_wrong_versions.py`, wv_1–wv_5), and each test fails with its wrong version put in (`tests/mutants.py`, 5/5).
  - The GATE §4 identity rule (`tests/test_review_identity.py`: red before the patch, green after).
  - The permission policy on 15 boundary cases (`tests/boundary_tests.py`, against Siddi's predictions).
  - One real run, independently rechecked from raw files (`check/independent_check.py`).
- **How:**
  - All tests, the mutation check, the independent check and the patch were written by Claude. None was written by Siddi before reading Claude's code.
  - The wrong versions they target, the boundary predictions and the review decision are Siddi's.
  - The posting counts were recomputed from raw responses by a separate script.
- **Not checked:**
  1. A real timeout or a real budget exhaustion on a live board. Both are shown only with a scripted fetch.
  2. A misspelling that lands on another company's real, non-empty board (see REVIEW-PACKET §6).
  3. Pagination against a real board with more than 100 postings. Canva has 35, so its single page never exercised the offset loop live.
  4. Any OS other than Windows 11, or any Python other than 3.13.2.
- **Not claiming:**
  - That the identity rule proves a board is the right company's.
  - That "new since previous run" is anything more than an id comparison with the last saved run.
  - That the agent judges relevance at all. JS2 watches boards; it does not judge postings.
- **Signed or withheld:** Signed, Siddi Kommuri, 2026-11-10

## Driver's seat

| Part | Claude should | Siddi should | Why it stays Siddi's | Evidence |
|---|---|---|---|---|
| The loop's exits, budgets, retries | Implement them exactly as written; flag contradictions (the §3/§4 retry question) | Write GATE.md; decide what a budget is and who changes it | A budget is an authority decision, not a computation | `1793a11` (Siddi's text, verbatim) |
| Permission policy | Enforce it in code; choose adversarial cases | Predict each case's outcome before it runs | Predictions written after results would prove nothing | `BOUNDARY-PREDICTIONS.md` commit precedes `BOUNDARY-TESTS.md` |
| The review | Reproduce, write the failing test first, patch, show the diff and evidence | Run the commands; accept, revise or reject | Accepting code is the accountable act; Claude reviewing its own patch is not review | `c0eea55` → `ef6456a`; REVIEW-PACKET §5 and §7 |
