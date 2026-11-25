# Reject audit — results

Computed 2026-11-25T23:17:45.352Z from `audit/audit-sheet.csv` (hand verdicts by Aravind), `audit/key.json` (v1.0.0 decisions) and `runs/filter/v1.1.0-d` (v1.1.0-d decisions). Sample drawn from the v1.0.0 run with seed 20261125 (`audit/sample.json`).

## Judging plan (declared 2026-11-25, before any verdict)

- judge the first 30 of the 40 random rejects in seeded draw order (seed 20261125) and all 15 closest calls; the other 10 random rejects and all 15 PM-titled rejects stay unjudged.
- Judged (45): A001, A005, A006, A007, A010, A013, A014, A015, A016, A017, A018, A019, A020, A021, A022, A023, A024, A025, A026, A027, A029, A030, A032, A033, A034, A035, A036, A037, A038, A039, A040, A041, A042, A043, A044, A045, A046, A047, A048, A049, A050, A051, A052, A053, A055.
- Not judged (25): A002, A003, A004, A008, A009, A011, A012, A028, A031, A054, A056, A057, A058, A059, A060, A061, A062, A063, A064, A065, A066, A067, A068, A069, A070.
- A001-A030 is NOT the first 30 draws: sheet rows were shuffled after drawing. The draw order is recomputed from the seed by this script.
- SHA-256 of the judged list: 6de3072e176a5b16c083b282c25a15b52757c6cb132764460f9df00bc8851f38.

## Recheck (second pass)

