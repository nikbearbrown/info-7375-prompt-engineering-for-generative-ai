# Job-Search Agent 2: The Loop, the Tools, and the Diff

**Student:** Ashwin Thankachan · INFO 7375, Fall 2026 · Assignment JS2 (due 2026-11-10)

**Started from:** my own JS1 (`fall-2026/ashwin-t/js1-contract-and-watch/`, commit `d95f05e`). Not from the
Reallocation Engine or Lectern; Lectern's `ATS.md` was read only for which public APIs exist. JS1 is unchanged.

JS2 turns the one-board watch into a **bounded loop over six boards on three applicant-tracking systems**
(Greenhouse, Ashby, Lever), with the exits, budgets, repeat rule, error policy and permission policy written first in
[`GATE.md`](GATE.md) (drafted by Codex, approved by me, committed alone at `c9ff312`, before any code). The persona is still the
fictional Supriya Sharma (`data/supriya-sharma.resume.json`). The agent never applies, emails, messages or
logs in. JS2 runs use the deterministic JS1 rule only; no Claude call is made by the agent (GATE.md section 5).

## Language and toolchain

| | |
|---|---|
| Language | Python 3, **standard library only** (no `pip install`) |
| Tested with | Python 3.9.6 (macOS `/usr/bin/python3`) and Python 3.12.15 (`/opt/homebrew/bin/python3.12`) |
| Network | Public, keyless GETs to `boards-api.greenhouse.io`, `api.ashbyhq.com`, `api.lever.co` only |
| Built with | Claude Code (desktop app) with Claude Opus 5.5 (`claude-opus-5-5`); reviewed with Codex |

## Run it (all commands from this folder)

```bash
cd fall-2026/ashwin-t/js2-loop-tools-diff
```

All tests, offline (fake transport, fake clock, throwaway projects under `tests/tmp/`):

```bash
python3 -m unittest discover -s tests -t .
```

The live loop (six boards, one deliberate failure; writes a new `runs/<id>-live/`, never `state/`):

```bash
python3 -m jobloop
```

Check any run folder independently (does not import `jobloop`):

```bash
python3 independent_check.py runs/2026-11-09T20-21-52Z-live
```

The finished-wrong-answer demonstration (seeded replay, no network):

```bash
python3 -m wrong_versions.demo_finished_wrong
```

The boundary table's Actual column:

```bash
python3 -m tests.test_boundaries --table
```

Exit codes of `python3 -m jobloop`: 0 finished, 1 incomplete, 2 budget-exhausted, 3 error. A state write
happens only with `--approve-state-write` **and** a finished run; with the deliberate-failure board configured,
no run can finish (see "Limits").

## What ran

| What | When (UTC) | Result | Evidence |
|---|---|---|---|
| Offline test suite, after the accepted patch `be7a54a` | 2026-11-10 | 54 tests OK, exit 0, on 3.9.6 and 3.12.15 (run by Claude Code) | `tests/`, `review-packet/checks-run-by-claude-code.txt` |
| Two GATE.md gaps found after the first submission (see below) | 2026-11-10 | tests failing first (`e27a5cc`), fixed in `5917493` | `tests/test_gate_gaps.py`, `review-packet/gate-gaps-*.txt/.diff` |
| **Checks I ran myself**, at `89013cf` | 2026-11-10 20:20:36 | review + gap tests 9 OK; full suite 60 OK on 3.9.6 and on 3.12.15; interrupt reproduction exit 0; independent check of the live run PASS; every exit 0 | `review-packet/checks-run-by-ashwin.txt` |
| **Live run** of 6 boards, code at `e270605` | 2026-11-09 20:21:52 | 5 boards observed (klaviyo 151, hubspotjobs 126, notion 153, supabase 71, palantir 304 postings); `greenhouse/klaviyo-nonexistent-js2` HTTP 404, **not retried**; 6 of 12 attempts, 5.1 s; status **incomplete, exit 1**; state not written; every board a **baseline** (no state existed) | [`runs/2026-11-09T20-21-52Z-live/`](runs/2026-11-09T20-21-52Z-live/report.md): `trace.jsonl`, `raw/`, `report.md`, `console.txt` |
| Independent check of the live run | 2026-11-09 | PASS, exit 0 | `runs/2026-11-09T20-21-52Z-live/independent-check.txt` |
| **Finished wrong answer** (SEEDED REPLAY, wrong version w01) | 2026-11-09 20:23:30 | **FINISHED, exit 0**, and reported a hand-made empty hubspotjobs board as "0 new" | [`finished-wrong-answer/`](finished-wrong-answer/README.md) |
| Independent check of that run | 2026-11-09 | **FAIL, exit 1**: C4, C5, C6 on hubspotjobs | `finished-wrong-answer/check-wrong-version.txt` |
| Same seeded replay, real code | 2026-11-09 20:23:30 | incomplete, exit 1, hubspotjobs `empty-needs-review`; check PASS | `finished-wrong-answer/check-real-code.txt` |
| Boundary tests B01-B18, first run after the committed predictions (`6c1c5b3`; Codex-drafted, see SOURCES.md) | 2026-11-10 | 8 tests OK; all 18 outcomes matched the predictions | [`policy/BOUNDARY-TABLE.md`](policy/BOUNDARY-TABLE.md) |
| Review packet: interrupted request not counted | 2026-11-10 | reproduced (`fb35380`, exit 1); review test red 3/3 (`279c10f`); patch to `jobloop/loop.py` only (`be7a54a`); test 3/3, suite 54 OK, reproduction exit 0; **accepted** by me | [`review-packet/REVIEW-PACKET.md`](review-packet/REVIEW-PACKET.md) |
| `python3 scripts/validate_course.py` (repo root) | 2026-11-10 | **exit 1** on both Pythons, not passing. 3.9.6 crashed on another student's 3.12-only syntax (`fall-2026/shubham-b/.../ports.py`); 3.12.15 listed 66 diagnostics, none under `fall-2026/ashwin-t/` | this table |

