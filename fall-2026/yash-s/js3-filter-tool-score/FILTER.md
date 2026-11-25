# FILTER — Job-Search Agent 3

**Version:** 1.2
**Date:** 2026-11-25 (Version 1.1: 2026-11-18)  
**Project:** Job-Search Agent 3 — The Filter, the Tool, and the Score

## 1. What I Am Building

In JS1, I built a job-board watcher for Databricks. In JS2, I extended it to collect postings from Databricks, Anthropic, and OpenAI.

For JS3, I want to decide which postings are worth reviewing and explain why each posting was kept or rejected.

I am using the fictional résumé of Priya Nair from my earlier projects. Priya is looking for early-career AI/ML Engineering and Data Engineering roles and has about eight months of professional experience.

My filter will use the posting's title, location, description, experience requirements, and matching skills.

I want the filter to be understandable, reproducible, and testable. A job containing several matching keywords should not automatically be considered a good match.

I committed Version 1.0 before implementation. After reviewing preliminary evidence from my JS2 postings with Claude, I am clarifying the rules in Version 1.1 before implementing the filter.

After implementing Version 1.1, auditing it by hand, and measuring candidate changes one at a time on held-out labels, I adopted one change in Version 1.2: Rule 1, Step 4 (related roles). Every other rule is unchanged from Version 1.1.

## 2. Expected Sources

I will start with the postings already collected in JS2.

| Board | ATS | Expected information |
|---|---|---|
| Databricks | Greenhouse | Posting ID, title, location, content |
| Anthropic | Greenhouse | Posting ID, title, location, content |
| OpenAI | Ashby | Posting ID, title, location, description, secondary locations |

The preliminary offline check found 2,418 unique postings across both JS2 live runs:

| Board | Unique postings |
|---|---:|
| Databricks | 916 |
| Anthropic | 677 |
| OpenAI | 825 |
| **Total** | **2,418** |

I will identify each posting using the board name and posting ID so that a posting appearing in multiple runs is counted once.

I will use the latest saved version of each posting when comparing duplicate IDs, while keeping the original source files available.

I will not assume a posting is still open just because it exists in a saved response.

### Missing sources and fields

If a board is unavailable, I will report it as unavailable rather than treating it as an empty board.

If a posting is missing its title, location, or usable description, I will record the missing field and avoid claiming anything that depends on it.

If a location is missing or ambiguous, I will mark the location as unknown.

If professional experience requirements are missing or unclear, I will mark experience as unknown.

I will preserve source references and excerpts so the justification for each posting can be checked against the original text.

## 3. My Filter Rules — Version 1.2

Only Rule 1, Step 4 changed from Version 1.1. Where Rules 2–8 below say "Version 1.1", the same rule applies unchanged in Version 1.2.

### Rule 1: Target and Related Roles

I will use complete words and phrases rather than arbitrary substring matching. Every title pattern below is matched as a whole word or phrase, ignoring case.

The filter checks each title in this fixed order. The first step that matches decides the role category. Seniority words (Rule 5) and special-program words (Rule 6) in the title are also hard exclusions, checked before scoring.

**Step 1: Excluded titles — rejected before scoring**

A title containing any of these words or phrases is rejected before scoring:

- Data Center, Data Centers, Datacenter, Datacenters
- Account Executive
- Sales
- Marketing
- Business Development
- Recruiter
- Counsel
- Legal

The filter still computes and records the score of an excluded posting for the audit, but the score cannot change the decision.

I will not use the word "data" alone to classify a Data Center role as data engineering.

Other non-engineering titles, such as policy, finance, or operations roles, do not need their own exclusion words. They match no role pattern below and are rejected in Step 5. I deliberately did not add "Policy" as an exclusion word, because it would also exclude "Applied AI Architect, International Policy."

**Step 2: Special review roles — exactly 20 role points**

A title containing any of these goes to the special review category:

- Architect (this covers Solutions Architect, Specialist Solutions Architect, Applied AI Architect, and Applied AI Security Architect)
- Forward Deployed
- FDE
- Solutions Engineer

These are the technical customer-facing roles in my saved postings. They will not enter the confirmed shortlist. If they pass every hard exclusion and score at least 65, they go to the review queue.

This step comes before the target step, so "AI Engineer – Forward Deployed Engineering (AI FDE)" is a special review role, not a target role.

**Step 3: Target engineering roles — 35 points**

A title containing any of these phrases is a target role:

- AI Engineer (this also covers Applied AI Engineer)
- Machine Learning Engineer
- ML Engineer
- Data Engineer
- Machine Learning Infrastructure Engineer
- ML Infrastructure Engineer
- Research Engineer, but only when the title also contains AI, ML, Machine Learning, LLM, Data, Reinforcement Learning, or RL

A title with an added specialization, such as "Data Engineer, Product," still matches the same target category.

**Step 4: Related technical roles — 20 points**

A title that did not match Steps 1–3 is a related role only when both conditions hold:

1. The title contains the whole word "Engineer" or "Scientist."
2. The job-specific text, after removing verified boilerplate (Rule 4), matches **at least two distinct topic categories** from Rule 2. *(Version 1.1 required one. Changed in Version 1.2; the evidence is below.)*

This rule covers the related roles I intended, for example (each still needs two topic categories):

- Software Engineer working on ML infrastructure, AI systems, data infrastructure, or data pipelines
- AI Systems Engineer
- Data Scientist or Applied Data Scientist working on machine learning or data processing
- Research Scientist working on ML or AI systems
- Performance Modeling Engineer when its responsibilities involve relevant engineering or ML systems

AI Support Engineer and Network Operations Engineer titles are not excluded by name. They count as related only when their job-specific text matches at least two Rule 2 topic categories. Otherwise they match no role.

