# AUDIT.md — the reject audit, judged by hand

## What was audited

FILTER.md **v1** ran on everything my JS2 agent collected: the live run of 2026-11-10, 1,014 postings from Anthropic (Greenhouse), Palantir (Lever) and Linear (Ashby). The result was **keep 46, close call 134, reject 834, cannot tell 0**. No board was missing.

**The sample.**
- 62 postings were drawn with seed `20261125`, which was fixed in FILTER.md before any label. The sample was committed (`cc1636a1`) before I saw any posting.
- No job was drawn twice: a posting whose group (same company, title and description) had already been drawn was skipped.
- The four sets:

| Set | How many | Drawn from |
|---|---:|---|
| Random rejects | 30 | postings with score 3 or less |
| Close calls | 8 | postings with score 4 |
| Kept | 8 | the grouped shortlist |
| Held out | 16 | postings with score 3–5, used only for the measurements |

**My labels.**
- I labeled **blind**: the items were shuffled and the filter's verdict was hidden. I worked from `audit/labeling-sheet.md` and the shorter `audit/quick-view.md`.
- The rule was my JS1 labeling rule, plus two decisions I made before any label (`audit/LABELING-DECISIONS.md`): "3+ years" counts as 3 or fewer, and clearance or visa *status* that the résumé does not record is "status unknown", not a fail.
- Every label and reason is in `audit/labels.csv`, and the lines I pasted are kept word for word in `audit/labels-raw.md`.

**Who decided each label:**
- **53 labels are mine.** I typed items 2, 3, 5–7, 13–16, 18 and 20 in batch 1. For items 21–62 I answered that I decided each one myself, and that the wording may have been tidied with help.
- **9 labels (1, 4, 8–12, 17, 19) were suggested by Claude Code** from my written rules, after I had marked them "Y/N not sure" or given a reason that contradicted my own clearance rule. I replied "confirm all" to every one. None of the 30 random rejects is among these nine except 8, 11 and 12. Those three are a research role in London only, an operations manager, and a "Lead" role.

## Results

| Set | Fit by my label | What it shows |
|---|---|---|
| **30 random rejects** | **0 of 30** | **My pass line (at most 1 of 30) is met.** |
| 8 close calls | **2 of 8** (items 53, 54) | the filter rejected two jobs that fit; both failed only R3, the location rule (below) |
| 8 kept | 7 of 8 | one kept job did not fit (item 32: "Must be graduating in December 2026 or Spring 2027") |
| 16 held out | 2 of 16 | used only in WHAT-MOVES-THE-SCORE.md |

## What 0 of 30 can and cannot say

- **It does not say the filter misses nothing.** 0 of 30 is a sample, not a measured rate for all 834 rejects.
- With 0 fits in 30 random rejects, the share of fits among all v1 rejects could still be as high as about **9.5%** (exact one-sided 95% bound; the rule of three gives about 10%). That is **up to about 79 of the 834 rejects**.
- The two-sided 95% interval is 0% to 11.6%.
- The other sets are smaller still. Close calls: 2 of 8 fit, 95% interval 3% to 65%. Kept: 7 of 8 fit, 47% to 99.7%. They show *that* something is wrong; they do not show *how often*.
- All of it is for one fictional candidate and one day's postings (2026-11-10). Labels are mine, by one person, and some of them depend on my two decisions above.

## A false friend

**"Platform Engineer"**, item 4: *Anthropic — IT Systems Engineer, Client Platform Engineer, ChromeOS*.
- R1 matched: `title contains "Platform Engineer"`.
- But the job is administration of a fleet of ChromeOS laptops ("*Have owned ChromeOS as a platform for a fleet of thousands of devices*", "*Google Admin console*", "*Android device management*"). It is not the software platform engineering R1 is meant to find.
- The role word matched for the wrong reason. My label is N.
- v1 rejected it anyway, because R5 found fewer than 2 of his skills. A posting that also listed two of his skills would have been kept.

Two more words matched for the wrong reason:
- **"New Grad"**, item 32. It passed R2 and supported the "early-career" claim (C2). Here, though, "new grad" means *still graduating*: "*Must be graduating in December 2026 or Spring 2027*". He finished in May 2026.
- **"SQL" and "Python"**, item 24, a cyber threat investigator. R5 found two of his skills ("*proficiency in SQL and Python for data analysis and threat detection*") in a role that is not software engineering. R1 rejected it.

