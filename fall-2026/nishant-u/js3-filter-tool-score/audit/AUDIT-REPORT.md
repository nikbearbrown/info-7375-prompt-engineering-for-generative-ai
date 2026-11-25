# Reject audit report — FILTER.md v1, and the v2 changes it led to

Comparison computed by Claude Code on 2026-11-25 from Nishant's committed verdicts (`audit/audit.csv`, commit `b8b0a20`) and the v1 filter's (`out3/filter-run/results.json`, commit `8e759bf`). The decisions on the proposed changes are Nishant's (2026-11-25), recorded in FILTER.md (commit `b68e605`). FILTER.md v2 was implemented and run in commit `fb071b5`.

## Inputs

- **Filter:** FILTER.md v1, run over 182 unique postings saved by the JS2 loop: 16 accepted, 166 rejected (F1 144, F2 9, F3 8, F4 5), 0 abstained.
- **Audit sample (seed 20261124, `audit/make_kit.py`):**
  - 30 drawn uniformly from all 166 rejects;
  - 5 close calls (rejects not in the 30 that fail exactly one rule: 4 only-F4, 1 only-F2);
  - 10 drawn from the 16 accepts.
- **Judgment rule:** AUDIT-RULE.md (`f308043`), applied by Nishant.
- **Agreement:** "agree" means the filter accepted and Nishant said yes, or the filter rejected and Nishant said no.

## Summary

| Group | n | Agree | Disagree | Disagreements |
| --- | ---: | ---: | ---: | --- |
| Random rejects | 30 | 27 | 3 | rows 10, 28, 30 (filter misses) |
| Close calls | 5 | 0 | 5 | rows 4, 8, 27, 35, 44 (filter misses) |
| Accepts | 10 | 10 | 0 | none |
| **All** | **45** | **37** | **8** | all 8 are rejects Nishant would show Priya; no false accepts |

## Random rejects: what the sample can and cannot say

- **Observed:** Nishant judged **3 of the 30** random rejects relevant (rows 10, 28, 30). These are postings the filter wrongly withheld. That is a rate of **10.0%** in the sample.
- **95% Clopper-Pearson interval:** **2.1% to 26.5%**.
- **What it means for the 166 rejects:** if the 30 are a fair draw, and they were drawn uniformly at random, the share of the 166 rejects that Nishant would want Priya to see is plausibly anywhere from about 2% to 27%. That is roughly **4 to 44 postings**, with 17 as the point estimate.
- **What it does not mean:**
  - It is a **sample estimate, not a measured rate.** The other 136 rejects were not judged.
  - The interval is wide because 30 is a small sample.
  - It describes these 166 postings from three boards collected on 2026-11-10, judged by one person under one rule. It says nothing about other boards, other dates, or another reader's rule.
  - It cannot say which of the unjudged 136 are misses.
  - It does not estimate false accepts: the 10 accepts were judged, but they are not part of this rate.

## Close calls and accepts (not random, so no rate)

These groups were chosen on purpose: the close calls are the rejects nearest the boundary, and the accepts are a sample of 10 of 16. Neither supports a rate for its pile.

- **Close calls: 5 of 5 disagree.** All five are rejects Nishant would show Priya.
  - **Row 4** failed F2 on the word "Lead".
  - **Rows 8, 27, 35 and 44** each failed only F4, because none of the 10 shipped skills is named. All four are Senior Applied AI/ML Scientist roles that ask for "Strong programming skills" without naming a language.
- **Accepts: 0 of 10 disagree.** Nishant judged all 10 sampled accepts relevant. The 6 accepts outside the sample were not judged.

## False friends

A false friend is a word that matched or blocked a posting for the wrong reason. These are the disagreements, plus agreements where a word came close to doing so.

### Confirmed: a word changed the verdict wrongly

1. **"Lead" blocked an individual-contributor role (row 4, F2).** This is the clearest false friend.
   - Title: *Strategy & Analytics Senior Lead - Multiple Openings*.
   - Filter: `F2 [title]: excluded word 'Lead'`.
   - Posting: "This is an ideal role for someone who wants to work as a high-impact individual contributor".
   - Nishant's note: "Possible false friend: the title says 'Lead', but the description describes an individual-contributor role."
