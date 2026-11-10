# Sign-off — Job-Search Agent 2

Tushar Patel · INFO 7375 · November 9, 2026

## Checked

- **Permissions.** I approved P01–P20 before the build and ran `tests/test_permissions.py`. All 20 cases matched. I used M1–M3 to see which layer blocked the P13 sibling path. Either the containment check or the parent real-path check blocked that write on its own. With both compromised, P13 failed with `DID NOT RAISE WriteDenied`. [Predictions, results, and mutations](evidence/PERMISSION-BOUNDARIES.md)
- **Real board failures.** I compared the two live summaries and the second trace. Live run 1 attempted each Ashby board once, left both counts null, and staged state only for Stripe. Live run 2 attempted the deliberate 404 once, left that board's counts null, and reported `incomplete` with the three successful boards still in the report. [Live run 1](evidence/runs/live-1-ashby-403/summary.json) · [Live run 2 summary](evidence/runs/live-2-after-ua-patch/summary.json) · [Live run 2 trace](evidence/runs/live-2-after-ua-patch/trace.jsonl)
- **The User-Agent fix.** I ran `test_ua01_request_sends_agent_user_agent` before Claude Code's patch, then reran it after reviewing the diff. It went from fail to pass. The 124-test run and the two Ashby successes in live run 2 supported my decision to accept `8131e58`. The later full suite passed 132 tests. [Review packet](REVIEW-PACKET.md) · [Final suite](evidence/test-runs/full-suite-final.txt)
- **A clean exit with a wrong count.** I ran the ordinary fixture and the seeded wrong variant. Both exited `finished`. The separate checker matched the ordinary run at 16 new IDs and flagged the seeded report's 0 versus 16 with checker exit 1. It also matched all three comparable boards in live run 2. [Checker output](evidence/finished-wrong-answer/demo-output.txt)

## How I checked

I used curl to reproduce the live 403 and read the saved responses and diff. I recorded the focused `ua01` failure before asking Claude Code to patch the transport. Claude chat helped draft the fake-handler pattern. I also ran the M1–M3 mutations on temporary test data. The checks answered different questions. The mutation tested whether the permission outcome changed when guards were removed, and `ua01` checked the exact header on the Request.

For the count, I ran `checks/independent_count.py` against the saved raw listings and starting state. Claude Code wrote the checker and the agent. The checker uses a separate implementation and imports no agent code. A direct set comparison of the two JS1 responses also found 16 IDs in the October 28 response that were absent on October 27.

## Not checked

- Real DNS lookup duration against the attempt cap. A blocking system lookup can run past the deadline.
- A live run that stops on its time budget. The network-window tests use a fake clock. The 12-attempt guard is tested directly because a valid config can make at most 10 attempts.
- Rejection of a symlink used as the output root itself and acceptance of an ancestor alias like `/var` → `/private/var`. The recorded permission cases cover links below the root.
- Concurrent runs sharing an output root or a process swapping folders during a write. The gate calls for one active run per root.
- How the checker and seeded mode respond together to a corrupt original fixture. The demo used known saved bytes.

## Not claiming

JS2 finds posting IDs that are new to a board's saved state. It makes no relevance judgments, and a repost can have a new ID. The shortlist is a tested approval boundary with no CLI approval flow. My live findings cover the configured endpoints and the November 9 runs. I make no claim about future provider responses.

## Driver's seat

| Part | What Claude did | What I did and why | Evidence |
|---|---|---|---|
| Loop contract | Claude Code raised recon questions, and Claude chat proposed answers. | I approved the gate and chose the exits, limits, and allowed actions. Those decisions determine what work the agent can do and what counts as done. | `1e5079e`, `b94c596`, `b48429d` · [Gate](GATE.md) |
| Permission checks | Claude Code implemented the guards and P01–P20. | I approved the predictions before code and ran M1–M3 to see what P13 could distinguish. The test outcome is the evidence I use to rely on the boundary. | `e2011de` · [Boundary results](evidence/PERMISSION-BOUNDARIES.md) |
| Live loop | Claude Code implemented the loop, budget, state, trace, and CLI. | I chose the endpoints, ran the live watch, and compared each board with my prediction. The first run showed why the exit label alone was insufficient. | [First live summary](evidence/runs/live-1-ashby-403/summary.json) |
| Diff review | Claude chat helped with the test pattern. Claude Code wrote the patch. | I reproduced the failure, saved the red test, reviewed the diff, reran the checks, and accepted the change on evidence. | `02c038f`, `8131e58` · [Review packet](REVIEW-PACKET.md) |
| Wrong-answer check | Claude Code wrote the replay mode and separate checker. | I used the October 27 and 28 responses to set up a comparison with a known difference and ran the checker on the saved evidence. I chose a check that reads the original inputs directly. | `0f5db51`, `c7c3e5c` · [Demo output](evidence/finished-wrong-answer/demo-output.txt) |

**Signed — Tushar Patel, November 9, 2026.** I authorize this sign-off for the checks and limits listed above.
