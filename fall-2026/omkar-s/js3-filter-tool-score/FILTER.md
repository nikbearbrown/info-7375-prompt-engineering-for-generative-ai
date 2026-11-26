# FILTER.md: the gate for Job-Search Agent 3

**Current version: 1.6** (2026-11-17). **Version 1.0 was written 2026-11-17 (finished 06:15 UTC) by Claude Code, before any JS3 code existed**; its frozen copy is `evidence/FILTER-v1.0-frozen.md` (sha256 in `evidence/TIMELINE.md`). Versions 1.1 to 1.6 came from measuring on the whole corpus, reading the generated shortlist, or a second reader's disagreement on the audit sample; each one is a single change, recorded in section 5 with the measurement behind it. The machine copy of each version is `filter/filter-v<version>.json`, and `filter/CURRENT` names the version in force. A test (`tests/test_filter_doc.py`) fails if this document and the current JSON disagree.

**Persona:** the fictional Aarav Patel (`persona/aarav-patel.example.json`, the same file byte for byte as in JS1 and JS2). He has an MS in Information Systems (2026-05), about 2 years full-time as a Software Engineer plus a co-op, and lives in Boston. He is open to any US location.

**Disclosure, written before measuring:** while surveying JS1, Claude Code saw the first 4 rows of `js1-contract-and-watch/experiments/prompt/labels.csv`: Omkar's 20 hand labels, which JS3 uses as its **held-out** set. Two of those 4 rows were *Senior* / *Lead* titles that Omkar labelled relevant. That is one reason rule T3 below is a penalty and not a gate. So the held-out set is not perfectly blind for that one design choice. No other label was read.

**[Omkar]** Every rule was proposed by Claude Code, from Omkar's JS1 contract and JS1 labeling rule. Omkar confirmed all five sections on 2026-11-25 and kept the threshold at 5.0 (section 6).

---

## 1. The filter

A posting is **kept** if it passes **all three gates** and its **score is at least the threshold (5.0)**. A posting that fails a gate is rejected whatever its score. Its score is still computed so that the audit can find close calls. Every rule that fires writes one justification line with its points, and **the lines sum to the score**. That property came from the Reallocation Engine's greenhouse-watch fix "justification lines now sum to the score".

Text matching is **case-insensitive and whole-word**: no letter or digit may touch either end of the match. This is JS1's rule, so `Java` does not match `JavaScript` and `SQL` does not match `PostgreSQL`. `content` is the posting body after HTML is unescaped, tags are stripped and whitespace is collapsed (JS1 `clean_content`).

### 1a. Gates (pass/fail)

| ID | Gate | Field | Rule | Reason (one line) | Origin |
|---|---|---|---|---|---|
| G1 | US location | `location.name`, `offices[]` | JS1 contract v2 `location_ok`, unchanged. Boston passes. "Remote" passes only with US / USA / United States in the same part. "City, ST" passes only if an office in `offices[]` is in the United States. **v1.1 adds:** a location part that ends in `USA` or `United States` passes (`G1_usa_suffix`). | Aarav is in Boston and open to any US location (Omkar, JS1 decision 2026-10-26). A bare "Remote" may be remote from anywhere. v1.1: Datadog writes "New York, New York, USA", which the JS1 rule rejected. | inherited (my JS1); v1.1 addition hand-set after measuring |
| G2 | Excluded title words | `title` | Reject if the title contains any of: `staff`, `principal`, `distinguished`, `director`, `head`, `vp`, `vice president`, `chief`, `manager`, `intern`, `internship` | Staff and above ask for far more than ~2 years. Managers and heads are not individual engineers. Aarav graduated, so internships are out. | `intern`, `vp`, `vice president`, `chief`, `director` inherited from greenhouse-watch `exclude_title_patterns`; the rest hand-set |
| G3 | Years too high | `content` | Reject if the **smallest** stated minimum is **more than 3** years (see 1c) | Omkar's JS1 labeling rule: "it counts only if it asks for about 3 years or fewer". Taking the smallest keeps a posting that offers any path at ≤ 3. | inherited (Omkar's JS1 labeling rule, 2026-10-26) |