2. **"Manager" in a title for individual analysis work (row 10).**
   - Title: *Insights Manager II, Retail Insights*.
   - The filter rejected it at F1 (no role word), but F2 would also have blocked it on "Manager".
   - Posting: "We're hiring an Insights Manager II to serve as the analytical backbone for a portfolio of key grocery retail partners".
   - Nishant's note: "Possible false friend: 'Manager' appears in the title, but the work is individual analysis."
3. **"Software Engineer" hiding ML work (row 30, F1 blocked by absence).**
   - Title: *Senior Software Engineer II - Ads Quality*.
   - Filter: `F1 [title]: no role word`.
   - Posting: "As a Senior Software Engineer II in the Ads Quality team specializing in ML infrastructure".
   - Nishant's note: "Possible false friend: the title says 'Software Engineer' but hides an ML role."
4. **"Lead" in a strategy title (row 28).**
   - Title: *Strategy & Operations Senior Lead*.
   - The filter rejected it at F1, because the title has no role word. "Lead" would also have blocked it at F2.
   - Posting: "This is an ideal role for someone who wants to work as a high-impact individual contributor"; "own the forecasting, business intelligence, and go-to-market strategy".
   - Nishant's note: "Possible false friend: the title says 'Lead', while the text describes an individual contributor."

### Near misses: the verdict was right, but the word could mislead

- **"AML" (row 11, agreed).**
  - Title: *Director, Financial Crimes Compliance - AML Officer*.
  - Posting: "owns the BSA/AML program".
  - Nishant's note: "'AML' here means anti-money laundering, not machine learning."
  - Whole-word matching did not count "ML" inside "AML". A substring matcher (FILTER.md wrong version 1) would have, so this is a real-data case for that mutant.
- **"Ads Manager" (rows 1 and 13, agreed).**
  - "Ads Manager" is a product name. Nishant's note on row 13: "'Ads Manager' is the product name."
  - Both postings were rejected at F1 first, so F2 never read "Manager". If an Ads Manager posting had a role word, F2 would block it for the wrong reason.
- **"hybrid" in a technical sentence (row 9, claim C4, not the verdict).**
  - The shortlist labels C4 "Remote" as *contradicted* by: "agent + tool + context strategy (preload vs. tool-calling vs. hybrid)".
  - That sentence is about an AI architecture, not a work schedule. The label happens to be right anyway, because the same posting contains Faire's hybrid-work paragraph ("Hybrid Faire employees currently go into the office 3 days per week"). But it quotes the wrong sentence.
  - This shows relevance without entailment: the word matched, but that sentence does not support the claim.

## Proposed rule changes (as measured on v1, before the decisions)

Counts are over Nishant's 45 verdicts. **Fixes** are disagreements the change would turn into agreement. **Breaks** are agreements it would turn into disagreement. **Unaudited** is how many of the other 137 postings would change verdict without any human label on them. Every change was measured by re-running the real `agent3/filter.py` with that one change patched in.

