# FRICTIONAL — Job-Search Agent 3

## 2026-11-18: Writing FILTER.md Before Any Code

### What I Am Building

For JS3, I want to improve my previous job-search agent by filtering the postings collected in JS2.

My JS2 agent collected 2,418 unique postings from Databricks, Anthropic, and OpenAI. However, collecting jobs does not mean all of them are suitable for Priya Nair, my fictional candidate.

I want my new filter to identify potentially relevant engineering roles, explain why it selected them, and show when there is not enough information to make a decision.

I wrote FILTER.md Version 1.0 before implementing any JS3 code.

### My Prediction Before Building

I expect my strict experience rule to make the confirmed shortlist quite small, possibly even empty.

I think many postings will go into the review queue because they do not clearly state their required professional experience.

For the reject audit, **I predict that 3 out of 30 randomly selected rejected postings will be jobs I would consider worth reviewing further.**

I chose this prediction because my city lookup may still miss some US locations, as my JS1 filter previously rejected city-only US jobs. Some relevant engineering roles might also use different titles or keywords from the ones I selected.

I also expect **"data" to be a false-friend keyword**, especially in Data Center roles that are not actually about data engineering.

My predictions about the small confirmed shortlist and the false-friend keyword are partly based on Claude's preliminary data check. That check found Data Center roles matching the word "data" and no US candidates in the preliminary filtered group explicitly stating an experience requirement of two years or less.

These are my predictions, not measured results.

### What I Think Could Go Wrong

My first concern is that the filter may reject good jobs because their titles do not contain my chosen role words.

My second concern is that my strict experience rule may prevent suitable entry-level jobs from reaching the confirmed shortlist when the posting does not specify experience.

My third concern is keyword matching. A posting might mention AI, Python, or data without making those skills part of the actual work.

I also think city-only locations could cause incorrect decisions if the location lookup is incomplete.

### After Claude Reviewed Version 1.0

Claude reviewed my FILTER.md and pointed out problems that I had not defined clearly enough.

One important finding was that "AI" appeared in every posting across all three boards during the preliminary check. This means it could give unrelated postings topic points.

Claude also pointed out that experience requirements such as "2+ years," "2–8 years," and multiple requirements in one posting need more precise handling.

I agree that these rules should be clearer before implementation.

I want to preserve Version 1.0 as my original decision and create Version 1.1 with documented changes instead of silently rewriting the original rules.

### What I Will Do Next

I will commit FILTER.md Version 1.0 and this FRICTIONAL entry before implementing the filter.

After that, I will revise the rules in Version 1.1, including boilerplate handling, experience requirements, exact matching phrases, and scoring.

I will record why each rule changed and keep my original predictions unchanged.

Once the filter is implemented, I will compare its results with my predictions and personally review at least 30 randomly selected rejected postings, along with borderline and kept examples.

---

## 2026-11-25: Final Results and Reflection

### Comparing My Predictions With the Results

Before building the filter, I predicted that the confirmed shortlist would be small or empty. The actual result matched this prediction. Version 1.1 processed 2,418 postings and produced 0 confirmed matches, 63 postings for review, and 2,355 rejections.

I also predicted that 3 out of 30 randomly selected rejected postings would be worth reviewing. After reviewing the sample, I identified only 1 out of 30 (3.3%). My prediction was too high. However, the sample was small, so I cannot claim that 3.3% is the actual false-negative rate across all rejected postings.

I expected the word "data" to create false matches. The audit showed that keyword matching can be misleading, including the phrase "agentic systems" in a security role. Removing that phrase from that posting (audit row 60) reduced its score from 65 to 35 and changed the decision from review to rejected.

### What I Learned From the Audit

The audit identified two postings that I would have kept for review but the filter rejected. It also identified three postings in the review queue that I thought should have been rejected.

This showed me that a filter can follow its written rules correctly and still make decisions I disagree with. I needed to improve the rules, not simply fix the code.

### What I Changed After Testing

I tested three changes individually, using 20 held-out postings labeled before measuring the results.

**X1: Lower the threshold from 65 to 55**

On the held-out postings affected by this change, 9 decisions improved and 6 became worse. The results were inconclusive, and the review queue would increase from 63 to 107. I decided not to adopt X1.

**X2: Require two topic categories for related roles**

This changed eight decisions. Seven improved and one became worse according to my labels. It also reduced the review queue from 63 to 55. I adopted X2 as FILTER.md Version 1.2.

The regression was the Applied Data Scientist, Personalization & Machine Learning posting. I would have kept it for review, but Version 1.2 rejects it. I accepted this limitation and documented it rather than hiding it.

