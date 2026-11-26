# FILTER.md: Job-Search Agent 3 — The Filter, the Tool, and the Score

Ethan Gomes · INFO 7375 · v1.3 · 2026-11-25 

## Scope

This file decides which collected postings reach me, and why. It is written before the filter, the shortlist, the tool server or the
scorer exist, and the code must follow it. It builds on my JS2 agent (commit `7404ffb`) and on my JS1 contract: the five rules R1–R5 in
`CONTRACT.md`, applied to the fictional persona Evan Gordon, a data engineer with about 4 years of experience who prefers Boston and is
open to remote or relocating within the US. A rule changes only through a new version of this file, with the change and its reason in
the change log at the bottom.

A posting ends in exactly one of three buckets:

- **kept**: it passes every hard rule and its score reaches the threshold. Kept postings are ranked by score.
- **rejected**: a hard rule fails on evidence in the posting's own text.
- **cannot tell**: a field the rules need is missing or empty, so the filter does not guess. These are listed separately and never
  counted as rejects or as "nothing relevant".

## 1. The filter (v1.3)

### Hard rules

| Rule | Reads | Passes when | Reasoning |
|---|---|---|---|
| **F1 Role** | title | The title contains one of the role phrases: "data engineer", "analytics engineer", "data platform", "data infrastructure", "data analyst", "business intelligence", "BI engineer" (case-insensitive, whole phrase); **or** (v1.3) the title has the whole word Engineer or Developer **and** the whole word Data or Pipeline | Evan's target titles, plus the two BI phrases because Tableau and Power BI are among his shipped skills. Whole phrases, because the word "data" or "analyst" alone matches unrelated jobs. The v1.3 clause because data platform work is often titled "Software Engineer - Distributed Data Systems": it raised held-out recall from 2/7 to 6/7 |
| **F2 Seniority** | title | The title contains none of these as whole words: Staff, Principal, Lead, Manager, Management, Director, Head, VP, Intern, Internship (v1.3), Distinguished, Architect. "Senior" is allowed | These levels are above or below 4 years. Senior is judged by years (F4) instead, because many Senior data roles ask for 4–5 |
| **F3 Location** | location | Boston, or a US marker (state, code, "United States", listed metro) as a whole word; remote counts if it names the US | Evan is in Boston, open to remote and to relocating within the US only |
| **F4 Years** | description | The first "N years" phrase with "experience" within 60 characters has N ≤ 5 | Evan has about 4 years; up to 5 is a fit, more is not. 3 or fewer is preferred and scores higher |

F4 fails only on a stated number above 5. A description with no years phrase passes F4, but the shortlist must then say "I cannot tell"
about seniority fit (section 2).

### Topic words and the score

The topic words are Evan's shipped skills, grouped as in his persona:

| Group | Words |
|---|---|
| Languages | Python, SQL, Scala, Bash |
| Data tools | Spark, Airflow, dbt, Kafka, Databricks, Pandas |
| Database and cloud | Snowflake, PostgreSQL, BigQuery, Redshift, AWS, GCP |
| DevOps | Docker, Terraform, Git, GitHub Actions |
| BI | Tableau, Power BI |

| Rule | Reads | What it does | Reasoning |
|---|---|---|---|
| **T1 Distinct, case-sensitive, whole-word** | description | Counts how many **different** topic words appear, matching exact case and whole words | "Spark" the tool is capitalized, "spark" the verb is not; "Scala" must not match "Scalable"; repeating "SQL" ten times is still one skill |
| **T2 Not counted** | — | Flink and Kubernetes never count | Evan has used them but never shipped them |
| **T3 Threshold** | — | Kept only if at least **2** distinct topic words appear | Inherited from JS1 R4: one shared word is too weak a signal |

The score ranks kept postings on a scale of 0 to 100. Every number has a stated origin, and changes to them are measured one at a time
on held-out labels (section 5).

