# Sources — Job-Search Agent 2

Tushar Patel · INFO 7375 · November 9, 2026

## Starting points

- I started with my JS1 Stripe watch in `fall-2026/tushar-p/js1-contract-and-watch/` at `cb4333e`. JS2 carries forward the baseline and new-ID logic. The seeded demo uses the [October 28 Stripe response](fixtures/greenhouse-stripe-2026-10-28-from-js1.json) and [starting state derived from October 27](fixtures/seed-state-2026-10-27.json). The fixture commit is `0f5db51`.
- The public sources are the Greenhouse listing route `/v1/boards/<token>/jobs` at `boards-api.greenhouse.io` and the Ashby route `/posting-api/job-board/<token>` at `api.ashbyhq.com`. The approved routes, board tokens, and User-Agent are in the [gate](GATE.md). The saved inputs and responses are under [preflight evidence](evidence/preflight/) and [live runs](evidence/runs/).
- The runtime uses Python 3.12.10 and its standard library. pytest 9.2.0 is the test dependency, pinned in [requirements.txt](requirements.txt).

## Who did what

- **My decisions and checks.** I approved the pre-code gate and permission predictions, captured the board responses, ran the live watch, reproduced the 403 with curl, and ran the M1–M3 variants. I added the test-first User-Agent regression with help from Claude chat and committed the failing test at `02c038f`. I accepted the patch after reviewing the diff, rerunning the tests, and seeing the second live result at `8131e58`. I used the saved Stripe inputs to run the ordinary and deliberately wrong replay and checked both reports.
- **Claude Code.** It worked from the gate, asked the F1–F20 recon questions, and implemented the permission layer, bounded loop, fixture modes, separate count checker, and the build test suites. The pre-review build commits are `7ef9c91`, `2679322`, and `ef15fb1`. It also wrote the focused User-Agent patch. [Patch](evidence/review-packet/ua-patch.diff)
- **Chat assistance.** Claude chat suggested gate revisions and F1–F20 answers, helped draft implementation prompts and the regression test pattern, and proposed mutation checks. I also used AI assistance to draft and edit the gate and submission documents and to run preliminary mutation probes. My own recorded mutation variants are M1–M3. The final documents use the saved commands, diffs, and outputs as their source. [Decision log](GATE.md#decision-log) · [Mutation evidence](evidence/PERMISSION-BOUNDARIES.md#mutation-check)

## What I changed or rejected

- I used my own board captures as evidence and left other students' materials out of the implementation.
- I kept the 12-attempt limit and documented that five boards with one retry each can make at most 10 attempts. I recorded the standard-library DNS limit rather than treating the attempt deadline as a DNS timeout.
- The first mutation follow-up targeted the input `..` guard. I moved the second mutation to the parent real-path check because the sibling input contains no `..`. The prefix calculation creates that component later.
- I left Claude Code's scratch checks out of the evidence when there was no saved output. The recorded suite and the committed M1–M3 diffs support the permission claims here. [Frictional log](FRICTIONAL.md)

pytest is MIT-licensed. JS2 uses it as a test dependency.
