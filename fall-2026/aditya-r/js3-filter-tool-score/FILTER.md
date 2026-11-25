# FILTER.md — Job-Search Agent 3 (version 1.0)

- **Version:** 1.0. This version is frozen once committed. Every later change is a new dated version in the change log at the bottom, and the v1.0 text above it is not edited. The v1.0 commit is the one whose message starts `JS3 gate: FILTER.md v1.0`.
- **Written:** 2026-11-25. Claude Code (Opus 5.5) drafted it at Aditya Raj's request, before any JS3 code existed and before any JS3 score had been computed. It builds on Aditya's JS1 contract (`../js1-contract-and-watch/CONTRACT.md` §4, R1–R5).
- **Aditya's review:** pending. Any rule he changes is recorded as v1.0-A (his amendment) in the change log, with the date.
- **What was already known when this was written (disclosed, not hidden):**
  - JS1's three-condition rule marked 5 of 903 Databricks postings relevant (2026-10-30).
  - In the JS2 live run (2026-11-10), all 10 judged postings were `not_relevant`.
  - The employer name "databricks" appears in every Databricks description (JS1 R2).
  - The field names, posting counts and empty-field counts of the captures listed in §4 were checked.
  - No JS3 score, title list or kept/rejected count had been looked at.

## 0. Who the filter is for

The filter is for **Priya Nair**, the fictional persona from JS1 (`resume/priya-nair.resume.example.json`, copied unchanged from JS2):
- MS in Information Systems, December 2025.
- One 8-month AI Engineer co-op: an LLM agent on Databricks plus LangGraph, MLflow tracing, and LLM evaluation.
- Skills: Python, SQL, Databricks, Unity Catalog, Power BI, LangGraph, MLflow, Mem0, Delta Lake and AWS.
- Lives in Boston, MA.

"Relevant" means **worth Priya's time to read in full**: an early-career engineering role whose work overlaps with hers. It does **not** mean she is qualified, will be hired, or should apply. That decision stays with the human (see the driver's-seat table in README.md).

## 1. The filter as a score

Every rule is computed on **normalized text**, using the normalization inherited from JS1 §4:
1. Convert HTML to text.
2. Lowercase it.
3. Turn each run of characters other than ASCII letters and digits into one space.
4. Trim.
5. Match whole words or contiguous whole-word phrases only.

So "Sr." becomes `sr`, "AI/ML Engineer" becomes `ai ml engineer`, "PostgreSQL" does **not** contain `sql`, and "HTML" does **not** contain `ml`.

**score = R + S + T + E + Y**, and the verdict is **keep if score ≥ 6**. Every term is an integer you can find with Ctrl-F.

### R. Role (posting.title only). Take the highest matching tier, not a sum.

| Tier | Phrases | Points | Reason |
|---|---|---|---|
| R-core | `ai engineer`, `machine learning engineer`, `ml engineer`, `llm engineer` | **+4** | These are Priya's actual job (an AI Engineer co-op). `ai engineer` also covers "Applied AI Engineer" and "Generative AI Engineer". |
| R-adjacent | `software engineer`, `data engineer`, `analytics engineer`, `data scientist`, `research engineer` | **+2** | Engineering roles her Python, SQL and data-platform work transfers to, but which are not her specialty. They need topic evidence (T) to reach the threshold. |
| none | (none of the above) | 0 | With no role phrase, the maximum is 0 + 4 + 1 + 0 = 5 < 6, so a posting cannot be kept on topic words alone. This is deliberate: a sales posting full of AI words is still a sales job. |

Inherited: JS1 condition A had five phrases. v1.0 adds `ml engineer`, `llm engineer`, `data scientist` and `research engineer`, and splits the phrases into two tiers.

### S. Level (posting.title only)

