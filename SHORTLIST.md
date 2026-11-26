# Source-grounded shortlist

The shortlist is built by `jsagent/shortlist.py` and written by `scripts/run_filter.py`. Each kept posting carries a list of claims.
Each claim is labeled **supported**, **contradicted** or **insufficient** against the posting's own text, with the field and the
quoted span, following FILTER.md §2.

- **v1.2** (`runs/filter-v1.2/shortlist.json`): 5 postings, 46 claims (26 supported, 20 insufficient, 0 contradicted)
- **v1.3** (`runs/filter-v1.3/shortlist.json`, the current filter): 10 postings, 85 claims (48 supported, 37 insufficient)

## The v1.3 shortlist

| # | Score | Posting | Location |
|---|---|---|---|
| 1 | 69 | Samsara — Software Engineer - Data Platform | Remote - US |
| 2 | 69 | Samsara — Data Engineer | Remote - US |
| 3 | 48 | Spotify — Backend Engineer - Data Infrastructure | New York, NY |
| 4–6 | 40 | Databricks — Senior Software Engineer - Distributed Data Systems (×3) | San Francisco · Mountain View · Bellevue |
| 7 | 32 | Palantir — Data Engineer - Talent Acquisition Operations | New York, NY |
| 8 | 32 | Zoox — Software Engineer - Pipeline Infrastructure & Integration | Foster City, CA |
| 9 | 24 | Zoox — Contract Student Worker - Data Analyst (Part-time) | Foster City, CA |
| 10 | 16 | Palantir — Backend Software Engineer - Data Connectors | New York, NY |

Scores are out of 100: 8 per distinct skill (at most 8 skills), +16 for asking ≤ 3 years, +10 for Boston or +5 for remote US, and
+10 if the posting offers visa sponsorship. None of the ten mentions sponsorship, so every visa claim is "I cannot tell from the
posting".

## Relevance is not entailment

**Spotify, "Backend Engineer - Data Infrastructure" (#3).** Four of Evan's skills appear in the text (AWS, BigQuery, Snowflake,
Terraform), and they earn 32 of its 48 points. None of them is required:

- *"curious about analytical databases and technologies such as Apache Druid, ClickHouse, Pinot, BigQuery, or Snowflake"*
- *"You've worked with, or are interested in learning, infrastructure technologies such as Kubernetes, Terraform, and cloud platforms
  like Google Cloud Platform or AWS"*

The posting is relevant by the filter's words, but all four claims "requires AWS / BigQuery / Snowflake / Terraform" are
**insufficient**. The checker labeled them correctly.

## Checking the labels themselves

Claude checked all 46 claims of the v1.2 shortlist against the posting text at my direction. **10 of 46 labels are wrong (22%):**

| Error | Claims | Example span |
|---|---|---|
| **Over-support:** a list of alternatives read as requiring each item | Samsara #1: Airflow, Python, Scala, Terraform; Samsara #2: Airflow | *"Proficiency in at least one production programming language such as Go, Python, Scala, or Java"* → labeled supported for both Python and Scala |
| **Over-support:** a "nice to have" line read as required | Samsara #1: Databricks | *"An ideal candidate also has: Experience with Databricks, Delta Lake…"* |
| **Under-support:** a real requirement missed, because list items with no full stops run together into one "sentence" that also holds a preference word | Samsara #1: AWS; Palantir: Python; Zoox student: Python, SQL | *"Required Qualifications Strong proficiency in SQL, PySpark, Python in production environments"* → labeled insufficient |

So the checker repeats wrong version 6 ("a word counts as support") in a form my test did not cover: "Python a plus" is caught, but
"such as Go, Python, Scala, or Java" is not. The 39 new claims in v1.3 were not checked one by one. The first new posting already shows
the same error: *"5+ years of production level experience in either Java, Scala or C++"* is labeled as supporting "requires Scala".

### My own spot-check of Claude's check (`audit/claim_spotcheck.csv`)

The 10-of-46 figure was Claude judging Claude's checker. On 2026-11-25 I judged 4 of those claims myself: 3 that Claude called wrong
and 1 it called right. For each I was shown the claim, the checker's label and the posting sentence.

| Claim | Checker | Claude | Me (final) |
|---|---|---|---|
| "requires Python": *"at least one … such as Go, Python, Scala, or Java"* | supported | wrong | **wrong** |
| "requires Databricks": *"An ideal candidate also has: Experience with Databricks…"* | supported | wrong | **right** |
| Palantir "requires Python": *"Expertise in Python and data manipulation…"* | insufficient | wrong | **wrong** |
| "requires SQL": *"Expertise in SQL, Python, and working with REST APIs."* | supported | right | **right** |

I confirmed 2 of the 3 errors Claude claimed, and the one correct label. On Databricks I disagree with Claude. That verdict also
conflicts with my own FILTER.md §2 rule ("a plus" does not support "requires"), so the rule and my judgment differ on "ideal candidate
also has", and the 10-of-46 figure is at best 9 of 46 by my reading.

What this spot-check can't show:
- **The first round wasn't independent.** I first marked all four "checker is right". I changed claims 1 and 3 only after Claude
  pointed to my §2 rule and asked again, so the second round was steered.
- **The order of the options may have mattered.** In both rounds every answer I picked was the first option listed.
- **The sample is small.** Four claims checked by hand is a spot-check, not an error rate.

## The abstention rule and its counterexample

**Rule** (FILTER.md §2): when a field a claim needs is missing, the agent says "I cannot tell from the posting", names the field, and
does not guess. This applies to a location with no country, no years phrase, no description, or a posting that never mentions
sponsorship.

**Where it is right.** The Zoox student posting states no years of experience, so the claim "requires at most 5 years" is
*"I cannot tell from the posting: it states no years of experience (field: description)"*. That is correct.

**Where it gives the wrong answer.** Three Spotify postings, "Backend Engineer - Data Platform" (two of them) and "Senior Data Engineer -
Data Platform", have the locations **"Stockholm"** and **"London"**. These name no country, so F3 abstains and the postings land in
"cannot tell" instead of "rejected". Any reader knows they are in Sweden and the UK, so abstaining here is wrong. The rule cannot tell
a missing fact from an obvious one. A list of non-US cities would fix these three, but it would be a hand-made list, like the US list
in JS1.
