# FILTER.md — Job-Search Agent 3

Tushar Patel · INFO 7375 · Fall 2026
Version 0.2 · November 23, 2026 (erratum: first written as November 24) · decisions frozen before any v0.2 code and before any held-out comparison
(v0.1 · November 21, 2026 · written before any JS3 code; its replaced text is kept in the changelog)

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
| G4 Experience | Find every stated minimum ("N+ years", "N–M years", "at least N years", "N years of") and every stated maximum ("less than N years", "up to N years", "no more than N years"). A range counts by its lower bound. Ignore a minimum whose sentence says "preferred", "nice to have", "bonus" or "a plus". If mandatory minimums remain: pass if all are ≤ 2, fail if all are > 2, unknown if some are each. If none remain but a maximum is stated: pass if 0 years satisfies it. If nothing is stated: pass. Details: "G4 in v0.2" below (C1–C4, C6). | Cole has 0 years. A cutoff of 2 allows some stretch roles (C3, a search-scope choice). Silence about experience is not a bar (C1), and a posting that sends mixed signals is cannot_tell, not reject (C4). |
| G5 Sponsorship | Applies only if `needs_sponsorship` is true (it is). Fail if the text says, in a stated phrase, that the employer will not sponsor (for example "unable to sponsor", "will not sponsor", "without sponsorship"). Otherwise pass. | A posting that says it won't sponsor is a hard no for a person who needs it. Silence is not a no. |

### Score (only for postings that pass every gate)

| Term | Points | Reason |
|---|---|---|
| Topic words in the text: backend, API, distributed systems, infrastructure, full-stack, LLM, machine learning ("platform" removed in v0.2, C5) | +1 per distinct word, cap 3 | Signals the work matches Cole's direction. The cap stops long postings from winning on length. |
| Cole's `skills` in the text | +1 per distinct skill, cap 3 | Direct overlap with what Cole can show. The cap has the same reason. |

**Keep if score ≥ 2.** Near-threshold calls are scores 1–3. Threshold and weights are hand-set (unchanged in v0.2). Where every number came from is tracked in the score report.

Matching is whole-word and case-insensitive on the posting text after HTML-unescape and tag stripping. "Java" does not match "JavaScript".

### G4 in v0.2 (changes C1–C4, C6)

Each change has an ID so it can be switched on alone on top of v0.1 and measured separately (see "Rule modes").

| ID | Change | Rule |
|---|---|---|
| C1 | No stated experience passes | If the text states no mandatory minimum and no maximum, G4 **passes** (v0.1: unknown). This is G4 only: it does not establish that the posting suits Cole overall. A posting with no usable text (missing, or under 200 characters) is still cannot_tell. |
| C2 | Stated maximum | "less than N years", "up to N years", "no more than N years" (also "year") are maximums. With no mandatory minimum, G4 **passes** when 0 years satisfies every stated maximum ("less than N" needs N ≥ 1; "up to N" and "no more than N" always hold) and fails otherwise. A mandatory minimum, if present, still decides (a maximum never overrides a conflicting minimum). A number inside a maximum phrase is not also read as a minimum ("less than 2 years of" is a maximum of 2, not a minimum of 2). In a maximum, N may be digits or a spelled number one–ten ("less than two years"). |
| C3 | Cutoff 3 → 2 | The cutoff in G4 is 2 years (v0.1: 3). This is a search-scope decision for Cole (0 years) that allows some stretch roles, not a conclusion proved by the audit. |
| C4 | Ranges, levels, preferred | A range counts by its lower bound. Every mandatory minimum is evaluated: all ≤ cutoff → pass; all > cutoff → fail; some of each → **unknown** (cannot_tell) (v0.1: fail if the largest is over the cutoff). A minimum is **preferred**, and ignored, if its own sentence contains "preferred", "nice to have", "bonus" or "a plus", **or** it sits under a heading containing any of those words (e.g. "Preferred qualifications", "Nice to have"), until the next heading. Every other minimum is mandatory. Never reject only because a range's upper end is high. |
| C6 | Spelled number with digit | "two (2) years" and similar "word (N)" forms count as N, in every G4 form: mandatory or preferred, minimum or maximum ("at least two (2) years", "five (5) years of", "less than two (2) years"). A spelled number without a digit is still not a minimum. |

