# What the shortlist claims can support

The 2026-11-10 snapshot produced four kept postings. I checked all 50 claim labels in `CLAIMS_REVIEW_DRAFT.csv` against the saved postings and accepted them without label changes. The reviewed `CLAIMS.csv` has 11 supported, 5 contradicted, and 34 insufficient claims. I narrowed two seniority excerpts after that review; the reviewed CSV excerpts are the final record and may differ from a fresh draft. `SHORTLIST.md` renders the reviewed CSV; a score of 7 does not turn an insufficient claim into a fact.

## Relevance is not entailment

**A12 — Software Engineer II, Test Frameworks & Tooling:** The posting passed the filter and was judged worth reviewing. Its technology list puts TypeScript under “Frontend,” but that does not establish the draft claim “The role requires TypeScript.” That claim is labeled `insufficient`, with the missing fact named in `CLAIMS.csv`. The same posting explicitly asks for 2+ years of software-engineering experience, which supports the narrower experience claim.

**A07 — Software Engineer, Conversational Products & Agent Workflows:** The posting passed and was judged relevant. It explicitly asks for 3+ years, contradicting the draft claim that it is open to someone with about two years. The score did not detect that mismatch because v1 has no requirement-years rule.

**A38 and A41 — Patch My PC:** Both scored 7 and were kept by v1, yet the reviewed verdicts were `not_relevant`. Each asks for 5+ years of C# development. The saved text also says the positions are not eligible for visa sponsorship, and its exhaustive remote-state list omits Massachusetts. The filter's `workplaceType: remote` match did not establish that a Boston resident could work remotely in either role.

## Abstention and its limit

The render step states only `supported` claims as positive facts, reports explicit contradictions, and says “I cannot tell” with the missing detail for `insufficient` claims. A07 is a concrete limit of a stricter score-only abstention rule: raising the cutoff from 6 to 8 would drop a score-7 posting that I judged worth review. Conversely, A12 shows why passing the score does not authorize the stronger TypeScript claim.

These labels establish what the saved postings said on the snapshot date. They do not independently verify that an opening remains active, that an employer's statements are current, or that pursuing a posting will lead to an interview or offer.
