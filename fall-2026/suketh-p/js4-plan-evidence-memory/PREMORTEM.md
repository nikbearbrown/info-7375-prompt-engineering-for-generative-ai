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

## What happened when the failure was triggered (Claude Code's record, 2026-11-28)

The student approved both writes in the chat; [replay/APPROVALS.md](replay/APPROVALS.md) holds the reply word for word. Claude Code then ran this from the JS4 folder at 13:44:30 UTC:

```bash
python3 -m jobwatch.replay premortem --capture runs/2026-11-08-normal-1 --approve-anthropic PREMORTEM-anthropic:replay/premortem/state.json:0:f046969f9ae59329fe59cd35ae89f2646852312efa07620522efc6416a824f7d --approve-databricks PREMORTEM-databricks:replay/premortem/state.json:0:f046969f9ae59329fe59cd35ae89f2646852312efa07620522efc6416a824f7d
```

| Line | What the record shows |
| --- | --- |
| 1 | Both updates were built on revision 0 of `replay/premortem/state.json`. The Anthropic update committed first. The Databricks update was refused, so it did not erase the Anthropic update. |
| 2 | The disposable file started empty at revision 0 (sha256 `f046969f…`). The two updates carry different posting keys: the Nov 8 capture's 675 Anthropic keys and its 922 Databricks keys. Each had its own run ID and an approval naming revision 0 and that SHA-256. |
| 3 | `jobwatch/memory.py` compared the approved revision and SHA-256 with the file while holding the lock. It refused the second write, voided the `PREMORTEM-databricks` approval, and reported "expected revision 0 … found revision 1". |
| 4 | The command read the file after the first commit and again after the refusal. Both times it was the same bytes, sha256 `72352a71ed7fb862e8f6bfd0b46a6dba7bb4be6d75927dd5fbdfb0ee3589fda9`. The state is at revision 1 with only `greenhouse/anthropic`: 1,350 facts (675 first-seen, 675 listed), each with its source fields. The refusal is recorded in [write-refused.json](replay/premortem/runs/PREMORTEM-databricks/write-refused.json) and [record.json](replay/premortem/record.json). The premortem command writes no separate trace file. |
| 5 | Not done yet: the student decides whether the Databricks update still makes sense after rereading revision 1. |
| 6 | Not tested by this trigger. |

Whether the prediction held is the student's judgment, for Frictional entry 3.

### Line 5, later on 2026-11-28

The student decided in the chat, by 08:50 EST: "Rebuild the update against revision 1 so revision 2 preserves the accepted Anthropic records and adds Databricks." The full reply is quoted in [replay/APPROVALS.md](replay/APPROVALS.md). With the student's approval of the new run ID `PREMORTEM-databricks-2` against revision 1, Claude Code ran this at 13:52:44 UTC:

```bash
python3 -m jobwatch.replay premortem-resume --capture runs/2026-11-08-normal-1 --watcher databricks --approve PREMORTEM-databricks-2:replay/premortem/state.json:1:72352a71ed7fb862e8f6bfd0b46a6dba7bb4be6d75927dd5fbdfb0ee3589fda9
```

It reread revision 1 (sha256 `72352a71…`, Anthropic only) and rebuilt the Databricks update on it from the Nov 8 capture's 922 keys. Then it committed revision 2, sha256 `96016689d3515d54f9326a4196cef77134481610c81c1a2a814c169ab678859c`. The state now holds 3,194 facts. The 1,350 Anthropic facts are unchanged and still credited to `PREMORTEM-anthropic`; the 1,844 Databricks facts are credited to `PREMORTEM-databricks-2`. The refused `PREMORTEM-databricks` approval stays void. Record: [resume-PREMORTEM-databricks-2.json](replay/premortem/resume-PREMORTEM-databricks-2.json).
