# AUDIT.md — the reject audit (Chapter 7)

**Filter audited:** FILTER.md v1.0 (`config/filter-v1.0.json`), run on 2026-11-24 over all 3,117 postings in `runs/2026-11-24T220432Z-live`. It kept 115 and rejected 3,002; it answered "cannot tell" for 0.
**Hand verdicts:** mine (Lavanya R), 2026-11-24, recorded in `audit/hand_verdicts.jsonl`.

## 1. Design (committed before the draw)

- **Sampling.** `audit/draw.py` drew the postings with the seed in `audit/SEED`. The seed was committed (`audit: sampling plan and seed`) before the draw ran. It drew:

  | Group | What | Size |
  |---|---|---|
  | A | simple random sample of all 3,002 rejects | 30 |
  | B | closest calls: 5 random at score 4 (one point under the threshold) and 5 random at score 5 (exactly at it), among postings that passed every hard reject | 10 |
  | C | random sample of the 115 kept | 10 |
  | H | held out for the Chapter 9 measurement (15 kept + 15 below the threshold), never used to choose a rule | 30 |

- **The sheet was blind.** All 80 postings were shuffled together, with no group, verdict or score shown.
- **What I saw for each posting:** the title, company and location, plus a short summary of its requirement lines.
  - Claude wrote each summary from the posting's own text, using the posting's words.
  - I answered each one: is it worth Priya's time? **y**, **n**, or **?** (can't tell).
- **How "wrong" is defined.** The filter is wrong when it keeps a posting I marked **n**, or rejects one I marked **y**. A **?** counts as neither.
- **Not completed:** I judged all of groups A–C. In H, I judged 21 of the 30 and stopped labelling; the other 9 have no verdict.

## 2. Results

| Group | Judged | Filter wrong | 95% interval (Wilson) for the rate in that group's population |
|---|---|---|---|
| A, random rejects | 30 (29 y/n + 1 ?) | **0 of 29** | 0% – 11.7% |
| B, closest calls | 10 | **4 of 10** (3 rejected at score 4 that I'd want; 1 kept at 5 that I wouldn't) | 16.8% – 68.7% |
| C, random kept | 10 | **2 of 10** | 5.7% – 51.0% |
| A+B+C | 49 y/n | 6 of 49 | (not a population rate: the groups were drawn from different strata) |

### What the sample can and can't show

- **Rejects.** 0 wrong out of 29 does **not** mean the filter never rejects a good posting.
  - With 29 random rejects, a 95% interval for the miss rate among all 3,002 rejects runs from 0% to about 11.7%.
  - That is consistent with anything from no good posting thrown away up to roughly **350** of them.
  - What the sample does show is that misses among the rejects are not common: a 20% miss rate would rarely produce 0 of 29.
- **Kept.** "2 of 10 kept were wrong" fits a junk rate among the 115 kept anywhere from about 6% to 51%. Ten is too few to say more.
- **Closest calls.** The closest calls are where the filter is weakest: 4 of 10 were wrong. This is a property of the threshold, not of a word list. The 3 misses at score 4 were all titles with "Software Engineer" (or an internship) whose text named only one ML word or skill.
- **Who judged.** All of these are my judgments of fit for a fictional persona, made from short summaries. A second judge was not used, so my own disagreement rate with myself is unknown (see Not checked in README).

## 3. The false friend

**", CA" in "Ontario, CA".** Rule R3 counts a 2-letter US state code after a comma as a US location.
- Anthropic writes Canadian locations as **"Ontario, CA"** and **"British Columbia, CA"**, where CA means Canada. R3 read them as California.
- Found on sheet item 18 ("Data Center Capacity Delivery, Canada", location "Ontario, CA"). The filter rejected it, but for R5 (years asked), not R3. R3's match list showed `Ontario, CA` as a US location.
- **8 postings** in the corpus have a Canadian place ending in ", CA". None changed verdict because of it: each was rejected by another rule, or also listed a real US city. The fix (X4) is therefore a fix of a **wrong reason**, with no measured change in outcome.

**Other words that matched for a reason I didn't intend** (I did not measure fixes for these):
- **"Intern"** in "Hardware Engineer Intern, Vehicle Development" (item 1). S1 matched correctly (it is an internship), but these internships require graduation in 2027–28, and Priya graduated in Dec 2025. The word is right, but the posting is not.
- **The smallest "N years"** (R5). "2 years of hands-on experience with big data" made the smallest number 2, while the same posting asks for "5+ years" (items 39 and 54). Both are in the held-out group, so I did not use them to choose a rule (X3 below).
- **"Manager" in "Software Engineer, Ads Manager"** (not in the sample). It is a product name, but R1 reads it as a management title.

