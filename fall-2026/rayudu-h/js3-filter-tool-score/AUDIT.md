# AUDIT.md: the reject audit (Chapter 7)

Every number here is recomputed from committed files by `python -m js3 audit`, which writes [`audit/audit-results.md`](audit/audit-results.md). That file also has the per-posting table.

> **Read section 8 first if you read only one.** Sections 1–7 use the **first-pass** labels, as committed on Nov 22. Section 8 shows that those labels were made with a view that **never showed the experience requirement**, what changed when Hemanth labeled again with it visible, and how that reversed the audit's main conclusion. Both sets of labels are kept and reported (`python -m js3 audit --labels corrected` → `audit/audit-results-corrected.md`).

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

**These gains are in-sample.** The same 55 labels that showed the problem also measured the fix, so the 39 → 42 flatters X1. In the audit sample, X1 fixes #23, #41, #61 and #95, and adds one wrong keep: #51, a crawler SRE Hemanth didn't want. The first held-out set couldn't test v1.1, because none of its 40 postings is a "Technical Staff" title (`SCORE.md`, E1a).

**So X1 got its own out-of-sample test** (`audit/x1-results.md`, labels Nov 22–23):
- **The draw:** the seed was committed first. 10 were drawn at random from the 13 never-labeled postings X1 changes, and mixed blind with 10 unaffected controls.
- **The result:** Hemanth wanted **7 of the 10** X1 postings. So v1.1 was right 7 times and v1.0 3 times (Wilson 95% for 7/10: 40%–89%).
- **The controls:** both versions agree with Hemanth 9 of 10.
- **What it shows:** the direction of the in-sample gain holds on postings that played no part in choosing X1. Ten postings can't say much more.

## 6. A tension the audit exposed

At the gate, Hemanth chose to penalize seniority (Q3, the recommended default). In the blind labels, Hemanth marked **11 of the 14** senior-titled audit postings as worth reading. Examples: "Staff+ Software Engineer, Kubernetes Platform" and "Principal Engineer Capacity/Compute".

Hemanth kept the rule (X2 rejected). The plan is to let the shortlist's level claim (C3) catch level problems with a quote, such as "8+ years". So the stated rule and the verdicts disagree, and that disagreement is recorded, not resolved.

**A second tension appeared in the X1 test: location.**
- FILTER.md says location never decides (Q4).
- Hemanth marked the London posting of "Member of Technical Staff (AI Inference Engineer)" **not relevant** (item 107), but the San Francisco posting of the same title **relevant** (item 110). The two texts share 25 of their roughly 35 sentences.
- The two Belgrade postings in that test (items 97 and 115) were also marked not relevant.
- That doesn't prove location drove the verdicts; other differences exist. It's the clearest case where the written rule and the hand verdicts may part ways. It is recorded and not acted on.

## 7. What this audit does not show

- **The relevance judgment.** One person (Hemanth) judged relevance, once. The judgments weren't checked by a second labeler or a second pass.
- **What the labels were based on.** Each verdict came from the title, the location and a 400-character excerpt, not the full posting. A verdict on a posting read in full might differ.
- **What "relevant" means here.** It is Hemanth's "worth Priya's time to read in full". It's broader than Priya's profile targets: Hemanth wanted data center architecture, hardware and sourcing roles. The filter is measured against these labels, not against Priya's profile.
- **The closest calls and the kept sample.** Neither supports a corpus-wide rate.
- **Whether X1 helps on unseen postings.** That's the held-out test in `SCORE.md`.

## 8. The labeling view left out the deciding fact (Nov 23–24, 2026)

**How it came up.** Before signing, Hemanth explained the senior-role verdicts: "I marked senior roles worth reading because I did not see the experience in job description, I can always label them again, but I want to create a good project from this."

**Measured** (`js3/labeling.py`, `states_years`):
- Of the 115 postings Hemanth had labeled, **90 state a number of years of experience** somewhere in their text.
- The first view, 400 characters starting at "About the role", showed that requirement in **0 of the 90**. The requirements section always comes later.
- **67** of the 90 ask for 5 years or more, and Hemanth had marked **31** of those "worth reading".

