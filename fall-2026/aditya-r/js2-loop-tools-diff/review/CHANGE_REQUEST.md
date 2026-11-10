Change request — Validate Greenhouse response totals

Requested by: Aditya Raj  
Date: November 10, 2026  
Status: Requested; implementation and acceptance pending.

1. Behavior to change

I want the Greenhouse response validation to reject inconsistent posting counts before treating the acquisition as successful or updating state.

The reproduced input contains one posting but declares `meta.total = 40`. The current implementation accepts it, reports `COMPLETE: 0 new posting(s), 0 retried.`, and returns exit code 0.

My captured regression run fails at:

```text
assert inconsistent_exit == 3
E assert 0 == 3
```

Pytest returned status 1. This is a behavioral assertion failure, not an import, syntax, or collection error.

Evidence:

- `review/investigation_output_P2.txt`
- `review/INVESTIGATION.md`
- `tests/test_aditya_total_mismatch.py`
- `review/prepatch_failure.txt`

The input is synthetic. This does not demonstrate a failure of the live Greenhouse service.

2. Required behavior after the change

Under GATE sections 1 and 4:

1. When Greenhouse supplies `meta.total`, validate that it is a nonnegative integer. Explicitly reject booleans, strings, floats, null, and negative values rather than coercing them.
2. Compare the valid declared total with the number of entries in the returned `jobs` list.
3. If the counts disagree, reject the response as inconsistent acquisition before evaluating postings or modifying working state.
4. For this single-board count-validation failure, return `incomplete`, exit code 3.
5. Preserve the complete existing state file byte-for-byte, including run history.
6. Save a clear diagnostic identifying the problem. For the reproduced mismatch, report declared total 40 and observed list length 1.
7. Do not print a successful completion message or present the failed acquisition as a reliable zero-new-postings result.
8. Preserve the raw response and diagnostic evidence where the existing workflow supports them.

A matching count must continue through the existing validation and processing logic; it must not bypass other checks.

This patch validates a total when supplied. It must not invent a total when the field is absent or silently make optional metadata mandatory for previously supported archived inputs.

Do not treat count agreement as proof that every posting is correct or that acquisition is complete in every possible sense.

3. Files and scope

Expected production changes are limited to:

- `agent/board.py`: Greenhouse metadata validation and an appropriate error distinction.
- `agent/watch.py`: handling that specific validation failure with the required exit behavior and state preservation.

You may add focused tests and update the review packet and factual process documentation.

Keep the implementation small. Do not change every existing board error to exit code 3 merely to satisfy this regression. Preserve unrelated error handling; use a specific distinction for this failure if necessary.

If another production file genuinely needs modification, explain the dependency before expanding the patch.

4. What must not change

Do not change:

- The assertions or expected results in the submitted regression test.
- The pre-patch evidence.
- The relevance rule, fictional résumé, judgment prompts, or judgment validator.
- Successful baseline and new-posting behavior for valid inputs.
- Unrelated network, retry, permission, or state policies.
- Existing tests merely to make the suite pass.

Do not bundle the multi-board loop, Ashby integration, approval mechanism, or separate suspect-empty demonstration into this review patch.

Do not substitute 40 jobs, alter the declared total, or otherwise repair the test input to conceal the mismatch.

5. Verification and acceptance criteria

Before patching, commit the reproduction, regression test, captured failure, investigation, and this request. Keep the implementation patch in a later, separate commit.

After patching:

- Run the unchanged regression test.
- Confirm that its state-preservation assertion is actually reached and passes. The current failure occurs earlier at the exit-code assertion, so the captured failing run does not establish state preservation.
- Add focused coverage for matching totals, mismatched totals, invalid supplied total types, and the supported absence of optional total metadata.
- Run the existing relevant parser and watch tests, followed by the inherited test suite.
- Save the commands and actual results, distinguishing Claude’s executions from mine.

I will inspect the diff as a change in behavior, run the supplied checks myself, and decide whether to accept, revise, or reject the patch. Passing tests alone does not constitute my acceptance.

6. Known limitation

The count-mismatch regression would miss a response whose declared total matches its length but whose posting contents are incorrect or substituted. Count consistency is one check, not proof of source accuracy.

7. Requested handoff

After implementing and testing the scoped patch, provide:

- The reproduction/test commit and patch commit.
- A concise explanation of the behavioral change.
- The exact commands for me to inspect the diff and rerun the checks.
- Actual test results and remaining limitations.

Leave my review decision and signature pending until I provide them.