| # | Kind of disagreement | Candidate change to FILTER.md | Fixes | Breaks | Unaudited changes | Claude's suggestion (before the decisions) |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 1 | "Lead" blocks an individual-contributor role | **Cut** "lead" from F2 | 1 (row 4) | 0 | 1 (*Strategy & Analytics Lead - Multiple Openings*) | Candidate to accept; check the one unaudited posting by hand first |
| 2 | Résumé practice named, but no résumé tool | **Add** to F4 the practices on Priya's résumé: "A/B test(s/ing)", "experimentation", "LLM evaluation", "LLM-as-judge" | 4 (rows 8, 27, 35, 44) | 1 (row 15, Staff scientist who will "mentor or manage") | 0 | Candidate to accept, with the row 15 break recorded. These come from her résumé bullets (A/B framework, LLM evaluation), not from the skills list, so FILTER.md must say so |
| 3 | Combined 1 + 2 | Both changes | 5 (rows 4, 8, 27, 35, 44) | 1 (row 15) | 1 | Combined effect; the same caveats apply |
| 4 | "Software Engineer" title hides ML work | **Add** to F1: pass if the posting text says "machine learning" or "ML" (whole word) at least N times | 1 (row 30), for N = 3, 5 or 8 | 0 | 0 | Weak evidence: one case. Choosing N from this one posting would be fitting the threshold to the audit, so pick N before re-auditing |
| 5 | "Manager" in an Insights title | **Add** "insights" to F1 and **cut** "manager" from F2 | 1 (row 10) | 0 | 0 | Cutting "manager" removes a guard that had no test case in this sample. Adding "insights" alone fixes 0, because F2 still blocks. Candidate to reject, or accept only with new tests for "Data Science Manager"-type titles |
| 6 | Strategy-titled individual-contributor analytics role | **Add** to F1: pass if the title contains "Strategy" and the text says "individual contributor" and names SQL | 1 (row 28) | 1 (row 38, *Strategy & Operations Senior Associate*, judged no) | 1 (*Strategy & Operations Senior Lead, Brand Growth*) | **Reject**: it trades one error for another and is tailored to one title family |
| 7 | F3 rejects Poshmark US office locations (`US California (Redwood City) - Office`) | **Add** to F3: a part beginning with "US " counts as US | 0 | 0 | not measured here | No audit evidence either way: every sampled Poshmark US posting failed F1 first. Decide on the FILTER.md text, not on this audit |
| 8 | "hybrid" in a technical sentence (C4 label) | Read C4's "hybrid" only near "office", "days" or "schedule" | 0 verdicts (a claim label, not relevance) | 0 | — | Optional; affects shortlist quotes only |

**Things the counts do not show:**
- **The fixes are on the sample that suggested them.** Measuring a change on the same 45 verdicts that motivated it overstates how well it works. A fair check needs postings not used to design the rule, such as a fresh random sample of rejects after the change.
- **Breaks can be hidden.** The unaudited column shows how many unlabelled verdicts would move, not whether those moves are right.

## Decisions (Nishant U, 2026-11-25)

| # | Decision | Reason |
| --- | --- | --- |
| 1 | **ACCEPT**: cut "lead" from F2 | "Lead" often marks a senior individual contributor, not a people manager (row 4). |
| 2 | **ACCEPT**: F4 also counts Priya's résumé practices (A/B testing, experimentation, LLM evaluation, LLM-as-judge) | Her skills include practices, not only tool names. Row 15 becomes a known miss because the filter can't see managing duties. |
| 4 | **REJECT**: F1 passes on an ML-count threshold | One case, and N would be a guess. |
| 5 | **REJECT**: add "insights" to F1 and cut "manager" from F2 | Would let real managers through. |
| 6 | **REJECT**: strategy title + "individual contributor" + SQL passes F1 | Swaps one error for another. |
| 7 | **ACCEPT**: "US <State> (<City>) - Office" counts as US in F3 | A parsing bug. |
| 8 | **ACCEPT**: C4 reads "hybrid" as contradicting Remote only near office, day(s) or schedule words | The "hybrid" false friend. |

Change 3 was changes 1 and 2 together, not a separate decision.

## Result: v1 vs v2 over all 182 postings

| | v1 | v2 |
| --- | ---: | ---: |
| Accepted | 16 | 23 |
| Rejected F1 | 144 | 144 |
| Rejected F2 | 9 | 7 |
| Rejected F3 | 8 | 8 |
| Rejected F4 | 5 | 0 |
| Abstained | 0 | 0 |

**Seven verdicts changed, all from reject to accept:**

