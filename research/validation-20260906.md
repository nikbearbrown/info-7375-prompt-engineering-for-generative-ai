# Local validation evidence

Command: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_course.py`

Run in the course repository on 2026-09-06. Exit code 0. This is a local offline suite, not a live Claude experiment.

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
Ran 13 tests in 0.004s

OK
PASS: 15 lessons, 90 lesson tests, integration suite, Python-only structure, and local links
```
