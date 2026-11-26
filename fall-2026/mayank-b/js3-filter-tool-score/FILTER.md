# FILTER.md: what reaches Priya, and why

**Version 0.1 · 2026-11-25 · Mayank Bhadrasen (mayank-b) · INFO 7375 Job-Search Agent 3**

Status: **DRAFT for my approval.** Claude Code turned my answers (`notes/filter-answers-2026-11-25.md`, from `notes/FILTER-QUESTIONS.md`) into this document. Lines marked _(proposed by Claude)_ are its wording or its additions; I keep, edit or cut each one before this is committed (JS3-CP1). This file is written **before** the filter code is committed and before the filter has seen the JS3 corpus. Its machine copy is `config/filter.json`; `tests/test_filter_md.py` fails if the two disagree.

**Started from.** My JS2 (`../js2-loop-tools-diff`: the bounded loop, allow-list, permission policy, raw responses + SHA-256), my JS1 title and location rule, and the instructor's **Lectern** filter as the model for this document. From Lectern I take a filter that is a document, a keep rule with a threshold, a per-company ignore list, and recording every word added, cut or rejected after measuring. Priya Nair (`persona/priya-nair.resume.json`) is fictional.

## 1. The filter

### 1.1 Role words: in the **title**

| Word | Why |
|---|---|
| `AI Engineer` | Priya's last job title (Staples co-op). Inherited from JS1. |
| `ML Engineer` | Her MS and co-op are ML engineering. Inherited from JS1. |
| `Machine Learning` | Catches "Machine Learning Engineer" and "Engineer, Machine Learning". Inherited from JS1. |
| `Applied AI` | The applied, building-with-models roles she targets. Inherited from JS1. |
| `Data Engineer` | Her SQL, Databricks and Delta Lake work. Inherited from JS1. |
| `LLM` | Her LLM evaluation and LLM-systems coursework. Inherited from JS1. |

Matching is **whole word, case-insensitive** (JS1): `LLM` does not match "LLMOps".

### 1.2 Exclude words: in the **title**

`Senior` · `Staff` · `Principal` · `Lead` · `Manager` · `Director` · `Head of` · `Intern`. Priya is early-career and not looking for an internship. Inherited from JS1, whole word: `Intern` does not match "International" (WF1).

### 1.3 Location (a hard gate)

Priya accepts **Boston, MA**, the relocation cities **San Francisco, CA** and **New York City, NY**, and **remote in the United States**. Each location piece (split on `|` and `;`) is compared exactly, ignoring case. Remote-US is a piece with the whole words "Remote" and "United States" (JS1), **plus** `Remote - USA`, `Remote - US`, `United States` and `US-Remote`. That addition is dated evidence: JS2's second check missed "Remote - USA" (`../js2-loop-tools-diff/runs/2026-11-11T02-24-39Z-second-check/`).

### 1.4 Topic words: in the posting **text**

A topic word counts **once** however often it appears (WF2). Each word's forms are listed; every form is whole-word, case-insensitive.

| Word | Forms _(proposed by Claude)_ | Why _(my line; Claude's suggestion until I rewrite it)_ |
|---|---|---|
| `python` | python | Her main language; every project on her résumé uses it. |
| `sql` | sql | Her Genie Router agent cut SQL query time about 30%; SQL appears twice on her résumé. |
| `llm` | llm, llms, large language model, large language models | Her co-op is LLM work: the router and LLM evaluation. |
| `evaluation` | evaluation, evaluations, evals | "LLM evaluation" is a named skill on her résumé (the A/B evaluation framework). |
| `agents` | agent, agents, agentic | She built a LangGraph agent used by 120+ analysts. |
| `machine learning` | machine learning | Her ML Engineer target and MLflow work; matched as a phrase. |

### 1.5 The keep rule, the score and the threshold

1. **Hard gates, from fields that exist.** An exclude word in the title → **reject**. A location Priya won't take → **reject**.
2. **Missing evidence.** No location, or no posting text → **cannot tell**, on a separate list. Never a reject (WF4) and never a keep.
3. **Keep** if a role word is in the title, **or** at least **T = 3** distinct topic words are in the text. T = 3 is inherited from Lectern, labelled so, and not fitted.
4. **The score** is the number of distinct topic words in the text (0–6). A **close call** is a reject decided by the score alone, at score T − 1 = 2.

Every record stores the words that matched, the form, where (title or text), the first offset and a 240-character snippet, so anyone can recompute it by hand.

### 1.6 Company boilerplate (Lectern's `ignore_words_by_company`)

v0.1 has **no** ignore list. After the v0.1 run I measure each topic word's share of each board's postings. A word in **≥ 90 %** of one board's postings goes on that board's ignore list, as a **measured change** in section 7, with its count.

### 1.7 Level ("5+ years")

**Not a filter rule.** It becomes shortlist claim C3 and is labelled like any other claim (section 2).

## 2. Evidence rules

**Labels.** Each claim in a shortlist justification gets one label, judged against **that posting's own text** (never the title alone, never the company's reputation):
- **supported:** a quoted passage states the claim, within its scope.
- **contradicted:** a quoted passage says the opposite (claim "early-career OK", text "7+ years").
- **insufficient:** the nearest passage is on topic but doesn't settle the claim; the row says what is missing.
- **not reviewed:** the default. **Only I may mark a row supported**, after reading the original posting. A matched word is relevance, not entailment (WF3).

**The claims per posting** (one sentence each, no "and"):
- **C1** the role matches Priya's target;
- **C2** the location is one Priya accepts;
- **C3** the level fits early-career;
- **C4** the work uses a skill Priya has (naming which one).

