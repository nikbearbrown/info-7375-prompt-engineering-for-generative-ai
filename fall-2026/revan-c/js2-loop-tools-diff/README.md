# Job-Search Agent 2 — The Loop, the Tools, and the Diff

INFO7375 · Revan C. · gate in [GATE.md](GATE.md) · Chapters 4–6

A bounded loop that watches three public job boards on two applicant-tracking systems (Klaviyo and Duolingo on Greenhouse, Patch My PC on Lever). It runs every network and file action through a permission policy enforced in code, and it ends each run with exactly one of four statuses. It never applies, emails, messages, or logs in. The persona is fictional (`@example.com`, `555` phone).

**Started from:** my Job-Search Agent 1 in this repository (its documents are now [JS1_README.md](JS1_README.md), [JS1_SOURCES.md](JS1_SOURCES.md), [JS1_FRICTIONAL.md](JS1_FRICTIONAL.md)). JS2 reuses JS1's fictional résumé, its résumé loader, and its relevance rule (`jsagent/rule.py`, governed by [CONTRACT.md](CONTRACT.md)) unchanged. The loop, policy, providers, and checks are new, in `jsloop/` and `tools/`. I did not use the Reallocation Engine's or Lectern's code; Lectern's `ATS.md` was read for how the ATS endpoints behave.

## Toolchain

- Python **3.12.14** (Homebrew, macOS). JS1 was built on 3.14.5, which was later uninstalled from this machine; JS1's 42 tests pass on 3.12.14.
- The loop uses the standard library only (`http.client`, `json`, `os`, `pathlib`).
- `jsonschema==4.26.0` (résumé check, from JS1) and `pytest==9.2.0`. `anthropic==2.3.0` is installed for JS1's Claude judge; JS2 never calls Claude and needs no API key.

## Setup from a fresh clone

```bash
python3.12 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements.txt
```

## Commands

All paths are relative to the repository root. The agent always writes inside this repository (`evidence/js2/`, `runs/js2/`, `state/js2/`), because GATE.md does not let a caller widen the write folders. To try it without changing the committed record, run it in a scratch clone.

Run every test (JS1 and JS2):

```bash
.venv/bin/python -m pytest -v
```

Check that each GATE.md wrong version is caught by its named test (builds 17 mutant copies in a temp dir):

```bash
.venv/bin/python tools/check_wrong_versions_js2.py
```

**Normal run** of boards 1–3, observation only (state not written):

```bash
.venv/bin/python -m jsloop run
```

Normal run that may update `state/js2/` if it finishes cleanly:

```bash
.venv/bin/python -m jsloop run --approve-state-write
```

**Deliberate-failure run**, the labeled demonstration (boards 1–4; board 4 does not exist):

```bash
.venv/bin/python -m jsloop run --demo-failure --approve-state-write
```

**Independent check** of any saved run, JS1 or JS2:

```bash
.venv/bin/python tools/independent_check.py runs/js2/<trace>.json
```

Options: `--seeded BOARD=fixtures/js2/FILE` reads that board from a seeded fixture instead of fetching it, and the trace labels it `seeded`. `--json` prints the full trace. Ask the policy about one action without doing it: see [BOUNDARY_TESTS.md](BOUNDARY_TESTS.md).

### Exit codes

| Status | Exit | Meaning (GATE.md, Exits) |
|---|---|---|
| `finished` | 0 | every selected board answered once with a valid nonempty list; trace saved; state saved if approved |
| `incomplete` | 10 | at least one board failed or was empty; the rest were observed; counts for the failed board are `unknown` |
| `budget-exhausted` | 11 | the next action would cross a limit (4 boards, 4 requests, 45 s with 10 s needed to start a request), or the deadline passed |
| `error` | 12 | preflight, permission, output, or state-write failure |

GATE.md says only that these must be distinct and nonzero; the numbers 10–12 are Claude Code's choice.

### What a run records

`runs/js2/<time>_<normal|demo>.json` is the **trace**. It holds:
- the selection, budget, run mode (live, seeded, or mixed), status, exit code, stop reason, request count, and elapsed seconds;
- one observation per selected board: HTTP status, error, raw-response path, posting count, baseline or new count, and new postings with their CONTRACT.md rule verdicts;
- `state_updated` and why;
- an ordered action ledger: every label, request, response, write, and refusal.

`evidence/js2/<time>_<board>.body` holds the **raw response bytes**, saved before parsing.

**Baseline.** GATE.md does not say what the first run reports. The code follows JS1: a board with no saved state is a baseline, and its `new_count` is `"baseline"`, not every posting.

## Finished-wrong demonstration

**What it shows.** A run that ends cleanly and is wrong: an empty board reported as "no new jobs". The wrong run is my **JS1 agent**. Its parser accepts `{"jobs": []}` as a valid board, so it reports `new=0` and exits 0. Nothing was planted: this is the JS1 code as submitted. Both runs below are **seeded**, from [fixtures/js2/klaviyo_empty_seeded.json](fixtures/js2/klaviyo_empty_seeded.json) (see [fixtures/js2/PROVENANCE.md](fixtures/js2/PROVENANCE.md)). They write only to `demo/finished_wrong/`.

1. JS1 baseline, from JS1's own committed seeded response:

```bash
.venv/bin/python -m jsagent run --board klaviyo --resume resumes/aarav-patel.json --no-claude --seeded-response evidence/klaviyo_2026-10-31_seeded.json --state demo/finished_wrong/seen_ids.json --runs-dir demo/finished_wrong/runs --evidence-dir demo/finished_wrong/evidence
```

2. JS1 on the empty board. It prints `new=0` and exits 0:

