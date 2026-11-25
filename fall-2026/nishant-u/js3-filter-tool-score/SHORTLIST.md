# SHORTLIST — Job-Search Agent 3 (nishant-u)

The source-grounded shortlist under **FILTER.md v2**, over the 182 unique postings my JS2 loop saved. Generated 2026-11-25 by `python -m agent3.run --filter-version 2` (code at `409b995`).

**Labels are computed, not hand-checked.** `agent3/shortlist.py` labels every claim against the posting's own text. Each label quotes the exact text it rests on, or says "no text found". I have not reviewed each label by hand; the cases below are the ones I examined.

## The full shortlist

Every accepted posting, with all of its claims (C1 US-based, C2 Uses <skill>, C3 Sponsors visas, C4 Remote), each labeled and quoted, is in **[`out3/filter-run-v2/shortlist.md`](out3/filter-run-v2/shortlist.md)**. The labels across the 23 accepted postings:

| Claim | Supported | Contradicted | Insufficient |
| --- | ---: | ---: | ---: |
| C1 US-based | 23 | 0 | 0 |
| C2 Uses <skill> | 38 (one row per skill found) | — (FILTER.md defines none) | — |
| C3 Sponsors visas | 0 | 0 | 23 |
| C4 Remote | 7 | 16 | 0 |

Per posting, in rank order (most supported claims, then fewest contradicted, then posting ID):

| # | Posting | Title | C1 US-based | C2 skills supported | C3 Sponsors visas | C4 Remote |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `greenhouse:instacart:7778693` | Staff Software Engineer,  Data Governance & Foundations | supported | Python, SQL, Databricks, Delta Lake, AWS | insufficient | supported |
| 2 | `greenhouse:instacart:8246054` | Senior Software Engineer II, Ads Data Solutions Engineering | supported | Python, SQL, Databricks, AWS | insufficient | supported |
| 3 | `greenhouse:instacart:8281965` | Senior Software Engineer II, Ads Data Solutions Engineering | supported | Python, SQL, Databricks, AWS | insufficient | supported |
| 4 | `greenhouse:instacart:8372846` | Staff Software Engineer, Ads Data Platform | supported | Python, SQL, Databricks | insufficient | supported |
| 5 | `greenhouse:faire:8806617002` | Staff Data Infrastructure Engineer | supported | Python, SQL, Databricks, AWS | insufficient | contradicted |
| 6 | `greenhouse:instacart:7793089` | Senior Machine Learning Engineer, Operations Research | supported | Python, SQL | insufficient | supported |
| 7 | `greenhouse:instacart:8240305` | Senior Machine Learning Engineer, Fulfillment | supported | Python, SQL | insufficient | supported |
| 8 | `greenhouse:instacart:7793391` | Senior Applied Scientist II, Ads Optimization | supported | Python | insufficient | supported |
| 9 | `greenhouse:faire:8804205002` | Senior Product Analytics Engineer - Ads | supported | Python, SQL | insufficient | contradicted |
| 10 | `greenhouse:faire:8828560002` | Senior Finance Analytics Engineer | supported | Python, SQL | insufficient | contradicted |
| 11 | `greenhouse:faire:8833031002` | Senior Analytics Engineer - Retailer Growth | supported | Python, SQL | insufficient | contradicted |
| 12 | `greenhouse:faire:8396231002` | Strategy & Analytics Senior Lead - Multiple Openings | supported | SQL | insufficient | contradicted |
| 13 | `greenhouse:faire:8610263002` | Senior Applied AI/ML Scientist - Compass | supported | Python | insufficient | contradicted |
| 14 | `greenhouse:faire:8618124002` | Senior Applied ML/AI Scientist - Search | supported | Python | insufficient | contradicted |
| 15 | `greenhouse:faire:8623235002` | Strategy & Analytics Lead - Multiple Openings | supported | SQL | insufficient | contradicted |
| 16 | `greenhouse:faire:8660923002` | Senior Applied ML/AI Scientist - Search | supported | Python | insufficient | contradicted |
| 17 | `greenhouse:faire:8801834002` | Staff Applied Scientist, LTV Modeling | supported | SQL | insufficient | contradicted |
| 18 | `greenhouse:faire:8856357002` | Senior Applied AI/ML Scientist - Search Ranking | supported | Python | insufficient | contradicted |
| 19 | `greenhouse:faire:8747498002` | Staff Applied AI/ML Scientist | supported | — (practice only) | insufficient | contradicted |
| 20 | `greenhouse:faire:8801507002` | Senior Applied AI/ML Scientist - Brand Growth | supported | — (practice only) | insufficient | contradicted |
| 21 | `greenhouse:faire:8831888002` | Senior Applied AI/ML Scientist - Listing Quality | supported | — (practice only) | insufficient | contradicted |
| 22 | `greenhouse:faire:8832899002` | Senior Applied AI/ML Scientist - Retailer Growth | supported | — (practice only) | insufficient | contradicted |
| 23 | `greenhouse:faire:8845103002` | Senior Applied AI/ML Scientist - Marketplace Quality | supported | — (practice only) | insufficient | contradicted |

## Relevance is not entailment

A posting can match the filter's words while its text does not support the claim built on them. A match makes a posting a candidate. Support has to be checked claim by claim against the sentence quoted.

### Case 1: "hybrid" in a sentence about AI architecture (C4 Remote, `faire:8610263002`, audit row 9)

