# AUDIT — the reject audit of filter v1.0

**Who did what.** Every verdict and every reason in the audit sheet is mine.
- **My verdicts:** I judged all 50 rows myself on 2026-11-25, in my own copy of the sheet. They were copied into `state/audit/audit_v1.0.csv` unchanged, and no other column moved.
- **Claude's part:** Claude drew the sample, wrote the sheet, ran `audit.py report`, and drafted this write-up around my verdicts. Claude drafted no verdict.
- **Status:** reviewed.

## The sample, stated honestly
- **What was drawn:** with seed 20261125, from the **4,203 postings outside the held-out set** (`audit.py draw`; `state/audit/draw_v1.0.json`).
  - **kept:** all 10 postings v1.0 keeps outside held-out. That's every one, not a sample.
  - **reject:** 30 random postings from the 4,193 rejects.
  - **near:** the 10 rejected postings closest to the threshold. No reject rule fired, and each scored 3, one below the threshold of 4. Ties were broken by the seed.
- **What the sheet hid:** the order was shuffled, so I couldn't see a row's group while judging. Each row did show the filter's verdict and its reason.
- **What these numbers describe:** these groups, on these 14 boards. The 14 boards were picked by rules aimed at analyst titles, so this is not "postings in general".
- **What the reject group allows:** 0 errors in 30 random rejects is consistent with a true reject error rate anywhere from 0% to 11% (95% Wilson interval). At the top of that range, that would be about 460 of the 4,193 rejects. The audit can't rule that out.

## Results
Output of `python3 audit.py report`, saved in `state/audit/report_v1.0.txt`. "Wrong" means I judged the verdict wrong for Riley.

| Group | Wrong | 95% interval (Wilson) |
|---|---|---|
| kept | **10/10** | 0.72–1.00 |
| reject (random) | 0/30 | 0.00–0.11 |
| near threshold | 0/10 | 0.00–0.28 |
| all 50 | 10/50 | 0.11–0.33 |

**What it says:**
- **Every error is a false keep.** Outside the held-out set, every posting v1.0 keeps is one I judged Riley would not apply to.
- **On the reject side, I found no posting Riley should have seen,** including the 10 that missed the threshold by one point.
- **The filter keeps too much, not too little.** On held-out it kept 2, both "yes" (`SCORE.md`). Outside held-out, it kept 10, none of them right.

## Why the 10 keeps were wrong (from my reasons)

| Why, in my words | Rows | What the filter missed |
|---|---|---|
| Requires 2+ years in the field (internships don't count, or the experience is in finance) | #19, #27, #30, #31, #41 | R2 rejects only at a lowest stated requirement of 3 or more. "2+ years" passes by design (see F3 in `SCORE.md`). |
| Needs experience in a specific system or field: Salesforce administration; 6+ years of FP&A | #4, #35 | #35: v1.0's R2 code took the lower of "6+ years" and "2+ years" (F4). #4: no rule reads named-system experience. |
| Veeva does not sponsor this role | #12 | R4's phrases don't include "does not provide sponsorship" (F1) |
| Part-time student contract | #34 | No rule reads employment type |
| Requires graduating December 2027 or later | #48 | No rule reads graduation dates |

## The false friend: "reporting" in "Reporting to …"
- **Where:** #27, Datadog's "FP&A Analyst R&D", is kept with a score of exactly 4.
- **How it got there:** a bare "analyst" in the title (+1) and three skill words: "Tableau", "Excel", and **"Reporting"**. The "Reporting" is in "**Reporting to the Senior Manager**, you will…". That sentence is about who the analyst reports to, not reporting work.
- **What it changed:** without that point, the posting scores 3 and is rejected.
- **FILTER.md predicted it.** v1.0 lists "'reporting' in 'reporting to the CFO'" as an expected false friend and doesn't special-case it, so that the audit could measure it first. It did.

**The second false friend, bare "analyst":** it is behind 5 of the 10 wrong keeps (#27, #30, #31, #35, #41). Three are finance analysts and two are product analysts. A bare "analyst" earns only 1 point, so each needed three skill words to pass. Finance and product postings list SQL, Tableau, and Excel as readily as data-analyst postings do.

**Not seen:** "excel" as a verb. It appears in none of the 10 wrong keeps.

## The changelog
Every rule added, cut, or rejected, from FILTER.md's first version to now.

| Date | Change | Kind | Evidence | Decision |
|---|---|---|---|---|
| 2026-11-17 | R1 seniority, R2 years, R3 location, R4 no sponsorship; the score; threshold 4 | added (v1.0) | My interview answers | Mine, committed in `126a2fd` |
| 2026-11-17 | "I cannot tell" on any insufficient claim | **rejected** before commit | Claude flagged that it would abstain on almost every posting | Narrowed to role, seniority, or location. Mine. |
| 2026-11-18 | The board-probe US check treated "IL" as Illinois | fixed (probe only) | Veeva's "Israel - Kiryat Ono IL" | Recorded in FILTER.md |
| 2026-11-25 | Supplement boards by a full-text probe rule | added (v1.1) | All 92 v1.0 labels were "no" | Mine (`6a3ea0f`) |
| 2026-11-25 | The v1.1 probe rule's first title test ("any analyst") | **rejected** before the probe ran | It flagged 16 finance, tax, and compliance analysts in the v1.0 corpus | Replaced by role phrase, or "analyst" with a data word |
| 2026-11-25 | Implementing R3: "SF" and a "San Francsico" typo count as US; "AMER", "NAMER", and "Americas" count as unknown, not US | implementation of v1.0 | A listing of all 340 non-US location strings | Recorded in FRICTIONAL. "Toronto, CA" counting as US remains a known false friend. |
| 2026-11-25 | F1: R4 also matches "does not provide sponsorship" | **added (v1.2)** | Audit #12; held-out unchanged; 1 corpus flip | Adopted, my decision |
| 2026-11-25 | F2: threshold 4 → 5 | **rejected** | Tuning only; held-out unchanged | Rejected, my decision |
| 2026-11-25 | F3: R2 rejects at 2+ years | **rejected** | It would fix 5 of my 10 audit errors, but loses a held-out "yes" (recall 2/2 → 1/2) | Rejected, my decision |
| 2026-11-25 | F4: R2 reads the highest of the stated requirements | **changed (v1.2), a code fix** | Audit #35; held-out unchanged; 1 corpus flip | Adopted, my decision |
| 2026-11-25 | F5: "reporting" not counted before "to" | **added (v1.2)** | Audit #27; held-out unchanged; 1 corpus flip | Adopted, my decision |
| 2026-11-25 | C1: prompt without "copy exactly"; C2: title-only context; C3: "no field names in quotes"; A1: abstain without seniority | C3 **added (v1.2)**; C1, C2, and A1 **rejected** | `SCORE.md` | My decisions |

**The result:** v1.2 keeps 9 postings instead of 12. My audit errors #12, #27, and #35 are now rejected, and held-out stays 2/2 and 2/2 (`SCORE.md`, "v1.2 as adopted").

**What the audit adds to those decisions:**
- **F3 is the hard one.** It would remove the largest group of my audit errors, the 2-year postings, but it costs the one held-out "yes" whose "2+ years" is only *preferred*.
- **A rule that separates "required" from "preferred"** would be the next change to try. It is not measured here.
