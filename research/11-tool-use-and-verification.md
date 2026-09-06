# Research notes — Claude tool use and verification

Status: initial implementation-source pass, 2026-09-06. Not approved for chapter drafting. Each item below is an agent inspection finding awaiting human review; no verified fact passport is implied.

## Primary local source

INFO 7375 course contributors, Claude tool use and verification, code/main.py (course adaptation 2026), [implementation](../lessons/11-tool-use-and-verification/code/main.py). Read in full during this pass. Companion [lesson](../lessons/11-tool-use-and-verification/docs/en.md) and [tests](../lessons/11-tool-use-and-verification/code/tests/test_main.py) remain scheduled for full chapter-specific reading. The course code is primary evidence of its own behavior, not of Claude internals or security guarantees.

## Claim ledger

1. **C11-1:** dispatch accepts only add with exactly two finite numeric arguments and rejects booleans and overflowing results. Source: the local implementation above; inspection-supported, awaiting review.

2. **C11-2:** results associates tool_result with tool_use_id; loop preserves assistant content and appends user results. Source: the local implementation above; inspection-supported, awaiting review.

3. **C11-3:** The bounded loop ends on end_turn without checking the final claim's factual correctness. Duplicate IDs are checked within one content batch, not globally across turns. Source: the local implementation above; inspection-supported, awaiting review.

## Execution evidence

The course validator ran on 2026-09-06: 15 demos, 90 lesson tests, and 13 integration tests passed. See [raw validation output](validation-20260906.md). That suite result does not independently verify every proposed chapter example or claim.

## External sources

Anthropic, Handle tool calls, Claude Platform Docs (rolling documentation; accessed 2026-09-06), primary: https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls . Page retrieved; detailed message-order and error-handling comparison remains pending.

## Remaining research and exclusions

- Read the complete lesson text, six tests, and artifact requirements and reconcile them with chapters-spec.md.
- Independently calculate or reproduce the proposed worked example; store actual outputs and interpreter version.
- Verify the relevant external documentation or derivation, with retrieval date and claim-level support.
- Read relevant companion-book passages before including any closing note; no empirical claim is imported by title alone.
- [UNVERIFIED] Full chapter source coverage is incomplete. Gate 1 remains open; do not draft from these notes alone.
- Do not describe the third ledger item as a newly fixed defect: this pass documents boundaries and makes no code changes.

## Executed second pass — 2026-09-06

This addendum supersedes the initial-pass task checklist above. The lesson and tests have now been inspected, and the proposed example has been exercised against the implementation. The research is evidence for review, not a human signature or a completed chapter.

The local add tool returns 42 for 17+25 with matching call identifiers. Boolean arguments and duplicate IDs are rejected. An end_turn answer of 99 can still finish. An independent arithmetic check, not protocol termination, establishes this example's correct answer.

See [reproducible script](worked_examples.py), [recorded output](worked-examples.json) (key `chapters.11`), [primary source register](sources.md), and [scope and review packet](review-packet.md). Optional companion notes and new empirical claims require passage-specific support; unsupported material is excluded, not silently marked verified.