## Rules added, cut or rejected after measuring

Recorded in FILTER.md as **v1.1**. Each was my decision, on Claude Code's recommendation.

| | Rule | Decision | Evidence |
|---|---|---|---|
| A | R3 accepts "**D.C.**" with dots | **added** | Items 53 and 54 (my Y) failed only R3: "Washington, D.C." did not match JS1's ", DC". 64 of the 1,014 postings have "D.C." and v1 failed all of them on R3. |
| B | R2 fails "must be graduating" in Dec 2026 or later | **added** | Item 32 (my N) was kept by v1. 3 kept v1 postings say this. |
| C | a rule against "Client Platform Engineer" | **rejected** (recorded only) | one example; a rule from one title would fit one posting |
| D | R4 counts must-have years only (M1) | **rejected** | no measurable difference on the held-out labels |
| E | keep at 4 of 5 (M2) | **rejected** | 6 wrong keeps on held-out |
| F | group by title alone | **rejected** | same-title postings differ in must-haves (clearance) |

**After v1.1, on the same labels:** item 32 is no longer kept, 53 and 54 are kept, and 55 (my N) moves from reject to close call, so it is still not kept. None of the 30 random rejects changes. A and B were found on these labels, so this agreement is in-sample, not proof. On the held-out labels, v1.1 agrees 16/16, the same as v1.

On all 1,014 postings, v1.1 gives **keep 61, close call 137, reject 816**: 46 jobs on the shortlist instead of 38.

## The limits I noticed while labeling

- **"3+ years":** my rule counts "3+ years" as fine, but Aarav has about 2.4 years. The rule is generous here.
- **Clearance and visa:** his résumé records no citizenship or work authorization. **6 of the 11** postings I labeled Y depend on clearance *eligibility* ("status unknown"): items 1, 10, 53, 54, 57 and 58. Those labels hold only if he turns out to be eligible.
- **My reason for item 17** says "*Requires 3+ years (Aarav has 29 months)*", which contradicts my own "3+ years" decision. The label N still stands on the other must-have I cited, "*1+ years as a mentor or tech lead*", which his résumé does not show.

## Every hand verdict

"v1 outcome (score)" is the filter's verdict when the sample was drawn. "v1.1" is after the changes above. Labels are Y (fit) or N.

