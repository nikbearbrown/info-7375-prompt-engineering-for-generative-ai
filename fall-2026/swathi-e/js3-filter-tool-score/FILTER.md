# FILTER.md — Job-Search Agent 3: the filter and the evidence rules

Version 1, written by Swathi Baba Eswarappa, 2026-11-17, before any JS3 code.
Claude (chat) helped me phrase my decisions; I confirmed every line.
Built on my JS2 agent (fall-2026/swathi-e/js2-loop-tools-diff/).
Persona: Priya Nair (fictional): AI/ML engineering first, data engineering
second; Boston, MA or remote in the US; F-1 OPT; 0-1 years of experience.

## Expected sources
| Board | System | Fields the filter reads |
|---|---|---|
| Databricks, Stripe | Greenhouse | title, location, description (fetched with descriptions included) |
| Plaid | Ashby | title, location (with secondaryLocations and address country), description |
- A board that fails is reported as failed (JS2 rules); no postings are invented for it.
- A posting with a missing or empty description: the text rules cannot be
  applied, so the answer is "I cannot tell", never relevant or not relevant.

## The filter
Each rule has one line of reasoning.

R1 Role (title). The title names AI, ML, Machine Learning, GenAI, Data
   Engineer/Engineering, Data Scientist/Science or Analytics, or says
   Software Engineer together with New Grad, Early Career, Entry or University.
   Why: these are Priya's target roles.
R2 "Analyst". A title with "Analyst" counts for R1 only if the job's
   responsibilities or required skills name data, analytics, SQL, machine
   learning or AI. Words that appear only in company boilerplate, the
   "About" section, benefits or legal text do not count.
   Why: in JS2, a Fraud Intelligence Analyst matched on "Analyst" alone.
R3 Seniority (title). Reject titles with Senior, Sr, Sr., Staff, Principal,
   Lead, Leader, Manager, Director, Head, Intern or Internship. "Sr" and
   "Sr." are treated the same.
   Why: these are not entry-level full-time roles.
R4 Location. Keep only postings in the US, or remote postings that allow
   working from the United States. A remote posting limited to another
   country is rejected.
   Why: Priya can work only in the US.
R5 Experience (description). Keep if it asks for 0-1 years, or says new grad,
   entry level or early career. Reject if its minimum is more than 1 year
   (e.g. "2+ years", "3-5 years") or it says it is not for new graduates.
   If no experience is stated: evaluate the responsibilities and skills; if
   the evidence is still insufficient, the answer is "I cannot tell".
   Why: Priya has 0-1 years; my JS1 labels failed mostly on experience.
R6 Work authorization (description). Reject if it requires US citizenship
   or a security clearance, or says it will not sponsor visas. The standard
   export-control "Compliance" paragraph is NOT such a requirement.
   Why: Priya is on F-1 OPT; in JS1 Claude mistook that paragraph for one.
R7 Topic words (description). Count distinct topic words: machine learning,
   deep learning, LLM, NLP, Python, SQL, Spark, data pipeline, statistics.
   Why: they show the work itself is AI/ML or data work, not just the title.

## The score (every number hand-set by me)
- A posting that fails R3, R4, R5 or R6 is rejected, with no score.
- A posting must pass R1 (or R2, for an "Analyst" title) to be shortlisted.
  Without a role match it is not shortlisted, whatever its other points.
- Otherwise: role match (R1/R2) = 3 points; explicit early-career evidence
  (R5) = 2 points; each distinct R7 topic word = 1 point, at most 3.
- Shortlist threshold: 5 or more points.
  Why: a role match plus either early-career evidence or two topic words.

## The evidence rules
For every claim in a shortlist justification (e.g. "asks 0-1 years",
"no sponsorship restriction", "ML engineering role", "in the US"):
- supported: an exact quote from the posting text says it;
- contradicted: an exact quote says the opposite;
- insufficient: the text does not say it either way.
A missing statement is insufficient, never supported (e.g. no sponsorship
sentence does not mean "will sponsor").
The agent must say "I cannot tell" when the description is missing or empty,
or when R5's experience question stays unanswered after reading the title,
skills and description.

## Wrong versions my tests must catch
1. Topic words matched anywhere, so a false friend like "training" in a
   sales-training posting counts as ML.
2. The export-control paragraph treated as a citizenship requirement.
3. A title-only filter (my JS1 rule) that keeps a Fraud Intelligence Analyst
   or misses a "5+ years" requirement in the description.
4. "0-2 years" read as qualifying because it starts at 0.
5. A missing description scored as 0 or "not relevant" instead of
   "I cannot tell".
6. No sponsorship sentence labeled "supported: will sponsor".

## Change log (rules added, cut or rejected after measuring)
(none yet: version 1)
