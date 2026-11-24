# Reject audit — AI-drafted assessments (pending review)

**Status: AI draft, not hand verdicts.** Claude proposed every verdict and explanation below on 2026-11-24 for Sreevarshan to review. They are not independent hand-written judgments. The final verdicts belong in the "My verdict" column of `output/audit_sheet.md`, which this draft does not touch.

**Candidate:** Priya Nair (fictional persona, Reallocation Engine `search/examples/priya-nair/`). She finished an MS in Information Systems at Northeastern (Dec 2025), has one 8-month AI Engineer co-op (Databricks Genie, LangGraph, MLflow), and is on F-1 OPT year 1, Boston-based, open to remote. Target: AI Engineer / ML Engineer, then Data Engineer. Needs sponsorship.

**Evidence used:** the posting's title, location, and Greenhouse metadata (company entity, posting category) from the JS2 raw files, matched by posting ID. All 40 sampled postings are Greenhouse (Databricks 23, Stripe 17). **None has description text**, so no qualifications, skills, or years of experience could be checked. Where a verdict leans on location, the reason is that OPT work must be done in the US.

**Not used:** the hand-verdict CSVs in `files.zip`. Their labeling rule judges against a different persona (Ananya Rao), and reading them first would have anchored this draft.

| # | Board | Posting ID | Title | Filter reason | AI draft verdict | Explanation | Needs my review |
|---|---|---|---|---|---|---|---|
| 1 | stripe | 8175820 | Operations Team Lead (Night Shift) | no_match | correct | An operations team-lead role based in Bengaluru. It is not engineering and not in the US. | No |
| 2 | databricks | 8517065002 | Manager, Field Engineering France - Specialist Solutions Architects | hard_reject | correct | A people-manager role over solutions architects, based in Paris. Both the level and the location rule it out. | No |
| 3 | databricks | 8735569002 | Delivery Solutions Architect - Communications, Media, Entertainment & Games | no_match | correct | A customer-delivery architect role in the Field Engineering category, aimed at media clients, not an ML or data engineering job. It is US-based, but the title is outside Priya's target roles. | No |
| 4 | stripe | 8130930 | Software Engineer, New Grad | no_match | correct | The level fits, but the job is in London, and Priya's OPT work has to be in the US. The filter got the right answer for a different reason (no topic word). | No |
| 5 | databricks | 8739458002 | Sr. Forward Deployed Engineer | no_match | correct | The title says "Sr.", which points above a new-grad level with one co-op. With no description it is unclear how much of the job is hands-on AI work, so the Forward Deployed role family is worth a look. | Yes |
| 6 | databricks | 8921587002 | Solutions Architect Spain | no_match | correct | A pre-sales architect role based in Madrid. It is neither an engineering target role nor in the US. | No |
| 7 | databricks | 8755492002 | Solutions Architect - Communications, Media, Entertainment and Games | no_match | correct | A Field Engineering pre-sales architect role for media clients in New Jersey. The title is not an ML or data engineering role. | No |
| 8 | databricks | 8145800002 | Product Manager, New Grad (2027) - Berlin | hard_reject | correct | A new-grad product-management role in Berlin. The function is not engineering and the job is outside the US. | No |
| 9 | stripe | 8128745 | Software Engineer, Intern (Summer or Winter) | no_match | correct | An internship, while Priya has finished her degree and is looking for full-time work. Check whether this matters for her OPT plan, since the posting text was not saved. | Yes |
| 10 | databricks | 8892968002 | Lead Solutions Architect - Generative AI (EMEA Emerging DNB) | no_match | correct | Despite "Generative AI" in the title, this is a lead-level pre-sales architect role for the EMEA region, listed as Remote - Sweden. | No |
| 11 | stripe | 7961101 | Product Marketing Manager, Radar | hard_reject | correct | A product-marketing role. It is not engineering. | No |
| 12 | stripe | 8128744 | Software Engineer, New Grad | no_match | needs review | A new-grad role in San Francisco, Seattle, or New York, so the level and location both fit. It was rejected only because no description was saved to show ML or data work; the title alone does not say whether it is general software work or something closer to Priya's targets. | Yes |
| 13 | stripe | 8209626 | EMEA Demand Generation, Platforms | no_match | correct | A marketing demand-generation role based in London. | No |
| 14 | databricks | 8571578002 | Lakebase Associate Director- Financial Services | hard_reject | correct | A director-level role in the Sales category. Wrong function and level. | No |
| 15 | stripe | 8128634 | Head of AEO & SEO | hard_reject | correct | A senior marketing leadership role for search optimization. | No |
| 16 | databricks | 8871482002 | Strategic Account Executive, Space Force | hard_reject | correct | A sales account role in the Sales category under Databricks Federal, LLC. | No |
| 17 | databricks | 8549248002 | Delivery Solutions Architect - Startups & Emerging Enterprise | no_match | correct | A customer-delivery architect role in Field Engineering. It is listed as remote in several states including Massachusetts, but the title is not an ML or data engineering role. | No |
| 18 | databricks | 8899461002 | Delivery Solutions Architect - Public Sector (DOJ) | no_match | correct | A customer-delivery architect role for a Department of Justice account under Databricks Federal, LLC. The title is outside the target roles; the saved data does not say whether clearance is needed. | No |
| 19 | databricks | 8569594002 | Lakebase Sales Specialist | no_match | correct | A sales role based in Singapore. | No |
| 20 | databricks | 8437008002 | Solutions Architect | no_match | correct | A pre-sales architect role based in Queensland, Australia. | No |
| 21 | databricks | 8771056002 | Solutions Architect - Financial Services & Insurance | no_match | correct | A pre-sales architect role based in Toronto, Canada. | No |
| 22 | stripe | 8304841 | Account Executive, Velocity Platforms (Hunter) | hard_reject | correct | A sales account role in San Francisco. | No |
| 23 | stripe | 8167558 | Incident Response Manager | hard_reject | correct | A manager-titled incident-response role based in Dublin. Wrong function and location. | No |
| 24 | databricks | 8548986002 | Delivery Solutions Architect - Digital Native Business | no_match | correct | A customer-delivery architect role in Field Engineering, remote on the West Coast. The title is not an ML or data engineering role. | No |
| 25 | stripe | 8319491 | Enterprise Account Executive, UK Financial Services, Banking | hard_reject | correct | An enterprise sales role in London. | No |
| 26 | databricks | 8433583002 | Senior Staff Software Engineer- Networking | no_match | correct | A senior staff networking role in Bengaluru, far above new-grad level and outside the US. | No |
| 27 | stripe | 7776179 | Security Engineer, Bridge | no_match | correct | A security engineering role. Security is not one of Priya's target areas. | No |
| 28 | stripe | 8261213 | Payments Fraud Investigator | no_match | correct | A fraud-investigation role. It is not engineering, even though it is remote in the US. | No |
| 29 | stripe | 8248086 | Sales Development Representative (Spanish fluency) | no_match | correct | An entry-level sales role in Chicago that asks for Spanish fluency. | No |
| 30 | databricks | 8929792002 | Strategic Account Executive - Energy | hard_reject | correct | A sales account role in London. | No |
| 31 | databricks | 7274563002 | Senior Staff Software Engineer - IAM | no_match | correct | A senior staff identity and access management role, far above new-grad level. | No |
| 32 | databricks | 8367019002 | Staff Backend Software Engineer- (Databricks AI) | no_match | correct | The title mentions AI, but this is a Staff-level backend role, well above someone with one co-op. | No |
| 33 | databricks | 8509534002 | Staff Software Engineer, Fullstack - AI Product (NYC) | no_match | correct | A Staff-level full-stack role on an AI product. Despite the AI wording, both the level and the full-stack focus are off-target. | No |
| 34 | databricks | 6866534002 | Software Engineering Intern (2027 Start) - Amsterdam | no_match | correct | An internship based in Amsterdam. Wrong level for a graduate, and outside the US. | No |
| 35 | stripe | 8130876 | Software Engineer, New Grad | no_match | correct | The level fits, but the job is in Bangalore, outside the US. | No |
| 36 | stripe | 8175656 | Software Engineer, Security Business Enablement | no_match | correct | A security-focused engineering role in Dublin. Off-target area and outside the US. | No |
| 37 | databricks | 8931033002 | Senior Software Engineer - Access Management | no_match | correct | A senior access-management role in Bellevue. The level is above new grad and the area is security, not ML or data. | No |
| 38 | stripe | 8332676 | Software Engineer - Full stack | no_match | needs review | A Seattle role with no level in the title. "Full stack" suggests product web work rather than ML or data, but with no description the level and the actual work can't be checked. | Yes |
| 39 | stripe | 8202299 | Software Engineer, New Grad | no_match | correct | The level fits, but the job is in Taiwan, outside the US. | No |
| 40 | databricks | 8720252002 | Senior Solutions Architect (EDW Enterprise Data Warehouse Migrations) | no_match | correct | It reached the closest-call list only because "data warehouse" is in the title. It is a senior pre-sales migration architect role based in Amsterdam. | No |

