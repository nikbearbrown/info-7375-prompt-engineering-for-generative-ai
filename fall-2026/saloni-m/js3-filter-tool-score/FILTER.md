# FILTER — Job-Search Agent 3 (the filter, the tool, and the score)

**Version 1.0**, written 2026-11-26, **before any JS3 code existed** (this file is the first JS3
commit, `JS3-1`). Every later change gets a new version number and a line in §6.

**Who decided what.** Drafted by Claude Code on 2026-11-26 from two things Saloni already
decided in JS1: the title rule in `../js1-contract-and-watch/CONTRACT.md` (keywords and
seniority terms, carried over as they were) and her labeling rule
(`../js1-contract-and-watch/labels/LABELING-RULE.md`: hands-on building, within ~3 years,
no PhD, not senior). The topic words, weights, threshold, and evidence rules below are Claude's
proposal; Saloni confirms or changes them in the sign-off. No JS3 posting had been collected
when this was written. The titles I could have seen were JS2's saved id lists, which have
titles and no posting text.

Persona: the fictional **Priya Nair** (`../js1-contract-and-watch/personas/priya-nair.resume.json`).
MS Information Systems Dec 2025, one 8-month AI Engineer co-op, Python/SQL, LangGraph, MLflow,
Databricks.

The filter is this document. `js3/filter.py` reads the JSON block in §1 and nothing else. A
test (`tests/test_filter_doc.py`) fails if the code and this file disagree on any word, weight,
or threshold.

## 1. The filter (machine-read block)

```json filter
{
  "filter_version": "1.0",
  "threshold": 3,
  "role_title": {
    "weight": 3,
    "phrases": ["machine learning", "ml", "mlops", "ai engineer", "applied ai", "inference",
                "data engineer", "data engineering", "data platform", "analytics engineer"]
  },
  "seniority_veto_title": ["senior", "sr", "staff", "principal", "lead", "manager", "head",
                           "director", "vp", "distinguished"],
  "topic_text": {
    "weight_each": 1,
    "cap": 2,
    "phrases": ["python", "sql", "mlflow", "databricks", "spark", "airflow", "langgraph",
                "llm", "evaluation", "data pipeline", "training"]
  },
  "years_penalty": {"weight": -3, "min_years": 5},
  "phd_penalty": {"weight": -2},
  "text_min_chars": 300
}
```

## 2. Every rule, with one line of reasoning

Matching is on whole words after lower-casing and splitting on anything that is not a letter or
digit (the JS1 rule). "ml" matches "ML Engineer" and "Engineer, ML"; it does not match "HTML".

| Rule | Effect | Why |
|---|---|---|
| R1 role words in the **title** | +3 if any phrase matches | The title is where a company says what the job is; a role word in the body ("partner with our ML team") is not the job. |
| R1 phrases `machine learning`, `ml`, `ai engineer`, `applied ai`, `inference`, `data engineer` | — | Carried from JS1; these are Priya's three target roles. |
| R1 phrase `mlops` | — | Her co-op was MLflow tracing and drift monitoring, which is MLOps work under another name. |
| R1 phrases `data engineering`, `data platform`, `analytics engineer` | — | Common title variants of "Data Engineer"; added from general knowledge, not from JS3 data. |
| R2 seniority veto in the **title** | rejected whatever the score | JS1 labeling rule 3: a senior or lead role is not for someone one co-op out of school. |
| R3 topic words in the **text** | +1 each distinct phrase, at most +2 | Her stack showing up in the posting is evidence the work is hers to do; capped so a long posting cannot win by repetition. |
| R3 phrase `training` | — | Included because ML postings talk about model training. **Suspected false friend**: it also means employee training and sales enablement. Kept on purpose so the audit can measure it. |
| R4 years penalty | −3 if the text asks for 5 or more years of experience | JS1 labeling rule 2: "no more than roughly 3 years". Set at 5, not 4, so a "3–5 years" posting is not penalised; "roughly 3" leaves room. |
| R5 PhD penalty | −2 if the text says a PhD is required (not "preferred") | JS1 labeling rule 2: no PhD required. −2 rather than a veto because "PhD or equivalent experience" is common. |
| R6 threshold | keep if score ≥ 3 and no veto | A title role match alone (3) is enough; topic words alone (max 2) are never enough. |
| R7 short text | if the text is under 300 characters, R3–R5 are not applied and the posting is flagged `text_missing` | A missing body is not a body with no requirements (wrong version 3). |