| Posting | Title | Changed by | Audit |
| --- | --- | --- | --- |
| `greenhouse:faire:8396231002` | Strategy & Analytics Senior Lead - Multiple Openings | change 1 (no "lead" exclusion) | row 4: yes, now agrees |
| `greenhouse:faire:8623235002` | Strategy & Analytics Lead - Multiple Openings | change 1 | **not audited** |
| `greenhouse:faire:8832899002` | Senior Applied AI/ML Scientist - Retailer Growth | change 2 ("experimentation") | row 8: yes, now agrees |
| `greenhouse:faire:8845103002` | Senior Applied AI/ML Scientist - Marketplace Quality | change 2 ("experimentation", "LLM evaluation") | row 27: yes, now agrees |
| `greenhouse:faire:8831888002` | Senior Applied AI/ML Scientist - Listing Quality | change 2 ("experimentation", "LLM evaluation", "LLM-as-judge") | row 35: yes, now agrees |
| `greenhouse:faire:8801507002` | Senior Applied AI/ML Scientist - Brand Growth | change 2 ("experimentation") | row 44: yes, now agrees |
| `greenhouse:faire:8747498002` | Staff Applied AI/ML Scientist | change 2 ("experimentation") | row 15: no, **now disagrees** (the accepted known miss) |

What the other two accepted changes did:
- **Change 7** changed no verdicts. Every Poshmark "US <State> (<City>) - Office" posting in the data fails F1 before F3 is read.
- **Change 8** changed no verdicts and no C4 labels. It changed one C4 quote: `faire:8610263002` (row 9) was quoted from "preload vs. tool-calling vs. hybrid" and is now quoted from "Hybrid Faire employees currently go into the office 3 days per week…". The label stays *contradicted*.

**On the 45 audited postings:** v1 agreed with Nishant on 37 and v2 agrees on 41. v2 fixes rows 4, 8, 27, 35 and 44, breaks row 15, and leaves rows 10, 28 and 30 as misses.

**The fix counts overstate the improvement.** The changes were proposed from these same 45 verdicts, and then measured on them. A rule designed to fix the cases you are looking at will look better on those cases than on new ones. "41 of 45" is therefore not evidence that v2 is better in general. To test v2 fairly, a fresh random sample of v2 rejects (and accepts) would be needed: postings not used to choose the changes, judged before seeing v2's reasons. That has not been done. In particular:
- The miss estimate for the reject pile (3 of 30, 95% CI 2.1%–26.5%) describes **v1**, not v2.
- The one unaudited change (`faire:8623235002`) has no human judgment.

## Not checked

- **The 136 unjudged rejects and the 6 unjudged accepts.**
- **A second judge.** There is no inter-rater check: one reader, one rule.
- **Shortlist claim labels.** C1–C4 were not audited here, apart from the C4 "hybrid" observation.
- **Whether AUDIT-RULE.md is the right rule.** Seniority (most yes postings ask for 3–10+ years) is outside it, by design.

## All 45 postings

