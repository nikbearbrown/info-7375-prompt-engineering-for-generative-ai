# Saved terminal output — index

## Executive summary

This folder holds the real terminal output of every command run for this assignment, saved at the time it ran, so the worked run and test report can paste output instead of describing it. Read this index to find which file came from which exact command. Two first attempts were overwritten when the corrected command was saved under the same file name; what they printed is recorded below rather than lost silently.

---

> **Folder name at run time.** Everything in this index up to the renamed clean-checkout run was produced while the prototype folder and recipe were still called `atharvahambir-data-roles-opt90-h1b-daily`. The files keep those paths exactly as printed. On 2026-10-03 they were renamed to `atharvahambir-reallocation-engine`.

## Setup baseline — `baseline-2026-09-30/` (run 2026-09-30)

Raw output was first written to a temporary folder and copied here the same day. One edit: `npm-install.txt` had a package author's email (from an npm deprecation notice) redacted.

| File | Exact command | Result |
|---|---|---|
| `npm-install.txt` | `npm install` | installed; deprecation warnings |
| `baseline-doctor.txt` | `npm run doctor` | exit 0 — "environment: ✓ runnable" |
| `baseline-verify.txt` | `npm run verify` | **exit 1** — conformance passed, manifest check failed: `ModuleNotFoundError: No module named 'yaml'` |
| `baseline-verify-venv.txt` | `python3.12 -m venv .venv && .venv/bin/pip install -q pyyaml`, then `source .venv/bin/activate && npm run verify` | exit 0 — passed with 3 warnings |
| `baseline-ats-scan.txt` | `REALLOCATION_ENGINE_PORTALS=data/ats/portals.example.yml npm run ats:scan -- --dry-run` | exit 0 — Databricks, 878 jobs, 71 after filters |
| *(overwritten)* | `npm run ats:scan -- --dry-run` (the assignment's command as written) | **exit 1** — `Error: portals.yml not found. Run onboarding first.` |
| `baseline-score.txt` + `baseline-runs/` | `npm run score -- data/examples/ch11-roles.json --out-dir <temporary folder>/baseline-runs` | exit 0 — Apply 2 · Consider 1 · Skip 2 |
| *(overwritten)* | `npm run ats:liveness -- "https://databricks.com/company/careers/open-positions/job?gh_jid=8633071002"` before the browser was installed | **exit 1** — `browserType.launch: Executable doesn't exist … npx playwright install` |
| *(not saved)* | `npx playwright install chromium` | downloaded Chrome Headless Shell 151.0.7922.34 (94.7 MiB) to `~/Library/Caches/ms-playwright/` |
| `baseline-liveness.txt` | `npm run ats:liveness -- "https://databricks.com/company/careers/open-positions/job?gh_jid=8633071002"` | exit 1 — ⚠️ uncertain, `ERR_TOO_MANY_REDIRECTS` |
| `baseline-liveness-gh.txt` | `npm run ats:liveness -- "https://job-boards.greenhouse.io/databricks/jobs/8633071002"` | exit 1 — ⚠️ uncertain, `ERR_TOO_MANY_REDIRECTS` |
| `baseline-liveness-dead.txt` | `npm run ats:liveness -- "https://job-boards.greenhouse.io/databricks/jobs/1111111111"` | exit 1 — ❌ expired (made-up job id) |
| `baseline-liveness-airbnb.txt` | `npm run ats:liveness -- "https://careers.airbnb.com/positions/8125981?gh_jid=8125981" "https://job-boards.greenhouse.io/airbnb/jobs/8125981"` | exit 0 — ✅ 2 active |

Each `.txt` ends with the `EXIT=` line the shell printed.

## Prototype break attempts — `prototype-2026-09-30/` (run 2026-09-30)

| File | What | Result |
|---|---|---|
| `mutation-check.txt` | three one-line mutants of `daily_check.py`, applied by hand, offline suite run against each, original restored and byte-compared | all three mutants made the suite fail. Superseded by the repeatable harness (`09-break-attempts.txt`), kept as the first record |

## Evidence capture — `evidence-2026-10-03/` (run 2026-10-03)

Every file starts with `$ <exact command>` and ends with `EXIT=<code>`. Files 02–09 were captured (again, the same day) after the sample was switched to the fictional persona in `search/examples/atharva/` and the break-attempt harness was added; the first capture of 02–08 was overwritten.

| File | Command | Result |
|---|---|---|
| `01-score-assignment-command.txt` | `npm run score -- data/examples/ch11-roles.json --out-dir course/2026fa/submissions/atharvahambir/runs` (the assignment's command, with my handle) | exit 0 — writes `runs/role-scores.json` + `runs/role-scores.md` |
| `02-prototype-tests.txt` | `python3 scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/test_daily_check.py` | exit 0 — 18 tests OK |
| `03-prototype-sample-run.txt` | `python3 scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/daily_check.py --sample --out-dir course/2026fa/submissions/atharvahambir/runs/evidence-2026-10-03/sample` | exit 0 — outputs in `sample/2026-10-01/` (the sample's fixed simulated date) |
| `04-conformance-prototype.txt` | `node scripts/conformance.mjs scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/ search/examples/atharva/` | exit 0 |
| `05-verify.txt` | `npm run verify` (inside the `.venv`) | exit 0 — 3 warnings |
| `06-doctor.txt` | `npm run doctor` | exit 0 |
| `07-pii-scan.txt` | `node scripts/pii-scan.mjs` | exit 1 — one finding, `package-lock.json` line 606 (an email inside an npm deprecation notice). It is in the instructor's committed lockfile at `015843d` and unchanged by my install; none of my files is flagged. The address is redacted in this saved copy, because saving the scanner's output otherwise makes the saved file itself a finding. |
| `08-git-status.txt` | `git branch --show-current; git status --short --untracked-files=all; git log --oneline -1` | on local branch `contrib/2026fa-atharvahambir-data-roles-opt90-h1b-daily`; new files only under `course/2026fa/submissions/atharvahambir/`, `scripts/contrib/2026fa/atharvahambir-…/`, `search/examples/atharva/`; nothing committed |
| `09-break-attempts.txt` | `python3 scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/break_attempts.py` | exit 0 — all 4 mutants in `fixtures/BROKEN-mutants.json` caught |
| `10-recipe-checks.txt` | conformance on `recipes/cases/2026fa/`, `logs/runs/`, the prototype and the persona; `[TODO` count vs `todos_open`; a path check of every backticked path in the recipe, card and run log; the recipe's verbatim commands (sample, tests, break attempts); `git branch` / `git status` / `git diff --stat` | all exit 0 — 7 = 7 TODOs; 58 paths exist and the 3 directories Fact 4 names as non-existent are confirmed absent (the `private/daily-check/*` inputs in the live-run command exist only on this machine, by design); `git diff --stat` is empty, so no tracked file was modified |
| `11-pii-baseline-vs-branch.txt` | `pii-scan.mjs` on a clean `git archive` export of `015843d`, then on this branch's working tree, then a diff of the two finding lists | identical: one finding, in `package-lock.json` (an npm deprecation notice in the instructor's lockfile) — **findings added by this work: 0**. Not "clean": the scan exits 1 on main too. A first attempt wrote the output into the repo while scanning and the scan flagged its own half-written file; redone with the output written outside the repo first |

## Worked run — `worked-run-2026-10-03/` (run 2026-10-03, live board)

Write-up: `../WORKED-RUN.md`. Raw board responses (1.7 MB each) stay local — this folder's `.gitignore` excludes `*/*/raw/`; their sha256 is recorded in `cross-check.txt`.

| File | Exact command | Result |
|---|---|---|
| `targets.step1.json` / `targets.step2.json` / `targets.step3-break.json` | inputs — as given / after gates G4+G5 / misspelled board | — |
| `step1-command-output.txt` | `daily_check.py --candidate search/examples/atharva/daily-check.candidate.json --targets …/targets.step1.json --out-dir …/step1` (timed) | exit 0 — 162 listed, 0 match; Robinhood "no row" with a hint; 0.66 s |
| `step2-command-output.txt` | same, `targets.step2.json` → `step2` | exit 0 — Robinhood Proven, network 1 |
| `step3-command-output.txt` | same, `targets.step3-break.json` → `step3` | exit 4 — HTTP 404, nothing scored |
| `cross-check.txt` | `grep` + a Python read of CSV row `ROBINHOOD MARKETS INC`; `shasum -a 256` of both raw responses | 824 / 24 / 97.17% — matches the report; raw responses identical |
| `after-fix-tests-and-breaks.txt` | `test_daily_check.py`, `break_attempts.py` after two fixes made during this run | 18 OK; 4/4 mutants caught |

Note: two display fixes to `daily_check.py` came after `evidence-2026-10-03/02` and `03` were captured. Neither changes those outputs (no sample row carries a similar-name hint, and the sample run doesn't stop), and the suite was re-run on the fixed code (`after-fix-tests-and-breaks.txt`).

## Clean-checkout test — `clean-checkout-2026-10-03/` (run 2026-10-03)

A fresh engine clone at `015843d` plus exactly the staged submission files, overlaid with the folder README's `cp -R` command. Script: `clean_test.sh.txt`. Every file starts with `$ <exact command>` and ends with the command's own exit code (`pipefail`). Write-up: `../TEST-REPORT.md`.

| File | What | Exit |
|---|---|---|
| `00-clone.txt` | clone + `git checkout 015843d`; 0 untracked files | 0 |
| `01-npm-install.txt` | `npm ci --offline` (local cache) | 0 |
| `02-before-doctor.txt` / `06-after-doctor.txt` | `npm run doctor`, before / after the overlay | 0 / 0 |
| `03-before-verify-default-python3.txt` | `npm run verify` with Python 3.14, no PyYAML | **1** (engine's manifest check) |
| `04-before-verify-with-pyyaml.txt` / `07-after-verify-with-pyyaml.txt` | `npm run verify` in the `.venv` | 0 / 0 |
| `05-overlay.txt` | the README's `cp -R` + `git status` | 0 |
| `08-conformance-prototype.txt` | conformance on the prototype folder | 0 |
| `09-sample-run.txt`, `10-sample-report.txt` | `daily_check.py --sample` and the report it wrote | 0 |
| `11-tests.txt`, `12-break-attempts.txt` | 18 tests; 4 mutants | 0 / 0 |
| `13-f4-expired-opt.txt` | past OPT end date | **2** |
| `14-missing-value.txt` | persona with `unemployment_days_used: null` | **2** |
| `15-offline-guard.txt` | network attempted with `DAILY_CHECK_OFFLINE=1` | **1** |
| `16-pii-scan.txt` | `pii-scan.mjs` (address redacted in the saved copy) | **1**, the engine's own lockfile only |
| `17-diff-stat.txt` | `git add -A && git diff --cached --stat` | 0 — 83 insertions, only my paths |
| `18-staged-vs-tested.txt` | byte comparison of the staged code / fixtures / recipe / card / persona with the tested copy, just before the commit | see file |

## Clean-checkout test, after the rename — `clean-checkout-2026-10-03-renamed/` (run 2026-10-03)

The same script and steps as the section above, rerun after the slug became `atharvahambir-reallocation-engine`. Same exit codes, step for step (03 → 1, 13/14 → 2, 15 → 1, 16 → 1, all others → 0). `17-diff-stat.txt`: 104 files, only my paths. **`TEST-REPORT.md` cites this run.** `18-staged-vs-tested.txt` is the byte comparison just before committing.

