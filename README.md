# Job-Search Agent 2: The Loop, the Tools, and the Diff

INFO 7375 · Ethan Gomes · Fall 2026 · Chapters 4–6

The JS1 watcher watched one Greenhouse board. JS2 turns it into a **bounded loop over ten public boards on two applicant-tracking
systems** (Greenhouse and Lever). It runs under a **permission policy enforced in code**, and it changes only through **code I reviewed**.
The rules were written first, in [GATE.md](GATE.md) (v2.3, committed before any JS2 code). The agent never applies, emails, messages or
logs in. It uses a **fictional persona** (Evan Gordon) only.

**Built on:** my own JS1 code. The JS1 folder was not a git repository, so the first commit (`09b1056`) records exactly what was copied,
plus the real 2026-10-31 Samsara baseline with sha256s ([baseline/2026-10-31/PROVENANCE.md](baseline/2026-10-31/PROVENANCE.md)).

## What ran (2026-11-10, ET)

| Run | Kind | Boards | Loop exit | Independent verifier | Shows |
|---|---|---|---|---|---|
| A 17:15:00 | **live** | 10 (`config/boards.json`) | **incomplete (1)** | FAIL (kraken empty) | the deliberate 404 handled with no retry and a null count; Samsara compared with the **real Oct 31 baseline**: 80 new, none data-titled |
| B 17:15:27 | **live**, same day | 9 | **finished (0)** | **FAIL** | **the live finished-wrong answer**: `lever:kraken` reported as 0 new |
| X 17:15:53 | my cross-check, **outside the agent** | — | — | — | Kraken lists **92 postings on Ashby**, so B's answer is wrong |
| C 17:16:05 | **SEEDED** replay, offline | 1 | **finished (0)** | **FAIL** | the same failure, reproducible offline: empty, and 0 vs 323 |
| D 17:16:11 | **live**, same day | 8 | **finished (0)** | **PASS** | the clean run (Toast: 1 new posting) |

Details and limits are in [evidence/RUNS.md](evidence/RUNS.md). **Only Samsara has a real earlier day.** B and D ran seconds after A.
No new data-titled posting appeared live, so the rule judge ran only in offline tests.

## Language, toolchain

