# FILTER.md
## Job-Search Agent 3: Posting Relevance Filter

**Version:** 1.0  
**Status:** Pre-build specification  
**Candidate:** Alex Morgan  
**Date:** November 19, 2026

---

## 1. Purpose and Starting Point

This document defines the rules used by Job-Search Agent 3 to determine whether a collected job posting is relevant to Alex Morgan.

The objective is to identify software engineering opportunities that align with Alex's professional experience, technical skills, target job titles, and preferred US locations.

The filter uses a weighted scoring system with a defined threshold. It evaluates job titles, technical keywords, and locations while maintaining separate rules for mandatory rejection and insufficient information.

### Starting point

This project builds on my Job-Search Agent 2 (copied unchanged at commit `8f821de4`): a bounded loop that collects Greenhouse, Lever, and Ashby postings.

JS1/JS2 had a pass/fail rule based on title, three skill matches, and location. Version 1.0 replaces that binary approach with a weighted, documented scoring system that makes individual decisions measurable and auditable.

### Candidate profile

The following information comes from `data/persona_alex.json`.

| Attribute | Profile |
|---|---|
| Name | Alex Morgan |
| Professional experience | June 2023 – August 2026 |
| Primary role | Backend Software Engineer |
| Target titles | Software Engineer, Backend Engineer, Backend Software Developer |
| Programming languages | Java, Python |
| Frameworks | Spring Boot |
| APIs | REST APIs |
| Databases | PostgreSQL, Redis |
| Messaging | Apache Kafka |
| Infrastructure | Docker, Kubernetes |
| Cloud | AWS |
| Development practices | Git, CI/CD |
| Target locations | Mountain View, CA; San Francisco, CA; Remote |

---

## 2. The Filter: Scoring Rules

### 2.1 Scoring overview

Each posting receives points from three dimensions:

1. Job title relevance.
2. Technical skill relevance.
3. Location relevance.

| Dimension | Maximum points |
|---|---:|
| Job title | 4 |
| Technical skills | 8 |
| Location | 2 |
| **Total** | **14** |

**Minimum relevance threshold: 8 points.**

A posting must also satisfy the mandatory role and location conditions to qualify for the shortlist.

### 2.2 Role words in the title

| Title match | Points |
|---|---:|
| Software Engineer | +4 |
| Backend Engineer | +4 |
| Backend Software Developer | +4 |
| Other technical engineering titles | 0 |

**Reasoning:** Alex has three years of professional software engineering experience, primarily developing backend applications and services. These three titles directly reflect his target positions.

Rules:

- Matching is case-insensitive.
- Match complete words or phrases, not arbitrary substrings.
- A title receives points only once.
- The role score is capped at 4.
- Senior or Lead prefixes do not automatically disqualify an otherwise matching title. They are flagged for additional review.

Examples:

| Posting title | Result |
|---|---|
| Software Engineer | +4 |
| Backend Engineer II | +4 |
| Senior Software Engineer | +4, review flag |
| Lead Backend Engineer | +4, review flag |
| Engineering Manager | 0 |
| Data Analyst | 0 |

### 2.3 Technical keywords in the description

Technical skills are organized into eight categories. Each distinct category contributes one point.

| Category | Matching keywords | Points |
|---|---|---:|
| Programming | Java, Python | +1 |
| Frameworks | Spring Boot | +1 |
| APIs | REST APIs | +1 |
| Databases | PostgreSQL, Redis | +1 |
| Messaging | Apache Kafka, Kafka | +1 |
| Containers | Docker, Kubernetes | +1 |
| Cloud | AWS, Amazon Web Services | +1 |
| Development workflow | Git, CI/CD, Continuous Integration, Continuous Delivery | +1 |

**Maximum technical score: 8 points.**

**Reasoning:** These categories represent technologies Alex has used professionally at Northstar Systems and Cedar Labs. Grouping related technologies prevents multiple mentions of the same skill category from artificially increasing a posting's score.

Rules:

- Each category contributes at most one point.
- Multiple keywords within the same category count only once.
- Repeated occurrences do not increase the score.
- Matching is case-insensitive.
- Complete words or phrases are required.
- At least one technical category must match for a posting to qualify.
- Generic terms such as Spring, Platform, and Cloud are not sufficient on their own to establish a technical match.

### 2.4 Location relevance

