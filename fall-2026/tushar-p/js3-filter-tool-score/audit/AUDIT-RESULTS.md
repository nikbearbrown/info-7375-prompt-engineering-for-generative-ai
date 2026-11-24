# JS3 reject audit — filter v0.1 vs Tushar's blind hand labels

Audit of `out/filter-v0.1/results.jsonl` (979 postings from `evidence/runs/live-text-1`: 8 keep, 951 reject, 20 cannot_tell) against the 48 rows of `audit/audit-sheet.csv`.

- **Labels were blind.** They were committed in `f97f528a` ("js3: Tushar's blind hand labels (audit 48, held-out 30)") before the filter's verdicts or the sheet key were opened.
- **The held-out sheet is still sealed.** Neither this file nor `audit/audit_v01.py` reads it or the `heldout` part of the key.
- **Every number here comes from** `python audit/audit_v01.py`. Run it from `js3-filter-tool-score/`.
- **No rule or FILTER.md text was changed.** The "what-if" counts in section f patch the filter's constants in memory for one run only.
- **Sampling** (`agent/sheets.py`, seed 7375): all 3 near-threshold postings, then 30 rejects drawn at random from all 951 (none of the 951 is near-threshold), then the remaining 5 keeps (the target was 10, but only 5 were left), then 10 of the 20 cannot_tell.

  The audit therefore covers **all 8 of the filter's keeps**.
- **No row has a note**, so section e uses no words from notes.

## a. Per-row table

