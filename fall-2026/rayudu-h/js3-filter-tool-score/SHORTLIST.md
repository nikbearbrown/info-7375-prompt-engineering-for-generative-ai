# SHORTLIST.md: the source-grounded shortlist (Chapter 7)

**What reaches Priya.** The top **10** postings kept by FILTER.md **v1.1** that are still listed in the latest snapshot (Nov 20, 2026), ranked by score (R14).
- **The cut is clean.** Nine postings tie at 6.5, all nine are on the list, and the tenth scores 6.0. The arbitrary tie-break never had to choose between postings at the cut.
- **Where every claim, label, quote and check is:** [`shortlist/shortlist-claims.md`](shortlist/shortlist-claims.md), generated from `shortlist/claims.json` (Claude's raw replies) and `shortlist/hand-check.csv` (Hemanth's check and the final labels).

## 1. How the claims were labeled

| Step | Who | When (Nov 22, 2026, EST) | Result |
|---|---|---|---|
| Claims built from the filter's matches: C1, C2 per matched skill (at most 3), C3, C4, C5 (FILTER.md section 3) | code | — | **69 claims** on 10 postings |
| Each claim labeled against the posting's own text, with a verbatim quote | Claude, `claude-sonnet-5-5`, one fresh `claude -p` per posting, no tools; prompt `prompts/claims_v1.md` (sha256 `49419c82…`) | 3:38–3:39 PM | 69 labels; commit `8d4d015` |
| The quote check: is each quote verbatim in **this** posting? | code (`js3/claims.py`) | — | **69 / 69 grounded**, 0 rejected |
| Hand check: does the quote really assert the label? | Hemanth, two messages: "all ok", "all ok" | 3:48 and 3:59 PM | **69 / 69 agreed** |
| Rule re-check: do the labels follow the written rule? | Claude, comparing each label with the posting's full text | after the hand check | **3 labels break the rule**: both sides were present, so each should be "insufficient" (section 4) |
| Corrections | Hemanth: "a" (correct them, keep the history) | 4:12 PM | #1 C3, #8 C5 and #9 C5 → insufficient. Claude's label, Hemanth's check and the final label all stay in the file |

## 2. The shortlist (final labels)

S = supported · **C** = contradicted · I = insufficient

| # | Posting | Score | C1 role | C2 skills | C3 level | C4 Boston/remote | C5 visa | Answer |
|---|---|---:|---|---|---|---|---|---|
| 1 | Security Engineer, Detection and Response (Notion, San Francisco) | 6.5 | S | Python S · SQL S · AWS S | I *(corrected)* | **C** | I | **worth reading** |
| 2 | Data Engineer, Product (Notion, San Francisco) | 6.5 | S | Python S · SQL S · AWS I | **C** | **C** | I | not for Priya |
| 3 | Forward Deployed Engineer, India (Notion, Hyderabad) | 6.5 | S | Python S · SQL S · AWS I | **C** | **C** | I | not for Priya |
| 4 | Security Engineer, Detection and Response (Notion, Dublin) | 6.5 | S | Python S · SQL S · AWS S | I | I | I | **worth reading** |
| 5 | Member of Technical Staff (Software Engineer, Data Platform) (Perplexity) | 6.5 | S | Python S · Databricks I · Delta Lake I | **C** | I | I | not for Priya |
| 6 | Member of Technical Staff (GTM Engineer, Growth) (Perplexity) | 6.5 | S | Python S · SQL S · AWS I | I | I | I | **worth reading** |
| 7 | Member of Technical Staff (Software Engineer, Computer Growth) (Perplexity) | 6.5 | S | Python S · SQL S · AWS I | S | I | I | **worth reading** |
| 8 | Support Engineer (Anthropic) | 6.5 | I | Python S · SQL S · AWS S | **C** | **C** | I *(corrected)* | not for Priya |
| 9 | Machine Learning Data Scientist, Forecasting Platform (Anthropic) | 6.5 | S | Python S · SQL S · AWS I | **C** | **C** | I *(corrected)* | not for Priya |
| 10 | Member of Technical Staff (Software Engineer, Training Infrastructure) (Perplexity) | 6.0 | S | Python I · AWS I | I | **C** | I | **I cannot tell** |

**Of the 10 top-scored postings:**
- 4 are "worth reading": #1, #4, #6, #7. Two of them (#1 and #4) are the same Notion role posted in two cities.
- 5 are "not for Priya". The posting's own text contradicts the level, for example "5+ years of experience as a data engineer…" or "3 to 6 years of hands-on experience…".
- 1 is "I cannot tell".

The filter's score knew none of this. Each of these postings scored at least 6.0, against a threshold of 3.0.

## 3. Relevance is not entailment

