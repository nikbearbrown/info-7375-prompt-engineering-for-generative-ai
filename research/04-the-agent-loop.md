# Research notes — The agent loop

Status: initial implementation-source pass, 2026-09-06. Not approved for chapter drafting. Each item below is an agent inspection finding awaiting human review; no verified fact passport is implied.

## Primary local source

INFO 7375 course contributors, The agent loop, code/main.py (course adaptation 2026), [implementation](../lessons/04-the-agent-loop/code/main.py). Read in full during this pass. Companion [lesson](../lessons/04-the-agent-loop/docs/en.md) and [tests](../lessons/04-the-agent-loop/code/tests/test_main.py) remain scheduled for full chapter-specific reading. The course code is primary evidence of its own behavior, not of Claude internals or security guarantees.

## Claim ledger

1. **C04-1:** run consumes actions from an iterator and enforces a positive turn budget. Source: the local implementation above; inspection-supported, awaiting review.

2. **C04-2:** Policy exhaustion returns incomplete; an exhausted budget returns budget-exhausted. Source: the local implementation above; inspection-supported, awaiting review.

3. **C04-3:** A finish action immediately returns finished; its answer is not compared with the recorded observation. Source: the local implementation above; inspection-supported, awaiting review.

## Execution evidence

The course validator ran on 2026-09-06: 15 demos, 90 lesson tests, and 13 integration tests passed. See [raw validation output](validation-20260906.md). That suite result does not independently verify every proposed chapter example or claim.

## External sources

[UNVERIFIED] No external source added in this initial pass. Gather the relevant primary documentation and mathematical references before drafting broader claims.

## Remaining research and exclusions

- Read the complete lesson text, six tests, and artifact requirements and reconcile them with chapters-spec.md.
- Independently calculate or reproduce the proposed worked example; store actual outputs and interpreter version.
- Verify the relevant external documentation or derivation, with retrieval date and claim-level support.
- Read relevant companion-book passages before including any closing note; no empirical claim is imported by title alone.
- [UNVERIFIED] Full chapter source coverage is incomplete. Gate 1 remains open; do not draft from these notes alone.
- Do not describe the third ledger item as a newly fixed defect: this pass documents boundaries and makes no code changes.

## Executed second pass — 2026-09-06

This addendum supersedes the initial-pass task checklist above. The lesson and tests have now been inspected, and the proposed example has been exercised against the implementation. The research is evidence for review, not a human signature or a completed chapter.

A lookup of blue followed by finish(red) ends with finished status. Repeated lookups exhaust a budget of two. Termination and factual correctness are separate properties.

See [reproducible script](worked_examples.py), [recorded output](worked-examples.json) (key `chapters.04`), [primary source register](sources.md), and [scope and review packet](review-packet.md). Optional companion notes and new empirical claims require passage-specific support; unsupported material is excluded, not silently marked verified.