| row | board | title | sample group | filter | deciding gate or score | me | note | agree |
|---|---|---|---|---|---|---|---|---|
| 1 | ashby/notion | Software Engineer, Developer Platform | keeps | keep | score 4 (topic backend, infrastructure, platform, LLM; skills TypeScript) | keep |  | agree |
| 2 | greenhouse/stripe | Engineering Manager, Self Serve Direct Onboarding | random rejects | reject | G1 fail | reject |  | agree |
| 3 | greenhouse/stripe | Machine Learning Engineer, Growth Platform | keeps | keep | score 5 (topic infrastructure, platform, LLM, machine learning; skills Python, SQL) | cannot_tell |  | **disagree** |
| 4 | greenhouse/stripe | Account Executive, UK Commercial Hunter | random rejects | reject | G1 fail | reject |  | agree |
| 5 | greenhouse/stripe | Senior Brand Designer, Link | random rejects | reject | G1 fail | reject |  | agree |
| 6 | greenhouse/stripe | Software Engineer, Vulnerability Management | near-threshold | keep | score 2 (topic infrastructure, platform; skills -) | keep |  | agree |
| 7 | greenhouse/stripe | Fraud Architect | random rejects | reject | G1 fail | reject |  | agree |
| 8 | greenhouse/stripe | Marketing Operations Manager, EMEA Events | random rejects | reject | G1 fail | reject |  | agree |
| 9 | greenhouse/stripe | Account Executive, Product - Local Payment Methods | random rejects | reject | G1 fail | reject |  | agree |
| 10 | greenhouse/stripe | Full Stack Engineer, Revenue | cannot_tell | cannot_tell | G3 unknown: N/A | reject |  | **disagree** |
| 11 | greenhouse/stripe | Renewals Specialist | random rejects | reject | G1 fail | reject |  | agree |
| 12 | greenhouse/stripe | Activations Specialist, Bridge | random rejects | reject | G1 fail | reject |  | agree |
| 13 | ashby/notion | Software Engineer, Web Infrastructure | cannot_tell | cannot_tell | G4 unknown | keep |  | **disagree** |
| 14 | ashby/notion | Software Engineer, New Grad (Dec 2026) | cannot_tell | cannot_tell | G4 unknown | keep |  | **disagree** |
| 15 | greenhouse/stripe | Account Executive, Enterprise Hunter (DACH Market) | random rejects | reject | G1 fail | reject |  | agree |
| 16 | ashby/notion | Enterprise Outcomes Architect (Customer Success) | random rejects | reject | G1 fail | cannot_tell |  | **disagree** |
| 17 | ashby/notion | GTM Recruiter, Tokyo | random rejects | reject | G1 fail | reject |  | agree |
| 18 | greenhouse/stripe | Software Engineer, Privy | cannot_tell | cannot_tell | G4 unknown | keep |  | **disagree** |
| 19 | greenhouse/stripe | Account Executive, Product Sales - Link | random rejects | reject | G1 fail | keep |  | **disagree** |
| 20 | ashby/notion | Software Engineer, Early Career (AI) | cannot_tell | cannot_tell | G4 unknown | keep |  | **disagree** |
| 21 | ashby/notion | Software Engineer, Mobile Core (Android) | cannot_tell | cannot_tell | G4 unknown | keep |  | **disagree** |
| 22 | greenhouse/stripe | Account Executive, Existing Business (Central Eastern Europe) | random rejects | reject | G1 fail | reject |  | agree |
| 23 | greenhouse/stripe | Account Executive - Enterprise, Growth | random rejects | reject | G1 fail | reject |  | agree |
| 24 | ashby/notion | Forward Deployed Architect | random rejects | reject | G1 fail | reject |  | agree |
| 25 | greenhouse/stripe | Large User Sales Managers, Platform Partnerships | random rejects | reject | G1 fail | reject |  | agree |
| 26 | greenhouse/stripe | Sales Strategy and Operations, Mergers and Acquisitions | random rejects | reject | G1 fail | reject |  | agree |
| 27 | greenhouse/stripe | Executive Advisory Programs Manager | random rejects | reject | G1 fail | reject |  | agree |
| 28 | ashby/notion | Mid-Market Solutions Consultant, San Francisco | random rejects | reject | G1 fail | reject |  | agree |
| 29 | greenhouse/stripe | Backend Engineer, Payments Experiences | random rejects | reject | G3 fail | keep |  | **disagree** |
| 30 | greenhouse/stripe | Technical Recruiter (Fixed Term Contract) | random rejects | reject | G1 fail | reject |  | agree |
| 31 | greenhouse/stripe | Backend Engineer, Developer & End-user Experience Platform | keeps | keep | score 5 (topic backend, API, infrastructure, platform; skills Docker, AWS) | reject |  | **disagree** |
| 32 | greenhouse/stripe | Machine Learning Engineer, Radar | near-threshold | keep | score 3 (topic infrastructure, platform, LLM, machine learning; skills -) | keep |  | agree |
| 33 | greenhouse/stripe | Backend Engineer, Developer & End-user Experience Platform | keeps | keep | score 5 (topic backend, API, infrastructure, platform; skills Docker, AWS) | reject |  | **disagree** |
| 34 | ashby/notion | Software Engineer, Product Infrastructure | cannot_tell | cannot_tell | G4 unknown | keep |  | **disagree** |
| 35 | greenhouse/stripe | Backend Engineer, Core Technology | keeps | keep | score 4 (topic distributed systems, infrastructure, platform, machine learning; skills Java) | reject |  | **disagree** |
| 36 | greenhouse/stripe | Full Stack Engineer, Developer & End User Experience Platform | cannot_tell | cannot_tell | G3 unknown: N/A | cannot_tell |  | agree |
| 37 | greenhouse/stripe | Account Executive, Enterprise (Grower) | random rejects | reject | G1 fail | reject |  | agree |
| 38 | greenhouse/stripe | Sales Program Manager, APAC | random rejects | reject | G1 fail | reject |  | agree |
| 39 | ashby/notion | Software Engineer, Growth (Early Career) | cannot_tell | cannot_tell | G4 unknown | keep |  | **disagree** |
| 40 | greenhouse/stripe | Software Engineer, Intern (Summer) | random rejects | reject | G2 fail: Intern | keep |  | **disagree** |
| 41 | greenhouse/stripe | Privacy Operations Program Manager | random rejects | reject | G1 fail | reject |  | agree |
| 42 | greenhouse/stripe | Full Stack Engineer, Enterprise & Ecosystem | cannot_tell | cannot_tell | G3 unknown: N/A | reject |  | **disagree** |
| 43 | greenhouse/stripe | Head of Product Sales, Payouts | random rejects | reject | G1 fail | reject |  | agree |
| 44 | greenhouse/stripe | Solutions Architect Manager, Startups & SMB | random rejects | reject | G1 fail | reject |  | agree |
| 45 | greenhouse/stripe | AI Engineer | random rejects | reject | G4 fail: 4+ years | keep |  | **disagree** |
| 46 | greenhouse/stripe | Senior Mechanical and Industrial Design Engineer | random rejects | reject | G1 fail | reject |  | agree |
| 47 | greenhouse/stripe | Customer Success Manager | random rejects | reject | G1 fail | cannot_tell |  | **disagree** |
| 48 | greenhouse/stripe | Backend Engineer, Link | near-threshold | keep | score 2 (topic backend, infrastructure; skills -) | cannot_tell |  | **disagree** |


