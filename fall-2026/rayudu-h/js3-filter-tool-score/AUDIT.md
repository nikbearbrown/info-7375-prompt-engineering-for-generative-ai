# AUDIT.md: the reject audit (Chapter 7)

Every number here is recomputed from committed files by `python -m js3 audit`, which writes [`audit/audit-results.md`](audit/audit-results.md). That file also has the per-posting table.

## 1. What was audited, and how

- **The filter.** FILTER.md **v1.0** (commit `12c826a`) ran on everything the agent collected: **1,176 unique postings** from three live snapshots (Oct 31, Nov 7 and Nov 20) of Anthropic, Notion and Perplexity. It **kept 194 and rejected 982**; none were "cannot tell" (`filter-runs/v1.0/summary.md`).
- **The samples.** The seed (20261122) was committed first (`afe2acb`). The samples were drawn from it before any label (`c037109`). The held-out set came first, and the four sets don't overlap:
  - **held-out H:** 40 postings (20 kept, 20 rejected). They're used only in `SCORE.md` and are **not** used here.
  - **30 uniform random rejects,** drawn from the 962 rejects outside H. This is the only part of the audit that supports a rate.
  - **10 closest calls:** the 5 nearest the threshold on each side, among postings the threshold decided. Ties were broken at random. These support no rate.
  - **15 random kept postings.**
- **The labeling was blind.**
  - Hemanth labeled all 95 postings (the 55 audit and 40 held-out, shuffled together) in chat, in 10 batches, on Nov 22, 2026, between 2:23 and 3:24 PM EST.
  - Each batch was committed as it was done (`audit/labels.csv` has a timestamp on every row).
  - No score, decision or sample set was shown. Each item showed the title, the location and a 400-character excerpt, using the same rule for every posting (`js3/labeling.py`).
  - The question was: "Is this worth Priya's time to read in full?" (y / n / ?). Hemanth answered y or n every time; no "?".
  - One typing slip, "888 n", was recorded as item 88, with a note.

## 2. How often the filter was wrong (filter v1.0 against Hemanth's verdicts)

| Stratum | n | filter wrong | wrong / n | Wilson 95% |
|---|---:|---:|---:|---|
| random rejects | 30 | **11** | 37% | 22%–54% |
| closest calls | 10 | 3 | 30% | 11%–60% |
| random kept | 15 | 2 | 13% | 4%–38% |

**What a sample of 30 can honestly say.**
- Hemanth would have wanted **11 of 30** randomly drawn rejects.
- With 95% confidence, between **22% and 54%** of the rejects are postings he would want. That's roughly **210 to 524** of the 962 rejected postings outside the held-out set.
- This is an **estimate from one sample of 30**, not a measured rate. The interval is wide because 30 is small.
- The sample does establish that the filter's misses are **not rare**. Even the bottom of the interval is about one reject in five.
- It cannot say how the misses split across the rules for the whole corpus. Section 3 gives counts within the sample only.

The kept side is better: 2 of 15 kept postings were not wanted. With 15 postings, that sample can't pin the rate down (4%–38%).

## 3. Where the misses come from (random rejects, by the rule that rejected them)

| Rule | Misses (marked relevant) | Correct (marked not relevant) |
|---|---:|---:|
| R2 title exclusions (Manager, Sales, Recruiter, …) | 0 | 13 |
| R3 "security clearance" | 0 | 1 |
| R8 "must name one of Priya's skills" | **7** | 3 |
| R10 score below the threshold | **4** | 2 |

- **The exclusions held: 14 of 14 correct.** Every posting excluded by title or by "security clearance" in this sample was one Hemanth didn't want.
- **R8 caused most misses.** These postings name none of Priya's skills, but Hemanth wanted them:
  - #49 Software Engineer, Observability & Profiling
  - #24 Staff+ Software Engineer, Claude Science
  - #58 Developer Relations, Platform
  - #66 Developer Education Lead, Claude Platform
  - #17 Hardware Systems Architect
  - #39 Data Center Architect, CSA
  - #76 Data Center OFE Sourcing Lead

  No word in Priya's skill list appears in them. This is a **limit of keyword matching**, as Lectern's audit says: a miss no word could catch shows what keywords can't do. It isn't fixable by adding a word.
