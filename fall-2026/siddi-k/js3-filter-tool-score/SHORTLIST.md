# The source-grounded shortlist (brief Step 2.2)

**The shortlist:** filter v1's kept postings, ranked by FILTER.md §A. v1 kept only 8, so the shortlist has 8, not 10.

**How each posting was checked (run 2026-11-26, `claude-sonnet-5-5` via CLI 2.1.325, each call in a new empty directory with built-in tools off):**
1. Claude wrote the justification as 4–7 claims, each with a quote copied from the posting (`prompts/justify_v1.md`). The justification is a **judgment**.
2. A **separate, fresh** Claude call labelled each claim supported / contradicted / insufficient under FILTER.md §B (`prompts/label_claims_v1.md`). It did not see the first call.
3. The **mechanical check** (`js3/evidence.py`) runs over both:
   - A quote that is not in the posting verbatim, is empty, or is only in cut boilerplate makes the claim **insufficient**, whatever Claude's labeller said.
   - A "contradicted" label counts only if the labeller's contradicting words are in the posting verbatim.
4. The **abstention rule** (FILTER.md §B) gives the agent's answer.

**Every claim, all 54 of them, with quote, check, labeller reason and final label:** [output/shortlist/SHORTLIST-CLAIMS.md](output/shortlist/SHORTLIST-CLAIMS.md). Raw Claude stdout for all 16 calls: `output/shortlist/filter-v1/2026-11-26T02-59-56Z/raw/`.

## Results

**Final labels:** 34 supported, 18 insufficient, 2 contradicted. Every quote Claude gave was found verbatim in its posting; the 7 empty quotes were all absence claims ("does not state…").

**The mechanical check overrode Claude's labeller 6 times,** all on absence claims ("the posting does not state a degree requirement"). The labeller called them supported. FILTER.md §B calls them insufficient, because there is no quote.

| # | Posting | Agent's answer (rule) | Siddi's blind label |
|---|---|---|---|
| 1 | PhD Data Scientist, Intern (Stripe) | relevant | relevant |
| 2 | PhD Machine Learning Engineer, Intern (Stripe) | **I cannot tell** (location claim insufficient) | relevant |
| 3 | Master's Machine Learning Engineer, Intern (Stripe) | **I cannot tell** (location claim insufficient) | relevant |
| 4 | Security Engineer, Detection and Response (Notion) | relevant | **not relevant** |
| 5 | Technical Operations Engineer, Revenue (Stripe) | **I cannot tell** (role claim insufficient) | relevant |
| 6 | Analytics Engineer (Stripe) | not relevant (years claim contradicted) | **relevant** |
| 7 | Business Systems Engineer (Notion) | relevant | relevant |
| 8 | Software Engineer, Early Career (AI) (Notion) | relevant | relevant |

The agent answered 5 and agreed with Siddi on 3 of them. It abstained on 3, all of which Siddi calls relevant.

## Relevance is not entailment

**Notion, "Security Engineer, Detection and Response"** (#4):
- **Relevance.** The filter kept it with score 5: python, sql, gcp and kubernetes, plus topic words. One of those, "ai", came from Notion's company blurb (AUDIT.md).
- **Entailment.** Claude's role claim is "The role is a security detection engineer … **not** a data engineering, machine learning or AI role". It quotes "We're looking for a hands-on Detection Engineer to build and operate the systems … to detect and respond to attacks". The labeller marked it **supported**.
- **So:** the posting matches Jordan's words, and its own text supports the opposite of the claim the shortlist needed, that this is a data or ML job. Siddi's blind label agrees: not relevant.

**A second case, in the other direction.** For **Analytics Engineer** (#6) the filter passed G3, because "5+ years in an analytics engineering or data analyst role" has no word "experience". The years claim quoting that sentence was labelled **contradicted** (the cap is 4). So the evidence check caught what the keyword gate missed.

## The abstention rule and the counterexamples that expose its limits

The rule (FILTER.md §B):
- If the posting's text or location is missing, answer "I cannot tell".
- Otherwise, if a role, location or years claim is contradicted, answer "not relevant".
- Otherwise, if the role or location claim is not supported, answer "I cannot tell".
- Otherwise, answer "relevant".

1. **It checks support, not meaning** (#4, and #7 in milder form):
   - The Security Engineer's role claim is supported, but what it says is "not a data/ML role". The rule only asks whether the deciding claim is supported, so it answers **relevant**, a confident wrong answer by Siddi's label.
   - The Business Systems Engineer's supported role claim also says "not a dedicated data engineering or machine learning role", and that answer happens to match Siddi.
   - **The limit:** support for a claim is not support for the conclusion. A fix would make the justification prompt write the deciding claims in a fixed form ("This job is data engineering, ML or AI work"). That has not been done or measured.
2. **It abstains when a person would not** (#2, #3):
   - The location "San Francisco, New York City, Seattle" was labelled insufficient for "in the United States", because §B allows abbreviations but not inference, and a city name does not literally say "US".
   - Siddi labels both internships relevant, and labelled #3 relevant in JS1 too.
   - **The limit:** strict entailment cannot use common knowledge, so the rule says "I cannot tell" about facts nobody doubts.
3. **An absence can never be supported** (6 claims): "The posting does not state required years" is true, but under §B it has no quote, so it is insufficient. The rule only works because §B says a missing years figure is not a reason to abstain.

## What a person checked, and what nobody checked

- Siddi's blind labels on all 8 postings are the check on the agent's **answers** (table above).
- Nobody checked the 54 **claim labels** by hand. They rest on the mechanical quote check plus a second Claude call, and that call can be wrong the same way the first one is.
- That gap is listed under "Not checked" in the sign-off.