## b. Confusion matrices

### Overall (48 rows, 28 agree)

| filter ↓ / me → | keep | reject | cannot_tell | total |
|---|---|---|---|---|
| **keep** | 3 | 3 | 2 | 8 |
| **reject** | 4 | 24 | 2 | 30 |
| **cannot_tell** | 7 | 2 | 1 | 10 |
| total | 14 | 29 | 5 | 48 |

### random rejects (30 rows, 24 agree)

| filter ↓ / me → | keep | reject | cannot_tell | total |
|---|---|---|---|---|
| **keep** | 0 | 0 | 0 | 0 |
| **reject** | 4 | 24 | 2 | 30 |
| **cannot_tell** | 0 | 0 | 0 | 0 |
| total | 4 | 24 | 2 | 30 |

### near-threshold (3 rows, 2 agree)

| filter ↓ / me → | keep | reject | cannot_tell | total |
|---|---|---|---|---|
| **keep** | 2 | 0 | 1 | 3 |
| **reject** | 0 | 0 | 0 | 0 |
| **cannot_tell** | 0 | 0 | 0 | 0 |
| total | 2 | 0 | 1 | 3 |

### keeps (5 rows, 1 agree)

| filter ↓ / me → | keep | reject | cannot_tell | total |
|---|---|---|---|---|
| **keep** | 1 | 3 | 1 | 5 |
| **reject** | 0 | 0 | 0 | 0 |
| **cannot_tell** | 0 | 0 | 0 | 0 |
| total | 1 | 3 | 1 | 5 |

### cannot_tell (10 rows, 1 agree)

| filter ↓ / me → | keep | reject | cannot_tell | total |
|---|---|---|---|---|
| **keep** | 0 | 0 | 0 | 0 |
| **reject** | 0 | 0 | 0 | 0 |
| **cannot_tell** | 7 | 2 | 1 | 10 |
| total | 7 | 2 | 1 | 10 |


Reading the matrices:
- The filter's rejects mostly hold (24/30).
- Its keeps mostly don't (3/8 agree).
- Its cannot_tell disagrees most (1/10): you call 7 of those 10 keep.

## c. Random rejects: miss estimate

Of the 30 random rejects, **you judged 6 should not be rejected** (4 keep, 2 cannot_tell).

| Count as a miss | k/n | Point | Wilson 95% interval | Same interval as postings out of 951 rejects |
|---|---|---|---|---|
| keep or cannot_tell (not reject) | 6/30 | 20.0% | 9.5% – 37.3% | about 90 – 355 |
| keep only | 4/30 | 13.3% | 5.3% – 29.7% | about 50 – 282 |

