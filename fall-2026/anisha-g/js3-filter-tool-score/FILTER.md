# FILTER.md: Job-Search Agent 3
**Anisha Gaikar · version 1.0 · 2026-11-25 ~2:05 pm, written before any JS3 code.**

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

## Change log
| Version | Date | Change | Why |
|---|---|---|---|
| 1.0 | 2026-11-25 | First version, before any code | — |