- **R10:** three of the four threshold misses are one false friend (section 4). The fourth is #14, "Research Scientist, Life Sciences": Python is its only match, and it has no role word.
- **Wrong on the kept side:**
  - #94, Notion's "Security Engineer, Detection and Response", scored 6.5. Its skills are real requirements ("strong SQL or Python skills", "Hands-on experience with AWS"), but in a security-detection job.
  - #5 and #65 are Perplexity billing and crawler roles that also list Python and AWS.

  The words matched for the right reason, but **a skill match isn't a role fit.**

## 4. False friends: words that matched for the wrong reason

| Word | Rule | Wrong reason | Size | Cost in the audit |
|---|---|---|---|---|
| **"Staff"** | R9 seniority (−2.0) | Perplexity titles every engineer **"Member of Technical Staff"**, a company-wide title, not a level | 66 titles, all Perplexity | 3 of the 11 random-reject misses (#23, #41, #61) and 1 closest-call miss (#95) |
| **"Data"** | R1 role word (+3.0) | **"Data Center"** roles (construction, power, cooling, sourcing) are not data roles | 35 titles | none today: every one is already rejected by R8 |
| **"Account"** | R2 exclusion | **"Account Abuse"** and **"Account Creation"** are engineering teams, not sales | 3 engineering titles | not in the sample. It was measured before Hemanth chose the bare word (FILTER.md section 6) |

The named false friend is **"Staff"**: the seniority rule fired because of the company's naming habit, not the job's level. "training", Lectern's false friend, appears in all 815 Anthropic postings. It isn't a rule word in this filter, so it couldn't mislead it. It would if it were ever added.

## 5. Rules added, cut or rejected after measuring

All four changes were measured on the 55 audit labels and on the whole corpus, then decided by Hemanth: **"X1 accept, X2 reject, X3 reject, X4 Reject"** (Nov 22, 3:33 PM EST). The full entries are in the FILTER.md changelog (section 6).

| Change | Correct / 55 | Kept in corpus | Decision |
|---|---:|---:|---|
| v1.0 (before) | 39 | 194 | — |
| **X1:** "Staff" inside "Technical Staff" is not seniority | **42** | 212 | **added → v1.1** |
| X2: drop the seniority penalty | 42 | 254 | rejected: no better than X1, 42 more kept, and it reverses Q3 |
| X3: drop the skill requirement | 40 | 266 | rejected: +1 correct for 72 more kept |
| X4: "Data Center" is not the role word "Data" | 39 | 194 | rejected: no measured effect today |

**These gains are in-sample.** The same 55 labels that showed the problem also measured the fix, so the 39 → 42 flatters X1. In the audit sample, X1 fixes #23, #41, #61 and #95, and adds one wrong keep: #51, a crawler SRE Hemanth didn't want. The held-out test of v1.1 is in `SCORE.md`.

## 6. A tension the audit exposed

At the gate, Hemanth chose to penalize seniority (Q3, the recommended default). In the blind labels, Hemanth marked **11 of the 14** senior-titled audit postings as worth reading. Examples: "Staff+ Software Engineer, Kubernetes Platform" and "Principal Engineer Capacity/Compute".

Hemanth kept the rule (X2 rejected). The plan is to let the shortlist's level claim (C3) catch level problems with a quote, such as "8+ years". So the stated rule and the verdicts disagree, and that disagreement is recorded, not resolved.

## 7. What this audit does not show

- **The relevance judgment.** One person (Hemanth) judged relevance, once. The judgments weren't checked by a second labeler or a second pass.
- **What the labels were based on.** Each verdict came from the title, the location and a 400-character excerpt, not the full posting. A verdict on a posting read in full might differ.
- **What "relevant" means here.** It is Hemanth's "worth Priya's time to read in full". It's broader than Priya's profile targets: Hemanth wanted data center architecture, hardware and sourcing roles. The filter is measured against these labels, not against Priya's profile.
- **The closest calls and the kept sample.** Neither supports a corpus-wide rate.
- **Whether X1 helps on unseen postings.** That's the held-out test in `SCORE.md`.