A related role must have a specific technical responsibility match. A generic mention of AI is not enough, because standalone "AI" is not a Rule 2 topic.

**The Version 1.2 change (adopted 2026-11-25) and its evidence.** In Version 1.1, one topic phrase was enough to make an "Engineer" or "Scientist" title a related role. My reject audit found related roles kept in the review queue on a single phrase that did not describe the work:
- "model evaluation" in Data Scientist, Real Estate & Workplace (audit row 55);
- "agentic systems" in Security Engineer, Agent Security (audit row 60).

I measured "require two categories" as change X2 (`experiments/REPORT.md`):

- It changes 8 of the 2,418 saved postings, all from review to rejected. Target and special-review titles are not affected.
- Every one of the 8 has my hand label: 3 from my tuning audit and 5 from my blind held-out sample. **By my labels, 7 decisions get better and 1 gets worse.** This is a count over every saved posting the change affects, not a sample estimate. It says nothing about postings collected later.
- **The regression:** audit row 59, OpenAI `5dce6671-9aa8-4c49-b263-b175a2a927f8`, Applied Data Scientist, Personalization & Machine Learning. Its job text matches one topic category (machine learning). I labeled it "correctly in review". Version 1.2 rejects it with "no matching role". So my own example above, "Applied Data Scientist working on machine learning", is now covered only when the posting also matches a second category.

**Step 5: No matching role — rejected**

A title that matches none of Steps 1–4 gets 0 role points and is rejected with the reason "no matching role."

**Reason:** A role title should indicate the main work of the job. A fixed order of checks makes every title's category reproducible, and generic AI or data terminology does not establish that the job matches Priya's target engineering roles.

**Reason for the Version 1.2 change:** for a title that does not name a target role, one topic phrase was too weak a signal. Of the 8 saved postings kept in review on one phrase, I judged 7 should have been rejected. I accept the one known regression, and it stays listed here.

### Rule 2: Relevant Technical Topics

I will count technical topics in the posting's job-specific text: its description after removing the verified boilerplate sentences defined in Rule 4.

Phrases are matched as whole words or phrases, ignoring case.

The initial topic categories are:

| Category | Matching terms or phrases |
|---|---|
| Machine learning | machine learning, ML engineering, ML models |
| Language models | large language models, LLM, LLMs, language model inference |
| Data engineering | data engineering, data pipelines, ETL, ELT |
| Model development | model training, model evaluation, model serving, model deployment |
| AI systems | AI infrastructure, ML infrastructure, inference infrastructure |
| Data processing | distributed data processing, data ingestion, data transformation |
| AI applications | retrieval augmented generation, RAG, agentic systems, AI agents |

I will count distinct topic categories, not repeated appearances of the same phrase.

**Boilerplate handling**

The preliminary check found:

- "AI" appeared in 100% of postings on all three boards.
- "Artificial intelligence" appeared in 100% of OpenAI postings.

I will therefore not award topic points for standalone "AI" or generic "artificial intelligence."

Specific technical phrases that appear only in standard company descriptions will not count. The filter removes verified company boilerplate sentences before matching, using the reviewed list described in Rule 4.

**Reason:** A common company description should not make every posting receive topic points.

### Rule 3: Matching Skills

I will use the skills from Priya's fictional résumé rather than adding skills just because they appear in job postings.

I checked the fictional résumé (`priya-nair.resume.example.json`, the same persona file as in JS1 and JS2). It lists skills in four main groups and one familiar-only group. Only the four main groups count:

| Résumé group | Skills | Counted? |
|---|---|---|
| languages | Python, SQL | Yes |
| data_bi | Power BI | Yes |
| data_bi | Databricks, Unity Catalog | No: company product names (Rule 4) |
| backend_automation | LangGraph, MLflow, Mem0 | Yes |
| database_cloud | Delta Lake, AWS | Yes |
| familiar_with_not_shipped | Ray, Kubeflow | No: familiar only, not demonstrated |

The counted skills are **Python, SQL, AWS, MLflow, Delta Lake, LangGraph, Power BI, and Mem0**.

Skills are matched as whole words, ignoring case, in the job-specific text (after removing verified boilerplate, Rule 4).

A skill listed as merely familiar, without evidence of experience or project use, will not count as a demonstrated match.

Each distinct skill will count once.

For example, a posting mentioning Python ten times will still count as one matching skill.

**Reason:** The number of keyword repetitions does not measure Priya's actual qualifications, and a skill she lists only as familiar is not a demonstrated match.

### Rule 4: Company Boilerplate and False Friends

I will not award skill or topic points for standard company boilerplate.

**Product names.** Databricks and Unity Catalog never earn skill points, on any board. My JS1 check found both in every Databricks posting. I will continue to count MLflow and Delta Lake when they appear in job-specific text.

**Boilerplate sentences.** I will keep an explicit list of verified company boilerplate sentences for each board in a rules file (`rules/boilerplate.json`). A sentence is verified only after I have explicitly reviewed it and approved it as company boilerplate. Verified sentences are removed before topic and skill matching.

The list is built this way:

1. The code proposes candidate sentences: sentences that appear word for word, after cleaning, in at least 5% of one board's postings and contain a Rule 2 topic phrase or a Rule 3 skill. The 5% threshold only proposes candidates. Frequency alone never removes a sentence.
2. I review every candidate myself and label it **company boilerplate** or **job-specific**.
3. Only sentences I have approved as company boilerplate are removed. A candidate I have not yet reviewed, or have labeled job-specific, stays in the job-specific text and still counts. A repeated job-specific requirement stays, even when many postings share it.
4. For each sentence, the file records the board, the exact sentence, how many postings contain it, my label, and the date I reviewed and approved it.