**Sentence (used by C4).** A sentence is a piece of one source block that ends at ".", "!" or "?" followed by a space, or at the end of the block. A block is a Greenhouse HTML block (paragraph, list item, heading, div, table cell, or a line break) or one Ashby line.

**Heading (used by C4).** A block is a heading if it is a Greenhouse `<h1>`–`<h6>`, or if it is not a list item (not a Greenhouse `<li>`, not an Ashby line starting with "-", "•", "*" or "–") and has at most 8 words and does not end with ".", "!" or "?". So "Preferred qualifications" as a `<p>` and Ashby's "NICE TO HAVE" line are headings. A preferred heading (one containing "preferred", "nice to have", "bonus" or "a plus") makes every block after it preferred until the next heading of any kind. A posting with no block structure has no headings.

Cutoff, maximum and mandatory are G4 terms only; G1–G3, G5 and the evidence rules are unchanged.

### Rule modes

| Mode | Rules |
|---|---|
| `v0.1` | FILTER.md v0.1 exactly (commit 821ddee); its results must reproduce `out/filter-v0.1/results.jsonl` byte for byte |
| `v0.1+C1` … `v0.1+C6` | v0.1 with that one change only |
| `v0.2` | v0.1 with C1–C6 together |

## Evidence rules

The shortlist explains each keep with **claims**. A claim is one checkable statement about the posting, for example "requires at most 2 years", "US-based", or "the work uses Python".

| Label | When it applies |
|---|---|
| **supported** | A span quoted verbatim from the posting text asserts the claim. The quote must exist in the text. Its meaning must assert the claim, not just mention the word. |
| **contradicted** | A quoted span asserts the opposite of the claim. |
| **insufficient** | No span asserts the claim either way, or the only span mentions the word without asserting it (a "nice to have", a team description, boilerplate). |

**Relevance is not entailment.** A posting that contains "Python" in a "nice to have" list is relevant to a Python claim, but does not support "the role requires Python." That claim is insufficient.

**When the agent must say "I cannot tell":**
- Any gate is unknown (bare "Remote"; in v0.1, no experience stated; in v0.2, mandatory minimums on both sides of the cutoff).
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

## False friend

**"platform"** (removed from the topic words in v0.2, C5). Stripe's boilerplate sentence "Stripe is a financial infrastructure platform for businesses." appears in 717 of 979 postings in `evidence/runs/live-text-1`. In 471 postings that sentence (or Linear's "the platform of choice") is the only place "platform" appears. Together with "infrastructure" from the same sentence it gave 2 topic points with no skill match, which meets the keep threshold of 2. In the audit, row 6's near-threshold keep scored 2 from that sentence alone (0 without it). Source: `audit/AUDIT-RESULTS.md` section e (commit 0df210f7).

"infrastructure" comes from the same sentence (421 postings where it is the only occurrence) but stays a topic word for now; it is counted separately, without a rule change.

## Changelog

