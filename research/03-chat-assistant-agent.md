# Research notes — Chat, assistant, and agent

Status: initial implementation-source pass, 2026-09-06. Not approved for chapter drafting. Each item below is an agent inspection finding awaiting human review; no verified fact passport is implied.

## Primary local source

INFO 7375 course contributors, Chat, assistant, and agent, code/main.py (course adaptation 2026), [implementation](../lessons/03-chat-assistant-agent/code/main.py). Read in full during this pass. Companion [lesson](../lessons/03-chat-assistant-agent/docs/en.md) and [tests](../lessons/03-chat-assistant-agent/code/tests/test_main.py) remain scheduled for full chapter-specific reading. The course code is primary evidence of its own behavior, not of Claude internals or security guarantees.

## Claim ledger

1. **C03-1:** SURFACES assigns reason/read/write capabilities to three teaching labels. Source: the local implementation above; inspection-supported, awaiting review.

2. **C03-2:** classify returns agent if a write event appears and otherwise classifies by read presence. Source: the local implementation above; inspection-supported, awaiting review.

3. **C03-3:** These labels are an invented instructional taxonomy, not a verified specification of actual products. Source: the local implementation above; inspection-supported, awaiting review.

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

The reason/read/write capability exercise reports different missing capabilities by mode. Its names are a course-specific action-surface classifier, not Anthropic's workflow/agent taxonomy.

See [reproducible script](worked_examples.py), [recorded output](worked-examples.json) (key `chapters.03`), [primary source register](sources.md), and [scope and review packet](review-packet.md). Optional companion notes and new empirical claims require passage-specific support; unsupported material is excluded, not silently marked verified.

