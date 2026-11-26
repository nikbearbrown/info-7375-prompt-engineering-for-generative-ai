# FRICTIONAL.md — Job-Search Agent 4

The student's entries are quoted word for word, with the time each one arrived. Claude Code's own record of the work is kept apart, in the commit history and, later, the README.

## Entry 1 — before building (the student dated it 2026-11-25; received in the chat by 10:08 EST, with PLAN.md v0.1 and "PLAN ready")

> I expect the hardest part to be deciding what I can say about a posting when the latest board list leaves it out. The November 24 comparison already has 271 keys in memory that are missing from the later lists, so I want to keep the history and be precise about what the source shows. I also want to see the second write fail cleanly when both watchers start from the same revision.

*Note by Claude Code, for traceability:* the 271 is Claude Code's offline count, made on 2026-11-25 at 14:49 UTC and reported to the student in Claude Code's PLAN worksheet, of keys in `state/state.json` (last advanced by run `2026-11-08-normal-1`) that are absent from the Nov 24 board lists (137 Anthropic, 131 Databricks, 3 Linear). The count and its script are in `evidence/2026-11-25-memory-vs-nov-24-lists.txt`, added in the commit after this one.

## Entry 2 — on the v0.1 review (the student dated it November 25, 2026, 11:56 p.m. EST; received in the chat by 00:43 EST on 2026-11-26)

> Frictional entry 2 · Job-Search Agent 4  
> Written November 25, 2026, 11:56 p.m. EST, reflecting on the v0.1 review.
>
> 1. Who writes `notes.json` · Modified. v0.1 already called for a shared writer. I clarified who owns the file and what each watcher hands over. Each watcher now has its own output path in the plan. The coordinator checks for one valid contribution per board before it merges them.
> 2. Independent checker · Accepted. A watcher and checker can agree on the wrong count if both use the same parser. I kept the approach from JS3’s independent checker, which reads the saved JSON directly. The 42-key fixture gives the checker a known answer when the summary claims 99.
> 3. Stale approval and `state/2` · Modified. v0.1 already put the revision and hash comparison inside the lock. I made the consequence explicit. A mismatch voids that run’s approval. I also specified where revision 0 comes from. The replay starts with empty versioned state, and a separate fixture checks that the legacy import preserves seen keys and run history.
> 4. How I checked the findings. I used the recorded comparison with `PLAN-v0.1.md` to check what the writer handoff already said. The read-only source inspection confirmed that `checks/independent_check.py` parses raw responses itself, `jobwatch/state.py` has no revision field in the legacy schema, and `jobwatch/policy.py` binds its legacy approval to a run ID and path.
> 5. What’s unresolved. The stale-write and same-revision hash-change unit tests pass. I still want an end-to-end record of the two separately approved premortem writes and a run that shows both watchers’ contributions in the merged notes.
> 6. Where to see it. v0.1 is `d349bacb`, the dated review is in `evidence/plan-review/` at `861cd461`, and v0.2 is `ac451bf5`. The planted count results are in `evidence/checks/2026-11-25-count-check.txt`. The memory tests are in `tests/test_memory.py`, with results in `evidence/test-runs/06-green-memory.txt`.

*Note by Claude Code, for traceability:* the six parts follow a skeleton of questions that Claude Code gave in the chat after committing the memory (3943f5ee). The student reworded the labels, and the text above is as the student sent it. Claude Code added only the quote markers and a Markdown line break after the title line. The commits and files the entry names exist as named. PLAN-v0.1.md's Steps 4 and 6 do describe a shared writer, and a revision and hash comparison under that writer's lock.
