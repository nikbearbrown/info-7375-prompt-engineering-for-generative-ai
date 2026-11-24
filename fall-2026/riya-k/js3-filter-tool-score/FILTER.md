# FILTER.md: the filter, the evidence rules, the sources (written before the build)

Riya Kapadnis · INFO 7375 · JS3 · **Filter version v1** · 2026-11-24

**Started from:** my JS2 agent (`../js2-loop-tools-diff/`, final commit `6a800a2`): its hard rules (amendments 1–4),
its fictional persona Arya Sahni, and the postings it saved on 2026-11-10. No Lectern or Reallocation Engine code.

**Who decided what:** every rule, weight, threshold and abstention case below is my decision, given in chat with Claude
Code on 2026-11-24 (I picked "JS2 rule → scored", accepted the drafted weights and threshold 6, picked "min years > 3", and
chose all four abstention cases and all four wrong versions). When Claude pointed out that the accepted weights let a
job with no AI/data title word reach 7, I chose to add gate G5. Claude wrote the wording and the one-line reasons from my
answers. Any wording I change after reading it is recorded in the version log (§6). This file is committed **before any JS3 code**.

---

## 1. The filter

A posting is **KEPT** only if it passes every hard gate **and** its score is at least the threshold. A posting that fails
any gate is **REJECTED** whatever its score. The abstention rules in §3 come before both.

All word matching is case-insensitive and **whole-word** (a word may not sit inside a longer word), as in JS2.

### 1a. Hard gates (G1–G4 carried over from JS2 unchanged; G5 new)

| # | Gate | Reason (one line) |
|---|---|---|
| G1 | Location is US, or Remote not tied to a non-US country (state codes in capitals only) | Arya is in Boston and job-hunting in the US only; lowercase "in"/"or" must not read as Indiana/Oregon (JS1 amendment 2). |
| G2 | Title has none of: Senior, Sr, Staff, Principal, Director, VP, Vice President, Head, Manager | Arya has about one year of experience; these titles are out of reach no matter the skills. |
| G3 | Title has no whole word Intern or Internship | Arya has graduated; the TA asked for this in JS1 feedback (JS2 amendment 3). |
| G4 | Full-time only: title has none of Co-op, Coop, Part-time, Part Time, Contract, Contractor, Temporary, Fixed-Term, Fixed Term; **and** where the board states a type (Ashby `employmentType`), it is FullTime | I want full-time jobs only; the title check stays because Notion's "[Contract]" job said FullTime in the field (JS2 amendment 4). |
| G5 | Title has a ROLE word (list in §1b) | Added 2026-11-24 before any code: without it, a "Sales Engineer" whose text lists Python, SQL, AWS, MLflow, agents and evaluation scores 7 and is kept (wrong version W3). JS2 also required a title word. |

### 1b. The score (hand-set by me; nothing fitted)

