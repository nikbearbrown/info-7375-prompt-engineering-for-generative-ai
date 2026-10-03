# TEST-REPORT — clean-checkout run of the data-roles daily checker

## Executive summary

This report records running the finished prototype from a clean copy of the engine, the way a grader would. It covers:
- the engine's own health checks before and after my files were added;
- the sample run and its output;
- every named failure case;
- proof that my changes touch only my assigned folders;
- what the tool still leaves to a person.

**Results.** The prototype ran from a fresh clone of the engine with nothing but my files added. The sample gave the expected six Apply, one Consider, two Skip and four "needs you". All 18 tests passed and all four deliberately broken versions were caught. Each failure case stopped or held instead of inventing a value. My files changed none of the engine's own checks. The one check that fails, the repo's privacy scan, fails identically without my files.

---

## How the clean checkout was made

The run was **2026-10-03**, repeated the same day after the slug was renamed to `atharvahambir-reallocation-engine`. Every output below is from the **renamed** run (`runs/clean-checkout-2026-10-03-renamed/`). The first run, under the old folder name, is kept in `runs/clean-checkout-2026-10-03/` and gave the same results and exit codes. The full script is saved as `runs/clean-checkout-2026-10-03-renamed/clean_test.sh.txt`.

1. **A fresh clone of the engine at `015843d`, with no untracked files.** I cloned my local copy of `nikbearbrown/the-reallocation-engine`, which is at exactly that commit, rather than re-downloading it. The folder README's `git clone https://github.com/…` gives the same commit.
2. **Dependencies.** `npm ci --offline`, from the npm cache filled by the original install, so nothing was downloaded.
3. **Overlay.** Exactly the files staged for commit in the course repo (`fall-2026/atharva-h/reallocation-engine-recipe/`), copied in with the README's own command: `cp -R <folder>/recipes <folder>/scripts <folder>/logs <folder>/course <folder>/search .`. That is the staged tree, not my working copy. Docs written or corrected after this run were added to the same single commit (listed at the end). The code, fixtures, recipe, card and persona were byte-compared with the tested copy just before committing.
4. **Python.** The prototype uses Python's standard library only. The engine's own `npm run verify` needs PyYAML, which comes from the gitignored `.venv` (`python3.12 -m venv .venv && .venv/bin/pip install pyyaml`).

Each step's exact command, output and exit code are in `runs/clean-checkout-2026-10-03-renamed/NN-*.txt`. Below, the scratch path is shortened to `<scratch>` and the course-repo folder to `<folder>`.

**A first attempt had a capture bug.** Two steps piped output through `| tail`, so the saved exit code was `tail`'s, not the command's: `verify` without PyYAML showed `EXIT=0`. Rerun with `set -o pipefail`; every code below is the command's own.

## Toolchain baseline — before and after my files

| Check | Before (fresh clone) | After (my files overlaid) |
|---|---|---|
| `npm run doctor` | exit 0, "environment: ✓ runnable" | exit 0, identical output |
| `npm run verify`, default `python3` (3.14, no PyYAML) | **exit 1**: `ModuleNotFoundError: No module named 'yaml'` in the engine's manifest check | not repeated; same engine issue |
| `npm run verify` with PyYAML | exit 0, "manifest check passed (3 warnings)" | exit 0, identical |
| `node scripts/pii-scan.mjs` | 1 finding (`package-lock.json`): see `runs/evidence-2026-10-03/11-pii-baseline-vs-branch.txt` | 1 finding, the same one (`16-pii-scan.txt`) |

```
$ npm run doctor 2>&1 | tail -6            # 02 before  ·  06 after (identical)
  open TODOs: 318 declared (in frontmatter) · 318 [TODO markers in bodies

SUMMARY
  environment: ✓ runnable
  recipes: 33/33 carry lifecycle frontmatter — all tracked
  next: continue
EXIT=0
```

```
$ python3 --version; npm run verify 2>&1 | tail -6      # 03 before, default python3
Python 3.14.7
ModuleNotFoundError: No module named 'yaml'

ERROR (1):
  E1 .ai/manifest.yaml does not parse: Error: Command failed: python3 -c "import yaml,json;print(json.dumps(yaml.safe_load(open('.ai/manifest.yaml'))))"

✗ manifest check FAILED (1 error)
EXIT=1
```

```
$ source <engine-src>/.venv/bin/activate && npm run verify 2>&1 | tail -6     # 04 before · 07 after (identical)
WARN (3):
  W1 ignore path not in .gitignore: archive/
  W2 private path not gitignored (PII/secret risk): private/
  W2 private path not gitignored (PII/secret risk): data/ats/

✓ manifest check passed (3 warnings)
EXIT=0
```

`doctor` counts only top-level recipes (33), so the case recipe under `recipes/cases/` doesn't change its numbers. The two W2 warnings are false alarms: the files inside both folders are gitignored.

## Conformance on the prototype folder

