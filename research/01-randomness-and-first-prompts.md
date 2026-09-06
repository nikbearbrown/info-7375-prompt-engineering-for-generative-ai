# Research notes — Randomness and first prompts

Status: initial implementation-source pass, 2026-09-06. Not approved for chapter drafting. Each item below is an agent inspection finding awaiting human review; no verified fact passport is implied.

## Primary local source

INFO 7375 course contributors, Randomness and first prompts, code/main.py (course adaptation 2026), [implementation](../lessons/01-randomness-and-first-prompts/code/main.py). Read in full during this pass. Companion [lesson](../lessons/01-randomness-and-first-prompts/docs/en.md) and [tests](../lessons/01-randomness-and-first-prompts/code/tests/test_main.py) remain scheduled for full chapter-specific reading. The course code is primary evidence of its own behavior, not of Claude internals or security guarantees.

## Claim ledger

1. **C01-1:** probabilities subtracts the maximum logit, exponentiates temperature-scaled differences, and normalizes the weights. Source: the local implementation above; inspection-supported, awaiting review.

2. **C01-2:** sample creates a local seeded random.Random and uses weighted choices. Source: the local implementation above; inspection-supported, awaiting review.

3. **C01-3:** The example models a three-item distribution, not Claude's actual tokenizer, logits, or sampling controls. Source: the local implementation above; inspection-supported, awaiting review.

## Execution evidence

The course validator ran on 2026-09-06: 15 demos, 90 lesson tests, and 13 integration tests passed. See [raw validation output](validation-20260906.md). That suite result does not independently verify every proposed chapter example or claim.

## External sources

Python Software Foundation, random — Generate pseudo-random numbers, Python 3 documentation (rolling version; accessed 2026-09-06), primary: https://docs.python.org/3/library/random.html . The page confirms weighted choices with replacement and separately instantiated generator state.

## Remaining research and exclusions

- Read the complete lesson text, six tests, and artifact requirements and reconcile them with chapters-spec.md.
- Independently calculate or reproduce the proposed worked example; store actual outputs and interpreter version.
- Verify the relevant external documentation or derivation, with retrieval date and claim-level support.
- Read relevant companion-book passages before including any closing note; no empirical claim is imported by title alone.
- [UNVERIFIED] Full chapter source coverage is incomplete. Gate 1 remains open; do not draft from these notes alone.
- Do not describe the third ledger item as a newly fixed defect: this pass documents boundaries and makes no code changes.

## Executed second pass — 2026-09-06

This addendum supersedes the initial-pass task checklist above. The lesson and tests have now been inspected, and the proposed example has been exercised against the implementation. The research is evidence for review, not a human signature or a completed chapter.

Constructed logits [1, 2, 3] give probabilities [0.0900305732, 0.2447284711, 0.6652409558] at temperature 1. With seed 7 and 1,000 draws, counts are [102, 268, 630]. Independent direct-exponential normalization agrees with the stabilized implementation. These are toy sampling results, not Claude logits or accuracy.

See [reproducible script](worked_examples.py), [recorded output](worked-examples.json) (key `chapters.01`), [primary source register](sources.md), and [scope and review packet](review-packet.md). Optional companion notes and new empirical claims require passage-specific support; unsupported material is excluded, not silently marked verified.

