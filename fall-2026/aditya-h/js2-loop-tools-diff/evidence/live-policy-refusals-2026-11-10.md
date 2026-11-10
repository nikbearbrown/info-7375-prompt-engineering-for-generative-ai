# Live permission refusals — 2026-11-10 13:56 EST

These ran on the real committed state; Claude Code ran them. They show the approval-gated write (GATE.md boundary cases 16 and 18) refusing on the actual CLI, not only in unit tests.

```text
$ python3 -m jobwatch2 reset greenhouse/stripe
refused: needs-approval: resetting 'greenhouse/stripe' requires --approve-reset greenhouse/stripe
exit 3

$ python3 -m jobwatch2 reset greenhouse/stripe --approve-reset ashby/openai
refused: needs-approval: resetting 'greenhouse/stripe' requires --approve-reset greenhouse/stripe
exit 3

$ ls runs/state/greenhouse__stripe.json
runs/state/greenhouse__stripe.json          # still there: nothing was deleted
```

Not run: the *approved* reset (`--approve-reset greenhouse/stripe`) on real state. It would delete Stripe's seen ids and turn the next run into a re-baseline, which is Aditya's decision to make, not the agent's. The approved path is covered by `test_17_reset_with_approval` and `TraceAndRecords.test_reset_needs_approval`.

**Gap noticed:** the `reset` command does not write a trace line for its refusal. Only the loop and (since patch v3) the check keep traces.

Also refused on the real CLI (2026-11-10 14:00, on a copy of the folder after patch v3):

```text
$ python3 -m jobwatch2 run --boards ../../../../../../etc/hosts
refused: read '../../../../../../etc/hosts' is outside the assignment folder
exit 3
```
