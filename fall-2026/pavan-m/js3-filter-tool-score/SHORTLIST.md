# Source-grounded shortlist — FILTER v1.1, top 10 by score

Every claim in each kept posting's justification was labeled by me against the posting's own text (shortlist/claim_labels.csv, with evidence quotes), using FILTER.md §3. Posting text and claims: shortlist/SHORTLIST_postings.md. Run: out/runs/2026-11-23T153111.

## Results (50 claims, 10 postings)

| Claim | SUPPORTED | CONTRADICTED | INSUFFICIENT |
|---|---|---|---|
| "The role requires <skill>" (20) | 4 | 4 | 12 |
| "Alex's ~3 years meets the experience requirement" (10) | 3 | 3 | 4 |
| "Open to US-based candidates" (10) | 10 | 0 | 0 |
| "Employer offers visa sponsorship" (10) | 0 | 0 | 10 |
| **Total** | **17** | **7** | **26** |

Only 17 of 50 claims (34%) are supported by the posting text. The location claims hold; the skill and experience claims mostly don't.

## Relevance is not entailment: S04, Software Engineer, IP Infrastructure (OpenAI)
The filter kept S04 partly because "Docker" appears in the text (Containers category). The justification therefore claimed "the role requires Docker". The posting says "prior expertise in every tool or a particular cloud provider is not required". The word matched, so the posting scored as relevant, but the text contradicts the claim. The same posting also asks for "4+ years of experience", contradicting the claim that Alex's ~3 years fits.
Across the shortlist, only 4 of 20 "requires <skill>" claims are supported: a keyword's presence shows the topic is mentioned, not that it is required.

## The abstention rule and a counterexample
Rule (FILTER.md §3.6): say "I cannot tell from the available posting text" when the description is missing, under 50 words, or the requested information is not in the posting.
Counterexample: S02, S05, S07 and S10 state no years of experience at all, yet each justification asserts "no explicit minimum of 5+ years, so Alex's ~3 years fits". The rule should have produced "I cannot tell" for that claim, but v1.0/v1.1 only abstain at the level of the whole posting (missing or short description), never for one claim. Absence of a requirement was treated as evidence that Alex qualifies, which §3.6 forbids.
Second limit, from the other direction: the years rule missed S09's "at least five years" because it only matches digits, so a posting that should be rejected under v1.1 was kept.

## What this shows and does not show
- These are my labels on 10 postings from one run; they show how often this justification template overclaims here, not a general rate.
- The justification is the filter's template, not a model's free-text answer; a Claude-written justification could overclaim differently.