| Location | Points |
|---|---:|
| Mountain View, CA | +2 |
| San Francisco, CA | +2 |
| San Francisco Bay Area | +2 |
| Remote, explicitly open to US applicants | +2 |
| Other US locations | 0 |
| Explicitly non-US-only positions | REJECT |
| Remote with no identifiable geographic eligibility | UNKNOWN |

**Reasoning:** Alex targets Mountain View and San Francisco but is also open to other US locations and remote opportunities.

Location interpretation:

- `Mountain View, CA` and `San Francisco, CA` receive +2.
- `SF` counts as San Francisco only when it appears as its own word in the location field (for example `SF` or `SF, CA`), never inside another word.
- `San Francisco Bay Area` receives +2 because it includes Alex's target locations.
- `Remote - US`, `Remote (US)` and `Remote (US/Canada)` are eligible and receive +2.
- Other identifiable US cities, such as Seattle or New York, are eligible but receive 0 points.
- `Remote` without geographic eligibility information is UNKNOWN.
- `Remote (North America)` is UNKNOWN unless US eligibility is explicitly established.
- International-only positions are rejected.

If a posting lists multiple locations, it qualifies geographically if at least one listed location is eligible in the United States.

Missing or ambiguous location information must not be interpreted as a non-US location.

### 2.5 Negative rules and mandatory rejection

The following conditions override the numerical score.

| Condition | Decision | Reason |
|---|---|---|
| Engineering Manager | REJECT | Alex targets individual contributor engineering roles. |
| Director / VP Engineering | REJECT | Outside Alex's current target responsibilities and career level. |
| Principal Engineer | REJECT | Requires a substantially more senior engineering profile. |
| Explicit minimum requirement of 8+ years | REJECT | Exceeds Alex's three years of professional experience. |
| Explicit non-US-only employment | REJECT | Outside the US job-search scope. |
| Senior Engineer | REVIEW | Seniority may exceed Alex's current experience, but the title alone is insufficient to reject it. |
| Lead Engineer | REVIEW | Requires additional examination of responsibilities and experience requirements. |

REVIEW is a flag, not a fourth outcome: a Senior or Lead posting still gets KEEP, REJECT or CANNOT TELL from §2.7, and KEEP results carry a `review: senior/lead` flag for my manual check.

**Experience matching rules:**

A mandatory experience requirement is considered a hard rejection when the posting explicitly specifies eight or more years using expressions such as:

- 8+ years of experience.
- 8 or more years of experience.
- Minimum of 8 years of experience.
- At least 8 years of experience.
- Equivalent expressions with a numerical requirement of 8 or higher.

Preferred experience is not treated as a mandatory minimum.

A requirement of five to seven years is not an automatic rejection under v1.0. It remains eligible for scoring and manual review.

**Reasoning:** Alex has approximately three years of professional experience. A strict minimum of eight years indicates a substantial mismatch, while preferred experience and seniority labels require more contextual judgment.

### 2.6 Missing or insufficient descriptions

A description is considered nearly empty when it contains fewer than 50 whitespace-separated words after HTML tags are removed and HTML entities are decoded.

| Condition | Decision |
|---|---|
| Description missing | CANNOT TELL |
| Description contains fewer than 50 words | CANNOT TELL |
| Description contains meaningful responsibilities and qualifications | Continue scoring |
| Description contains only generic information | Not detected automatically in v1.0 (see §3.7) |

**Reasoning:** Without meaningful job information, the agent cannot reliably establish whether the role matches Alex's technical background.

The 50-word cutoff is a hand-set data-quality threshold, not a claim that every description above 50 words is informative.

### 2.7 Final decision

| Condition | Result |
|---|---|
| Score >= 8, title match >= 2, at least one technical category, eligible US location | KEEP |
| Score below 8 | REJECT |
| Mandatory negative rule applies | REJECT |
| Missing title | CANNOT TELL |
| Missing location | CANNOT TELL |
| Missing or nearly empty description | CANNOT TELL |
| Remote geographic eligibility unknown | CANNOT TELL |

A KEEP decision means that the posting deserves further investigation. It does not guarantee that Alex satisfies every qualification or that the employer will consider his application.

### 2.8 Matching rules

All keyword matching follows these conventions:

1. Case-insensitive matching.
2. Whole-word or complete-phrase matching.
3. HTML entities are decoded before matching.
4. HTML tags are removed before description analysis.
5. Whitespace and punctuation are normalized.
6. Repeated occurrences of the same keyword count only once.
7. Multiple keywords in the same category count only once.
8. Substring matches are not accepted.

