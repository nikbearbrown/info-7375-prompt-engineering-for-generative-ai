# FILTER.md — Job-Search Agent 3

Tushar Patel · INFO 7375 · Fall 2026
Version 0.1 · November 21, 2026 · written before any JS3 code

## Who the filter is for

The fictional persona **Cole Palmer** (`../js1-contract-and-watch/persona/cole-palmer.example.json`). The filter reads only `skills`, `job_search.target_titles`, `job_search.years_experience`, `job_search.needs_sponsorship`, and `job_search.work_country`. Target titles: Software Engineer, AI Engineer, Backend Engineer. Persona values: `years_experience` 0, `needs_sponsorship` true, `work_country` US. Skills: Python, Java, TypeScript, SQL, PostgreSQL, Spring Boot, React, Docker, AWS.

## Verdicts

Every posting gets exactly one verdict: **keep**, **reject**, or **cannot_tell**. Gates run first. A failed gate is a reject, whatever the score. An unknown gate is cannot_tell. The score decides only between keep and reject for postings that pass every gate.

## The filter

### Gates (any fail → reject; any unknown → cannot_tell)

| ID | Rule | Reason |
|---|---|---|
| G1 Title role | The title contains, whole-word and case-insensitive, one of: Software Engineer, Software Developer, Backend Engineer, Back-End Engineer, Full Stack Engineer, Full-Stack Engineer, AI Engineer, Machine Learning Engineer, ML Engineer. Otherwise fail. | Cole targets these roles. Other "Engineer" titles (Sales, Solutions, Support, Security) are different jobs. |
| G2 Title seniority | Fail if the title contains Senior, Sr, Staff, Principal, Lead, Manager, Director, Head, VP, or Intern. Exclusions win over G1. | Cole has 3 years or less; these titles signal more, or an internship. |
| G3 Location | Pass if any listed location is in the US, or is US remote. Fail if every listed location is outside the US. Unknown if the only value is "Remote" or a placeholder with no country. | Cole's `work_country` is US. A bare "Remote" doesn't say where. |
| G4 Experience | Find every stated minimum ("N+ years", "N–M years", "at least N years", "N years of"). Fail if the largest minimum is more than 3. Unknown if none is stated. | Cole has 3 years or less. A posting that states nothing hasn't ruled him in or out. |
| G5 Sponsorship | Applies only if `needs_sponsorship` is true (it is). Fail if the text says, in a stated phrase, that the employer will not sponsor (for example "unable to sponsor", "will not sponsor", "without sponsorship"). Otherwise pass. | A posting that says it won't sponsor is a hard no for a person who needs it. Silence is not a no. |

### Score (only for postings that pass every gate)

| Term | Points | Reason |
|---|---|---|
| Topic words in the text: backend, API, distributed systems, infrastructure, platform, full-stack, LLM, machine learning | +1 per distinct word, cap 3 | Signals the work matches Cole's direction. The cap stops long postings from winning on length. |
| Cole's `skills` in the text | +1 per distinct skill, cap 3 | Direct overlap with what Cole can show. The cap has the same reason. |

**Keep if score ≥ 2.** Near-threshold calls are scores 1–3. Threshold and weights are hand-set in v0.1. Where every number came from is tracked in the score report.

Matching is whole-word and case-insensitive on the posting text after HTML-unescape and tag stripping. "Java" does not match "JavaScript".

## Evidence rules

The shortlist explains each keep with **claims**. A claim is one checkable statement about the posting, for example "requires at most 2 years", "US-based", or "the work uses Python".

| Label | When it applies |
|---|---|
| **supported** | A span quoted verbatim from the posting text asserts the claim. The quote must exist in the text. Its meaning must assert the claim, not just mention the word. |
| **contradicted** | A quoted span asserts the opposite of the claim. |
| **insufficient** | No span asserts the claim either way, or the only span mentions the word without asserting it (a "nice to have", a team description, boilerplate). |

**Relevance is not entailment.** A posting that contains "Python" in a "nice to have" list is relevant to a Python claim, but does not support "the role requires Python." That claim is insufficient.

**When the agent must say "I cannot tell":**
- Any gate is unknown (bare "Remote", no experience stated).
- The posting has no text, or the text is under 200 characters after stripping.
- A shortlist claim that the verdict depends on is insufficient.

It never fills these gaps with a guess, and never reports them as a reject.

## Expected sources

| Board | Route | Text field | Location fields | Date field |
|---|---|---|---|---|
| greenhouse/stripe | `/v1/boards/stripe/jobs?content=true` | `content` (HTML-escaped) | `location.name` | `first_published`, else `updated_at` |
| ashby/notion | `/posting-api/job-board/notion` | `descriptionPlain` | `location`, `secondaryLocations[]`, `isRemote`, `workplaceType` | `publishedAt` |
| ashby/linear | `/posting-api/job-board/linear` | `descriptionPlain` | same as Notion | `publishedAt` |

**Gate change (dated 2026-11-21):** JS2 GATE F2 denied every query string. For JS3, the single query `?content=true` is allowed on the Greenhouse listing route only, because the filter and evidence rules need posting text. Every other query, path, host, and method rule from JS2 stays. The permission tests must show that `?content=true` is allowed and any other query is still denied.

**When something is missing:**
- A board fails to fetch → its postings are absent, reported as a board failure, never as zero postings.
- A posting has no text → cannot_tell (unless G1 or G2 already rejects it from the title).
- A location field is missing → G3 unknown → cannot_tell.
- A persona field the filter reads is missing → the run stops with an error.

## Wrong versions my tests must catch

| Wrong version | What the test must show |
|---|---|
| Substring matching: "AI" matches inside "maintain", or "Engineer" matches "Engineering Manager" as a role. | Whole-word matching. "Engineering Manager" fails G1, and the seniority word also fails G2. |
| Exclusions lose: "Senior Software Engineer" is kept because G1 matched. | G2 rejects it whatever G1 says. |
| Missing text becomes a reject, silently dropping postings that couldn't be judged. | No-text postings are cannot_tell, counted separately. |
| A bare "Remote" becomes a pass (or a reject). | It is cannot_tell. |
| Length bias: a long posting outranks a short one by piling up topic hits. | Each score term is capped at 3. |
| A shortlist claim is labeled supported because its keyword appears in the text. | A "nice to have" or team-description span gives insufficient, not supported. |

## Predicted false friends (to check in the reject audit)

"training" (ML training vs. employee training), "agent" (AI agents vs. support or sales agents), "pipeline" (data vs. sales pipeline), "model" (ML vs. business model), "platform" (software vs. marketing platform), and Greenhouse's AI-disclaimer boilerplate putting "AI" in non-AI postings.

## Changelog

| Version | Date | Change | Reason | Measured by |
|---|---|---|---|---|
| 0.1 | 2026-11-21 | Initial filter, evidence rules, sources, and wrong versions | Written before the build | — |

Rules added, cut, or rejected after measuring go here, each with the measurement that justified it.
