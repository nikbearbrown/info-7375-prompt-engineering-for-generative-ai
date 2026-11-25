# Review packet - one Claude Code change (Chapter 6)

**Change:** Greenhouse postings get a country, so R3 stops rejecting every Greenhouse job.
**Made by:** Claude Code (Opus 5.5), 2026-11-01. **Reviewed and decided by:** Vrajesh (steps 5-6).
**Files changed:** `earlybird/boards.py` only. **Test added first:** `tests/test_review_r3.py`.

> How the defect was picked: on 2026-10-31 I first chose the JS1 years-regex false positive. Claude searched 288 real non-senior SWE postings on all 9 boards and found 0 false positives (72 of 72 R2-by-years failures were real experience lines), so I switched to this one. Claude had named this defect as an option *before* the first multi-board run. The run then showed it for real.

## 1. Reproduce the defect (end to end, as a user sees it)
`python -m earlybird run --live --label run2-live` on 2026-11-01 00:09 EDT → [`reports/run2-live.md`](../reports/run2-live.md)
- 177 new postings on Stripe, Figma and Databricks, **0 relevant**.
- Databricks **"Software Engineer - New Grad (2027 Start)"** (Bellevue, WA; Mountain View, CA; San Francisco, CA; Vancouver) was rejected with `R3: posting country is None, not the US`. That is exactly the job this agent exists to find.
- The validator caught it on its own: 10 records `cite 'address.postalAddress.addressCountry', which does not exist` (the "Records citing a missing field" column).
- Cause: `boards.normalize("greenhouse", ...)` copies `location.name` (free text) but sets no `address`. JS1's R3 reads `address.postalAddress.addressCountry`, which only Ashby (and, after mapping, Lever) provide.

## 2. Test written before the patch
[`tests/test_review_r3.py`](../tests/test_review_r3.py), run against the unpatched code → [`2-test-before-patch.txt`](2-test-before-patch.txt): **3 of 4 fail** with the real symptom (`'R3' == 'R3' : posting country is None`, `None != 'USA' : San Mateo, CA, United States`, records citing a missing field).
The 4th (`test_non_us_posting_still_fails_r3`, Sao Paulo) passed even before the patch, because *everything* failed R3. It is there to stop a patch that "fixes" R3 by letting every posting through.

## 3. The diff, read as a behavior change
[`3-patch.diff`](3-patch.diff) (33 lines added, 2 removed, one file). What changes for a user:
- Every Greenhouse posting now has `address.postalAddress.addressCountry`: `"USA"` if its location text names the US, a US state, or `, XX` with a US state code; otherwise `None` (present, unknown).
- A posting open in several places counts as US if **one** of them is US (the applicant can choose that office). This is a relevance decision, not just a bug fix.
- `US` counts only in upper case, so the English word "us" does not.
- New field `country_inferred_from: "location.name"` marks the country as inferred, not given by the ATS.
- On the 2026-11-01 data, 1,678 of 2,683 Greenhouse postings are now `USA` ([`5-location-audit.txt`](5-location-audit.txt), all 740 distinct strings listed).
- Same 190 new postings, before vs after ([`4-before-after.txt`](4-before-after.txt)): relevant **0 → 4** on Greenhouse, invalid records **10 → 0**. The 4 that changed are Databricks New Grad 2027 (×2), Stripe "Software Engineer - Full stack" (Seattle), and Stripe "Software Engineer, Fraud System Interventions" (South San Francisco).

## 4. Did the change stay in scope?
- Only `earlybird/boards.py` changed. `rule.py`, `validate.py` and `resume.py` are still byte-identical to JS1 (`cmp` on 2026-11-01).
- Ashby and Lever are untouched: Commure and Palantir verdicts are the same before and after (`4-before-after.txt`).
- Not done on purpose: no change to R3's wording, no city list, no handling of "Remote". Each would widen the change. They are listed in step 7 instead.

