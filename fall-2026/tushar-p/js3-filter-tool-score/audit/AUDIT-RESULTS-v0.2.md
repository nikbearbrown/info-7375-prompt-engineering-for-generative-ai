# JS3 filter v0.2: development measurement on the audit sheet

This compares filter v0.2 (FILTER.md v0.2, frozen 2026-11-23, C1–C6, with C4's preferred-heading rule amended 2026-11-23 before any held-out comparison), each single change C1–C6 on top of v0.1, and v0.1 against the 48 hand labels on `audit/audit-sheet.csv`.

**Development data, not a test.** The v0.2 rules were chosen after reading these same 48 rows, so better agreement here is expected. It is not evidence that v0.2 generalizes. That is what the sealed held-out sheet is for, and it has not been compared to any filter result.

Every number here comes from `python audit/audit_v02.py` (run from `js3-filter-tool-score/`). The script:
- evaluates each mode in-process with the current `agent/filter.py`, the same code `python -m agent.filter --rules MODE` runs;
- reads only the audit sheet;
- recovers the blind labels from the labeler's correction history in each note, and checks them against commit `f97f528a`; they match.

## Verdict counts per mode (all 979 postings)

| mode | keep | reject | cannot_tell |
|---|---|---|---|
| v0.1 | 8 | 951 | 20 |
| v0.1+C1 | 21 | 951 | 7 |
| v0.1+C2 | 10 | 951 | 18 |
| v0.1+C3 | 7 | 953 | 19 |
| v0.1+C4 | 8 | 950 | 21 |
| v0.1+C5 | 7 | 952 | 20 |
| v0.1+C6 | 8 | 952 | 19 |
| v0.2 | 17 | 956 | 6 |

## Random-reject misses (v0.1's rejects: 30 drawn at random from 951)

| Labels | Not reject | Wilson 95% | Out of 951 rejects |
|---|---|---|---|
| **Blind** (as labeled before the filter's verdicts were seen; commit `f97f528a`) | 6/30 (4 keep, 2 cannot_tell) | 9.5% – 37.3% | about 90 – 355 |
| **After post-unblinding corrections** (rows 19, 29, 40, 45 → reject, by Tushar after reading `AUDIT-RESULTS.md`) | 2/30 (2 cannot_tell: rows 16, 47) | 1.8% – 21.3% | about 18 – 203 |

**The blind figure is the result of the blind audit.** The corrected figure is post-unblinding: the four corrections were made after seeing the filter's verdicts, so it is not a blind measurement and must not be presented as one. Both are estimates from 30 random rows, not measured rates for all 951 rejects, and 27 of the 30 were easy G1 title rejects.

Raw script output:

- blind labels (commit f97f528a): 6/30 not reject ({'reject': 24, 'cannot_tell': 2, 'keep': 4}); Wilson 95% [9.5%, 37.3%] ≈ 90–355 of 951
- after post-unblinding corrections: 2/30 not reject ({'reject': 28, 'cannot_tell': 2}); Wilson 95% [1.8%, 21.3%] ≈ 18–203 of 951
- corrected rows: ['19', '29', '40', '45']

## Agreement with the hand labels, per mode (48 audit rows)

| mode | agree, blind labels | agree, corrected labels | keep | reject | cannot_tell |
|---|---|---|---|---|---|
| v0.1 | 28/48 | 32/48 | 8 | 30 | 10 |
| v0.1+C1 | 35/48 | 39/48 | 15 | 30 | 3 |
| v0.1+C2 | 30/48 | 34/48 | 10 | 30 | 8 |
| v0.1+C3 | 28/48 | 32/48 | 7 | 31 | 10 |
| v0.1+C4 | 28/48 | 32/48 | 8 | 30 | 10 |
| v0.1+C5 | 27/48 | 31/48 | 7 | 31 | 10 |
| v0.1+C6 | 28/48 | 32/48 | 8 | 30 | 10 |
| v0.2 | 34/48 | 38/48 | 13 | 32 | 3 |

Reading the table:
- **C1 accounts for almost all of the gain** (+7 rows): rows 13, 14, 18, 20, 21, 34 and 39 state no minimum experience, and you labeled all seven keep.
- **C2** adds 2 rows (20 and 39, "less than two years"), which C1 already covers.
- **C3** moves one audit row: row 3 goes from keep to reject. You labeled it cannot_tell, so agreement doesn't change.
- **C4 and C6** change no audit verdict.
- **C5 costs one row.** Row 6 (Software Engineer, Vulnerability Management) scored 2 only from the Stripe boilerplate. Without "platform" it scores 1 and is rejected, but you labeled it keep. The rule removed a point that carried no evidence about the job, and the result was a wrong reject on this row.
- **v0.2 is 38/48, one below C1 alone (39/48).** The difference is row 6.

## v0.2 confusion matrix vs corrected labels

| filter ↓ / me → | keep | reject | cannot_tell |
|---|---|---|---|
| **keep** | 9 | 3 | 1 |
| **reject** | 1 | 28 | 3 |
| **cannot_tell** | 0 | 2 | 1 |

## Audit rows whose verdict changes from v0.1 to v0.2

| row | title | v0.1 | v0.2 | v0.2 G4 | me (corrected) | changes that move it alone |
|---|---|---|---|---|---|---|
| 3 | Machine Learning Engineer, Growth Platform | keep | reject | fail: 3+ years | cannot_tell | C3 |
| 6 | Software Engineer, Vulnerability Management | keep | reject | pass: 2+ years | keep | C5 |
| 13 | Software Engineer, Web Infrastructure | cannot_tell | keep | pass: - | keep | C1 |
| 14 | Software Engineer, New Grad (Dec 2026) | cannot_tell | keep | pass: - | keep | C1 |
| 18 | Software Engineer, Privy | cannot_tell | keep | pass: - | keep | C1 |
| 20 | Software Engineer, Early Career (AI) | cannot_tell | keep | pass: max: less than two years | keep | C1, C2 |
| 21 | Software Engineer, Mobile Core (Android) | cannot_tell | keep | pass: - | keep | C1 |
| 34 | Software Engineer, Product Infrastructure | cannot_tell | keep | pass: - | keep | C1 |
| 39 | Software Engineer, Growth (Early Career) | cannot_tell | keep | pass: max: less than two years | keep | C1, C2 |

**What v0.2 does not change, by decision:**
- **Rows 31, 33, 35 and 48 are still keep** under v0.2. Their only stated minimum is the lower bound of "2–12+ years" or "2–10+ years", which is ≤ 2. You labeled them reject or cannot_tell. C4 says never to reject only because a range's upper end is high.
- **Rows 10 and 42 are still cannot_tell.** The G3 "N/A" → reject change was rejected.
- **Rows 16 and 47 are still reject.** Your label is cannot_tell, and the title fails G1.

## Infrastructure check (no rule change)

"Company boilerplate" here means the "About Stripe" sentences that describe the company rather than the role. They were chosen by reading every sentence that contains "infrastructure" and repeats in 4 or more postings; they are listed in `INFRA_BOILERPLATE` in `audit/audit_v02.py`.

- postings containing 'infrastructure': 799; only in company boilerplate: 431
- by board: {'greenhouse/stripe': 431}
- v0.1: scored postings 8; infrastructure point only from boilerplate 2; of those kept 2; keeps that would fall below 2 without that point 1 ('Software Engineer, Vulnerability Management')
- v0.2: scored postings 19; infrastructure point only from boilerplate 2; of those kept 1; keeps that would fall below 2 without that point 0
- examples:
  - greenhouse/stripe 8172510 'Abuse Investigator': "Stripe is a financial infrastructure platform for businesses."
  - greenhouse/stripe 8194287 'Data Analyst, Intern': "We build entirely new pieces of financial infrastructure to enable new ideas."
  - greenhouse/stripe 8194291 'Data Analyst, Intern': "The most ambitious companies in the world use Stripe as core infrastructure to grow faster."
  - greenhouse/stripe 8186367 'Integration Reliability Engineer Intern, Technical Operations': "And our significant advances in risk and fraud infrastructure over many years are making the internet economy safer and more accessible."

"infrastructure" stays a topic word in v0.2. Under v0.2, no keep depends on a boilerplate-only "infrastructure" point. Under v0.1 one did: row 6, which C5 already rejects through "platform".

## C4 preferred-heading amendment (2026-11-23)

C4 as first frozen counted a minimum under a "Preferred qualifications" heading as mandatory unless its own sentence said "preferred", "nice to have", "bonus" or "a plus". Tushar amended C4 before any held-out comparison: a minimum under a preferred heading is now preferred, and ignored, until the next heading. FILTER.md v0.2 defines "heading": an `<h1>`–`<h6>`, or a short (8 words or fewer) non-list block that doesn't end in ".", "!" or "?".

**Verdicts changed by the amendment: none, in every mode.** Every count and table above is the same as before the amendment.

**Why none changed.** G4 changed in 41 postings, but all 41 are already decided by another gate:
- 40 fail G1 on the title.
- 1 is cannot_tell on G3: audit row 10, location "N/A". Its preferred "2+ years" is now ignored, and G4 stays pass on the mandatory "2-5+ years".

In this run, no posting that passes G1, G2 and G3 has a minimum that only the heading rule marks as preferred.

Output of `python audit/audit_v02.py`. "Pre-amendment" means the same code run with block kinds removed, which gives no headings:

Pre-amendment C4 = the same code with block kinds removed (no headings; own sentence only).

- v0.1+C4: G4 output changed in 41 postings, G4 result changed in 23, verdict changed in 0; the verdict of every G4-changed posting is decided by: {'G1': 40, 'G3': 1}
  - audit row 10 'Full Stack Engineer, Revenue': G4 pass ['2-5+ years', '2+ years'] -> pass ['2-5+ years', 'ignored (preferred): 2+ years']; verdict cannot_tell (unchanged)
- v0.2: G4 output changed in 41 postings, G4 result changed in 6, verdict changed in 0; the verdict of every G4-changed posting is decided by: {'G1': 40, 'G3': 1}
  - audit row 10 'Full Stack Engineer, Revenue': G4 pass ['2-5+ years', '2+ years'] -> pass ['2-5+ years', 'ignored (preferred): 2+ years']; verdict cannot_tell (unchanged)
  - greenhouse/stripe 8328323 'IT Support Engineer': G4 unknown -> pass ['At least 2 years', 'ignored (preferred): 3+ years']; verdict reject via G1
  - greenhouse/stripe 8204227 'Product Manager - Developer Experience, Bridge': G4 fail -> pass ['ignored (preferred): 6–10+ years']; verdict reject via G1
  - greenhouse/stripe 8223723 'Product Manager - Payments Experience, Bridge': G4 fail -> pass ['ignored (preferred): 6-10+ years']; verdict reject via G1
  - greenhouse/stripe 7214197 'Program Manager, Risk Ops Enablement': G4 unknown -> fail ['6+ years', 'ignored (preferred): 2+ years']; verdict reject via G1
  - greenhouse/stripe 8214620 'Strategy & Operations Business Partner, Solution Architecture': G4 unknown -> fail ['8+ years', '11+ years', 'ignored (preferred): 2+ years']; verdict reject via G1
  - greenhouse/stripe 8159355 'University Recruiter': G4 fail -> pass ['ignored (preferred): 3-4 years']; verdict reject via G1

## Readings to check before the held-out comparison

1. **C4 "sentence" and "heading".** Settled by the 2026-11-23 amendment above.
2. **C2 maximums accept spelled numbers one–ten** ("less than two years"), which is how rows 20 and 39 are written. Tushar accepted this; it is recorded in the FILTER.md changelog. Minimums still need digits, or C6's "word (N)".
3. **G4 "1 year" (singular)** was not part of v0.2 and is unchanged.

## Errata

- The post-unblinding correction notes on rows 19, 29, 40, 45 say 2026-11-24 because of a typo in Tushar's instruction; the labeled_at stamps (2026-11-23) are correct.
