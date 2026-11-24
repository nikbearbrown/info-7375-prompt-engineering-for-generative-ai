# FILTER.md — Job-Search Agent 3
Version: 0.2
Written by Sreevarshan Sathiyamurthy, 2026-11-24, before any code.

## 1. What this filter decides

A posting passes the filter if it is plausibly relevant for Priya Nair: an OPT student targeting ML and data engineering roles. The filter runs on what the raw data actually contains. It does not guess at fields that are not present.

## 2. Role words (title matching)

A posting passes on title if its title contains at least one of:

- machine learning
- ml engineer
- data engineer
- data scientist
- ml platform
- mlops
- data platform
- analytics engineer
- software engineer (only when paired with a topic word — see section 3)

Reasoning: these are the titles Priya Nair is targeting. "Software engineer" alone is too broad; it passes only when the description or metadata also contains a topic word.

## 3. Topic words (description and metadata matching)

Applies to Lever postings (Spotify), which have description text. A posting passes on topic if its description or lists contain at least one of:

- python
- pytorch
- tensorflow
- spark
- sql
- dbt
- airflow
- kafka
- kubernetes
- ml pipeline
- feature store
- data warehouse
- etl

Reasoning: these are tools and concepts in Priya Nair's skill set and the roles she is targeting.

For Greenhouse postings (Databricks, Stripe): description text was not fetched. Title matching is the only available signal. This is a known gap. Postings are not rejected on the absence of topic words when no description is available; they are accepted or rejected on title alone.

## 4. Hard rejects (title matching)

A posting is rejected regardless of topic words if its title contains any of:

- manager
- director
- principal (when not paired with "engineer" or "scientist")
- VP
- head of
- counsel
- legal
- recruiter
- executive

Reasoning: these are seniority or function mismatches for a new-graduate OPT candidate.

## 5. Evidence rules

A claim about a posting (for example, "this role requires Python") counts as:

- **Supported**: the word or phrase appears in the posting's own text fields (title, description, lists, metadata values).
- **Contradicted**: the posting's text explicitly states the opposite (for example, "no Python required").
- **Insufficient**: the field is absent, empty, or the word does not appear. This is the default for Greenhouse postings where description was not fetched.

The agent must say "I cannot tell" rather than inferring from the company name or job board. A Databricks posting does not automatically become an ML posting because Databricks works on ML products.

## 6. Expected sources

| Board | ATS | Fields available | Description available |
|---|---|---|---|
| Databricks | Greenhouse | title, location, metadata | No |
| Stripe | Greenhouse | title, location, metadata | No |
| Spotify | Lever | title, description, categories, lists | Yes |

If a board returns zero postings or is unreachable, the filter reports that board as missing and does not treat missing as zero-match.

## 7. Wrong versions this filter must catch

**Wrong version A — topic-only filter:** A filter that passes postings based only on topic words, with no title check. Would pass postings for "ML Recruiter" or "Legal Ops with Python experience." Tests must include a posting with a topic word in a non-target role.

**Wrong version B — strict keyword match without stemming awareness:** A filter that rejects "Machine Learning Engineer" because the rule says "machine learning" (lowercase) and the title is mixed case. Tests must check case-insensitive matching.

## 8. Version history

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-11-24 | Initial version, written before any code |
| 0.2 | 2026-11-24 | Added section 9: implementation decisions recorded after first build |

## 9. Implementation decisions (v0.1 → v0.2 candidates)

These choices were made during the first build and are recorded here for the reject audit. Each is a candidate for revision after measuring.

**Word boundary matching:** A role or topic word must start at a word boundary but may carry a suffix. "data engineer" matches "Data Engineering"; "etl" does not match inside "settlement"; "sql" does not match inside "PostgreSQL". Plain substring matching would produce false friends on short tokens.

**Where topic words are searched:** Description fields, lists, and Greenhouse metadata values. A Lever posting with a role-word title passes on title alone (reason: title_match) even without a topic word in the description.

**Software engineer + Greenhouse (no description):** A Greenhouse "Software Engineer" posting with no topic word in metadata receives reason no_match and topic_evidence: insufficient. It does not automatically pass on title alone. This may need revision after the reject audit shows how many such postings exist.
