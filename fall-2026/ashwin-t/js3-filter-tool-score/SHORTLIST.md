# Source-grounded shortlist (Step 2.2)

Drafted by Claude Code on 2026-11-25. **Ashwin has not labeled any claims yet: 0 of 90.** Every S / C / I label
belongs to Ashwin and goes in `shortlist/claim-sheet.csv`. The cases below are candidates for Ashwin to confirm or
reject once the claims are labeled. They are not conclusions.

## What ran

- **The shortlist:** the 18 development postings filter v1.0 kept, ranked as in `runs/v1.0/summary.md`. Filter v1.1
  adds 2 more, the Mission Manager postings, and **they have no claims**. The shortlist is v1.0's.
- **The claims:** one live, tool-free `claude -p` call per posting on 2026-11-25, 13:23:12–13:23:53 UTC, model
  `claude-opus-5-5`, prompt `prompts/claims-v1.md` (written by Claude Code, not tuned).
- **The raw replies:** `shortlist/claims-v1-2026-11-25T13-23-12Z/raw/`.
- **Validity:** 18 of 18 replies passed the strict JSON check, giving 90 claims, 19 of them abstentions.

## The rules

FILTER.md section 5 sets the evidence rules. Each claim gets one of three labels:
- **S, supported:** the posting states it, or a faithful paraphrase of it.
- **C, contradicted:** the posting says something incompatible with it.
- **I, insufficient:** the posting is silent or ambiguous, or has only a related word.

**Abstention rule.** The prompt makes the first two claims about experience level and US remote work. If the posting
does not settle one, the claim must read "I cannot tell from this posting: …" with an empty quote.
`jobfilter/claims.py` refuses a reply where the abstention and the empty quote disagree.

**Mechanical check.** `mechanical()` only says one of four things: the quote was found in the named field, it was
not found, it was found but contains a negation, or the claim abstained. It never says "supported". Wrong version W7
treats any present quote as support, so "Java is not required" would back "Java is required"; `test_w7_negated_quote`
catches it.

Mechanical results for the 90 claims:

| Result | Count |
|---|---:|
| Quote found | 70 |
| Abstained | 19 |
| Quote found, with a negation | 1 |
| Quote not found | 0 |

## Candidate: relevance is not entailment

`greenhouse/klaviyo/8041054003`, "Software Engineer, Conversational Products & Agent Workflows", Boston, is the
filter's top KEEP at score 8. It matched three of the résumé's topic groups (Python, Redis, Kubernetes), so it is
*relevant* by the filter's words.

Its first claim reads: "The posting asks for 3+ years of professional software engineering experience, which is
above a typical new-gr[ad level]", quoting "3+ years of professional software engineering experience". If Ashwin
labels that claim S, the posting matches the words but its own text works against the new-grad target. That would
be relevance without entailment.

Other KEEPs with the same pattern:
- `lever/palantir/832e4652…` and `…e47d4410…`: "4+ years of professional software development experience".
- `…cd2423c6…` and `…d5d83a8f…`: "3+ years…".

## Candidate: a counterexample to the abstention rule

The rule covers only experience and remote work. Palantir's "New Grad - Production Infrastructure" postings,
`…15844944…`, `…4d5a144e…` and `…e1a6c138…`, pass the experience claim with a real quote. The claim reads "The posting
is aimed at new graduates", quoting the title.

The same postings require "Active US Security clearance, or eligibility and willingness to obtain a US Security
clearance". Supriya's eligibility for that is unknown. No claim abstains on it, because the rule never asks.

So a posting can satisfy every abstention the rule demands and still hinge on a fact nobody can tell. Ashwin's audit
clearance rule (`drafting/EVALUATION-SETS.md`) marks these `?`, which the shortlist never surfaces.

**A second limit, for Ashwin to check:** an abstention passes validation however settled the question really is.
The sheet's instruction for abstention claims is S if the posting truly does not settle the question, and C if it
does. A C there would show the rule letting a wrong "I cannot tell" through.

## The one negation flag

One claim's quote contains a negation word: `lever/palantir/6fe5515f…`. The claim reads "The posting says experience
with highly-available distributed systems is not required." The quote is "Experience developing and managing
highly-available distributed systems is beneficial, but not required."

Here the claim states the negation itself, so the flag fires on a claim that reads correctly. That is why the flag
asks for a human and never decides. It needs Ashwin's S / C / I, like every other claim.

## Still to do (Ashwin)

- Label all 90 claims in `shortlist/claim-sheet.csv`.
- Confirm or replace the two candidate cases above.
- Decide whether the 2 v1.1-only KEEPs need claims, which would take a new live run.