**This is an estimate from 30 randomly drawn rows. It is not a measured rate for all 951 rejects.** The interval is wide because n is 30.

Most random rejects are easy cases. 27 of the 30 failed G1 on the title (Account Executive, Recruiter, Renewals Specialist and so on). Three of those 27 still drew a non-reject label from you (rows 16, 19, 47). The other three disagreements are the only random rejects whose title named a target role: row 29 (G3), row 40 (G2) and row 45 (G4).

The estimate rests heavily on four rows (19, 29, 40 and 45; see "Labels that conflict with a persona fact" below). If any of those labels changed, the estimate would change with it. Changing a label now would be a post-unblinding correction. The blind version stays in `f97f528a`.

## d. Disagreements (20)

**Implementation problems: 0.** In every disagreement the code did what FILTER.md v0.1 says, so each one is a **rule problem** as defined here. The word or phrase is what the filter matched. The "sentence" is where it came from: the title for G1/G2, the location field for G3, and the posting text for G4 and the score.

### Random rejects you would not reject (6)

| Row | Title | Filter → you | Responsible term | Matched | Sentence it came from | Type |
|---|---|---|---|---|---|---|
| 16 | Enterprise Outcomes Architect (Customer Success) | reject → cannot_tell | G1 (no target role) | none | title: "Enterprise Outcomes Architect (Customer Success)" | rule |
| 19 | Account Executive, Product Sales - Link | reject → keep | G1 (no target role) | none | title: "Account Executive, Product Sales - Link" | rule |
| 29 | Backend Engineer, Payments Experiences | reject → keep | G3 fail (every location outside the US) | none US | location field: "Sao Paulo" | rule |
| 40 | Software Engineer, Intern (Summer) | reject → keep | G2 fail | **Intern** | title: "Software Engineer, Intern (Summer)" | rule |
| 45 | AI Engineer | reject → keep | G4 fail (largest minimum 4 > 3) | **4+ years** | "Minimum Requirements 4+ years of experience as an engineer shipping production systems" | rule |
| 47 | Customer Success Manager | reject → cannot_tell | G1 (no target role) | none | title: "Customer Success Manager" | rule |

Gates behind these rejects (the filter reports only the first failing gate; these are the others):

| Row | G1 | Other gates that also fail | Evidence for the other gates |
|---|---|---|---|
| 16 | fail | G4 | "7+ years of experience driving customer adoption, value realization, renewals, or expansion within a B2B software environment" |
| 19 | fail | G3, G4 | location "Singapore"; "Minimum requirements 7+ years of customer-facing experience at a leading technology or payments company" |
| 47 | fail | G2, G4 | G2 matched "Manager"; "Minimum requirements • 4+ years of experience in a client-facing role in Enterprise relationship management" |
| 40 | pass | G2, G3 | G3: location "Toronto" |

None of these rows would flip on a G1 change alone.

### Keeps and near-threshold you would not keep (5)

The filter kept these because G1–G5 passed and the score was ≥ 2. Your rows have no notes, so which term you object to is your call. The table shows the term that decided "pass" where a judgment was involved, which is G4 in every case. The other gates passed on clear evidence (a target title and a US city), and the score is well above 2 except on row 48.