| # | Title | Group | Filter verdict | Filter reason | My verdict | My note | Agree? |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sr Software Engineer II - Ads Manager (Front End) | reject | reject | F1 [title]: no role word in 'Sr Software Engineer II - Ads Manager (Front End)' | no | Its a front-end role focused on designing, building, and maintaining high-quality React user interfaces; based in Canada (remote), not the US. Possible false friend: 'Ads Manager' refers to the product name, not a people-management title. | agree |
| 2 | Senior Machine Learning Engineer, Operations Research | accept | accept | accept: role word 'Machine Learning', no excluded word, US part 'United States - Remote', skills Python, SQL | yes | Its an ML engineering role involving designing, developing, and deploying machine learning solutions; requires strong Python programming and fluency in data manipulation with SQL and Pandas; US remote. | agree |
| 3 | Staff Software Engineer, Web | reject | reject | F1 [title]: no role word in 'Staff Software Engineer, Web' | no | A web engineering role responsible for creating web application features, not a data/ML role; AWS appears only among desirable web technologies. | agree |
| 4 | Strategy & Analytics Senior Lead - Multiple Openings | close | reject | F2 [title]: excluded word 'Lead' in 'Strategy & Analytics Senior Lead - Multiple Openings' | yes | Its an analytics role for a high-impact individual contributor using SQL or Excel to analyze large datasets; based in San Francisco or New York and requiring 8+ years. Possible false friend: the title says 'Lead', but the description describes an individual-contributor role. | **DISAGREE** |
| 5 | Senior Software Engineer II, Ads Data Solutions Engineering | reject | reject | F3 [location.name]: no US part in 'Canada - Remote (ON, AB, BC, or NS Only)' | no | Data engineering work in Python, Databricks, SQL, and AWS, which match her skills, but the role is Canada-remote (CAN $196,000–$207,000 CAD), not US-based. | agree |
| 6 | Principal Computer Vision Engineer | reject | reject | F1 [title]: no role word in 'Principal Computer Vision Engineer' | no | Computer-vision/ML work in Python, but based in Israel on a hybrid schedule requiring 3 days a week in the office, not in the US. | agree |
| 7 | Senior Product Marketing Manager | reject | reject | F1 [title]: no role word in 'Senior Product Marketing Manager' | no | A product marketing role focused on building and owning an end-to-end go-to-market strategy, not a data/ML role. | agree |
| 8 | Senior Applied AI/ML Scientist - Retailer Growth | close | reject | F4 [content]: none of the 10 shipped skills named | yes | Applied ML work designing and implementing ML solutions without supervision, including experimentation and causal inference; based in San Francisco. It names no specific resume tool, only 'strong programming skills', but the LLM and experimentation work aligns with her A/B testing and LLM-evaluation experience. | **DISAGREE** |
| 9 | Senior Applied AI/ML Scientist - Compass | accept | accept | accept: role word 'Scientist', no excluded word, US part 'New York City, NY', skills Python | yes | A deeply hands-on individual-contributor role with no direct reports; its LLM evaluation work - offline evaluation suites, LLM-as-judge metrics - and the FLARE Python app match her resume; based in San Francisco or New York. | agree |
| 10 | Insights Manager II, Retail Insights | reject | reject | F1 [title]: no role word in 'Insights Manager II, Retail Insights' | yes | An analytics role despite the title, serving as the analytical backbone and requiring strong SQL skills; US remote, with no direct reports mentioned. Possible false friend: 'Manager' appears in the title, but the work is individual analysis. | **DISAGREE** |
| 11 | Director, Financial Crimes Compliance - AML Officer | reject | reject | F1 [title]: no role word in 'Director, Financial Crimes Compliance - AML Officer' | no | A compliance director role owning and maintaining Poshmark's BSA/AML program, focused on program leadership rather than data/ML. Possible false friend: 'AML' here means anti-money laundering, not machine learning. | agree |
| 12 | Senior Applied ML/AI Scientist - Search | accept | accept | accept: role word 'Scientist', no excluded word, US part 'New York City, NY', skills Python | yes | Applied ML for search ranking, requiring strong programming skills in Python, Java, or an equivalent language, plus A/B testing; US pay range, based in San Francisco or New York. | agree |
| 13 | Senior Software Engineer - Ads Manager | reject | reject | F1 [title]: no role word in 'Senior Software Engineer - Ads Manager' | no | A backend role building backend services and APIs in a modern web framework such as Ruby on Rails or Go; based in Canada (pay in CAD). Possible false friend: 'Ads Manager' is the product name. | agree |
| 14 | Senior SOX Manager - Business Processes | reject | reject | F1 [title]: no role word in 'Senior SOX Manager - Business Processes' | no | A SOX compliance management role covering SOX compliance and internal audit, not a data/ML role. | agree |
| 15 | Staff Applied AI/ML Scientist | reject | reject | F4 [content]: none of the 10 shipped skills named | no | An ML scientist role, but one with lead/manager responsibilities - acting as a pod lead and mentoring or managing Senior Applied AI/ML Scientists - so it is not purely individual-contributor work; borderline. Possible false friend: the title contains no manager wording, yet the work includes managing. | agree |
| 16 | Senior Applied AI/ML Scientist - Search Ranking | accept | accept | accept: role word 'Scientist', no excluded word, US part 'San Francisco, CA', skills Python | yes | Applied ML for search ranking, requiring strong programming skills in Python, Java, or an equivalent language, plus A/B testing; based in San Francisco, CA. | agree |
| 17 | Product Manager, Ad Formats | reject | reject | F1 [title]: no role word in 'Product Manager, Ad Formats' | no | A product manager for ad formats requiring 4+ years of product management experience, not a data/ML role. | agree |
| 18 | Head of Paid Marketing | reject | reject | F1 [title]: no role word in 'Head of Paid Marketing' | no | A marketing leadership role leading a dedicated team of paid marketers, not a data/ML role. | agree |
| 19 | HR Business Partner | reject | reject | F1 [title]: no role word in 'HR Business Partner' | no | An HR business partner role requiring 3–5 years of HRBP experience, not a data/ML role. | agree |
| 20 | Director, AI Solutions Strategy & Planning | reject | reject | F1 [title]: no role word in 'Director, AI Solutions Strategy & Planning' | no | A go-to-market strategy director role for a dedicated strategy and planning leader, not a data/ML role. | agree |
| 21 | Manager, Digital Design | reject | reject | F1 [title]: no role word in 'Manager, Digital Design' | no | A design management role managing and mentoring a small team of creatives, not a data/ML role. | agree |
| 22 | Live E-Commerce Digital Host | reject | reject | F1 [title]: no role word in 'Live E-Commerce Digital Host' | no | An on-camera sales hosting role hosting live shopping shows on site, not a data/ML role. | agree |
| 23 | Bilingual Customer Experience T3 Specialist (Spanish) | reject | reject | F1 [title]: no role word in 'Bilingual Customer Experience T3 Specialist (Spanish)' | no | A customer service role handling real-time calls and occasionally emails, not a data/ML role. | agree |
| 24 | International Strategy and Operations Lead | reject | reject | F1 [title]: no role word in 'International Strategy and Operations Lead' | no | An analytics role where SQL experience is strongly preferred, but based out of the London, UK office, not the US. Possible false friend: the title says 'Lead', while the text describes an individual contributor. | agree |
| 25 | Senior Sales Engineer | reject | reject | F1 [title]: no role word in 'Senior Sales Engineer' | no | A sales engineering role guiding customers through the sales cycle, not a data/ML role. | agree |
| 26 | Staff Software Engineer,  Data Governance & Foundations | accept | accept | accept: role word 'Data', no excluded word, US part 'United States - Remote', skills Python, SQL, Databricks, Delta Lake, AWS | yes | Data-platform engineering using Databricks, Confluent, Airflow, dbt, Delta Lake, Scala, Python, Postgres, and AWS; US remote; requires 10+ years. | agree |
| 27 | Senior Applied AI/ML Scientist - Marketplace Quality | close | reject | F4 [content]: none of the 10 shipped skills named | yes | Applied ML work owning applied ML projects end to end; building and validating LLM evaluation pipelines matches her evaluation work; based in San Francisco. It names no specific resume tool, only 'strong programming skills'. | **DISAGREE** |
| 28 | Strategy & Operations Senior Lead | reject | reject | F1 [title]: no role word in 'Strategy & Operations Senior Lead' | yes | A high-impact individual-contributor role owning forecasting and business intelligence, requiring strong proficiency in Excel and SQL; requires 8+ years; borderline between strategy and analytics. Possible false friend: the title says 'Lead', while the text describes an individual contributor. | **DISAGREE** |
| 29 | Senior Global Mobility and Immigration Specialist | reject | reject | F1 [title]: no role word in 'Senior Global Mobility and Immigration Specialist' | no | An immigration specialist role requiring 7+ years of US business immigration experience, in HR/legal rather than data/ML. | agree |
| 30 | Senior Software Engineer II - Ads Quality | reject | reject | F1 [title]: no role word in 'Senior Software Engineer II - Ads Quality' | yes | ML infrastructure work specializing in ML infrastructure, using Python and Go, along with expertise in data manipulation using SQL, Spark, and Pandas; US remote. Possible false friend: the title says 'Software Engineer' but hides an ML role. | **DISAGREE** |
| 31 | Senior Analytics Engineer - Retailer Growth | accept | accept | accept: role word 'Analytics', no excluded word, US part 'San Francisco, CA', skills Python, SQL | yes | Analytics engineering requiring production-level development experience in Python and strong SQL skills; based in San Francisco, CA. | agree |
| 32 | Lifecycle Marketing Coordinator, CRM | reject | reject | F1 [title]: no role word in 'Lifecycle Marketing Coordinator, CRM' | no | Its a CRM campaign coordination role building, QA-ing, and launching campaigns; based in Canada (pay in CAD), not a data/ML role. | agree |
| 33 | Senior Applied ML/AI Scientist - Search | accept | accept | accept: role word 'Scientist', no excluded word, US part 'New York City, NY', skills Python | yes | Applied ML for search, requiring strong Python and a test-led approach - letting A/B tests, not opinions, settle what works; US pay range, based in San Francisco or New York. | agree |
| 34 | Deal Desk Specialist | reject | reject | F1 [title]: no role word in 'Deal Desk Specialist' | no | Its A deal desk / sales finance role requiring an understanding of quote-to-cash processes; based in Canada, not a data/ML role. | agree |
| 35 | Senior Applied AI/ML Scientist - Listing Quality | close | reject | F4 [content]: none of the 10 shipped skills named | yes | Applied ML work owning applied ML projects end to end; building LLM-as-judge and human-in-the-loop evaluation systems matches her evaluation work; based in San Francisco. It names no specific resume tool. | **DISAGREE** |
| 36 | Staff Data Infrastructure Engineer | accept | accept | accept: role word 'Data', no excluded word, US part 'New York City, NY', skills Python, SQL, Databricks, AWS | yes | A hands-on data infrastructure role using Databricks, with strong SQL, solid Python, and AWS; based in San Francisco or New York, at a senior level involving setting direction for it. | agree |
| 37 | Growth Platform, Marketing Engineer | reject | reject | F1 [title]: no role word in 'Growth Platform, Marketing Engineer' | no | Software engineering inside marketing, using Kotlin, Java, JUnit, React, and Next.js, with SQL only in a supporting role; borderline. | agree |
| 38 | Strategy & Operations Senior Associate | reject | reject | F1 [title]: no role word in 'Strategy & Operations Senior Associate' | no | The core of the role is go-to-market strategy - defining and building the go-to-market strategy - with SQL listed; borderline between strategy and analytics. | agree |
| 39 | Sr. Manager, Product Marketing (Posh Live) | reject | reject | F1 [title]: no role word in 'Sr. Manager, Product Marketing (Posh Live)' | no | Its a senior product marketing management role requiring 5–8 years of product marketing experience, not a data/ML role. | agree |
| 40 | Senior Software Engineer II, Machine Learning | reject | reject | F3 [location]: no US part in 'IN Tamil Nadu (Chennai) - Office' | no | ML engineering in Python, SQL, MLflow, and Databricks, which match her skills, but the office is in Tamil Nadu (Chennai), India, not the US. | agree |
| 41 | Senior Product Manager, Instacart Business - Growth | reject | reject | F1 [title]: no role word in 'Senior Product Manager, Instacart Business - Growth' | no | It’s a product management role for growth requiring 5+ years of product management experience, not a data/ML role. | agree |
| 42 | Senior HRBP & Strategic Projects Lead | reject | reject | F1 [title]: no role word in 'Senior HRBP & Strategic Projects Lead' | no | An HR business partner role for a UK-based HR leader, not a data/ML role and not US-based. | agree |
| 43 | Senior Finance Analytics Engineer | accept | accept | accept: role word 'Analytics', no excluded word, US part 'New York City, NY', skills Python, SQL | yes | Analytics engineering requiring expert-level SQL and working proficiency in Python; based in San Francisco or New York. | agree |
| 44 | Senior Applied AI/ML Scientist - Brand Growth | close | reject | F4 [content]: none of the 10 shipped skills named | yes | Applied ML work owning applied ML projects end to end, including experimentation and causal inference; based in San Francisco. It names no specific resume tool, only 'strong programming skills'. | **DISAGREE** |
| 45 | Senior Product Analytics Engineer - Ads | accept | accept | accept: role word 'Analytics', no excluded word, US part 'San Francisco, CA', skills Python, SQL | yes | Analytics engineering requiring production-level development experience in Python and strong SQL skills; based in San Francisco; mentoring only. | agree |