```
$ node scripts/conformance.mjs scripts/contrib/2026fa/atharvahambir-reallocation-engine/     # 08
conformance: 18 files (1 md · 3 py · 14 json)
✓ all conform (machine half of P4). Adequacy is still the human gate.
EXIT=0
```

## The sample run and its output

```
$ python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/daily_check.py --sample     # 09
✓ 2026-10-01 — 11/13 boards read · 22 postings listed · 13 match (13 new)
  Apply 6 · Consider 1 · Skip 2 · Held for you 4 · closed 0 · network 1 · not checked 2
  scripts/contrib/2026fa/atharvahambir-reallocation-engine/out/sample/2026-10-01/daily-check.md  +  scripts/contrib/2026fa/atharvahambir-reallocation-engine/out/sample/2026-10-01/daily-check.json
EXIT=0
```

From the report it wrote (`10-sample-report.txt` has it whole):

```
**Apply: 6 · Consider: 1 · Skip: 2 · Needs you first: 4.** 1 sponsor company has nothing open for you — network into those instead.
**Your clock:** the latest workable start date is **2026-12-17**, set by your unemployment allowance (OPT ends 2027-03-15; unemployment allowance runs out 2026-12-17). You want 30 days of slack before it.

| ★ | Stripe | Data Analyst, Revenue | us (record) | within (record) | Proven (record) | 0.7 → start 2026-11-26 (your-input) | composite 0.388 ≥ 0.3, gates healthy | — |
| ★ | Chime | Data Analyst | … | Likely (record) | 0.7 → start 2026-11-26 | above threshold (0.315) but one soft spot: sponsorship tier "Likely" | — |
| ★ | Pinterest | Business Intelligence Analyst | … | Proven (record) | … | E-Verify enrollment not checked — look it up and record it in the targets file — once cleared the scorer would say **Apply** (0.367) | — |
| ★ | Moloco | Data Analyst | … | Proven (record) | … | employer is not E-Verify enrolled, so it cannot support the STEM extension (confirm with your DSO) | — |
| ★ | Roblox | Data Engineer | … | Proven (record) | 0.0 → start 2026-12-24 | gated: timeline ≈ 0.000 (a closed gate zeroes the composite regardless of votes) | — |
| Databricks | Proven (record) | Network into this company (3 networking hours) … |
```

(Rows are trimmed to the columns that matter here; the full table is in the saved report.) Hand check: Stripe 0.9·0.35 + 0.8·0.3 = 0.555; × 1.0 (live) × 0.7 (21 days slack ÷ 30-day buffer) = 0.388. ✓

## Tests and break attempts

```
$ python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/test_daily_check.py     # 11 (last lines)
Ran 18 tests in 1.232s

OK
EXIT=0
```

```
$ python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/break_attempts.py     # 12
✓ real daily_check.py: suite passes
✓ BROKEN-1-past-opt-date-passes: caught by test_f4_past_opt_date_stops_at_the_intake_gate
✓ BROKEN-2-unknown-sponsor-scored-as-zero: caught by test_sample_run_end_to_end
✓ BROKEN-3-e-verify-gate-ignored: caught by test_sample_run_end_to_end
✓ BROKEN-4-timeline-gate-weakened: caught by test_sample_run_end_to_end, test_timeline_factor
✓ all 4 mutants caught
EXIT=0
```

## Each failure case, exercised

| # | Failure | How exercised | What happened |
|---|---|---|---|
| F1 | company not in the CSV | sample (Northwind Analytics) + `test_f1_…` | Held: "no row named 'Northwind Analytics' … unknown, not 'does not sponsor'"; not sent to the scorer |
| F2 | row with no H-1B fields | sample (Coinbase → `COINBASE GLOBAL INC`) + `test_f2_…` | Held: "is in the data but has no H-1B history fields" |
| F3 | posting taken down | `test_second_run_reports_new_and_closed_and_leaves_unread_boards_alone` | listed under "closed since the last check" |
| F4 | OPT end date already past | CLI, `13-f4-expired-opt.txt` | **exit 2**, output below |
| F4 | start date after the deadline | sample (Roblox, 12 hiring weeks) | Skip: "gated: timeline ≈ 0.000" |
| — | a required value missing | CLI, `14-missing-value.txt` | **exit 2**, output below |
| F5 | sponsor on record, no matching title | sample (Stripe, Benchling, Notion, Roblox, Databricks rows) | flagged "none of the ≤5 listed sponsored titles…"; **no dedicated test assertion** |
| F6 | identical H-1B record | sample (Apricus) + `test_f6_…` | Held: "identical to ASCUS BIOSCIENCES INC — likely a join artifact" |
| F7 | not E-Verify enrolled / not recorded | sample (Moloco / Pinterest) | Skip / Held, with the scorer's view shown as a preview |
| F8 | board not Greenhouse or Ashby | sample (Adobe, Workday link) | "not checkable … only those two sources are supported so far" |
| F9 | board unreadable | sample (Dropbox) + second-run test | "not checked today"; its earlier postings are *not* marked closed |
| F10 | 5+ years / 3–5 years / not stated | sample + `test_parse_experience` | dropped with the sentence shown / kept, flagged / kept, flagged |
| — | network attempted in an offline run | CLI, `15-offline-guard.txt` | **exit 1**, output below |