| Part of the score | Points | Origin |
|---|---|---|
| Each distinct topic word, capped at 8 | 8 each (max 64) | set by me, v1.1 |
| Years N ≤ 3 (preferred) | +16 | set by me; points v1.1, cut-off 3 v1.2 (the persona said 4) |
| Location: Boston, or else remote in the US (one bonus only) | +10 Boston, +5 remote US | set by me, v1.1 |
| Visa sponsorship offered (rule V1) | +10 | set by me, v1.1 |
| **Maximum** | **100** | 64 + 16 + 10 + 10 |
| Threshold: at least 2 distinct topic words | gate, not points | inherited from JS1 R4 |
| Years limit 5 | gate, not points | inherited from the persona |

A posting asking for 4 or 5 years is kept but gets no years bonus, and so does a posting with no years phrase. A posting that is both in Boston and remote gets the Boston bonus only.

### Visa sponsorship (points only, never a reject)

| Rule | Reads | What it does | Reasoning |
|---|---|---|---|
| **V1 Sponsorship offered** | description | +10 only when a sentence states that visa sponsorship is offered or available. A sentence that also negates it ("unable to sponsor", "does not sponsor", "no sponsorship", "without sponsorship") earns nothing | I want postings that clearly sponsor ranked higher, but I don't want to drop good jobs that are silent about it |
| **V2 Silent or negative** | — | A posting that says nothing about sponsorship, or says it doesn't sponsor, is still kept if it passes F1–F4 and T3. It gets no visa points | The filter reads only the posting's own text. A company's general visa policy is not observed, so silence is "I cannot tell", not "no" |

The closest calls are postings that pass F1–F4 with exactly 1 or 2 distinct topic words, or with a years phrase of exactly 5 or 6.
These are the postings the reject audit samples near the threshold.

### Text rules

| Rule | Reasoning |
|---|---|
| **X1** Descriptions are compared after HTML is stripped and entities are decoded | Greenhouse sends HTML; a tag or `&amp;` must not hide or create a match |
| **X2** Matching uses the whole description, never a truncated part | In JS1 a 6,000-character cut hid "10+ years" from the judge |
| **X3** A topic word inside a longer word, or in the wrong case, does not count | The JS1 false friends: "React" inside "React Native", "Scala" inside "Scalable", "PowerBI" written as one word |

## 2. The evidence rules

The shortlist gives a justification for each kept posting as a list of claims, such as "requires 3+ years", "uses Airflow" or "remote in
the US". Each claim is labeled against the posting's own text (title, location and description) and nothing else.

| Label | When |
|---|---|
| **supported** | A span of the posting text states the claim. The label records the field and the quoted span. A word that merely appears is not enough: the span must say what the claim says (for example "Python a plus" does not support "requires Python") |
| **contradicted** | A span states the opposite: "8+ years" against "requires at most 5 years", "on-site only" against "remote", "not required" against "requires" |
| **insufficient** | No span supports or contradicts it. A claim that needs a fact the posting doesn't give (salary, team, visa) is insufficient |

**Relevance is not entailment.** A posting can match the filter's words and still fail to support a claim. The shortlist report must
show at least one such posting.

**When the agent must say "I cannot tell":**
- the description is missing or empty: no claim about years or skills can be made
- the location is missing or does not name a country (for example a bare "Remote"): no claim about US eligibility
- no years phrase exists: no claim about seniority fit
- the posting never mentions sponsorship: no claim about visa sponsorship either way
- the claim needs a fact the posting never states
- the raw response failed to load or failed its shape check (the JS2 error policy)

In these cases the agent answers "I cannot tell from the posting", names the missing field, and does not guess. The report must also
show one counterexample where this abstention rule gives the wrong answer.

## 3. The expected sources

**Boards:** the same ten as JS2 (`config/boards.json`): Samsara, Databricks, Toast, Klaviyo and Datadog on Greenhouse; Palantir, Spotify,
Zoox and Kraken on Lever; and the deliberate 404 board.

**Fields the filter reads:**

| Field | Greenhouse | Lever |
|---|---|---|
| title | `title` | `text` |
| location | `location.name` | `categories.location` |
| description | `content` (HTML) | `descriptionPlain`, the `lists` items, and `additionalPlain` |
| link | `absolute_url` | `hostedUrl` |