Claude's preliminary analysis (2026-11-18) shows why repetition alone is not enough. On Databricks, 7 sentences meet the candidate rule. One is company text, found in 148 postings: "We do this by building and running the world's best data and AI infrastructure platform so our customers can use deep data insights to improve their business." The other six are repeated job requirements, such as "Comfortable writing code in either Python, Scala, JavaScript/TypeScript, and modern frameworks" (68 postings). Anthropic and OpenAI have no candidate sentences.

**Experience boilerplate.** Anthropic's standard experience sentence is handled in Rule 8.

I will also identify false-friend keywords, where a word matches but its meaning is unrelated to the target role.

Examples include:

- "Data" in Data Center Electrical Engineer
- "AI" in AI Sales Director
- "Training" when referring to employee training rather than model training

I will preserve these examples for the reject audit and shortlist evidence checks.

**Reason:** A matching word must refer to relevant responsibilities or qualifications, not just appear somewhere in the posting.

### Rule 5: Seniority

I will reject roles whose titles include any of these whole words:

- Senior / Sr. / Sr
- Staff
- Principal
- Lead
- Leader
- Manager
- Director
- Head
- Vice President / VP
- Chief

I will use whole-word matching so unrelated character sequences do not trigger these exclusions. "Leader" needs its own entry, because with whole-word matching "Lead" does not match "Leader."

**Seniority in the description.** A seniority word in a description will not automatically reject the posting.

For example, "collaborate with senior engineers" does not prove that the advertised position is senior.

The description triggers a seniority rejection only when a sentence matches one of these patterns, ignoring case, because they describe the advertised position itself:

- "As a Senior …", "As a Staff …", "As a Principal …", "As a Lead …"
- "hiring a Senior …", "seeking a Senior …", "looking for a Senior …", and the same with Staff or Principal
- "This is a Senior …", "This is a Staff …", "This is a Principal …"

Every other use of "senior" in the description is ignored. The reject audit will check whether these patterns miss senior roles.

A clear seniority exclusion overrides the numerical relevance score.

**Reason:** Priya has approximately eight months of professional experience, so clearly senior roles are outside the intended early-career target.

### Rule 6: Internships and Special Programs

For Version 1.1, I will exclude special programs from the regular-job results: the confirmed shortlist and the review queue. A title containing any of these whole words or phrases is a special program:

- Intern, Internship
- New Grad, New Graduate
- Fellow, Fellows, Fellowship
- Resident, Residency
- Apprentice, Apprenticeship
- Emerging Talent

This includes "Software Engineer, Applied Emerging Talent (2027)," which I treat as a graduate-cohort program even though its title does not say "New Grad."

Program postings are rejected with the reason "special program" and listed separately in the results, so I can review whether this exclusion causes false negatives. I will preserve these postings in the audit data rather than deleting them.

**Reason:** My current target is regular early-career engineering employment. Programs may have different graduation dates, eligibility requirements, and application rules.

### Rule 7: United States Locations

I will count clearly supported US locations.

The filter splits a posting's location into parts. Greenhouse separates parts with ";" or "|". For OpenAI on Ashby, the location and secondary locations are joined with "·". Each part is classified as US, non-US, or unknown.

**A part is US** when it:

- contains "United States", "USA", or "U.S.", which covers Anthropic's "Remote-Friendly, United States"
- is exactly "US - Remote", OpenAI's form for US remote roles
- names a US state in full, such as "Mountain View, California"
- ends with a comma and a two-letter US state or DC postal code, such as "San Francisco, CA" or "Washington, DC"
- exactly matches a city in my US city lookup

The US city lookup is an explicit list in a rules file (`rules/us_locations.json`): San Francisco, New York City, New York, Seattle, Mountain View, Bellevue, Boston, Austin, Chicago, Denver, Atlanta, Los Angeles, San Diego, Dallas, and Washington, D.C. The city-only US names in my saved OpenAI postings are San Francisco, New York City, Seattle, and Mountain View. The others come from my Version 1.0 examples.

A location such as "San Francisco" should be recognized as a US location even when the country is not written.

In my saved data, ", CA" always means California. Canada is written "Ontario, CAN" or "Ontario - Remote."

**A part is non-US** when its country is named and is not the United States (for example "London, UK", "Ontario, CAN", or "India - Remote"), or it is a bare non-US city in the same rules file, such as "Singapore" or "São Paulo."

**A part is unknown** when it is "Remote" or "Remote-Friendly" without a country, an ambiguous name such as "Ontario - Remote" or "Ontario" alone, or anything the rules above do not classify. I will not guess.

**Posting decision:**

- **US-supported** (15 points) when at least one part is US. A location containing several alternatives counts as US-supported if at least one clearly eligible US work location is stated.
- **Rejected as outside the US** only when every part is non-US.
- **Location unknown** otherwise: no location points, and the posting cannot be confirmed.

Every part the filter leaves unknown will be listed in the results. The city lookup will remain an explicit list that I can review and extend after measuring missed locations, with a Version History row for each change.

**Reason:** My JS1 filter missed city-only US locations, especially in Ashby postings. I want to correct that without guessing unknown locations.

### Rule 8: Experience Requirements

I am keeping the strict experience rule, but Version 1.1 needs to distinguish two things:

1. Whether a job passes my chosen **two-year screening cutoff**.
2. Whether Priya's actual **eight months of professional experience** satisfies the posting's stated requirement.

These are not always the same.

#### Which year counts are qualifications

The filter reads the job-specific text, with Anthropic's experience boilerplate removed (see below). It finds year counts written as "N years", "N+ years", "N or more years", "at least N years", "minimum of N years", "N–M years", "N-M years", or "N to M years", where N is written in digits or as a word from one to ten.

A year count is treated as a qualification unless:

