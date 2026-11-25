# FILTER.md: Job-Search Agent 3
**Anisha Gaikar · version 1.0 · 2026-11-25 ~2:02 pm, written before any JS3 code** (commit `7ee4178`). **Current version: 1.2** (see the change log at the end; sections 1–4 below are v1.0 exactly as gated, with the later rules in §5).

**Who chose what.**
- **Mine:** I made every decision in this file. Claude offered options and I chose: title words, seniority, the text rule, boards, evidence rules, abstention, missing fields and wrong versions.
- **Claude's:** Claude wrote the wording and the one-line reasons from my choices. The score numbers in §1.4 are Claude's proposal to reproduce my rule exactly, so I count them as *hand-set*.

**Who it's for:** the fictional persona Nadia Okafor (`persona/resume.json`), an entry-level data analyst with at most 3 years of experience. Her core skills are SQL, Python, Tableau, Power BI, Excel, dbt, Looker, Snowflake, A/B testing and ETL.

## 1. The filter (v1.0)
| # | Rule | Reason (one line) |
|---|---|---|
| R1 | **The title** contains a role word as a **whole word**: `analyst`, `analytics`, `business intelligence`, `BI`, `insights` | These are the titles of the jobs Nadia targets; whole words only, so "BI" doesn't match inside "ability". |
| R2 | **Reject** if the title contains a seniority word: `senior`, `sr`, `lead`, `staff`, `principal`, `manager`, `director`, `head`, `vp` | Nadia has at most 3 years; in JS1, every Lead or Senior posting asked for 5 or more years. |
| R3 | **The posting text** names **at least 2** of Nadia's core skills, as whole words or phrases | One skill word appears in almost any office job; two show the work is really analytical. |
| R4 | **The largest "N years"** requirement stated in the text is **3 or less** (if a range is given, its **top** counts, as in JS1) | It's her limit. If years aren't stated, the posting is allowed, but the years claim is labelled "I cannot tell". |

**Kept** = R1 and R3 and R4 pass, and R2 doesn't reject. Everything else is rejected, with the failing rules listed.

### 1.4 The score (for ranking and for finding close calls)
`score = 3 (if R1) + 1 per core skill named (max 5) − 3 (if R2 rejects) − 3 (if R4 fails)`. **Keep if score ≥ 5 and no rule fails.**
- **Where the numbers come from:** all **hand-set**, to reproduce the rule above. A title match plus 2 skills is exactly 5.
- **Close calls:** postings that score 4, 5 or 6, or that fail exactly one rule.

## 2. The evidence rules (for each claim in a shortlist justification)
| Label | When |
|---|---|
| **SUPPORTED** | A sentence in the posting states it **as a requirement or duty**. For example, "requires SQL" is supported by "Proficiency in SQL". |
| **CONTRADICTED** | The posting states **the opposite**. For example, "≤3 years" is contradicted by "5+ years of experience". |
| **INSUFFICIENT** | The word is **absent**, or it appears only as **"nice to have", "a plus", "preferred", "bonus"**, or in passing (for example, in the company description). |

**"I cannot tell":** the agent must say "I cannot tell" instead of a verdict on a claim when:
- the posting text is missing or blank;
- the posting states no years at all, for the years claim;
- a skill claim is only INSUFFICIENT.

**A posting is never shortlisted on a guess.**

## 3. Expected sources
- **Boards (max 5, my JS2 budget):**
  - **Greenhouse:** `klaviyo`, `datadog`, `stripe`, `lyft`;
  - **Lever:** `palantir`.
  - Their live status is unverified until the first run.
- **The fields the agent must see:** `id`, `title`, `location`, `text` (the full posting text: Greenhouse `content`, Lever `descriptionPlain` plus lists), and `url`.
- **When something is missing:**
  - **A missing title or text** puts the posting in an **"I cannot tell"** list. It's never silently rejected.
  - **A failed board** is reported as **failed**, never as "0 postings" (my JS2 rule).
  - **A missing location** doesn't affect the verdict.

## 4. Wrong versions my tests must catch
1. **Substring match:** "analyst" or "BI" matched inside other words. For example, "BI" in "ability" or "possibility" would make many unrelated postings look relevant: a false-friend filter.
2. **Rank by word count:** score = the number of skill words found, with no cap and no rules. A long posting that lists every tool would always rank first, even a Senior one.