| # | Set | Posting | v1 outcome (score) | v1.1 | My label | My reason | Who decided |
|---|---|---|---|---|---|---|---|
| 2 | reject | Palantir — Deal Team - Business Affairs | reject (1) | reject | **N** | more than 3+ years of experience (5+ years) | me |
| 5 | reject | Palantir — Forward Deployed Software Engineer, Internship - Commercial | reject (3) | reject | **N** | the location is not USA | me |
| 7 | reject | Anthropic — Manager, Product Program Management | reject (1) | reject | **N** | experience level does not match, too high | me |
| 8 | reject | Anthropic — [Expression of Interest] Research Engineer / Scientist, Alignment - London | reject (3) | reject | **N** | London, UK only; research role | Claude suggested, I confirmed |
| 11 | reject | Anthropic — Product Operations Manager, Embedded | reject (2) | reject | **N** | product operations manager: not engineering, manager role | Claude suggested, I confirmed |
| 12 | reject | Anthropic — Developer Education Lead, Claude Platform | reject (2) | reject | **N** | developer education lead: not engineering of his kind, lead role | Claude suggested, I confirmed |
| 13 | reject | Linear — Account Executive, Enterprise | reject (1) | reject | **N** | not a software engineering role | me |
| 14 | reject | Palantir — Senior Revenue Accountant | reject (2) | reject | **N** | not a software engineering role | me |
| 15 | reject | Anthropic — Engineering Manager, GPU (ML Accelerator) | reject (2) | reject | **N** | the job title is for engineering manager | me |
| 16 | reject | Palantir — People Partner | reject (2) | reject | **N** | the job title is vague, does not specify software engineering | me |
| 18 | reject | Anthropic — Partner Marketing Lead, Resellers | reject (1) | reject | **N** | not a software engineering role | me |
| 20 | reject | Linear — Product Manager | reject (0) | reject | **N** | the job title is vague, does not specify software engineering; also experience is too high | me |
| 21 | reject | Anthropic — Finance & Strategy, Deal Strategy | reject (2) | reject | **N** | Finance and Deal Strategy, not engineering. | me |
| 23 | reject | Anthropic — Research Engineer, Visual Knowledge Work | reject (2) | reject | **N** | Research engineering; requires 7+ years and ML research experience. | me |
| 25 | reject | Anthropic — Product Manager, New Markets and Monetization | reject (1) | reject | **N** | Product Manager; requires 8+ years. | me |
| 27 | reject | Palantir — Operations Analyst - US Government Security | reject (3) | reject | **N** | Operations Analyst; requires classified-environment operations experience. | me |
| 28 | reject | Anthropic — Enterprise Account Executive - DNB | reject (1) | reject | **N** | Enterprise Account Executive; sales role in South Korea. | me |
| 31 | reject | Linear — Senior / Staff Fullstack Engineer | reject (1) | reject | **N** | Senior/Staff title; requires 5+ years. | me |
| 33 | reject | Anthropic — Data Center Facility Operations Lead | reject (0) | reject | **N** | Operations Lead; outside US and requires extensive experience. | me |
| 34 | reject | Anthropic — Head of Digital Natives & Startups, ANZ | reject (0) | reject | **N** | Head-level sales leadership position. | me |
| 36 | reject | Anthropic — Staff+ Software Engineer, Experimentation | reject (2) | reject | **N** | Staff+ engineering; requires 15+ years. | me |
| 37 | reject | Palantir — Operations Analyst - US Government | reject (2) | reject | **N** | Operations Analyst; not engineering. | me |
| 39 | reject | Anthropic — Software Engineer, Beneficial Deployments | reject (3) | reject | **N** | Requires 6+ years; Aarav has 29 months. | me |
| 40 | reject | Anthropic — Anthropic Research Resident | reject (2) | reject | **N** | Research Resident; located in London. | me |
| 46 | reject | Anthropic — Partner Account Manager, Systems Integrators | reject (0) | reject | **N** | Partner Account Manager; located in Tokyo. | me |
| 47 | reject | Anthropic — Applied AI Engineer, Enterprise | reject (1) | reject | **N** | Applied AI engineering; requires 6+ years and French-market technical advisory experience. | me |
| 49 | reject | Anthropic — Strategic Account Executive, Asset & Wealth Management | reject (2) | reject | **N** | Strategic Account Executive; enterprise sales role. | me |
| 51 | reject | Anthropic — Staff Software Engineer, GTM Systems | reject (3) | reject | **N** | Staff Software Engineer; senior title and Salesforce platform experience. | me |
| 61 | reject | Anthropic — Research Scientist, Life Sciences (Computational Chemistry) | reject (3) | reject | **N** | Computational Chemistry Research Scientist; requires a Chemistry PhD. | me |
| 62 | reject | Anthropic — Research Engineer, Machine Learning (RL Velocity) | reject (3) | reject | **N** | ML Research Engineer; requires large-scale distributed training experience. | me |
| 3 | close call | Palantir — Deployment Strategist - US Government | close call (4) | close call | **N** | needs an active clearance, does not show | me |
| 4 | close call | Anthropic — IT Systems Engineer, Client Platform Engineer, ChromeOS | close call (4) | close call | **N** | must-haves (ChromeOS fleet, Google Admin console, Android device management) not on his résume | Claude suggested, I confirmed |
| 19 | close call | Palantir — Year at Palantir - Forward Deployed Software Engineer, Internship - Commercial | close call (4) | close call | **N** | internship for students; he has graduated | Claude suggested, I confirmed |
| 35 | close call | Palantir — Software Engineer, Internship - Infrastructure | close call (4) | close call | **N** | Infrastructure internship; requires 2028 graduation. | me |
| 48 | close call | Palantir — Deployment Strategist - US Government | close call (4) | close call | **N** | Deployment Strategist; requires active Top Secret clearance. | me |
| 50 | close call | Anthropic — Staff+ Software Engineer, Claude App Infrastructure | close call (4) | close call | **N** | Staff+ Software Engineer; senior-level distributed systems and low-level infrastructure requirements. | me |
| 53 | close call | Palantir — Forward Deployed Infrastructure Engineer, New Grad - US Government | close call (4) | keep | **Y** | New-grad infrastructure engineering; matching languages. Clearance eligibility accepted. Status unknown. | me |
| 54 | close call | Palantir — Forward Deployed Software Engineer, New Grad - US Government | close call (4) | keep | **Y** | New-grad forward-deployed software engineering; matching languages. Clearance eligibility accepted. Status unknown. | me |
| 1 | kept | Palantir — Software Engineer, New Grad - Production Infrastructure | keep (5) | keep | **Y** | new grad infrastructure SWE, Seattle, no years; clearance 'or eligibility and willingness to obtain' -> status unknown | Claude suggested, I confirmed |
| 10 | kept | Palantir — Forward Deployed Software Engineer - US Government - Federal Health and Civilian | keep (5) | keep | **Y** | strong coder Python/Java/TypeScript, New York, no years; clearance 'or willingness to obtain' -> status unknown | Claude suggested, I confirmed |
| 29 | kept | Palantir — Software Engineer - Frontend Developer Productivity | keep (5) | keep | **Y** | Frontend infrastructure engineering; 2+ years and TypeScript experience. | me |
| 32 | kept | Palantir — Forward Deployed Software Engineer, New Grad - Warp Speed | keep (5) | close call | **N** | Requires December 2026 or Spring 2027 graduation; Aarav graduated May 2026. | me |
| 44 | kept | Palantir — Software Engineer - Developer Productivity | keep (5) | keep | **Y** | Developer Productivity engineering; 2+ years and matching Java/TypeScript/Python skills. | me |
| 52 | kept | Palantir — Backend Software Engineer - Infrastructure | keep (5) | keep | **Y** | Backend infrastructure engineering; Java/Python match, no mandatory clearance or experience threshold. | me |
| 56 | kept | Palantir — Software Engineer, New Grad - Query Engines | keep (5) | keep | **Y** | New-grad software engineering; recently completed master's degree and Java experience. | me |
| 57 | kept | Palantir — Software Engineer, New Grad | keep (5) | keep | **Y** | New-grad software engineering; clearance eligibility accepted. Status unknown. | me |
| 6 | held out | Palantir — Software Engineer - Apollo Platform | keep (5) | keep | **Y** | — | me |
| 9 | held out | Anthropic — Technical Editor | reject (3) | reject | **N** | Technical Editor is not engineering | Claude suggested, I confirmed |
| 17 | held out | Palantir — Software Engineer - Mission Manager | close call (4) | close call | **N** | must-have 1+ years as mentor or tech lead not shown on his résume | Claude suggested, I confirmed |
| 22 | held out | Anthropic — Research Engineer / Research Scientist, Tokens | reject (3) | reject | **N** | Research Engineer/Scientist; ML research role. | me |
| 24 | held out | Anthropic — Technical Cyber Threat Investigator | close call (4) | close call | **N** | Cyber Threat Investigator; requires threat intelligence experience. | me |
| 26 | held out | Anthropic — Policy Development, Technical AI Governance | reject (3) | reject | **N** | AI Governance and Policy role, not engineering. | me |
| 30 | held out | Anthropic — Research Engineer / Scientist, Alignment | close call (4) | close call | **N** | Alignment research engineering; ML research requirements. | me |
| 38 | held out | Palantir — Talent Strategist | reject (3) | reject | **N** | Talent Strategist; recruiting role. | me |
| 41 | held out | Anthropic — Staff+ Software Engineer, Capacity Engineering | close call (4) | close call | **N** | Staff+ engineering; requires senior-level infrastructure and observability experience. | me |
| 42 | held out | Palantir — Forward Deployed Software Engineer, Internship - Commercial | close call (4) | close call | **N** | Internship; requires 2027/2028 graduation. | me |
| 43 | held out | Anthropic — Product Management, Research | reject (3) | reject | **N** | Product Management, Research; requires 5+ years. | me |
| 45 | held out | Palantir — Deployment Strategist - US Government | close call (4) | close call | **N** | Deployment Strategist; requires active Top Secret clearance. | me |
| 55 | held out | Palantir — Mixed Reality Developer | reject (3) | close call | **N** | Mixed Reality Developer; Unity/Unreal experience not demonstrated. | me |
| 58 | held out | Palantir — Software Engineer, New Grad - Defense | keep (5) | keep | **Y** | New-grad software engineering; clearance eligibility accepted. Status unknown. | me |
| 59 | held out | Anthropic — Security Engineer, Offensive Security | reject (3) | reject | **N** | Offensive Security; requires 5+ years of red-teaming experience. | me |
| 60 | held out | Anthropic — Data Scientist, Product | reject (3) | reject | **N** | Data Scientist; requires 7+ years. | me |
