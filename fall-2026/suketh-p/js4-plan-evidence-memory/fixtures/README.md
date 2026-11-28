# Fixtures (constructed, not board responses)

Claude Code wrote these on 2026-11-25 for the checks in [PLAN.md](../PLAN.md) v0.2. Nothing in this folder was fetched from a board, and every file carries a FIXTURE label. Step 5 of the plan runs its planted cases "against labeled disposable fixtures".

| Folder | What it holds | What the count check must do |
| --- | --- | --- |
| `count-42/` | One Greenhouse-format body with exactly the keys 1 to 42 (the plan: "exactly 42 unique keys, numbered 1 through 42"). The trace and the summary both say 42 | pass, with a recount of 42 |
| `count-42-planted-99/` | The same body and the same trace. The summary (`results.json` and `results.md`) says 99: the planted "42 in the trace, 99 in the claim" error | reject it |

Rebuild both folders from the JS4 folder with `python3 -I fixtures/make_count_fixtures.py`. [tests/test_count_check.py](../tests/test_count_check.py) checks that a rebuild gives the same contents.

## The closure fixture

Claude Code wrote [closure/2026-11-28-closure.json](closure/2026-11-28-closure.json) on 2026-11-28 for the "fresh is not true" case (PLAN.md v0.2's evidence matrix; [MEMORY-GATE.md](../MEMORY-GATE.md) A2). It names Anthropic posting `5456619008`. That is the first key in the Nov 24 capture that the Nov 8 capture also lists; 538 keys are listed on both days. The fixture states a closure at 2026-11-25T12:00:00Z, after the Nov 24 capture. It is constructed, and it says nothing about whether the posting is open in the real world. A replay given `--closure` checks it in memory on the staged state and never writes it to the replay state.
