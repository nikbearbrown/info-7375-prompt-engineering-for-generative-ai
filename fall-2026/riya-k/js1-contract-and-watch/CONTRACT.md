# CONTRACT — Job-Search Agent 1

Riya Kapadnis · written 2026-10-31, before any code for this agent existed.

## In

- **Board:** one Greenhouse board token. For this assignment: `databricks`
  (public endpoint `https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true`).
- **Résumé:** a JSON file for a **fictional** persona, Arya Sahni (`@example.com` email, 555 phone).
  The fields the agent uses are `skills` (all groups except `familiar_with_not_shipped` and `agent_note`).
- **It needs:** network access to the one allow-listed host, a state file listing the posting ids
  already seen, and a folder to save each raw board response in.

## Out — for each NEW posting

- `id`, `title`, `location`, `url` of the posting
- `verdict`: `relevant` or `not_relevant`
- `judge`: `rule` (a **record**: anyone can recompute it) or `claude` (a **judgment**: labeled as one)
- `justification`: must name at least one **résumé field** (e.g. `skills.languages: Python`) and at least
  one **posting field** (e.g. `title`, `content`, `location.name`) that the verdict rests on.

The first run is a baseline: it records every posting id and reports none as new.

## Refuses

- Fetching any host except `boards-api.greenhouse.io`.
- Showing a real résumé on screen or on GitHub. Only the fictional persona JSON is committed.
- Presenting Claude's verdict as a fact. It is always labeled `judge: claude` (a judgment).
- Applying to any job, emailing or messaging anyone, or logging in anywhere.

## The rule (a TA can compute this by hand)

All matching is case-insensitive and **whole-word** (a word inside a longer word does not count).

A posting is **RELEVANT** only if all three hold:

1. **Title words.** The `title` contains at least one of:
   AI, LLM, GenAI, Generative AI, ML, Machine Learning, Data Engineer, Data Platform,
   Data Scientist, Data Science, Analytics.
2. **Skills.** At least **2** of Arya's shipped skills appear in the posting's `title` or `content`:
   Python, SQL, Unity Catalog, Power BI, LangGraph, MLflow, Mem0, Delta Lake, AWS.
   - "Databricks" is **not** counted: the board is Databricks, so it would be a free match on every posting.
   - Ray and Kubeflow are **not** counted: they are listed as familiar, not shipped.
3. **Location.** `location.name` is in the US or Remote: it contains "United States", "USA", "US",
   a US state name or two-letter state code, or "Remote" without naming a non-US country.

And it is **NOT RELEVANT** if the `title` contains any of these seniority words:
Senior, Sr, Staff, Principal, Director, VP, Vice President, Head, Manager.

Otherwise: **NOT RELEVANT**.

## Labeling rule (for my 20 hand labels)

I label a posting relevant if Arya could apply honestly today: the role matches her AI/ML/data target,
it is not senior, and she has at least 2 of the core skills the posting asks for.

## Wrong versions my tests must catch

1. **Labels on the wrong posting:** verdicts get attached to the wrong posting id
   (for example, shifted by one after sorting).
2. **Justification that cites nothing:** it says "good fit" but names no résumé field and no posting field.

Extra checks (also tested): a posting already in the baseline reported as new again, and a skill
matched inside another word ("SQL" inside "NoSQL", "AI" inside "maintain").

## What a failure looks like

2026-10-31: A failure is the agent reporting a posting as new that was already seen, or calling a
posting relevant without naming the résumé and posting fields behind it.

## Amendments (dated; the original text above is unchanged)

- **2026-10-31, amendment 1 (rule 2, skills):** "Unity Catalog" is also **not** counted. Found while preparing
  the hand-labeling sheet: it appears in 901 of 901 Databricks postings because Databricks' standard
  "About Databricks" paragraph names it, so it was a free match on every posting, the same trap as
  "Databricks". Decided by Riya in the chat. Runs before this amendment (the live baseline and the seeded
  two-day run) used the original rule; none of their 24 new postings changes verdict under the amendment.
- **2026-10-31, amendment 2 (rule 3, location; clarification found by Claude in a pre-submission audit):** "US" and the two-letter
  state codes are matched **case-sensitively, in capitals** (all other matching stays case-insensitive). Reason: matched
  case-insensitively, "Montréal, Canada" contains "al" as a whole word (the "é" breaks the word) and would count as
  Alabama. The code already behaved this way; this records it so a TA computing by hand gets the same answer. Checked on
  all 191 location strings in both snapshots: only the two Montréal strings differ, and case-sensitive classifies them correctly as non-US.
- **2026-10-31, Out fields:** the original code omitted `location` and `url` from each verdict although "Out" lists them;
  fixed, and the seeded two-day run was re-run so its report includes them.