| Version | Date | Change | Reason | Measured by |
|---|---|---|---|---|
| 0.1 | 2026-11-21 | Initial filter, evidence rules, sources, and wrong versions | Written before the build | — |
| 0.2 C1 | 2026-11-23 | G4: no stated experience passes | Audit: 7 of 10 cannot_tell rows were G4 unknown, and the hand label was keep for all 7 (rows 13, 14, 18, 20, 21, 34, 39) | v0.1 vs v0.1+C1 on the held-out set |
| 0.2 C2 | 2026-11-23 | G4: a stated maximum that 0 years satisfies passes | Audit rows 20 and 39: "You have less than two years of engineering experience." was G4 unknown; hand label keep | v0.1 vs v0.1+C2 on the held-out set |
| 0.2 C3 | 2026-11-23 | G4 cutoff 3 → 2 | Search-scope decision: persona `years_experience` is 0 while v0.1 allowed 3. Audit rows 3, 31, 33, 35 and 48 passed G4 at 2–3 years against hand labels of reject or cannot_tell. Not a conclusion proved by the audit | v0.1 vs v0.1+C3 on the held-out set |
| 0.2 C4 | 2026-11-23 | G4: every mandatory minimum evaluated; mixed → unknown; preferred minimums ignored; range by lower bound | Ranges such as "2–12+ years" (audit rows 31, 33, 35) and level-spanning postings | v0.1 vs v0.1+C4 on the held-out set |
| 0.2 C5 | 2026-11-23 | Topic words: remove "platform" | False friend (section above): Stripe boilerplate in 717 postings gave 2 topic points with no skill match | v0.1 vs v0.1+C5 on the held-out set |
| 0.2 C6 | 2026-11-23 | G4: "two (2) years" forms count as the digit | Build-step-1 gap; 3 postings have the form, 1 verdict changes in the what-if (audit section f) | v0.1 vs v0.1+C6 on the held-out set |
| 0.2 C2 note | 2026-11-23 | C2 maximums accept spelled numbers one to ten ("less than two years"). **Accepted** by Tushar | Rows 20 and 39 write their maximum in words | with C2 |
| 0.2 erratum | 2026-11-23 | 2026-11-23: erratum, v0.2 date corrected from 2026-11-24 (typo) | Tushar's instruction said 2026-11-24; the date was 2026-11-23 | — |
| 0.2 C4 amended | 2026-11-23 | 2026-11-23: C4 amended before any held-out comparison: preferred headings now mark their items as preferred, matching the v0.2 intent | v0.2 as first frozen counted minimums under a "Preferred qualifications" heading as mandatory; no held-out comparison had been run | v0.1 vs v0.1+C4 on the held-out set |
| 0.2 rejected | 2026-11-23 | G3: "N/A" location → reject. **Rejected** | Audit rows 10 and 42 were hand-labeled reject, but a placeholder doesn't say where the job is; it stays cannot_tell (row 36, also "N/A", was hand-labeled cannot_tell) | — |
| 0.2 rejected | 2026-11-23 | G2 Intern/Internship, topic APIs, topic LLMs variants. **Rejected for v0.2** | Measured: no verdict changes in the audited sample (Internship 1 posting, APIs 156, LLMs 12; 0 verdict changes each). That does not prove they would never matter | — |

**Decisions frozen 2026-11-23 before any held-out comparison. Each change C1–C6 will be measured separately against v0.1 on the held-out set, and the combined v0.2 separately. Rules will not be revised in response to held-out results.**

Not decided in v0.2 (left as in v0.1): the G4 "1 year" singular form (8 postings; 7 of them say "At least 1 year of university education", which is education, not experience).

### v0.1 text replaced in v0.2 (kept verbatim)

- G4 row: `| G4 Experience | Find every stated minimum ("N+ years", "N–M years", "at least N years", "N years of"). Fail if the largest minimum is more than 3. Unknown if none is stated. | Cole has 3 years or less. A posting that states nothing hasn't ruled him in or out. |`
- Score topic row: `| Topic words in the text: backend, API, distributed systems, infrastructure, platform, full-stack, LLM, machine learning | +1 per distinct word, cap 3 | Signals the work matches Cole's direction. The cap stops long postings from winning on length. |`
- Score note: `**Keep if score ≥ 2.** Near-threshold calls are scores 1–3. Threshold and weights are hand-set in v0.1. Where every number came from is tracked in the score report.`
- Cannot-tell bullet: `- Any gate is unknown (bare "Remote", no experience stated).`
- Header: `Version 0.1 · November 21, 2026 · written before any JS3 code`

The complete v0.1 file is at commit 821ddee.

Rules added, cut, or rejected after measuring go here, each with the measurement that justified it.