| Row | Title | Filter → you | Responsible term | Matched | Sentence it came from | Type |
|---|---|---|---|---|---|---|
| 3 | Machine Learning Engineer, Growth Platform | keep → cannot_tell | G4 pass (largest minimum 3 ≤ 3) | **3+ years** | "Minimum requirements 3+ years of industry experience in machine learning engineering, software engineering, or applied data science, with hands-on experience building and shipping ML models in production." | rule |
| 31 | Backend Engineer, Developer & End-user Experience Platform | keep → reject | G4 pass ("N–M years" read as minimum 2) | **2–12+ years** | "Minimum requirements 2–12+ years of industry software engineering experience (does not include internships or co-ops)" | rule |
| 33 | (same title; same posting text as row 31, different locations) | keep → reject | G4 pass, as row 31 | **2–12+ years** | same sentence as row 31 | rule |
| 35 | Backend Engineer, Core Technology | keep → reject | G4 pass, minimum 2 | **2–12+ years** | "2–12+ years of professional hands-on software development experience, able to write well-factored algorithms…" | rule |
| 48 | Backend Engineer, Link | keep → cannot_tell | G4 pass, minimum 2; score exactly 2 | **2–10+ years**; topic **backend**, **infrastructure** | "Minimum requirements 2–10+ years of industry software engineering experience (does not include internships or co-ops)"; "Interest in working as a backend specialist across varying technologies and stacks…"; "You'll play a key role in expanding our product suite and the infrastructure that supports it." | rule |

**One fact behind all five.** FILTER.md's G4 fails a posting only when the largest minimum is more than **3**, because "Cole has 3 years or less". The persona file the filter reads says `years_experience` is **0**. Every posting above asks for at least 2–3 years, and the code applies the 3-year cutoff exactly as written.

Rows 31 and 33 are two postings (7476555, 7292520) with identical text. You labeled both reject.

### Cannot_tell you would decide (9)

| Row | Title | Filter → you | Responsible term | Matched | Sentence it came from | Type |
|---|---|---|---|---|---|---|
| 10 | Full Stack Engineer, Revenue | cannot_tell → reject | G3 unknown (placeholder, no country) | **N/A** | location field: "N/A" | rule |
| 42 | Full Stack Engineer, Enterprise & Ecosystem | cannot_tell → reject | G3 unknown | **N/A** | location field: "N/A" | rule |
| 13 | Software Engineer, Web Infrastructure | cannot_tell → keep | G4 unknown (no stated minimum) | none | no experience statement; the only "year" is "…$150,000 - $168,000 per year." | rule |
| 14 | Software Engineer, New Grad (Dec 2026) | cannot_tell → keep | G4 unknown | none | no years stated; "To be eligible for this role, you need to graduate in December 2026 and be able to start full time by January/February 2027." | rule |
| 18 | Software Engineer, Privy | cannot_tell → keep | G4 unknown | none | no "year" anywhere in the text | rule |
| 21 | Software Engineer, Mobile Core (Android) | cannot_tell → keep | G4 unknown | none | no experience statement ("By the end of your first year, own a core product area…"; salary "per year") | rule |
| 34 | Software Engineer, Product Infrastructure | cannot_tell → keep | G4 unknown | none | no experience statement (salary "per year" only) | rule |
| 20 | Software Engineer, Early Career (AI) | cannot_tell → keep | G4 unknown (a maximum is not a minimum) | none | "You have less than two years of engineering experience." | rule |
| 39 | Software Engineer, Growth (Early Career) | cannot_tell → keep | G4 unknown | none | "You have less than two years of engineering experience." | rule |

Notes on these rows:
- **G3 "N/A".** For a placeholder with no country, FILTER.md says unknown, and G3 returns unknown. The posting text has no other location statement; the only mention is Stripe's "consider you for different orgs based on your experience, location, etc." Row 36 is also a Stripe Full Stack Engineer posting with location "N/A". You labeled it cannot_tell, which agrees with the filter.
- **G4 unknown.** FILTER.md says unknown "if none is stated", and the code follows that. Six of these seven are Notion postings; Notion states no minimum or states a ceiling ("less than two years"). Rows 20 and 39 state a maximum that Cole meets. None of FILTER.md's four forms is a maximum, so the rule has no place for it.

### Labels that conflict with a persona fact

These four labels conflict with a constraint FILTER.md takes from the persona, not with a tuning choice. I haven't changed any of them. If one was a slip, `tools/label.py --correct ROW` keeps the old blind label in the note.

