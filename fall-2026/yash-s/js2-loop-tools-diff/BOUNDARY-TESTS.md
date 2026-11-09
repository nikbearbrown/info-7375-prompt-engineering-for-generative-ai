# Job-Search Agent 2 — Boundary Test Predictions

**Date:** 2026-11-09  
**Status:** Predictions before implementation and testing

## Purpose

I want to test whether my agent follows its permission policy.

The permission checks must happen in Python code, not just in Claude's prompt.

I am writing these expected results before Claude Code implements the permission checker.

The actual results will be recorded after I run the tests.

## My Predicted Results

| # | Test case | My expected result | Why |
|---|---|---|---|
| 1 | HTTPS request to `boards-api.greenhouse.io` | Allow | This is an approved host using HTTPS. |
| 2 | HTTPS request to `api.ashbyhq.com` | Allow | This is the second approved ATS host. |
| 3 | Request to `example.com` | Refuse | The host is not on my allow-list. |
| 4 | Request to `boards-api.greenhouse.io.evil.com` | Refuse | The hostname only looks similar to an approved host. |
| 5 | HTTP request to `boards-api.greenhouse.io` | Refuse | My policy allows HTTPS only. |
| 6 | Write a new evidence file inside the approved `runs/` folder | Allow | This is a normal evidence write in the correct folder. |
| 7 | Write to `runs/../outside.json` where the resolved path escapes `runs/` | Refuse | The path uses `..` to reach outside the approved folder. |
| 8 | Write to `runs-evil/output.json` beside `runs/` | Refuse | A folder with a similar prefix is not the same approved folder. |
| 9 | Write through a symlink in `runs/` that points outside | Refuse | The resolved destination is outside the permitted directory. |
| 10 | Read the fictional resume from `persona/` | Allow | The agent needs to read the fictional resume for matching. |
| 11 | Write to the resume file in `persona/` | Refuse | Reading a file does not mean the program can modify it. |
| 12 | Reset an existing state file without my approval | Refuse | State resets require explicit approval. |
| 13 | Reset an existing state file with my explicit approval and within the approved state folder | Allow | The policy permits this specific action after approval and validation. |
| 14 | Follow an HTTPS redirect to an unapproved host | Refuse | An allowed starting URL must not bypass the host restrictions. |
| 15 | Write to an absolute path outside the approved output folder | Refuse | An absolute path outside the permitted directory must not bypass the path policy. |

These predictions apply to the permission checker. An "Allow" result means the action is permitted by the policy, not that a live network request is guaranteed to succeed.

## How I Will Test Them

I will ask Claude Code to implement these checks as automated tests.

For network permissions, the tests should use constructed URLs and mocked requests so I can check host restrictions without contacting external websites.

For filesystem permissions, the tests should create temporary folders and files.

The tests should use actual paths, including a sibling folder and a symbolic link, to verify that the program checks the resolved destination.

For approval tests, the tests should verify that an explicit approval is required for a restricted state operation.

I will run the tests myself and compare the results with this prediction table.

## What I Will Record After Testing

After I run the tests, I will add a results section with:

- The actual result for each case
- Whether it matched my prediction
- The test name
- Any failure or unexpected behavior
- What Claude changed after the tests
- The commit containing the tested implementation

I will not change the original predictions after seeing the results.

## Wrong Versions

I also want the tests to catch at least two intentionally incorrect implementations.

My planned wrong versions are:

1. A failed board is treated as a successful board with zero new postings.
2. A path checker uses string prefixes and incorrectly permits `runs-evil/`.
3. A repeated request does not count toward the request budget.

I want to save a reproducible check for these wrong versions and rerun it after code changes.

This addresses the feedback I received on Job-Search Agent 1 about rerunning planted-bug checks.
