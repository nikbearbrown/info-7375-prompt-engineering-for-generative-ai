# Reject audit (filter v1) with my labels

All counts below are recomputed by `python scripts/audit_summary.py` (output saved in `results/audit-summary.txt`) from my labels
(`audit-labels.csv`), the key (`audit-key.json`) and the snapshot. Draft prepared with Claude (SOURCES.md); the verdicts are Vrajesh's.

## What was audited
Filter **v1** ran on all **3,068** postings in the 2026-11-01 snapshot (9 boards): 99 relevant, 2,969 rejected
(R1 2,105, R2 715, R3 90, R5 59). The audit sheet (`audit-sheet.md`) was built with seed 7375, shuffled so order gave nothing away,
with the filter's verdicts hidden in `audit-key.json`:

| Group | n | How chosen |
|---|---|---|
| Random rejects | 35 | simple random sample of the 2,969 rejects (the brief asks for at least 30) |
| Close calls | 12 | defined before looking: 8 R1 rejects whose title still says engineer, developer or architect with no seniority word, and 4 R2 rejects where the only trigger was exactly "3+ years" |
| Kept | 15 | simple random sample of the 99 kept |

I labelled each one Y, N or ?, and my labels were committed (`183e7f3`) before the key was opened; the sheet hid the filter's verdicts.
Every error count below is an error against my labels. After the key was opened I
changed two labels from N to ? (items 26 and 34, `cbcec48`); my notes on those items said the facts were unknown.

## Results
| Group | Filter wrong | 95% Wilson interval | Notes |
|---|---|---|---|
| Random rejects (35) | **0** false rejects | 0.0% to 9.9% | rules in the sample: R1 25, R2 8, R3 2, **R5 0** |
| Close calls (12) | **1** false reject | 1.5% to 35.4% | item 60 "Backend / API Engineer, Radar" rejected by R1 because of the "/ API" |
| Kept (15) | **3** wrong, 2 unsure | 7.0% to 45.2% for the 3 | items 6 and 15 (Roblox sponsorship wording), 18 (Databricks "secret clearance"); items 26 and 34 are "?" |

## What I can honestly say about those numbers
- **Zero errors in 35 does not mean zero errors.** With 35 random rejects and none wrong, the true false-reject rate among the 2,969
  rejects is plausibly anywhere from 0% up to about 10%. It would take far more than 35 to rule out a small rate.
- **The sample says almost nothing about R3 and R5 rejects** (2 and 0 in the random sample), and nothing about postings the filter
  never sees (boards not in the snapshot).
- **The kept side is where the filter was weakest:** about one in five of the 15 kept postings (3) was clearly wrong, plus two I could
  not decide. The interval is wide (7% to 45%) because n is 15. This is a sample estimate, not a measured rate for all 99.
- **Shared framing:** my notes cite the filter's own rule codes, so agreement on the N verdicts is partly agreement with the same
  rules, not an independent judgement. One person labelled everything.
- **Tuning on the audit:** the v2 changes came from these labels, so v2 looks better on this sample by construction. The held-out
  measurement for a change is in `REPORT-one-change.md`; the v2 filter changes themselves have **no** held-out measurement.

## False friends (a word that matched for the wrong reason), measured on all 3,068 postings
- **"training"**: appears in **1,108** postings; only **421 (38.0%)** have a role title. A filter that treats "training" as a signal
  (wrong version W2) would wrongly keep the other **687**. This is why topic words count in the title only.
- **"sponsor"**: appears in **365** postings; **270 (74.0%)** are about visas, mostly Roblox's sentence. The rest are things like
  "executive sponsor" or "gain sponsorship for deployments". R4 v2 is anchored to visa words for this reason.
- **"ML"**: 16 titles contain the standalone token; a case-insensitive "ml" substring would also hit "HTML". R1's ML exclusion is
  case-sensitive for this reason.
- **"Go"** (in the claim labeler): "go-to-market" and "Go to market" are not the language.
- **"1 year of university education"** (claim labeler, **not fixed**): matched "years" and was labelled support for "asks for fewer
  than 3 years of experience". It is education, not experience.

## Rules added, cut or rejected after measuring (FILTER.md version log has the same list)
- **Changed R4** to also catch "may not be able to employ ... sponsorship" and visa-word + "sponsorship at this time". Measured:
  v1 R4 matched **0 of 3,068** postings; v2 moves 14 postings (all Roblox). Only items 6 and 15 of those 14 are in the labelled sample.
- **Changed R5** to also catch "secret clearance" and "government clearance". Moves 1 posting (item 18). Bare "clearance" was not added.
- **Changed R1** to allow "Backend / API Engineer" (only "/ API"). Moves 4 postings: 2 relevant, 2 rejected by R3.
- **Rejected** adding "Web Application Developer", "Security Engineer", "Solutions Engineer", "Integration Reliability Engineer"
  to R1: I labelled items 5, 29, 42, 47 and 52 as N.
- **Rejected** a PhD/degree rule: one case (item 26), now "?".

## Wrong versions the tests catch
`tests/wrong_filters.py` builds W1 (no seniority rule), W2 ("training" as a topic word) and W3 (no clearance rule);
`tests/test_filter.py` proves the 27 constructed cases fail each. The red run is `review/1-tests-before-rule-change.txt`.

## Unresolved
- **"U.S. Person Required"**: 3 shortlisted Palantir postings say it. A persona who needs sponsorship probably cannot meet it, and
  neither R4 nor R5 catches it. Not changed.
- **R5 and "clearance is a plus"**: R5 still rejects it (audit item 55 was a beneficial clearance). The abstention counterexample.
- **`cannot_tell`** never fired on a real posting (every posting has a location and a description); it is tested on constructed
  postings only.
- **R3 on Greenhouse** infers the country from free-text location; the audit did not test that inference beyond 2 R3 rejects.