- **Row 19.** Account Executive (not a target title), Singapore (`work_country` is US), "7+ years".
- **Row 29.** Sao Paulo is outside the US, and `work_country` is US.
- **Row 40.** Intern: FILTER.md G2 rules out internships for Cole. The location is Toronto.
- **Row 45.** "Minimum Requirements 4+ years", against `years_experience` 0.

## e. False-friend candidates

These are counts of whole-word, case-insensitive matches over all 979 postings, the same way the filter matches. **These are candidates only; you choose which to name.**

**Only "platform" (and "infrastructure", added below) are v0.1 terms.** "training", "agent", "pipeline" and "model" are not used by any gate or score term in v0.1, so their matches change no v0.1 verdict today. They matter only if they are added later. "AI" is not a text term either: G1 reads "AI Engineer" from the title only.

| word | v0.1 term? | postings matched | stripe | notion | linear | audit rows | plural only |
|---|---|---|---|---|---|---|---|
| training | no | 69 | 60 | 7 | 2 | 4 | 0 |
| agent | no | 56 | 32 | 21 | 3 | 4 | 218 |
| pipeline | no | 224 | 137 | 81 | 6 | 12 | 51 |
| model | no | 255 | 158 | 94 | 3 | 15 | 176 |
| platform | topic word | 798 | 733 | 33 | 32 | 38 | 13 |
| infrastructure | topic word | 799 | 770 | 28 | 1 | 42 | 0 |
| AI | no | 453 | 251 | 170 | 32 | 27 | 0 |

"plural only" counts postings that contain the plural (agents, models and so on) but never the singular. The filter's whole-word match does not count those.

### platform (v0.1 topic word: live)
- **Stripe boilerplate, 717 postings:** "Stripe is a financial infrastructure platform for businesses." In **471** postings, this sentence or the Linear one below is the only place "platform" appears.
- **Linear boilerplate, 32 postings:** "Founded in 2019, Linear has become the platform of choice for more than 50,000 companies (including OpenAI, Coinbase, and Ramp) to plan, build, and ship their products."
- **Sales sense** (8274927, Account Executive, Amer Platform): "Software Platforms, also known as B2B Indirect, are software platform businesses who serve other businesses."

### infrastructure (v0.1 topic word; not in FILTER.md's list, added because of what the audit found)
- **Stripe boilerplate:** the same sentence gives "infrastructure" too, and in **421** postings it is the only occurrence. This one sentence therefore earns **2 topic points**, which already meets the keep threshold of 2 with no skill matched.
- **Second Stripe boilerplate, 28 postings:** "The most ambitious companies in the world use Stripe as core infrastructure to grow faster."
- **Effect on this audit.** Recomputing the 8 scored postings without the boilerplate sentences:
  - **row 6** (Software Engineer, Vulnerability Management, near-threshold keep) drops from **2 to 0**. Its keep rests entirely on the boilerplate.
  - **row 32** (Machine Learning Engineer, Radar) drops from 3 to 2.
  - The other six are unchanged.
  - You labeled row 6 keep, so the verdict agrees, but the score that produced it carries no evidence about the job.

### training (not a v0.1 term): 69 postings
- 8354772 Head of Enterprise Sales, East: "Experience training, coaching, and scaling a high-performance sales team."
- 7917880 Technical Solutions Engineer: "…regularly assembling training for non-developers internal to the organization…"
- 8172111 Training Program Manager: "…develop training initiatives that enhance the capabilities of our Operations teams, specifically Product Support and Risk Operations."

### agent (not a v0.1 term): 56 postings, plus 218 with only "agents"
Most matches are the AI sense. Wrong-sense examples:
- 8224617 Program Manager, Commercial Solutions: "…acting as a change agent across the business." The same wording appears in 8279867 and 8279850.
- 8172111 Training Program Manager: "…with a keen sense in identifying user and agent issues" (support agents).
- Notion 14879c7f Campaign Lead, Brand: "Order agent: You possess strong organizational and analytical skills…"