**X3: Treat "may also have" as a preferred-qualification heading**

This changed no decisions across the saved postings. I did not adopt it because I had no measured improvement to support the change.

### What Claude Got Wrong

Claude helped implement the filter, generate audit reports, test alternative rules, and build the MCP server.

However, Claude also made mistakes. One experiment report initially estimated improvements using the wrong population. It also calculated a sampling interval for X2 even though all eight affected postings had labels. Both problems were corrected, and regression tests were added.

The MCP testing revealed another issue. Both my server and the Lesson 8 reference server crashed when they received deeply nested JSON. Claude fixed my server, and the same test then returned a parse error without stopping the server.

These examples reminded me that I should verify Claude's calculations and code rather than accept its answers automatically.

### What I Am Responsible For

Claude can help write code, calculate scores, identify possible mistakes, and organize evidence.

I remain responsible for choosing the filter rules, evaluating job relevance, deciding whether to adopt changes, and deciding which tools I trust.

A high score does not automatically mean that a job is worth applying to. The filter supports my decisions, but it does not replace them.

### Final Outcome and Remaining Limitations

FILTER.md Version 1.2 processed 2,418 saved postings:

- Confirmed: 0
- Review: 55
- Rejected: 2,363

All 112 automated tests passed on Python 3.9 and 3.13, and all six planted bugs were caught.

The results are limited to previously saved job postings. I have not established how accurately the filter will handle newly published jobs, changing requirements, or unfamiliar location formats.

My biggest takeaway is that building a working filter is not enough. I also need evidence that its decisions are useful, a record of where it fails, and clear boundaries around what I allow AI tools to decide.

### What I Accepted, Modified, and Rejected From Claude

*Drafted by Claude at my request on 2026-11-25. It restates my documented decisions (`experiments/RULE-CHANGE-LOG.md`, and my label history in `e926b963` and `810de710`). It adds no new judgment.*

- **Accepted:** X2, Claude's proposal to require two topic categories for related roles. I adopted it as FILTER.md Version 1.2 (`7757d59c`) after the held-out measurement: 7 of the 8 affected decisions improved, and 1 got worse (audit row 59).
- **Rejected:** X1, Claude's proposal to lower the threshold from 65 to 55. The held-out result was inconclusive: 9 of 15 improved (95% Wilson 36%–80%). The review queue would also have grown from 63 to 107 postings.
- **Not adopted:** X3, Claude's proposal to treat "may also have" as a preferred-qualification heading. It produced no decision changes on the saved postings, so there was no measured improvement.
- **Modified:** Claude checked my pasted audit labels against the posting evidence. Before committing them (`e926b963`), I corrected:
  - two reasons that called a preferred item "required" (rows 31 and 51);
  - 16 false-friend cells. I cleared 8 where the filter matched no phrase (rows 7, 15, 21, 22, 24, 25, 29, 55), and replaced 8 with the phrase the filter actually matched (rows 2, 3, 6, 9, 31, 33, 49, 60).

  No verdict changed. On the held-out sheet, I corrected one note (row 17) before committing it (`810de710`).

### Evidence references

*Compiled by Claude at my request on 2026-11-25, so each statement above can be traced. It adds no decision of mine.*

- **Commits:**
  - `e926b963`: my 60 audit labels.
  - `810de710`: my 20 blind held-out labels, committed before any change was measured.
  - `f88d1922`: the experiment report, committed before my decisions.
  - `7757d59c`: FILTER.md Version 1.2 with X2, the archived v1.1 rules in `rules/v1.1/`, and the v1.2 run.
- **Claude prompt:** `mcp/claude-prompt.txt`. It was used for both live tool-server sessions, on 2026-11-25 at 04:18 and 04:26 UTC. Their transcripts are in `mcp/transcripts/`.
- **Tests:**
  - `test_experiment.WhatTheLabelsSay`, added after the wrong-population mistake.
  - `test_mcp_server.ProtocolErrors.test_deeply_nested_json_is_a_parse_error_not_a_crash`, added after the crash.
  - `test_versions.ExactlyOneChange.test_v12_differs_from_v11_only_in_the_adopted_value`, which checks that Version 1.2 is Version 1.1 plus X2 only.
  - `wrong_versions.py`, which caught 6 of 6 planted bugs.
- **Reports:**
  - `audit/sample-filter-v1.1-2026-11-18T212545Z/audit-results.md`: the 1 of 30 random rejects and the `agentic systems` false friend.
  - `experiments/REPORT.md`: X1, X2 and X3.
  - `runs/filter-v1.2-2026-11-25T203343Z/report.md`: 0 confirmed, 55 review, 2,363 rejected.