| Part | Where it looks | Points | Words | Reason (one line) |
|---|---|---|---|---|
| ROLE | title | **+4, once** | AI, Applied AI, ML, Machine Learning, LLM, GenAI, Generative AI, Data Scientist, Data Science, Data Engineer, Data Platform, Analytics | The title is the strongest signal of what the job actually is; it is worth the most so no amount of skills can stand in for it alone. |
| JOB-TYPE | title | **+1, once** | Engineer, Scientist, Developer, Analyst | Separates hands-on roles from sales/marketing roles that also say "AI". |
| SKILL | title + text | **+1 each, max 4** | Python, SQL, Power BI, LangGraph, MLflow, Mem0, Delta Lake, AWS (the persona's shipped skills; Databricks and Unity Catalog never count, JS1 amendment 1) | Each skill Arya has actually shipped is evidence she can do the job; capped so a long skills list can't swamp the title. |
| TOPIC | title + text | **+1 each, max 2** | RAG, retrieval, evaluation, agents, LLM, fine-tuning, MLOps, embeddings | The kind of work Arya did (agents, LLM evaluation); small weight because these words also appear in company boilerplate. |

**Maximum score: 11. Threshold: KEEP if score ≥ 6.**
Reason: ROLE (4) + 2 skills = 6 is the same bar as the JS2 rule (title word + 2 skills), but a JOB-TYPE or TOPIC point can
stand in for one skill.

### 1c. What I expect this filter to get wrong (before measuring)

- Words with two meanings ("agents" for support agents, "training" for sales training, "AI" in sales titles) can add points
  for the wrong reason. The audit must look for these ("false friends").
- Greenhouse gives no employment type, so a part-time Greenhouse job whose title doesn't say so passes G4.

---

## 2. The evidence rules (for every claim in a shortlist justification)

Each kept posting gets a justification made of claims. Each claim is labeled against **the posting's own text only**
(title, location field, description, and the Ashby employment field). Nothing from outside the posting counts.

| Claim | SUPPORTED when | CONTRADICTED when | INSUFFICIENT when |
|---|---|---|---|
| C1 "It is an AI/data role" | the title has a ROLE word | (never from the title alone; see §5 relevance ≠ entailment) | — |
| C2 "It asks for skill X" (one claim per skill) | X appears whole-word in the posting text | the text says X is not needed (rare; checked by hand) | X does not appear. **Absence is not contradiction.** |
| C3 "It is in the US" | the location field names a US place or "United States" | the location field names only non-US places | the location is only "Remote"/"Remote-Friendly" with no country |
| C4 "It fits an early-career candidate (about 1 year)" | the smallest stated years-of-experience number is **3 or less** | the smallest stated number is **more than 3** (e.g. "4+ years", "5+ years") | no years are stated: the agent says **"I cannot tell"** about level |
| C5 "It is full-time" | Ashby `employmentType` is FullTime, or the text says "full-time" | the field or text says part-time, contract, temporary or intern | Greenhouse posting whose text never says (no field exists) |

A claim is never upgraded because the posting "seems like" it supports it. If the words are not in the text, the label is
INSUFFICIENT.

---

## 3. When the agent must say "I cannot tell" (abstention)

Checked **before** the score. The agent answers `cannot_tell` (not kept, not rejected; shown to me separately) when:

| # | Case | Reason (one line) |
|---|---|---|
| A1 | The posting text (description) is under 300 characters | There is nothing to check the claims against. |
| A2 | The location is only "Remote"/"Remote-Friendly" with no country | US eligibility (G1) can't be told; JS2 counted bare "Remote" as US, which is a guess. |
| A3 | The score is exactly 6 (the threshold) **and** any claim is INSUFFICIENT | A borderline keep built on missing evidence should go to me, not onto the shortlist. |
| A4 | No years of experience are stated | Claim-level only: C4 is "I cannot tell"; the rest of the posting is still judged. |

---

## 4. Expected sources

| Source | What the agent should see | Fields used | If missing |
|---|---|---|---|
| Greenhouse `databricks` | 914 postings (JS2 day-2 raw, 2026-11-10 19:45 UTC) | title, content, location.name | no employment field → C5 insufficient unless text says |
| Greenhouse `anthropic` | 677 postings (same run) | same | same |
| Ashby `openai` | 830 postings (same run) | title, descriptionHtml/Plain, location, employmentType | — |
| Ashby `notion` | 155 postings (same run) | same | — |
| Ashby `notarealco-js2` | nothing (HTTP 404, planted in JS2) | — | report "no data from this board", never "no relevant jobs" |
| SmartRecruiters `hubspot` | 0 postings (empty-200 trap in JS2) | list has no description | report "no data / suspect empty"; any posting from it would hit A1 |

Expected total from the four real boards: **2,576** postings. If the agent loads a different number, it must say so and
stop, not filter a partial corpus silently.

---

## 5. Wrong versions my tests must catch

Each one is plausible and would still produce a shortlist. Each gets a test that fails if the wrong version is planted.

| # | Wrong version | Why it's plausible | What catches it |
|---|---|---|---|
| W1 | **Substring matching:** "AI" matches inside "maintain"/"email", "SQL" inside "NoSQL" | it's the default `in` check in most languages | a test posting with only "maintain", "email", "NoSQL" must score 0 for ROLE/SKILL |
| W2 | **Score without the gates:** rank by score only | the score already looks like relevance | a London posting and a Staff posting with score 11 must be REJECTED |
| W3 | **Title-blind scoring:** count skills anywhere, ignore the title | skills feel like the real evidence | a "Sales Engineer" posting whose text has Python, SQL, AWS, MLflow, agents, evaluation must be REJECTED |
| W4 | **Threshold tuned on the held-out labels** | it makes the measured result look better | the held-out label file's hash is committed before any change is measured; a test checks the file still matches that hash |

Note on W3: with the score alone, a posting with no ROLE word can reach 1 + 4 + 2 = 7 ≥ 6. The threshold does not block
W3; gate G5 does. The W3 test therefore checks the gate, and planting W3 means deleting G5.

---

## 6. Version log (filled in after measuring)

| Version | Date | Change | Added / cut / rejected | Measured on | Result |
|---|---|---|---|---|---|
| v1 | 2026-11-24 | this file (G5 added before any code, see §1a) | added G5 | reasoning only (worked example), not data | — |