## Summary (AI-drafted, pending review)

- **Total postings reviewed:** 40 (30 random rejects, rows 1–30; 10 closest calls, rows 31–40). Order and IDs are unchanged from `audit_sample.json`.
- **Provisionally correct:** 38. Two of these (rows 5 and 9) are flagged for a quick check.
- **Provisionally false reject:** 0.
- **Needs further review:** 2 (rows 12 and 38).
- **Flagged "Needs my review: Yes" in total:** 4 (rows 5, 9, 12, 38).

**By filter reason:** all 10 hard rejects look correct. Each title is plainly a manager, director, head, account-executive, or marketing role. Of the 30 `no_match` rejects, 28 look correct, mostly because the title names a sales, architect, or security role, a senior or staff level, or a job outside the US.

### Which rules caused possible false rejections

- **The software-engineer pairing rule on Greenhouse postings with no description** (FILTER.md sections 2, 3 and 9). This is the only rule behind the two open cases (rows 12 and 38). Both were rejected only because no description was saved to supply a topic word. The rule can't separate a general software role from an ML or data one, because the evidence it needs was never fetched.
- **No hard-reject word caused a possible false reject in this sample.**

### Candidate false friends (posting evidence)

- **Row 40, databricks 8720252002**, "Senior Solutions Architect (EDW Enterprise Data Warehouse Migrations)". The topic word "data warehouse" in the title put it among the closest calls. The role is a senior pre-sales architect role based in Amsterdam (Field Engineering category).
- **Row 10, databricks 8892968002**, "Lead Solutions Architect - Generative AI (EMEA Emerging DNB)". "Generative AI" sounds on-target, but the job is a lead pre-sales architect role, listed as Remote - Sweden.
- **Row 32, databricks 8367019002**, "Staff Backend Software Engineer- (Databricks AI)". The AI wording sounds on-target, but the role is Staff level.

