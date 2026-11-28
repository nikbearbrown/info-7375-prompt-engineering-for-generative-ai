# Approvals for state writes

Each state write in this folder needs the student's approval for its run ID, target path, starting revision and SHA-256 ([PLAN.md](../PLAN.md) v0.2, Approval). This file records each approval as the student sent it, what it answered, and what the write then did. The approvals are the student's; Claude Code keeps this record.

## 2026-11-28: three writes from revision 0

In the chat, at about 08:41 EST, Claude Code's request listed three writes. Each started from revision 0, with sha256 `f046969f9ae59329fe59cd35ae89f2646852312efa07620522efc6416a824f7d`:

| Run ID | Path | Starting revision |
| --- | --- | --- |
| `SEEDED-1-2026-11-08` | `replay/state/state.json` | 0 |
| `PREMORTEM-anthropic` | `replay/premortem/state.json` | 0 |
| `PREMORTEM-databricks` | `replay/premortem/state.json` | 0 |

The student's reply, word for word, received in the chat by 08:44 EST:

> Approved  
> Suketh Produtoor

The reply answers the request above. It does not restate the values or give a date; the date on record is the day the reply arrived.

| Run ID | What the write did (UTC) |
| --- | --- |
| `SEEDED-1-2026-11-08` | 13:44:18: committed revision 1 of `replay/state/state.json`, sha256 `3539364075cf9f1304f73b9604936ce8bd057a051f03c26feba7ed299b4f31e5` (3,258 facts). Evidence: [runs/SEEDED-1-2026-11-08/](runs/SEEDED-1-2026-11-08/) |
| `PREMORTEM-anthropic` | 13:44:30: committed revision 1 of `replay/premortem/state.json`, sha256 `72352a71ed7fb862e8f6bfd0b46a6dba7bb4be6d75927dd5fbdfb0ee3589fda9` (1,350 facts, Anthropic only) |
| `PREMORTEM-databricks` | 13:44:30: refused as a stale write, as the premortem predicted. It expected revision 0 and found revision 1, and the file's bytes did not change. This approval is now void. Record: [premortem/runs/PREMORTEM-databricks/write-refused.json](premortem/runs/PREMORTEM-databricks/write-refused.json) |
