# Re-executed validation — 2026-09-06

Raw output from the local revision/hash inspection and validator. Python 3.14.6; no live model calls. This records execution, not human approval.

```text
a8629ce1c437abee3a2c4f025bd8be3183b0f0af
a2847abab5646fe09bcdcfa8fe744a784d9a9639d45ebb9ea519c6343b10326d  lessons/01-randomness-and-first-prompts/code/main.py
b05f14da33a90605cd1b23edfb129b2f8e8bcaf5f488f26cb9912d5175792eab  lessons/02-prompt-contracts-and-evaluation/code/main.py
d7568e952ae8275ad4d1d27e0c2c393e75edb8074e31b1221dbfa224e4024daa  lessons/03-chat-assistant-agent/code/main.py
9bc21179b2063647cee464702b04e9a600e57bf1d84ef6f62c8569996cf7fd11  lessons/04-the-agent-loop/code/main.py
7e2d124d20d2ab3e6ce25cee8c40fba2eef6d96a70c91316f09244741a2cf1fe  lessons/05-tools-and-permissions/code/main.py
de166d8785a572f5d0f76c518e168d6c8dba0fe62b749ad7fecc30244f03e04b  lessons/06-claude-code-and-diff-review/code/main.py
3aa9ef7955b78a78d54f3cf58778fb96048b4be1810cd2dae23e084291ca7dca  lessons/07-context-retrieval-and-cowork/code/main.py
948337afc71b67b659aac44b4a8f3efec5dc699b9bb7c2e683dd6888068b1769  lessons/08-mcp-from-scratch/code/main.py
81b9863ce238f3c7d89ca8e46d663efd94e238ff1782bbe9b94ea8194da969c2  lessons/09-training-and-configuration/code/main.py
cc0ef5ac595bf1b1550519b65438b461697c6a2a18b100fb2b60d4a6bedb0e93  lessons/10-planning-before-acting/code/main.py
382c1fece2f7db737b335cf6a4b7c0789780c620032826f5e5be098998b535fe  lessons/11-tool-use-and-verification/code/main.py
ecf1bd6eaba2cbf7c77f5ee86b1ab646c0f1c79e501a2c091a9d77af16d125f5  lessons/12-memory-and-multiple-agents/code/main.py
d5d25a203f8e1254cccff6750f5ead7d2ac528f87b27650f26e79aa75edfd8ba  lessons/13-evaluation-and-approval-gates/code/main.py
87c35b54fd5269be5d13b719de5a9c27d297aec8ef76856ef5a4cae02b220919  lessons/14-team-governance-and-ethics/code/main.py
ce9d60388665270f942f123525d4990b652cbc0b66fba46e0767c15b6688f9ad  lessons/15-supervised-capstone/code/main.py
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
Ran 13 tests in 0.004s

OK
PASS: 15 lessons, 90 lesson tests, integration suite, Python-only structure, and local links
```

