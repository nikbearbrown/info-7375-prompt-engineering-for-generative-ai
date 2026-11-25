# SHORTLIST — source-grounded claims for kept postings

**Who did what.**
- **The claim labels are mine.** I checked each of the 72 quotes against its claim and filled in `my_label` on 2026-11-25, in my own copy of the sheet. My labels were copied into `state/claims/base_checked.csv` unchanged, and no other column moved.
- **Two labels changed later, at my request:** I asked Claude to make every label follow FILTER.md's rules. Claude checked all 72 against the exact-span rule. Only two of my labels broke it: two location quotes I had labeled supported. Both were changed to insufficient, and each row's `note` says so.
- **Claude's part:** `claude -p` wrote the claims, Claude's checker gave the first labels, and Claude drafted this write-up around my labels.
- **Status:** the write-up is waiting for my review.

## How the shortlist is made
1. **The filter decides.** v1.0 keeps 12 of the 4,240 postings. Claude never decides keep or reject.
2. **Claude writes claims.** For each kept posting, `claude -p` gives six fixed claims a status and a quote. The claims are role, seniority, years, location, sponsorship, and skills, worded in `claims.py`. A status is supported, contradicted, or insufficient.
3. **The substring checker labels each claim first:**
   - If the quote is found in the posting (after whitespace is collapsed), Claude's status stands.
   - If it isn't found, the claim is "insufficient".
4. **I confirm every label.** The checker can show that a quote is *there*. Only reading it shows whether it *says what the claim says*.
5. **The abstention rule:** the agent answers "I cannot tell" when the role, seniority, or location claim is insufficient, or the description is missing. Years and sponsorship never force it (FILTER.md "Evidence rules").

## My labels against the checker's
- **My labels:** 41 supported, 3 contradicted, 28 insufficient.
- **The checker's labels:** 42 supported, 4 contradicted, 26 insufficient.
- **We differ on 2 of the 72.** There were 4 before the two location labels were brought in line with the rule (see below).

| Posting | Claim | Claude's quote | Checker | Mine |
|---|---|---|---|---|
| FanDuel, Analyst | years: "The job requires 2 years of experience or fewer." | "2+ years' experience in an analytics/technical role preferred." | supported (quote found) | **insufficient** |
| FanDuel, Analyst | seniority: "The job is entry level or junior." | "Opportunity to mentor junior analysts on day-to-day requests as well as team best practices" | contradicted (quote found) | **insufficient** |

## Relevance is not entailment
**The case:** FanDuel, "Analyst", the years claim.
- **The claim:** "The job requires 2 years of experience or fewer."
- **What Claude said:** **supported**, quoting "2+ years' experience in an analytics/technical role preferred."
- **What the checker said:** the quote is in the posting, so the label is supported.
- **My label:** **insufficient**.
- **Why:** the quote is relevant, since it is about years of experience. But it states a *preferred* minimum of 2 years. It doesn't say the job requires 2 years or fewer, and it doesn't say what is required at all.

**The same posting, the seniority claim:**
- **What Claude said:** **contradicted**, quoting "Opportunity to mentor junior analysts…".
- **My label:** **insufficient**.
- **Why:** mentoring junior analysts is about the team, not a statement of this job's level.
- **Note:** on the second run of the same prompt (C0' in `SCORE.md`), Claude itself called this claim insufficient.

**What it means:** a quote the checker found is a necessary condition for "supported", not a sufficient one. That is why FILTER.md has me confirm every label, and why `SCORE.md` reports "quotes found", never "claims verified".

**The other direction: two labels brought back in line with the rule.**
- **Where:** two location quotes begin with "Locations:", the prompt's own field name, not part of the posting. They are Veeva ADP's ("Locations: New York - New York City") and FanDuel "Analyst"'s ("Locations: New York City; New York Office").
- **My first labels:** supported, because the location after the field name is in the posting.
- **What FILTER.md says:** "insufficient … if the quoted span is not in the text".
- **The change:** I asked Claude to make every label follow the rules, so both are now insufficient, with the change recorded in each row's `note`.
- **The lesson:** the content was right, and the evidence was malformed. The rule judges the evidence. The prompt fix C3 (`SCORE.md`) stops Claude from copying field names in the first place.

## The shortlist
Answers computed from **my** labels with `python3 claims.py confirmed`, saved in `state/claims/base_answers_my_labels.json`.

| Posting | Filter score | Agent's answer (my labels) | What made it abstain | My posting label (side) |
|---|---|---|---|---|
| FanDuel, Campaign Analytics, Data Analyst | 9 | I cannot tell | seniority | **yes** (held-out) |
| Stripe, Data Analyst, SF | 8 | I cannot tell | seniority | no (tuning) |
| Veeva, Marketing Analytics Data Analyst, ADP | 7 | I cannot tell | location (the quote began with "Locations:") | no (tuning) |
| Zoox, Student Worker, Data Analyst (part-time) | 7 | **keep** | — | no (tuning) |
| Zoox, Financial Analyst, Marketing and Commercial | 7 | I cannot tell | role | not labeled (audit: wrong keep) |
| Stripe, Data Analyst, Intern | 6 | **keep** | — | no (tuning) |
| Axios, Salesforce Business Analyst | 6 | **keep** | — | no (tuning) |
| FanDuel, Analyst | 6 | I cannot tell | seniority; location (the quote began with "Locations:") | **yes** (held-out) |
| Datadog, FP&A Analyst, Cloud Finance | 5 | I cannot tell | role, seniority | not labeled (audit: wrong keep) |
| Datadog, FP&A Analyst R&D | 4 | I cannot tell | role, seniority | not labeled (audit: wrong keep) |
| FanDuel, Product Analyst (NYC) | 4 | I cannot tell | seniority | no (tuning) |
| FanDuel, Product Analyst (Atlanta) | 4 | I cannot tell | seniority | no (tuning) |

**Coverage, from my labels:** 3 of 12 answered, and all 3 answers are labeled "no". The agent abstains on both "yes" postings. These are the same answers the checker's labels give.

**Veeva's sponsorship:** its sponsorship claim is "contradicted" by "Veeva does not provide sponsorship…", but under FILTER.md sponsorship never forces an abstention. Only R4 can reject on it, and R4's phrases miss this wording (F1 in `SCORE.md`). Veeva is an abstention here only because of a malformed location quote. With C3's clean quotes, it would be a confident wrong "keep".

## The abstention rule, and its counterexamples
**The rule:** abstain when the role, seniority, or location claim is insufficient, or the description is missing.

**Counterexample 1, a confident wrong answer:** Zoox's part-time student worker.
- I labeled its role, seniority, and location claims all **supported**, so the agent answers **keep**.
- Riley wouldn't apply: it's a part-time student contract (my audit, row #34).
- The rule abstains on missing evidence. It doesn't abstain on a property it doesn't track, like employment type. Stripe's intern posting (graduation date) and Axios (Salesforce administration experience) fail the same way.

**Counterexample 2, abstaining on a match:** FanDuel, "Campaign Analytics, Data Analyst", labeled "yes".
- The posting never says "entry level" or "junior", so the seniority claim is insufficient (my label agrees) and the agent answers **I cannot tell**.
- Yet "Minimum of 1+ years of previous experience in a similar role" is clear enough for Riley, and I labeled the posting "yes".

**What was measured:** dropping the seniority clause (A1 in `SCORE.md`) fixes counterexample 2, but answers 6 of 7 tuning postings, all wrong. I rejected A1 on 2026-11-25 (FILTER.md v1.2), so the rule stays as it is, and coverage is reported next to accuracy, so an abstention is never counted as a correct answer.