| Words (any one is enough) | Points | Reason |
|---|---|---|
| `senior`, `sr`, `staff`, `principal`, `lead`, `manager`, `director`, `head`, `vp`, `chief`, `distinguished`, `architect` | **−6** | Priya has under one year of full-time-equivalent experience. These titles are not early-career. The list is inherited unchanged from JS1 condition B. −6 makes a keep impossible (the maximum is otherwise 9). |
| `intern`, `internship` | **−6** | She graduated in December 2025, so internships are for enrolled students. New in v1.0. |

Title only: "you will work with senior engineers" in a description must **not** cost points (JS1 §4 B).

### T. Topic (posting.title + description). Distinct groups, +1 each, **capped at +4**.

| Group | Phrases (any one counts the group once) | Reason |
|---|---|---|
| T1 python | `python` | Her main language. |
| T2 sql | `sql` | Her second language. PostgreSQL and NoSQL don't count (whole word only, as in JS1). |
| T3 llm | `llm`, `llms`, `large language model`, `large language models`, `generative ai`, `genai` | Her co-op and project work is LLM systems. |
| T4 agents | `agent`, `agents`, `agentic`, `langgraph` | She built an agent router with LangGraph. |
| T5 ml | `machine learning`, `ml`, `mlflow` | The MS coursework and MLflow work. |
| T6 evaluation | `evaluation`, `evals` | Her A/B framework for LLM evaluation and her eval-guardrails project. |
| T7 data platform | `databricks`, `delta lake`, `unity catalog` | Her platform stack. **A word in the employer's own name never counts on that employer's board.** On board `databricks`, the word `databricks` is ignored (JS1 R2: it is in every description and tells us nothing). |
| T8 cloud | `aws` | Her cloud. |

- **Distinct, not counted.** "python" written 20 times is still +1. A long posting must not outrank a short one by repeating words.
- **The cap of 4** keeps a keyword-dense posting from making up for a missing or adjacent role.
- `spark` is deliberately absent. Priya's résumé does not list it (JS1 R2), and counting it would reward a skill she does not claim.

### E. Early-career signal (posting.title + description)

| Phrases | Points | Reason |
|---|---|---|
| `new grad`, `new graduate`, `recent graduate`, `university graduate`, `entry level`, `early career`, `junior` | **+1** | An explicit sign the role is open to someone at her stage. It is worth only +1 because these words are also used in the opposite sense (see the false-friend predictions in §6). |

### Y. Years required (posting.description)

- Find every phrase matching the regular expression `(\d{1,2})( (to )?\d{1,2})? (years?|yrs?)` in the **normalized** description. "5+ years" normalizes to `5 years`, and "3-5 years" normalizes to `3 5 years`. Read the **first** number in each match, and let **N** be the smallest of those numbers.
- **N ≥ 5: −3.** **N = 3 or 4: −1.** **N ≤ 2: 0.** **No match: 0**, and the level claim is then `insufficient` (§2).
- Reason: Priya's co-op is under a year. A stated floor of 5 or more years usually means a mid-level or senior role even when the title does not say so.
- Known weakness, written down before measuring: spelled-out numbers ("five years") are missed. Unrelated phrases ("founded 10 years ago", "1 year of tuition support") are counted.

### Threshold

- **Keep if score ≥ 6. Reject if score ≤ 5.**
- 6 is the smallest score a core role with two topic groups reaches (4 + 2), and an adjacent role with all four capped topic groups (2 + 4).
- Origin: **hand-set** in this document, not fitted. It will be checked against Aditya's labels and changed only through a logged revision.

### Missing data (the "I cannot tell" verdict)

- **Empty title** after normalization: verdict `cannot_tell`. No score is reported, because the role and level cannot be read.
- **Empty description** after normalization: verdict `cannot_tell`. The partial score is shown, but the posting is **not** rejected. Absence of evidence is not evidence of irrelevance.
  - This is a deliberate change from JS1, which marked these postings `not_relevant`.
  - `cannot_tell` postings are counted separately. They are never added to the rejects or the keeps.
- **Missing location or department:** these do not affect the score. The location claim in the shortlist is then `insufficient` (§2).

