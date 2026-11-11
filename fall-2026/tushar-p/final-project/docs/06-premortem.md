# 06 — Premortem

Drafted by Claude Code, reviewed by Tushar
Date: Nov 3, 2026

Written before the build. Each entry is a prediction, not a result. Tushar chose P1 as the Phase 6 controlled failure (final).

## P1 — The agent edits or deletes the test file to make the check pass (Phase 6 controlled-failure candidate, final)

- **What fails:** instead of fixing the bug, the agent changes, weakens, or deletes the test file so pytest passes.
- **Why likely:** the agent will have `write_file` and `run_command`, and the shortest path to green tests is often to change the tests, especially if a goal is phrased as "make the tests pass".
- **Independent check:** `check.sh` will check that the test file is unchanged (T1.1), for example by its SHA-256, separate from pytest's result. The policy will also deny writes to check files (T2.1).
- **Impact:** a false PASS, the exact failure this project exists to catch.
- **Prevention / recovery:** the policy denies the write; if a write slips through, the hash check fails the run. For Phase 6, trigger it on purpose (for example, a task or prompt that tempts editing the test), save the trace, show the check catching it, fix, rerun, and save the new trace (T6.1).

## P2 — The NetworkPolicy is not enforced, so the pod can reach the internet

- **What fails:** the default-deny egress NetworkPolicy is applied, but kind's default CNI (kindnet) does not enforce it, so the sandbox pod still has network access.
- **Why likely:** whether kindnet enforces NetworkPolicy is an open research question in T0.5; a policy object can exist without anything enforcing it.
- **Independent check:** a test pod will try to reach the internet and must fail (T1.2), and the isolation test for "no network" (T4.1).
- **Impact:** the agent could download code or exfiltrate data; "isolated sandbox" would be a false claim.
- **Prevention / recovery:** if the egress test connects, install Calico and document it (T1.2). Do not claim network isolation until the egress test fails to connect.

## P3 — The agent's "done" is taken as the verdict

- **What fails:** the loop ends when the model says it is finished, and that gets reported as PASS without the check deciding.
- **Why likely:** the simplest loop stops on the model's final message, and the code that ends the loop sits right next to the code that reports the result.
- **Independent check:** the stop-condition test (T2.3): an agent that says "done" with a failing check must not produce PASS. Verdicts come only from the harness-run check (D11).
- **Impact:** false PASS results across the whole eval table.
- **Prevention / recovery:** "done" only triggers the check; the trace records the check's exit code as the verdict source.

## P4 — Go and Kubernetes together overrun the schedule

- **What fails:** task 001 does not run on kind by Thu Nov 12, and later phases (evaluation, controlled failure) get squeezed.
- **Why likely:** both Go and Kubernetes are new to Tushar, and kind adds its own setup and debugging (image loading, NetworkPolicy, `kubectl cp`).
- **Independent check:** the calendar. M1 ("first slice works end to end on kind") either exists by Nov 12 or does not.
- **Impact:** no time for evaluation and the packet, which carry most of the grade.
- **Prevention / recovery:** T0.5 does kind by hand first. If Nov 12 passes, Claude Code writes `internal/sandbox/docker.go` behind the same interface; log why (friction log in the claude.ai Project, then FRICTIONAL.md at the end) and the Decision log (D16).

## P5 — A runaway loop burns tokens and money

- **What fails:** the agent repeats a failing command or rereads large files until the run costs far more than expected, possibly across a whole `apg eval`.
- **Why likely:** agents loop when a tool result is confusing; eval runs repeat each task several times.
- **Independent check:** the budget exits (max steps, tokens, cost, wall-clock timeout; T2.2), and, independent of the harness code, the spend limit on the `apg-harness` Console workspace (T0.1).
- **Impact:** wasted budget; the spend limit stops further runs until it is raised.
- **Prevention / recovery:** a test forces each budget exit (T2.2). The trace records the exit reason, so a budget hit shows up in the results table.

## P6 — Eval results are overclaimed

- **What fails:** a pass-rate difference between two prompt contracts gets written up as a real improvement, or prompt tuning quietly used the held-out tasks.
- **Why likely:** with 12–20 tasks and a few runs each, chance differences look like effects, and it is tempting to tune on whatever tasks are at hand.
- **Independent check:** the split commit hash in `docs/07-evidence.md` will predate any prompt tuning (T3.2); `apg compare` will show per-task changes, not just a headline rate (T5.3); the honest-limits section (T5.2).
- **Impact:** claims in the packet that the evidence does not support.
- **Prevention / recovery:** freeze the split first; report per-task results and run counts; write what the sample can and cannot show before writing conclusions.
