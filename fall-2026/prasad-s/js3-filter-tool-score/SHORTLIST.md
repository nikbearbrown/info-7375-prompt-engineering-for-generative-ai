# SHORTLIST.md — Job-Search Agent 3: the source-grounded shortlist

**Author:** Prasad Shinde
**Written:** 2026-11-19
**Version:** v1 — 2026-11-19
**Rests on:** FILTER.md v2 (JS3-CP8a) and its run, output/filter_v2_2026-11-19T201210Z/ (JS3-CP8c); the evidence rules in FILTER.md §2; my claim labels, shortlist/claim_labels.tsv (JS3-CP9a, corrected in JS3-CP9b).

## 1. The shortlist
(Brief: "For each posting on your shortlist, label every claim in its justification supported / contradicted / insufficient against the posting text.")

FILTER v2 kept 2 of the 1,248 development postings; the 50 sealed postings were not judged. In F8 order:

| Position | Posting | Location |
|---|---|---|
| 1 | ashby:notion 11e56782-ee28-4025-ba0e-76222b0bfcea, "AI Product Manager, Growth Marketing" | New York, New York; San Francisco, California |
| 2 | greenhouse:stripe 7737124, "Product Manager: New Grad Accelerator" | San Francisco, New York City, Seattle |

Both score 0 (no persona skill in the text), so they tie on score, and F8 orders them by board key: ashby:notion before greenhouse:stripe.

## 2. Every claim, labeled
The agent's justification is output/filter_v2_2026-11-19T201210Z/justifications.tsv: one claim for each reason it kept the posting. I labeled each claim against the posting's own text under FILTER.md §2 (shortlist/claim_labels.tsv):

| Posting | Claim | Field | Label | Span |
|---|---|---|---|---|
| 1 | The title names a target role: Product Manager. | title | supported | AI Product Manager, Growth Marketing |
| 1 | The location is workable: New York. | location | supported | New York |
| 1 | The title has no seniority word. | title | supported | AI Product Manager, Growth Marketing |
| 1 | The posting asks for no more than 3 years of experience. | text | **insufficient** | no span either way: the text states no number of years |
| 2 | The title names a target role: Product Manager. | title | supported | Product Manager: New Grad Accelerator |
| 2 | The location is workable: New York. | location | supported | New York City |
| 2 | The title has no seniority word. | title | supported | Product Manager: New Grad Accelerator |
| 2 | The posting asks for no more than 3 years of experience. | text | supported | New grad or 0-2 years of professional experience |

Seven of the 8 claims are supported, 1 is insufficient, and none is contradicted. My first labels (JS3-CP9a) marked claim 1.4 supported with "no span either way", and 1.3 and 2.3 supported with no span. Under §2, a supported claim needs a span that states it, so JS3-CP9b corrected all three.

## 3. Relevance is not entailment
(Brief: "Show one case where relevance is not entailment: a posting that matches your words but does not support the claim.")

**From the audit: "Product Manager" in a Staff title.** In audit row 36, "Staff Product Manager, Startup Products" (greenhouse:stripe, NYC), FILTER v1's C1 matches "Product Manager" in the title, so the agent claims "The title names a target role: Product Manager." The words are there, so the posting is relevant to the rule. But it does not support what the agent uses the claim for, that this is Alex's target role: the same title says "Staff", which on PM ladders sits above Senior, far beyond Alex's 3 years. This is the false friend of AUDIT.md §8, which FILTER v2's F9 now catches.

**From the shortlist itself: claim 1.4.** Posting 1 passes C4 because its text states no number of years above 3. The agent turns that into the claim "The posting asks for no more than 3 years of experience." Nothing in the text says so: not finding a requirement is not the posting stating a limit. The rule's pass is relevant; it does not entail the claim. Posting 2 shows the difference: its text says "New grad or 0-2 years of professional experience", which does state the claim.

## 4. The abstention rule, and a counterexample to it
(Brief: "Show your abstention rule and one counterexample that exposes its limits.")

**The rule** (FILTER.md F7 and §2): the agent says "I cannot tell" (1) for a posting whose missing field would decide its verdict (cannot_tell, reported in its own list); (2) for a claim labeled insufficient, including one where two spans disagree; and (3) for a board that was not checked, never turning that into "no relevant postings".

**The counterexample: claim 1.4.** Posting 1's text is present but says nothing about years. F7 abstains only when a field is missing, so it never fires here: C4 passes, and the agent asserts "The posting asks for no more than 3 years of experience" instead of saying "I cannot tell". The rule's limit is that it treats a silent field as an answered one. The corpus shows how little the rule covers as built: F7 fired on 0 of 1,248 development postings under both v1 and v2 (each run's summary.txt), while 1 of the 8 claims on a 2-posting shortlist needed it.

What would close the gap, not built in JS3: when C4 passes because no years are stated, the agent should claim "The text states no number of years", which is supported, or abstain on the level claim, instead of claiming a limit. It is recorded here as a known limit of FILTER v2.

## 5. What this does not show
- The shortlist is 2 postings. Its labels say nothing about how often the agent's claims hold in general.
- The labels are mine, under §2, and I corrected three of them after review (§2 above).
- Both shortlisted postings were also audited (AUDIT.md §7, rows 8 and 58), so the rules that kept them were chosen with these postings in view. The held-out measurement (SEAL.md §9) is the independent test.

## Changelog
- **v1 — 2026-11-19.** Written after the claim labels were committed and corrected (JS3-CP9a, CP9b). Claude (Claude.ai) typed this text at my request from the committed files; the labels and decisions are mine.