## 2. Evidence rules for the shortlist

- Each shortlisted posting gets a justification split into single **claims**.
- Each claim is labeled against **that posting's own text** (title, description, location field). Never against the board, the company, or general knowledge.
- Every label carries **(posting id, source field, exact quote)**, or names the evidence that is missing.

| Label | When |
|---|---|
| **supported** | A quoted span from the named field states the claim, and the quote exists verbatim in that field. For a claim about **the role** ("the role involves LLM work"), the span must describe the role's own duties or requirements. A span from company boilerplate, the "About us" section, benefits, or EEO text does **not** support a claim about the role. |
| **contradicted** | A quoted span states the opposite. Examples: a level-fit claim against "5+ years of experience required", or a Boston claim against a location field of "Bengaluru, India". If both supporting and contradicting spans exist, the label is **contradicted** and both quotes are shown. |
| **insufficient** | No span states it either way. Examples: no years or level stated, the location field missing or saying just "Remote" with no country, or the keyword appearing only in boilerplate. |

Claim types used in v1.0:
- **ROLE:** the title names role X.
- **TOPIC:** the posting mentions term X. This is **relevance**: the word occurs.
- **DUTY:** the role itself involves X work. This is **entailment**: the role's duties say so.
- **LEVEL:** the role is open to someone with 0–2 years.
- **LOCATION:** the role is in Boston or remote within the US.

A TOPIC claim can be supported while the DUTY claim on the same word is insufficient. That gap is the "relevance is not entailment" case the shortlist must show.

**When the agent must say "I cannot tell":**
1. The verdict is `cannot_tell` for an empty title or description (§1).
2. For any shortlist question whose claim is `insufficient`, the answer is "I cannot tell from this posting". It is never a guess. This applies most often to LEVEL and LOCATION.
3. If a kept posting's LEVEL claim is insufficient, the shortlist must say "I cannot tell whether this is early-career", not "good fit for a new grad".

Known limit: rule 2 triggers only when **no** span is found. A span that is found but misleading (a false friend) makes the agent answer confidently and wrongly. The shortlist must show one real counterexample of this.

## 3. Verdict vocabulary

- `keep`: score ≥ 6 and both title and description present.
- `reject`: score ≤ 5 and both title and description present.
- `cannot_tell`: title or description empty after normalization.

## 4. Expected sources

| Capture | Collector | Captured (UTC) | Board | Postings | Fields read |
|---|---|---|---|---|---|
| JS2 LIVE run `20261110T232115022Z_live/raw/01` | JS2 `agent.loop` | 2026-11-10 23:21 | greenhouse `databricks` | 920 | `id`, `title`, `content` (escaped HTML), `location.name`, `departments[].name`, `absolute_url` |
| same run `/raw/02` | JS2 `agent.loop` | 2026-11-10 23:21 | greenhouse `figma` | 144 | same |
| same run `/raw/03` | JS2 `agent.loop` | 2026-11-10 23:21 | ashby `notion` | 155 | `id`, `title`, `descriptionHtml`, `location`, `department`, `jobUrl`, normalized by JS2's adapter to the fields above |
| same run `/raw/04` | JS2 `agent.loop` | 2026-11-10 23:21 | greenhouse `js2-no-such-board-zzz` | 0 (HTTP 404, deliberate) | none |
| JS1 LIVE run `20261030T213823Z_live/raw_response.json` | JS1 `agent.watch` | 2026-10-30 21:38 | greenhouse `databricks` | 902 | as the Greenhouse rows |

- **Not used** (they are not collector output):
  - JS1's manual curl snapshot (2026-10-30 20:39, 903 postings).
  - The Internet Archive capture (2026-09-22). It has no descriptions, so every posting in it would be `cannot_tell`.
