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

## Entry 3 — after the premortem trigger and the two replays (the student dated it November 28, 2026, 9:08 a.m. EST; received in the chat by 09:09 EST)

> Frictional entry 3 · Job-Search Agent 4  
> Written November 28, 2026, 9:08 a.m. EST.
>
> 1. Did my prediction hold? Yes. Both proposals started at revision 0. Anthropic committed revision 1 first, and the writer refused Databricks with “expected revision 0 … found revision 1.” The revision-1 hash matched before and after the refusal, so the accepted Anthropic records survived.
> 2. What I checked myself, and how. I ran `shasum -a 256` on both final state files. The hashes matched the replay and recovery receipts. I also ran `checks/independent_check.py` on the November 24 replay with November 8 as the earlier capture. It passed and counted 193 new keys, 271 missing, and zero returned. That command ran in count-only mode. My separate hash check covered the saved state bytes.
> 3. What I decided after the refusal. I approved `PREMORTEM-databricks-2` against revision 1. Rebuilding from the November 8 capture added the 922 Databricks keys at revision 2 and preserved all 1,350 Anthropic facts.
> 4. What I accepted, modified, or rejected. I accepted the stale-write refusal and chose to rebuild the proposal with a fresh approval. I count `shasum` as independent verification of the saved bytes and the checker’s separate raw-response parser as independent recomputation of the counts. Both checks are scoped to the saved evidence.
> 5. What’s still unresolved. I still can’t tell whether the 271 missing postings closed. The replay demonstrated closure for one explicitly labeled fixture. A write can start from the right revision and still carry a claim the source doesn’t support.
> 6. Where to see it. `PREMORTEM.md` records the prediction at `9a8f1cc3` and the refusal at `4fb18fe6`. The two-day replay is in `7b6121a7`, and the Databricks recovery is in `17a5a2ca`. My Terminal output is in `evidence/student-checks/2026-11-28-hand-check-as-pasted.txt` at `48d33602`.

*Note by Claude Code, for traceability:* the six parts follow a skeleton of questions that Claude Code gave in the chat after commit 17a5a2ca. The student reworded the labels, and the text above is as the student sent it. Claude Code added only the quote markers and a Markdown line break after the title line. The five commits the entry names exist as named. Its 193 new and 271 missing keys are the sums of the checker's per-board counts (93 + 99 + 1 and 137 + 131 + 3) in the student's own output, evidence/student-checks/2026-11-28-hand-check-as-pasted.txt.

## Entry 4 — before submitting (the student dated it November 28, 2026, 9:24 a.m. EST; received in the chat by 09:26 EST)

> Frictional entry 4 · Job-Search Agent 4  
> Written November 28, 2026, 9:24 a.m. EST, before submission.
> 1. What changed in how I read the results. The stale-write test showed that the writer protected the first update. The closure fixture showed how memory at the current revision can still carry an outdated observation. I needed separate evidence for each conclusion.
> 2. What I checked myself. I ran shasum on the two saved state files and ran the count checker against the November 8 and November 24 captures. I used the recorded tests and run artifacts to review the stale-write refusal, recovery, and closure fixture. I used drafting and implementation help and made the recorded approvals and recovery decision.
> 3. Which memory choices I kept. I kept listing statements tied to their capture time because the replays used saved responses. I kept “I cannot tell” for a closure recorded after the latest listing that gives an earlier or equal closure time. I also kept returned for a known key that appears again on the same board after its latest observation was missing or closed. It keeps its original first-seen record.
> 4. What counts as independent in the evidence matrix.
>
> | Row | My decision |
> | --- | --- |
> | Listed | Partly checked. The hashes and recount cover the saved bytes and totals. An independent check of an individual listing still needs an exact board-and-key lookup in the dated raw response. |
> | Closed | Fixture behavior only. The run shows how memory responds to one constructed closure record. A real closure claim needs separate, dated evidence for that exact posting. |
> | Location | Pending. JS4 ran no location check. I’d compare the saved location field and any office, hybrid, or travel requirements directly with the claim. |
> | Sponsorship | Pending. JS4 ran no sponsorship check. I’d check the original passage for wording that applies to the specific role. General employer policy leaves that question open. |
>
> 5. What I’m leaving unresolved. The 271 missing keys tell me what disappeared from the later lists. Their real-world status remains unknown. My sign-off stays within the saved captures, matching state hashes, and recorded fixture behavior.
> 6. Where to see it. The plan is in d349bacb and ac451bf5, with approval in a1b9e3a2. The premortem is 9a8f1cc3, the memory gate is aa5d3f62, and the memory implementation is 3943f5ee. The replays are 5d9faf79 and 7b6121a7. The refusal and recovery are 4fb18fe6 and 17a5a2ca. My Terminal check is 48d33602, and my sign-off is 7d9be61d.

*Note by Claude Code, for traceability:* the six parts follow a skeleton of questions that Claude Code gave in the chat after commit f69ff806. The student reworded the labels, and the words above are as the student sent them. [evidence/2026-11-28-frictional-4-as-pasted.txt](evidence/2026-11-28-frictional-4-as-pasted.txt) is the entry exactly as received. Claude Code added the quote markers and a Markdown line break after the title line. It also turned line 4's tab-separated rows, indented three spaces, into a Markdown table, so they show as a table. A script rebuilt the entry's lines and found them identical. The twelve commits the entry names all exist. Its line-4 decisions are quoted in EVIDENCE-MATRIX.md's last column.
