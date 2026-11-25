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

## Addition before the reject audit and before any tuning (2026-11-24, about 17:50 EST)

**The held-out set (Chapter 9).** The student chose "15 kept + 15 rejected", one of three options Claude Code wrote. The option, in Claude Code's words: "Random 15 from the 42 kept or review, and 15 from the 1,509 rejected. Tests both sides. The 50/50 mix isn't the corpus mix, so agreement isn't a rate for all postings." The other options were 30 at random from all 1,551 postings, and 30 at random from the 138 that pass the role and level rules. The 30 are drawn once, with a fixed seed, before any rule changes, and are never used to change a rule.

## After the reject audit, before any held-out label was scored (2026-11-24, about 19:35 EST)

Claude Code compared v0.1 with the 50 development labels (`audit/v0.1/DEV-COMPARISON.md`; the two held-out groups are not in it) and asked four questions. The answers are the student's. Every option's wording is Claude Code's.

**The one change in v0.2.** The student chose "Experience-minimum rule": "Reject when the description sets a minimum of 3+ years that is not marked preferred. Dev (quick count): fixes P25, P44, P46, P56, P71; costs no Yes. About 28 of 42 still reach Alex." The other options were cutting "ai" from the title topics, adding early-career phrases to the description topics, and no change. Nothing else in v0.1 changes. How the rule decides that a statement sets a minimum, and what "marked preferred" means, is written in `jobwatch/screen.py` and its tests, committed before the held-out comparison runs.

**How a held-out Can’t tell counts.** The student chose "Leave out, scale to 90%": "Score only the Yes and No rows; pass at 90% of them." The other options were "Always a miss" and "Match if shown to Alex". The first part of the bar now reads: at least 90% of the held-out rows labeled Yes or No match the filter's decision (27 of 30, scaled to the rows that can be scored).

**Unmet requirements.** The bar says it didn't work if the reader "clears even one unmet requirement". Asked whether that applies to the filter's held-out decisions, the student chose "Both": "Both the filter's kept held-out rows and the shortlist claims." For the filter, Claude Code's mechanical reading, fixed before the run: a held-out row counts as a cleared unmet requirement when the filter keeps it or holds it for review, the student labeled it No, and the student's reason either states a number of years without the word "preferred" or names a minimum, a requirement, a clearance, new graduates or entry-level applicants. Every other reaching row labeled No is listed with the student's reason and not counted.

**Unchanged:** it didn't work if the filter rejects more than one held-out posting labeled Yes ("wrongly rules out more than one eligible posting"), or if a check misses a deliberate failure.

**False friends.** Asked which false friend the reject audit names, the student chose "Both": "machine learning" matched in descriptions, and "ai" matched in Applied AI titles (`reports/REJECT-AUDIT.md`).
