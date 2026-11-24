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