**A second false friend, found after the audit: the Databricks footer.** While labelling the shortlist (SHORTLIST.md §1a), Claude found that every one of the 890 Databricks postings ends with the same "About Databricks" paragraph. It contains "…analytics and **agents**", "**Unity Catalog**" and the word **Databricks**, so S2 and S3 give every Databricks posting points for words that describe the company, not the job.
- Measured as X5 (§4): dropping the footer changes 6 verdicts in the corpus, none of them among my hand verdicts.
- Deferred to the next version.

## 4. Rules added, cut and rejected after measuring

`audit/measure.py` re-runs each variant (one change from v1.0 each) against my 49 y/n verdicts in groups A–C. Output: `logs/js3-01-measure-dev.txt`.

| Change | Wrong (of 49) | Kept overall | Decision |
|---|---|---|---|
| v1.0 as written | 6 | 115 | — |
| X1 threshold 5 → 4 | 5 | 237 | **rejected**: one fewer mistake in 49 is too small to trust, and it doubles the reading |
| X2 add "Forward Deployed" to S1 | 6 | 124 | **rejected**: no measured gain |
| X3 R5 uses the largest years asked | 6 | 109 | **rejected**: no measured gain on audit labels |
| X4 ", CA" after a Canadian place is not California | 6 | 115 | **adopted** → FILTER.md v1.1 (fixes the false friend's wrong reason) |
| X5 ignore the "About Databricks" footer (found later, measured against v1.1) | 6 (unchanged: none of the 6 postings it changes is hand-judged) | 110 (5 fewer kept; 1 more "cannot tell") | **deferred**: no hand label covers any posting it changes; measure on new labels first (`logs/js3-07-measure-footer.txt`) |

Decisions: Claude proposed X1–X4 and recommended these four decisions; I chose to follow them. No variant was measured on group H before these decisions.

**Disclosure.** Claude's first comparison script (not committed) printed v1.0's mistakes in **all four groups, including the held-out group H**, before X1–X4 were proposed. So Claude had seen which held-out postings v1.0 got wrong, including items 39 and 54, which X3 would fix, when it recommended rejecting X3. The decisions were measured on groups A–C only, and the one variant that H later favoured (X3) was rejected. Still, the held-out labels were not perfectly unseen during rule-making. I wasn't shown those H results, but Claude was.

## 5. Every hand verdict, groups A–C

Generated by `python3 -B audit/tables.py` (filter column = v1.0).

### Group A: 30 random rejects

| Sheet # | Title (board) | Filter v1.0 | Why | Score | My verdict | Filter wrong? |
|---|---|---|---|---|---|---|
| 5 | Lead Solutions Architect - Generative AI (EMEA Emerging DNB) (databricks) | reject | R1, R3 | 9 | ? | ? |
| 11 | Automation Engineer - Compute Software Performance (zoox) | reject | R5 | 4 | n | no |
| 12 | Deployment Strategist, Internship (palantir) | reject | R3 | 2 | n | no |
| 14 | Deployment Strategist - US Government (palantir) | reject | below_threshold | 2 | n | no |
| 15 | Sr. Forward Deployed Engineer (FDE) - Digital Native Business (databricks) | reject | R1, R5 | 6 | n | no |
| 16 | Product Management Intern (2027) - Amsterdam (databricks) | reject | R3 | 7 | n | no |
| 17 | National Security Lead, APAC (anthropic) | reject | R1, R3, R5 | 0 | n | no |
| 18 | Data Center Capacity Delivery, Canada (anthropic) | reject | R5 | 0 | n | no |
| 19 | Greenfield Startups, Account Director (openai) | reject | R1, R3, R5 | 0 | n | no |
| 23 | Sr Staff Technical Program Manager- Security (databricks) | reject | R1, R5 | 4 | n | no |
| 24 | Staff Software Engineer, Claude Code (anthropic) | reject | R1, R5 | 5 | n | no |
| 25 | Signal Integrity Engineer (openai) | reject | R5 | 0 | n | no |
| 33 | Mechanical Design Engineer, Battery Pack (openai) | reject | R5 | 0 | n | no |
| 34 | Strategy & Operations Lead, France (openai) | reject | R1, R3, R5 | 0 | n | no |
| 35 | Sr. Forward Deployed Engineer (databricks) | reject | R1, R5 | 6 | n | no |
| 36 | Customer Success Manager (anthropic) | reject | R1, R3, R5 | 0 | n | no |
| 37 | Staff Technical Program Manager - Compute Hardware (zoox) | reject | R1, R5 | 1 | n | no |
| 38 | Sr. Product Manager, Compute Platform (databricks) | reject | R1, R5 | 4 | n | no |
| 41 | Solutions Architect (databricks) | reject | R3 | 4 | n | no |
| 42 | Senior Network Security Engineer (zoox) | reject | R1, R5 | 4 | n | no |
| 49 | Staff Vehicle Attributes Engineer (zoox) | reject | R1, R3, R5 | 1 | n | no |
| 50 | Software Engineer, Business Technology (anthropic) | reject | R5 | 4 | n | no |
| 55 | Lead, Technical Accounting (Compute Infrastructure) (openai) | reject | R1, R5 | 1 | n | no |
| 56 | Enterprise Solutions Consultant (notion) | reject | R3 | 2 | n | no |
| 63 | Events Manager, Business (openai) | reject | R1, R5 | 1 | n | no |
| 65 | Global Head of Applied AI Engineering, SMB / Mid-Market (openai) | reject | R1 | 3 | n | no |
| 72 | Finance Operator (palantir) | reject | below_threshold | 0 | n | no |
| 74 | Global Head of Renewals, Product & Engineering (anthropic) | reject | R1 | 1 | n | no |
| 76 | Software Engineer, Manufacturing Infrastructure (openai) | reject | R5 | 4 | n | no |
| 79 | Manager/Sr. Manager, AI Forward Deployed Engineering (databricks) | reject | R1, R3 | 8 | n | no |

### Group B: 10 closest calls (score 4 and 5)

| Sheet # | Title (board) | Filter v1.0 | Why | Score | My verdict | Filter wrong? |
|---|---|---|---|---|---|---|
| 10 | Software Engineer, Cyber Safeguards (openai) | reject | below_threshold | 4 | n | no |
| 21 | Backend Software Engineer - Defense (palantir) | keep | — | 5 | y | no |
| 28 | Software Engineer, Developer Platform (notion) | keep | — | 5 | n | **yes** |
| 30 | Solutions Engineer (databricks) | reject | below_threshold | 4 | n | no |
| 31 | Software Engineer, Codex Enterprise (openai) | reject | below_threshold | 4 | y | **yes** |
| 40 | Software Engineer, New Grad - Defense (palantir) | reject | below_threshold | 4 | y | **yes** |
| 53 | Forward Deployed Infrastructure Engineer, New Grad - US Government (palantir) | keep | — | 5 | y | no |
| 57 | Year at Palantir - Forward Deployed Software Engineer, Internship - Commercial (palantir) | reject | below_threshold | 4 | y | **yes** |
| 73 | Software Engineer, Agent Infrastructure (openai) | keep | — | 5 | y | no |
| 80 | Software Engineer - Learned Trajectory Machine Learning Engineer (zoox) | keep | — | 5 | y | no |

### Group C: 10 random kept

| Sheet # | Title (board) | Filter v1.0 | Why | Score | My verdict | Filter wrong? |
|---|---|---|---|---|---|---|
| 1 | Hardware Engineer Intern, Vehicle Development [Summer 2027] (zoox) | keep | — | 5 | n | **yes** |
| 2 | Software Engineer, Security Observability (openai) | keep | — | 5 | y | no |
| 20 | Applied Data Scientist, Personalization & Machine Learning (openai) | keep | — | 7 | y | no |
| 32 | Applied AI Engineer, Mid-Market Enterprise (openai) | keep | — | 6 | y | no |
| 43 | Machine Learning Engineer, Core Experimentation (openai) | keep | — | 7 | y | no |
| 44 | Machine Learning Infrastructure Engineer, Safeguards Research (anthropic) | keep | — | 7 | y | no |
| 47 | AI Engineering Intern, Operational Safety [Summer 2027] (zoox) | keep | — | 9 | y | no |
| 52 | Software Engineer, Observability (openai) | keep | — | 5 | y | no |
| 61 | Forward Deployed AI Engineer (palantir) | keep | — | 7 | y | no |
| 64 | Research Engineer, Machine Learning (Reinforcement Learning) (anthropic) | keep | — | 7 | n | **yes** |
