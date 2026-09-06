# Research notes — MCP from scratch

Status: initial implementation-source pass, 2026-09-06. Not approved for chapter drafting. Each item below is an agent inspection finding awaiting human review; no verified fact passport is implied.

## Primary local source

INFO 7375 course contributors, MCP from scratch, code/main.py (course adaptation 2026), [implementation](../lessons/08-mcp-from-scratch/code/main.py). Read in full during this pass. Companion [lesson](../lessons/08-mcp-from-scratch/docs/en.md) and [tests](../lessons/08-mcp-from-scratch/code/tests/test_main.py) remain scheduled for full chapter-specific reading. The course code is primary evidence of its own behavior, not of Claude internals or security guarantees.

## Claim ledger

1. **C08-1:** Server requires initialize and notifications/initialized before tool use. Source: the local implementation above; inspection-supported, awaiting review.

2. **C08-2:** The server advertises one lookup tool and returns a text fixture with isError for missing records. Source: the local implementation above; inspection-supported, awaiting review.

3. **C08-3:** initialize returns the fixed version 2025-11-25 without evaluating the client's requested version; this is not full version negotiation. Source: the local implementation above; inspection-supported, awaiting review.

## Execution evidence

The course validator ran on 2026-09-06: 15 demos, 90 lesson tests, and 13 integration tests passed. See [raw validation output](validation-20260906.md). That suite result does not independently verify every proposed chapter example or claim.

## External sources

Model Context Protocol maintainers, Lifecycle, specification 2025-11-25 (accessed 2026-09-06), primary: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle . Page retrieved; detailed clause-by-clause comparison remains pending.

## Remaining research and exclusions

- Read the complete lesson text, six tests, and artifact requirements and reconcile them with chapters-spec.md.
- Independently calculate or reproduce the proposed worked example; store actual outputs and interpreter version.
- Verify the relevant external documentation or derivation, with retrieval date and claim-level support.
- Read relevant companion-book passages before including any closing note; no empirical claim is imported by title alone.
- [UNVERIFIED] Full chapter source coverage is incomplete. Gate 1 remains open; do not draft from these notes alone.
- Do not describe the third ledger item as a newly fixed defect: this pass documents boundaries and makes no code changes.

## Executed second pass — 2026-09-06

This addendum supersedes the initial-pass task checklist above. The lesson and tests have now been inspected, and the proposed example has been exercised against the implementation. The research is evidence for review, not a human signature or a completed chapter.

Tool listing before initialization is rejected. Initialization returns version 2025-11-25, the initialized notification has no response, and a missing lookup returns isError. A fixed supported-version fallback can be legal under MCP; the teaching implementation's limited parameter/capability coverage, not fallback alone, prevents claiming full conformance.

See [reproducible script](worked_examples.py), [recorded output](worked-examples.json) (key `chapters.08`), [primary source register](sources.md), and [scope and review packet](review-packet.md). Optional companion notes and new empirical claims require passage-specific support; unsupported material is excluded, not silently marked verified.

