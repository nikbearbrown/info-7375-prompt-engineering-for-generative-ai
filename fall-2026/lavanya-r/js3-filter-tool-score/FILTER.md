# FILTER.md — what reaches me, and why

**Version:** v1.1 · v1.0 written 2026-11-24 before any JS3 filter or scorer code; v1.1 the same day after the audit (see Changes) · Lavanya R
**Persona:** Priya Nair (fictional; `persona/priya-nair.resume.json`): MS Information Systems (Dec 2025), one AI Engineer co-op; Python, SQL, Databricks, MLflow, LangGraph; needs visa sponsorship.
**Started from:** my own JS1 rule (`agent/rule.py`, five checks), which JS2 carried over unchanged. I did not use the Reallocation Engine's scorer or Lectern's filter.

> **How this file was written (2026-11-24).** Claude computed the corpus facts. For section 1, Claude showed me the counts and real titles for each rule and offered 2–3 options for the words and for the reason; I chose each rule and each reason from those options, one rule at a time. So the choices are mine, but most of the wording of the reasons is Claude's. (My JS1 feedback asked me to write the rule in my own words first; for JS3 I picked from options instead. This is recorded in FRICTIONAL.md.) Sections 2–4 were drafted by Claude and marked as such; the Changes table records what I accepted or changed.

## Corpus facts (computed 2026-11-24 from `runs/2026-11-24T220432Z-live`, before any filter)

3,117 postings on 6 boards: databricks 890, openai 872, anthropic 632, palantir 305, zoox 246, notion 172. 1 has no text (zoox).

| Word in **title** (whole word, any case) | Postings | | Word in **title** | Postings |
|---|---|---|---|---|
| Engineer | 1,188 | | Senior | 273 |
| Software Engineer | 604 | | Sr | 230 |
| AI | 289 | | Staff | 293 |
| Applied AI | 149 | | Lead | 204 |
| Forward Deployed | 220 | | Manager | 607 |
| Data | 146 | | Director | 106 |
| Machine Learning | 29 | | Principal | 29 |
| ML | 24 | | Account | 216 |
| New Grad | 43 | | Solutions | 259 |
| Intern / Internship | 38 / 44 | | Research Scientist | 29 |

| Word in **text** | Postings | | Word in **text** | Postings |
|---|---|---|---|---|
| training | 1,423 | | sponsor (whole word) | 649 |
| Python | 1,065 | | 5+ years | 435 |
| Databricks | 912 | | PhD | 114 |
| evaluation | 511 | | 1+ years | 25 |
| LLM | 299 | | new grad | 7 |
| MLflow | 45 | | fine-tuning | 61 |

Rough US count: about 1,958 postings name a US place in a location field.

---

## 1. The filter v1.0 (rules and reasons chosen by me)

The structure Claude proposed and I accepted: **hard rejects** first, then a **score**, and a posting is kept if its score is at or above the **threshold**. The postings just above and below the threshold are the "closest calls" the audit looks at.

### 1a. Hard rejects (any one → reject)

