# The reject audit (brief Step 2.1)

Filter v1 (FILTER.md, commit `4e62099c`) ran on everything the agent collected: run `2026-11-26T02-59-56Z`, 975 postings (Stripe 772, Notion 174, Canva 29). Result: **keep 8, reject 967, cannot tell 0** (`output/filter/filter-v1/.../summary.json`).

**Hand verdicts:** Siddi labelled 62 postings blind on 2026-11-25 (finished by 22:25 ET) in `labels/labeling-sheet.html`. The sheet was shuffled and showed no verdict, score or sample group. Its selection was committed before any label existed (`e958bc43`), and the labels were committed before any comparison (`4d633be9`). Every row with its hand verdict is in [output/audit/AUDIT-TABLES.md](output/audit/AUDIT-TABLES.md).

## What the samples show

"Wrong" below means the filter disagrees with Siddi's label.

| Sample | How drawn | Filter wrong | Exact 95% interval |
|---|---|---|---|
| Random rejects | 30 of the 967 rejects, seed 7375 | **18 of 30** (all 18 are rejects Siddi labelled relevant) | 40.6% – 77.3% |
| Close calls | every posting scoring 3 (just below the keep line) or 4 (just at it), 8 in all | 1 of 8 | 0.3% – 52.7% |
| Kept | all 8 kept postings (a sample of 8 is all there were) | 1 of 8 (Notion "Security Engineer, Detection and Response": kept, Siddi says not relevant) | 0.3% – 52.7% |

**What a sample of 30 can honestly say:**
- 18 of 30 is a sample result, not a measured rate for all 967 rejects.
- The exact interval says that, if these labels are the standard, the share of rejects Siddi would call relevant is plausibly anywhere from about 41% to about 77%. That is roughly 390 to 750 postings.
- It cannot say which ones, and it cannot rank causes.
- A sample this small would also very likely miss a problem that affects only a few percent of rejects: with 0 errors in 30, the 95% upper bound would still be 11.6%.

## Why the number is so high: two standards, not one

Siddi chose to keep the blind labels as they are (`labels/DECISION.md`): they are Siddi's judgment today, which is broader than LABELING.md. Read against the filter, the 18 disputed random rejects split like this:

| Reason the filter rejected it | Count | What it means |
|---|---|---|
| Outside the US, or the location could not be placed (Taipei, Dublin ×4, Canada, Tokyo, Mexico City, "LOCATION") | 9 | FILTER.md G4 says "anywhere in the USA", from LABELING.md answer 3. Siddi's labels today accept non-US roles. |
| US, but a title word from G1 (customer ×1, product ×2) | 3 | G1 is Siddi's JS1 exclusion list. Siddi's labels today accept these roles. |
| US, no G1 word | 6 | These are where the filter's *design* is in question. Staff SWE, High Availability (G2 "staff"); Strategy & Operations, Infrastructure (G3 years); Integration Engineer, Chicago (score 0: no role word, none of Jordan's skills and no topic word in its text); Software Engineer, Revenue and Financial Automation (G3 years); Program Manager, Card Network Office (G2, G3); Staff Program Manager (G2, G3). |

**The honest reading:** most of the disagreement (12 of 18) is between Siddi's labels today and the rules Siddi wrote earlier, not between the code and those rules. The filter does what FILTER.md says. Whether FILTER.md says what Siddi wants is the open question, and it is Siddi's.

A labeller-consistency check came for free. One posting was labelled blind twice: Stripe 7392697, "Product Manager, Link - Consumer". It was labelled not relevant on 2026-10-31 and relevant on 2026-11-25. One posting cannot give a rate, but it shows the labels themselves move.

## Problems found by measuring the whole collection, not by sampling

The random sample would very likely have missed these. They were found by counting every posting:

| Problem | How many postings | Found how |
|---|---|---|
| G4 reads bare US cities as "not US" ("Chicago", "SF, NYC", "SEA, SF, NYC, CHI") | 111 | Listing all 149 location strings that G4 placed outside the US. Fixed in **v1.1** (adopted). |
| G4 reads placeholders ("N/A" 25, "LOCATION" 7, "na" 3) as "not US", where wrong version 4 says they should be cannot tell | 35 | Same listing. Not changed. |
| The false friend "ai" (below) | 28 Notion postings | Counting where each topic word matched |

## The false friend: "ai"

"ai" is in R3's topic words so that AI work counts, and in R1's role words. It matched for the wrong reason in two ways:

1. **In the text: Notion's company blurb.** All 174 Notion postings open with a "Who we are" section containing "Notion is the collaborative AI workspace…", so all 28 Notion postings that reached scoring got R3's topic point from a sentence about the company, not the job. Example: the kept "Security Engineer, Detection and Response" matched "ai" in that blurb sentence (`output/filter/filter-v1/.../results.jsonl`, `topics`).
   - Measured fix: candidate v1.2 drops that sentence. It changed **no verdict**, on the collection or on the held-out set, because every affected kept posting had other topic words. Siddi **rejected v1.2 for now**, since the plan requires a fixed held-out error.
   - So the false friend inflated scores without crossing the keep line *on this data*. A Notion posting with exactly 3 other points would be kept because of the blurb alone.
2. **In titles: "AI" in sales roles.** 32 titles contain "AI" as a whole word, and 22 of them are stopped by a G1 word: account 7, solutions 5, marketing 4, sales 2, and 4 others. "Account Executive, AI Sales" matches the role word "ai" for the wrong reason, and only G1 stops it. Remove G1, and every "AI Sales" title gets R1's 3 points.

## Every rule added, cut or rejected after measuring

FILTER.md §E is the log. In short:
- **v1.1 added** US place names; adopted by Siddi. Held-out agreement went from 15 to 17 of 29.
- **v1.2 considered** (drop the Notion blurb); rejected for now.
- **`keep_threshold` fitted on the audit labels**: 4, the same as the hand-set value; kept.
- Three problems were **found and not changed**: G3 missing years stated without the word "experience", placeholder locations, and the evidence rule's polarity hole.