- it describes something other than the candidate, matching one of these patterns: "over the next N years", "in the next N years", "after N years of", "for the past N years", "for the last N years", or "N years ago"
- it is a hyphenated "N-year", as in "4-year degree"
- its number is above 30

The filter does not require the word "experience." Claude's preliminary analysis (2026-11-18) found 2,070 year-count sentences across the 2,418 postings. 322 of them do not contain the word "experience," but most are still requirements, such as "6+ years in solutions architecture, technical pre-sales, or a senior hands-on technical role." Unrelated year counts it found include "After 30 years of painfully slow progress…" and "…over the next 1-2 years."

Every mandatory year requirement counts, whatever its type: total professional, engineering, role-specific, management, or sales experience.

Months, such as "6+ months," are not parsed in Version 1.1. A posting that states experience only in months is experience unknown.

#### Reading one requirement

| Wording | Minimum used |
|---|---|
| "N+ years", "N or more years", "at least N years", "minimum of N years" | N |
| "N years" | N |
| "N–M years" or "N–M+ years" | N, the lower bound |

#### Interpreting experience statements

In general: a minimum of 0 is compatible with Priya's experience; a minimum of 1 or 2 years is within the screening cutoff, but Priya does not meet it; a minimum above 2 years is rejected.

| Posting wording | Interpretation |
|---|---|
| No professional experience required | Compatible with Priya's experience |
| 0–1 years | Compatible with Priya's experience |
| 1+ years | Within the two-year screening cutoff, but Priya does not meet the stated minimum |
| 2+ years | Within the screening cutoff, but Priya does not meet the stated minimum |
| 2–8 years | Minimum is two years; Priya does not meet that minimum |
| 3+ years | Exceeds the screening cutoff; reject |
| 4–6 years | Exceeds the screening cutoff; reject |
| 5 or more years | Exceeds the screening cutoff; reject |
| No stated years | Experience unknown; review |
| Conflicting or unclear requirements | Experience unknown; review |

A statement like "2+ years" means at least two years, not zero to two years.

I will not claim that Priya meets a minimum requirement of one or two years when she has only eight months.

#### Preferred requirements

A year count is **preferred**, not mandatory, when one of these words appears before it in the same sentence (after any earlier year count in that sentence): "preferred", "preferably", "ideally", "nice to have", "nice-to-have", "bonus", or "a plus". It is also preferred when it is listed under a heading containing "Preferred", "Nice to have", or "Bonus."

For example, in "Have 8+ years of software engineering experience, ideally with 2+ years at a Staff or equivalent technical leadership level," the 8+ years is mandatory and the 2+ years is preferred.

Preferred experience will be recorded separately from required experience. It will never trigger a rejection.

#### Multiple experience requirements

Each mandatory requirement is one **unit**. A group of OR alternatives is also one unit.

**How two year counts in one sentence are connected.** The filter looks at the words between them and uses the first row that applies, checked from top to bottom:

| Words between the two year counts | Reading |
|---|---|
| "including" or "with at least" | AND: a nested requirement |
| "or", but not "and" | OR: alternatives |
| both "or" and "and" | Ambiguous: the unit is unknown |
| only "and", or none of these words | AND |

A requirement line ending in "OR," followed by a line with another year count, is also a pair of alternatives. Requirements in separate sentences are AND.

**AND.** Every mandatory unit must be satisfied.

For example:

"3+ years as a Data Engineer and 8+ years in software engineering"

Both requirements matter, so the decisive minimum is 8. I will not take only the smallest number.

**OR, when the structure is clear.** I will evaluate each alternative independently. The OR unit takes its most favorable alternative: its minimum is the smallest minimum among the alternatives. One alternative above two years does not reject the posting when another alternative is compatible.

For example:

- "3+ years as a Software Engineer OR 3+ years as a Solutions Architect": both alternatives are above two years, so the unit is above the cutoff and the posting is rejected.
- "4+ years in data engineering OR 0–1 years of software engineering experience" (a constructed example, not from my saved postings): the second alternative is compatible, so the unit is compatible.

**OR, when the structure is ambiguous.** The unit is **unknown** when:

- both "or" and "and" appear between two year counts, or
- an alternative depends on a degree or credential, such as BS, BA, MS, MA, PhD, Bachelor's, Master's, or "degree." The filter does not check degrees in Version 1.1.

For example, "BS w/ 4+ or MS with 2+ years or PhD with 0-1 year(s) of relevant industry experience" is unknown, because every alternative depends on a degree.

**Combining units.** The decisive minimum is the largest minimum across all mandatory units. The experience status is decided in this order:

1. Any unit above two years: **above cutoff**, rejected. Rejection wins, even if another unit is unknown.
2. Otherwise, any unit unknown: **unknown**.
3. Otherwise, a decisive minimum of 1 or 2 years: **within cutoff, not met**.
4. Otherwise, a decisive minimum of 0: **compatible**.

I will not assume that any number followed by "years" refers to total professional experience.

#### Boilerplate experience statements

The preliminary check found that all 677 Anthropic postings contain this standard wording:

"Years of experience required will correlate with the internal job level requirements for the position."

This does not state a numerical minimum.

I will treat it as insufficient evidence rather than as an experience requirement, and the filter removes this sentence before reading year counts.

#### Final experience decision

Each posting gets exactly one experience status:

| Status | When | Effect |
|---|---|---|
| Compatible | Every mandatory unit is clear and the decisive minimum is 0, or the posting explicitly says no professional experience is required and states no year count | 10 experience points; can be confirmed |
| Within cutoff, not met | No unit is above the cutoff or unknown, and the decisive minimum is 1 or 2 years | Review queue if the score is at least 65; never confirmed |
| Above cutoff | Any mandatory unit is above 2 years, including an OR unit whose alternatives are all above 2 years | Rejected (hard exclusion) |
| Unknown | No unit is above the cutoff, and there is no mandatory year count, experience is stated only in months, or a unit is ambiguous | Review queue if the score is at least 65; never confirmed |

