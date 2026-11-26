# FILTER.md — Job-Search Agent 3

**Filter version: v1** · Persona: fictional "Jordan Lee" (`data/persona_resume.json`, copied unchanged from JS1)

> **Who wrote this.** Claude drafted it on 2026-11-25 (about 21:45 ET), at Siddi's choice ("Claude drafts, I edit").
> It is built from three things Siddi wrote or decided: JS1 `CONTRACT.md` (title words, exclusions, seniority,
> the years rule, the skill vocab), JS1 `LABELING.md` (what Siddi counts as relevant), and Siddi's decisions on
> 2026-11-25. At about 21:59 ET Siddi answered the draft's three open questions (location: anywhere in the USA;
> years cap: 4; budget: keep 30) and approved the rest as written. This file was committed before any filter
> code existed. Only the collector (`js3/collect.py`, which reads boards and does not filter) was written earlier.

Each number below is tagged with where it came from: **inherited** (from JS1), **hand-set** (chosen in this draft, not fitted on any labels), or **decision** (Siddi's decision, dated).

## A. The filter

A posting is **kept**, **rejected**, or **cannot tell**. A posting that fails a gate is rejected and gets no score. A posting that passes all four gates gets a score, and it is kept if the score is 4 or more.

All word matches are whole-word matches on lowercased text, `(?<![a-z0-9])WORD(?![a-z0-9])`, never substrings (inherited from JS1).

### Gates (any one fails → rejected, and the record names the gate)

| # | Rule | Why |
|---|---|---|
| G1 | The title contains none of these words: account, sales, solutions, architect, recruiter, recruiting, marketing, consultant, customer, support, field, partner, evangelist, advocate, product. *(inherited, JS1 Appendix A)* | These titles name selling, supporting or product roles, even when "AI" or "data" is in the title, and Jordan builds data and ML systems. |
| G2 | The title has no seniority word: senior, sr, staff, principal, lead, manager, director, head, vp. *(inherited)* | Jordan has 2 years of experience. |
| G3 | `years_required` is 4 or less, using JS1's years regex (only sentences that say "experience" count, the lower bound of a range counts, a number right after a master's/PhD is skipped). If no number is found, the gate passes. *(inherited: years_experience 2 + 2)* | More than 4 required years is out of reach for Jordan. *(decision, Siddi, 2026-11-25: the cap stays at 4, not the stricter 2 that LABELING.md answer 2, "2+years", could also mean)* |
| G4 | The location is in the United States, or remote in the US (rule in "Location" below). *(decision: LABELING.md answer 3, "Anywhere in usa")* | This replaces JS1's five preferred cities. All of JS1's judge misses came from the gap between those cities and "anywhere in USA". *(decision, Siddi, 2026-11-25)* |

### Score (only for postings that pass every gate)

| # | Rule | Points | Why |
|---|---|---|---|
| R1 | Role words: the title contains one of machine learning, ml, data engineer, data engineering, data platform, data scientist, ai *(inherited, JS1 `target_title_keywords`)* | +3 *(hand-set)* | The title is the strongest signal of what the job is. |
| R2 | Skill words: each of Jordan's 12 skills found in the posting text, using JS1's vocab aliases (python, sql, scala, spark, airflow, kafka, dbt, bigquery, gcp, docker, kubernetes, tableau) *(inherited)* | +1 each, at most 4 *(hand-set)* | Matches the work Jordan can already do. The cap stops a long posting from winning on length. Distinct skills count, not repetitions. |
| R3 | Topic words: the posting text contains any of machine learning, deep learning, data pipeline, data pipelines, etl, data warehouse, data modeling, ai, llm, llms *(hand-set)* | +1 once *(hand-set)* | Catches data and ML work whose title doesn't use a role word. |

**Keep line:** a score of 4 or more *(hand-set)*. So a role-word title needs one more hit, and a title with no role word needs 4 skills, or 3 skills plus a topic word. This leans toward skill, as LABELING.md answer 5 says ("To skill").

**Changed from JS1, on purpose:** JS1's "at least 3 skills and at least 40% of the posting's skills" rule is replaced by R2's capped points, so there is a threshold and the audit has close calls to look at. The 40% ratio also depended on how big the vocab was.

**Degrees and internships:** no gate. LABELING.md answer 4 counts master's roles and internships, and in JS1 Siddi labelled a US PhD internship relevant.

### Posting text

- Stripe `content` is HTML. It goes through JS1's text preparation: unescape, straighten quotes, cut from a `cut_headings` heading onward, strip tags into lines, lowercase, and drop sentences that contain a `drop_sentence_phrases` entry.
- Notion `descriptionPlain` and Canva's job-ad sections are plain text, and get the same steps from straightening quotes onward.
- Boilerplate in v1: Stripe uses JS1 v2's list (cut at "in-office expectations", drop "stripe is a financial infrastructure platform"). Notion and Canva have **none yet**, because neither has been measured. If a company blurb produces matches, that is a change to record below, with its measurement.
- R2, R3 and G3 read only the prepared text. R1, G1 and G2 read only the title. G4 reads only the location fields.

### Location (G4)

- Split the location on `;`, `|`, `/` and the whole word "or". The posting passes if any part is in the US.
- A part is in the US if it whole-word contains "united states", "usa", "us" or "u.s.", or ends in ", XX" where XX is a US state or DC postal code, or names a US state in full.
- If the board gives a country field (Ashby `addressCountry` in `address` or `secondaryLocations`, SmartRecruiters `location.country`), that field decides instead of the name.
- A remote part passes only if it also names the US (or North America), or the country field says US. A bare "Remote" with no country is **cannot tell**, not a pass and not a reject.
- **Why:** "Remote - Australia" and "Toronto, ON" must fail, and a city with no country must not be guessed.