```bash
.venv/bin/python -m jsagent run --board klaviyo --resume resumes/aarav-patel.json --no-claude --seeded-response fixtures/js2/klaviyo_empty_seeded.json --state demo/finished_wrong/seen_ids.json --runs-dir demo/finished_wrong/runs --evidence-dir demo/finished_wrong/evidence
```

3. The independent check, not JS1's own report, catches it. It exits 1 with `FAIL empty-response-claimed-as-no-new-jobs`. Pass it the exact `run file=` path that step 2 printed. Don't use `ls | tail -1`: when both runs happen in the same second, step 2's file is `..._seeded-1.json`, which sorts *before* step 1's `..._seeded.json`.

```bash
.venv/bin/python tools/independent_check.py demo/finished_wrong/runs/<the run file step 2 printed>.json
```

4. For contrast, JS2 on the same bytes ends `incomplete` (exit 10), with Klaviyo's counts `unknown`:

```bash
.venv/bin/python -m jsloop run --seeded klaviyo=fixtures/js2/klaviyo_empty_seeded.json
```

`tools/independent_check.py` imports nothing from `jsagent` or `jsloop` (a test checks this). It recounts postings from the saved raw bytes and compares them with what the run claimed. It does not fetch anything, so it cannot tell a truly empty board from a broken one. It can only say an empty response does not support "no new jobs".

## What ran

**Runs I ran in my terminal, November 10, 2026 (UTC).** The two unsuccessful normal attempts are included because they happened before the finished run. The commands for the seeded demonstration are written out in the numbered steps above.

| Run | Command | When (UTC) | Status / exit | Trace | Independent check |
|---|---|---|---|---|---|
| Normal attempt 1, live | `.venv/bin/python -m jsloop run --approve-state-write` | 06:32:28 | `incomplete`, exit 10; all three DNS lookups failed; state unchanged | [trace](runs/js2/2026-11-10T06-32-28Z_normal.json) | Not run; no board response arrived |
| Normal attempt 2, live | `.venv/bin/python -m jsloop run --approve-state-write` | 06:32:42 | `incomplete`, exit 10; Klaviyo 149, Duolingo 61, Patch My PC timed out; state unchanged | [trace](runs/js2/2026-11-10T06-32-42Z_normal.json) | Not run |
| Normal approved run, live | `.venv/bin/python -m jsloop run --approve-state-write` | 06:33:08 | `finished`, exit 0; 149 / 61 / 5 postings, all baseline; state updated | [trace](runs/js2/2026-11-10T06-33-08Z_normal.json) | [10 passed, 0 failed](demo/independent_check_normal_run.txt) |
| Deliberate failure, live | `.venv/bin/python -m jsloop run --demo-failure --approve-state-write` | 06:33:21 | `incomplete`, exit 10; fourth board HTTP 404, counts `unknown`; state unchanged | [trace](runs/js2/2026-11-10T06-33-21Z_demo.json) | [9 passed, 0 failed](demo/independent_check_demo_run.txt) |
| JS1 baseline, seeded | Finished-wrong step 1 | 06:34:13 | Exit 0; 154 postings saved as baseline, 0 new | [run](demo/finished_wrong/runs/2026-11-10T06-34-13Z_seeded.json) | Not run |
| JS1 empty board, seeded | Finished-wrong steps 2–3 | 06:34:17 | Exit 0; 0 postings, incorrectly reported 0 new | [run](demo/finished_wrong/runs/2026-11-10T06-34-17Z_seeded.json) | [1 passed, 1 failed](demo/finished_wrong/independent_check.txt): `empty-response-claimed-as-no-new-jobs` |
| JS2 empty-board contrast, mixed | Finished-wrong step 4 | 06:34:30 | `incomplete`, exit 10; seeded Klaviyo counts `unknown`; two other boards live; state unchanged | [trace](runs/js2/2026-11-10T06-34-30Z_normal.json) | [7 passed, 0 failed](demo/independent_check_seeded_empty_js2.txt) |

**Claude Code's checks** (2026-11-10, scratch folders outside the repository; not the submitted trace):
- All 108 tests passed (42 JS1, 66 JS2) before the review patch; 110 passed after it, and 17 of 17 mutants were caught.
- Live normal run: `finished`, 149/61/5 postings, 3 requests, 2.8 s.
- Live demo run: `incomplete`, exit 10; board 4 got HTTP 404 with body `{"status":404,"error":"Job not found"}` and counts `unknown`; state not written.
- JS1 on the empty fixture exited 0 with `new=0`, and the independent check failed it.

## Documents

[GATE.md](GATE.md) (Revan) · [COMMIT_LOG.md](COMMIT_LOG.md) (every cited commit) · [BOUNDARY_TESTS.md](BOUNDARY_TESTS.md) · [REVIEW_PACKET.md](REVIEW_PACKET.md) · [SIGNOFF.md](SIGNOFF.md) (sign-off and driver's seat) · [SOURCES.md](SOURCES.md) · [FRICTIONAL.md](FRICTIONAL.md) · [fixtures/js2/PROVENANCE.md](fixtures/js2/PROVENANCE.md)

## Layout

```
jsloop/           policy.py  fetch.py  providers.py  budget.py  loop.py  __main__.py
tools/            independent_check.py  check_wrong_versions_js2.py
tests/            test_js2_boundary.py  test_js2_loop.py  test_js2_independent_check.py  js2_support.py
fixtures/js2/     seeded inputs (read-only to the agent)
evidence/js2/     raw responses     runs/js2/  traces     state/js2/  seen ids (approved runs only)
jsagent/ ...      Job-Search Agent 1, reused for the résumé and the rule
```