### pipeline (not a v0.1 term): 224 postings
- Notion f5f95c45 Enterprise Solutions Consultant (sentence repeated in 31 postings): "You'll build pipeline with BDRs, engage key stakeholders, lead discovery…"
- Notion 499cda6b Solutions Consultant, Mid Market, MEA: "Create pipeline across your book of business."
- 7370967 Pre-Sales Solutions Architect: "…support pipeline development and revenue attainment…"

### model (not a v0.1 term): 255 postings
- Notion f5f95c45 (sentence repeated in 30 postings): "Experience in a shared account ownership model, partnering with a post-sale or Customer Success team…"
- Notion 05e14247 Business Development Representative: "Notion is rebuilding its go-to-market motion around a workflow-first, builder-led model…"
- 8356912 Staff Security Engineer, Abuse Control: "Execute ACE's incubation model by defining handoff criteria, operational documentation, timelines…"

### Greenhouse AI-disclaimer boilerplate (not a v0.1 term)
**Not found as predicted.** 251 of 777 Stripe (Greenhouse) postings contain "AI", but no single disclaimer block repeats across them. The most repeated Stripe "AI" sentence appears in 19 postings: "Ability to leverage AI tools to accelerate development while applying rigorous critical thinking and professional judgement to review, refine, and validate all outputs."

The near-universal AI boilerplate is on **Notion (Ashby)**: "A NOTE ON AI … excited to use AI as a real collaborator in their work" appears in all 170 Notion postings. Because "AI" is not a v0.1 text term, none of this affects a v0.1 verdict.

## f. Known rule gaps from build step 1

"Form present" means the posting contains the gap's form. "What-if" means that one gap alone is closed, in memory, and the filter re-run.

| Gap | Form present (postings) | What-if: gate or score changes | What-if: verdict changes | Audit rows with the form | Audit verdict affected? |
|---|---|---|---|---|---|
| G2 Intern vs **Internship** | 1 | 1 (G2 would fail) | 0 | none | no |
| Topic **API vs APIs** (APIs, never API) | 156 | 0 | 0 | 1, 2, 10, 20, 40, 45 | no: row 1's topic score is already capped at 3, and the others never reach the score |
| Topic **LLM vs LLMs** (LLMs, never LLM) | 12 | 0 | 0 | 20, 35 | no: row 35 already capped, row 20 never reaches the score |
| G4 **"1 year"** | 8 | 8 (G4 unknown → pass) | 0 | 40 | no: row 40 is already rejected by G2 (and G3) |
| G4 **"two (2) years"** | 3 | 3 | 1 | none | no |

- **Internship.** The one posting, 8241260 "High School Internship, Software Engineering (Summer 2027)", already fails G1 ("Software Engineering" is not "Software Engineer").
- **"1 year".**
  - 7 of the 8 postings are Stripe Software Engineer Intern postings with "At least 1 year of university education, or equivalent work experience." That is **education, not experience**: closing this gap as stated would read it as a minimum of 1 year of experience.
  - The 8th is 8144233 Solutions Architect: "…with at least 1 year in a customer facing pre-sales role".
- **"two (2) years".**
  - 8197135 Software Engineer, High Availability and Disaster Recovery would move from **cannot_tell to reject** on "…plus five (5) years of post-bachelor's progressive software development work experience."
  - That same posting also accepts "a Master's Degree … plus three (3) years of software development work experience". G4's "largest minimum" rule would read 5 and ignore the alternative.
  - The other two are already rejected by G1: 8208521 Customer Success Manager, Enterprise ("plus four (4) years of experience in enterprise customer success…") and 8230758 User Risk Strategist ("Must also have five (5) years of experience in each of the following…").
- **Not in the build-step-1 list, but seen in this audit:** rows 20 and 39 state a *maximum* in words ("less than two years"). No G4 form covers this, and it decides 2 of the 9 cannot_tell disagreements in section d.
