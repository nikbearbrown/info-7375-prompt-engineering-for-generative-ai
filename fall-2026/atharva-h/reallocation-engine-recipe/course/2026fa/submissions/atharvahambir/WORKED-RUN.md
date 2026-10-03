# Worked run — one real target (Robinhood), live board, 2026-10-03

## Executive summary

This is a real run of the daily checker against a live job board, the kind of run the student would do each morning. The target was Robinhood: real company, real board, real sponsorship data. The candidate was the fictional persona "Atharva" (invented dates), so nothing personal is committed.

**Step 1.** The board listed 162 postings and none fit entry-level data work today. Robinhood's sponsorship record was *not found*, because the data files it under its legal name. The tool said "unknown" and suggested the right row instead of guessing.

**Step 2.** At the human gate, the student confirmed the legal name and stated the E-Verify status. Robinhood then showed as a **Proven** sponsor with nothing open: a company to **network into**, not apply to.

**Step 3.** A deliberate typo in the board link made the run stop without inventing anything.

Two small display bugs were found and fixed along the way.

> **Folder name at run time.** These runs were made before the prototype folder and recipe were renamed from `atharvahambir-data-roles-opt90-h1b-daily` to `atharvahambir-reallocation-engine` (2026-10-03). The pasted outputs keep the old paths exactly as printed; the only code change in the rename is the recipe-id string.

---

## Inputs

| Input | Value | Label |
|---|---|---|
| Candidate | `search/examples/atharva/daily-check.candidate.json`: fictional persona; OPT end 2027-03-15; 3 unemployment days used as of 2026-09-21, limit 90; buffer 30 days; needs an E-Verify employer | your-input (fictional) |
| Target (step 1) | `runs/worked-run-2026-10-03/targets.step1.json`: `Robinhood`, `https://job-boards.greenhouse.io/robinhood`, E-Verify `null`, default 8 hiring weeks | your-input |
| Target (step 2) | `runs/worked-run-2026-10-03/targets.step2.json`: adds `csv_name: ROBINHOOD MARKETS INC` (confirmed by me at gate G5) and E-Verify `enrolled: true` (stated by me at gate G4; not verified by the tool) | your-input |
| Board | live `https://boards-api.greenhouse.io/v1/boards/robinhood/jobs?content=true`, fetched 2026-10-03 14:01 and 14:10 EDT; 1,751,334 bytes, sha256 `a6ac36d2a87278210f842f9af071544dd8b49b37871f8883313811ce50854f29` (identical both times) | record |
| Sponsorship data | `data/80-days-to-stay/80-days-csv/mapped_student_employment_targets_v3.csv`, sha256 `eccdee2addf472b1…` | record |

All paths below are under `course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/` unless written in full.

## Commands and real output

### Step 1: the target exactly as given (`step1-command-output.txt`)

```
$ python3 scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/daily_check.py --candidate search/examples/atharva/daily-check.candidate.json --targets course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/targets.step1.json --out-dir course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step1
✓ 2026-10-03 — 1/1 boards read · 162 postings listed · 0 match (0 new)
  Apply 0 · Consider 0 · Skip 0 · Held for you 0 · closed 0 · network 0 · not checked 0
  course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step1/2026-10-03/daily-check.md  +  course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step1/2026-10-03/daily-check.json
real 0.66
user 0.18
sys 0.03
EXIT=0
```

From `step1/2026-10-03/daily-check.md`, the target-list row and the filtered-out list. The hint is printed twice; that's bug 1, fixed before step 2. This file is kept as it was produced.

```
| Robinhood | greenhouse | no-row: no row named 'Robinhood' in the sponsorship data — the data has similar names: ROBINHOOD MARKETS INC (824 approvals); ROBINHOOD VENTURES LLC-FINAUTO VENTURE-1 (no H-1B fields); if one is this company, set csv_name in targets — unknown, not 'does not sponsor' — similar names: ROBINHOOD MARKETS INC (824 approvals), ROBINHOOD VENTURES LLC-FINAUTO VENTURE-1 (no H-1B fields) | not checked *(your-input)* | 8 wk (default) *(your-input)* | 162 | 0 | 161 / 1 / 0 / 0 |

| Robinhood | Business Analyst Intern (Summer 2027) | title word: intern |
```

### Gate decisions (human)