### Cannot tell (the filter's own abstention)

A posting goes to **cannot tell** instead of being kept or rejected only when the missing field could change the outcome:
- its text is empty after preparation (or the text was never collected), and it passes G1 and G2; or
- G4 cannot place its location, and it passes every other gate.

Cannot-tell postings are listed for Siddi and counted on their own. They are never counted as rejects.

### Shortlist and ranking

- The shortlist is the 10 highest-scoring kept postings.
- Ties go to more distinct skills, then board order (Stripe, Notion, Canva), then id.
- **Why:** a fixed, recomputable order, so a TA can rebuild the list by hand.

## B. Evidence rules

The shortlist justification for each posting is written by Claude, and it is a **judgment**. It is a list of **claims**: one checkable statement each, typed as role, location, years, degree, skill or other. Each claim carries a quote copied from the posting's title, location or text.

- **Supported:** all three hold.
  - The quote is found verbatim in the posting's own fields, after case, whitespace and quote-mark normalization.
  - The quote is not in cut boilerplate.
  - The quote, read on its own, says what the claim says. Plain abbreviations count ("SF" = San Francisco); inference does not.
- **Contradicted:** some text in the posting's own fields says the opposite. For example, the claim "needs 4 years or less" against "7+ years of experience", or "US-based" against "Toronto". The contradicting quote must be shown. If a supporting quote and a contradicting quote both exist, the claim is **contradicted**, so the shortlist never hides a conflict.
- **Insufficient:** nothing contradicts the claim, and either the quote isn't found verbatim, or it is found but doesn't state the claim. Examples: the word appears in another sense ("spark" in "spark ideas"), the quote is in boilerplate, or the claim needs a step the text doesn't take ("remote-friendly" from "distributed team").
- **"I cannot tell":** for a shortlisted posting, the agent answers "I cannot tell" instead of relevant or not relevant when:
  - the posting's text or location was missing; or
  - either deciding claim, **role** or **location**, is insufficient.
  It never fills a deciding claim from the company name or the title alone.
  - A years claim that the posting never states is **not** a reason to abstain, because no stated requirement is not a barrier (inherited from JS1's G3). A stated years claim that is contradicted makes the answer "not relevant".

## C. Expected sources

| Board | System and request | Fields the agent uses | Count on 2026-11-25 probe |
|---|---|---|---|
| Stripe | Greenhouse `GET boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` (1 request) | `id`, `title`, `location.name`, `content`; `absolute_url` recorded, never fetched | 772 |
| Notion | Ashby `GET api.ashbyhq.com/posting-api/job-board/notion` (1 request) | `id`, `title`, `location`, `secondaryLocations`, `address.postalAddress.addressCountry`, `isRemote`, `workplaceType`, `descriptionPlain`; `jobUrl` recorded, never fetched | 174 |
| Canva | SmartRecruiters `GET api.smartrecruiters.com/v1/companies/Canva/postings?limit=100&offset=0` (1), then `GET …/postings/{id}` once per posting | list: `id`, `name`, `location.fullLocation`, `location.country`, `location.remote`; detail: `jobAd.sections.*.text` | 28 |

- **Budget** *(decision, Siddi, 2026-11-25)*: at most 30 requests and 120 seconds per collection run. GET only, no redirects, and only the three hosts above.
  - With 28 Canva postings, full text needs 31 requests (1 + 1 + 1 + 28). Claude had first said "about 30". Siddi chose to keep 30 anyway, so a run today ends `budget-exhausted`, and the last Canva posting in id order has no text.
- **When something is missing:**
  - **A board fails** (404, timeout, bad body): it is reported as failed with its reason, and the run is `incomplete`. It is never reported as "0 relevant postings" (JS2 GATE §4).
  - **A Canva detail call fails, or the budget runs out before it:** that posting has no text, and the run says how many postings lack text and why. Such a posting is **cannot tell** if it passes G1 and G2.
  - **An empty board** (200 with 0 postings) counts only if the response's structure and the board identity check out, as in JS2's patch `ef6456a`.

## D. Wrong versions (the tests must catch each one)

1. **Substring matching:** "ai" counted inside "maintain", "email" or "Taiwan", or "ml" inside "HTML", so non-ML postings score.
2. **Boilerplate counted:** a company blurb or a benefits section gives every posting at that company the same skill or topic hits. For example, Stripe's "financial infrastructure platform" sentence is left in the text.
3. **Score instead of gates:** a "Sr. Machine Learning Engineer", or a posting in Toronto, is kept because its score is high.
4. **Missing treated as an answer:** a posting with no text, or a location the rule can't place, is silently rejected (or kept) instead of going to cannot tell.
5. **Ranking by repetition:** counting every occurrence instead of distinct skills, or dropping the cap, so a long posting that says "Python" nine times outranks a shorter one that matches more of Jordan's skills.
6. **Relevance taken as entailment:** a shortlist claim is labelled supported because its word appears somewhere in the posting (for example, "requires Spark" because the text says "spark new ideas"), or because the quote exists but doesn't state the claim.
7. **Invented quote:** a claim is labelled supported when its quote is not in the posting verbatim.
8. **No abstention:** a shortlisted posting whose role or location claim is insufficient still gets a confident "relevant".

## E. Version log

Every rule added, cut or rejected after measuring goes here, with the date, the measurement and the evidence file. Past versions are never edited.

| Version | Date | Change | Measured on | Decision |
|---|---|---|---|---|
| v1 | 2026-11-25 | First version (this file) | — | — |
