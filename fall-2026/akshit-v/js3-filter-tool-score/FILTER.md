# FILTER — Job-Search Agent 3

**Version:** v1.0 (2026-11-24)
**Provenance:** Claude Code proposed each rule below as a numbered option on 2026-11-24, after showing me one measurement of the inherited JS1 rule (section 0). I approved all of F1–F9, E1–E5 and A1–A3 as drafted, chose all four wrong versions in section 4, and chose the label sizes in section 5. This file was committed alone, before any JS3 code existed. A rule changes only through a new version entry in section 7, with the measurement that justified it.

## 0. What I started from, and what I measured before writing this

- **Started from:** my own Job-Search Agent 1 rule (`agent/rule.py`, CONTRACT.md "The rule") and my Job-Search Agent 2 loop, providers, and permission policy (`agent2/`). I did not use the Reallocation Engine or Lectern.
- **Persona:** unchanged, the fictional **Jack Spencer** (data engineer, 5 years, master's completed, full-time only).
- **What "relevant" means** (v1.0, superseded for the JS3 labels on 2026-11-25; see the version log and `labels/LABELING_RULE.md`): unchanged from `experiments/LABELING_RULE.md` in JS1. A posting is relevant if I would tell Jack it is worth a day of his time to apply: (1) the work is data engineering at its core; (2) the level fits a 5-year individual contributor; (3) it is full-time; (4) he could plausibly be shortlisted. **My hand labels are the answer key. This filter is a cheap, readable stand-in for them, and it is judged against them.**
- **One measurement before v1.0.** Claude ran the inherited JS1 rule over the 603 postings my JS2 agent saved on 2026-11-10 (figma 144, spotify 86, snowflake 373). It kept 51. **45 of them were on the Snowflake board**, mostly Solution Engineer, Support, Architect and Auditor roles. The skill "Snowflake" matched the employer's own name, which appears in 382 of the 603 postings. That is the first false friend, and rule F6 below exists because of it.

## 1. The filter rules

All matching is case-insensitive and **whole-word**: a term never counts inside a longer word. This is inherited from JS1, where it stopped "SQL" from matching inside "PostgreSQL" and "AWS" inside "Washington".

| # | Rule | Why (one line) |
|---|---|---|
| F1 | **Fields read:** the posting `title`, its `content` as plain text (JS2 providers), and the board's structured employment-type field where one exists (Ashby `employmentType`, Lever `categories.commitment`). | These are the only fields all three boards have in common, plus the one structured fact that answers rule (3) without reading prose. |
| F2 | **Disqualify by title word:** Staff, Principal, Director, Manager, Head of, Intern, PhD, Contract, Temporary. | Inherited from JS1 unchanged. Jack is a 5-year individual contributor who wants full-time work; "Senior" and "Lead" stay allowed. |
| F3 | **Disqualify by structured field:** Ashby `employmentType` other than `FullTime`; Lever `commitment` present and not `Permanent`. A missing field is **unknown**, never a reject. | A structured field is more reliable than a title word. Missing data is not evidence of a part-time job. |
| F4 | **Role words (title):** Data Engineer, Data Engineering, Data Platform, Data Infrastructure, Analytics Engineer, Analytics Engineering, ETL, Data Integration, Data Pipeline. **+4** if any matches. | The title is the employer's own one-line statement of the job. It carries the most weight, but not enough to keep a posting alone. |
| F5 | **Topic groups (content):** each group counts **+1** once, at most **+4** in total. **T1 pipelines:** data pipeline(s), ETL, ELT. **T2 storage:** data warehouse(s), data warehousing, data lake(s), lakehouse. **T3 modeling:** data modeling, data model(s). **T4 orchestration:** orchestration. **T5 streaming:** streaming. **T6 batch:** batch processing, batch job(s). **T7 quality:** data quality. | These words describe the day-to-day work (rule 1 of "relevant"), not the tools. They are grouped so one idea repeated five times counts once. **Watch item:** "streaming" may mean *music* streaming on Spotify; kept in v1.0 and left to the audit to measure. |
| F6 | **Skills (content):** Jack's 8 skills (Python, SQL, Spark, Airflow, Kafka, dbt, Snowflake, AWS), **+1** each. **The employer's own name never counts as a skill on its own board** (Snowflake on the `snowflake` board). | Inherited skill list; the exception is the measured false friend from section 0. |
| F7 | **Score** = role (0 or 4) + topics (0–4) + skills (0–8), maximum 16. **Keep** if not disqualified and **score ≥ 6**. Otherwise **reject**. | A role-word title needs 2 more points of evidence; a posting without one needs 6 from content alone. This replaces JS1's two branches (3 skills / 4 skills) with one number I can rank by. |
| F8 | **Too little text:** if the content is shorter than **300 characters**, the answer is **"I cannot tell"**, not reject. | A posting with no description has not shown it is irrelevant; it has shown nothing. |
| F9 | **Ranking and shortlist:** kept postings sorted by score (high first); ties go to a role-word title, then more skills, then id. The **shortlist is the top 10**. **Close calls** are scores **5, 6 and 7** (threshold ±1). | A fixed, recomputable order. Ten is the number I could actually read in a sitting. |

## 2. The evidence rules (for the shortlist justification)

Every justification on the shortlist is a list of **claims**. Each claim carries a **quote**: an exact span copied from the posting's title, content, or structured field.

| # | Label | When |
|---|---|---|
| E1 | **supported** | The quote appears **verbatim** in the posting (after normalizing whitespace and case), **and** read in its own sentence it **states** what the claim says. |
| E2 | **contradicted** | Some span of the posting states the **opposite** of the claim (for example: claim "full-time", text "6-month contract"; claim "individual contributor", text "manage a team of five"). The contradicting span is quoted. |
| E3 | **insufficient** | No quote; or the quote is not in the posting verbatim; or the quote **mentions the claim's keyword without stating the claim**. Examples: a tool listed under "nice to have" cited as a requirement; the company's product description cited as the job's duties; boilerplate ("About Snowflake", benefits) cited as the work. |
| E4 | **Who labels.** The verbatim check is code. The meaning check (does the sentence *state* the claim?) is a fresh Claude session acting as a checker, and **I verify every label on the shortlist by hand**. Where I disagree, my label stands and the disagreement is recorded. | A string match can show a word is present. It cannot show the sentence means the claim. |
| E5 | **Relevance is not entailment.** A posting can match the filter's words and still not support the claim built on them. Keeping a posting is never evidence that any claim about it is supported. | This is what the shortlist must demonstrate on at least one real posting. |

**Abstention: when the agent must say "I cannot tell."**

| # | Rule |
|---|---|
| A1 | The posting's content is missing or shorter than 300 characters (F8). |
| A2 | Either **core claim** ("the main work is data engineering", "the level fits a 5-year individual contributor") is **insufficient** after checking. If a core claim is **contradicted**, the answer is "not relevant", not abstention. |
| A3 | The posting's board failed this run. The answer for that board is "no data: I cannot tell", **never** "no relevant postings". |

## 3. The expected sources

| Board | System | Fields used | Expected result | If something is missing |
|---|---|---|---|---|
| `figma` | Greenhouse | `title`, `location.name`, `content` (HTML → text), `absolute_url` | about 140 postings | No employment-type field exists: full-time is **unknown** unless the content states it. |
| `spotify` | Lever | `text` (title), `categories.location`, `categories.commitment`, `descriptionPlain` + `lists` + `additionalPlain`, `hostedUrl` | about 85 postings | `commitment` missing on some postings: unknown, not a reject (F3). |
| `snowflake` | Ashby | `title`, `location`, `employmentType`, `descriptionPlain`, `jobUrl`; only `isListed` postings | about 370 postings | — |
| `no-such-board-js2` | Greenhouse | — | **HTTP 404, on purpose** | Reported as "no data: I cannot tell" (A3), never as zero relevant postings. |

Missing a whole board makes the run's shortlist **incomplete**, and it says which board is missing. A board that returns 0 postings after returning more last time is `suspicious_empty` (JS2 rule) and also "I cannot tell".

## 4. Wrong versions my tests must catch

Each is plausible: it runs, it produces well-formed output, and it is wrong. My tests must pass on the real code and fail on each of these. Test postings are labeled CONSTRUCTED.

| # | Wrong version | Why it is plausible | The test that must catch it |
|---|---|---|---|
| WV1 | **Employer name as skill.** "Snowflake" counts as Jack's skill on Snowflake's own board. | It is the JS1 rule, unchanged; on Figma or Spotify the same word really is a skill. | A CONSTRUCTED `snowflake` posting whose only "Snowflake" is the employer name: its skill count must not include Snowflake, and its keep/reject must not change because of it. The same text on a non-Snowflake board does count it. |
| WV2 | **Keyword present = supported.** A claim is labeled supported whenever its quote is found verbatim, skipping the meaning check. | A verbatim quote looks like evidence. This is relevance treated as entailment. | A CONSTRUCTED posting with "Nice to have: experience with Spark". The claim "the role requires Spark" quoting that line must come out **insufficient** when the meaning check says the sentence does not state it. |
| WV3 | **Missing data = not relevant.** A failed board or an empty description is reported as "not relevant" or "0 kept". | Silence looks like a negative answer. | A CONSTRUCTED posting with a 40-character description must come out "I cannot tell"; the 404 board must come out "no data: I cannot tell", never 0 relevant. |
| WV4 | **Threshold off by one.** Keep at score > 6 instead of ≥ 6. | Both read as "above the threshold". | A CONSTRUCTED posting that scores exactly 6 must be kept, and its rank must sit above every score-5 posting. |

## 5. How the filter will be measured

**The corpus** is everything my agent collected: the JS2 saved responses of 2026-11-10 and a new live run on 2026-11-24, merged by posting id (the newer copy of a posting wins). The filter runs on all of it.

**My hand labels: 80 postings, blind.** One shuffled sheet shows each posting's board, title, location, employment-type field and full text, with **no** filter score, verdict, or Claude output. I label each `relevant` or `not_relevant` under the JS1 labeling rule, with a one-line note. The sample is drawn by a script with a fixed, recorded random seed.

| Set | Size | How it is drawn | Used for |
|---|---|---|---|
| **Audit: random rejects** | 30 | simple random sample of v1.0 rejects | the reject error rate, and what a sample of 30 can honestly say about it |
| **Audit: closest calls** | 10 | random from scores 5, 6, 7 (threshold ±1), at least 4 from each side when available | where the threshold is wrong |
| **Audit: random kept** | 10 | simple random sample of v1.0 kept | the kept error rate |
| **Held-out (sealed)** | 30 | 15 random rejects + 15 random from kept or the close-call band, none of them in the audit | **only** to measure each one-at-a-time change. Never used to design a rule. |

The audit sets drive rule changes (section 6). The held-out set is scored once per change, and its numbers are reported whether or not they flatter the change.

## 6. What changes the filter

A rule is **added, cut, or rejected** only after a measurement on my hand labels. Each change gets a row in section 7 with: the rule, what was measured, on which labels, and the number before and after. A change I tried and did not adopt is recorded as **rejected**, with its number.

## 7. Version log

| Version | Date | Change | Measured on | Before → after |
|---|---|---|---|---|
| v1.0 | 2026-11-24 | first version, written before any JS3 code | — (section 0 measures the JS1 rule, not v1.0) | — |
| v1.0 (definition) | 2026-11-25 | **What "relevant" means changed; no filter rule changed.** After labeling, I replaced the four-criterion definition with: the posting's technical skills overlap Jack's skills, fully or in part; job family and title level don't count against it; not relevant if the work isn't technical, it's an internship or not full-time, or it requires clearly more experience than 5 years. Wording drafted by Claude from my notes, accepted by me (`labels/LABELING_RULE.md`, dated entry). Consequence: rules F2 (title-level disqualifiers) and F4 (role words) now encode a stricter standard than my labels. | my 80 labels, as labeled | — |