**When the agent must say "I cannot tell".** When the posting has no text, or the field a must-claim needs (C2 location, C3 level) is missing or insufficient. The posting goes on the **cannot-tell** list, never on the rejects and never on the shortlist.

**The abstention rule's known limit.** _(Counterexample to be shown from the real corpus.)_ A posting where C4 is matched by a word ("experience with LLMs", "agents") but the role is sales or support. Relevance passes and entailment fails, and the abstention rule does **not** fire, because the text exists and is on topic.

## 3. Expected sources

| Board | ATS | Fields I expect | When something is missing |
|---|---|---|---|
| `greenhouse/anthropic` | Greenhouse, `?content=true` | id, title, location, url, updated, text (`content`) | no text → cannot tell; no location → C2 insufficient |
| `greenhouse/hubspotjobs` | Greenhouse, `?content=true` | the same | the same |
| `ashby/notion` | Ashby | id, title, location (+ secondary, remote), url, published, text (`descriptionPlain`) | the same |
| `greenhouse/mayank-js2-no-such-board` | Greenhouse | none: a deliberate failure kept from JS2 | HTTP 404 → **error, not 0 postings** (JS2's error policy, unchanged) |

One new run of the JS2 loop: 4 GETs, two allow-listed hosts, raw bytes + SHA-256 saved. The 2026-11-11 JS2 files stay as history.

**My predictions, dated, written before the fetch** _(3b, mine: I chose option (a) of Claude's suggestions on 2026-11-25, before the fetch)_:
- **Counts, within ±10 % of 2026-11-11:** Anthropic 610–745, HubSpot 112–136, Notion 140–172.
- **Greenhouse fields:** the same fields as on 2026-11-11, plus a new `content` field holding the posting text as HTML, for at least 99 % of postings.
- **Notion fields:** `title`, `location` and `descriptionPlain` on every posting.
- **Location:** present on every posting, as on 2026-11-11.
- **The bad board:** HTTP 404 again, reported as an error, not 0 postings.

## 4. Wrong versions my tests must catch

| | Wrong version | Why it is plausible | The test that catches it |
|---|---|---|---|
| **WF1** | Substring match: `"intern" in title` | It is the obvious one-liner. In the saved JS2 titles, substring "intern" hits 15 titles and whole-word hits 6; one extra hit is "Applied AI Architect, International Policy". | `tests/test_filter.py` + `scripts/wrong_versions.py` |
| **WF2** | Ranking by the raw keyword count | Counting repeats feels like "more relevant", but a long posting that says "agent" 40 times beats a short one that fits. | the same |
| **WF3** | Relevance treated as entailment | A posting that matches C4's word is labelled "supported" without a quoted passage. | `tests/test_shortlist.py` + `scripts/wrong_versions.py` |
| **WF4** | A silent drop of postings with no text | Score 0 → reject looks tidy, but it hides "I could not read it" inside "not relevant". | `tests/test_filter.py` + `scripts/wrong_versions.py` |

The tool server has its own planted wrong version (WF6, answering before the handshake), tested in `tests/test_mcp.py`.

## 5. The reject audit

- **Draw.** A seeded uniform random sample of **30 rejects**, **every close call** (score 2; a seeded 15 if there are more), and a seeded **10 of the kept**. The seed is committed before the draw.
- **Verdicts.** Mine, by hand, from the original posting. Claude never fills them.
- **Words to flag** on the sheet (false-friend candidates): **pipeline** (data pipeline vs sales pipeline) and **training** (model training vs teaching people). The false friend itself is named only after I find one in the audit.
- **How I state the result.** If 0 of 30 random rejects are wrong, the one-sided 95 % upper bound on the reject error rate **for this snapshot's reject pool** is about 9.5 %. If k > 0, I report k/30 with an exact interval. I never write "the filter misses X % of jobs."

## 6. What moves the score

- **Held-out labels.** A new seeded held-out set of **30** postings, stratified 10 kept / 10 close calls / 10 random rejects of v0.1, **labelled blind** (the sheet hides the verdict and score), committed sealed before any rule changes, and used **once**. JS1's 20 labels were already looked at, so they are development data.
- **One change.** The filter file first: the one rule change my reject audit suggests, measured on the held-out set (agreement, false keeps, false rejects, before vs after). Everything else is held fixed.
- **Persistence.** A saved filter file changing later runs is configuration persisting, not training: no weights moved.

## 7. Decisions log (dated; every rule added, cut or rejected)

| Date (ET) | Change | Measured? | Evidence |
|---|---|---|---|
| 2026-11-25 | **Cut before v0.1:** topic word `rag`. RAG is not on Priya's résumé (0 mentions), so a keep on `rag` would produce a C4 claim her résumé can't support. | no: decided from the résumé | `persona/priya-nair.resume.json` |
| 2026-11-25 | v0.1 created from my answers | no: inherited (JS1, Lectern) or hand-set | `notes/filter-answers-2026-11-25.md` |
| 2026-11-25 | **Observation, not a change:** while building the loader, Claude Code saw that Notion writes "San Francisco, California" and "New York, New York". The inherited exact-match rule accepts only "San Francisco, CA" and "New York City, NY". v0.1 keeps the rule as decided; the audit decides. | seen before the run | `../js2-loop-tools-diff/runs/2026-11-11T02-24-39Z-second-check/raw/ashby__notion__a1__200.json` (location counts) |

## 8. Claude in this system

There is **no Claude in the filter or the score**. Claude writes **one short justification per shortlisted posting**, from the posting text and Priya's `search` block, with the current Haiku model. Its claims are what I label in section 2. Budget: at most 40 calls, plus one re-run of 5 to show variation. The call uses raw `urllib`; `api.anthropic.com` is allowed only in `src/jsa3/shortlist.py`, never in the tool server. The key comes from a git-ignored `.env` and is never printed.