**Collection for JS3:** JS2's Greenhouse list requests did not include descriptions, so the filter cannot run on them. JS3 collects a
fresh snapshot of the same boards with descriptions: one Greenhouse list request per board with `?content=true`, and Lever's list, which
already includes them. This is a change to JS2's fixed URL template, recorded here as a decision. The hosts, the read-only GET rule and
the rest of JS2's permission policy are unchanged.

**When something is missing:**

| Situation | Answer |
|---|---|
| A board fails (404, timeout, bad shape) | "Not observed": no postings, and never "no relevant jobs" (JS2 error policy) |
| A board returns an empty list (Kraken) | "0 postings, needs review", never "no relevant jobs" |
| A posting has no description | cannot tell |
| A posting has no location, or a location with no country | cannot tell for F3 |
| A posting has no title | cannot tell |

## 4. Wrong versions the tests must catch

1. **Role by single word.** F1 matches "data" or "analyst" alone, so "Data Center Technician" and "Compliance Analyst" are kept.
2. **Case-insensitive topic words.** "spark" the verb and "Scalable" count as Spark and Scala.
3. **Counting repeats.** A description that says "SQL" fifteen times outranks one that names five different tools.
4. **Missing description treated as zero skills.** A posting with no description is rejected instead of going to "cannot tell".
5. **Years from the wrong phrase.** The last years phrase is used, or a number with no "experience" nearby ("founded 12 years ago").
6. **A word counts as support.** "Python a plus" is labeled as supporting the claim "requires Python".
7. **Abstention that never fires.** A bare "Remote" location is labeled as remote in the US.
8. **Tuning on the held-out labels.** A score change is chosen using the labels set aside for measuring it.
9. **The word "sponsor" counts as an offer.** "We are unable to sponsor visas" or "event sponsorship" earns the +10 visa points.
10. **Two location bonuses.** A posting listed as "Boston or Remote (US)" gets +10 and +5, so the score can pass 100.

## 5. Labels and measurement

Before any score change is tried, I hand-label a set of postings from the new snapshot as relevant or not, without seeing the filter's
or Claude's answers, following the labeling rule from JS1. The set is split into tuning labels and held-out labels, and the held-out
file's hash is recorded before tuning starts. Every change in section 1 is measured only on the held-out labels, one change at a time.

## Change log

| Version | Date | Change | Reason |
|---|---|---|---|
| v1 | 2026-11-24 | First version, written before any JS3 code | Built from the JS1 contract R1–R5, the persona and the JS2 boards |
| v1.1 | 2026-11-25 | Score out of 100 (8 per skill, capped at 8; +16 years; +10 Boston or +5 remote US; +10 visa); visa rules V1–V2; "business intelligence" and "BI engineer" added to F1; wrong versions 9–10. Kept: threshold 2, Senior allowed, years limit 5, no years phrase = kept, fresh snapshot | My decisions on the v1 placeholders, still before any JS3 code |
| v1.2 | 2026-11-25 | Preferred years cut-off moved from 4 to 3: N ≤ 3 gets +16; 4–5 is kept with no bonus; the limit stays 5 | I prefer roles asking 3 years or fewer, but up to 5 is still a fit; still before any JS3 code |
| v1.3 | 2026-11-25 | **Added** to F1: Engineer/Developer + whole word Data or Pipeline (change A). Tuning recall 2/4 → 3/4, no false keeps; held-out (one look) recall 2/7 → 6/7, precision 0.67 → 0.75 | The only change that moved anything on tuning, and it held on held-out |
| v1.3 | 2026-11-25 | **Added** "internship" to F2. **Not measured**: found on held-out, where change A kept "Software Engineer, Internship - Data Connectors"; validating it needs new labels | "intern" as a whole word misses "Internship"; my rule excludes internships |
| v1.3 | 2026-11-25 | **Rejected** B (threshold 2 → 1), C (threshold 2 → 3), E (no location bonus): no effect on tuning (E: AUC 0.809 → 0.801), so not sent to held-out | A number that changes nothing measurable stays as written |
| v1.3 | 2026-11-25 | **Rejected** D (drop the years ≤ 3 bonus): tuning AUC 0.809 → 0.711 (bonus helps), held-out 0.869 → 0.877 (bonus slightly hurts). Bonus kept at +16 | The two splits disagree, so with 4 and 7 relevant postings the effect is noise; no change is justified |