### 1b. Score (points)

| ID | Rule | Field | Points | Reason (one line) | Origin |
|---|---|---|---:|---|---|
| T1 | A role phrase is in the title: `software engineer`, `software developer`, `backend engineer`, `back-end engineer`, `back end engineer`, `frontend engineer`, `front-end engineer`, `full stack engineer`, `full-stack engineer`, `fullstack engineer`, `platform engineer`, `infrastructure engineer`, `site reliability engineer`, `devops engineer`, `cloud engineer`, `data engineer` | `title` | +3.0 | These are the roles Aarav has held or that mostly mean writing and running software, like his co-op | weight inherited (greenhouse-watch `title` 3.0); phrase list hand-set |
| T2 | No T1 phrase, but `engineer` or `developer` is in the title and no non-software phrase is: `sales engineer`, `solutions engineer`, `support engineer`, `customer engineer`, `field engineer`, `hardware`, `mechanical`, `electrical`, `developer relations`, `business developer`; **v1.2 adds** `developer advocate`, `developer advocacy`, `developer engagement`, `presales engineer`, `escalations engineer`, `it systems engineer`, `security compliance engineer`, `network engineer` | `title` | +1.5 | Matches Omkar's "close engineering role" (for example "Lead Engineer, Applied AI") but counts it as weaker evidence than a named SWE title. v1.2: the added phrases are sales, support, IT, developer-relations and security-compliance titles, which Omkar's JS1 labeling rule says do not count | weight inherited (greenhouse-watch `title_partial` 1.5); phrase lists hand-set |
| T3 | A seniority word is in the title: `senior`, `sr`, `lead`, `iii`, `iv` | `title` | −2.0 | Omkar's labels go by the years in the posting, not the title (see the disclosure), so this lowers the score instead of rejecting | hand-set |
| K1 | Each distinct **shipped** skill (`skills.languages`, `backend_automation`, `database_cloud`, `devops_cicd`) found in `content`, at most 8 | `content` | +1.0 each | The same evidence as JS1 clause C, now graded instead of pass/fail | weight and cap of 8 inherited (greenhouse-watch `skill` 1.0, `max_skill_hits` 8) |
| K2 | Each **familiar-but-not-shipped** skill (`Rust`, `Terraform`) found | `content` | +0.25 each | The persona is honest that these were never shipped, so they count for little | inherited (greenhouse-watch `skill_unshipped` 0.25) |
| Y1 | Level evidence: a stated minimum of 3 years or fewer, **or** an entry phrase (`new grad`, `new graduate`, `entry level`, `entry-level`, `early career`, `early-career`, `university grad`, `recent graduate`) in the title or content | `title`, `content` | +1.0 (once) | A posting that says it fits ~2 years is better evidence than one that is silent | hand-set |

**Threshold: keep if score ≥ 5.0** (hand-set). 5.0 = a named SWE title (3.0) plus 2 shipped skills (2.0). That mirrors JS1 clause C ("≥ 2 skills") for a posting whose title already says Software Engineer.

