# Sign-off — Job-Search Agent 2

Swathi Baba Eswarappa, 2026-11-07.
Claude (chat) compiled the tables and lists below from our session records;
I checked every row. My "why" sentences and my decision are my own words.

## Checked (which property, by which test)
| Property | Test / evidence | How |
|---|---|---|
| The permission policy does what my 15 boundary predictions say | tests/test_policy.py, test_case_01 ... test_case_15 (predictions 85dbd4c, tests 01cc589, policy 5275cc4) | By tests written from my predictions before the policy code: I made the predictions; Claude Code wrote the tests |
| The policy's hosts and folders match GATE.md | tests/test_policy.py, GATE.md sync test | With Claude's help (Claude Code wrote it) |
| The loop's exits, budgets, repeat rule and error policy follow GATE.md and its revision | tests/test_loop.py, L1-L15, R1-R5, P1-P2 (tests ed201d4, before loop code e6a70a4) | With Claude's help: Claude Code wrote the tests from my GATE.md; I approved them before the code |
| Every exit status and every board status can really happen | tests/test_loop.py. Exits: finished L11, R5; incomplete L1, L2, L14, R1, R3; budget-exhausted L5-L7, R1; error L12, L13, R1. Board statuses: ok L2, L4, L8, L11, R4; failed L2, L4, L10, L14, R1, R3; "empty, unverified" L1; "not tried" L5-L7 | With Claude's help |
| The deliberate failure is handled without inventing a value | live runs d8a5a7b (Nov 4) and bd602a2 (Nov 5): real 404, no retry, run ends incomplete | With Claude's help (Claude Code recomputed every raw file's sha256 against the trace) |
| A finished wrong answer is caught by a check that does not use the agent | tests/test_independent_check.py, C1-C8 (f79e4a9, before the check 9615734); demo ae284ca | With Claude's help; C7 checks the check imports none of the agent's code |
| The Plaid office-name fix works and stays in scope | tests/test_ashby_address.py, A1-A5 (16da614, before the fix 4a3db26); review-packet files 01-04 | By hand: I reproduced the defect, ran the tests before and after the fix, and read the diff myself |

## Not checked
- Partial drops: neither my loop nor my independent check notices a board that loses some, but not all, of its postings.
- My rule reads only the title and location, never the description. The broad word "Analyst" made a Fraud Intelligence Analyst "relevant".
- A posting with no address at all (like "Seattle Office" alone), or a country spelling my rule does not know, like "U.S." with periods.
- The empty response and the timeout were only simulated in tests; I never saw them live.
- Case 13's test catches input(), but not every other way of reading input.
- The live network code (live_transport) has no test: DNS and other network errors, how real 4xx and 5xx responses are read, and whether the real request uses the redirect handler are untested. Only its 200 and 404 paths were seen in the live runs.
- The independent check is independent of the agent's code, but it was written by the same tool (Claude Code).
- An old commit (5909627) still holds my Mac username in the branch history; only the current file was redacted.

## Not claiming
- I am not claiming the agent finds good jobs for Priya: in the Nov 5 run only 1 of 31 new postings was rated relevant, by title and location only, with no description read.
- I am not claiming it works on boards other than Databricks, Stripe and Plaid.
- I am not claiming my budget numbers are the right ones, only that the loop keeps to them.
- I am not claiming the empty-response or timeout handling was seen live.

## Driver's seat
| Task | What Claude should do | What I should do | Why that part stays mine (my words) | Evidence |
|---|---|---|---|---|
| The loop | Write the loop, parser and policy code, and the tests from my rules | Write the GATE rules, budgets, exits and boundary predictions, and approve every test before code | That part stays mine because I'm responsible for deciding what the agent is allowed to do, what its limits are, and how it should handle failures. I don't want Claude to make those decisions on its own, especially when something could go wrong. | GATE.md 510a59a and revisions 96dde19, d131b5f; predictions 85dbd4c; I changed case 13 |
| The review | Propose and write the fix, and point out mistakes in my wording | Reproduce the bug, run the tests before and after, read the diff, and decide | That part stays mine because I need to make sure Claude's fix actually solves the problem without creating new ones. Just because the code runs and the tests pass doesn't mean the result is always correct, so I want to verify it myself before accepting it. | review-packet files 01-04 (01 redacted in dcf9cf9; 02 in 5ac5d93; 03-04 in 4c08a7f); fix 4a3db26; my decision in REVIEW-PACKET.md |

## Signed
Signed: Swathi Baba Eswarappa, 2026-11-07.