| | |
|---|---|
| Language | Python 3 (ran on **3.11.14**, macOS). **Standard library only**, no `pip install` |
| Tests | `unittest` (stdlib), 113 tests, all offline |
| Network | HTTPS GET to `boards-api.greenhouse.io` and `api.lever.co` only (`config/allowlist.json`), 1 s apart per host. `scripts/crosscheck_kraken.py` is my separate tool and also calls `api.ashbyhq.com`; it is not the agent |
| Claude | Claude Code (Opus 5.5) wrote most of the code and drafted the documents (see [SIGNOFF.md](SIGNOFF.md), the driver's seat). The in-agent Claude judge is **off** in every graded run (`--no-claude`), so no Claude login is needed |

## Exact commands (from a fresh clone)

```bash
cd fall-2026/ethan-g/js2-loop-tools-diff

# Offline: no network, no Claude
python3 -m unittest discover -s tests -t .        # 113 tests (75 from JS1, 3 of them updated to the gate; 38 new)
python3 scripts/sabotage_check.py                 # plants each wrong version W1-W19 in a temp copy: expect 19/19 RED (caught)
python3 scripts/boundary_report.py                # 18 boundary cases: predicted vs actual, expect 18/18
python3 review/reproduce_port_userinfo.py         # the review-packet defect: expect "0 URL(s) decided against GATE.md"
python3 scripts/verify_run.py out/runs/2026-11-10T171500_live            # re-check committed run A: FAIL (kraken empty)
python3 scripts/verify_run.py out/runs/2026-11-10T171527_live            # run B: FAIL (the finished-wrong answer)
python3 scripts/verify_run.py out/runs/2026-11-10T171611_live            # run D: PASS

# Seeded run C again, offline, into a temporary output root (touches nothing committed)
python3 scripts/run_and_verify.py --boards config/boards_seeded.json --out /tmp/js2-seeded --no-claude \
  --replay greenhouse:samsara=tests/fixtures/seeded/empty-samsara.json --seeded "TA rerun of run C"

# Live (network), into a temporary output root: Samsara is compared with the Oct 31 baseline, the others are baselined
python3 scripts/run_and_verify.py --boards config/boards.json --out /tmp/js2-live --no-claude
python3 scripts/run_and_verify.py --boards config/boards_no_failure.json --out /tmp/js2-live --no-claude
python3 scripts/crosscheck_kraken.py              # my cross-check (writes evidence/crosscheck/<time>_ashby_kraken.com.json)
```

Exit codes: 0 finished, 1 incomplete, 2 budget-exhausted, 3 error. `scripts/run_and_verify.py` returns the loop's code and saves
`console.txt` and `verifier.txt` in the run folder.

## Where each required piece is

| Brief asks for | File |
|---|---|
| GATE.md: exits, budgets, repeat rule, error and permission policy, wrong versions | [GATE.md](GATE.md) |
| The loop (3+ boards, 2+ ATS, budget, exit status, observations) | [jsagent/loop.py](jsagent/loop.py), [jsagent/providers.py](jsagent/providers.py), [jsagent/net.py](jsagent/net.py) |
| Trace of one real run, including the deliberate failure | [out/runs/2026-11-10T171500_live/](out/runs/2026-11-10T171500_live/) (`trace.jsonl`, `console.txt`, `report.json`, `raw/`) |
| The finished-wrong answer and the independent check | [FINISHED_WRONG_ANSWER.md](FINISHED_WRONG_ANSWER.md), [scripts/verify_run.py](scripts/verify_run.py) |
| Permission policy in code, and the boundary-test table (18 predicted cases) | [jsagent/policy.py](jsagent/policy.py), [BOUNDARY_TESTS.md](BOUNDARY_TESTS.md) |
| Review packet | [REVIEW_PACKET.md](REVIEW_PACKET.md), [review/](review/) |
| Sign-off and driver's seat | [SIGNOFF.md](SIGNOFF.md) |
| Saved raw responses | `out/runs/*/raw/`, `evidence/seeded/…/raw/`, `evidence/crosscheck/`, `baseline/2026-10-31/` |
| Test evidence | [evidence/tests/](evidence/tests/): red before code, after the build, after the patch, sabotage |
| SOURCES.md, FRICTIONAL.md | [SOURCES.md](SOURCES.md), [FRICTIONAL.md](FRICTIONAL.md) |
| My prompts to Claude Code, mapped to commits | [evidence/PROMPTS.md](evidence/PROMPTS.md) |

## Commit order (the gate first, tests before code, the test before the patch)

```
09b1056  starting point (JS1 copy + Oct 31 baseline)
82f02cb … 6cc9e07  GATE.md v1 → v2.3, including a67bdbf, my own edit
e51d208  tests first: B01-B18 predictions + W1-W19 tests, before any JS2 code (113 tests: 21 failures, 38 errors)
6c82b59  build (W4 still red: the inherited JS1 defect)
58ce031  review packet 1/2: reproduce the defect, no code change
afb3877  review packet 2/2: the patch (113 OK, 18/18)
2dfc3b1  sabotage check (19/19 caught)
024c1f7  runs A-D + cross-check
```

## JS1's limits, carried forward (from GATE.md)

- The change between JS1 runs was a constructed seed, not a real second day. JS2 has a real Oct 31 → Nov 10 comparison for Samsara
  only.
- I deleted the evidence for several JS1 runs I had cited. In JS2, every cited run is in RUNS.md and nothing was deleted.
- The JS1 Claude judge varied on Samsara 7922530 (relevant 6 times, not relevant 3). JS2's graded runs keep the judge off.

## Privacy and boundaries

- Fictional persona only. No real résumé, contacts, credentials or transcripts are in this folder.
- Public, read-only endpoints only, paced at 1 s per host. About 30 agent requests and 1 cross-check request in total.
- The agent never applies, emails, messages or logs in (GATE.md section 5).
