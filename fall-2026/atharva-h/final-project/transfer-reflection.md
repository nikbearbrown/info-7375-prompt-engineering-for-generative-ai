# Transfer reflection

Packet document 10 of 10. Previous: [audit-note.md](audit-note.md) · Back to: [README.md](README.md)

The sections marked **Owner** are the owner's to write; the course grades them as the owner's own account. Claude's section is labelled as Claude's and is only a recommendation from the evidence.

## Evidence summary (facts, for the decision)

- **Development:** 4/10 with contract v1, then 9/10 with v2. **Held-out:** 5/5, scored once. All three unchanged after re-scoring with stricter comparators.
- **Unsafe SQL:** 0 executed. The model never tried; the policy is evidenced by tests and fixtures.
- **Deliberate failure cases:** 10/10 as predicted. **Controlled failure:** a replication of the October draft's failure, caught by the independent key and recovered.
- **Independent review:** 18 findings; 9 led to code changes, 9 acknowledged in docs.
- **Open defects** (after the independent review; fixed items are in `audit-note.md`):
  1. **Process:** contract v2 was used for scoring before owner review, so the held-out set is spent.
  2. **D8 whitespace:** the contract's `TRIM()` doesn't remove tabs or non-breaking spaces; the key does.
  3. **H3 false "MISMATCH":** the count check trusts the model's `answer_type`, and there's no `value` type.
  4. **No refuse field** in the reply schema.
  5. **File-mode approvals** aren't tied to a person or run.
  6. **The live CLI** is untested against the real model, and its 180 s timeout isn't capped by the question budget.
  7. **No real human gate decision** recorded.
  8. **No stranger run.**
- **Limits:** 15 questions, one file, one model run per question; answer keys built with Claude, not recounted by hand.

## Claude's recommendation (not the decision)

**Narrow.** The evidence supports shipping SponsorSQL as a **narrowed** portfolio piece: a supervised question-answerer for this one public FY2026 Q3 file, always showing its SQL and matching rows, with the evaluation published alongside it. It doesn't support a claim of general accuracy, or use on other DOL releases without a new freeze. Before calling it shipped:
- the owner reviews contract v2 (or replaces it)
- fix the contract-side defects in a v3 contract: a `value` answer type, a refuse field, and Unicode-whitespace trimming
- freeze a **new** held-out set written by someone other than the contract's author, and score it once
- record one real gate decision
- complete the stranger run

## What I will hand to an agent more readily — Owner

*To be written by the owner.*

## What I will keep practicing — Owner

*To be written by the owner.*

## Decision: ship, narrow, defer, or stop — Owner

*To be written and signed by the owner, with reasons tied to the evidence above. Also record it in [SIGNOFF.md](SIGNOFF.md).*
