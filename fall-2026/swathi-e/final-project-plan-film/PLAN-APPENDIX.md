# Plan Appendix: Supervised Job-Search Agent with Sponsorship Evidence

**Final Project Film appendix, INFO 7375, Fall 2026**
Author: Swathi Baba Eswarappa · Drafted with Claude Chat, revised 2026-11-22 after review with ChatGPT; decisions recorded 2026-11-22 · **Status: plan approved; final text pending my review**

This appendix holds the detail the film keeps out of the executive summary. It separates **completed work (JS1–JS3, past tense, with commits)** from **planned work (final project, future tense)**. Nothing in sections 3–7 has been built or measured. Every threshold is a proposed target, not a result.

---

## 1. What I am building

A supervised job-search agent for international students. It collects early-career postings from public company job boards, filters them with written rules, and for each remaining posting shows two kinds of evidence side by side: what the posting itself says about sponsorship or work authorization, and the employer's historical H-1B labor condition filings with the US Department of Labor. It flags differences between the two. It does not apply, send messages, or modify any outside system; a person approves, refuses, or defers every job.

## 2. Completed work this builds on (JS1–JS3)

All figures come from committed artifacts on the JS3 branch `js3-filter-tool-score-swathi-e` (final commit `c2e624e`, PR #48).

| What | Result | Source |
|---|---|---|
| Filter rules written before code | FILTER.md Version 1, 2026-11-17 | `0f689b8` |
| Live collection, 2026-11-17 21:47 EST | 1,832 public postings: Databricks 901, Stripe 789, Plaid 142 | `d4a3b94` |
| Filter v1 results | 4 shortlisted, 2 not shortlisted, 1,800 rejected, 26 cannot tell | `beb8a26` |
| Hand audit (sampled by group, on **v1** results) | 48 postings: 30 random rejects, close calls, cannot-tell cases, all 4 shortlisted | `fed055f`; report `815064e` |
| 30 random rejects (original audit result) | 0 judged relevant. A random sample: the true false-reject rate among the 1,800 v1 rejects could still be up to about 10% (95%, rule of three). Not a measured rate. | `815064e` |
| Audit disclosure | Rows 5–48 were judged by me against the posting text after seeing an AI draft from ChatGPT (recorded in `how_judged`). Row 35 adjudicated not relevant, recorded beside the original label. | `fed055f`, `40f130e` |
| Filter **v1.1** (subsequent improvement, after the audit) | 7 verdicts changed on the same saved batch: 6 cannot tell → rejected, 1 rejected → cannot tell. Shortlist unchanged at 4. The audit was not re-run on v1.1. | `2c3ef12`, `7672a21` |
| Held-out threshold experiment | 20 held-out postings labeled; threshold 5 kept, threshold 6 rejected after measuring | `b09f9ce`, `e8299de` |
| Source-grounded shortlist | 21 claims: 17 supported, 4 insufficient, 0 contradicted; all 4 shortlisted postings marked "needs human check" | `1442650`, `f4dadb2`, `bf15eaf` |
| Read-only MCP tool server | Contract and tests before code; 42 tests passed after implementation; path-traversal request rejected | `f1c24dd`, `ae93c19`, `de027ed`, `4fd59d6` |

Earlier: JS1 (contract and watch, Databricks) and JS2 (loop, tools and stop rules across Databricks, Stripe and Plaid; a finished-wrong-answer demonstration caught by an independent check).

## 3. Data sources (planned use)

| Source | Contents used | Access | Boundary label |
|---|---|---|---|
| Greenhouse job board API (`boards-api.greenhouse.io`) | Public job postings | Public, no key | public |
| Ashby job board API (`api.ashbyhq.com/posting-api/job-board/{slug}`) | Public job postings | Public, no key | public |
| DOL OFLC LCA disclosure files (H-1B, H-1B1, E-3) | Case-level records: case number, case status, visa class, employer name, trade name, job title, worksite, fiscal year | Free download from the DOL Performance Data page; quarterly, cumulative per fiscal year | public (contains personal fields; see below) |
| Priya Nair persona files | Fictional résumé and targets | Already in repo | synthetic |
| USCIS H-1B Employer Data Hub | Not used in the core plan. Mentioned in the film as existing work only. | — | — |

### 3.1 What an LCA record does and does not show

An employer must obtain a certified Labor Condition Application from the Department of Labor before filing an H-1B petition (Form I-129) with USCIS (20 CFR Part 655, Subpart H). A certified LCA is therefore **historical evidence of sponsorship activity** by that employer. It does **not** show that a petition was filed or approved, that a visa was issued, how many people were hired, or that the employer will sponsor this job or any future one. Card wording will follow this, for example: "Department of Labor records show N certified H-1B labor condition applications filed by [legal name] in fiscal years X–Y." Certified-Withdrawn cases, if any, appear on a separate line and are not part of N. When nothing qualifies, the card says: "No qualifying record found in the selected datasets (H-1B, certified, fiscal years X–Y)." That wording does not mean the employer has never sponsored. The agent will not state "this employer sponsors."

### 3.2 Filtering rules for the DOL files (written before code)

Field names and values below were checked against the DOL record layout for LCA disclosure files, fiscal year 2024 Q1. They will be re-checked against the FY2026 layout before any code is written; any difference will be recorded.

| Rule | Detail |
|---|---|
| Visa class | Keep only `VISA_CLASS = "H-1B"`. Exclude `E-3 Australian`, `H-1B1 Chile`, `H-1B1 Singapore`, which are different classifications and are not H-1B evidence. |
| Case status | Only `Certified` enters the primary count. `Certified-Withdrawn` is listed separately, labeled as such, and excluded from the primary count. `Denied` and `Withdrawn` are excluded. |
| Deduplication | Each disclosure file is cumulative within its fiscal year, with one record per case number based on the most recent determination. The plan uses the final (Q4) file for each completed fiscal year and the latest available file for the current year. If more than one file covering the same period is loaded, records are deduplicated by `CASE_NUMBER`, keeping the record with the latest `DECISION_DATE` (then the most recent file). The same rule applies if a case number appears in two fiscal-year files. The number of duplicates removed is logged on every run. |
| Employer identity | Match on `EMPLOYER_NAME` (legal business name) and `TRADE_NAME_DBA` only. |
| Placement records | Rows where workers are placed at a **secondary entity** are attributed to the filing employer, never to the secondary entity. An LCA filed by a staffing firm for work at Stripe is not Stripe's record. |
| Fiscal years | State the fiscal years covered on every card; record which disclosure files and versions were used. |
| Personal data | The files include names, phone numbers and emails of employer contacts, attorneys and preparers. These columns are dropped at load, never displayed, logged, or committed. Raw files are not committed; their SHA-256 and download date are recorded. |

### 3.3 Posting language versus employer history

A posting that says "no sponsorship" or "US citizens only" and an employer with certified H-1B LCAs are **not necessarily contradictory**: the employer may sponsor for other roles, may have changed policy, or the role may have specific requirements. So the agent will:

1. Treat an **explicit posting-level eligibility restriction as the primary signal** for that job (it decides the card's headline).
2. Show the employer's LCA history as **context**, labeled "historical employer activity".
3. Flag the pair as a **difference to review**, not as an error or contradiction.

The film and the cards will use "difference", not "contradiction", for this case.

## 4. Resources

| Need | What I have | Notes |
|---|---|---|
| Model access | Claude Code on my Northeastern premium seat, which covers model access subject to its usage limits | Scripted `claude -p` calls confirmed working with no API key on 2026-10-25 (used for the JS1 judges) |
| Token credits | No separate credits needed | The seat's usage limits are a real constraint; the run budget respects them |
| Accounts / access | GitHub fork (BESWATHI); job board APIs need no key | |
| Data | Free public downloads | LCA files are large; processed locally |
| Compute | My laptop | Matching and checking are deterministic code |

## 5. Agent design (planned)

**Loop.** Collect → filter → match → check → record → stop.

**Memory and state.** A state file of postings already seen; the data file versions used (with SHA-256); an append-only audit log of every run; a decision register of every human decision.

**Tool permissions (enforced in code).**
- **External sources are read-only:** job board APIs (GET only, allow-listed hosts, rate-limited) and local copies of DOL files.
- **Internal writes are allowed only to allow-listed project paths:** `state/` (memory), `audit/` (run logs), `decisions/` (human decisions). Any other write is refused by the code and logged.
- **No tool exists** to apply, send email or messages, or change any outside system.
- Tests attempt forbidden actions (writes outside the allowed paths, non-allow-listed hosts, any send) and must see them refused.

**Budget.** Maximum postings processed and maximum model calls per run, set in a config file.

**Deterministic stop.** The run stops when the queue is empty, the budget is exhausted, or an error limit is reached, or when it reaches the human gate with items waiting. It never stops because a model says it is finished.

**Human gate.** For each job, I approve, refuse, or defer. The decision is stored with a SHA-256 hash of the exact evidence card I was shown; a decision whose hash does not match the current card is rejected.

**Tests written before code** (committed with the contract, expected to fail before implementation):

| Area | Test |
|---|---|
| Budget enforcement | A run with a budget of N postings processes exactly N and stops with reason `budget`; a model-call budget of M allows no call M+1. |
| Deterministic stopping | Each stop reason (`queue_empty`, `budget`, `error_limit`, `awaiting_gate`) is triggered by a fixture. The same inputs and config produce the same stop reason, the same processed set and the same audit record apart from timestamps. Model output saying "done" has no effect on stopping. |
| Stale evidence hash | A decision made on a card that has since changed is rejected and logged; replaying an old decision against a new card is rejected. |
| Permissions | Writes outside `state/`, `audit/`, `decisions/`, requests to non-allow-listed hosts, and any send are refused and logged. |
| Data handling | Only `VISA_CLASS = "H-1B"` enters evidence; `Certified-Withdrawn` is listed separately and excluded from the primary count; duplicate case numbers are removed by the rule in §3.2; personal-data columns are absent after load. |
| Label isolation | The matcher and the alias-building step cannot read the held-out label file (§6). |

## 6. Matching and the independent checker (planned)

**Employer identity table.** For each employer in scope, an alias table maps the job-board company to its legal and trade name(s), each with a source. To keep held-out answers out of development:

1. Aliases come **only from company-published sources** (for example, the company's own legal or terms page), never from DOL records and never from the label files.
2. For held-out employers, the aliases are compiled and committed (with SHA-256) **before** I look those employers up in the DOL files to label them, and are frozen before scoring.
3. The held-out labels (which DOL records belong to which employer) live in a separate file. The matcher and the alias-building step cannot read it; a test enforces this. The checker uses the alias table, not the labels.
4. Development employers' aliases may be refined during development. Any held-out alias changed after labeling is logged, and results that depend on it count only as a regression test.

**Matcher.** Normalizes case, punctuation and legal suffixes (Inc., LLC, Corp.) and matches against the alias table. Anything uncertain is reported as "No qualifying record found in the selected datasets", never as a guess.

**Independent checker** (separate code that does not import the matcher):

1. **Source attribution:** re-opens the hash-verified raw DOL file and confirms each cited case number exists in that file version.
2. **Employer identity:** confirms the record's `EMPLOYER_NAME` or `TRADE_NAME_DBA` exactly equals a reviewed alias for *this* employer. A real case number from a different employer fails.
3. **Classification and status:** confirms `VISA_CLASS = "H-1B"` and an allowed `CASE_STATUS` for every cited record.
4. **Claim support:** recomputes the counts and fiscal years from the cited records and confirms the card's sentence states exactly that, using only the approved wording template. Posting quotes must appear verbatim in the saved posting.
5. **Result:** any failure blocks the card from reaching the gate and is logged.

## 7. Evaluation methodology (planned)

### 7.1 Label sets and protocol

- **60 employers, hand-labeled by me** against the DOL files before the matcher exists: 20 development, 40 held-out.
- **Held-out composition (planned):** at least 25 employers with qualifying records (certified H-1B LCAs in the selected fiscal years) and at least 10 with no qualifying records, including deliberately tricky cases (legal suffixes, trade names, look-alike names, staffing placements).
- Employers come from public job boards beyond Databricks, Stripe and Plaid. Planted cases are labeled SEEDED.

**Held-out protocol.**
1. The held-out labels are committed, with their SHA-256 recorded, before the matcher is written.
2. Development and tuning use only the 20 development employers. A test confirms the held-out file's hash is unchanged before the scored run.
3. The held-out set is scored once, and that first result is recorded and never overwritten.
4. If a failure leads to a fix, the original result stays in the record. Any re-run on the same 40 employers is labeled **"regression test after fix, not an independent held-out evaluation."**

### 7.2 Measures and proposed thresholds

| Measure | Definition | Proposed threshold | Why |
|---|---|---|---|
| Wrong employer match | A card attributes another employer's LCA records to this employer, or reports records for an employer with no qualifying records | 0 across all 40 | The most harmful error: it tells a student something false. Any one is a defect. |
| Missed match | Among held-out employers that **truly have** qualifying records (at least 25), the agent reports "No qualifying record found in the selected datasets" | At most 2 | Lower cost: that wording sends the student to verify rather than misleading them. Recall is computed only over employers with qualifying records and reported as a count and a share (for example, 24 of 25). |
| Correct "no qualifying record" | Among employers with **no** qualifying records (at least 10), the agent reports "No qualifying record found in the selected datasets" | All of them | Any failure here is a wrong match and is counted above. |
| Unsupported claim | Any sponsorship statement that fails the independent checker | 0 | The checker makes this testable; any occurrence breaks the evidence contract. |
| Difference detection | Planted posting-versus-history differences (SEEDED) flagged as "difference to review" with the posting restriction as headline | All planted cases | The cases are known in advance; missing one is a rule bug, not noise. |
| Deliberate failure cases | At least 5, predicted in writing first: no filings; legal-suffix variant; trade name; look-alike name; staffing placement; H-1B1/E-3-only filer | Each behaves as predicted | Required by the final project rubric. |
| Controlled failure | A wrong match triggered on purpose | Caught by the independent checker, then recovered with my review | Required; a failure only described earns nothing. |
| Unauthorized action | Any forbidden write, host or send that succeeds | 0 | Prevented by design and verified by tests that attempt them. |

### 7.3 What the results can and cannot show

The 40 held-out employers are **chosen on purpose** and over-represent hard cases. They are not a random sample of employers, so no confidence bound for a real-world error rate will be reported. Results will be reported as counts per group (with records, without records, tricky cases) and describe how the rules behave on these cases only. Zero errors would mean the rules handled these cases correctly, not that the real-world error rate is zero.

The JS3 bound in section 2 is different: it came from a random sample of the 1,800 v1 rejects, so the rule-of-three bound applies there.

### 7.4 What would tell me it failed

Any wrong match or unsupported claim on the held-out set; more missed matches than the threshold; a planted difference not flagged; the controlled failure not caught; any successful forbidden action. In that case the transfer-reflection decision will be narrow, defer, or stop, not ship.

## 8. What this project will not claim

- That an employer will sponsor, or that any visa was approved.
- That H-1B1 or E-3 records are H-1B evidence.
- A real-world error rate from the purposively chosen held-out set.
- Legal or immigration advice.

## 9. References and verification status

Checked by Claude Chat on 2026-11-22. "Opened directly" means the page or PDF itself was retrieved and read. "Search excerpt only" means the wording was seen in a search-result excerpt of that official page, but the page was not opened. "Secondary source only" means the claim was seen only on a third party's page. I must open every link myself before committing (a link is a claim).

**Opened directly**

| Reference | Claim it supports | Notes |
|---|---|---|
| DOL LCA Record Layout, FY2024 Q1: https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/LCA_Record_Layout_FY2024_Q1.pdf | Field names; `VISA_CLASS` values (H-1B, E-3 Australian, H-1B1 Chile, H-1B1 Singapore); `CASE_STATUS` values (Certified, Certified-Withdrawn, Denied, Withdrawn); personal-data contact fields; secondary-entity fields | PDF read in full. The **FY2026** layout has **not** been checked. |
| DOL OFLC Performance Data: https://www.dol.gov/agencies/eta/foreign-labor/performance | The page exists and hosts disclosure data | Page opened, but the retrieved text did not include the disclosure-data paragraphs. The "quarterly, cumulative per fiscal year, one record per case number" wording comes from a **search excerpt** of the same page. |

**Search excerpt only (official sources)**

| Reference | Claim it supports |
|---|---|
| DOL OFLC Performance Data (same page as above) | Disclosure files are released quarterly, are cumulative for the fiscal year, and contain unique records by case number based on the most recent determination (basis for the deduplication rule in §3.2) |
| DOL Foreign Labor Certification page, https://www.dol.gov/agencies/eta/foreign-labor | Announcement dated 2026-11-16 of disclosure data through FY2026 Q4 |
| 20 CFR Part 655, Subpart H: https://www.ecfr.gov/current/title-20/chapter-V/part-655/subpart-H | An employer obtains DOL certification of an LCA, then may submit the H-1B petition with it |
| USCIS, "USCIS Launches H-1B Employer Data Hub": https://uscis.gov/news/alerts/uscis-launches-h-1b-employer-data-hub | Hub launched; search by employer and fiscal year back to FY2009; approval and denial rates can be calculated |
| H1BGrader "H1B Sponsor Checker" (Chrome Web Store listing) | Extension built because job sites show no sponsorship history |

**Secondary source only**

| Reference | Claim it supports | Seen on |
|---|---|---|
| MyVisaJobs: https://www.myvisajobs.com | Employer sponsorship search and top-sponsor reports | University career-office pages (e.g. Duke); the site itself was not opened |
| Interstride H-1B Sponsorship Finder | Free extension marking sponsoring companies on LinkedIn, Indeed and Glassdoor | Yale SOM career page excerpt; Interstride's own site was not opened |

**Not verified**

- The current USCIS H-1B Employer Data Hub page URL: it could not be opened, and a third-party dataset refers to an archive location. Not linked until checked.
- The FY2026 LCA record layout (field names and values may differ from FY2024).
- Whether any existing tool already compares posting text with employer history. I found none, but did not survey all tools, so the film describes only what existing tools do well and makes no uniqueness claim.

**My own work**

| Reference | Claim it supports | Status |
|---|---|---|
| JS3 artifacts (branch `js3-filter-tool-score-swathi-e`, final commit `c2e624e`, PR #48) | All figures in section 2 | Checked against my session records, not against the repository itself. Re-check in the repo before committing. |