Examples:

| Posting text | Keyword | Match? |
|---|---|---|
| Java development | Java | YES |
| JavaScript development | Java | NO |
| Kafka-based workflows | Kafka | YES |
| KAFKA experience | Kafka | YES |
| Spring Boot applications | Spring Boot | YES |
| Spring 2027 internship | Spring Boot | NO |
| PostgreSQL databases | PostgreSQL | YES |

---

## 3. Evidence Rules

Relevance scoring and factual evidence are separate evaluations.

A posting can receive a high relevance score without supporting every claim made in its justification.

Every factual claim in the shortlist must be labeled SUPPORTED, CONTRADICTED, or INSUFFICIENT.

### 3.1 SUPPORTED

A claim is supported when the posting explicitly states the information or provides direct textual evidence.

Example:

- Claim: The position requires Java.
- Posting: Java development experience is required.
- Verdict: SUPPORTED.

### 3.2 CONTRADICTED

A claim is contradicted when the posting explicitly provides information that conflicts with the claim.

Example:

- Claim: The role requires no more than five years of experience.
- Posting: A minimum of eight years of experience is required.
- Verdict: CONTRADICTED.

### 3.3 INSUFFICIENT

A claim is insufficient when the posting does not provide enough evidence to establish whether it is true or false.

Example:

- Claim: The employer sponsors H-1B visas.
- Posting: No visa sponsorship information is provided.
- Verdict: INSUFFICIENT.

### 3.4 Important evidence distinctions

The agent must distinguish between:

- Required skills and preferred skills.
- Required experience and preferred experience.
- Remote work and remote work explicitly available to US applicants.
- Mentioning a technology and requiring experience with that technology.
- A company's general description and the actual responsibilities of the position.

For example, if Java appears only under Nice to Have, the claim that Java is required cannot be labeled SUPPORTED.

### 3.5 Claims that cannot be assumed

The agent must not invent or infer:

- Salary or compensation.
- H-1B or other visa sponsorship.
- Employer willingness to sponsor international students.
- Team size.
- Company culture.
- Work-life balance.
- Technologies not mentioned in the posting.
- Responsibilities not described in the posting.

### 3.6 Abstention rule: I cannot tell

The agent must explicitly say:

**"I cannot tell from the available posting text."**

This applies when:

1. The job description is missing.
2. The description contains fewer than 50 words after preprocessing.
3. The requested information is not present in the posting.
4. The title or location is missing and is required to make the decision.
5. The description is too incomplete or corrupted to establish a reliable conclusion.

The absence of evidence must never be treated as evidence of the opposite.

### 3.7 Abstention counterexample and limitation

A description containing 60 words of generic company marketing language could pass the 50-word minimum while providing no meaningful information about job responsibilities or qualifications.

Under the mechanical word-count rule, this posting would pass the initial description-length check.

This exposes a limitation of v1.0: word count does not guarantee useful information.

During the manual audit, I will identify whether this situation occurs in the collected postings and record any resulting false decisions. I will not claim that the initial abstention rule catches every incomplete description.

---

## 4. Expected Sources and Fields

The agent collects job postings from three applicant tracking systems.

### 4.1 Greenhouse

| Field | Purpose |
|---|---|
| `title` | Job title matching |
| `location.name` | Location evaluation |
| `content` | Technical matching and evidence evaluation |
| `id` | Posting identification |

### 4.2 Lever

| Field | Purpose |
|---|---|
| `text` | Job title |
| `categories.location` | Location evaluation |
| `descriptionPlain` | Technical matching and evidence evaluation |
| `id` | Posting identification |

### 4.3 Ashby

| Field | Purpose |
|---|---|
| `title` | Job title matching |
| `location` | Location evaluation |
| `descriptionHtml` | Technical matching and evidence evaluation |
| `id` | Posting identification |

### 4.4 Missing-field behavior

| Missing field | Expected behavior |
|---|---|
| Job title | CANNOT TELL; do not calculate role relevance. |
| Location | UNKNOWN; exclude from actionable shortlist. |
| Description | CANNOT TELL; do not assume technical relevance. |
| Posting ID | Flag as a data-quality issue; do not invent an identifier. |
| Optional metadata | Continue processing if the field is not necessary for scoring. |

The agent must not silently substitute fields from another board or assume that a missing field contains information.