### Limitations from missing descriptions

- None of the 40 postings has description text, because the Greenhouse fetch did not request it. No verdict here is based on stated qualifications, skills, years of experience, sponsorship policy, or clearance requirements. They rest only on title, location, and metadata.
- The level was judged from title words (New Grad, Intern, Sr., Senior, Staff, Lead). A title with no level word, like row 38, can't be placed.
- Sponsorship and clearance can't be checked for any posting. That matters for Priya, who needs sponsorship and excludes clearance roles (for example, row 18 under Databricks Federal, LLC).
- 19 of the 38 "correct" explanations cite a location outside the US. For 3 of them (rows 4, 35, 39, all new-grad software roles) location is the only reason. That assumes every listed location is a hard requirement, which the posting text might soften.

### Outside the sample (observation, not a verdict)

While checking the AI Engineer and Forward Deployed questions, a scan of all 1732 rejects in `filter_results.json` showed that **FILTER.md's role words don't include "AI Engineer"**, which is Priya's primary target. Eight rejected titles contain it. Examples: Stripe "AI Engineer" and Databricks "Applied AI Engineer", both rejected as `no_match`. Another 103 rejected titles contain "Forward Deployed", many as "AI Forward Deployed Engineer". None of these was drawn into the 40, so this audit can't estimate how much the gap costs. It is a candidate rule change for review, separate from these verdicts.