**The second pass** (Hemanth chose option "a", relabel all 90):
- **Setup:** the seed (`audit/relabel-seed.json`) and the list in a seeded order (`audit/relabel-list.json`) were committed before the first item was shown.
- **The new view (v2):** the same rule for every posting, showing the title, the location, a 250-character summary, and **every "N years" phrase with about 110 characters around it, verbatim**.
- **A defect, fixed before any label:**
  - the first version of view v2 cut Greenhouse text at sentence ends, which that text doesn't have, so 4 of the first 10 items showed no years phrase;
  - Claude caught it before Hemanth answered and fixed it; the list and order are unchanged (commit history).
- **The labeling:** Hemanth labeled all 90 blind, in 9 batches, on Nov 23–24 (`audit/labels-v2.csv`, with a timestamp on every row).

| first pass → second pass | postings |
|---|---:|
| relevant → **not relevant** | **35** |
| not relevant → relevant | 4 |
| unchanged | 51 |

**39 of 90 verdicts changed** (Wilson 95% 34%–54%). Of the 43 first-pass "relevant" verdicts among these postings, 35 became "not relevant" (Wilson 67%–90%). Details: `audit/relabel-results.md`.

**What a labeling view is.** It's a retrieval step, and it left out the one fact that decides most of these postings for an 8-month co-op graduate. This is Chapter 7's point ("retrieval and what it leaves out") showing up in our own measurement, not in the agent.

**The corrected labels:** the second-pass verdict where one exists, otherwise the first-pass one. They reverse the audit's conclusion (filter v1.0; `audit/audit-results-corrected.md`):

| | First-pass labels (sections 1–7) | **Corrected labels** |
|---|---|---|
| Random rejects Hemanth wanted (misses) | 11 / 30 (22%–54%, about 210–524 postings) | **3 / 30** (3%–26%, about 33–246 postings) |
| Random kept Hemanth didn't want | 2 / 15 (4%–38%) | **7 / 15** (25%–70%) |
| The filter's main weakness | recall: it rejects too much | **precision: it keeps senior roles** |
| X1 on the 55 audit labels (in-sample) | 39 → 42 | **42 → 39** |
| X1 on its own fresh test (10 postings) | v1.1 right 7/10 | v1.1 right **8/10** |

- **X1 now points two ways.** On the audit labels it costs 3, because some Perplexity "Technical Staff" postings it keeps ask for 4–5 years and are now "not relevant". On its own fresh 10 it still helps. Both results are reported. X1 stays, and the experience rule below covers what it lets through.
- **The location tension (section 6) mostly disappeared.** The London AI Inference Engineer posting, which Hemanth first marked "not relevant", became "relevant" once its "3+ years" was visible.

**What changed in the filter (FILTER.md v1.2; the changelog has every measurement):**
- **Rejected,** measured on the 75 corrected tuning labels (the audit's 55 plus the X1 test's 20, never the held-out 40):
  - Y1 and Y2, which keep more (53 and 52 correct, against 57 for v1.1);
  - Y3, which softens seniority, because its evidence was the view artifact;
  - Y5, the location penalty (57).
- **Added: R17, reject a posting whose text asks for 5 or more years.** It is 70 of 75 correct, against 57. Precision rises from 56% to 87% with the same recall (91%), and what reaches Priya drops from 212 postings to 105.
  - The cut-off 5 is **fitted**: 3, 4, 5 and 6 were compared.
  - **A second false friend** was found while measuring it: "Minimum 2-6 years … (depending on seniority level)" was read as 6 years. A range now counts by its lower bound.
- **These decisions were delegated.** Hemanth: "Do whatever you recommend and complete the project, I need to submit this today". The held-out result is in `SCORE.md` section 2c.

**What this section does not show:**
- **The second pass is the same person, a day later, who had already seen many of these titles.** Some changes may come from memory or a changed mood, not only from the new view. There was no second labeler.
- **View v2 shows only the years phrases and a summary.** Other facts, such as the domain or the visa, can still be hidden.
- **The 25 labeled postings that state no years were not shown again.** Their first-pass verdicts stand in the corrected set.

