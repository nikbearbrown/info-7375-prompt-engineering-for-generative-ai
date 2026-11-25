# Reject audit — results (spec v1.0.0)

Computed 2026-11-25T22:41:11.004Z from `audit/audit-sheet.csv` (hand verdicts by Aravind) and `audit/key.json`. Sample drawn with seed 20261125 (`audit/sample.json`).

## Judging plan (declared 2026-11-25, before any verdict)

- judge the first 30 of the 40 random rejects in seeded draw order (seed 20261125) and all 15 closest calls; the other 10 random rejects and all 15 PM-titled rejects stay unjudged.
- Judged (45): A001, A005, A006, A007, A010, A013, A014, A015, A016, A017, A018, A019, A020, A021, A022, A023, A024, A025, A026, A027, A029, A030, A032, A033, A034, A035, A036, A037, A038, A039, A040, A041, A042, A043, A044, A045, A046, A047, A048, A049, A050, A051, A052, A053, A055.
- Not judged (25): A002, A003, A004, A008, A009, A011, A012, A028, A031, A054, A056, A057, A058, A059, A060, A061, A062, A063, A064, A065, A066, A067, A068, A069, A070.
- A001-A030 is NOT the first 30 draws: sheet rows were shuffled after drawing. The draw order is recomputed from the seed by this script.
- SHA-256 of the judged list: 6de3072e176a5b16c083b282c25a15b52757c6cb132764460f9df00bc8851f38.

Each stratum is reported separately. They are never pooled into one error rate.

## random_reject (judged 30 of 40 on the sheet)

My verdicts: relevant 2, not_relevant 28, cannot_tell 0.

**False rejects (I judged relevant): 2 of 30.** Estimate 6.7%, exact 95% interval 0.8% to 22.1%.

What this can show: the sample is 30 of the 1061 rejects in this snapshot (the first 30 of 40 uniform draws, in seeded order), under spec v1.0.0. It estimates the false-reject share *within that population* only. It is not a rate for all postings, other boards, other dates, or other filter versions.  

| audit_id | title | decision | score | T | L | E (phrase) | P (terms) | my verdict | my note |
|---|---|---|---|---|---|---|---|---|---|
| A032 | Staff Product Manager,  Startup Products | reject | 0.55 | 0.5 | 1 | 0 (8+ years) | 1 (payments, data) | relevant |  |
| A035 | Staff Product Manager, Stripe Tax | reject | 0.425 | 0.5 | 0 | null (—) | 1 (payments, data) | relevant |  |

## closest_call (judged 15 of 15 on the sheet)

My verdicts: relevant 15, not_relevant 0, cannot_tell 0.

**Disagreements: 12 of 15** (decided rows only; cannot_tell rows are listed, not scored). These were *selected* by distance to the threshold, not sampled, so no population interval applies.

| audit_id | title | decision | score | T | L | E (phrase) | P (terms) | my verdict | my note |
|---|---|---|---|---|---|---|---|---|---|
| A005 | Product Manager, Connected Account Onboarding Experiences | reject | 0.75 | 1 | 1 | 0 (6+ years) | 1 (payments, data) | relevant |  |
| A010 | Product Manager - Developer Experience, Bridge | reject | 0.75 | 1 | 1 | 0 (10+ years) | 1 (payments, fintech, data) | relevant |  |
| A013 | Product Manager, Link - Consumer | reject | 0.75 | 1 | 1 | 0 (8+ years) | 1 (payments, data) | relevant |  |
| A014 | Product Manager, Trips | cannot_tell | 0.775 | 1 | 1 | null (—) | 0 (—) | relevant |  |
| A020 | Product Manager, Terminal Developer Experiences | reject | 0.75 | 1 | 1 | 0 (5+ years) | 1 (payments, data, mobile) | relevant |  |
| A022 | Product Manager, Connect Growth & Monetization | cannot_tell | 0.875 | 1 | 1 | null (—) | 1 (payments, ecommerce) | relevant |  |
| A025 | Product Manager, Treasury for Platforms | reject | 0.75 | 1 | 1 | 0 (6+ years) | 1 (payments, data) | relevant |  |
| A027 | Technical Program Manager, Extensibility | reject | 0.75 | 1 | 1 | 0 (5+ years) | 1 (payments, data) | relevant |  |
| A030 | Product Manager, Disputes | reject | 0.75 | 1 | 1 | 0 (8+ years) | 1 (payments, data) | relevant |  |
| A037 | Product Manager, Strategic Apps | reject | 0.75 | 1 | 1 | 0 (8+ years) | 1 (payments, data) | relevant |  |
| A042 | Product Manager - Issuance, Bridge | cannot_tell | 0.875 | 1 | 1 | null (—) | 1 (payments, fintech, data) | relevant |  |
| A044 | Technical Program Manager, Extensibility Platform | reject | 0.75 | 1 | 1 | 0 (5+ years) | 1 (payments, data) | relevant |  |
| A047 | Product Manager, Services | reject | 0.7 | 1 | 1 | 0 (10+ years) | 0.5 (data) | relevant |  |
| A049 | Product Manager, Radar | reject | 0.75 | 1 | 1 | 0 (8+ years) | 1 (payments, data) | relevant |  |
| A052 | Technical Program Manager, Money-as-a-Service | reject | 0.75 | 1 | 1 | 0 (6+ years) | 1 (payments, fintech, data) | relevant |  |

## kept (judged 0 of 0 on the sheet)

My verdicts: relevant 0, not_relevant 0, cannot_tell 0.

No postings were kept by spec v1.0.0, so there is nothing to sample. A false-keep rate cannot be estimated for this version.

## cannot_tell (judged 3 of 3 on the sheet)

My verdicts: relevant 3, not_relevant 0, cannot_tell 0.

The filter abstained on these. My verdicts above say what an answer would have been.

| audit_id | title | decision | score | T | L | E (phrase) | P (terms) | my verdict | my note |
|---|---|---|---|---|---|---|---|---|---|
| A014 | Product Manager, Trips | cannot_tell | 0.775 | 1 | 1 | null (—) | 0 (—) | relevant |  |
| A022 | Product Manager, Connect Growth & Monetization | cannot_tell | 0.875 | 1 | 1 | null (—) | 1 (payments, ecommerce) | relevant |  |
| A042 | Product Manager - Issuance, Bridge | cannot_tell | 0.875 | 1 | 1 | null (—) | 1 (payments, fintech, data) | relevant |  |

## Not checked

- **PM-titled rejects (pm_reject):** 15 drawn (seed 20261126) from a population of 133 PM/product-titled rejects; **none judged**. No error estimate exists for PM-titled rejects, the group where a false reject would matter most.
- **Random rejects, draws 31-40:** on the sheet, not judged, not counted.
