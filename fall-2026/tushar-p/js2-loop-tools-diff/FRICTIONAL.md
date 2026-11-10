# Frictional — Job-Search Agent 2

Tushar Patel · INFO 7375 · Fall 2026

I wrote these November 9 entries retrospectively from my running notes, commits, and saved test output.

## November 9 · What I carried over from JS1 feedback

I started JS2 a day before it was due. My JS1 feedback gave me two things to fix. Claude chat had picked the prompt change I reviewed, and I had left the sign-off line blank. For JS2 I wanted the review to start with a failure I found myself. I also wanted to make an explicit sign-off decision after recording what I checked and what was still open. [Review packet](REVIEW-PACKET.md) · [Sign-off](SIGNOFF.md)

## November 9 · The gate before code

I kept Stripe so I could carry over the JS1 baseline logic, added Notion and Linear to exercise a second ATS, and chose a made-up Greenhouse token to test a real 404. Claude's gate review pointed out that my first draft didn't say which exit wins when two apply or how long a retry waits. I added exit precedence, a 10-second request cap, a 1-second retry wait, and three permission predictions for local reads and approval reuse. I approved the 20 predictions and committed the gate before Claude Code started building. [Gate decisions](GATE.md#decision-log) · Commit `7b171a4`.

The sandboxed preflight couldn't resolve the hosts. My Terminal checks got 200 from Stripe, Notion, and Linear, and 404 from invalid tokens on both systems. During recon, Claude Code looked at other students' folders to infer the Ashby schema. I discarded those findings, used my saved Ashby responses, and restricted later prompts to my folder with read-only access to JS1 where needed.

Claude's 20 recon questions made me pin down what counts as an attempt, how to save state, and what the deadline covers. I kept DNS elapsed time in the budget and recorded that the system lookup can block past the deadline. I also corrected the gate when it credited Claude with an invalid-token check I had run myself. [Preflight evidence](evidence/preflight/) · [Contract decisions](GATE.md#contract-decisions-v03) · Commit `553efbe`.

## November 9 · P13 stayed green under the first mutation

I reran the permission suite and all 20 results matched the predictions. I expected the prefix-only check to let `out-evil` through, but my M1 edit and pytest run showed that P13 still passed. Claude chat's first explanation blamed the input `..` check. When I read the code, I saw that P13's input has no `..`. The prefix check admits the sibling and `relpath()` introduces `..` afterward. The parent real-path check is the later refusal. [Baseline output](evidence/test-runs/permissions-run1.txt) · [M1 output](evidence/test-runs/mutation-M1.txt)

I twice thought I had both edits in place for M2. The first diff only disabled the parent check. The next diff was identical to M1 and only changed the prefix check. I switched to a script with assertions for both edits and checked the diff before treating the test result as evidence.

In the saved variants, M1 changed containment to a prefix check, M2 also disabled the parent check, and M3 disabled only the parent check. In M2, P13 failed with `DID NOT RAISE WriteDenied`. M1 and M3 passed. I kept P13 as a check of the final outcome. It can't tell which layer blocked the write. I left the output-root symlink and ancestor-alias cases open and excluded Claude Code's scratch checks because there was no saved output. [Mutation results and diffs](evidence/PERMISSION-BOUNDARIES.md#mutation-check) · Commit `ca1f667`.

## November 9 · The budget that a live run can't hit

Claude Code's loop build surfaced a mismatch in my limits. Five boards with one retry each can make at most 10 attempts. I kept the 12-attempt guard and documented that the tests exercise it directly. The time limit can still stop a live run. The offline suite passed 123 tests at this stage. The real HTTPS path still needed my live run. [Loop test output](evidence/test-runs/full-suite-run1.txt) · [Gate](GATE.md) · Commit `c16a48e`.

## November 9 · The first live run had the expected exit for extra reasons

I predicted three successes and one deliberate 404. Live run 1 said `incomplete`, but only Stripe succeeded. Both Ashby boards returned 403, with one attempt each and null counts, and only Stripe's state was staged. The saved Ashby bodies gave me error code 1010. This was the failure I chose for the review. I used curl to vary the User-Agent and saw 403 with the Python value and 200 with the student-project value. I added the exact student-project header to the gate. [Live run 1 summary](evidence/runs/live-1-ashby-403/summary.json) · [Curl reproduction](evidence/review-packet-ua-repro.txt)

With help from Claude chat on the handler pattern, I added `ua01` and saved its failure before asking Claude Code for a patch. I checked the transport diff, ran the focused test and suite, and ran the watch again. I accepted the patch after both Ashby boards returned listings and the only failed board was the one I meant to fail. I kept the fake-handler limitation in the review packet because it reads the Request object and can't establish what an external server will accept later. [Review packet](REVIEW-PACKET.md) · Commits `20d46dd`, `346c2f8`, and `9d8e012`.

## November 9 · A finished run can still be wrong

I replayed the October 28 Stripe response against seen IDs from October 27. A direct comparison gives 16 new IDs. I used that difference as the reference point for Claude Code's seeded empty-list mode. The ordinary replay agreed with the separate count. The seeded run still exited `finished` and gave me zero. The checker read the original bytes and starting state and returned a mismatch with exit 1.

I kept the original agent exit and the checker exit in the evidence because they answer different questions. Claude Code wrote both programs, so I rely on their separate code paths and the known fixture difference for this check. I also ran the checker on the live evidence. It matched all three successful boards, including the one new Stripe ID in live run 2. The 404 had no valid listing to compare. The final offline suite passed 132 tests. [Replay output](evidence/finished-wrong-answer/demo-output.txt) · [Final test output](evidence/test-runs/full-suite-final.txt) · Commits `a67355e`, `f12c14b`, and `f5f6406`.