- Declared before the recheck in `audit/recheck-plan.json` (2026-11-25; amended 2026-11-25, before the recheck was run: added A010, A013, A030, A037, A047, A049 (Aravind, in chat). Under v1.1.0-a these 6 closest calls are still rejected while their first-pass verdict is relevant; A013/A030/A037/A049 state 8+ years, A047 10+, A010 6-10+ (misread as 10+, FILTER.md §5.3).): 14 ids.
- Definition used: FILTER.md v1.1.0-a, §1: mostly roles requiring at most 4 years, sometimes 5+ or 6+, never 7+; locations as listed; no sponsorship refusal; a TPM counts only if the posting describes owning product direction.
- Reason: First pass used a looser bar than the written definition (excerpts only, stated years not checked; A035 is outside Maya's locations). The definition itself was then corrected. These rows are rechecked under the corrected definition.
- **Rechecked 14; revised 11; unchanged 3.**
- **Selection caveat:** These rows were chosen after seeing the v1.0.0 audit results; 11 of 14 are rows where the first-pass verdict disagreed with the filter. Rows where the first pass agreed with the filter (28 random rejects judged not_relevant) are not rechecked. The second pass is therefore not blind, and its selection leans toward agreement with the filter.
- **Definition caveat:** the relevance definition changed between the passes (persona corrected after the first-pass results, `f3cefa22`). View B measures v1.1.0-d on rows whose results motivated it (dev use), so it is not an independent test; the held-out labels are.

| audit_id | title | first pass | final | reason (Aravind's note) |
|---|---|---|---|---|
| A010 | Product Manager - Developer Experience, Bridge | relevant | relevant (unchanged) | 6-10+ yrs is PREFERRED, min reqs state no years; SF/NY works |
| A013 | Product Manager, Link - Consumer | relevant | not_relevant | 8+ yrs in MINIMUM reqs → n |
| A014 | Product Manager, Trips | relevant | cannot_tell | no role desc or years in text; body appears missing → c |
| A022 | Product Manager, Connect Growth & Monetization | relevant | relevant (unchanged) | "more than three years" in MINIMUM reqs → r |
| A027 | Technical Program Manager, Extensibility | relevant | not_relevant | TPM owns program, only influences roadmaps; min reqs 5+ yrs TPM-specific → n |
| A030 | Product Manager, Disputes | relevant | not_relevant | 8+ years PM in MINIMUM reqs -> n |
| A032 | Staff Product Manager,  Startup Products | relevant | not_relevant | 8+ yrs (PM or founder) in MINIMUM reqs → n |
| A035 | Staff Product Manager, Stripe Tax | relevant | not_relevant | Dublin → n (years only "significant", unstated) |
| A037 | Product Manager, Strategic Apps | relevant | not_relevant | 8+ yrs in MINIMUM reqs → n; title says PM, body says Staff PM |
| A042 | Product Manager - Issuance, Bridge | relevant | relevant (unchanged) | 5+ yrs PREFERRED only, min reqs no years; SF/NY → r |
| A044 | Technical Program Manager, Extensibility Platform | relevant | not_relevant | identical text to A027 → same verdict (n) |
| A047 | Product Manager, Services | relevant | not_relevant | 10+ yrs consumer PM required → n |
| A049 | Product Manager, Radar | relevant | not_relevant | 8+ yrs PM in MINIMUM reqs → n |
| A052 | Technical Program Manager, Money-as-a-Service | relevant | not_relevant | TPM, delivery only, partners with PMs; min 6+ yrs eng/TPM → n |

## Side by side

Each stratum is reported separately; strata are never pooled into one error rate. An error is a reject judged relevant or a keep judged not_relevant. cannot_tell decisions and cannot_tell verdicts are not counted as errors (they are listed in the views below).

| stratum | judged | view A errors | view B errors | view A' errors |
|---|---|---|---|---|
| random_reject | 30 of 40 | 2 of 30 (estimate 6.7%, exact 95% interval 0.8% to 22.1%) | 0 of 30 (estimate 0.0%, exact 95% interval 0.0% to 11.6%) | 0 of 30 (estimate 0.0%, exact 95% interval 0.0% to 11.6%) |
| closest_call | 15 of 15 | 12 | 3 | 4 |
| kept | 0 of 0 | 0 | 0 | 0 |
| cannot_tell | 3 of 3 | 0 | 0 | 0 |

- **View A:** v1.0.0 decisions vs first-pass verdicts.
- **View B:** v1.1.0-d decisions vs final verdicts.
- **View A':** v1.0.0 decisions vs final verdicts (summary only: isolates the verdict change from the rule change).
- The random_reject rows are a uniform sample of **v1.0.0's** 1061 rejects. Under a later version they measure how that version does on those same postings; they are not a sample of the later version's rejects.

## View A: v1.0.0 decisions vs first-pass verdicts

### random_reject (judged 30 of 40)

Verdicts: relevant 2, not_relevant 28, cannot_tell 0. Decisions: keep 0, cannot_tell 0, reject 30.

**Errors: 2 of 30 (estimate 6.7%, exact 95% interval 0.8% to 22.1%).** What this can show: the first 30 of 40 uniform draws (seeded order) from the 1061 v1.0.0 rejects in this snapshot. It estimates the error share within that population only, not for all postings, boards, dates, or versions.

| audit_id | title | decision | verdict | T | L | E (phrase) | P (terms) | note |
|---|---|---|---|---|---|---|---|---|
| A032 | Staff Product Manager,  Startup Products | reject | relevant **(error)** | 0.5 | 1 | 0 (8+ years) | 1 (payments, data) | recheck 2026-11-25: 8+ yrs (PM or founder) in MINIMUM reqs → n |
| A035 | Staff Product Manager, Stripe Tax | reject | relevant **(error)** | 0.5 | 0 | null (—) | 1 (payments, data) | recheck 2026-11-25: Dublin → n (years only "significant", unstated) |

### closest_call (judged 15 of 15)

Verdicts: relevant 15, not_relevant 0, cannot_tell 0. Decisions: keep 0, cannot_tell 3, reject 12.

**Errors: 12 of 15.** Selected by distance to the v1.0.0 threshold, not sampled: no population interval applies.

| audit_id | title | decision | verdict | T | L | E (phrase) | P (terms) | note |
|---|---|---|---|---|---|---|---|---|
| A005 | Product Manager, Connected Account Onboarding Experiences | reject | relevant **(error)** | 1 | 1 | 0 (6+ years) | 1 (payments, data) |  |
| A010 | Product Manager - Developer Experience, Bridge | reject | relevant **(error)** | 1 | 1 | 0 (10+ years) | 1 (payments, fintech, data) | recheck 2026-11-25: 6-10+ yrs is PREFERRED, min reqs state no years; SF/NY works |
| A013 | Product Manager, Link - Consumer | reject | relevant **(error)** | 1 | 1 | 0 (8+ years) | 1 (payments, data) | recheck 2026-11-25: 8+ yrs in MINIMUM reqs → n |
| A014 | Product Manager, Trips | cannot_tell | relevant | 1 | 1 | null (—) | 0 (—) | recheck 2026-11-25: no role desc or years in text; body appears missing → c |
| A020 | Product Manager, Terminal Developer Experiences | reject | relevant **(error)** | 1 | 1 | 0 (5+ years) | 1 (payments, data, mobile) |  |
| A022 | Product Manager, Connect Growth & Monetization | cannot_tell | relevant | 1 | 1 | null (—) | 1 (payments, ecommerce) | recheck 2026-11-25: "more than three years" in MINIMUM reqs → r |
| A025 | Product Manager, Treasury for Platforms | reject | relevant **(error)** | 1 | 1 | 0 (6+ years) | 1 (payments, data) |  |
| A027 | Technical Program Manager, Extensibility | reject | relevant **(error)** | 1 | 1 | 0 (5+ years) | 1 (payments, data) | recheck 2026-11-25: TPM owns program, only influences roadmaps; min reqs 5+ yrs TPM-specific → n |
| A030 | Product Manager, Disputes | reject | relevant **(error)** | 1 | 1 | 0 (8+ years) | 1 (payments, data) | recheck 2026-11-25: 8+ years PM in MINIMUM reqs -> n |
| A037 | Product Manager, Strategic Apps | reject | relevant **(error)** | 1 | 1 | 0 (8+ years) | 1 (payments, data) | recheck 2026-11-25: 8+ yrs in MINIMUM reqs → n; title says PM, body says Staff PM |
| A042 | Product Manager - Issuance, Bridge | cannot_tell | relevant | 1 | 1 | null (—) | 1 (payments, fintech, data) | recheck 2026-11-25: 5+ yrs PREFERRED only, min reqs no years; SF/NY → r |
| A044 | Technical Program Manager, Extensibility Platform | reject | relevant **(error)** | 1 | 1 | 0 (5+ years) | 1 (payments, data) | recheck 2026-11-25: identical text to A027 → same verdict (n) |
| A047 | Product Manager, Services | reject | relevant **(error)** | 1 | 1 | 0 (10+ years) | 0.5 (data) | recheck 2026-11-25: 10+ yrs consumer PM required → n |
| A049 | Product Manager, Radar | reject | relevant **(error)** | 1 | 1 | 0 (8+ years) | 1 (payments, data) | recheck 2026-11-25: 8+ yrs PM in MINIMUM reqs → n |
| A052 | Technical Program Manager, Money-as-a-Service | reject | relevant **(error)** | 1 | 1 | 0 (6+ years) | 1 (payments, fintech, data) | recheck 2026-11-25: TPM, delivery only, partners with PMs; min 6+ yrs eng/TPM → n |

### kept (judged 0 of 0)

Verdicts: relevant 0, not_relevant 0, cannot_tell 0. Decisions: keep 0, cannot_tell 0, reject 0.

v1.0.0 kept nothing, so this stratum is empty.

### cannot_tell (judged 3 of 3)

Verdicts: relevant 3, not_relevant 0, cannot_tell 0. Decisions: keep 0, cannot_tell 3, reject 0.

| audit_id | title | decision | verdict | T | L | E (phrase) | P (terms) | note |
|---|---|---|---|---|---|---|---|---|
| A014 | Product Manager, Trips | cannot_tell | relevant | 1 | 1 | null (—) | 0 (—) | recheck 2026-11-25: no role desc or years in text; body appears missing → c |
| A022 | Product Manager, Connect Growth & Monetization | cannot_tell | relevant | 1 | 1 | null (—) | 1 (payments, ecommerce) | recheck 2026-11-25: "more than three years" in MINIMUM reqs → r |
| A042 | Product Manager - Issuance, Bridge | cannot_tell | relevant | 1 | 1 | null (—) | 1 (payments, fintech, data) | recheck 2026-11-25: 5+ yrs PREFERRED only, min reqs no years; SF/NY → r |

## View B: v1.1.0-d decisions vs final verdicts

### random_reject (judged 30 of 40)

Verdicts: relevant 0, not_relevant 30, cannot_tell 0. Decisions: keep 0, cannot_tell 0, reject 30.

**Errors: 0 of 30 (estimate 0.0%, exact 95% interval 0.0% to 11.6%).** What this can show: the first 30 of 40 uniform draws (seeded order) from the 1061 v1.0.0 rejects in this snapshot. It estimates the error share within that population only, not for all postings, boards, dates, or versions. Zero errors does not mean zero: the data allow up to 11.6%.

### closest_call (judged 15 of 15)

Verdicts: relevant 6, not_relevant 8, cannot_tell 1. Decisions: keep 7, cannot_tell 3, reject 5.

**Errors: 3 of 15.** Selected by distance to the v1.0.0 threshold, not sampled: no population interval applies.

| audit_id | title | decision | verdict | T | L | E (phrase) | P (terms) | note |
|---|---|---|---|---|---|---|---|---|
| A005 | Product Manager, Connected Account Onboarding Experiences | keep | relevant | 1 | 1 | 0.5 (6+ years) | 1 (payments, data) |  |
| A010 | Product Manager - Developer Experience, Bridge | keep | relevant | 1 | 1 | 0.5 (6–10+ years) | 1 (payments, fintech, data) | recheck 2026-11-25: 6-10+ yrs is PREFERRED, min reqs state no years; SF/NY works |
| A014 | Product Manager, Trips | cannot_tell | cannot_tell | 1 | 1 | null (—) | 0 (—) | recheck 2026-11-25: no role desc or years in text; body appears missing → c |
| A020 | Product Manager, Terminal Developer Experiences | keep | relevant | 1 | 1 | 0.5 (5+ years) | 1 (payments, data, mobile) |  |
| A022 | Product Manager, Connect Growth & Monetization | cannot_tell | relevant | 1 | 1 | null (—) | 1 (payments, ecommerce) | recheck 2026-11-25: "more than three years" in MINIMUM reqs → r |
| A025 | Product Manager, Treasury for Platforms | keep | relevant | 1 | 1 | 0.5 (6+ years) | 1 (payments, data) |  |
| A027 | Technical Program Manager, Extensibility | keep | not_relevant **(error)** | 1 | 1 | 0.5 (5+ years) | 0.5 (data) | recheck 2026-11-25: TPM owns program, only influences roadmaps; min reqs 5+ yrs TPM-specific → n |
| A042 | Product Manager - Issuance, Bridge | cannot_tell | relevant | 1 | 1 | null (—) | 1 (payments, fintech, data) | recheck 2026-11-25: 5+ yrs PREFERRED only, min reqs no years; SF/NY → r |
| A044 | Technical Program Manager, Extensibility Platform | keep | not_relevant **(error)** | 1 | 1 | 0.5 (5+ years) | 0.5 (data) | recheck 2026-11-25: identical text to A027 → same verdict (n) |
| A052 | Technical Program Manager, Money-as-a-Service | keep | not_relevant **(error)** | 1 | 1 | 0.5 (6+ years) | 1 (fintech, data) | recheck 2026-11-25: TPM, delivery only, partners with PMs; min 6+ yrs eng/TPM → n |

### kept (judged 0 of 0)

Verdicts: relevant 0, not_relevant 0, cannot_tell 0. Decisions: keep 0, cannot_tell 0, reject 0.

v1.0.0 kept nothing, so this stratum is empty.

### cannot_tell (judged 3 of 3)

Verdicts: relevant 2, not_relevant 0, cannot_tell 1. Decisions: keep 0, cannot_tell 3, reject 0.

| audit_id | title | decision | verdict | T | L | E (phrase) | P (terms) | note |
|---|---|---|---|---|---|---|---|---|
| A014 | Product Manager, Trips | cannot_tell | cannot_tell | 1 | 1 | null (—) | 0 (—) | recheck 2026-11-25: no role desc or years in text; body appears missing → c |
| A022 | Product Manager, Connect Growth & Monetization | cannot_tell | relevant | 1 | 1 | null (—) | 1 (payments, ecommerce) | recheck 2026-11-25: "more than three years" in MINIMUM reqs → r |
| A042 | Product Manager - Issuance, Bridge | cannot_tell | relevant | 1 | 1 | null (—) | 1 (payments, fintech, data) | recheck 2026-11-25: 5+ yrs PREFERRED only, min reqs no years; SF/NY → r |

## Named false friends (Aravind's call, from postings judged by hand)

- **"training"**, named by Aravind on 2026-11-25. Rows: A014, A047. In both rows it appears only in Airbnb's pay boilerplate, not in anything about the role. (Corpus count: 172 of 203 Airbnb postings contain it.) Note: "training" is not one of the filter's topic terms in v1.0.0 or v1.1.0-a, so it changed no filter decision here; it is a false friend for any keyword filter that would count it, and the same boilerplate sentence also carries "work experience", which the experience rule scans (no years phrase, so no effect).
  - Line (verbatim, from both rows): "Our job titles may span more than one career level. The actual base pay is dependent upon many factors, such as: training, transferable skills, work experience, business needs and market demands."

## Not checked

- **PM-titled rejects (pm_reject):** 15 drawn (seed 20261126) from 133 PM/product-titled v1.0.0 rejects; **none judged**. No error estimate exists for PM-titled rejects, where a false reject matters most.
- **Random rejects, draws 31-40:** on the sheet, not judged, not counted.
- **Recheck coverage:** the 31 judged rows outside the recheck plan keep their first-pass verdict under the corrected definition.