## 5. Rules after measuring (v1.1 and v1.2)
Every change below came from **audit items** (groups A, B and C; AUDIT.md), never from the held-out set H. **Timing, exactly:** the two v1.1 rules were proposed and coded by Claude at 14:21, from reading the kept sample (group C) **before** I had judged anything; my blind verdicts (14:27–14:51) later marked both postings "n", and I accepted the rules at ~2:55 pm. R5 (v1.2) and the rejected rules came **after** my verdicts, from my reasons. Each was measured on H afterwards (WHAT_MOVES_THE_SCORE.md). Each is in its own filter file (`filters/filter_v1.1.json`, `filters/filter_v1.2.json`), with tests written before the code.

| Rule | Status | Version | Evidence that led to it | Reason (one line) |
|---|---|---|---|---|
| **R1b** reject a title containing `engineer` (whole word) | **ADDED** | 1.1 | C: *Software Engineer, Data Warehouse Analytics* was kept (noticed by Claude at 14:21; my later blind verdict: "n") | "Analytics" in an engineering title is a **false friend** for R1. |
| **R4 fix:** ignore an "N years" followed within 40 characters by `education / university / college / degree / school` | **ADDED** | 1.1 | C: *Financial Data Analyst Intern* had "At least 2 years of **university education**" counted as experience | Years of study are not years of experience (**false friend**). |
| **R5** reject a location that names a non-US place and no US place; missing or vague locations pass | **ADDED** | 1.2 | C: both kept **intern** postings were "n" in my verdicts, with **Toronto** and **Singapore** in my reasons; many A reasons name non-US cities | Nadia is in Boston. Location was the most frequent reason in my "n" verdicts that the filter couldn't see. |
| Exclude `FP&A` titles | **REJECTED after measuring** | — | C: 2 FP&A Analysts kept, both "n" ("finance role, wants finance degree") | It would fix 2 audit items, but it's a domain judgment about one family of titles. I'd rather keep a readable rule set than add a word rule for each domain I dislike. Recorded as a known source of wrong keeps. |
| Add `specialist` as a role word | **REJECTED after measuring** | — | B: *Compensation Specialist* was rejected (R1); my verdict was "y" | On the whole corpus it would add 1 keep from 52 "specialist" titles. One posting doesn't justify widening R1. |
| Case-sensitive `Excel` (so "you **excel** at" stops counting) | **REJECTED for now** | — | *Credit Risk Operations Analyst* ("You excel in…") is a **held-out** item | A clear false friend, but I found it on a held-out item. Changing the filter because of it would contaminate the held-out measurement. Candidate for v1.3. |
| Read "two (2) years" | **REJECTED for now** | — | *Operations Insights…* is a **held-out** item | Same reason as Excel. |
| R4 counts the **bottom** of a range ("3–5 years" → 3), candidate **v1.3** | **NOT ADOPTED after measuring** | (1.3 candidate) | H2: all 3 postings I marked y were rejected by R4 on the top of a range; my reasons accept "3–5 years" | It catches 2/3 on H2, but that's circular (the rule came from H2). On the clean set H it changes nothing. No clean evidence yet, so v1.2 stays current; it needs a third labelled set. |
| **Cut** any v1.0 rule | none | — | Random rejects: 0 of 30 wrong (AUDIT.md) | No v1.0 rule was shown to reject good postings in the random sample. |

**Who decided:** Claude measured each candidate on the corpus and proposed it. I chose: accept both v1.1 rules (already coded at 14:21, before my verdicts), add R5, reject FP&A and specialist (2026-11-25, ~2:55 pm). Note: `tests/test_filter_v11.py` and `filters/filter_v1.1.json` say "after the audit's kept sample"; that means after Claude read group C, not after my verdicts. Both files are frozen by hash, so I corrected the wording here instead.

## Change log
| Version | Date | Change | Why |
|---|---|---|---|
| 1.0 | 2026-11-25 | First version, before any code | — |
| 1.1 | 2026-11-25 | + R1b (no `engineer` titles); R4 ignores education years | Two false friends in the audit's kept sample (§5) |
| 1.2 | 2026-11-25 | + R5 US-only location | My audit reasons (§5) |
| 1.3 (candidate) | 2026-11-25 | R4 reads the bottom of a range: **not adopted** | H2 finding; no clean evidence (§5) |
