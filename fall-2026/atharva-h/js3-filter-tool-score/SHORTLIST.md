# SHORTLIST — source-grounded claims for kept postings

**Status: Claude's draft from `claims.py` (base prompt).**
- **Claim labels:** waiting for me to confirm each one in `state/claims/base_checked.csv` (the `my_label` column, 72 rows).
- **Choices of case:** the relevance-vs-entailment case and the counterexamples below are Claude's picks, for my review.

## How the shortlist is made
1. **The filter decides.** v1.0 keeps 12 of the 4,240 postings. Claude never decides keep or reject.
2. **Claude writes claims.** For each kept posting, `claude -p` gives six fixed claims a status and a quote. The claims are role, seniority, years, location, sponsorship, and skills, worded in `claims.py`. A status is supported, contradicted, or insufficient.
3. **The substring checker labels each claim** (`claims.py check`):
   - If the quote is found in the posting's title, locations, or description (after whitespace is collapsed), Claude's status stands.
   - If it isn't found, the claim is "insufficient".
4. **I confirm every label.** The checker can show that a quote is *there*. It can't show that the quote *says what the claim says*.
5. **The abstention rule:** the agent answers "I cannot tell" when the role, seniority, or location claim is insufficient, or when the description is missing. Years and sponsorship never force it (FILTER.md "Evidence rules").

## The shortlist (base prompt)

| Posting | Filter score | Agent's answer | Which claim made it abstain | My label (side) |
|---|---|---|---|---|
| FanDuel, Campaign Analytics, Data Analyst | 9 | I cannot tell | seniority | **yes** (held-out) |
| Stripe, Data Analyst, SF | 8 | I cannot tell | seniority | no (tuning) |
| Veeva, Marketing Analytics Data Analyst, ADP | 7 | I cannot tell | location (the quote began with "Locations:") | no (tuning) |
| Zoox, Student Worker, Data Analyst (part-time) | 7 | **keep** | — | no (tuning) |
| Zoox, Financial Analyst, Marketing and Commercial | 7 | I cannot tell | role | not labeled |
| Stripe, Data Analyst, Intern | 6 | **keep** | — | no (tuning) |
| Axios, Salesforce Business Analyst | 6 | **keep** | — | no (tuning) |
| FanDuel, Analyst | 6 | I cannot tell | location (the quote began with "Locations:") | **yes** (held-out) |
| Datadog, FP&A Analyst, Cloud Finance | 5 | I cannot tell | role, seniority | not labeled |
| Datadog, FP&A Analyst R&D | 4 | I cannot tell | role, seniority | not labeled |
| FanDuel, Product Analyst (NYC) | 4 | I cannot tell | seniority | no (tuning) |
| FanDuel, Product Analyst (Atlanta) | 4 | I cannot tell | seniority | no (tuning) |

**Coverage:** 3 of 12 answered, and all 3 answers are labeled "no". The agent abstained on both "yes" postings.

**Claims, all 12 postings:** 72 claims in all.
- Claude gave 48 as supported or contradicted, with a quote.
- The checker found 46 of those 48 quotes.
- The other 2 began with the prompt's own field name, "Locations:", so they aren't posting text. The checker was right to refuse them. A prompt sentence fixes it (C3 in SCORE.md: 46/46).

## Relevance is not entailment
**The case:** Zoox, "Contract Student Worker - Data Analyst (Part-time)".
- **The claim:** seniority, "The job is entry level or junior."
- **What Claude said:** **supported**, quoting "Currently enrolled in a B.S. or M.S. program in Computer Science, Data Science, Engineering, or a related quan[titative field]".
- **What the checker said:** the quote is found, so the label is supported.
- **Why the quote doesn't prove the claim:** it is *relevant*, since it is about who the job is for. But it says the applicant must currently be a student, not that the job is entry level. It describes a part-time student contract, which Riley, graduating in December 2026, isn't looking for. The text is there. What the claim says isn't.
- **The consequence:** this posting is one of the three the agent answered "keep", and my label for it is "no".

**A second case, in the other direction:** FanDuel, "Analyst".
- **What Claude said:** seniority **contradicted**, quoting "Opportunity to mentor junior analysts on day-to-day requests as well as team best practices".
- **Why it doesn't prove the claim:** the quote is found, and mentoring juniors suggests a role above junior. But it doesn't say the job isn't open to someone early in their career, and the same posting gives "2+ years ... preferred". On the C0' run, the same prompt called this claim insufficient.

**What it means:** quote-found is a necessary condition for "supported", not a sufficient one. That is why FILTER.md has me confirm every label, and why the checker's numbers in SCORE.md are "quotes found", never "claims verified".

## The abstention rule, and its counterexamples
**The rule:** abstain when the role, seniority, or location claim is insufficient, or the description is missing.

**Counterexample 1, a confident wrong answer:** Zoox's part-time student worker.
- Role, seniority, and location are all supported, with quotes the checker finds, so the agent answers **keep**.
- Riley wouldn't apply: it's a part-time student contract.
- The rule abstains on missing evidence. It doesn't abstain on evidence about the wrong thing, or on a property it doesn't track, like employment type or graduation date. Stripe's intern posting (which requires graduating December 2027 or later) fails the same way.

**Counterexample 2, abstaining on a match:** FanDuel, "Campaign Analytics, Data Analyst", labeled "yes".
- The posting never says "entry level" or "junior", so the seniority claim is insufficient and the agent answers **I cannot tell**.
- Yet "Minimum of 1+ years of previous experience in a similar role" is clear enough for Riley, and I labeled it "yes".

**What I did about it:** dropping the seniority clause (A1 in SCORE.md) fixes counterexample 2, but answers 6 of 7 tuning postings, all wrong. Recommendation: keep the rule as it is, and report coverage next to accuracy, so an abstention is never counted as a correct answer.
