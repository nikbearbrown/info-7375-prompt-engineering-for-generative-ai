# Transfer reflection

Packet document 10 of 10. Previous: [audit-note.md](audit-note.md) · Back to: [README.md](README.md)

The sections marked **Owner** are the owner's to write; the course grades them as the owner's own account. Claude's section is labelled as Claude's and is only a recommendation from the evidence.

## Evidence summary (facts, for the decision)

- **Development:** 4/10 with contract v1, then 9/10 with v2. **Held-out:** 5/5, scored once. **Unsafe SQL executed:** 0. **Deliberate failure cases:** 10/10 as predicted. **Controlled failure:** caught by the independent key and recovered.
- **Open defects:**
  1. D8 whitespace: the contract's `TRIM()` doesn't remove tabs or non-breaking spaces; the key does.
  2. A false "MISMATCH" warning when a single non-count value is labelled `count` (H3).
  3. The live CLI adapter is untested against the real model, because the CLI wasn't logged in.
  4. No real human gate decision recorded yet.
  5. No stranger run yet.
- **Limits:** 15 questions, one file, one model run per question; answer keys built with Claude, not recounted by hand.

## Claude's recommendation (not the decision)

**Narrow.** The evidence supports shipping SponsorSQL as a **narrowed** portfolio piece: a supervised question-answerer for this one public FY2026 Q3 file, always showing its SQL and matching rows, with the evaluation published alongside it. It doesn't support a claim of general accuracy, or use on other DOL releases without a new freeze. Before calling it shipped:
- fix the two code-side defects (a `value` answer type, plus Unicode-whitespace trimming via `norm()` or a documented rule) as a v3 contract with a **new** held-out set
- record one real gate decision
- complete the stranger run

## What I will hand to an agent more readily — Owner

*To be written by the owner.*

## What I will keep practicing — Owner

*To be written by the owner.*

## Decision: ship, narrow, defer, or stop — Owner

*To be written and signed by the owner, with reasons tied to the evidence above. Also record it in [SIGNOFF.md](SIGNOFF.md).*