```
$ python3 …/daily_check.py --sample --candidate …/fixtures/candidate.expired.fictional.json --out-dir <scratch>/f4     # 13
✗ stopped at the intake gate: OPT end date 2026-09-15 is not after today 2026-10-01: there is no runway to score against
  <scratch>/f4/2026-10-01/daily-check.md
EXIT=2
```

```
$ python3 …/daily_check.py --sample --candidate <scratch>/missing.json --out-dir <scratch>/missing     # 14 (persona with unemployment_days_used = null)
✗ stopped at the intake gate: visa.unemployment_days_used is missing or not a number — fill it in; there is no default
  <scratch>/missing/2026-10-01/daily-check.md
EXIT=2
```

```
$ DAILY_CHECK_OFFLINE=1 python3 …/daily_check.py --candidate search/examples/atharva/daily-check.candidate.json --targets …/fixtures/targets.sample.json --out-dir <scratch>/guard --today 2026-10-01 2>&1 | tail -2     # 15
    raise RuntimeError("network fetch attempted while DAILY_CHECK_OFFLINE=1")
RuntimeError: network fetch attempted while DAILY_CHECK_OFFLINE=1
EXIT=1
```

## Only my namespaced paths changed

In the clean clone, after the overlay:

```
$ git add -A && git diff --cached --stat | tail -12 && git diff --cached --name-only | cut -d/ -f1-3 | sort | uniq -c     # 17
 …
 104 files changed, 9710 insertions(+)
  77 course/2026fa/submissions
   1 logs/runs/2026fa-atharvahambir-1.md
   1 logs/runs/2026fa-atharvahambir-2.md
   2 recipes/cases/2026fa
  19 scripts/contrib/2026fa
   4 search/examples/atharva
EXIT=0
```

All 104 files are insertions under my assigned paths (`search/examples/` is the repo's sanctioned place for a new fictional persona). Nothing existing was modified, and `logs/RUN_LOG.md` is untouched. In the course repo, the commit adds files only under `fall-2026/atharva-h/reallocation-engine-recipe/`.

## PII scan

```
$ node scripts/pii-scan.mjs     # 16 — the address is redacted in the saved copy
pii-scan: 1 finding(s) — see DATA_CONTRACT.md §Zero-Conditions

  [email] package-lock.json — [email redacted in this saved copy — npm package author metadata]
EXIT=1
```

**Not clean, and not because of this work.** The only finding is an npm deprecation notice in the engine's own committed `package-lock.json` (line 606). A clean export of `015843d` gives the identical finding (`runs/evidence-2026-10-03/11-pii-baseline-vs-branch.txt`), so the findings added by my files number **0**. Making it pass would mean editing the instructor's lockfile or weakening the scanner; I did neither.

## What the gates require a person to judge

- **G4 E-Verify:** whether each employer is enrolled, looked up and recorded by me. The tool never decides immigration eligibility.
- **G5 sponsorship evidence:** whether an unmatched company's legal name is one of the hinted rows (the `csv_name` decision, e.g. Robinhood → `ROBINHOOD MARKETS INC`), and whether a "similar names exist" warning on a matched company means it's the wrong row (CHIME INC vs CHIME FINANCIAL INC).
- **G3 timeline inputs:** the unemployment days used, the limit, the buffer and each company's hiring time are mine. The limits are questions for a DSO.
- **Flags on kept postings:** "experience not stated / crosses your limit", "location not confirmed as US", "title word to check: ii", "open N days".
- **The filtered-out list:** whether a dropped posting should have been kept, meaning whether my title phrases or word rules are wrong.
- **G7, the decision itself:** apply, network or skip. The recipe never applies anywhere.

## Did not test

- A literal `git clone` from GitHub on a different machine (the clone came from my local copy at the same commit), and a fresh `npm install` from the network (dependencies came from the offline cache).
- `npm run verify` on a machine whose default `python3` has PyYAML. Here it needed the `.venv`.
- Live board scoring. The live worked run had no matching posting, so live scoring is exercised only on fixtures (`WORKED-RUN.md`).
- Any live Ashby board, or more than one live company at once.
- A dedicated assertion for F5.

## Byte comparison before committing

Just before the single commit, every code, fixture, recipe, card and persona file staged for commit was compared with the copy this run used. Result: `runs/clean-checkout-2026-10-03-renamed/18-staged-vs-tested.txt`.

Changed after this run, all documentation:
- this report;
- `FRICTIONAL.md` entry 12;
- `runs/INDEX.md` rows;
- the saved outputs in `runs/clean-checkout-2026-10-03-renamed/`;
- `logs/runs/2026fa-atharvahambir-1.md`, where a transcription error was corrected: Pinterest's preview score said 0.368, and the report prints 0.367.