**Close call:** a gate-passing posting whose score is within 1.0 of the threshold (4.0 ≤ score < 6.0). The audit reads these first, because that is where misses live (Lectern's `audit_rejects.py` near-miss idea).

### 1c. How years are read (G3 and Y1)

A **years statement** matches one of these, with 0 to 60 characters before the word `experience`:

- `N+ years`, `N + years`, `N or more years`, `at least N years`, `minimum of N years`, `N-M years`, `N to M years` (in a range, N is the minimum)

**(v1.5)** An explicit `N+ years` also counts without the word `experience` (Toast: "Solid engineering experience. 5+ years building and shipping software").

`N` is written as digits, 0–20. The **stated minimum** is the smallest `N` over all such statements. **(v1.6)** A statement right after `with`, `including`, `of which` or `plus` is a sub-requirement and does not set the minimum, unless every statement is one ("5+ years of engineering experience, **with** 2+ years building AI/ML"). If no statement matches, the level is **unknown**: G3 does not fire, and Y1 fires only on an entry phrase.

Known gap, written down before measuring: numbers written as words ("three years") are not read. Section 3 uses this as a test of the abstention rule.

---

## 2. The evidence rules (source-grounded shortlist)

Every kept posting carries a justification. It is a list of **claims**, one per rule that fired, and **each claim is checked against the posting's own text**. A claim's label is decided by the posting alone, never by the persona and never by Claude.

| Claim | Text | Supported when | Contradicted when | Insufficient when |
|---|---|---|---|---|
| CL-role | "The title names a software-engineering role" | `title` contains a T1 phrase (quote it) | `title` contains a non-software phrase from T2's list | only T2 fired (a generic "engineer" title) |
| CL-loc | "The job is in the US" | G1 passes; quote `location.name` (and the US office) | `location.name` is non-empty and G1 fails | `location.name` is empty, or is "Remote" with no country |
| CL-level | "The posting is open to someone with 3 or fewer years" | a years statement with minimum ≤ 3, or an entry phrase; quote it; and no statement > 3 | any years statement has minimum > 3 (quote it) | no years statement and no entry phrase |
| CL-skill:X | "The posting asks for X" (X is a skill Aarav shipped) | X appears inside a **requirements section** (see below); quote the sentence | X appears only in a negated phrase (`no X`, `not X`, `without X`) | X appears, but only **outside** a requirements section: company blurb, team description, "nice to have", benefits |

**Requirements section:** the text after a heading that contains one of `requirements`, `qualifications`, `what you'll need`, `what you need`, `you have`, `you bring`, `must have`, `what we're looking for`, `who you are`, `about you`, `you'll need`, `skills`. It ends at the next heading that contains `nice to have`, `bonus`, `preferred`, `plus`, `benefits`, `perks`, `about us`, `compensation`, `pay`, **(v1.4)** `technologies we use`, `our tech`, `tech stack`, `our stack`, or at the end of the posting. **(v1.3)** A heading phrase also matches with a trailing `s`, so "Nice to Haves" ends the section. A heading that matches neither list leaves the state as it was, and a heading line inside a requirements section is itself part of it (so a sub-heading "Python" counts). Headings are the `<h1>`–`<h4>`, `<strong>` and `<b>` texts in Greenhouse HTML, the `lists[].text` labels in Lever, and lines that end in `:` in plain text (Ashby).

**Relevance is not entailment.** K1 counts a skill wherever it appears, because that is what "relevant" means here: the word is on the page. CL-skill asks a stronger question: does the posting *ask for* it? A posting can be kept on K1 points and still have skill claims that are **insufficient**. The shortlist shows both and never upgrades one into the other.

### The abstention rule ("I cannot tell")

The agent says **"I cannot tell"** instead of a yes or no in these cases:

| ID | When | What it says instead |
|---|---|---|
| AB1 | `content` is shorter than 300 characters after cleaning, or `title` is empty | posting verdict `cannot_tell`: "the posting text is too short to check any claim" (it is neither kept nor rejected, and it goes to the audit) |
| AB2 | a kept posting has **fewer than 2 supported CL-skill claims** | shortlist status `cannot_tell`: "the words matched, but the posting does not say it asks for them" |
| AB3 | a kept posting's CL-level is **insufficient** | it stays on the shortlist with "level: I cannot tell from the posting". It is never shown as "entry-level" |
| AB4 | a source is missing, errored, or returned 0 postings | for that source: "I cannot tell whether <company> has matching postings". Never "0 matches" |

A posting is **worth reading** (the top group on the shortlist) only if CL-role, CL-loc and CL-level are **supported** and at least 2 CL-skill claims are supported. Every other kept posting is listed under **"kept, but I cannot tell"**, with the reason.

---

## 3. The expected sources

| Source | ATS | Why it is watched | Fields the agent must see | Expected answer if missing |
|---|---|---|---|---|
| `greenhouse:klaviyo` | Greenhouse | Boston HQ; carried over from JS1 and JS2 | `id`, `title`, `location.name`, `offices[].location`, `content`, `absolute_url` | AB4 for Klaviyo |
| `greenhouse:hubspotjobs` | Greenhouse | Boston HQ (JS2) | same | AB4 |
| `greenhouse:toast` | Greenhouse | Boston HQ, many SWE roles (new in JS3, probed 2026-11-17: HTTP 200) | same | AB4 |
| `greenhouse:datadog` | Greenhouse | has a Boston office (new in JS3, probed 2026-11-17: HTTP 200) | same | AB4 |
| `ashby:linear` | Ashby | second ATS (JS2) | `id`, `title`, `location` (+ secondary), `isRemote`, `address.postalAddress.addressCountry`, `descriptionPlain`, `jobUrl`, `isListed` | AB4 |
| `ashby:webflow` | Ashby | JS2 found that Webflow moved from Greenhouse to Ashby; JS3 watches the right board | same | AB4 |
| `lever:spotify` | Lever | third ATS (JS2) | `id`, `text`, `categories.allLocations`, `country`, `workplaceType`, `descriptionPlain`, `lists[]`, `additionalPlain`, `hostedUrl` | AB4 |
| `greenhouse:webflow` | Greenhouse | **kept on purpose** as a known-empty source: JS2 saw HTTP 200 with `{"jobs":[]}` | — | must be reported as AB4 ("I cannot tell"), **not** as "0 matches" |

**Missing fields:** a missing `title` or a `content` shorter than 300 characters triggers AB1. A missing `location.name` makes CL-loc insufficient, so G1 fails and the posting is rejected with the reason "no location", which the audit can see. A missing `absolute_url` is shown as "(no link)" and has no effect on the verdict.

**Coverage line:** every shortlist starts with "covered N of 8 sources", followed by each source's status. A shortlist with any AB4 source is marked **incomplete**.

---

## 4. Wrong versions the tests must catch

Each is a plausible filter or ranking that looks right. `tests/mutants/` holds one file per wrong version, and `tests/run_mutants.py` must report each as **KILLED** (at least one test fails), after a control run on the real code passes.

| ID | Wrong version | Why it is plausible | What it gets wrong |
|---|---|---|---|
| WV1 | Skill match by **substring** | "just search for the skill" | `Java` scores on every JavaScript posting; `SQL` on PostgreSQL |
| WV2 | **Rank by raw keyword count**: no gates, no cap | "more matching skills = better fit" | a Staff Engineer posting that lists 10 skills outranks an entry SWE posting with 3 |
| WV3 | **Relevance as entailment**: CL-skill is supported whenever the word appears anywhere | "it says Python, so it asks for Python" | a skill mentioned in the company blurb or "nice to have" becomes a supported requirement |
| WV4 | **First number before "years"** as the requirement | "the first number is the requirement" | "for over 10 years, Toast has…" rejects a posting that asks for 2 years |
| WV5 | **No abstention**: a missing or short `content` becomes `reject` | "no evidence = not relevant" | an empty posting is silently thrown away instead of being flagged "I cannot tell" |
| WV6 | **Bare "Remote" passes G1** | "remote means anywhere, including the US" | a "Remote – EMEA" posting is kept for a Boston candidate |
| WV7 | **Empty source counted as "0 matches"** | "the board answered 200 OK" | the known-empty `greenhouse:webflow` is reported as covered with nothing to show |

---

## 5. Change log

Every rule added, cut or rejected **after measuring** is recorded here with the measurement that caused it. Version 1.0 is the state before any measurement.

| Version | Date (UTC) | Change | Measured on | Result | Decided by |
|---|---|---|---|---|---|
| 1.0 | 2026-11-17 06:15 | initial filter, written before any JS3 code | — | — | Claude Code proposal (see the confirmations table) |
| 1.1 | 2026-11-17 06:20 | **added** to G1: a location part ending in `USA` / `United States` is a US location | v1.0 vs v1.1 on the whole corpus (1,142 postings; recomputed from `runs/2026-11-17T06-16-31Z/filter-v1.0/records.jsonl.gz` and `filter-v1.1/records.jsonl.gz`) | **120** postings change from G1-fail to G1-pass (118 Datadog, 2 HubSpot), 78 of them "New York, New York, USA" (Datadog's format). 41 of the 120 failed no other gate. **0 keep/reject verdicts flipped**: every one of them still fails G2, G3 or the threshold. The change fixes the *reason* for 120 rejects, and those reasons are what the audit reads. (Erratum: this row first said 133 and "on G1 alone"; an independent review recomputed it, see FRICTIONAL) | Claude Code (measured); **[Omkar]** to confirm |
| 1.2 | 2026-11-17 06:21 | **added** 8 phrases to T2's non-software list (`developer advocate`, `developer advocacy`, `developer engagement`, `presales engineer`, `escalations engineer`, `it systems engineer`, `security compliance engineer`, `network engineer`) | every T2 title in the v1.1 summary (66 postings, 53 titles), read one by one | **0 verdicts flipped; 14 scores fell by 1.5; 1 close call removed** ("Developer Advocate – Service Management", 4.5 → 3.0). False friend: `developer` in "Developer Advocate" earned T2 points. `presales engineer` slipped past `sales engineer` because whole-word matching does not see "sales" inside "PreSales" | Claude Code (measured); **[Omkar]** to confirm |
| 1.3 | 2026-11-17 06:25 | **changed** heading matching: a heading phrase also matches with a trailing `s` (`plural_headings`) | the v1.2 shortlist (`shortlist/shortlist-v1.2.md`), read posting by posting | Toast's "Special Sauce* (Nice to Haves)" did not end the requirements section, because whole-word matching does not find `nice to have` inside "Haves". **2 claim labels flipped** supported → insufficient (Toast Vision AI: TypeScript; Toast SWE II Backend: Java). 0 keep/reject verdicts change (heading rules only affect claims) | Claude Code (found while reading); **[Omkar]** to confirm |
| 1.4 | 2026-11-17 06:25 | **added** 4 tech-stack headings to the end list (`technologies we use`, `our tech`, `tech stack`, `our stack`) | the v1.3 shortlist | The same Klaviyo heading "Technologies We Use (not exhaustive)" was labelled *insufficient* on one posting and *supported* on another, only because on the second it came after a requirements heading. A stack list says what the team uses, not what it asks for. **12 claim labels flipped** supported → insufficient, on 3 postings. The top-scoring posting (Klaviyo "Software Engineer II, Test Frameworks & Tooling", 11.25) moves from *worth reading* to *kept, but I cannot tell* (only 1 of its 7 matched skills is asked for). 0 keep/reject verdicts change | Claude Code; **[Omkar]** to confirm |
| 1.5 | 2026-11-17 06:36 | **added** to 1c: an explicit `N+ years` counts even without the word `experience` (`years_plus_alone`) | the audit sample: the Claude second rater rejected 2 kept postings, quoting a years requirement the filter had not read (cards 2 and 49). Then v1.4 → v1.5 on the whole corpus | Toast "Senior Software Engineer, Vision AI" ("Solid engineering experience. 5+ years building and shipping software in production") and Webflow "Senior Infrastructure Engineer" ("Have 5+ years owning and operating cloud infrastructure") had **no** years statement under v1.4. On the corpus: **3 verdicts flip**: those 2 keep → reject, and 1 reject → keep: Klaviyo "Full Stack Software Engineer – People Systems", whose new minimum 2 comes from "…with **2+ years** building AI/ML…", a sub-requirement of a 5+ year requirement. That third flip is a **new error** made by the smallest-minimum rule; v1.6 is the fix. 133 minimums change in total (79 postings newly fail G3, 16 newly pass). All 79 + 16 were checked only by count, not read | Claude Code (measured); **[Omkar]** to confirm |
| 1.6 | 2026-11-17 06:37 | **added** to 1c: a statement right after `with` / `including` / `of which` / `plus` does not set the minimum (`years_ignore_sub`). **Rejected** while measuring: `and` in the same list, because "a BS **and** 2+ years" is usually the main requirement | v1.5 on the whole corpus | **1 verdict flips** (the People Systems posting, back to reject: minimum 5). 45 minimums change. Kept: 7 postings, close calls: 4 | Claude Code (measured); **[Omkar]** to confirm |
| (bug fix, no version) | 2026-11-17 06:24 | code bug, not a rule change: a skill written as a sub-heading inside a requirements section (Klaviyo's "Python" heading) was never searched, because heading lines were skipped | v1.2 shortlist | 1 claim flipped insufficient → supported (Klaviyo Conversational Products: Python). *Not reproducible from the folder:* the pre-fix shortlist was overwritten when it was regenerated; the flip was seen in the console at the time. The rule text already said "inside a requirements section"; the code did not do it | Claude Code |
| (bug fix, no version) | 2026-11-17 06:32 | code bug found by `tests/test_evidence.py::test_inline_bold_is_not_a_heading` (written before this fix): an inline `<strong>Python</strong>` inside a sentence was split into its own heading line, which the rule says it is not | v1.4 shortlist, before and after | **0 claim labels flipped** on the real shortlist; the constructed case is now right | Claude Code |
| — | 2026-11-17 | **rejected:** add bare "`N years … experience`", "`Minimum N years`" and "`+N years`" to 1c | v1.2 on the whole corpus | 13 postings have such a statement and no v1 statement. All 13 are non-engineering (Account Executive ×9, Product Manager ×2, Executive Assistant, Tax Analyst): **0 verdicts would flip**. The gap stays, and is documented in section 2 (abstention counterexample) | Claude Code |
| — | 2026-11-17 | **rejected:** cut `early-career` from Y1's entry phrases, even though it is a false friend (it fired on "mentoring and developing **early-career** PMs" in a Principal PM posting) | v1.2 on the whole corpus | 2 scores change, **0 verdicts flip**: both postings fail G2 anyway. Cutting it would also lose the phrase where it is meant ("early-career program manager"). Kept, and named as a false friend in AUDIT.md | Claude Code |
| — | 2026-11-17 | **rejected:** ignore `Kubernetes` and `AWS` on Datadog (greenhouse-watch's `ignore_skills` idea) | v1.2 on the whole corpus | They fire on 48 and 42 Datadog non-engineering postings (Sales Engineer: "public cloud (AWS, Azure, GCP), Kubernetes"). Ignoring them changes 56 scores but **0 verdicts**, and would remove real evidence from Datadog's engineering postings. Kept; named as a false friend in AUDIT.md | Claude Code |

---

## 6. [Omkar] Confirmations

| Section | Confirm / change (your words) | Date |
|---|---|---|
| 1a gates G1–G3 | confirm (Omkar, typed in chat, entered by Claude Code) | 2026-11-25 |
| 1b weights and the threshold 5.0 | keep 5.0 (Omkar, typed in chat, entered by Claude Code). The dev fit on my audit labels (`experiments/FIT-THRESHOLD-dev.md`) gives 46 of 49 correct at both 4.5 and 5.0, a tie, so 5.0 costs nothing on dev | 2026-11-25 |
| 2 evidence rules and abstention AB1–AB4 | confirm (Omkar, typed in chat, entered by Claude Code) | 2026-11-25 |
| 3 sources | confirm (Omkar, typed in chat, entered by Claude Code) | 2026-11-25 |
| 4 wrong versions | confirm (Omkar, typed in chat, entered by Claude Code) | 2026-11-25 |