A posting can enter the **confirmed shortlist** only when its required experience is explicitly compatible with Priya's eight months, or the posting explicitly says no professional experience is required.

A posting with a stated minimum of one or two years goes to the review queue if it scores at least 65, and it must clearly say that Priya does not currently meet that minimum.

A posting with an explicit mandatory minimum above two years will be rejected.

A posting with unknown required experience will not enter the confirmed shortlist.

**Reason:** I want the filter to distinguish a promising job from one whose requirements Priya actually satisfies. Missing or incomplete information should not be treated as proof of eligibility.

## 4. Relevance Score — Version 1.2 (unchanged from Version 1.1)

I will continue using a score from 0 to 100.

The weights remain hand-set starting values, not fitted values.

| Component | Maximum points | Scoring rule |
|---|---:|---|
| Target role | 35 | 35 for a target title; 20 for a related technical role or a special review role (Rule 1); otherwise 0 |
| Technical topics | 20 | 10 for one distinct job-specific topic category, 20 for two or more |
| Matching résumé skills | 20 | 10 for one distinct supported skill, 20 for two or more |
| US location | 15 | 15 for a clearly supported US location, otherwise 0 |
| Experience | 10 | 10 when the posting explicitly accepts Priya's experience, otherwise 0 |
| **Maximum** | **100** | |

My initial threshold remains **65 points**.

I will preserve the threshold initially so I can measure its performance instead of choosing a better-looking value after seeing the results.

### Decision order

Every posting is decided in this fixed order. The first step that applies decides it.

**Step 1: Hard exclusions (rejected).** The posting is rejected, with the reason recorded, if any of these applies:

1. Its title matches an excluded title pattern (Rule 1, Step 1).
2. Its title contains a seniority word, or its description contains an explicit seniority statement (Rule 5).
3. It is a special program (Rule 6).
4. Its title matches no role pattern (Rule 1, Step 5).
5. Every location part is outside the US (Rule 7).
6. Its experience status is above the cutoff: a mandatory experience unit, including an OR unit whose alternatives are all above two years, is above two years (Rule 8).

The score is still computed and recorded for these postings, but it cannot change the decision.

**Step 2: Low score (rejected).** A posting scoring below 65 is rejected, even if some of its information is unknown.

**Step 3: Review queue.** A posting scoring at least 65 goes to the review queue if any of these applies:

- It is a special review role (Rule 1, Step 2).
- Its experience is unknown (Rule 8).
- Its location is unknown (Rule 7).
- Its minimum experience is one or two years: within the screening cutoff, but above Priya's eight months.
- It matches no résumé skill in its job-specific text. A high score without a demonstrated skill never reaches the confirmed shortlist.

**Step 4: Confirmed shortlist.** A posting that reaches this step is confirmed only if it satisfies every one of these conditions:

1. Score at least 65.
2. Target or related technical engineering role.
3. At least one distinct résumé skill in the posting's job-specific text.
4. Clearly supported US location.
5. Required professional experience explicitly compatible with Priya's eight months.
6. No seniority or program exclusion.
7. Enough description evidence to justify the decision: the description is present and not empty after cleaning.

As a safety net, a posting that reaches Step 4 but still fails a condition goes to the review queue with the failed condition recorded. It is not confirmed.

A high score cannot override a hard exclusion.

### Review queue

A posting goes to review when it is potentially relevant but cannot be confirmed.

The review queue is not a confirmed shortlist.

I will record the uncertainty and which evidence would be needed to resolve it.

### Rejected

A posting is rejected in Step 1 or Step 2 above.

I will preserve the score, rejection reason, and relevant source details.

### Shortlist for the Chapter 7 evidence exercise

I will always produce two separate lists:

1. The **confirmed shortlist**: every confirmed posting. It may be empty.
2. The **high-scoring review-candidate shortlist**: the top 10 review-queue postings, ordered by descending score, then by board name (A to Z), then by posting ID compared as text. If the review queue has fewer than 10 postings, it will contain all of them. It is produced on every run, even when confirmed postings exist.

Review candidates are drawn only from the review queue, so no posting appears on both lists. The two lists will be saved, reported, and labeled separately.

I will label review candidates as unconfirmed and will not claim that Priya meets their missing or incompatible requirements.

This will let me check source-grounded justifications without inventing eligible jobs.

### Near-threshold cases

I will review postings close to 65, initially using scores from 55 to 75.

If this range produces too few examples, I will record how the selection was expanded.

I will examine both numeric scores and hard exclusions so high-scoring rejected postings are not overlooked.

**Reason for keeping this scoring system:** I want a stable starting point that I can evaluate on hand labels. The extra hard gates prevent title and topic matches from being treated as proof of eligibility.

## 5. Evidence Rules for Shortlist Claims

For every posting in the confirmed shortlist and in the review-candidate shortlist, kept as separate lists, I will break the justification into individual factual claims and compare them with the original posting.

Each claim will receive one of three labels.

### Supported

A claim is supported when the posting explicitly states it or the claim follows directly from clearly stated information.

**Example:** A posting lists Python as a required skill, so "The role requires Python" is supported.

### Contradicted

A claim is contradicted when the posting explicitly states information incompatible with it.

**Example:** The justification says "Priya meets the experience requirement," but the job requires five years of professional experience.

### Insufficient

A claim has insufficient evidence when the posting does not give enough information to establish its truth.

**Example:** A justification says "This is suitable for early-career candidates," but the posting provides no required experience level or entry-level eligibility statement.

