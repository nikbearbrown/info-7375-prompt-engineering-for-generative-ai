# SponsorScout board resolver v0.1

The first piece promised in the pitch film (2026-10-14): find public job boards for the **107 of
123** sponsors that have none, and report board coverage as a number, with each new mapping saved
with its raw API response and a test.

**Status (2026-11-23): built, tested offline, and run live once** (`runs/live-2026-11-23/`:
629 requests, stop `done`, 38 proposed · 1 mismatch-only · 67 not-found · 1 incomplete).
**G1 (Akshit Verma, 2026-11-23): 34 approved, 5 refused (wrong company). Coverage: 50/123**
(16 from 2026-10-03 + 34 new; `runs/live-2026-11-23/coverage.md`). Of the 34: 5 boards have 0 postings,
and Rise's identity is unclear (only "Account Manager" titles). `decisions.json` keeps the full history,
including the five approvals that were later refused. The `demo-fixture` run
uses synthetic responses and shows only that the machinery works.

Python 3.12, standard library only. No install step.

## Commands (run from this folder)

```bash
# tests: offline, urlopen is patched to fail
python -m unittest -v test_resolver.py

# offline demo: synthetic responses, 5 companies
python resolver.py probe --fixture fixtures/demo-transport.json --out-dir runs/demo-fixture \
  --only "YEXT INC" --only "HUMAN INC" --only "NUTANIX INC" --only "ZANBATO INC" --only "SOFAR SOUNDS LTD"

# live, when approved: real GETs to the three public APIs only, 1 per second
python resolver.py probe --live --out-dir runs/live-YYYY-MM-DD

# human gate G1: one per proposal, using the hash shown in review.md
python resolver.py decide --run runs/<run> --company "<COMPANY>" --ats greenhouse --slug <slug> \
  --decision approve|refuse|defer --by "<name>" --seen-sha256 <12+ chars>

python resolver.py coverage --run runs/<run>
```

The rules (loop, permission policy, stop conditions, gate, coverage) are in [CONTRACT.md](CONTRACT.md).

## Where the agentic parts live

| Part | Where |
|---|---|
| Loop: observe → decide → act → record → stop | `cmd_probe`, `Run.probe_one`; each phase is a line in `runs/<run>/log.jsonl` |
| Budget and exits | `--budget` (`HttpTool`), `--max-errors`, canary; `summary.json` → `stop_reason` |
| Tool + permission policy in code | `check_policy`, `HttpTool.get`, `check_out_dir`; offline unless `--live` |
| State | `proposals.json`, `raw/`, `decisions.json` per run |
| Stop condition not "the model said so" | done · budget · upstream-errors · canary-failed |
| Human gate bound to what was seen | `cmd_decide`: the hash of the saved response must match `--seen-sha256` |

There is no LLM in v0.1. Slugs are rule-based. Whether an LLM should help with name matching is an
open design question (see the limits below).

## What ran, by kind of evidence (2026-11-23)

| Kind | What | Result |
|---|---|---|
| Fixture output | `python -m unittest test_resolver.py` | 28 tests, OK |
| Fixture output | tests run once *before* `resolver.py` existed | 1 error: import failed (expected) |
| Code inspection + fixture | 5 mutations: gate hash check off, tamper check off, host allowlist off, canary off, proposals counted as coverage | each one made ≥1 test fail |
| Fixture output, real input data | dev set: the 16 boards confirmed on 2026-10-03 | all 16 known slugs generated; 11 of 12 Greenhouse names `name-match`, Upstart only `name-partial` |
| Fixture output | demo run, `runs/demo-fixture/` (synthetic responses) | 21 requests, stop `done`; wrong hash refused (exit 7); 17/123 *in the demo only* |
| Bug found by running it | `decide` on a cp1252 console saved the approval, then crashed (exit 1) | regression test added first (failed), then fixed (passes) |

## Not done / not claimed

- One live run only (2026-11-23). On it, all three APIs answered the made-up canary slug with
  404, which the canary re-checks on every live run. Unite USA timed out and wasn't retried.
- **No real G1 decisions.** The demo's decisions are signed "DEMO-not-a-real-signoff".
- `CONTRACT.md` is **Claude's draft and unsigned**.
- **Known limits:** name-derived slugs can't find boards under a brand name (Social Finance →
  `sofi`, Neutron Holdings → Lime), so those need a person to supply aliases. Lever and Ashby
  return no company name, so a hit there proves only that a slug exists. A short generic
  name (HUMAN, TALENT, INFORMED) can collide with another company's board.
- The console fix (`safe_console`) is only tested together with the ASCII messages, not on its own.

## Inputs

Copied read-only from the Assignment 1 repository at `a1d321f`. Hashes are in
[inputs/PROVENANCE.md](inputs/PROVENANCE.md). The Assignment 1 repository and the pitch-film folder were not changed.
