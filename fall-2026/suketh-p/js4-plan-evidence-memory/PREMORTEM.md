# PREMORTEM.md — Job-Search Agent 4

The student's premortem is quoted word for word below, with the time it arrived. It was committed before any JS4 memory code was written (at this commit, `jobwatch/` and `state/` are unchanged since the JS3 copy `a470a831`) and before the failure was triggered. What happens when the failure is triggered will go in a later section. The quote will not change.

## The premortem (the student dated it November 25, 2026, 11:15 p.m. EST; received in the chat by 23:19 EST)

> Premortem · Job-Search Agent 4  
> Written November 25, 2026, 11:15 p.m. EST, before triggering the failure.
>
> 1. How I expect shared memory to fail. Both watchers read revision 0. The Anthropic watcher saves its update first. If the Databricks watcher then saves its old copy, it can erase the Anthropic update even though both writes produce valid JSON.
> 2. How I’ll trigger it offline. I’ll use a disposable state file and prepare two updates with different posting keys. Each gets its own run ID and approval tied to the same revision 0 and starting SHA-256. I’ll commit the Anthropic update first, then submit the Databricks update with its original revision and hash.
> 3. What the design should do. The writer should compare the approved revision and hash with the current file while holding the lock. It should reject the second update, void that run’s approval, and report that it expected revision 0 and found revision 1.
> 4. What I’ll check. I’ll read the file directly after the first commit and again after the refusal. The bytes and SHA-256 should match. The state should still show revision 1 and the Anthropic posting with its source record. The trace should record the stale-write refusal.
> 5. Who decides when work resumes. I decide whether the Databricks update still makes sense after rereading revision 1. If it does, I reconcile it with the newer state and approve a new run ID against the new revision and hash.
> 6. What the design still misses. A writer can start from the current revision and still save a wrong fact. If a posting disappears from a board list, I’d still need separate source evidence before calling it closed.

*Note by Claude Code, for traceability:* the six parts follow a skeleton of six questions that Claude Code gave the student in the chat at 23:12 EST. Claude Code built it from the brief and from Chapter 12's premortem rows (failure, trigger, control, detection evidence, owner and resume condition, residual risk). The student reworded the six labels, and the text above is as the student sent it. Claude Code added only the quote markers and a Markdown line break after the title line, so the title shows on its own line.
