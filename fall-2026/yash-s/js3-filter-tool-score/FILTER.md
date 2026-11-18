# FILTER — Job-Search Agent 3

**Version:** 1.0  
**Date:** 2026-11-18  
**Project:** Job-Search Agent 3 — The Filter, the Tool, and the Score

## 1. What I Am Building

In JS1, I built a job-board watcher for Databricks. In JS2, I extended it to collect postings from Databricks, Anthropic, and OpenAI.

For JS3, I want to decide which postings are worth reviewing and explain why each posting was kept or rejected.

I am using the fictional résumé of Priya Nair from my earlier projects. Priya is looking for early-career AI/ML Engineering and Data Engineering roles and has about eight months of professional experience.

My filter will use the posting's title, location, description, required experience, and skills.

I want the filter to be understandable and testable. A job containing several matching keywords should not automatically be considered a good match.

This is my first version. I will write the rules before implementing the filter, then test them against saved postings.

## 2. Expected Sources

I will start with the postings already collected in JS2.

| Board | ATS | Expected information |
|---|---|---|
| Databricks | Greenhouse | ID, title, location, content |
| Anthropic | Greenhouse | ID, title, location, content |
| OpenAI | Ashby | ID, title, location, description, secondary locations |

I will identify each posting using its board and posting ID so the same posting from two runs is not counted twice.

The initial JS2 data contains 2,418 unique postings across these three boards, based on my preliminary offline data check.

If a board or response is unavailable, I will report that it is unavailable. I will not treat missing data as zero postings.

If a posting has no title, location, or usable description, I will mark the missing information and explain which decision cannot be made. I will not invent missing details.

I will preserve the original source information so I can compare each shortlist claim against the posting text.

## 3. My Filter Rules — Version 1

### Rule 1: Target Role

My main target roles are:

- AI Engineer
- Machine Learning Engineer / ML Engineer
- Data Engineer
- Applied AI Engineer
- Research Engineer, when the work is clearly AI/ML-related
- Closely related AI/ML or data infrastructure engineering roles

I will match complete words or phrases rather than matching arbitrary character sequences.

**Reason:** I want the main work of the job to match Priya's engineering interests, not just contain a word such as "AI" somewhere in an unrelated title.

A Solutions Architect or Forward Deployed Engineer role will be reviewed separately if its work is clearly technical. It will not automatically qualify just because it mentions AI.

### Rule 2: Relevant Technical Topics

I will look for these topics in the job description:

- Machine learning
- Artificial intelligence
- Large language models / LLMs
- Data engineering
- Data pipelines
- Model development or deployment
- ETL and data processing
- Backend systems used for AI/ML or data workloads

**Reason:** A job's responsibilities should support the role match. A matching title alone does not prove that the work is suitable.

I will count distinct topic categories, not repeated appearances of the same word.

### Rule 3: Matching Skills

I will look for skills from Priya's fictional résumé, including:

- Python
- SQL
- AWS
- MLflow
- Delta Lake
- LangGraph
- Power BI
- Other tools explicitly listed in the fictional résumé

I will count distinct skills, not the number of times a skill appears.

**Reason:** Repeated keywords should not make a posting appear more relevant than it is.

### Rule 4: Company Boilerplate

I will not award skill points merely because a company's standard text mentions its own products.

For Databricks, I will initially exclude "Databricks" and "Unity Catalog" from the skill score because my preliminary data check found them in all Databricks postings.

I will still count MLflow and Delta Lake when they appear as genuine job requirements.

**Reason:** A company name or standard product description does not prove that a particular role requires that skill.

I will review this rule after measuring the filter's results.

### Rule 5: Seniority

I will reject postings whose titles clearly indicate seniority beyond Priya's experience, including:

- Senior / Sr.
- Staff
- Principal
- Lead
- Manager
- Director
- Head
- Vice President / VP
- Chief

I will also reject postings that explicitly require more than two years of professional experience.

**Reason:** Priya has approximately eight months of professional experience. Jobs requiring several years of experience are not suitable early-career matches.