- **G5, sponsorship evidence:** "Is the Robinhood board the same employer as `ROBINHOOD MARKETS INC` (824 approvals, 24 denials, 97.2%)?" Atharva Hambir: **yes**, so `csv_name` was set.
- **G4, E-Verify:** Atharva Hambir: **"it is E-verified"**, recorded as `enrolled: true`, your-input, *not verified by the tool*.

### Step 2: after the gates (`step2-command-output.txt`)

```
$ python3 scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/daily_check.py --candidate search/examples/atharva/daily-check.candidate.json --targets course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/targets.step2.json --out-dir course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step2
✓ 2026-10-03 — 1/1 boards read · 162 postings listed · 0 match (0 new)
  Apply 0 · Consider 0 · Skip 0 · Held for you 0 · closed 0 · network 1 · not checked 0
  course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step2/2026-10-03/daily-check.md  +  course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step2/2026-10-03/daily-check.json
EXIT=0
```

From `step2/2026-10-03/daily-check.md`:

```
**Your clock:** the latest workable start date is **2026-12-17**, set by your unemployment allowance (OPT ends 2027-03-15; unemployment allowance runs out 2026-12-17). You want 30 days of slack before it. *(your-input — confirm the rules with your DSO)*

## Network, don't apply (1)
| Robinhood | Proven *(record)* | Network into this company (3 networking hours): ask for an informational chat before a role opens. |

## Your target list today
| Robinhood | greenhouse | Proven — 824 approvals, 97.2% (ROBINHOOD MARKETS INC) *(record)* · ⚠ none of the ≤5 listed sponsored titles is one of your title phrases | enrolled *(your-input)* | 8 wk (default) *(your-input)* | 162 | 0 | 161 / 1 / 0 / 0 |
```

Read back from `step2/2026-10-03/daily-check.json` with a one-line Python print of four fields (the long `curve` text is shortened to `...` here):

```
timeline {'value': 0.633, 'source': 'your-input', 'expected_start': '2026-11-28', 'cliff': '2026-12-17', 'slack_days': 19, 'buffer_days': 30, ...}
e_verify {'value': True, 'source': 'your-input', 'source_note': 'stated by Atharva Hambir at gate G4; not verified by the tool', 'checked_on': '2026-10-03'}
listing_evidence https://boards-api.greenhouse.io/v1/boards/robinhood/jobs?content=true fetched 2026-10-03T14:10:24-04:00
scorer {'called': False, 'why': 'no posting had a sponsorship value to score'}
```

### Step 3: deliberate break, board name misspelled `robinhod` (`step3-command-output.txt`)

```
$ python3 scripts/contrib/2026fa/atharvahambir-data-roles-opt90-h1b-daily/daily_check.py --candidate search/examples/atharva/daily-check.candidate.json --targets course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/targets.step3-break.json --out-dir course/2026fa/submissions/atharvahambir/runs/worked-run-2026-10-03/step3
✗ no company board could be read — see the report
EXIT=4
```

`step3/2026-10-03/daily-check.md` (complete, as produced, before the wording fix):

```
This is the daily check of your target companies' job boards, but **it stopped early**: no company board could be read — nothing was checked. No posting was scored, and nothing was guessed to keep going. Fix what is named above and run it again.

- Robinhood: board could not be read: HTTPError: HTTP Error 404: Not Found
```

## Verified vs. inferred (step 2, line by line)

| Line in the result | Label | Why |
|---|---|---|
| 162 postings listed on Robinhood's board | **record** | the board API response, sha256 above |
| 0 match; 161 not a target title; 1 dropped for the word "intern" | **record** + your rules | record titles, filtered by my approved title phrases and word list |
| Matched row `ROBINHOOD MARKETS INC` | **your-input** | my `csv_name` at gate G5; the tool only suggested it |
| 824 approvals · 24 denials · 97.2% · 5 listed titles | **record** | CSV row 22735, cross-checked by hand |
| Tier **Proven**, p 0.9 | **record**, through my approved rule | ≥10 approvals and ≥90% rate |
| "none of the ≤5 listed sponsored titles is one of your title phrases" | **record** | the 5 titles are SWE / manager / accountant |
| E-Verify enrolled | **your-input** | stated by me, not verified |
| OPT end 2027-03-15, unemployment allowance ends 2026-12-17, deadline 2026-12-17 | **your-input** | persona dates; the deadline is the earlier clock |
| Expected start 2026-11-28, 8 hiring weeks, timeline factor 0.633 | **your-input** | my default estimate; 19 days slack ÷ 30-day buffer |
| "Network, don't apply" | follows from the records above | Proven + E-Verify not false + 0 matching postings |
| Apply / Consider / Skip | none produced | no posting matched, so the scorer was not called; nothing was scored on a guess |
| model-judgment | **none** | no language model is called at run time |