No new posting was observed live in JS2 either: the only live run was the first observation of every board.

## How the pieces map to the brief

| Brief | Where |
|---|---|
| The gate | [`GATE.md`](GATE.md) |
| Loop: 3+ boards, 2+ ATSs, budget, exit status, record of every observation | `jobloop/loop.py`, `config/boards.json`, `runs/*/trace.jsonl` |
| One board fails on purpose, handled without inventing a value | `greenhouse/klaviyo-nonexistent-js2` in the live run: `failed`, `postings_observed: null`, listed under "Attention required" |
| Finished wrong answer caught by an independent check | `finished-wrong-answer/`, `independent_check.py` |
| Permission policy in code, 10+ predicted boundary cases | `jobloop/policy.py`, `policy/BOUNDARY-TABLE.md`, `tests/test_boundaries.py` |
| Wrong versions the tests catch (GATE.md section 6) | `wrong_versions/__init__.py`, `tests/test_wrong_versions.py`, `tests/test_boundaries.py` |
| Review packet | `review-packet/` |
| Sign-off and driver's seat | [`SIGNOFF.md`](SIGNOFF.md) |
| Saved raw responses | `runs/*/raw/` (byte-for-byte; sha256 in `trace.jsonl`) |

## Layout

```text
GATE.md                 the approved exits, budgets, repeat rule, error and permission policy, wrong versions
config/boards.json      the six boards (one marked deliberate-failure)
jobloop/                loop.py, policy.py, providers.py, fetch.py, state.py, report.py
                        rule.py, text.py, persona.py copied unchanged from JS1 d95f05e
independent_check.py    recounts raw evidence; imports nothing from jobloop
wrong_versions/         the 16 GATE.md wrong versions as patchable faults, and the demo
seeded/                 the labeled seeded replay and the script that built it from real slices
runs/                   one live run and two seeded runs, each with trace, raw, report
policy/                 boundary table, first test run output, actuals
review-packet/          reproduction, my test, the diff, my decision
tests/                  60 offline tests
drafting/               the questions Claude Code drafted before I wrote GATE.md
```

## Changed after the first submission (2026-11-10)

I first pushed and zipped at `dfcf112`. A review I asked for afterwards found two real gaps against my
own gate, which Claude Code reproduced at `dfcf112` before changing anything:

1. **Processing was outside the time budget** (GATE.md section 2). With slow rule classification on the
   fake clock, a run ended `finished` after 242.6 s on a 120 s budget. Now no classification starts after
   the deadline; such a run ends `budget-exhausted` (exit 2) and never writes state. A classification
   already running cannot be interrupted, so one can still overrun (the same case now stops at ~121.6 s).
2. **State could advance before the report was saved** (GATE.md section 1). Now `report.json` and
   `report.md` are saved first, the approved state write happens after, and its result goes to
   `state-result.json`. If the report cannot be saved, state is unchanged and the CLI says so.

Tests first (`e27a5cc`, 6 failing), fix second (`5917493`, only `jobloop/loop.py`). The saved runs in
`runs/` were made with the earlier code (`e270605` / `a11a167`); neither gap affected them, because no run
wrote state and the live run took 5.1 s. The first submission also lacked checks run by me; I ran them
at `89013cf` (`review-packet/checks-run-by-ashwin.txt`).

From the zip instead of a clone: `cd js2-loop-tools-diff && python3 -m unittest discover -s tests -t .`

## Limits (carried from JS1, and new)

- **No new posting has been observed live**, in JS1 or JS2. Detecting one needs a saved baseline, and my
  gate lets only a finished, approved run write state. Because the deliberate-failure board is always
  configured, every real run is incomplete, so no baseline is ever saved. I kept that rule (GATE.md
  section 1); a watch-only config would be the next decision, written into the gate first.
- **JS1's held-out experiment was not clean** (the only held-out case that changed was the worked example),
  and JS1's watch defaults to `baseline-v1` although `revision-v2` did better. JS2 does not call Claude, so
  neither is fixed or retested here.
- The rule verdicts were not rechecked by hand for the new Ashby and Lever boards; their location and
  content fields are mapped onto the JS1 rule's Greenhouse shape (`jobloop/providers.py`).
- `fetch.https_get`'s whole-request deadline (watchdog) was not tested against a slow server; tests use a
  fake transport.