### Rule 6: Internships and Special Programs

For this version, I will exclude internships, New Grad programs, and fellowships from the confirmed shortlist.

I will still record those postings separately so I can review whether this exclusion causes false negatives.

**Reason:** My current target is regular early-career engineering employment. Program-specific eligibility may be different and requires separate consideration.

### Rule 7: United States Location

I will keep postings with a clearly supported United States location.

This includes:

- "United States" or "USA"
- A recognized US state
- A recognized US city such as San Francisco, Seattle, Boston, or New York
- Remote roles explicitly available in the United States

I will use a documented city-to-country lookup for known city-only locations.

If a city name is ambiguous, or a remote posting does not identify eligible countries, I will mark the location as unknown instead of guessing.

**Reason:** My JS1 location rule incorrectly treated city-only Ashby locations as non-US. This could reject suitable OpenAI postings.

I will reject roles explicitly located outside the US unless the posting also clearly offers an eligible US location.

### Rule 8: Strict Experience Requirement

I am choosing a strict experience rule for Version 1.

- **Explicitly requires more than two years:** Reject.
- **Explicitly allows zero to two years, or says no professional experience is required:** Eligible for the confirmed shortlist if the other rules pass.
- **Does not state required experience:** Mark `experience_unknown` and send to a review queue.
- **Has conflicting experience requirements:** Mark `experience_unknown` and review the original posting.

A job with unstated experience will not enter the confirmed shortlist automatically.

**Reason:** Missing experience requirements do not prove that a job is suitable for Priya.

This rule may produce very few confirmed matches. I will measure that outcome instead of weakening the rule just to make the shortlist longer.

## 4. Relevance Score — Version 1

I will give each posting a score from 0 to 100.

These weights are **hand-set starting values**, not learned or fitted values.

| Component | Maximum points | Scoring rule |
|---|---:|---|
| Target role | 35 | 35 for a target engineering title, 20 for a related technical engineering title, otherwise 0 |
| Technical topics | 20 | 10 for one matching topic category, 20 for two or more |
| Matching résumé skills | 20 | 10 for one distinct matching skill, 20 for two or more |
| US location | 15 | 15 when a supported US location is present, otherwise 0 |
| Experience | 10 | 10 when the stated requirement allows Priya's experience, otherwise 0 |
| **Maximum** | **100** | |

My initial threshold is **65 points**.

I will classify postings as follows:

- **Confirmed shortlist:** Score at least 65, a target or related engineering role, supported US location, explicitly compatible experience, and no exclusion rule triggered.
- **Review queue:** Score at least 65 but an important fact, especially required experience or location, is unknown.
- **Rejected:** Score below 65, or a clear exclusion rule applies.

A high score cannot override a clear seniority, experience, or location exclusion.

I will keep the original score and the reason for the final decision.

**Why I chose 65:** This is a starting threshold to compare clear matches with borderline postings. I have not tested whether it is optimal.

I will review scores near the threshold, including postings just above and below 65.

## 5. Evidence Rules for Shortlist Claims

For every posting on the shortlist, I will break the justification into individual factual claims and compare each claim with the original posting.

I will use three labels.

### Supported

A claim is supported when the posting explicitly states it, or the claim follows directly from clearly stated information.

**Example:** The posting lists Python under required qualifications, so "The role requires Python" is supported.

### Contradicted

A claim is contradicted when the posting explicitly states something incompatible with it.

**Example:** The justification says "This is an entry-level role," but the posting requires five years of professional experience.

### Insufficient

A claim has insufficient evidence when the posting does not provide enough information to establish whether it is true.

**Example:** The justification says "Priya meets the experience requirement," but the posting does not state the required years of experience.

I will not treat insufficient evidence as supported evidence.

I will store the claim, its label, the relevant source excerpt or field, and my explanation.

## 6. When the Agent Must Abstain

The agent must say **"I cannot tell"** when the source does not support a confident answer.

Examples include:

1. The posting does not state the required years of professional experience.
2. The location is missing or ambiguous.
3. The description is missing or unusable.
4. The posting does not explain what the role actually involves.
5. The claimed qualification depends on information not present in the posting.