**#5, "Member of Technical Staff (Software Engineer, Data Platform)", Perplexity.** It matched three of Priya's skills, including **Databricks** and **Delta Lake**, her two rarest. Those two words were worth +2.0 and put it in the top 10.
- **What the posting says:** "…while thoughtfully combining platforms such as **Databricks** and Snowflake with open-source technologies including Spark, Kafka, Flink, Airflow, Dagster, dbt, Iceberg, **Delta Lake**, and ClickHouse."
- **Why that doesn't support the claim:** the sentence describes the team's stack. It doesn't ask the candidate for either skill.
- **So:** "The posting asks for Databricks" and "…asks for Delta Lake" are both **insufficient**.
- **And the level is contradicted:** "5+ years (Senior) or 8+ years (Staff) of software engineering experience."

The posting matches Priya's words without supporting the claims those words were counted for.

**It isn't a one-off.** 9 of the 29 skill claims (C2) on the shortlist are insufficient although the word is in the posting:
- "AWS" in a "Tech Stack: … | AWS" line (#6, #7);
- a skill as one of several options: "such as Python, Rust, C++, or Go" (#10); "(AWS, GCP, Azure)" (#2, #3, #9).

The filter counts a word. The claim needs a sentence that asks for it.

## 4. The abstention rule, and a counterexample that exposes its limits

**The rule** (FILTER.md section 3):
- "worth reading" needs C1 supported, at least one C2 supported, and C3 **not contradicted**.
- Any contradicted C1 or C3 gives "not for Priya".
- Everything else gives **"I cannot tell"**, with the reason.

**Where it worked.** #10, "Training Infrastructure", abstained. Its only skill words are options in a list ("such as Python, Rust, C++, or Go"; "such as AWS and Kubernetes"), so no skill claim is supported. The rule said "I cannot tell (no skill claim supported)" instead of guessing.

**The counterexample: #6, "Member of Technical Staff (GTM Engineer, Growth)".** The rule answers **"worth reading"**, and its limits show in two ways:
1. **"Not contradicted" is treated as good enough.**
   - The posting asks for "**2+ years** as a growth, GTM, data or full-stack engineer…". That exact sentence is the quote for its Python claim. Priya has one 8-month co-op.
   - Yet C3 was labeled **insufficient**, not contradicted, by Claude, and Hemanth's check agreed.
   - Because the rule only stops on a *contradicted* level, an insufficient level lets it answer confidently. The rule is only as good as the weakest label it reads.
2. **The facts that matter most to Priya never trigger an abstention.** C4 (Boston or remote) and C5 (visa) are insufficient here, and the rule still answers, by design (Hemanth's Q4 and Q5). Priya needs sponsorship (F-1 OPT), but **no posting in the whole corpus states sponsorship for a specific role**:
   - Anthropic's 815 postings all carry the same "We do sponsor visas! However, we aren't able to … for every role" paragraph;
   - Notion and Perplexity say nothing.

   So every "worth reading" here is silent on a fact that can end Priya's application.

**The rule also depends on the labeler being consistent, and it wasn't.**
- **#1 and #4 are the same Notion job**, with the same requirements text. Claude labeled the level in #1 *contradicted* ("3+ years") and in #4 *insufficient* (both sides). So one role got two answers until the rule re-check corrected #1.
- Two more inconsistencies remain, because the written rule doesn't settle them:
  - **A skill listed as one of several options:** "Experience with AWS, GCP, or Azure" was labeled *supported* in #1 and #4, but *insufficient* in #2, #3 and #9.
  - **A location that is only a city:** "San Francisco" counted as *contradicted* for Boston-or-remote in #10, but *insufficient* in #5, #6 and #7.

## 5. What the checks caught, and what they missed

- **The machine check** (verbatim quotes) passed 69 of 69. It proves each quote exists, not that the quote means what the label says.
- **Hemanth's check** passed 69 of 69. It confirmed the quotes made sense, but it did not re-apply the both-sides rule. That rule required reading text that wasn't shown: the other half of a conflict.
- **Claude's rule re-check** found 3 labels that break the rule. Corrections were made only with Hemanth's decision ("a"), and the history is kept.
- **Domain fit is not one of the claims.** #1, the Security Engineer in San Francisco, ends as "worth reading". In the blind audit, Hemanth had marked the same posting **not relevant** (audit item 94). C1–C5 check role, skills, level, place and visa; none of them asks whether security detection is work Priya wants. That judgment stays Hemanth's (see the driver's seat in `README.md`).

## 6. What this shortlist does not show

- Claude labeled each posting **once**, so how often its labels change from run to run is not measured here. `SCORE.md` measures run-to-run variation for the relevance judge, not for this labeler.
- Hemanth's check is one pass by one person, with quotes shortened to about 130 characters in chat. The full quotes are in the generated file.
- How to label a skill listed among options, or a location that is only a city, is unresolved.
- Two shortlisted postings, #3 and #4, are in the held-out set. Their held-out verdicts are not used here.