| Rule | Exact words / condition | Why |
|---|---|---|
| R1 Seniority in title | Senior, Sr, Staff, Principal, Distinguished, Manager, Director, Lead, Head of (JS1's list plus "Head of") | These titles mean several years of experience or managing people; Priya has one co-op and no full-time years. |
| R2 Not my kind of role (title) | Account Executive, Recruiter, Counsel, Designer, PhD, Research Scientist (JS1 had Sales too; dropped, because "Sales" names a product area in engineering titles such as "Full Stack Software Engineer, Sales Platform") | These titles name sales, recruiting, legal, design or PhD research jobs; Priya is an engineer, and an AI word in the title doesn't change the job. |
| R3 Location | Reject unless at least one location names the US. A location names the US if it has JS1's markers (a state name, "USA", "United States", "D.C."), **or** a 2-letter US state code after a comma (", CA"), **or** one of the US cities listed in `config/filter.json` (San Francisco, Seattle, New York, Mountain View, Palo Alto, …). JS1's markers alone missed 112 "San Francisco" and 34 "Foster City, CA" postings. | Her work authorization (OPT, then sponsorship) only applies in the US. |
| R4 Sponsorship | Reject if the text says it can't sponsor: JS1's 10 phrases ("unable to sponsor", "not able to sponsor", "cannot sponsor", "can't sponsor", "will not sponsor", "does not sponsor", "do not sponsor", "without sponsorship", "no sponsorship", "sponsorship is not available"). Silence about sponsorship is **not** a reject. | It caught 0 of the US candidates on 2026-11-24, but it guards future boards; a posting that says nothing about sponsorship is "cannot tell" for the shortlist, not a reject. |
| R5 Experience (new) | Reject if the **smallest** "N years" / "N+ years" / "N-M years" the text asks for is **3 or more** (N under 20). | A stated minimum number of years is a screening requirement; Priya has under one year, so she would be screened out. |

### 1b. Score (points; kept if total ≥ threshold)

| Rule | Exact words | Points | Why |
|---|---|---|---|
| S1 Role words in title | AI, Machine Learning, ML, Software Engineer, Intern, New Grad, Early Career (JS1's list) | 3 if any appears | The title is the clearest sign of what the job is; these words name the AI/ML and entry-level engineering jobs Priya is aiming for. |
| S2 Topic words in text | LLM, large language model, machine learning, evaluation, MLOps, inference, fine-tuning, RAG, agents | 1 per different word, max 3 | A generic "Software Engineer" title can hide LLM or ML work; these words show the day-to-day work is what Priya did in her co-op (LLM evaluation, inference, agents). |
| S3 Résumé skills in text | the 10 skills in the four counted résumé fields: Python, SQL, Databricks, Unity Catalog, Power BI, LangGraph, MLflow, Mem0, Delta Lake, AWS (JS1's list; "familiar with, not shipped" still excluded) | 1 per different skill, max 3 | Each skill named in the posting is one she can point to on her résumé, so the application has evidence behind it. |

**Threshold:** 5 points (maximum 9). Why: A title word alone (3) isn't enough: the posting must also show ML work or her skills in its text, which keeps "AI" in a title from carrying a non-ML job.

All words match as whole words, ignoring case (JS1's matcher). Each word counts once, however often it appears.

### 1c. "Cannot tell"

The filter answers **cannot tell** (not keep, not reject) when a rule it needs has nothing to read. A title reject (R1, R2) still rejects, because the title is present.

| Condition | Why |
|---|---|
| The text is under 200 characters | Missing is not "no": a missing field is not evidence against a posting; rejecting it would hide a job Priya might want, so she sees it marked "cannot tell" instead. |
| The posting has no location | same |
| Every location is just "Remote", with no country or US state | same |

---

## 2. The evidence rules (drafted by Claude; accepted by me as written, 2026-11-24)

A **claim** is one sentence in a shortlist justification about the posting, such as "the role uses MLflow" or "it is in the US".

| Label | When |
|---|---|
| **supported** | A **verbatim quote** from the posting's own title, location or text says it. The quote must be found character for character (whitespace normalised) in the posting, and it must say the claim, not just contain the word. |
| **contradicted** | A verbatim quote from the posting says the opposite (e.g. "5+ years" against "fits a new grad"; "unable to sponsor" against "sponsors visas"). |
| **insufficient** | No quote supports or contradicts it. This includes a quote that contains the word but doesn't make the claim (relevance is not entailment), and a claim about anything the posting doesn't cover (salary not listed, team size, culture). |

**The agent must say "I cannot tell"** instead of answering when:
- E1: the posting has no text, or text under 200 characters;
- E2: the question is about the persona's fit on a point the posting is silent on (sponsorship never mentioned → "cannot tell", never "sponsors");
- E3: two quotes in the same posting contradict each other (e.g. "0–2 years" and "5+ years");
- E4: the claim's only support is a quote outside the posting (a company blog, Claude's general knowledge).

A shortlist justification with any **contradicted** claim is shown with that claim flagged. It is not silently dropped.

## 3. Expected sources (drafted by Claude; accepted by me as written, 2026-11-24)

| Board | ATS | Fields the agent reads | If missing |
|---|---|---|---|
| databricks, anthropic | Greenhouse | `title`, `location.name`, `offices[].name`, `content` (needs `?content=true`) | no `content` → "cannot tell" (E1), never reject on text rules |
| openai, notion | Ashby | `title`, `location`, `secondaryLocations[]`, `descriptionPlain` | same |
| palantir, zoox | Lever | `text` (title), `categories.location`, `categories.allLocations`, `descriptionPlain`, `lists[]`, `additionalPlain` | same |

- A board that fails or returns 0 jobs is reported as missing (JS2's `suspicious_empty` / `not_found`). Its postings count as **unseen, not rejected**.
- Expected size: about 3,100 postings (2026-11-24). A run under half of that for the same boards means something is wrong; it is not a quiet day.

## 4. Wrong versions my tests must catch (drafted by Claude; accepted by me as written, 2026-11-24)

| # | Plausible but wrong | Why it is wrong | Test |
|---|---|---|---|
| W1 | Substring matching ("Intern" matches "Internal", "ML" matches "HTML", "AI" matches "Aide") | the word matched for the wrong reason | `tests/test_filter.py` |
| W2 | Seniority checked in the text instead of the title ("work with senior engineers" rejects a new-grad job) | the text describes the team, not the role | same |
| W3 | Treating "cannot tell" (no text) as reject | a missing field is not evidence against the posting | same |
| W4 | Ranking by raw word count (a long posting repeating "AI" 30 times outranks a short exact fit) | length is not relevance; each topic word counts once | same |
| W5 | A shortlist claim labeled "supported" because the word appears anywhere in the posting | relevance is not entailment | `tests/test_evidence.py` |
| W6 | "Sales" as a reject word in the title (JS1's list) | it rejects engineering jobs such as "Full Stack Software Engineer, Sales Platform", where Sales names the product area | `tests/test_filter.py` |

## Changes

| Version | Date | Change | Measured? | Decision |
|---|---|---|---|---|
| v1.0 | 2026-11-24 | first version, before any filter code. Sections 2–4 accepted as Claude drafted them; W6 added | counts shown while choosing (Corpus facts and the counts quoted in R2, R3, R5) — not yet measured against my hand verdicts | — |
| v1.1 | 2026-11-24 | **Added X4:** ", CA" after a Canadian place (Ontario, British Columbia, …) is not California. The audit's false friend: R3 read "Ontario, CA" as California. | yes, on my 49 audit verdicts (`audit/measure.py`): 6 wrong before and after; 0 verdicts changed in the whole corpus (115 kept either way) | **adopted**: it fixes a wrong reason before a Canada-only job slips through |
| — | 2026-11-24 | **Rejected X1:** threshold 5 → 4 | 6 wrong → 5 wrong of 49; kept list 115 → 237 | **rejected**: one fewer mistake in 49 is too small to trust, and it doubles the reading |
| — | 2026-11-24 | **Rejected X2:** add "Forward Deployed" to S1 | 6 → 6 wrong; kept 115 → 124 | **rejected**: no measured gain |
| — | 2026-11-24 | **Rejected X3:** R5 uses the largest years asked, not the smallest | 6 → 6 wrong; kept 115 → 109 | **rejected**: no measured gain on my audit verdicts (the two postings it would fix are in the held-out set, which I may not use to choose; see AUDIT.md §4, Disclosure) |