### 4.5 Text preprocessing

Before scoring, the agent must:

1. Decode HTML entities.
2. Remove HTML tags.
3. Normalize whitespace and punctuation.
4. Convert matching text to lowercase.
5. Preserve the original posting text for evidence verification.
6. Apply consistent matching rules across all three sources.

The original source response must remain available so that every decision can be traced back to the collected posting.

---

## 5. Wrong Versions: Tests Must Catch

The following are plausible but incorrect implementations. The test suite must demonstrate why each is unreliable.

### Wrong Version 1: Substring Matching

**Incorrect approach:** Use substring matching to identify keywords.

Example:

- Configured keyword: Java.
- Posting: JavaScript developer.
- Incorrect result: Java match.

Why it is wrong: JavaScript is a different programming language. Substring matching creates false positives.

**Expected test:** Java must not match JavaScript.

### Wrong Version 2: Title-Only Filtering

**Incorrect approach:** Evaluate only the job title and ignore the description.

Example:

- Title: Software Engineer.
- Description: Primarily frontend development with no relevant technical skills.

Why it is wrong: A matching title does not establish that the actual position aligns with Alex's backend engineering background.

**Expected test:** A generic Software Engineer title without relevant technical categories must not automatically qualify.

### Wrong Version 3: Raw Keyword Counting

**Incorrect approach:** Add points every time a keyword appears.

Example:

- Posting A mentions Java, Spring Boot, and Kafka once each.
- Posting B mentions Java 30 times.

Why it is wrong: Repetition does not establish stronger relevance.

**Expected test:** Repeated occurrences of the same keyword must not increase the technical score.

### Wrong Version 4: Missing Description as Rejection

**Incorrect approach:** Automatically classify postings without descriptions as irrelevant.

Why it is wrong: Missing information does not prove that the role is irrelevant.

**Expected test:** A missing description must produce CANNOT TELL rather than REJECT.

### Wrong Version 5: Case-Sensitive Matching

**Incorrect approach:** Match keywords only when capitalization is identical.

Example:

- Configured keyword: Kafka.
- Posting: kafka experience required.

Why it is wrong: Capitalization does not change the meaning of a technical keyword.

**Expected test:** Kafka, KAFKA, and kafka must all match.

---

## 6. False Friends: Audit Expectations

I expect potential false friends among generic technical terms, including:

| Word | Potential false match |
|---|---|
| Platform | Business platform rather than software infrastructure. |
| Training | Employee training rather than machine learning. |
| Spring | Spring internship rather than Spring Boot. |
| Cloud | General cloud product rather than cloud infrastructure. |
| Java | A non-programming context rather than Java development. |

These terms will be examined during the manual rejection and shortlist audits.

A keyword match alone is not sufficient evidence that a posting is relevant. The surrounding context must be examined before accepting a match.

At least one actual false friend will be identified and documented from the collected postings during the audit.

---

## 7. Origin of Scoring Numbers

All numerical values in v1.0 are hand-set. They are not fitted using a machine-learning model or optimized against the audit labels.

| Parameter | Value | Origin |
|---|---:|---|
| Matching target titles | 3 | Inherited from Alex's persona |
| Title weight | 4 | Hand-set |
| Technical categories | 8 | Derived from Alex's skills |
| Category weight | 1 | Hand-set |
| Technical score cap | 8 | Hand-set |
| Target location weight | 2 | Hand-set |
| Relevance threshold | 8 | Hand-set |
| Experience rejection cutoff | 8+ years | Hand-set |
| Minimum description length | 50 words | Hand-set |

These values represent the initial design assumptions. Their effectiveness must be measured against manually reviewed postings and held-out labels.

---

## 8. Version History

| Version | Changes |
|---|---|
| v1.0 | Initial documented filter. Replaces JS2's binary title/three-skill/location rule with weighted scoring, explicit evidence classifications, abstention rules, source-field definitions, and testable failure cases. |

All weights, the threshold of 8, the 8-year experience cutoff, and the 50-word description cutoff are hand-set in v1.0.

Any changes after testing must be recorded in a new version with:

- The rule added, modified, or removed.
- The reason for the change.
- Evidence from manual audits or test results.
- The impact on previously classified postings.

**Important:** Version 1.0 is an initial hypothesis, not an optimized filter. Its effectiveness must be evaluated against manually reviewed postings before claiming that it reliably identifies relevant opportunities.