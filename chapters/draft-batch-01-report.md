# Draft batch 1 — 2026-09-06

Research approval recorded in [approval](../research/approval-20260906.md). Five chapters drafted in Teardown register, with paired lessons, worked examples, citations, graduated ungraded Assessments, figure-needs markers, and selective closing notes. Full draft is not complete: chapters 6–15 remain absent. Their drafting is already authorized and requires no new planning or research gate.

## Checks actually run

- Structural draft checker: exit 0. Counts use whitespace-delimited manuscript tokens, including headings, code, and tables; they are not a claim of editorial approval.
- Offline worked-example script, all 15 research cases: exit 0.
- Course validator: exit 0; 90 lesson tests plus 13 integration tests pass.
- Embedded Python blocks parse; paired lesson/quiz links and local link targets exist.
- Each saved chapter has an unsigned draft sidecar. No human rewrite or full-book fact-check is claimed.
- Cajal figure needs are markers only. No figures or EPUB were generated.

## Structural result

```json
{
  "scope": "structural checks only; not prose, source, or human approval",
  "chapters": [
    {
      "chapter": "01-randomness-and-first-prompts.md",
      "whitespace_words": 5628
    },
    {
      "chapter": "02-prompt-contracts-and-evaluation.md",
      "whitespace_words": 6108
    },
    {
      "chapter": "03-chat-assistant-agent.md",
      "whitespace_words": 6155
    },
    {
      "chapter": "04-the-agent-loop.md",
      "whitespace_words": 5648
    },
    {
      "chapter": "05-tools-and-permissions.md",
      "whitespace_words": 5904
    }
  ],
  "total_whitespace_words": 29443,
  "pending": [
    "06-claude-code-and-diff-review.md",
    "07-context-retrieval-and-cowork.md",
    "08-mcp-from-scratch.md",
    "09-training-and-configuration.md",
    "10-planning-before-acting.md",
    "11-tool-use-and-verification.md",
    "12-memory-and-multiple-agents.md",
    "13-evaluation-and-approval-gates.md",
    "14-team-governance-and-ethics.md",
    "15-supervised-capstone.md"
  ],
  "full_draft_exists": false,
  "failures": []
}
```

## Editorial review still required

The first five manuscripts are full-length AI drafts, not author-approved final prose. Human review should examine repetition across chapters, the balance of mechanism and supervisory commentary, and exercise difficulty. The exact Teardown sub-section word allocations have not been independently certified. The chapters stay within the overall approved range.

Chapter 3 distinguishes executed research cases from additional trace labels derived by code inspection. Chapter 4 distinguishes bounded iteration from wall-clock timeouts and notes that finish is not appended to the reference trace. Chapter 5 does not claim that changing the original symlink necessarily redirects a returned resolved path; the remaining gap is preflight-to-use integration and mutable filesystem state.

Additional companion passages read during drafting were limited to the specified supervision practices: Conducting AI chapter 3 and Computational Skepticism chapters 4 and 8. Broader empirical assertions in those manuscripts are not imported. The Anthropics note in chapter 2 uses the checked upstream evaluations overview, not a claim that every notebook was reviewed.

## Course validation output

```text
Week 01: demo and 6 tests checked
Week 02: demo and 6 tests checked
Week 03: demo and 6 tests checked
Week 04: demo and 6 tests checked
Week 05: demo and 6 tests checked
Week 06: demo and 6 tests checked
Week 07: demo and 6 tests checked
Week 08: demo and 6 tests checked
Week 09: demo and 6 tests checked
Week 10: demo and 6 tests checked
Week 11: demo and 6 tests checked
Week 12: demo and 6 tests checked
Week 13: demo and 6 tests checked
Week 14: demo and 6 tests checked
Week 15: demo and 6 tests checked
test_full_fixture_lifecycle (test_integration.McpTests.test_full_fixture_lifecycle) ... ok
test_budget_stops_repeated_actions (test_integration.ToolLoopTests.test_budget_stops_repeated_actions) ... ok
test_duplicate_ids_rejected (test_integration.ToolLoopTests.test_duplicate_ids_rejected) ... ok
test_multiple_results_and_history (test_integration.ToolLoopTests.test_multiple_results_and_history) ... ok
test_overflow_rejected (test_integration.ToolLoopTests.test_overflow_rejected) ... ok
test_budget (test_integration.TransportTests.test_budget) ... ok
test_http_error_is_sanitized (test_integration.TransportTests.test_http_error_is_sanitized) ... ok
test_malformed_response (test_integration.TransportTests.test_malformed_response) ... ok
test_missing_key (test_integration.TransportTests.test_missing_key) ... ok
test_mock_transport_headers_and_timeout (test_integration.TransportTests.test_mock_transport_headers_and_timeout) ... ok
test_offline_denied_before_key_access (test_integration.TransportTests.test_offline_denied_before_key_access) ... ok
test_request_shape (test_integration.TransportTests.test_request_shape) ... ok
test_requires_claude (test_integration.TransportTests.test_requires_claude) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.003s

OK
PASS: 15 lessons, 90 lesson tests, integration suite, Python-only structure, and local links
```

