# FILTER.md — Job-Search Agent 3

*The student's filter, v0.1. The student sent it in the chat on 2026-11-24 at about 17:25 EST and answered "I wrote both myself" (FILTER.md and Frictional entry 1). Claude Code saved it here: the headings and the tab-separated tables became Markdown. No words were changed.*

## The filter

I started with the JS1 screening rule I carried into Assignment 7. On November 21, that rule rejected all 172 new postings. For this version, I want a generic title like “Software Engineer” to pass when the description gives me a concrete reason to consider it for Alex Morgan, my fictional applicant targeting early-career ML, AI systems, and data infrastructure roles.

| Rule | Decision | Reason |
| --- | --- | --- |
| Role | Require engineer or developer in the title. Give a matching title 1 point. | A generic engineering title can still describe relevant work. |
| Level | Reject titles containing senior, sr, staff, principal, lead, manager, director, head, intern, or internship. | I’m screening for early-career jobs. A senior title fails this screen, while a senior colleague mentioned in the description has no effect. |
| Topic in title | Add 2 points for machine learning, ml, ai, inference, model serving, data engineer, data platform, or data infrastructure. | The title gives the strongest signal about the role’s focus. |
| Topic in description | If the title earns no topic points, add 1 point for machine learning, model inference, model serving, ml infrastructure, data pipeline, data pipelines, or data platform. | Specific phrases can establish a reason to review a generic title. A lone mention of AI in hiring boilerplate earns zero. |

Decode HTML, lowercase the text, and match whole words or consecutive word sequences. Keep postings that pass the role and level rules and score at least 2. Rank by descending score, then by board identifier and posting key. I set the weights and cutoff by hand for v0.1. The cutoff requires both an engineering title and a topic match. Repeating a term earns no extra points.

I dropped the Python-plus-one-skill gate because a relevant role can use a different stack. I also dropped the fixed city list. An explicit U.S. work location fits the search. A posting limited to locations outside the U.S. falls out of scope. Remote by itself leaves the country unresolved, so the agent keeps it visible for review.

## The evidence rules

Each shortlist entry can make separate claims about the work, the location, whether the role accepts new graduates, each minimum or preferred qualification, and what the employer says about work authorization or sponsorship for that role. For each claim, record the board, posting key, source field, capture date, and exact quote from the saved posting.

| Label | When it applies |
| --- | --- |
| Supported | The passage states the claim for this role and preserves any conditions, exceptions, or alternatives. I mark it supported after reading the original passage in context. |
| Contradicted | The passage directly conflicts with the claim. “Five years preferred” contradicts a claim that this line sets a five-year minimum. |
| Insufficient | The text leaves the claim unresolved. Record what is missing and say “I cannot tell.” |
| Not reviewed | The agent found a potential quote and I still need to check its meaning. |

If the posting is silent about sponsorship, the agent says “I cannot tell whether this role offers sponsorship.” A verbatim quote can still support the wrong conclusion if the agent drops a qualifier like preferred. A fixed phrase check can also miss clear wording such as “We sponsor H-1B visas for this role.” I’ll check the full clause, including any or that changes how a requirement can be met.

## The expected sources

Assignment 7 authorized these public employer postings through the configured read-only feeds. Chapter 7 calls for your own dated count prediction before the first JS3 collection. The prior totals give you a reference for that prediction.

| Assignment 7 source | Owner | Nov 8 total | Nov 21 total | Expected JS3 total |
| --- | --- | ---: | ---: | --- |
| Greenhouse anthropic | Anthropic | 675 | 635 | 635 (added 2026-11-24, see below) |
| Greenhouse databricks | Databricks | 922 | 895 | 895 (added 2026-11-24, see below) |
| Ashby linear | Linear | 32 | 32 | 32 (added 2026-11-24, see below) |

Read Greenhouse id, title, location.name, and content, and Ashby jobUrl, title, location, and descriptionHtml. Use jobUrl as an identifier. Keep the board name and capture time with each record.

If a board fails or returns an unusable payload, report its count as unknown and name the failure. A blank location leaves the work location unresolved unless the description establishes it. If the normalized description is blank, retain any title-based match, abstain on description-based claims, and leave any unresolved topic decision open for review.

## Wrong versions

| Wrong version | Case that should catch it |
| --- | --- |
| Keep the old Python-plus-one-skill gate. | Software Engineer, Model Serving lists Go and gRPC. Keep it with score 3. |
| Look for topics only in titles. | Software Engineer says “Build model serving systems.” Keep it with score 2. |
| Count any mention of AI in the description. | Software Engineer, Internal Tools says “We use AI to schedule interviews.” Reject it with score 1. |
| Treat an exact quote as sufficient evidence. | A posting says “Five years preferred.” The claim “Five years are required” must come back contradicted. |

## Additions before the build (2026-11-24, before any code and before the JS3 collection)

At about 17:30 EST, Claude Code asked four questions about gaps in v0.1. The answers are the student's.

**Expected totals.** The student's words, as typed:

> November 24, 2026 · Before collection
>
> I expect 635 Anthropic postings, 895 Databricks postings, and 32 Linear postings. The last run found 83 previously unseen Anthropic postings even as its board total fell by 40. With only two snapshots, I’m using the latest totals as my baseline and will record actual minus expected for each board I can verify.

**Which words make a location U.S.** The student chose "Country or state", one of two options Claude Code wrote. The option, in Claude Code's words: "U.S. if it says United States, USA, US or U.S., or names a U.S. state, in full or as a 2-letter code ('San Francisco, CA'). Outside if it names only other countries. Remote, regions or a bare city go to review. Risk: CA can mean Canada, IN India." Both options said that a posting with any U.S. location counts as U.S. The other option was "Country words only".

**Shortlist size.** The student chose 8 postings. The options were 5, 8 and 10.