R4 reads a number of years that comes within 60 characters before the word "experience" (as in
"5+ years of experience", "at least 6 years' experience"). R5 reads "PhD" or "Ph.D." in the same
sentence as "required" or "must", and not in a sentence with "preferred", "or equivalent", or
"nice to have".

## 3. Evidence rules (for the shortlist's justifications)

A justification is a list of claims. Each claim has a **kind** (role, skill, experience,
seniority, degree, other), a sentence, and a **quote** that is supposed to come from the
posting. Each claim gets exactly one label, checked against the posting's own text (title +
location + department + body), never against what the model or I believe about the company.

| Label | When |
|---|---|
| **supported** | the quote appears in the posting text (case and whitespace ignored), **and** the quote contains the claim's checkable term (the skill, the number of years, the role word). |
| **contradicted** | the posting text contains a span that conflicts with the claim: a claim of "≤3 years" against "5+ years of experience"; "not senior" against a seniority word in the title; "no PhD required" against a PhD-required sentence; "uses X" against "X is not required". |
| **insufficient** | anything else: the quote is not in the text (paraphrased or invented), the quote is in the text but does not contain the claim's term, or the claim is about something the text never addresses. |

Contradicted beats supported: if both hold, the label is contradicted.

**When the agent must say "I cannot tell"** instead of keep/reject:

1. the posting text is under 300 characters (R7), or
2. half or more of the justification's claims are insufficient, or
3. any claim of kind experience, seniority, or degree is contradicted, and that claim is the
   reason the posting was kept.

"I cannot tell" goes to Saloni. It is never counted as a keep or as a reject.

## 4. Expected sources

| System | Board | Host | URL | Fields the agent must see |
|---|---|---|---|---|
| Greenhouse | `anthropic` | boards-api.greenhouse.io | `/v1/boards/anthropic/jobs?content=true` | `id`, `title`, `location.name`, `departments[].name`, `content` (HTML, escaped), `absolute_url`, `updated_at` |
| Greenhouse | `figma` | boards-api.greenhouse.io | `/v1/boards/figma/jobs?content=true` | same |
| Ashby | `openai` | api.ashbyhq.com | `/posting-api/job-board/openai` | `id`, `title`, `location`, `department`, `descriptionPlain`, `jobUrl`, `publishedAt`, `isListed` |

The same allow-list as JS2 (two hosts, https, GET only). No login, no POST, no other host.

**When something is missing:**

- **A board fails** (non-200, not JSON, no jobs list): the agent reports "board X was not seen"
  and does not say "nothing relevant on X". The run is `incomplete`.
- **A board returns 0 jobs**: suspicious, same as a failure (JS2 wrong version 1).
- **A posting has no title or no id**: dropped and counted in `dropped`, never guessed.
- **A posting's body is missing or under 300 characters**: filtered on the title only, flagged
  `text_missing`, and the evidence layer says "I cannot tell".
- **An Ashby posting with `isListed: false`**: not collected (not public).
- **A field the filter does not use is missing** (location, department): recorded as null; it
  changes nothing.

## 5. Wrong versions the tests must catch

Drafted by Claude Code; Saloni confirms or replaces them in the sign-off.

1. **Substring matching.** "ml" matches inside "HTML", "ai" inside "maintain", "sr" inside
   anything. A filter that uses `phrase in title` keeps "HTML Email Developer".
   Test: `test_wv1_substring_match_is_caught`.
2. **Ranking by match count.** A filter that ranks by how many topic words appear (no cap, no
   veto) puts a long "Senior Staff ML Engineer" posting that says "Python" thirty times above a
   short "ML Engineer, New Grad" posting. Test: `test_wv2_count_ranking_is_caught`.
3. **Absence counted as support.** An evidence checker that labels "does not require more than 3
   years" as supported because no "5+ years" appears, on a posting whose text is empty. Silence
   is not support. Test: `test_wv3_absence_as_support_is_caught`.

## 6. Changelog: rules added, cut, or rejected after measuring

| Version | Date | Change | Measured on | Result | Kept? |
|---|---|---|---|---|---|
| 1.0 | 2026-11-26 | first version, before any JS3 data | — | — | — |