## Verification

- **Hand cross-check against the source CSV** (`cross-check.txt`): row 22735 says `Total Approvals = 824.0`, `Total Denials = 24.0`, `Approval_Rate = 97.16981132075472`, and the titles are Software Engineer ×3, Engineering Manager, Senior Corporate Accountant. The report shows 824 / 97.2% and the "no matching title" warning. ✓
- **Same board both times:** the step 1 and step 2 raw responses have the identical sha256 `a6ac36d2…`, so the only change between the runs was my gate answers. ✓
- **Deliberate break (step 3):** a misspelled board → HTTP 404 → exit 4, no score, no invented value, and the failure is named. ✓
- **Tests after the fixes** (`after-fix-tests-and-breaks.txt`): 18 tests OK; all 4 break mutants caught. ✓

## Reflection

**What worked**
- The gate design earned its place on real data. Step 1 refused to call Robinhood a non-sponsor, and its hint pointed at the right row. One human answer turned "unknown" into a sourced Proven record.
- The run was fast (0.66 s for one board) and reproducible: the same raw bytes went in both times.

**What it got wrong or missed**
- *Bug 1:* the similar-name hint was printed twice in the target-list table. Fixed in `daily_check.py`.
- *Bug 2:* the stop report said "fix what is named above" while the failing company was listed below. Fixed: "named here".
- *A title-filter miss (prediction 1 in my brief, partly confirmed).* "Data Solutions & Analytics Senior Analyst" is data-analyst work but contains none of my title phrases. It was senior, so it would have been dropped anyway. A junior posting worded that way would be missed silently: it lands in "not a target title", which the report counts but doesn't list.
- *Unverified inputs.* E-Verify is only my statement. The 8-week hiring time is a guess printed to three decimals (prediction 2).
- *No live matching posting today.* The scoring path is proven on fixtures, not yet on a live posting.

**One concrete next improvement:** add a **"near-miss" list** to the report: postings whose titles contain data words ("data", "analytics", "analyst", "BI") but no target phrase, so I can see what the phrase list skipped and widen it on purpose rather than by luck.

## Attestation

- Recipe: atharvahambir-reallocation-engine v0.1.0
- By: Atharva Hambir · 2026-10-03. The gate answers (G4, G5) and the choice of target are mine; the commands were run by the AI agent at my direction. I read the reports and sign below.
- Signed off after reading the reports: ☑ Atharva Hambir · 2026-10-03

### Tested

| Ran | Saw | Expected |
|---|---|---|
| Step 1: live run, target as given | 162 listed, 0 match; Robinhood "no row" + hint `ROBINHOOD MARKETS INC (824 approvals)`; not on the network list | unknown, not "does not sponsor"; no guess |
| Step 2: live run after gates G4/G5 | Proven (824, 97.2%); E-Verify enrolled (your-input); timeline 0.633, start 2026-11-28; Robinhood on "Network, don't apply" | sourced tier; a networking target because nothing matched |
| **Step 3: deliberate break, misspelled board** | HTTP 404 → exit 4; report names the failure; nothing scored | stop without inventing |
| Hand cross-check: CSV row 22735 | 824 / 24 / 97.17%, 5 non-data titles | the report's numbers |
| sha256 of the step 1 vs step 2 raw responses | identical `a6ac36d2…` | the same board, so only the gate answers changed |
| Offline tests + break mutants after the fixes | 18 OK; 4/4 mutants caught | all pass / all caught |

### Did not test

- A live posting that matches. None existed today, so live scoring, Held postings and E-Verify skips were exercised only on fixtures.
- A second live day, i.e. "new" and "closed since last check" on real data.
- More than one live company at once, and any live Ashby board.
- Whether Robinhood is really enrolled in E-Verify. That is my statement, not checked.
- My real private inputs. They still have empty fields by design, so a real run would stop at the intake gate.
- Workday, iCIMS, Lever and SmartRecruiters boards. Not supported yet.

### Broke during testing, fixed

- Duplicate similar-name hint in the target-list table: seen in step 1, removed in `render_md()` in `daily_check.py`; tests re-run, 18 OK.
- Stop-report wording "named above" pointed the wrong way: seen in step 3, changed to "named here"; tests and break mutants re-run, all pass.