I will not treat missing evidence as supported evidence.

For each claim, I will record:

- Posting ID and board
- Claim text
- Supported, contradicted, or insufficient label
- Supporting or contradicting source excerpt, when available
- Source field
- My explanation

A source-grounded justification must distinguish between what the posting says and what the filter infers.

## 6. When the Agent Must Abstain

The agent must say **"I cannot tell"** when the original posting does not support a confident answer.

Examples include:

1. Required professional experience is not stated.
2. Location is missing or ambiguous.
3. The description is missing or unusable.
4. The advertised responsibilities do not make the role type clear.
5. Experience requirements are contradictory or cannot be interpreted reliably.
6. A qualification claim cannot be verified against the posting text.

An abstention does not automatically mean that a job is irrelevant.

The agent will record the unresolved question and place an otherwise promising posting in the review queue.

**Counterexample exposing the limit:** A job may not state required years but may describe responsibilities intended for experienced engineers. Marking experience unknown avoids a false claim of eligibility, but it does not establish that Priya would be a suitable candidate.

## 7. Relevance Is Not the Same as Evidence

I will separate keyword relevance from factual support.

For example, a Data Center Electrical Engineer posting may match the word "data," but that does not support the claim that the work involves data pipelines or machine learning.

Similarly, a Machine Learning Engineer posting may be relevant to Priya's interests while requiring five years of experience.

The title may support topical relevance but contradict a claim that Priya currently satisfies the experience requirements.

I will use at least one actual saved posting to demonstrate this difference after implementing the filter.

## 8. Reject Audit Plan

After implementing Version 1.1, I will run the filter on all 2,418 unique saved postings, subject to verifying that the input set is complete.

I will then:

1. Save the initial filter results before making any further changes.
2. Draw a reproducible random sample of at least 30 rejected postings.
3. Record the random seed, sampling method, population size, and posting IDs.
4. Personally judge each sampled posting against the original source text.
5. Review additional postings near the score threshold.
6. Review a separate sample of confirmed matches and review-queue candidates.
7. Compare my judgments with the filter decisions.
8. Record false negatives and false positives.
9. Identify at least one false-friend keyword.
10. Record each rule I add, remove, or reject after measuring the results.

### What I will measure

I will distinguish between:

- A rejected posting I believe should have been retained for further review
- A posting incorrectly confirmed as suitable
- A posting correctly left in the review queue because important information is missing
- A posting correctly rejected because of an explicit requirement

I will not assume that a sample of 30 represents the exact error rate across all postings.

I will keep random rejects, near-threshold cases, and kept examples as separate groups in the report.

I will also preserve the original hand labels before using any of them to tune the filter.

## 9. Wrong Versions I Want My Tests to Catch

### Wrong Version 1: Substring Matching

A broken filter matches "AI" inside unrelated words such as "email."

**Expected result:** The tests catch false matches caused by arbitrary substrings.

### Wrong Version 2: Counting Boilerplate

A broken filter counts generic company descriptions, "Databricks," "Unity Catalog," or standalone "AI" as evidence of job-specific skills and topics.

**Expected result:** The tests catch incorrectly inflated scores.

### Wrong Version 3: Incorrect US Location Handling

A broken filter rejects San Francisco or Seattle because the location does not explicitly contain "United States."

**Expected result:** The tests recognize known US cities and flag genuinely ambiguous locations.

### Wrong Version 4: Missing Experience Treated as Eligible

A broken filter assumes that a posting without a stated experience requirement accepts early-career applicants.

**Expected result:** The tests ensure missing experience does not produce a confirmed match.

### Additional experience and scoring cases

I also want tests for:

- `2+ years` interpreted as a minimum of two years, not zero to two years
- `2–8 years` interpreted using the stated lower bound
- Multiple mandatory experience requirements connected by AND
- Alternative requirements connected by OR
- A preferred requirement not treated as a mandatory requirement
- Anthropic's generic experience boilerplate not treated as a numerical minimum
- A job scoring 70 through title, topics, and location but matching no demonstrated résumé skill going to the review queue, never the confirmed shortlist
- A seniority exclusion overriding a high relevance score
- "Senior engineers" in a description not automatically making the advertised role senior
- "As a Senior Field Engineer" in a description triggering the seniority exclusion
- Unknown remote locations not automatically treated as US locations
- "US - Remote" and "Remote-Friendly, United States" recognized as US, and "Ontario - Remote" marked unknown
- "Leader" in a title triggering the seniority exclusion
- An excluded title, such as "Data Center Electrical Engineer," rejected before scoring
- "AI Engineer – Forward Deployed Engineering" classified as a special review role, not a target role
- A Solutions Engineer title classified as a special review role with exactly 20 role points
- A clear OR unit with one compatible alternative and one alternative above two years not causing a rejection
- A clear OR unit whose alternatives are all above two years causing a rejection
- An OR unit with a degree alternative, or with both "or" and "and" between year counts, making experience unknown
- A compatible OR unit plus a separate mandatory 3+ year requirement still causing a rejection (every AND unit must be satisfied)
- "After 30 years of…" and "over the next 1-2 years" not read as qualifications
- A verified boilerplate sentence earning no points, while a repeated job-specific sentence, or a frequent sentence I have not approved, still counts
- "Software Engineer, Applied Emerging Talent (2027)" classified as a special program
- The review-candidate shortlist keeping the same order on every run (score, then board, then posting ID)
- The review-candidate shortlist produced even when confirmed postings exist, with no posting on both lists

### Degree-dependent OR requirement (CONSTRUCTED)

**This is a CONSTRUCTED test case, not a real posting from my JS2 data.**

A posting states: "BS with 4+ years OR MS with 2+ years OR PhD with 0–1 years."