## 5. Commands I ran myself (Vrajesh, 2026-11-10)
Run these and paste what you see (or "same as the file"):
```bash
python -m unittest tests.test_review_r3 -v                 # expect 4 ok
python -m unittest discover -s tests                        # expect all OK
git diff --no-index review/before-patch/boards.py earlybird/boards.py
python -m earlybird run --replay 2026-10-23 --label my-review-day1 --state data/state/my-review.json --only ashby:commure,greenhouse:stripe,greenhouse:figma,greenhouse:databricks,lever:palantir
python -m earlybird run --replay 2026-11-01 --label my-review-day2 --state data/state/my-review.json --only ashby:commure,greenhouse:stripe,greenhouse:figma,greenhouse:databricks,lever:palantir
#   expect: stripe 2 relevant, databricks 2 relevant; open reports/my-review-day2.md and read the 4
```
- Date: 2026-11-10, Windows cmd. My full terminal output, pasted verbatim: [`6-my-run-2026-11-10.txt`](6-my-run-2026-11-10.txt).
- What the output shows: 4/4 review tests ok; 57/57 tests ok; day 2 = Stripe 2 relevant, Databricks 2 relevant, Palantir 1, the same as Claude's after-fix run.
- What I saw in `reports/my-review-day2.md`, my words: "I saw that there are 7 new opening in commure and 91 new opening on GreenHouse stripr"

## 6. Accept, revise, or reject (Vrajesh, 2026-11-10)
The evidence for the decision:
- **For accepting:** it fixes the reproduced defect; 4 real entry-level US SWE jobs now reach me; 0 invalid records; scope is one file.
- **Against, or for revising:** 1 known false positive (`'Toronto, CA'` counted as US, since `CA` is Canada there); many US jobs still missed (step 7); the multi-location rule is a judgment I am making, not a fact.
- **Decision: revise.** My words (2026-11-10): "Fix for Toronto: Add a conditional check that looks at the context of the abbreviation. If CA is preceded by a known Canadian city  (or if the input format allows for country codes), map it to Canada instead of the US state of California.Fix for Bare Cities: Implement a fallback dictionary or a named-entity recognition (NER) lookup for the world's top major cities.  If an input matches "Chicago", without a state or country attached, the system should automatically resolve it to its primary global location. "Keep It to United States Only""
- How the revision was done: see step 6b below.

## 6b. The revision, done the same way (2026-11-10)
- **Tests first:** class `Revision` in [`tests/test_review_r3.py`](../tests/test_review_r3.py), from real 11-01 location strings. Run before the revised code → [`7-revision-test-before.txt`](7-revision-test-before.txt): 2 of 4 fail for exactly my two reasons (`None != 'USA' : Chicago`, `'USA' is not None : Toronto, CA`). The 2 that pass are guards: California `, CA` must stay US, and non-US bare cities (Dublin, London, Toronto, Remote...) must stay unknown.
- **Code (Claude):** [`9-revision.diff`](9-revision.diff), `earlybird/boards.py` only. `Toronto, CA` (and 13 other Canadian cities followed by `, CA`) is rewritten to `..., Canada` before the checks. A short list of well-known **US** cities plus `NYC` / `SF` / `SEA` counts as US. "Keep It to United States Only": no world-city list, and no NER, which would need a library and a model that a fresh clone does not have.
- **Result:** 61/61 tests pass. On the 11-01 data, 59 location strings (119 postings) changed: 118 bare US cities `None → USA`, and `Toronto, CA` `USA → None` ([`8-revision-audit.txt`](8-revision-audit.txt), every change listed). USA postings 1,678 → 1,795 of 2,683.
- **Honest limit:** on the same 190 new postings (replays `review-revision-day1/2`), **no verdict changed**: still 4 relevant on Greenhouse. The revision fixes classification for future runs; it did not change this week's shortlist.

## 7. One case the test still misses
After the revision: **lower-case short forms and region codes.** `'sf, nyc'` stays unknown because `SF`/`NYC` match only in upper case (kept that way so the English words are not caught). `'USCA'` (3 postings) and `'AMER'` (2) are also missed. Bare `'Remote'` (12) stays unknown on purpose, since a remote job may not be open to the US. None of these is in any test.

### Before the revision (patch 1), for the record
**Bare US city names with no state or country.** They stay `None` and still fail R3, for example `'Chicago'` (15 postings), `'San Francisco'` (14), `'San Francisco Bay Area'` (6), `'Seattle'` (6), `'NYC'` (4), `'NYC, SF'` (4) (counts from `5-location-audit.txt`). No test covers them, and every location string in the test's 17 cases is one the patch handles.
Also not covered: `'Toronto, CA'` is a **false positive**, and bare `'Remote'` (12) is unknown on purpose, since a remote job may not be open to the US.