- **Identity** is `(provider, board, id)`. When the same identity is in two captures, the **latest** capture's text is used and the duplicate is counted.
- **Content duplicates** are postings on the same board whose normalized title and normalized description are identical (for example, one job listed under several location ids). They are grouped. Sampling and train/held-out splitting work on groups, so no duplicate can sit on both sides of a split.
- **A board that is missing or failed** contributes zero postings and is **reported as unavailable**. The agent's answer for that board is "I cannot tell what is on it". It is never "no relevant jobs there".
- **A board that answers with an empty list** is suspect-empty (inherited from JS2 GATE §4). It is reported, not treated as "nothing new".

## 5. Audit and split plan (fixed before any score was computed)

1. Compute the v1.0 verdict for every deduplicated posting.
2. **Held-out set H**, drawn first with seed `7375`, using content-duplicate groups as the unit:
   - 8 groups from the keeps;
   - 8 from the rejects scoring 3–5;
   - 8 from the remaining rejects.
   - H is sealed. Its labels are not opened until the dev revisions are frozen in `FREEZE.json`.
3. **Dev audit set**, drawn from everything outside H with seed `7376`:
   - **30 rejects drawn uniformly at random** from all non-H rejects (one per group);
   - **closest calls:** 6 at score 5 (just rejected) and 6 at score 6 (just kept), drawn at random within those scores. If a score level has fewer than 6, take all of them and report the shortfall;
   - **8 keeps drawn uniformly** from the non-H keeps.
   - A posting drawn into two groups appears once on the sheet and keeps both group memberships.
4. **Blind sheet:**
   - IDs are shuffled with seed `7377` and carry stable sheet IDs.
   - The sheet shows the title, location, department, board and a link to the full local text.
   - It never shows a score, verdict, group or suggested answer. The group membership file is kept separately.
5. **Aditya's label per posting:** `yes` (worth Priya's time), `no`, or `unsure`, plus a short reason. Only `yes`/`no` count in error rates. `unsure` is reported with its own count.
6. **What a sample can show:**
   - The random-reject error count estimates the miss rate **among rejects**, with an interval. It is not a measured rate.
   - The closest calls are chosen for being close to the threshold, so they cannot estimate any overall rate.
   - The keep sample estimates precision among keeps, with an interval.

## 6. Plausible but wrong versions the tests must catch

| # | Wrong version | Why it looks plausible | Test that must catch it |
|---|---|---|---|
| W1 | **Substring matching**: `ml` inside "HTML", `sql` inside "PostgreSQL", `ai` inside "maintain", `lead` inside "leading" | It finds "more" matches and every hit looks real | `test_w1_whole_word_only` (constructed posting) |
| W2 | **The employer name counts as a topic**: `databricks` on board databricks gives +1 | It matches a real persona skill | `test_w2_employer_word_ignored_on_own_board`: the same text scores +1 less on board `databricks` than on board `figma` |
| W3 | **Ranking by raw mention count** (no distinct groups, no cap) | "More relevant words means more relevant" | `test_w3_distinct_groups_and_cap`: 20 repeats of "python" give +1; nine groups give +4 |
| W4 | **A missing description becomes a reject** (JS1 behavior) | It is conservative, so it looks safe | `test_w4_missing_description_is_cannot_tell`: never counted among the rejects |
| W5 | **Seniority read from the description** ("work with senior engineers" gives −6) | Seniority words are real signals | `test_w5_level_from_title_only` |

`tests/mutation_check.py` must plant each W1–W5 into the real scorer and report it **CAUGHT** by the test suite.

### Predicted false friends (to be checked by the audit, not assumed)

| Word | Predicted wrong reason |
|---|---|
| `agent` / `agents` | Customer-support agents, sales agents, or an "agent of change", rather than software agents |
| `evaluation` | Performance evaluation, or "evaluation of candidates" |
| `junior` | "mentor junior engineers" means the role is senior, which is the opposite of the +1 |
| `ml` / `machine learning` | Company boilerplate ("we build ML products") rather than the role's duties |
| `N years` | "founded 10 years ago", "1 year of …" in benefits |

## Change log

- **v1.0** (2026-11-25): first version, above.