An abstention is not the same as rejection.

I will record abstained postings in the review queue so I can examine them separately.

**Limit of this rule:** A posting can omit experience requirements but still be intended for experienced candidates. An abstention avoids falsely confirming a match, but it does not reveal the employer's actual expectations.

## 7. Relevance Is Not the Same as Evidence

I will not treat keyword relevance as proof of a specific claim.

For example, a posting titled "Data Center Electrical Engineer" may match the word "data" but involve electrical infrastructure rather than data engineering.

Similarly, a posting mentioning Python does not automatically prove that Priya meets the job's experience requirements.

I will use these types of postings to test the difference between relevance matching and source-supported claims.

## 8. Reject Audit Plan

After implementing Version 1, I will run the filter on all unique saved postings.

I will then:

1. Draw a reproducible random sample of at least 30 rejected postings.
2. Record the random seed and the sampling method.
3. Judge each sampled posting myself using the original title, location, description, and requirements.
4. Review additional postings closest to the score threshold.
5. Review a separate sample of kept postings and review-queue postings.
6. Compare my hand judgments with the filter's decisions.
7. Record false negatives and false positives.
8. Identify at least one false-friend keyword match.
9. Decide which filter rules to add, remove, or keep based on the observed results.

I will not treat the fraction of errors in a small sample as an exact error rate for all collected postings.

I will distinguish the randomly sampled rejects from the deliberately selected borderline and kept examples.

I will also preserve the hand labels and the original Version 1 results before making changes.

## 9. Wrong Versions I Want My Tests to Catch

### Wrong Version 1: Substring Matching

A broken filter checks for keyword substrings instead of complete words.

For example, it might match "AI" inside "email."

**Expected test result:** The incorrect match must be caught.

### Wrong Version 2: Counting Boilerplate

A broken filter counts "Databricks" and "Unity Catalog" as skills in every Databricks posting.

**Expected test result:** The tests must catch incorrectly inflated scores.

### Wrong Version 3: Incorrect US Location Handling

A broken filter treats "San Francisco" or "Seattle" as outside the United States because the location does not spell out the country.

**Expected test result:** The tests must catch the incorrect classification for known US cities.

### Wrong Version 4: Missing Experience Treated as Eligible

A broken filter treats a missing experience requirement as proof that a job accepts early-career applicants.

**Expected test result:** The tests must ensure that this posting enters the review queue, not the confirmed shortlist.

I will record which wrong versions the tests actually catch after implementation.

## 10. What Moves the Score

I will document the source of every number in the scoring system.

The Version 1 weights and 65-point threshold are hand-set.

The experience cutoff of two years comes from the relevance decisions I used in JS1.

The skill list comes from Priya's fictional résumé.

I will not claim that these values were learned from training data.

After collecting my hand labels, I will create a held-out evaluation set before tuning the filter.

I will then change one object at a time and measure the effect on the held-out labels.

For example, I may change the filter document while keeping the scorer code, model prompt, context, tool list, and settings unchanged.

I will record the before-and-after results and any regressions.

A change in behavior across runs or sessions does not mean that a model was trained. It may simply mean that the prompt, context, filter, tool, or setting changed.

## 11. Version History

| Version | Date | Decision | Reason | Measurement |
|---|---|---|---|---|
| 1.0 | 2026-11-18 | Initial role, topic, skill, location, seniority, and experience rules | Establish a filter before implementation | Not tested yet |

I will add a new row whenever I change a rule.

I will record rules I considered but rejected, along with the measurements behind those decisions.

I will not rewrite Version 1 after seeing the results.

## 12. What I Will Not Claim

At this stage, I have defined the filter but have not implemented or evaluated it.

I do not yet know its precision, recall, false-negative rate, or best threshold.

I do not claim that the filter can identify every suitable job.

I do not claim that a job's missing requirements make it suitable.

I will use the reject audit, source-grounded shortlist, and held-out evaluation to determine what the filter actually does.
