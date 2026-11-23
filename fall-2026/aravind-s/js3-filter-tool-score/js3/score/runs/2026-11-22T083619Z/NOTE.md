# A note on these saved runs

The `metrics` field inside these files was computed with a bug in the tool's first version: the held-out kit names
its pools "random kept" and "random rejected", and the tool looked for "kept" and "rejected", so each pool's counts
came out as 0 of 0 (the "all" counts were right). The `rows` are correct and complete. `js3/score/EXPERIMENTS.md` is
rebuilt from the rows by `python3 tools/heldout_experiments.py report`, after the fix; nothing was measured again.
`whole-run.json` was added by that report command: it judges all 1,509 postings of the filter run under each change
and reads no held-out answer.