Priya has an MS degree and approximately eight months of professional experience.

**Expected result:** The filter must not classify this posting as a confirmed match. Under Version 1.1, the parser should mark the degree-dependent experience requirement as `unknown`, and an otherwise relevant posting scoring at least 65 should enter the review queue.

### Version 1.2 related-role rule (CONSTRUCTED)

**These are CONSTRUCTED test cases, not real postings.** They live in `tests/test_versions.py`:

- A "Software Engineer" title whose job text matches one topic category is no role, and is rejected, in Version 1.2. The same posting is a related role in Version 1.1.
- With two topic categories, it is a related role.
- A target title such as "Data Engineer" is not affected.
- Version 1.2 differs from Version 1.1 in exactly one rule value. The Version 1.1 rules files are kept byte for byte.
- The rejected and unadopted changes were not applied: the threshold is still 65, and "may also have" is not a preferred heading.

I will record which wrong versions the tests actually catch after implementation.

## 10. What Moves the Score

I will document where the numbers and scoring rules came from.

| Item | Origin |
|---|---|
| Role weight: 35 | Hand-set |
| Technical topic weight: 20 | Hand-set |
| Matching skill weight: 20 | Hand-set |
| US location weight: 15 | Hand-set |
| Experience weight: 10 | Hand-set |
| Threshold: 65 | Hand-set. 55 was tested as change X1 and not adopted (inconclusive on held-out labels, and a larger review queue) |
| Topic categories a related title needs: 2 (Version 1.2; 1 in Version 1.1) | Hand-set rule, changed after measuring: chosen from my tuning audit, checked on my held-out labels (change X2). Not fitted by any algorithm |
| Near-threshold review range: 55–75 | Hand-set |
| Two-year screening cutoff | Inherited from JS1 relevance decisions |
| Priya's eight months of experience | Fictional résumé |
| Skill vocabulary | Fictional résumé: the four main skill groups |
| Databricks and Unity Catalog exclusion | Measured in JS1: present in every Databricks posting |
| Boilerplate candidate rule: a sentence in at least 5% of one board's postings | Hand-set; it only proposes candidates for my review |
| Boilerplate sentence list | Candidates measured by the code; each removed only after my explicit approval |
| Title patterns (excluded, special review, target, related) | Hand-set, informed by Claude's preliminary analysis of 139 postings |
| Unrelated year-count patterns | Taken from examples in Claude's preliminary analysis |
| US city lookup | My saved OpenAI locations plus my Version 1.0 examples |
| Review-candidate shortlist size: 10 | Hand-set |

I will not claim that any of these values were learned from training data.

### One-change-at-a-time evaluation

Before changing the filter after implementation, I will collect my own labels and reserve a held-out set for evaluation.

I will not use held-out labels to select the best threshold or tune rules.

I will compare an unchanged baseline with an experiment where only one object changes.

Possible objects include:

- Filter rules
- Claude prompt
- Context given to Claude
- Available tool list
- Model or runtime setting

I will record the exact changed object, the unchanged settings, the label set, the results before and after, and any regressions.

If I use a revised filter version, I will preserve the previous version and explain the reason for the change.

A change in behavior across sessions does not prove that the model was trained. The change may come from a different prompt, tool, context, filter, or setting.

## 11. Version History

