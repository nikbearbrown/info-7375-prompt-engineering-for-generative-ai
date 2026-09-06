# Research notes — Planning before acting

Status: initial implementation-source pass, 2026-09-06. Not approved for chapter drafting. Each item below is an agent inspection finding awaiting human review; no verified fact passport is implied.

## Primary local source

INFO 7375 course contributors, Planning before acting, code/main.py (course adaptation 2026), [implementation](../lessons/10-planning-before-acting/code/main.py). Read in full during this pass. Companion [lesson](../lessons/10-planning-before-acting/docs/en.md) and [tests](../lessons/10-planning-before-acting/code/tests/test_main.py) remain scheduled for full chapter-specific reading. The course code is primary evidence of its own behavior, not of Claude internals or security guarantees.

## Claim ledger

1. **C10-1:** missing_fields reports absent or false-valued required fields. Source: the local implementation above; inspection-supported, awaiting review.

2. **C10-2:** order repeatedly removes sorted ready steps and rejects duplicates, unknown prerequisites, and cycles. Source: the local implementation above; inspection-supported, awaiting review.

3. **C10-3:** Field presence does not establish plan meaning, authorization, or verification quality. Source: the local implementation above; inspection-supported, awaiting review.

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

The dependency order is inspect, build, verify; a cycle is rejected. A syntactically populated but semantically empty plan produces no missing-field findings. Structural validation cannot establish plan quality.

See [reproducible script](worked_examples.py), [recorded output](worked-examples.json) (key `chapters.10`), [primary source register](sources.md), and [scope and review packet](review-packet.md). Optional companion notes and new empirical claims require passage-specific support; unsupported material is excluded, not silently marked verified.