- **v1's evidence for "Remote: contradicted"** was this sentence: "how to leverage Faire's proprietary data, agent + tool + context strategy (preload vs. tool-calling vs. hybrid), and how to measure and raise agent quality as systems gain the ability to act."
- **Why that sentence doesn't support the label:** the word "hybrid" there names an AI design choice, not a work schedule. The label happened to be right, because the same posting also says "Hybrid Faire employees currently go into the office 3 days per week on Tuesdays, Thursdays, and a third flex day of their choosing". But v1 rested it on the wrong sentence.
- **The fix:** FILTER.md v2 change 8 counts "hybrid" only in a sentence that also says office, day(s) or schedule. v2 now quotes the schedule sentence.

### Case 2: a skill named only as "familiarity" under Preferred Qualifications (C2, `instacart:8372846`, *Staff Software Engineer, Ads Data Platform*)

- **What the shortlist says:** "Uses Python: supported" and "Uses Databricks: supported".
- **The only text either label rests on:** "Preferred Qualifications 10+ years of experience Strong background in Scala and functional programming. Familiarity with Snowflake, Databricks, DBT, Airflow, Python, Terraform, and Go."
- **Why that doesn't support the claim:**
  - That is a nice-to-have list of familiarity. It does not say the role's own work uses Python or Databricks.
  - The posting's required qualifications ask for "Spark, ETLs, Distributed System architecture, MapReduce, SQL", and a "Strong background in Scala".
- **What the text actually supports:** "the posting would welcome familiarity with Python and Databricks". The C2 wording, "Uses Python", claims more than the text says.

### Case 3: a skill offered as one option among several (C2, `faire:8660923002` and `faire:8856357002`)

- **What the shortlist says:** "Uses Python: supported".
- **The text it rests on:** "Strong programming skills (Python, Java, or equivalent)".
- **Why that doesn't support the claim:** "or equivalent" means Python is one acceptable option, not a stated requirement of the work.
- **The same pattern elsewhere:** "You can use SQL or Excel to analyze large datasets" (`faire:8396231002`, `faire:8623235002`) supports "SQL is acceptable", not "uses SQL".

### Near miss: "sponsored" that is not about visas (C3)

Every accepted Faire posting contains "Employer-sponsored retirement plan, dependent on country of employment". The C3 patterns correctly ignore it, because "sponsor" there is about a retirement plan. A looser pattern, such as any "sponsor" word, would have turned a benefits line into "Sponsors visas: supported".

## The abstention rule and its counterexample

**The rule (FILTER.md, unchanged in v2):** the agent says "abstain: cannot tell" when the posting text is shorter than 300 characters after removing HTML, or when the board is unverified-empty.

**On the real data:**
- **Short text:** the length test fired **0 times on 182 postings**. The shortest posting is 2,679 characters after removing HTML.
- **Unverified-empty board:** only `greenhouse:poshmark` is unverified-empty, and it abstains at board level with 0 postings.

**Why length is the wrong measure.** Length measures how much text there is, not how much of it is about the job. A long posting can be almost entirely company boilerplate and still tell you nothing about the work.

**Counterexample (CONSTRUCTED: not a real posting).** I built a Greenhouse-shaped posting in four parts:
- title "Data Analyst";
- location "New York City, NY";
- content of two copies of a 422-character generic company paragraph ("Examplemart is a marketplace that connects independent shops… Benefits include health coverage, paid parental leave…");
- one role line between them: "We are hiring a Data Analyst. SQL."

Only 34 of its 880 characters are about the role. I ran the real filter on it, with no changes:

| | Verdict | Abstain | Reason | Text length |
| --- | --- | --- | --- | ---: |
| FILTER.md v1 | accept | False | accept: role word 'Data', no excluded word, US part 'New York City, NY', skills SQL | 880 |
| FILTER.md v2 | accept | False | accept: role word 'Data', no excluded word, US part 'New York City, NY', skills/practices SQL | 880 |

Its claims came out as:
- C1: supported ("New York City, NY");
- C2 "Uses SQL": supported (quote: "SQL.");
- C3: insufficient;
- C4: insufficient.

**What should happen instead:** the honest answer is "cannot tell". The posting states no duties, no level, no team and no requirements beyond one word. The 300-character test passes it because the boilerplate is long. The rule's limit is that it counts characters, not role-specific content.

**Possible repairs (not decided, not applied):**
- measure only the text that remains after removing paragraphs repeated across a company's postings;
- abstain when no sentence describes the work.

Either would need its own wrong-version tests and a measurement.

## C3 "Sponsors visas" is insufficient for every accepted posting

**All 23 accepted postings are "insufficient" on C3.** A check of the posting texts for visa, sponsor, H-1B, work authorization, citizenship and clearance found no visa or work-authorization wording at all. The only hit was the "Employer-sponsored retirement plan" benefits line above.

**What that means:** none of these postings says, in its own text, whether the employer sponsors visas. They are silent, so the shortlist cannot tell Priya, a graduate on OPT, anything about sponsorship from these postings.

**What it does not mean:**
- It does not mean these employers **don't** sponsor. Silence is not "contradicted".
- It does not mean they **do** sponsor. Silence is never "supported"; that is FILTER.md wrong version 2.
- It says nothing about what a recruiter would say, or what the company's careers pages or other postings say. Only each posting's own text was read.

**What to do with it:** sponsorship has to be asked about directly, outside this agent. The shortlist should not be read as screening for it.