| Version | Date | Change | Reason and evidence |
|---|---|---|---|
| 1.0 | 2026-11-18 | Initial filter, evidence rules, scoring, and wrong versions | Written and committed before implementation |
| 1.1 | 2026-11-18 | Removed standalone AI and generic artificial intelligence as scoring topics | Claude's preliminary analysis found "AI" in 100% of postings across all three boards and "artificial intelligence" in 100% of OpenAI postings |
| 1.1 | 2026-11-18 | Defined exact excluded, special-review, target, and related title patterns, checked in a fixed order; special-review roles, including Solutions Engineer, get exactly 20 role points; excluded titles are rejected before scoring | Claude's preliminary analysis of 139 US, non-senior postings with a topic word in the title found 40 target-like titles, 30 architect or forward-deployed titles, and 16 Data Center titles sharing similar keywords. Across all postings, 17 titles contain "Solutions Engineer." "Policy" was not made an exclusion word because it would also exclude "Applied AI Architect, International Policy" |
| 1.1 | 2026-11-18 | Added "Leader" to the seniority words | With whole-word matching, "Lead" does not match "Leader." Claude's preliminary analysis found 11 titles containing "Leader," such as "AI Transformation Leader" |
| 1.1 | 2026-11-18 | Defined explicit description patterns for seniority | "Collaborate with senior engineers" describes other people, while "As a Senior Field Engineer…" describes the advertised role (an example from Claude's preliminary analysis) |
| 1.1 | 2026-11-18 | Counted Priya's four main skill groups (Python, SQL, AWS, MLflow, Delta Lake, LangGraph, Power BI, Mem0); excluded Databricks, Unity Catalog, Ray, and Kubeflow | Claude's check of the résumé found Mem0 missing from my list, and found that my earlier "experience or projects only" wording would have excluded Python, AWS, Delta Lake, and Power BI, which appear only in the skills list |
| 1.1 | 2026-11-18 | Added a reviewed per-board list of boilerplate sentences. The 5% repeated-sentence threshold only proposes candidates; a sentence is removed only after my explicit approval | Claude's preliminary analysis found "AI infrastructure" in 240 Databricks postings, 148 of them from one company sentence. Six other repeated Databricks sentences are job requirements, so repetition alone does not prove boilerplate |
| 1.1 | 2026-11-18 | Made experience parsing deterministic: N+, ranges, AND (every mandatory unit must be satisfied; the largest minimum decides), OR (each alternative evaluated independently when the structure is clear; unknown when ambiguous or when an alternative depends on a degree), preferred requirements, unrelated year counts, and months | Claude's preliminary analysis: of the 139 postings, 54 had no numerical year requirement, 73 had one, and 12 had several. Across all postings, 322 of 2,070 year-count sentences lacked the word "experience" but were mostly real requirements, and some year counts were unrelated, such as "After 30 years of painfully slow progress." It also found degree-based alternatives, such as "BS w/ 4+ or MS with 2+ years or PhD with 0-1 year(s)" |
| 1.1 | 2026-11-18 | Distinguished the two-year screening cutoff from Priya's eight months | A posting requiring 2+ years passes the numerical screening cutoff but does not mean Priya meets the minimum |
| 1.1 | 2026-11-18 | Added handling for Anthropic's experience boilerplate | Claude's preliminary analysis found the generic experience statement in 677 of 677 Anthropic postings |
| 1.1 | 2026-11-18 | Fixed the decision order: hard exclusions, then a score below 65, then review, then confirmation | The earlier 1.1 draft required at least 65 for review but rejected low scores only when nothing was unknown. Claude's preliminary analysis found 741 of 2,418 postings with no year count, so low-scoring postings could have flooded the review queue |
| 1.1 | 2026-11-18 | Defined city-aware US locations, "US - Remote", "Remote-Friendly, United States", and unknown "Remote" and "Ontario" locations | The JS1 location rule missed city-only US locations in Ashby (502 OpenAI postings). Claude's preliminary analysis found 31 distinct OpenAI location values, "US - Remote" in 42 OpenAI postings, Canada written as "Ontario, CAN" or "Ontario - Remote," and ", CA" always meaning California in the saved data |
| 1.1 | 2026-11-18 | Added a demonstrated-skill requirement to confirmed matches; a posting scoring at least 65 without a matching skill goes to the review queue | The original score allowed title, topics, and US location to reach 70 without any matching résumé skills |
| 1.1 | 2026-11-18 | Defined the review-candidate shortlist as the top 10 review-queue postings, ordered by score, board, and posting ID, produced on every run and kept separate from the confirmed shortlist | The strict experience rule may produce no confirmed matches. In Claude's preliminary analysis, none of the 40 target-like titles stated two years or less |
| 1.1 | 2026-11-18 | Treated "Software Engineer, Applied Emerging Talent (2027)" as a special program | Found by Claude's preliminary analysis outside the 139-posting group. It states "0-1 years of experience" but is a graduate-cohort program |
| 1.1 | 2026-11-18 | Named Performance Modeling Engineer as a possible related role | Found by Claude's preliminary analysis outside the 139-posting group: "ideal for early-career engineers with 1–2 years of experience." Its title has no topic word |
| 1.1 | 2026-11-18 | Expanded planned tests for experience and scoring edge cases | Preliminary posting analysis exposed cases not covered by the original four wrong versions |
| 1.2 | 2026-11-25 | Rule 1, Step 4: a related title needs at least two distinct Rule 2 topic categories, not one | Change X2 (`experiments/REPORT.md`). It changes 8 of 2,418 saved postings, all from review to rejected. All 8 carry my hand label: 7 better, 1 worse. The regression is audit row 59, Applied Data Scientist, Personalization & Machine Learning. On my blind held-out labels alone: 5 better, 0 worse. The measurements were committed (`f88d1922`) before my decision (`experiments/RULE-CHANGE-LOG.md`) |
| 1.2 | 2026-11-25 | Not adopted: X1 (threshold 55) and X3 ("may also have" treated as a preferred heading) | X1 was inconclusive: 9 of 15 held-out flips improved (95% Wilson 36%–80%), and the review queue would grow from 63 to 107. X3 changes no decision on the saved postings, so I claim no improvement; I keep it as a possible parsing improvement |

The Version 1.0 content remains preserved in Git commit `f50b5001`. The Version 1.1 content remains preserved in Git commit `9d78317d`, and its rules files are kept byte for byte in `rules/v1.1/`. The Version 1.2 wording was edited by Claude Code from my decisions in `experiments/RULE-CHANGE-LOG.md`.

The measurements in the Version 1.1 rows come from Claude's preliminary, read-only analysis of my saved JS2 postings on 2026-11-18. They are not results of the JS3 filter. The Version 1.2 rows are results of the JS3 filter, measured on my hand labels. The final Version 1.1 wording was edited by Claude Code from decisions I approved.

I will record further rules that I add, cut, or reject after measuring the filter.

The Version 1.1 changes are based on preliminary observations. They do not establish that the filter has improved until it is implemented and evaluated.

## 12. What I Will Not Claim

**Version 1.2 (2026-11-25):**
- I do not claim that Version 1.2 is better on postings collected after 2026-11-10, or on any posting nobody labeled. The X2 result is a count of my own judgments over the 8 saved postings it changes.
- Version 1.2 has one known regression (audit row 59).
- The reject audit, the shortlist and the tool server in this folder were made with Version 1.1. The Version 1.2 run is in `runs/` under a `filter-v1.2-` folder name.
- I still do not know the filter's precision or recall.

**Written for Version 1.1 on 2026-11-18, before implementation:**

At this stage, I have written and revised the filter rules but have not implemented or evaluated the JS3 filter.

The preliminary group of 139 postings was selected using simple title, seniority, program, and location checks. It was not a random sample and does not establish the filter's accuracy.

I do not yet know the precision, recall, false-negative rate, or best score threshold.

I do not claim that any candidate with unknown experience is eligible.

I do not claim that a high relevance score means Priya meets every requirement.

I do not claim that the saved postings are still available today.

I will use the full filter run, hand-labeled reject audit, source-grounded shortlist, and held-out evaluation to determine what the system actually does.